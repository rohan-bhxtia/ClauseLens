
"""Run extraction on all 5 leases x 15 questions and save the results."""

import json
from pathlib import Path

from google.genai import errors

from clauselens.config import get_settings
from clauselens.extraction.extract import ExtractionError, extract_fact
from clauselens.extraction.verify import build_page_text, verify_quote
from clauselens.ingest.chunker import groupBlocks_toClauses
from clauselens.ingest.parser import parse_pdf
from clauselens.llm.cache import ResponseCache
from clauselens.llm.router import EmptyResponseError, make_client
from clauselens.retrieval.embeddings import EmbeddingRetriever
from clauselens.retrieval.questions import QUESTIONS


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "eval" / "results" / "extraction_run1.json"

TOP_K = 3
LEASE_IDS = [f"lease_{i:02d}" for i in range(1, 6)]


def save_results(results: dict) -> None:
    """Save progress so completed questions aren't lost."""
    OUT.parent.mkdir(parents=True, exist_ok=True)

    with OUT.open("w", encoding="utf-8") as file:
        json.dump(results, file, indent=2, ensure_ascii=False)


def main() -> None:
    lease_clauses = {}
    page_text = {}

    # 1. Parse each lease and prepare its clauses.
    for doc_id in LEASE_IDS:
        pdf_path = ROOT / "data" / f"{doc_id}.pdf"

        print(f"\nParsing {doc_id}...")

        blocks = parse_pdf(str(pdf_path))
        clauses = groupBlocks_toClauses(blocks)

        lease_clauses[doc_id] = clauses
        page_text[doc_id] = build_page_text(blocks)

        print(f"  Blocks: {len(blocks)}")
        print(f"  Clauses: {len(clauses)}")

    # 2. Initialize shared components once.
    retriever = EmbeddingRetriever(
        lease_clauses,
        persist_directory=str(ROOT / "chroma_db"),
    )

    settings = get_settings()
    client = make_client(settings)
    cache = ResponseCache(settings.cache_dir)

    # 3. Process every question for every lease.
    results = {doc_id: {} for doc_id in LEASE_IDS}

    for doc_id in LEASE_IDS:
        print(f"\nProcessing {doc_id}...")

        for question in QUESTIONS:
            question_id = question.id
            print(f"  {question_id}...", end=" ")

            try:
                query = (
                    f"{question.text} {' '.join(question.keywords)}"
                )

                # Retrieve the top matching clauses.
                top = retriever.search(doc_id, query, TOP_K)

                chosen = [
                    lease_clauses[doc_id][i]
                    for i in top
                ]

                # Extract a structured Fact using Gemini.
                fact = extract_fact(
                    client,
                    settings,
                    cache,
                    question_id,
                    question.text,
                    chosen,
                )

                # Verify the evidence quote against the original PDF.
                check = verify_quote(fact, page_text[doc_id])

                results[doc_id][question_id] = {
                    "fact": fact.model_dump(mode="json"),
                    "quote_check": check,
                    "retrieved": [
                        {
                            "index": i,
                            "title": lease_clauses[doc_id][i].title,
                            "text": lease_clauses[doc_id][i].text,
                            "page": lease_clauses[doc_id][i].page,
                        }
                        for i in top
                    ],
                }

                print(check)

            except (
                ExtractionError,
                errors.APIError,
                EmptyResponseError,
            ) as exc:
                results[doc_id][question_id] = {
                    "error": str(exc)
                }

                print(f"ERROR: {exc}")

            # Save after every question.
            save_results(results)

    # 4. Print final summary.
    total = 0
    error_count = 0
    quote_counts = {}

    for lease_results in results.values():
        for result in lease_results.values():
            total += 1

            if "error" in result:
                error_count += 1
                continue

            outcome = result["quote_check"]
            quote_counts[outcome] = (
                quote_counts.get(outcome, 0) + 1
            )

    print("\n========== EXTRACTION SUMMARY ==========")
    print(f"Total questions: {total}")
    print(f"Successful: {total - error_count}")
    print(f"Errors: {error_count}")

    print("\nQuote verification outcomes:")

    for outcome, count in sorted(quote_counts.items()):
        print(f"  {outcome}: {count}")

    print(f"\nResults saved to: {OUT}")


if __name__ == "__main__":
    main()
