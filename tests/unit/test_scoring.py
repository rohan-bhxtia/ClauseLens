
import pytest

from clauselens.extraction.scoring import (
    answers_equal,
    duration_days,
    lines_match,
)


@pytest.mark.parametrize(
    ("gold", "pred", "expected"),
    [
        (
            {"amount": 60, "unit": "days"},
            {"amount": 2, "unit": "months"},
            True,
        ),
        (
            {"amount": 12, "unit": "months"},
            {"amount": 1, "unit": "years"},
            True,
        ),
        (
            {"amount": 30, "unit": "days"},
            {"amount": 2, "unit": "months"},
            False,
        ),
        (
            {"percent": 5, "when": "every_year"},
            {"percent": 5, "when": "on_renewal"},
            False,
        ),
        (
            {"amount": 1000, "payer": "tenant"},
            {"amount": 1000, "payer": "landlord"},
            False,
        ),
        (5, 5.0, True),
    ],
)
def test_answers_equal(gold, pred, expected):
    assert answers_equal(gold, pred) is expected


def test_duration_days():
    assert duration_days({"amount": 60, "unit": "days"}) == 60


def test_lines_match_gold_is_prefix():
    assert lines_match(
        "The agreement shall remain valid for 12 months",
        "The agreement shall remain valid for 12 months from the commencement date",
    )


@pytest.mark.parametrize(
    ("gold", "pred"),
    [
        (None, "Some evidence"),
        ("Some evidence", None),
        (None, None),
    ],
)
def test_lines_match_none(gold, pred):
    assert lines_match(gold, pred) is False
