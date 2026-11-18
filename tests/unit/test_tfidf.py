
import pytest

from clauselens.retrieval.tfidf import TfidfRetriever
from clauselens.schemas.clause import Clause_format


@pytest.fixture
def retriever():
    leases = {
        "lease_01": [
            Clause_format(
                number="1",
                title="Security Deposit",
                text="The tenant must pay a security deposit of fifty thousand rupees.",
                page=1,
            ),
            Clause_format(
                number="2",
                title="Notice Period",
                text="Either party must provide two months notice before termination.",
                page=2,
            ),
        ],
        "lease_02": [
            Clause_format(
                number="1",
                title="Rent",
                text="Monthly rent is twenty thousand rupees.",
                page=1,
            ),
            Clause_format(
                number="2",
                title="Maintenance",
                text="The tenant is responsible for monthly maintenance charges.",
                page=2,
            ),
            Clause_format(
                number="3",
                title="Lock-in Period",
                text="The agreement has a lock-in period of eleven months.",
                page=3,
            ),
            Clause_format(
                number="4",
                title="Termination",
                text="The landlord may terminate the agreement after written notice.",
                page=4,
            ),
            Clause_format(
                number="5",
                title="Renewal",
                text="The agreement may be renewed with mutual consent.",
                page=5,
            ),
        ],
    }

    return TfidfRetriever(leases)


def test_relevant_clause_ranks_first(retriever):
    results = retriever.search(
        lease_id="lease_01",
        query="security deposit",
        k=2,
    )

    assert results[0] == 0


def test_results_are_best_first(retriever):
    results = retriever.search(
        lease_id="lease_01",
        query="notice period termination",
        k=2,
    )

    assert len(results) == 2
    assert results[0] == 1


def test_returns_at_most_k_results(retriever):
    results = retriever.search(
        lease_id="lease_01",
        query="rent payment",
        k=1,
    )

    assert len(results) <= 1


def test_searches_only_requested_lease(retriever):
    results = retriever.search(
        lease_id="lease_01",
        query="maintenance charges",
        k=5,
    )

    assert len(results) == 2
    assert all(index in [0, 1] for index in results)


def test_unknown_lease_raises_error(retriever):
    with pytest.raises(ValueError, match="Unknown lease_id"):
        retriever.search(
            lease_id="lease_99",
            query="security deposit",
            k=2,
        )


def test_search_matches_clause_title(retriever):
    results = retriever.search(
        lease_id="lease_01",
        query="security deposit",
        k=2,
    )

    assert results[0] == 0


def test_k_must_be_positive(retriever):
    with pytest.raises(ValueError, match="k must be at least 1"):
        retriever.search(
            lease_id="lease_01",
            query="security deposit",
            k=0,
        )
