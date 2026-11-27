
"""Identify extracted answers that need human review (Day 6)."""

from pydantic import BaseModel

from clauselens.schemas.lease import Fact


# SECTION 1: Define the structure of one review item
class ReviewItem(BaseModel):
    field: str
    reason: str  # "extraction error" | "unclear" | "quote not verified"


# SECTION 2: Identify all fields that need human review
def needs_review(
    facts: dict[str, Fact],
    quote_checks: dict[str, str],
    errors: dict[str, str],
) -> list[ReviewItem]:

    review_items = []

    # CHECK 1: Find fields where extraction produced an error
    for field in errors:
        review_items.append(
            ReviewItem(
                field=field,
                reason="extraction error",
            )
        )

    # CHECK 2: Find facts where Gemini returned an unclear answer
    for field, fact in facts.items():
        if fact.status == "unclear":
            review_items.append(
                ReviewItem(
                    field=field,
                    reason="unclear",
                )
            )

    # CHECK 3: Find quotes that could not be verified
    for field, status in quote_checks.items():
        if status in ("wrong_page", "not_found"):
            review_items.append(
                ReviewItem(
                    field=field,
                    reason="quote not verified",
                )
            )

    # SECTION 3: Return all review items in one list
    return review_items
