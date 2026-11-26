# F002 — RAG Evaluation & Benchmarking TODO

Canonical task and status source for F002. Mark tasks complete only when acceptance evidence is recorded in the implementation journal and the evaluation report.

## T001 — Create and verify the labelled query set

- **Status:** COMPLETE — 24 balanced, source-verified records and JSONL validation test; evidence in `docs/002-rag-evaluation-benchmarking.md`.
- **Action:** Create 24 source-verifiable queries in `eval/eval.jsonl`, balanced across exact-ID, keyword/phrase, semantic and multi-circular types. Check required fields, expected circular IDs and source PDF identity/content; record source evidence for each label. Do not rely on archive listing pages as PDF pages.
- **Files:** `eval/eval.jsonl`, `tests/test_eval_data.py`, `docs/002-rag-evaluation-benchmarking.md`
- **Requirements / plan:** R006, R010.1; P001, P009, P014
- **Acceptance:** 20–30 valid labelled queries cover all four types; every expected ID is confirmed against an indexed source document, with query/type/expected IDs recorded and no out-of-scope filters, OCR or supersession cases. Automated validation covers JSONL shape and required fields.
- **Dependencies:** None.

## T002 — Implement the compact evaluator and metric tests

- **Status:** NOT STARTED
- **Action:** Add one script that opens the existing local indexes, runs each labelled query through dense, hybrid and hybrid-rerank with F001's 20-candidate/top-five settings, deduplicates ranked chunks by circular ID, and computes per-query Recall@5/MRR plus overall and per-type aggregates. Persist ranked IDs and metrics as JSON. Do not ingest or embed.
- **Files:** `scripts/evaluate_rag.py`, `eval/results.json`, `tests/test_eval_metrics.py`, `docs/002-rag-evaluation-benchmarking.md`
- **Requirements / plan:** R002–R005, R007, R010.2–R010.3, R012; P002–P003, P006–P008, P010, P015
- **Acceptance:** Unit tests cover duplicate-chunk collapse, multiple expected IDs, Recall@5, MRR, per-type aggregation and JSON serialization. Evaluator uses `open_local_indexes` and `retrieve`, keeps limits fixed, uses identical data across modes, and makes rerank calls sequentially. It does not invoke ingestion or embedding construction.
- **Dependencies:** T001.

## T003 — Run full-index retrieval comparison

- **Status:** NOT STARTED
- **Action:** Run the evaluator under `uv` using the existing `data/index`; verify 36,853 persisted nodes and 7,591 distinct indexed source PDF paths from node `pdf_path` metadata against F001's baseline. Report circular-ID coverage separately. Run all 24 queries across all three modes, save actual results and record command, runtime, API behavior and any failures.
- **Files:** `eval/results.json`, `docs/002-rag-evaluation-benchmarking.md`
- **Requirements / plan:** R002–R007, R010.1–R010.3; P003, P008, P011, P013, P015
- **Acceptance:** Evidence confirms the same complete persisted F001 index was used (7,591 distinct indexed source PDF paths / 36,853 nodes), each query ran in all three modes with fixed settings, results contain per-query ranked unique IDs and metrics plus overall/type metrics, and Cohere rerank calls ran sequentially. Circular-ID coverage is reported separately. Any baseline mismatch or failed calls are reported without claiming a complete comparison.
- **Dependencies:** T002 and available local index plus Cohere credentials/network.

## T004 — Generate and manually classify answer samples

- **Status:** NOT STARTED
- **Action:** Select nine representative queries (three per retrieval mode), reuse retrieved passages and the existing GPT-4.1-mini answer pipeline, then manually classify each answer as supported, unsupported or insufficient evidence by checking cited passages. Record brief evidence notes and counts by mode.
- **Files:** `eval/report.md`, `docs/002-rag-evaluation-benchmarking.md`
- **Requirements / plan:** R008–R010.4; P004, P012, P016
- **Acceptance:** Nine generated answers (within the required 5–10 total) are manually checked; each classification is supported by a note about its cited passages; counts distinguish all three grounding classes and identify the three-answer denominator for each mode. No LLM judge or automated claim validator is used.
- **Dependencies:** T003 and available OpenAI credentials/network.

## T005 — Report results and reconcile evidence

- **Status:** NOT STARTED
- **Action:** Produce a concise report with the requested comparison table, query count, fixed retrieval settings, grounding counts and two or three actual examples of improvement, ties or failures. Reconcile requirement → plan → task → implementation → automated/live evidence and record commands, outcomes, failures and limitations in the journal.
- **Files:** `eval/report.md`, `docs/002-rag-evaluation-benchmarking.md`, `docs/002-rag-evaluation-todo.md`
- **Requirements / plan:** R009–R010; P005, P017–P018
- **Acceptance:** The report contains measured Recall@5 and MRR by mode and query type, supported-answer count/sample by mode, and 2–3 sourceable real examples. All 20–30 queries were evaluated on the full baseline index in each mode, nine answers were manually grounded, and the journal separates implementation, automated test, and live verification evidence. No fabricated or inferred measurements are presented as results.
- **Dependencies:** T001–T004.

## Lineage coverage

- R001–R005 → P002, P006, P008, P013, P015 → T002–T003 → evaluator opening persisted indexes with fixed settings; metric/config tests and full-index live evidence.
- R006 → P001, P009, P014 → T001 → labelled query data, source verification evidence and JSONL validation test.
- R007 → P002–P003, P010–P011, P015 → T002–T003 → deduplicated metrics, sequential Cohere execution, unit tests and saved live results.
- R008 → P004, P012, P016 → T004 → GPT-4.1-mini answer samples and manual passage-grounding classifications.
- R009–R010 → P004–P005, P014–P018 → T003–T005 → report metrics/examples, journal evidence and final reconciliation.
- R011–R012 → P006–P008, P018 → T002–T005 → scope constraint, no new dependency, prescribed `uv` checks and documented verification boundaries.

All requirements R001–R012 and plan items P001–P018 are mapped above. Implementation, automated checks, full-index retrieval and manual answer grounding remain separate evidence categories.
