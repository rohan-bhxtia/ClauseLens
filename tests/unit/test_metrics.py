
from clauselens.schemas.clause import Clause_format
from clauselens.retrieval.metrics import gold_clause_indexes, hit_at_k


def test_gold_clause_indexes_finds_correct_clause():
    clauses = [
        Clause_format(number="1", title="Rent", text="Monthly rent is 20000", page=1),
        Clause_format(number="2", title="Deposit", text="Security deposit is 50000", page=1),
        Clause_format(number="3", title="Notice", text="Notice period is two months", page=2),
    ]

    result = gold_clause_indexes(clauses, "Security deposit is 50000", 1)

    assert result == {1}


def test_gold_clause_indexes_checks_page():
    clauses = [
        Clause_format(number="1", title="Rent", text="Monthly rent is 20000", page=1),
    ]

    result = gold_clause_indexes(clauses, "Monthly rent is 20000", 2)

    assert result == set()


def test_gold_clause_indexes_returns_multiple_matches():
    clauses = [
        Clause_format(number="1", title="Deposit", text="Security deposit is 50000", page=1),
        Clause_format(number="2", title="Other", text="Other information", page=2),
        Clause_format(number="3", title="Deposit Details", text="Security deposit is 50000", page=1),
    ]

    result = gold_clause_indexes(clauses, "Security deposit is 50000", 1)

    assert result == {0, 2}


def test_hit_at_k_finds_gold_clause():
    ranked = [4, 2, 7, 1, 5]
    gold = {7}

    assert hit_at_k(ranked, gold, k=3) is True


def test_hit_at_k_returns_false_outside_top_k():
    ranked = [4, 2, 7, 1, 5]
    gold = {7}

    assert hit_at_k(ranked, gold, k=2) is False


def test_hit_at_k_handles_large_k():
    ranked = [4, 2]
    gold = {2}

    assert hit_at_k(ranked, gold, k=5) is True


def test_hit_at_k_rejects_zero_k():
    import pytest

    ranked = [4, 2]
    gold = {2}

    with pytest.raises(ValueError):
        hit_at_k(ranked, gold, k=0)
