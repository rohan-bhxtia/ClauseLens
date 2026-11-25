# ClauseLens

**Know what you're signing before you sign it.**

Upload an Indian rental agreement (PDF). ClauseLens extracts key terms (rent, deposit, lock-in, notice period…), shows the exact source quote and page for each answer, and flags risky clauses.

> Informational only. Not legal advice.

## Status

🚧 In progress. **Day 5 of 10 done. Day 6 is next.**

Working so far:
- 15 key lease questions defined, with hand-checked answers for 5 test leases
- PDF reading with page numbers using Docling, including a fix for the corrupted ₹ symbol
- Text normalisation (spaces and curly quotes) for reliable quote matching
- Splitting leases into clauses while preserving clause numbers, titles and starting pages
- Settings loaded from `.env` (API key, models, retry options and cache directory)
- Gemini LLM Router with retry logic and automatic backup-model fallback
- JSON response cache to avoid repeating identical Gemini requests
- Router unit tests using mocked Gemini responses
- Manual integration checks against the real Gemini API
- Clause retrieval: Hit@3 100% on 55 gold lines, 5 synthetic leases (dense embeddings, question + keywords)
- Structured fact extraction: Gemini returns a typed fact (status, answer, quoted line, page) validated by Pydantic, with one repair retry
- Source-quote verification: every quote is checked against the cited PDF page
- First extraction result on 5 synthetic leases (75 pairs): status 94.67%, answer 96.30%, 57/57 quotes verified, 1 extraction error. Not a general accuracy.

## Next

- Lease classifier (is this a lease?), risk checks and human review of unsure answers
- Question answering with clause citations and a backend API

Day-by-day log: [PROGRESS.md](PROGRESS.md)

## How accuracy is measured

- 5 synthetic test leases with 15 hand-checked answers each (`eval/gold/`)
- Retrieval and extraction are measured separately
- Retrieval: Hit@k on the 55 gold evidence lines
- Extraction: status, answer, quote-exists, line and page match are reported separately (`eval/score_extraction.py`)
- All numbers come from 5 synthetic, clean-style leases, so they are indicative, not general accuracy. Known gaps are listed in [PROGRESS.md](PROGRESS.md).

## Run tests

```bash
uv sync
uv run pytest
```
