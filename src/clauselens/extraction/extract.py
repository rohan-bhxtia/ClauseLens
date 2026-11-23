
"""Extract one typed Fact from retrieved clauses (Day 5, Step 3b)."""

from pydantic import ValidationError

from clauselens.extraction.prompt import build_extraction_prompt
from clauselens.llm.router import call_with_fallback
from clauselens.schemas.clause import Clause_format
from clauselens.schemas.lease import LeaseFacts


class ExtractionError(Exception):
    """Gemini's reply was still invalid after one repair attempt."""


def extract_fact(
    client,
    settings,
    cache,
    field_id: str,
    question_text: str,
    clauses: list[Clause_format],
):
    # 1. Get the Fact type for the requested field.
    fact_type = LeaseFacts.model_fields[field_id].annotation

    # 2. Generate its JSON schema.
    schema = fact_type.model_json_schema()

    # 3. Build the extraction prompt.
    prompt = build_extraction_prompt(question_text, clauses)

    # 4. Call Gemini with structured output.
    result = call_with_fallback(
        client,
        settings,
        prompt,
        cache,
        None,
        schema,
    )

    # 5. Validate Gemini's JSON response.
    try:
        return fact_type.model_validate_json(result.text)

    except ValidationError as error:
        # 6. Give Gemini one chance to repair invalid JSON.
        repair_prompt = (
            prompt
            + "\n\nYour previous reply was invalid:\n"
            + str(error)
            + "\nReturn corrected JSON only."
        )

        repair_result = call_with_fallback(
            client,
            settings,
            repair_prompt,
            cache,
            None,
            schema,
        )

        try:
            return fact_type.model_validate_json(repair_result.text)

        except ValidationError as last_error:
            raise ExtractionError(
                f"Extraction failed for field '{field_id}' "
                "after one repair attempt."
            ) from last_error
