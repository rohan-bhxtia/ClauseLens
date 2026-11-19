from clauselens.retrieval.embeddings import EmbeddingRetriever
from clauselens.schemas.clause import Clause_format


def test_embedding_retriever_returns_ranked_results(tmp_path):
    leases = {
        "lease_01": [
            Clause_format(
                number="1",
                title="Maintenance",
                text="Tenant is responsible for property repairs.",
                page=1,
            ),
            Clause_format(
                number="2",
                title="Rent",
                text="Tenant must pay monthly rent of 25000 rupees.",
                page=2,
            ),
        ]
    }

    retriever = EmbeddingRetriever(
        leases,
        persist_directory=str(tmp_path),
    )

    results = retriever.search(
        lease_id="lease_01",
        query="Who is responsible for property repairs?",
        k=1,
    )

    assert results == [0]


def test_embedding_retriever_isolates_leases(tmp_path):
    leases = {
        "lease_01": [
            Clause_format(
                number="1",
                title="Rent",
                text="Monthly rent is 25000 rupees.",
                page=1,
            )
        ],
        "lease_02": [
            Clause_format(
                number="1",
                title="Maintenance",
                text="Tenant handles all property repairs.",
                page=1,
            )
        ],
    }

    retriever = EmbeddingRetriever(
        leases,
        persist_directory=str(tmp_path),
    )

    results = retriever.search(
        lease_id="lease_01",
        query="Who handles property repairs?",
        k=1,
    )

    assert results == [0]