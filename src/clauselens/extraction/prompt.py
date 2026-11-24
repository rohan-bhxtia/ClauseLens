"""Prompt builder for fact extraction (Day 5)."""

from clauselens.schemas.clause import Clause_format


def build_extraction_prompt(
    question: str,
    clauses: list[Clause_format],
) -> str:

    clause_text = "\n\n".join(
        f"Page {clause.page} | {clause.title}:\n{clause.text}"
        for clause in clauses
    )

    return f"""
You are a rental agreement fact extraction system.

Answer the question using ONLY the retrieved clauses below.

QUESTION:
{question}

RETRIEVED CLAUSES:
{clause_text}

RULES:
1. Use only the provided clauses. Never assume or invent information.
2. status = "found" when the clauses clearly state the answer.
3. status = "not_stated" when the clauses do not state the answer.
   Do not guess from what leases usually contain.
4. status = "unclear" when the clauses mention the topic but the wording
   is ambiguous or contradictory. Give the quote and page that show it,
   and no answer.
5. The quote must be ONE single unbroken sentence copied character for
   character from the clauses. No "...", no joining two lines, no fixing
   typos, no paraphrasing.
6. The page is the page number shown for the clause the quote came from.
7. Write amounts as plain digits, for example 32000 instead of Rs 32,000.

Put the exact quote in the "line" field.
""".strip()
