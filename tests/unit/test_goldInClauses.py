# we are testing this btwn gold data and our parser and chunker that our 
# evidence should come same. both extraction and gold data should match
import json
from pathlib import Path

import pytest

from clauselens.ingest.parser import parse_pdf, normalize
from clauselens.ingest.chunker import groupBlocks_toClauses


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
GOLD_DIR = ROOT / "eval" / "gold"


@pytest.fixture(scope="module")
def parsed_leases():
    """Parse all five PDFs once and reuse their clauses."""

    leases = {}

    for pdf_path in sorted(DATA_DIR.glob("lease_*.pdf")):
        doc_id = pdf_path.stem

        blocks = parse_pdf(str(pdf_path))
        clauses = groupBlocks_toClauses(blocks)

        leases[doc_id] = clauses

    return leases

# to pass tests with different input values 
@pytest.mark.parametrize(
    "gold_file",
    sorted(GOLD_DIR.glob("lease_*.json")),
    ids=lambda path: path.stem,
)
def test_gold_lines_exist_in_clauses(gold_file, parsed_leases):

    with open(gold_file, encoding="utf-8") as f:
        gold = json.load(f)

    doc_id = gold["doc_id"]
    clauses = parsed_leases[doc_id]


    checked = 0

    for field, entry in gold.items():

        if field == "doc_id" or entry["status"] != "found":
            continue

        line = normalize(entry["line"])
        page = entry["page"]

        evidence_exists = any(
            line in normalize(clause.text) and clause.page == page
            for clause in clauses
        )

        assert evidence_exists, (
            f"{doc_id}: {field} not found on page {page}"
        )

        checked += 1
    print(f"{doc_id}: checked {checked} gold lines")    

    assert checked > 0, f"No gold evidence checked for {doc_id}"
