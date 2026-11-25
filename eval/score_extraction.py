
"""Score extraction_run1.json against gold (Day 5, Step 6)."""

import json
from collections import Counter, defaultdict
from pathlib import Path

from clauselens.extraction.scoring import answers_equal, lines_match


ROOT = Path(__file__).resolve().parents[1]
GOLD_DIR = ROOT / "eval" / "gold"
RESULTS = ROOT / "eval" / "results" / "extraction_run1.json"

LEASE_IDS = [f"lease_{i:02d}" for i in range(1, 6)]


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as file:
        return json.load(file)


def main() -> None:
    results = load_json(RESULTS)

    status_correct = 0
    answer_correct = 0
    found_total = 0
    not_stated_correct = 0
    not_stated_total = 0
    errors = 0

    quote_counts = Counter()
    status_confusion = Counter()

    line_correct = 0
    line_total = 0
    page_correct = 0
    page_total = 0

    field_counts = defaultdict(
        lambda: {
            "status_correct": 0,
            "status_total": 0,
            "answer_correct": 0,
            "answer_total": 0,
        }
    )

    total_pairs = 0
    misses = []

    for lease_id in LEASE_IDS:
        gold_path = GOLD_DIR / f"{lease_id}.json"
        gold_data = load_json(gold_path)
        lease_results = results[lease_id]

        for field_id, gold_fact in gold_data.items():
            if field_id == "doc_id":
                continue

            total_pairs += 1
            field = field_counts[field_id]
            gold_status = gold_fact["status"]

            entry = lease_results.get(field_id, {})

            # Fixed denominators: count before checking for extraction errors.
            if gold_status == "found":
                found_total += 1
                field["answer_total"] += 1

            if gold_status == "not_stated":
                not_stated_total += 1

            field["status_total"] += 1

            # Extraction errors count as incorrect predictions.
            if "error" in entry or "fact" not in entry:
                errors += 1
                pred_status = "ERROR"
                status_confusion[(gold_status, pred_status)] += 1

                misses.append(
                    (
                        lease_id,
                        field_id,
                        gold_status,
                        gold_fact.get("answer"),
                        "ERROR",
                        entry.get("error"),
                    )
                )
                continue

            pred_fact = entry["fact"]
            pred_status = pred_fact["status"]

            status_confusion[(gold_status, pred_status)] += 1

            # Status accuracy
            status_ok = pred_status == gold_status

            if status_ok:
                status_correct += 1
                field["status_correct"] += 1

            # Answer accuracy: gold found only
            answer_ok = None

            if gold_status == "found":
                answer_ok = (
                    pred_status == "found"
                    and answers_equal(
                        gold_fact.get("answer"),
                        pred_fact.get("answer"),
                    )
                )

                if answer_ok:
                    answer_correct += 1
                    field["answer_correct"] += 1

            # Correctly staying quiet when nothing was stated
            if gold_status == "not_stated" and pred_status == "not_stated":
                not_stated_correct += 1

            # Record status or answer misses
            if not status_ok or answer_ok is False:
                misses.append(
                    (
                        lease_id,
                        field_id,
                        gold_status,
                        gold_fact.get("answer"),
                        pred_status,
                        pred_fact.get("answer"),
                    )
                )

            # Quote verification: only predictions that have a quote
            if pred_fact.get("line") is not None:
                quote_check = entry.get("quote_check")
                quote_counts[quote_check or "missing"] += 1

            # Compare evidence line and page when both have a line
            gold_line = gold_fact.get("line")
            pred_line = pred_fact.get("line")

            if gold_line is not None and pred_line is not None:
                line_total += 1
                page_total += 1

                if lines_match(gold_line, pred_line):
                    line_correct += 1

                if pred_fact.get("page") == gold_fact.get("page"):
                    page_correct += 1

    if total_pairs != 75:
        raise ValueError(
            f"Expected 75 gold pairs, found {total_pairs}. "
            "Check the gold files."
        )

    if found_total != 54 or not_stated_total != 20:
        raise ValueError(
            f"Unexpected gold denominators: found={found_total}, "
            f"not_stated={not_stated_total}. Expected 54 and 20."
        )

    def percentage(correct: int, total: int) -> str:
        if total == 0:
            return "N/A"
        return f"{correct}/{total} ({correct / total * 100:.2f}%)"

    print("\n5 synthetic leases, 75 pairs. Not a general accuracy.\n")

    print("EXTRACTION METRICS")
    print("-" * 65)

    print(f"Status accuracy:                      {percentage(status_correct, 75)}")
    print(f"Answer accuracy:                      {percentage(answer_correct, 54)}")
    print(
        "Stayed quiet when nothing was stated: "
        f"{percentage(not_stated_correct, 20)}"
    )

    quote_total = sum(quote_counts.values())
    print(
        f"Quote verified:                       "
        f"{percentage(quote_counts['verified'], quote_total)}"
    )

    print(f"Line matches gold:                    {percentage(line_correct, line_total)}")
    print(f"Page matches gold:                    {percentage(page_correct, page_total)}")

    print(f"\nExtraction errors: {errors}")

    print("\nQUOTE CHECK COUNTS")
    print("-" * 65)

    for status in ("verified", "wrong_page", "not_found"):
        print(f"{status}: {quote_counts[status]}")

    if quote_counts["missing"]:
        print(f"Missing quote-check result: {quote_counts['missing']}")

    print("\nSTATUS CONFUSION COUNTS")
    print("-" * 65)

    for (gold_status, pred_status), count in sorted(status_confusion.items()):
        print(
            f"Gold: {gold_status:12} "
            f"Predicted: {pred_status:12} Count: {count}"
        )

    print("\nPER-FIELD RESULTS")
    print("-" * 80)
    print(f"{'Field':30} {'Status accuracy':20} {'Answer accuracy':20}")
    print("-" * 80)

    for field_id, counts in sorted(field_counts.items()):
        status_result = percentage(
            counts["status_correct"],
            counts["status_total"],
        )
        answer_result = percentage(
            counts["answer_correct"],
            counts["answer_total"],
        )

        print(f"{field_id:30} {status_result:20} {answer_result:20}")

    print("\nMISSES (status wrong or answer wrong)")
    print("-" * 80)

    for lease, field, g_status, g_answer, p_status, p_answer in misses:
        print(
            f"{lease} {field}: gold={g_status} {g_answer} "
            f"| pred={p_status} {p_answer}"
        )


if __name__ == "__main__":
    main()
