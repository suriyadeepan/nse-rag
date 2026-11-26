# F003 — Performance, Cost & Failure Analysis

## Objective

Measure practical latency and API cost for the three retrieval modes on the **full F001 corpus** (7,591 indexed PDFs; 36,853 chunks), then document a few meaningful failures observed in F002. Reuse existing code and results.

## Requirements

### R001 — Lightweight latency benchmark

- Benchmark `dense`, `hybrid`, and `hybrid-rerank` using the same persisted F001 indexes and F002 query set.
- Use **10 representative queries** (mix exact-ID, keyword and semantic) from `eval/eval.jsonl`.
- Run one warm-up and **3 measured repetitions per query/mode**. Run sequentially and respect Cohere's trial rate limit.
- Measure retrieval latency. For `hybrid-rerank`, include the Cohere rerank call in retrieval time.
- Measure GPT-4.1-mini answer latency separately for the same small sample only if straightforward to capture.
- Report average and p50 latency. Skip p95, concurrency testing, cold-start analysis and hardware profiling.
- Record basic context: corpus/index counts, candidate top-k, final top-k, model names and run date.

### R002 — Simple cost estimate

- Reuse F001's recorded corpus embedding estimate: approximately **$0.24 USD** for 36,853 chunks / 11.8M input tokens. Label it an estimate, not account billing.
- For a small sample of answer queries, record OpenAI input/output token usage and estimate GPT-4.1-mini cost using provider pricing checked on the run date.
- Record Cohere rerank usage/cost for the benchmark if the API response or account usage makes it available. If unavailable, state that clearly rather than inventing a figure.
- Report approximate variable cost per evaluated query where usage data supports it.
- Keep corpus ingestion cost separate from query-time cost. No amortization model or cost dashboard.

### R003 — Short failure analysis

Create `failure-analysis.md` with **at least three observed examples** from F002 or the F003 benchmark.

Prioritize:
- Dense retrieval missing an exact circular ID that hybrid retrieves.
- Reranking lowering the rank of a relevant semantic result (e.g. F002 query 14).
- Cohere rate-limit response (HTTP 429) and the successful sequential retry.

For each example, record only:
- Query or operation.
- Expected and actual result.
- What failed and likely cause, if known.
- Practical fix or limitation.

Add other failures only if encountered during this. Do not perform an exhaustive corpus audit or invent root causes without evidence.

### R004 — Compact comparison

Publish a small table for the three modes:

| Metric | Dense | Hybrid | Hybrid + Rerank |
|---|---:|---:|---:|
| Recall@5 | Use F002 | Use F002 | Use F002 |
| MRR@5 | Use F002 | Use F002 | Use F002 |
| Retrieval latency — average | TBD | TBD | TBD |
| Retrieval latency — p50 | TBD | TBD | TBD |
| Approx. query cost | TBD | TBD | TBD |

Include corpus size, benchmark query count, run count and the separate one-time embedding estimate. Reuse F002 retrieval scores; do not rerun the full evaluation just to reproduce them.

## Acceptance criteria

- All three modes measured on the same full persisted corpus.
- Latency measured with the same queries and retrieval limits.
- Cost figures are traceable to token/usage data and dated provider pricing; unavailable usage is explicitly marked.
- At least three real failure examples documented without speculative root causes.
- A concise comparison report is saved and matches the recorded measurements.

## Out of scope

- Production load or concurrency tests.
- Extensive repeated-run statistical benchmarking or p95 guarantees.
- Cold-start infrastructure profiling.
- Detailed cost forecasting or amortization models.
- Exhaustive failure taxonomy, corpus audit or automated root-cause analysis.
- Dashboards, monitoring or production performance infrastructure.

## Implementation principle

Reuse F001 indexes, F002 queries, metrics and answer code. Measure a small representative sample, record what the evidence supports, and stop.
