
"""Measure dense embedding retrieval: hit@1/3/5 on every gold line."""

import json
from pathlib import Path

from clauselens.ingest.chunker import groupBlocks_toClauses
from clauselens.ingest.parser import parse_pdf
from clauselens.retrieval.metrics import gold_clause_indexes, hit_at_k
from clauselens.retrieval.questions import QUESTIONS
from clauselens.retrieval.embeddings import EmbeddingRetriever


ROOT = Path(__file__).resolve().parents[1]
KS = (1, 3, 5)


# FUNCTION 1:
# Loads all five lease PDFs, extracts their text blocks using the parser,
# groups those blocks into clauses using the chunker,
# and stores the clauses in a dictionary against their lease IDs.
def load_leases() -> dict:

    leases = {}

    for number in range(1, 6):
        doc_id = f"lease_{number:02d}"
        pdf_path = ROOT / "data" / f"{doc_id}.pdf"

        blocks = parse_pdf(str(pdf_path))
        clauses = groupBlocks_toClauses(blocks)

        leases[doc_id] = clauses

        print(f"{doc_id}: {len(clauses)} clauses loaded")

    return leases


# FUNCTION 2:
# Opens the gold JSON file for a particular lease.
# Extracts every entry that contains an evidence line and its page number.
# Returns a list of (field, line, page) tuples.
def load_gold_lines(doc_id: str) -> list[tuple[str, str, int]]:

    gold_path = ROOT / "eval" / "gold" / f"{doc_id}.json"

    with gold_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    gold_lines = []

    for field, entry in data.items():

        if field == "doc_id":
            continue

        line = entry.get("line")

        if not line:
            continue

        page = entry.get("page")

        if page is None:
            raise ValueError(
                f"Missing page for {doc_id}, field {field}"
            )

        gold_lines.append((field, line, page))

    return gold_lines


# FUNCTION 3:
# Builds the search query for the retriever.
# If use_keywords is False, it uses only the predefined question.
# If use_keywords is True, it combines the question with its keywords.
def build_query(question, use_keywords: bool) -> str:

    if not use_keywords:
        return question.text

    keywords = " ".join(question.keywords)

    return f"{question.text} {keywords}"


# FUNCTION 4:
# Evaluates dense embedding retrieval against the gold evidence lines.
# For every gold entry:
# 1. Finds its corresponding predefined question.
# 2. Builds the search query.
# 3. Retrieves the top 5 clauses.
# 4. Identifies the correct clause using gold_clause_indexes().
# 5. Checks Hit@1, Hit@3 and Hit@5 using hit_at_k().
# 6. Records cases where the correct clause is missing from the top 3.
#
# Returns the hit counts, total evaluated entries and misses.
def evaluate(retriever, leases, use_keywords: bool):

    question_map = {
        question.id: question
        for question in QUESTIONS
    }

    hits = {k: 0 for k in KS}
    total = 0
    misses = []

    for doc_id, clauses in leases.items():

        gold_lines = load_gold_lines(doc_id)

        for field, line, page in gold_lines:

            total += 1

            if field not in question_map:
                raise ValueError(
                    f"No question found for gold field: {field}"
                )

            question = question_map[field]

            query = build_query(question, use_keywords)

            ranked = retriever.search(
                lease_id=doc_id,
                query=query,
                k=max(KS),
            )

            gold = gold_clause_indexes(
                clauses=clauses,
                line=line,
                page=page,
            )

            if not gold:
                raise ValueError(
                    f"Gold clause not found: "
                    f"{doc_id}, field={field}, page={page}"
                )

            # Check whether the correct clause appears in the top K.
            for k in KS:
                if hit_at_k(ranked, gold, k):
                    hits[k] += 1

            # If the correct clause is not in the top 3,
            # save the failure details for later investigation.
            if not hit_at_k(ranked, gold, 3):

                gold_titles = [
                    clauses[index].title
                    for index in sorted(gold)
                ]

                top3 = [
                    {
                        "index": index,
                        "title": clauses[index].title,
                    }
                    for index in ranked[:3]
                ]

                misses.append({
                    "lease": doc_id,
                    "field": field,
                    "gold_line": line,
                    "gold_titles": gold_titles,
                    "top3": top3,
                })

    return hits, total, misses


# FUNCTION 5:
# Displays the evaluation results.
# Calculates Hit@1, Hit@3 and Hit@5 percentages.
# Also prints every Hit@3 miss, showing the correct clause
# and the three clauses that the retriever actually returned.
def print_results(name: str, hits: dict, total: int, misses: list):

    print("\n" + "=" * 60)
    print(name)
    print("=" * 60)

    for k in KS:
        percentage = (hits[k] / total) * 100

        print(
            f"Hit@{k}: {percentage:.1f}% "
            f"({hits[k]}/{total})"
        )

    print(f"\nMisses at Hit@3: {len(misses)}")

    for miss in misses:

        print("\n" + "-" * 50)

        print(
            f"Lease: {miss['lease']} | "
            f"Field: {miss['field']}"
        )

        print(f"Gold evidence: {miss['gold_line']}")

        print(f"Gold clause title: {miss['gold_titles']}")

        print("Retrieved top 3:")

        for result in miss["top3"]:
            print(
                f"  Index {result['index']}: "
                f"{result['title']}"
            )


# FUNCTION 6:
# Main controller of the entire evaluation script.
# 1. Loads all five leases.
# 2. Creates the dense embedding retriever.
# 3. Runs evaluation using question-only queries.
# 4. Runs evaluation using question + keywords.
# 5. Checks that exactly 55 gold entries were evaluated.
# 6. Prints the results of both experiments.
def main() -> None:

    print("Loading leases...")

    leases = load_leases()

    print("\nBuilding dense embedding retriever...")

    retriever = EmbeddingRetriever(leases)

    # Experiment 1: Question text only.
    print("\nEvaluating question-only queries...")

    hits_without, total_without, misses_without = evaluate(
        retriever,
        leases,
        use_keywords=False,
    )

    # Experiment 2: Question text + keywords.
    print("\nEvaluating question + keywords...")

    hits_with, total_with, misses_with = evaluate(
        retriever,
        leases,
        use_keywords=True,
    )

    # Ensure both experiments evaluated exactly 55 entries.
    if total_without != 55 or total_with != 55:
        raise ValueError(
            f"Expected 55 gold lines, got "
            f"{total_without} and {total_with}"
        )

    # Display both experiment results.
    print_results(
        "DENSE EMBEDDINGS: QUESTION TEXT ONLY",
        hits_without,
        total_without,
        misses_without,
    )

    print_results(
        "DENSE EMBEDDINGS: QUESTION TEXT + KEYWORDS",
        hits_with,
        total_with,
        misses_with,
    )


# Entry point: execute main() when this file is run directly.
if __name__ == "__main__":
    main()
