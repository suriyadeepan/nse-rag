# F003 — Performance, Cost & Failure Analysis Requirements

## Objective

Measure practical latency and API cost for the three retrieval modes on the full F001 corpus (7,591 indexed PDFs; 36,853 chunks), then document a few meaningful failures observed in F002. Reuse existing code and results. [R001]

## Requirements

### R001 — Lightweight latency benchmark

- **R001.1** Benchmark `dense`, `hybrid`, and `hybrid-rerank` using the same persisted F001 indexes and F002 query set.
- **R001.2** Use 10 representative queries, mixing exact-ID, keyword and semantic types, from `eval/eval.jsonl`.
- **R001.3** Run one warm-up and three measured repetitions per query and mode. Run sequentially and respect Cohere's trial rate limit.
- **R001.4** Measure retrieval latency; include the Cohere rerank call in `hybrid-rerank` retrieval time.
- **R001.5** Measure GPT-4.1-mini answer latency separately for the same small sample only if straightforward to capture.
- **R001.6** Report average and p50 latency. Do not report p95 or perform concurrency, cold-start or hardware profiling.
- **R001.7** Record corpus/index counts, candidate top-k, final top-k, model names and run date.

### R002 — Simple cost estimate

- **R002.1** Reuse F001's recorded corpus embedding estimate of approximately $0.24 USD for 36,853 chunks / 11.8M input tokens. Label it an estimate, not account billing.
- **R002.2** For a small sample of answer queries, record OpenAI input/output token usage and estimate GPT-4.1-mini cost using provider pricing checked on the run date.
- **R002.3** Record Cohere rerank usage/cost for the benchmark if API response or account usage makes it available. Otherwise state that it is unavailable; do not invent a figure.
- **R002.4** Report approximate variable cost per evaluated query where usage data supports it.
- **R002.5** Keep corpus ingestion cost separate from query-time cost. Do not create an amortization model or cost dashboard.

### R003 — Short failure analysis

- **R003.1** Create `eval/failure-analysis.md` with at least three observed examples from F002 or the F003 benchmark.
- **R003.2** Prioritize dense missing an exact circular ID that hybrid retrieves; reranking lowering a relevant semantic result (for example F002 query 14); and a Cohere HTTP 429 followed by a successful sequential retry.
- **R003.3** For each example, record only: query or operation; expected and actual result; what failed and likely cause, if known; practical fix or limitation.
- **R003.4** Add other failures only if encountered during F003. Do not perform an exhaustive corpus audit or invent root causes without evidence.

### R004 — Compact comparison

- **R004.1** Publish a compact three-mode table containing Recall@5, MRR@5, retrieval latency average and p50, and approximate query cost.
- **R004.2** Reuse F002 retrieval scores; do not rerun the full evaluation to reproduce them.
- **R004.3** Include corpus size, benchmark query count, run count and the separate one-time embedding estimate.

## Acceptance criteria

- **R005.1** All three modes are measured on the same full persisted corpus, query set and retrieval limits.
- **R005.2** Cost figures are traceable to token/usage data and provider pricing dated to the run; unavailable usage is explicitly marked.
- **R005.3** At least three real failure examples are documented without speculative root causes.
- **R005.4** A concise comparison report is saved and matches recorded measurements.

## Out of scope

- **R006.1** Production load/concurrency tests, cold-start infrastructure profiling, extensive statistical benchmarking or p95 guarantees.
- **R006.2** Detailed forecasting/amortization, dashboards/monitoring, exhaustive failure taxonomy, corpus audit or automated root-cause analysis.

## Implementation principle

Reuse F001 indexes and F002 queries, metrics and answer code. Measure a small representative sample, record what evidence supports, and stop. [R001–R006]
