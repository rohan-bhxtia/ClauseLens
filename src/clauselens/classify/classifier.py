
"""Is this document a residential lease? (Day 6)"""

from typing import Literal

from pydantic import BaseModel

from clauselens.llm.router import call_with_fallback


class DocClassification(BaseModel):
    doc_type: Literal[
        "residential_lease",
        "other_contract",
        "not_a_contract",]
    reason: str
# both doctype and reason are part of schema

def build_classifier_prompt(first_page_text: str) -> str:
    return f"""You are a document classification system.

Use ONLY the document text provided below.

Classify the document into exactly one of these categories:

- residential_lease:
  An Indian residential rental agreement or leave and licence agreement.

- other_contract:
  Any other kind of contract.

- not_a_contract:
  A document that is not a contract, such as an invoice,
  resume, or letter.

Give a one-sentence reason for your classification.

Document text:
---
{first_page_text}
---
"""


def classify_document(
    client,
    settings,
    cache,
    first_page_text: str,
) -> DocClassification:

    # 1. Build prompt using only the first 3000 characters
    prompt = build_classifier_prompt(first_page_text[:3000])

    # 2. Get the expected JSON structure from Pydantic
    schema = DocClassification.model_json_schema()

    # 3. Call Gemini through our existing LLM Router
    result = call_with_fallback(
        client,
        settings,
        prompt,
        cache,
        None,
        schema,
    )

    # 4. Validate Gemini's JSON response
    return DocClassification.model_validate_json(result.text)
