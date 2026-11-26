# F004 — POC Quality Checks (Metadata & Citations) TODO

Canonical task and status source for F004. Keep implementation, automated tests, manual PDF checks, and live LLM validation evidence separate in the journal.

## T001 — Add lightweight claim validation and richer source metadata

- **Status:** COMPLETE — claim validation, metadata references and fail-closed unit coverage implemented.
- **Action:** Extend the existing answer flow with claim-level statuses, cited-source mappings and an automated-aid caveat. Use only citations associated with each factual claim; fail closed to **Needs review** when the validator response or mapping is invalid. Include existing title/date metadata in source references when available. Add focused unit tests for all statuses, invalid output, evidence mapping and missing metadata.
- **Files:** `src/nse_rag/answer.py`, `tests/test_answer.py`
- **Requirements / plan:** R002.1, R003, R004.2–R004.3; P001–P002, P009–P011
- **Acceptance:** Existing answer/citation behavior remains compatible; claim results include circular ID, actual page and passage; missing title/date are omitted rather than invented; invalid validator output cannot appear as **Supported**. Tests cover these behaviors.
- **Dependencies:** None.

## T002 — Display claim checks and evidence in the query CLI

- **Status:** COMPLETE — CLI renders claim statuses, references, metadata and the automated-aid notice.
- **Action:** Render claim text, status, associated source IDs/dates/pages and passage alongside the generated answer. Clearly label automated validation as an aid, not a guarantee. Show available title/date metadata in the regular references and describe surfaced duplicate/conflicting source ambiguity without assigning supersession.
- **Files:** `src/nse_rag/cli.py`, `tests/test_cli.py`
- **Requirements / plan:** R002.1, R003.2–R003.6, R004.2–R004.3; P001–P002, P007, P010–P011
- **Acceptance:** Query output exposes a status and inspectable evidence for each validated claim, retains circular ID/actual PDF page/passage citations, and includes the automated-aid note. Any ambiguity wording names only available IDs/dates and makes no supersession decision. CLI tests cover output.
- **Dependencies:** T001.

## T003 — Manually verify five existing evaluation answers

- **Status:** COMPLETE — checked five saved answers and all seven citation instances against five indexed source/page pairs.
- **Action:** Select five representative fact answers from saved F002/F003 evaluation evidence. Map every citation to an indexed source PDF, check page bounds, inspect the actual PDF page text, and record pass/fail plus issues and limitations.
- **Files:** `eval/citation-check.md`, `docs/004-poc-quality-checks.md`
- **Requirements / plan:** R002, A003–A004; P004, P014
- **Acceptance:** Five answers and all their citations are documented with circular-ID/PDF mapping, page-range result, page-text result and pass/fail. Report integrity only; do not claim entailment coverage.
- **Dependencies:** None.

## T004 — Validate five representative factual claims

- **Status:** COMPLETE — five factual claims were checked against source PDF pages and results recorded, including one appropriate Needs review case.
- **Action:** Run the lightweight claim validator on representative factual answers, manually compare at least five claims with their cited source pages, and record results plus any obvious false positives/negatives.
- **Files:** `eval/claim-validation.md`, `docs/004-poc-quality-checks.md`
- **Requirements / plan:** R003, A005–A006; P001, P005, P015
- **Acceptance:** At least five claim/status/evidence examples are manually checked and recorded, including false-positive/negative observations if found. Failures or unavailable LLM access are documented without claiming validation succeeded.
- **Dependencies:** T001–T002.

## T005 — Verify compatibility, document limitations and converge

- **Status:** COMPLETE — focused tests passed; existing 36,853-node index reopened without ingestion or migration; artifacts and limitation recorded.
- **Action:** Run focused checks under `uv`; verify existing local indexes reopen and query without ingestion/rebuild or migration; confirm metadata-filter limitation is documented; reconcile requirement → plan → task → implementation/test/manual evidence, update this TODO and the journal, and identify any unresolved gaps.
- **Files:** `tests/test_answer.py`, `tests/test_cli.py`, `src/nse_rag/answer.py`, `src/nse_rag/cli.py`, `docs/004-poc-quality-checks-todo.md`, `docs/004-poc-quality-checks.md`, `docs/004-poc-quality-checks-plan.md`
- **Requirements / plan:** R001, A001–A007, O001–O006; P003, P006–P008, P013–P016
- **Acceptance:** Focused checks and existing-index compatibility evidence are recorded; no ingestion or schema migration occurs; all report values are evidence-backed; any missing live/manual verification remains visibly incomplete rather than marked complete.
- **Dependencies:** T001–T004.

## Lineage coverage

- R001 → P003 → T005 → documented retrieval limitation and report.
- R002 → P002, P004, P007, P011–P012, P014 → T001–T003, T005 → source metadata display, five-answer PDF inspection and recorded evidence.
- R003 → P001, P005, P007, P009–P010, P015–P016 → T001–T002, T004–T005 → implemented claim checks, tests, CLI output and five manual claim reviews.
- R004 → P002, P006, P011, P013 → T001–T002, T005 → metadata display and ambiguity behavior without supersession logic.
- A001–A007 → P001–P016 → T001–T005 → automated, manual PDF, live LLM and compatibility evidence.
- O001–O006 → P006, P008, P013, P016 → T001–T005 → no ingestion framework, index migration, governance system or production infrastructure.
