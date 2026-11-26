##checks the output of gemini with gold data 

from clauselens.ingest.parser import normalize

DAYS_PER_UNIT = {"days": 1, "months": 30, "years": 360}


def duration_days(duration: dict) -> int:
    return duration["amount"] * DAYS_PER_UNIT[duration["unit"]]


def answers_equal(gold: object, pred: object) -> bool:
    if isinstance(gold, dict) and isinstance(pred, dict):
        if "unit" in gold and "unit" in pred:
            return duration_days(gold) == duration_days(pred)

        return all(
            key in pred and gold[key] == pred[key]
            for key in gold
        )

    return gold == pred


def lines_match(
    gold_line: str | None,
    pred_line: str | None,
) -> bool:
    if gold_line is None or pred_line is None:
        return False

    gold = normalize(gold_line)
    pred = normalize(pred_line)

    if not gold or not pred:
        return False

    return gold in pred or pred in gold
