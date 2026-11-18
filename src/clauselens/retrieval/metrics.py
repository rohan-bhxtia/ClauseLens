## this is the evaluation logic of our retrieval...
# it return true or false for hit@k .. like :
# Question	               Hit@1	Hit@3	Hit@5
# Monthly rent	            False	True	True
# Security deposit	         True	True	True
# Notice period	            False	False	True
# Lock-in period	         True	True	True


from collections.abc import Sequence

from clauselens.schemas.clause import Clause_format
from clauselens.ingest.parser import normalize


def gold_clause_indexes(
    clauses: Sequence[Clause_format],
    line: str, 
    page: int
    ) -> set[int]:
    """Find clause positions containing the gold line on the given page."""

    needle = normalize(line)

    return {
        index
        for index, clause in enumerate(clauses)
        if needle in normalize(clause.text) and clause.page == page
    }


def hit_at_k(
        ranked: list[int],   # this will come from tfidf 
        gold: set[int], 
        k: int
        ) -> bool:
    """Check whether any gold clause appears in the top K results."""

    if k < 1:
        raise ValueError(f"k must be at least 1, got {k}")

    return any(index in gold for index in ranked[:k])
