# F004 — POC Quality Checks (Metadata & Citations) Journal

## Implementation

- Extended `SourceReference` with optional indexed `title` and `date`; answer prompts and CLI citations preserve these values when present. No metadata is repaired or inferred.
- Added an LLM-based claim check using the existing GPT-4.1-mini completion model. It asks for strict JSON claim text, cited source IDs and **Supported / Unsupported / Needs review**. Unknown source IDs, missing mappings, malformed responses, or validator errors fail closed to **Needs review**. Each claim result retains its linked source references and passages.
- CLI output shows claim text/status plus circular ID, title/date when available, actual PDF page and passage. It states that automated checks are an aid, not a guarantee. The answer prompt asks the model to identify IDs/dates and describe duplicate/conflicting-version ambiguity without deciding supersession.
- Metadata filters were omitted. Chroma dense retrieval and the existing BM25 retriever do not expose an existing shared mechanism for the same metadata condition before RRF; implementing it would require custom branch-level filter behavior, which is outside this POC.
- No dependency, ingestion behavior, metadata schema, persisted index or index contents were changed.

## Citation integrity evidence

- Source artifact: `eval/citation-check.md`.
- Manually inspected five saved F002 answer outputs and all seven citation instances, covering five unique circular/page pairs. Every ID mapped to the recorded indexed PDF; every actual page was within page bounds; the stated supporting text was present on that page. All passed. This does not establish claim entailment beyond the cited excerpts.

## Claim validation evidence

- Source artifact: `eval/claim-validation.md`.
- Ran five F002 queries through hybrid retrieval with 20 candidates/top 5 against the existing index and used GPT-4.1-mini for each answer and claim validation. Query 9 was run a second time to inspect its claim/source mapping compactly. Four representative claims were marked Supported and manually confirmed against the actual source page. A date-specific claim about the November 21, 2026 SLBM session was marked Needs review because its mapped passage came from a June session; this was the correct conservative result. No obvious false positive/negative was found in the reviewed examples.
- Claim checking is approximate: the validator can split or map claims incorrectly, and a Supported status is not a guarantee. The exact source passage remains visible beside each status.

## Commands and verification

- `uv run pytest tests/test_answer.py tests/test_cli.py` — 10 passed, 6 dependency deprecation warnings.
- `uv run python` opening `open_local_indexes()` — reopened 36,853 persisted nodes with BM25 available. No ingestion or index rebuild ran.
- Manual PDF inspection used the indexed `pdf_path` for each circular and PyMuPDF to inspect the listed 1-based page number. Full per-answer and per-claim observations are recorded in the two eval artifacts.
- No full test suite, production deployment or exhaustive claim-entailment evaluation was run; none is required for this POC scope.
