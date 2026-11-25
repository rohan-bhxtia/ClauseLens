# ClauseLens — Progress

Started: 2026-10-19 · Plan: 10 build days + 3 buffer days (counting build days, not calendar days)

## Versions

| Version | Day | What you can do with it |
|---|---|---|
| v0.1 | 1 | 15 questions in code + checked answers (gold) for 5 leases + tests |
| v0.2 | 2 | Read PDFs and split them into clauses with page numbers |
| v0.3 | 3 | Talk to Gemini reliably (retry, backup model, response cache) |
| v0.4 | 4 | Find the right clauses for a question (accuracy measured) |
| v0.5 | 5 | AI fills the 15 facts; each checked against the PDF; first accuracy number |
| v0.6 | 6 | Classifier (is this a lease?) + risk checks + human review of unsure answers |
| v0.7 | 7 | Ask questions, get answers with clause citations; backend API |
| v0.8 | 8 | One-command accuracy report; safety tests; hide personal data |
| v0.9 | 9 | Web page + Docker |
| v1.0 | 10 | GitHub-ready: README, diagram, real numbers, demo |
| extra | 11–13 | Catch up first; then compare two leases |

## Day 1 — DONE (2026-10-24)

Built:
- Project set up with uv (pyproject.toml, uv.lock, .gitignore)
- `src/clauselens/schemas/lease.py` — 15 questions + 3 rules (found / not_stated / unclear), written by Rohan
- `eval/gold/lease_01..05.json` — 75 answers, every quoted line verified to exist on its page, reviewed by Rohan
- `tests/test_lease.py` — gold files valid + checker rejects broken data
- First git commit

Test results: all tests passed.

Found:
- ₹ symbol extracts incorrectly from some PDFs → handled on Day 2
- Tests caught a real bug: "licence" vs "license" spelling mismatch
- All 5 leases are GPT-made, clean style → add 3–5 real public templates later
- `late_fee` is not_stated in all 5 leases → cannot be scored yet

Decisions:
- Every fact = answer + exact line + page + status
- v1 = leases only; other contract types = new schema file later
- Cut from v1: deposit-deduction reasons list; names/addresses never extracted
- Classifier (doc type) is separate from LLM Router

## Day 2 — DONE (2026-10-24 → 2026-10-27)

Built:
- Added Gemini (`google-genai`), `python-dotenv` and `docling`
- First Gemini API call works — `gemini-3.1-flash-lite`, key read from `.env`
- `scripts/peek_raw.py` — converts lease PDFs into text with Docling
- `scripts/peek_items.py` — inspects Docling labels and page numbers
- `src/clauselens/schemas/clause.py` — `Block_format` and `Clause_format`
- `src/clauselens/ingest/parser.py`:
  - `parse_pdf()` converts PDFs into blocks with page numbers
  - `clean_text()` fixes the corrupted rupee symbol and escaped underscores
  - `normalize()` standardizes whitespace and quotation marks for comparisons only
- `src/clauselens/ingest/chunker.py`:
  - `groupBlocks_toClauses()` groups blocks at headings
  - Text before the first heading becomes "Preamble"
  - Each clause retains its starting page
- `scripts/realPass_chunker.py` — runs the chunker on leases 02–05 and checks clause counts
- Parser and chunker unit tests

Real PDF results:
- lease_02 = 17 clauses
- lease_03 = 18 clauses
- lease_04 = 17 clauses
- lease_05 = 18 clauses
- All matched the expected counts.

Test results: 27 passed.

Found:
- Docling reads headings, clause numbers and paragraphs correctly
- ₹ came out as "n" (e.g. "n32,000") → fixed in `clean_text()`
- Sub-clause identifiers are now preserved as strings (e.g. "2.1", "2.10", "2.1.3")

Cleaned up:
- `src/clauselens/schemas/1.py` deleted
- `scratch/` removed from git and ignored; files remain on disk
- `.DS_Store` ignored

## Day 3 — DONE (2026-10-28 → 2026-11-03): LLM Router

Built:
- `src/clauselens/config.py`:
  - `Settings` reads the Gemini key and options from `.env`
  - Primary model: `gemini-3.1-flash-lite`
  - Backup model: `gemini-3.5-flash-lite`
  - Retry count, wait times, request timeout and cache directory
  - `get_settings()` loads settings once and reuses them
- `src/clauselens/llm/router.py`:
  - `LLMResult` — stores response text, model, input/output/thought tokens and latency
  - `make_client()` — creates the Gemini client with a timeout and disables SDK retries
  - `call_gemini()` — makes one Gemini call and rejects empty responses
  - `call_with_retry()` — checks the cache first, then retries temporary API failures
  - `call_with_fallback()` — tries the primary model and switches to the backup when appropriate
- `src/clauselens/llm/cache.py`:
  - Creates a SHA-256 cache key from the model, prompt and system instruction
  - Saves responses as JSON files
  - Retrieves previously saved responses
- `scripts/try_router.py` — manually checks the backup model, normal primary call and forced fallback
- `tests/unit/test_router.py` — automated router tests using mocked Gemini responses

Test results:
- 34 passed
- 6 deprecation warnings from Docling/Pydantic dependencies
- Router unit tests cover cache hits, cache writes, retries, non-retryable errors and fallback behaviour
- Manual Gemini checks confirmed that both models work and the fallback path is reached

Found:
- SDK retries could multiply our own retries → disabled SDK retries
- A 404 (invalid model name) cannot be fixed by retrying the same model → fallback handles it
- Cache hits avoid repeating identical requests

Decisions:
- Stay on the Gemini free tier
- No pricing configuration or cost logging in the router
- Router remains separate from lease-specific extraction logic
- Router unit tests use mocks; real Gemini calls are checked separately through `scripts/try_router.py`

Build days used: 3 of 13

## Day 4 — DONE (2026-11-17 → 2026-11-20): Clause Retrieval

Built:
- `src/clauselens/retrieval/questions.py` — retrieval questions for the 15 lease facts, with keywords
- `src/clauselens/retrieval/metrics.py` — gold-clause matching and Hit@k rules
- `src/clauselens/retrieval/tfidf.py` — TF-IDF baseline retriever with per-lease filtering
- `src/clauselens/retrieval/embeddings.py` — `EmbeddingRetriever`:
  - Embeds clauses with `sentence-transformers/all-MiniLM-L6-v2`
  - Stores them in a Chroma vector DB (cosine distance) with lease_id, clause index, number, title and page
  - Rebuilds the `lease_clauses` collection on each run so stale clauses never leak into results
  - Searches only within the requested lease; rejects unknown lease_ids and k < 1
- `eval/run_retrieval.py` — measures Hit@1/3/5 against the gold evidence and prints every miss
- `scripts/try_embeddings.py` — quick manual check of the embedding model (renamed from `test_embeddings.py` so pytest doesn't collect it)
- Tests for questions, gold-clause matching, metrics, TF-IDF and embeddings (lease isolation, unknown lease, invalid k)

Results (55 question–lease pairs, 5 synthetic leases):

| Method | Query | Hit@1 | Hit@3 | Hit@5 |
|---|---|---|---|---|
| TF-IDF | question only | 69.1% (38/55) | 83.6% (46/55) | 90.9% (50/55) |
| TF-IDF | + keywords | 76.4% (42/55) | 92.7% (51/55) | 92.7% (51/55) |
| Dense (Chroma) | question only | 74.5% (41/55) | 96.4% (53/55) | 98.2% (54/55) |
| Dense (Chroma) | + keywords | 80.0% (44/55) | 100% (55/55) | 100% (55/55) |

Test results:
- 60 passed
- Warnings are deprecation notices from Docling/Pydantic dependencies

Found:
- Reusing an existing Chroma collection kept old clauses around → delete and recreate it on every build
- Chroma rejects `None` metadata values → untitled clauses store `""` as title
- A file named `scripts/test_*.py` gets picked up by pytest → renamed to `try_embeddings.py`
- Question-only misses were in lease_02 (agreement_type, rent_increase); adding keywords fixed both

Decisions:
- No BM25 + RRF and no reranker: dense hit@3 is 96.4% (question only) and 100% (with keywords), above the ~90% threshold. Revisit if real, messier leases are added.
- Chroma instead of Qdrant, and sentence-transformers (all-MiniLM-L6-v2) instead of FastEmbed: chosen for familiarity and schedule. This deviates from the original stack; swapping is one file because the interface is `search(lease_id, query, k)`.

Known gaps:
- Only 55 pairs on 5 synthetic, clean-style leases: results are indicative, not general.
- Keywords were written before measuring, but the misses were read afterwards. More keyword tuning on these same 55 would overfit.
- agreement_type has more than one valid evidence clause (the title clause also says it); the metric counts only the gold clause.
- TF-IDF with a query that matches nothing returns clauses in original order, which means nothing.

Build days used: 4 of 13

## Day 5 — DONE (2026-11-20 → 2026-11-25): Structured Fact Extraction

Built:
- `src/clauselens/extraction/prompt.py` — `build_extraction_prompt()`: question + the 3 retrieved clauses (page and title shown), rules for found / not_stated / unclear, one exact quoted sentence, amounts as plain digits
- `src/clauselens/extraction/extract.py` — `extract_fact()`:
  - Takes the schema from the `LeaseFacts` field type, so there are no 15 hand-written schemas
  - Calls the router with `response_schema`; Pydantic validates the reply into a typed `Fact`
  - Invalid reply → one repair retry with the Pydantic error added to the prompt, then `ExtractionError`
- `src/clauselens/extraction/verify.py` — `build_page_text()` and `verify_quote()`: checks the quote against the whole PDF page (not only the retrieved clauses); returns verified / wrong_page / not_found / not_applicable
- `src/clauselens/extraction/scoring.py` — comparison rules, written before looking at results: durations compared in days (1 month = 30 days, 1 year = 360), dict answers must match every gold key, everything else exact; a line matches gold if either normalized line contains the other
- Router change: `response_schema` argument (JSON mode via `response_json_schema`) passed through `call_gemini`, `call_with_retry` and `call_with_fallback`; the cache key includes the schema only when one is given, so old cached keys stay valid
- `scripts/try_extract.py` — one question on one lease, prints the typed Fact
- `eval/run_extraction.py` — 5 leases × 15 questions: retrieve top 3 → extract → verify; saves `eval/results/extraction_run1.json` after every question; one failed question does not stop the run
- `eval/score_extraction.py` — scores run 1 against gold with fixed denominators
- Tests: `test_extract.py` (3, fake router), `test_verify.py` (5), `test_scoring.py`, `test_router.py` updated for the schema argument

Test results:
- 80 passed, 21 warnings (deprecation notices from Docling/Pydantic dependencies); run on Mac with `uv run pytest -q`
- New this day: extraction (3), verification (5), scoring, and router tests updated for the response schema

Results (run 1: 5 synthetic leases, 75 pairs. Not a general accuracy):

| Metric | Result |
|---|---|
| Status accuracy | 71/75 (94.67%) |
| Answer accuracy (gold found only) | 52/54 (96.30%) |
| Stayed quiet when nothing was stated | 17/20 (85.00%) |
| Quote verified on the cited page | 57/57 (100%) |
| Line matches gold | 51/55 (92.73%) |
| Page matches gold | 55/55 (100%) |
| Extraction errors | 1 |
| Quote check outcomes | verified 57, wrong_page 0, not_found 0 |

Status confusion: found→found 53, found→unclear 1, not_stated→not_stated 17, not_stated→unclear 2, not_stated→ERROR 1, unclear→unclear 1.

The 5 misses, with causes (read from the saved results):
- lease_03 landlord_can_end_early: gold found, predicted unclear. Clauses 7A (60 days) and 7B (90 days) conflict on notice; both say the landlord can end early. Model was over-cautious. Real model miss.
- lease_04 landlord_can_end_early: gold false, predicted true. Both used the "termination for material breach" sentence; the question does not say "without cause". Question wording gap.
- lease_05 maintenance and deposit_refund_time: gold not_stated, predicted unclear. The lease text itself says it does not specify these, so unclear is defensible. Gold-definition gap between not_stated and unclear.
- lease_05 late_fee: the one error. Gemini returned status found with a null answer; the repair attempt returned the same. Pydantic correctly rejected it.

The 4 line mismatches are alternate but valid evidence (for example lease_02 agreement_type quotes the title where gold quotes the fee line), not fabricated quotes.

Found:
- Asking for a format in the prompt gave loose text ("Page 1", "N/A"); a response schema gave real integers and nulls
- The cache key must include the schema, or typed and untyped calls would return each other's cached replies
- Retrying with the same prompt would hit the cached bad reply → the repair prompt includes the error, so it is a new request
- Gemini sometimes says "found" with an empty answer when it means "not stated"; the repair step fixed this once (lease_05 deposit_refund_time, which became unclear with the same quoted sentence) and failed once (lease_05 late_fee)
- `verified` only proves the sentence exists on the cited page, not that it supports the answer
- The first primary-model call hit a 503 (overload) and the router used the backup model; the backup accepted the schema

Decisions:
- Run 1 is the baseline. The prompt was not tuned on these 5 leases. If a rule such as "if the lease says it is unspecified, use not_stated" is added later, it is reported as a separate run, labelled as changed after seeing run 1 misses.
- Gold files were not edited after seeing results.
- `response_json_schema` with a plain schema dict is used instead of passing the Pydantic class
- LangGraph retry workflow stays out of v0.5; the single repair retry covers the small version
- Quote check uses the whole PDF page, independent of retrieval

Known gaps:
- Only 5 synthetic, clean-style leases (75 pairs): results are indicative, not general accuracy
- Some calls in the run were served by the backup model (at least lease_02 total_length); the results file does not record which model answered
- A quote that spans a page break would be reported as not_found
- No unit test that the response schema changes the cache key (skipped by choice)
- Two gold cases (lease_05 maintenance, deposit_refund_time) sit on the not_stated vs unclear boundary; one question (landlord_can_end_early) is ambiguous
- agreement_type and conflict cases have more than one valid evidence line; the metric counts only the gold line
- Extraction errors from Gemini API failures are recorded per question, but this run had none (the only error was an invalid reply)

Build days used: 5 of 13 (Day 5 took 6 calendar days, 2026-11-20 → 2026-11-25)

## Remaining Days

Day 6 — Lease classifier, risk checks and human review.

Day 7 — Question answering with clause citations and backend API.

Day 8 — Accuracy report, safety tests and personal-data protection.

Day 9 — Web page and Docker.

Day 10 — README, architecture diagram, measured results and demo.

Days 11–13 — Buffer, catch-up and lease comparison.

---

**Current milestone:** PDF ingestion, Gemini Router, clause retrieval (Hit@3 = 100%) and structured fact extraction with quote verification (status 94.67%, answer 96.30%, 0 fabricated quotes on 5 synthetic leases) are complete. Next is Day 6: lease classifier, risk checks and human review.