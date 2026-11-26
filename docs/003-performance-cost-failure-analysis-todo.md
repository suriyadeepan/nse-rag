# F003 — Performance, Cost & Failure Analysis TODO

Canonical task and status source for F003. Complete tasks only when implementation, live evidence and report reconciliation are recorded in the journal.

## T001 — Select sample and implement the lightweight benchmark

- **Status:** COMPLETE — sample and sequential benchmark implemented; answer response usage capture confirmed.
- **Action:** Select 10 representative F002-labelled queries across exact-ID, keyword/phrase and semantic types. Add a compact script that opens the existing index, verifies baseline inventory, and runs each query/mode sequentially with one warm-up and three timed repetitions at 20 candidates/top 5. Include rerank time, enforce the 6.2-second Cohere interval, and save per-call data and run context. Inspect existing answer response metadata and support separate answer sampling/token usage if available without invasive changes.
- **Files:** `scripts/benchmark_performance.py`, `eval/performance-results.json`, `docs/003-performance-cost-failure-analysis.md`
- **Requirements / plan:** R001, R005.1; P001–P003, P006–P010
- **Acceptance:** The script uses identical 10 queries, persisted indexes, and retrieval limits across modes; includes one warm-up and three measured calls per query/mode; serializes Cohere requests with pacing; records measured retrieval values, run metadata, and answer usage where exposed. No ingestion or full F002 evaluation occurs. Run under `uv`.
- **Dependencies:** None; existing local index and provider credentials/network required for live execution.

## T002 — Run the live benchmark and cost sample

- **Status:** COMPLETE — full-index benchmark completed with 30 measured calls plus one warm-up per query/mode; evidence and costs recorded in the F003 journal/results.
- **Action:** Run the script against the F001 persisted index; confirm 36,853 nodes and 7,591 source PDF paths before API calls. Capture 10-query/three-mode timings, answer latency and OpenAI input/output usage for a small sample where available, and Cohere usage/cost if exposed. Check OpenAI pricing on the run date and calculate only evidence-supported costs. Record failures and retries.
- **Files:** `eval/performance-results.json`, `docs/003-performance-cost-failure-analysis.md`
- **Requirements / plan:** R001–R002, R005.1–R005.2; P002–P003, P007–P013
- **Acceptance:** Results contain 10 queries × 3 modes × 3 measured calls plus warm-up counts, average and p50 retrieval latency, model/index/limit/date context, and separate answer sample evidence where captured. Cost computation is traceable to usage and dated pricing; missing Cohere/answer usage is explicitly stated. Full-index baseline mismatch prevents measurements.
- **Dependencies:** T001 and live index/API access.

## T003 — Publish compact performance/cost report and failure examples

- **Status:** COMPLETE — comparison reuses F002 scores and three evidence-backed failures are documented.
- **Action:** Reuse F002 Recall@5/MRR without rerunning its full evaluation. Produce the comparison table and cost context. Document at least three observed failures: dense exact-ID miss recovered by hybrid, F002 query 14 semantic rerank rank drop, and Cohere 429 followed by sequential successful retry. Use only the four required fields per failure and do not speculate on causes.
- **Files:** `eval/performance-report.md`, `eval/failure-analysis.md`, `docs/003-performance-cost-failure-analysis.md`
- **Requirements / plan:** R002–R005; P001, P003–P006, P008–P010, P013–P014
- **Acceptance:** Three-mode table values agree with F002 saved scores and F003 raw timing/usage evidence. Failure artifact contains at least three real examples with query/operation, expected/actual result, failure/known cause, and practical fix/limitation only. The $0.24 one-time embedding estimate is separated from query cost.
- **Dependencies:** T002; F002 result/report/journal artifacts.

## T004 — Reconcile evidence and close F003

- **Status:** COMPLETE — result/report values reconciled and evidence limits recorded in the journal.
- **Action:** Check requirement → plan → task → implementation → live evidence/artifact lineage; reconcile all report numbers against saved JSON; record commands, results, failures and evidence limits in the journal. Do not add or run automated tests for this measurement-only scope.
- **Files:** `docs/003-performance-cost-failure-analysis-todo.md`, `docs/003-performance-cost-failure-analysis.md`, `eval/performance-results.json`, `eval/performance-report.md`, `eval/failure-analysis.md`
- **Requirements / plan:** R001–R006; P001–P015
- **Acceptance:** Report and artifacts agree; task statuses reflect evidence; implementation, live provider measurements and manual artifact review are identified separately. No fabricated result or unverified success is claimed.
- **Dependencies:** T001–T003.

## Lineage coverage

- R001 → P001–P003, P006–P012 → T001–T002 → benchmark implementation and live timing/usage evidence.
- R002 → P003–P004, P007, P009–P010, P013 → T001–T003 → token/price inputs, cost estimates and report evidence.
- R003 → P001, P004, P008, P014 → T003 → failure examples checked against F002 artifacts and journal.
- R004 → P001, P004, P006, P013, P015 → T002–T004 → compact comparison and reconciled result artifacts.
- R005 → P002–P004, P011–P015 → T002–T004 → acceptance evidence for full index, traceable cost, real failures and aligned report.
- R006 → P005, P015 → T001–T004 → scope limits preserved; no full rerun, dashboard or expanded benchmarking.
