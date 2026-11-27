from clauselens.risk.review import needs_review
from clauselens.schemas.lease import Fact


def make_fact(status="found"):
    if status == "found":
        return Fact(
            status="found",
            answer=25000,
            line="Monthly rent is 25000.",
            page=1,
        )

    if status == "unclear":
        return Fact(
            status="unclear",
            answer=None,
            line="The rent amount is ambiguous.",
            page=1,
        )

    return Fact(status="not_stated")


def test_extraction_error_needs_review():
    items = needs_review(
        facts={},
        quote_checks={},
        errors={"monthly_rent": "API error"},
    )

    assert len(items) == 1
    assert items[0].field == "monthly_rent"
    assert items[0].reason == "extraction error"


def test_unclear_fact_needs_review():
    items = needs_review(
        facts={"monthly_rent": make_fact("unclear")},
        quote_checks={},
        errors={},
    )

    assert len(items) == 1
    assert items[0].reason == "unclear"


def test_wrong_page_quote_needs_review():
    items = needs_review(
        facts={},
        quote_checks={"monthly_rent": "wrong_page"},
        errors={},
    )

    assert len(items) == 1
    assert items[0].reason == "quote not verified"


def test_not_found_quote_needs_review():
    items = needs_review(
        facts={},
        quote_checks={"monthly_rent": "not_found"},
        errors={},
    )

    assert len(items) == 1
    assert items[0].reason == "quote not verified"


def test_clean_result_needs_no_review():
    items = needs_review(
        facts={"monthly_rent": make_fact()},
        quote_checks={"monthly_rent": "verified"},
        errors={},
    )

    assert items == []


def test_not_applicable_quote_needs_no_review():
    items = needs_review(
        facts={},
        quote_checks={"monthly_rent": "not_applicable"},
        errors={},
    )

    assert items == []