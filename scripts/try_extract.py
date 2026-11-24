
"""Manual check: one question on one lease -> structured Gemini extraction.

Usage: uv run python scripts/try_extract.py lease_01 monthly_rent
"""

import sys
from pathlib import Path

from clauselens.config import get_settings
from clauselens.extraction.extract import extract_fact
from clauselens.ingest.chunker import groupBlocks_toClauses
from clauselens.ingest.parser import parse_pdf
from clauselens.llm.cache import ResponseCache
from clauselens.llm.router import make_client
from clauselens.retrieval.embeddings import EmbeddingRetriever
from clauselens.retrieval.questions import QUESTIONS

ROOT = Path(__file__).resolve().parents[1]
TOP_K = 3


def main() -> None:
    if len(sys.argv) != 3:
        sys.exit("Usage: try_extract.py <lease_id> <question_id>")

    doc_id, field = sys.argv[1], sys.argv[2]

    question = next((q for q in QUESTIONS if q.id == field), None)
    if question is None:
        sys.exit(f"Unknown question id: {field}")

    # Parse only this one lease (Docling is slow).
    blocks = parse_pdf(str(ROOT / "data" / f"{doc_id}.pdf"))
    clauses = groupBlocks_toClauses(blocks)

    # Same query as Day 4: question text + keywords.
    query = f"{question.text} {' '.join(question.keywords)}"
    retriever = EmbeddingRetriever({doc_id: clauses})
    top = retriever.search(doc_id, query, TOP_K)
    chosen = [clauses[i] for i in top]

    print(f"\nRetrieved clauses: {[(i, clauses[i].title) for i in top]}")

    # Prepare Gemini and cache.
    settings = get_settings()
    client = make_client(settings)
    cache = ResponseCache(settings.cache_dir)

    # Extract one structured fact.
    fact = extract_fact(
        client,
        settings,
        cache,
        field,
        question.text,
        chosen,
    )

    print("\n----- FACT -----")
    print(fact.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
