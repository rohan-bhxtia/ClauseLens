
from types import SimpleNamespace

import pytest

from clauselens.extraction import extract
from clauselens.schemas.clause import Clause_format

VALID = '{"status": "found", "answer": 25000, "line": "Rent is 25000.", "page": 1}'
BAD = "this is not json"

CLAUSES = [
    Clause_format(
        number="1",
        title="RENT",
        text="Rent is 25000.",
        page=1,
    )
]


def run(monkeypatch, replies):
    """Fake router: returns each reply in order, records every call."""
    calls = []

    def fake(client, settings, prompt, cache, system_instruction, response_schema):
        calls.append((prompt, response_schema))
        return SimpleNamespace(text=replies[len(calls) - 1])

    monkeypatch.setattr(extract, "call_with_fallback", fake)
    return calls


def test_valid_reply_returns_fact(monkeypatch):
    calls = run(monkeypatch, [VALID])

    fact = extract.extract_fact(
        None, None, None, "monthly_rent", "Rent?", CLAUSES
    )

    assert fact.answer == 25000
    assert fact.page == 1
    assert len(calls) == 1


def test_bad_then_good_uses_repair_prompt(monkeypatch):
    calls = run(monkeypatch, [BAD, VALID])

    fact = extract.extract_fact(
        None, None, None, "monthly_rent", "Rent?", CLAUSES
    )

    assert fact.answer == 25000
    assert len(calls) == 2
    assert "Your previous reply was invalid" in calls[1][0]
    assert calls[1][0] != calls[0][0]


def test_bad_twice_raises(monkeypatch):
    calls = run(monkeypatch, [BAD, BAD])

    with pytest.raises(extract.ExtractionError):
        extract.extract_fact(
            None, None, None, "monthly_rent", "Rent?", CLAUSES
        )

    assert len(calls) == 2
