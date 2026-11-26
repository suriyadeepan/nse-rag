# F003 — Performance, Cost & Failure Analysis Plan

## Scope and approach

- **P001** Select 10 labelled rows from `eval/eval.jsonl` covering exact-ID, keyword/phrase and semantic queries. Reuse F002's saved results for Recall@5/MRR and its documented failures. Do not rerun the 24-query evaluation. [R001, R003.1–R003.4, R004.1–R004.3]
- **P002** Add a compact benchmark script that opens F001's persisted `data/index`, verifies 36,853 nodes / 7,591 source PDF paths, then runs the same 10 queries in all three modes using `RetrievalSettings(20, 5)`. For each query/mode, make one warm-up call and three sequential timed calls. Include Cohere call time in reranked retrieval latency and preserve Cohere's minimum 6.2-second interval between requests. Record average and median (p50). Do not add concurrency, cold-start, p95 or hardware profiling. [R001.1–R001.4, R001.6–R001.7, R004.1, R005.1]
- **P003** For a small subset of those queries, call the existing GPT-4.1-mini answer path separately; record answer latency and response input/output token usage when exposed by the completion response. Check official OpenAI model pricing on the actual run date and calculate sample-based answer cost. Report query-time components and per-query estimate only where usage evidence supports it. Record Cohere usage/cost only if API/account evidence provides it; otherwise label unavailable. Keep the F001 $0.24 corpus embedding estimate separate from query-time cost. [R001.5, R002.1–R002.5]
- **P004** Save raw benchmark evidence and metadata to `eval/performance-results.json`; publish the compact comparison table and run context in `eval/performance-report.md`. Add the three required observed cases to `eval/failure-analysis.md`, using only the four requested fields and sourceable F002/F003 evidence. [R003–R005]
- **P005** Do not change retrieval/index architecture, rebuild indexes, rerun full F002 scoring, add dependencies, fabricate unavailable provider usage, or extend this into a cost dashboard/statistical benchmark. [R001.6, R002.3–R002.5, R003.4, R004.2, R006]

## Affected files and dependencies

- **P006** Add `scripts/benchmark_performance.py`, `eval/performance-results.json`, `eval/performance-report.md`, and `eval/failure-analysis.md`; add the F003 journal `docs/003-performance-cost-failure-analysis.md`; update only F003's feature state. Reuse `eval/eval.jsonl`, `eval/results.json`, `nse_rag.index_store`, `nse_rag.retrieval`, and `nse_rag.answer`. [R001–R005]
- **P007** Use the existing `uv` environment and locked dependencies. The live benchmark requires the local persisted index, network access and Cohere credentials; answer/cost sampling also requires OpenAI credentials. Add no dependency. [R001–R002]

## Compatibility matrix

| Area | Status | Evidence / validation |
|---|---|---|
| Python runtime | VERIFIED for project configuration; local `python3` is 3.15.2 | `pyproject.toml` requires Python >=3.14; F002 records the configured CPython 3.14 `uv` environment. Run implementation via `uv`, not the unrelated system interpreter. |
| CPU architecture | VERIFIED: arm64 Darwin | `uname -sm` returned `Darwin arm64`. |
| Native dependencies | VERIFIED for existing stack | F001/F002 record successful imports and tests with ChromaDB, ONNX Runtime, PyMuPDF and LlamaIndex. F003 adds no native dependency. |
| Container format | UNKNOWN / not applicable | No container configuration is used by this local benchmark. |
| Deployment target | VERIFIED: local developer machine | `data/index` and `data/index/nodes.jsonl` exist; benchmark reopens the existing local Chroma/BM25 state. Confirm exact index inventory immediately before the live run and stop on mismatch. |
| External services | VERIFIED as existing integrations; F003 live availability pending | F001/F002 record OpenAI and Cohere use and local `.env` configuration. Do not print secrets. Confirm live service availability during implementation; Cohere requests remain serial and paced. |

Automated compatibility checks: run the script under `uv`; verify its persisted index inventory against the F001 baseline before requests and ensure the generated JSON contains query/mode/run counts, timing samples and available usage fields. Provider pricing is a dated external source check on the benchmark run date.

## Risks and mitigations

- **P008** Cohere's trial rate limit can interrupt repeated measurements: serialize calls and maintain at least the already-used 6.2-second interval; record a 429 and retry outcome as observed. [R001.3, R003.2]
- **P009** A small sample may be noisy and an API response may omit usage: report only requested average/p50, disclose sample/run counts, and mark unavailable costs rather than inferring them. [R001.6, R002.2–R002.4]
- **P010** OpenAI response usage shape may not be exposed through the current LlamaIndex wrapper: inspect the returned response object during implementation; if absent, use the least invasive existing response metadata path, otherwise report usage/cost unavailable and do not claim a token-based estimate. [R001.5, R002.2, R005.2]

## Acceptance and validation

- **P011** Run 10 representative queries against one verified 36,853-node / 7,591-source-PDF persisted index in all three modes, with shared 20-candidate/top-five limits, one warm-up and three measured repetitions per query/mode. Rerank calls are sequential and timed end-to-end. [R001, R005.1]
- **P012** Report average and p50 retrieval latencies, and separate answer latency where captured. Record model names, counts, date, candidate/final top-k and each measured sample in results. [R001.4–R001.7]
- **P013** Reconcile F002 Recall@5/MRR into the report without rerunning the full evaluation; trace cost estimates to captured token/usage data and run-date provider pricing, separate the $0.24 ingestion estimate, and mark unavailable usage explicitly. [R002, R004]
- **P014** Document at least three real failures in `eval/failure-analysis.md` with only query/operation, expected/actual, failure/known cause, and practical fix/limitation; cross-check each example against F002 artifacts/journal. [R003, R005.3]
- **P015** Reconcile report values with raw result samples and verify the benchmark artifacts and F003 journal record actual commands, results and evidence limits. No automated test additions or test runs are planned for this measurement-only feature; live acceptance is the benchmark run and artifact reconciliation. [R004–R005]
