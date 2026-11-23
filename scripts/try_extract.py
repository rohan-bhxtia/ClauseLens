"""Manual check: one question on one lease -> raw Gemini reply.

Usage: uv run python scripts/try_extract.py lease_01 monthly_rent
"""

import sys
from pathlib import Path

from clauselens.config import get_settings
from clauselens.extraction.prompt import build_extraction_prompt
from clauselens.ingest.chunker import groupBlocks_toClauses
from clauselens.ingest.parser import parse_pdf
from clauselens.llm.cache import ResponseCache
from clauselens.llm.router import call_with_fallback, make_client
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

    prompt = build_extraction_prompt(question.text, chosen)
    print("\n----- PROMPT -----")
    print(prompt)

    settings = get_settings()
    client = make_client(settings)
    cache = ResponseCache(settings.cache_dir)
    result = call_with_fallback(client, settings, prompt, cache)

    print("\n----- REPLY -----")
    print(result.text)
    print(
        f"\nmodel={result.model} in={result.input_tokens} "
        f"out={result.output_tokens} thought={result.thought_tokens} "
        f"latency={result.latency_s:.2f}s"
    )


if __name__ == "__main__":
    main()
