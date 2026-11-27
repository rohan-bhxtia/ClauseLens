"""Run the risk rules on saved run-1 facts (no API calls)."""

import json
from pathlib import Path

from clauselens.risk.rules import check_risks
from clauselens.schemas.lease import LeaseFacts

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "eval" / "results" / "extraction_run1.json"

results = json.loads(RESULTS.read_text(encoding="utf-8"))

for lease_id, fields in results.items():
    facts = {}

    for field_id, entry in fields.items():
        if "fact" not in entry:
            continue

        fact_type = LeaseFacts.model_fields[field_id].annotation
        facts[field_id] = fact_type.model_validate(entry["fact"])

    print(f"\n== {lease_id} ==")

    flags = check_risks(facts)

    if not flags:
        print("No flags")

    for flag in flags:
        print(
            f"[{flag.severity}] {flag.rule_id}: "
            f"{flag.message} (page {flag.page})"
        )