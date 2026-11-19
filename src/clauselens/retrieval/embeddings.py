
from collections.abc import Mapping, Sequence

import chromadb
from sentence_transformers import SentenceTransformer

from clauselens.schemas.clause import Clause_format


class EmbeddingRetriever:
    def __init__(
        self,
        leases: Mapping[str, Sequence[Clause_format]],
        persist_directory: str = "./chroma_db",
    ) -> None:

        # Load the embedding model.
        self._model = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2"
        )

        # Create persistent ChromaDB storage.
        self._client = chromadb.PersistentClient(
            path=persist_directory
)
        

        # Create or access the collection.
        self._collection = self._client.get_or_create_collection(
            name="lease_clauses",
            metadata={"hnsw:space": "cosine"},
        )

        self._rows = {}

        # Prepare clause data for ChromaDB.
        ids = []
        documents = []
        metadatas = []

        for lease_id, clauses in leases.items():

            lease_rows = []

            for index, clause in enumerate(clauses):

                clause_id = f"{lease_id}_{index}"

                text = f"{clause.title or ''} {clause.text}"

                ids.append(clause_id)
                documents.append(text)

                metadatas.append({
                    "lease_id": lease_id,
                    "clause_index": index,
                    "number": clause.number or "",
                    "title": clause.title,
                    "page": clause.page,
                })

                lease_rows.append(index)

            self._rows[lease_id] = lease_rows

        # Generate embeddings for all clauses.
        embeddings = self._model.encode(
            documents,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )

        # Store documents, embeddings and metadata.
        self._collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings.tolist(),
            metadatas=metadatas,
        )

    def search(
        self,
        lease_id: str,
        query: str,
        k: int,
    ) -> list[int]:

        if lease_id not in self._rows:
            raise ValueError(f"Unknown lease_id: {lease_id}")

        if k < 1:
            raise ValueError(f"k must be at least 1, got {k}")

        # Convert query into a dense embedding.
        query_embedding = self._model.encode(
            [query],
            normalize_embeddings=True,
            convert_to_numpy=True,
        )[0]

        # Search only within the requested lease.
        results = self._collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=min(k, len(self._rows[lease_id])),
            where={"lease_id": lease_id},
            include=["metadatas"],
        )

        # Return clause positions within the requested lease.
        return [
            int(metadata["clause_index"])
            for metadata in results["metadatas"][0]
        ]
