
def build_extraction_prompt(
    question: str,
    clauses: list,
) -> str:
    """
    Build an extraction prompt using retrieved clauses.
    """

    clause_text = "\n\n".join(
        f"Page {clause.page}:\n{clause.text}"
        for clause in clauses
    )

    return f"""
You are a rental agreement fact extraction system.

Answer the question using ONLY the retrieved clauses.

QUESTION:
{question}

RETRIEVED CLAUSES:
{clause_text}

RULES:
1. Use only the provided clauses.
2. Never assume or invent information.
3. If the answer is not explicitly available,
   return status as "not_stated".
4. If found, provide the extracted answer.
5. Provide an exact verbatim supporting quote.
6. Provide the page number of the supporting quote.
""".strip()
