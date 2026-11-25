## this file is ot chekc whether the evidence/quote that gemini give ..
#  present in the actual pdf 


"""Check that a Fact's quote exists on its cited page (Day 5, Step 4)."""

from clauselens.ingest.parser import normalize
from clauselens.schemas.clause import Block_format


def build_page_text(blocks: list[Block_format]) -> dict[int, str]:
    """Combine all blocks belonging to each page."""
    pages: dict[int, list[str]] = {}

    for block in blocks:
        pages.setdefault(block.page, []).append(block.text)

    return {
        page: normalize(" ".join(texts))
        for page, texts in pages.items()
    }


def verify_quote(fact, page_text: dict[int, str]) -> str:
    """Check whether the fact's quote exists on its cited page."""
    if fact.line is None:
        return "not_applicable"

    needle = normalize(fact.line)

    if not needle:
        return "not_found"

    # First, check the page cited by Gemini.
    if fact.page in page_text:
        cited_page = normalize(page_text[fact.page])
        if needle in cited_page:
            return "verified"

    # Then, check whether the quote exists on another page.
    for page, text in page_text.items():
        if page != fact.page and needle in normalize(text):
            return "wrong_page"

    return "not_found"
