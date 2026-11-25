
from types import SimpleNamespace

from clauselens.extraction.verify import verify_quote


def test_verified():
    fact = SimpleNamespace(
        line="Rent is 25000.",
        page=1,
    )
    page_text = {
        1: "The tenant shall pay Rent is 25000. every month.",
        2: "The agreement starts in January.",
    }

    assert verify_quote(fact, page_text) == "verified"


def test_wrong_page():
    fact = SimpleNamespace(
        line="Rent is 25000.",
        page=1,
    )
    page_text = {
        1: "The tenant shall pay rent every month.",
        2: "Rent is 25000.",
    }

    assert verify_quote(fact, page_text) == "wrong_page"


def test_not_found():
    fact = SimpleNamespace(
        line="Rent is 50000.",
        page=1,
    )
    page_text = {
        1: "Rent is 25000.",
        2: "The agreement starts in January.",
    }

    assert verify_quote(fact, page_text) == "not_found"


def test_not_applicable():
    fact = SimpleNamespace(
        line=None,
        page=None,
    )
    page_text = {
        1: "Rent is 25000.",
    }

    assert verify_quote(fact, page_text) == "not_applicable"


def test_spacing_difference_still_verifies():
    fact = SimpleNamespace(
        line="Rent is 25000.",
        page=1,
    )
    page_text = {
        1: "Rent is  25000.",
    }

    assert verify_quote(fact, page_text) == "verified"
