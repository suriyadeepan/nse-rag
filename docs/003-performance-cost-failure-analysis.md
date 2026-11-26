# F003 — Performance, Cost & Failure Analysis Journal

## T001 — Benchmark implementation

- Added `scripts/benchmark_performance.py`, reusing the F002 JSONL and retrieval/answer modules. The fixed sample uses eval rows 1–2 (exact-ID), 7–10 (keyword/phrase), and 13–16 (semantic).
- The script verifies persisted node/source counts before provider requests, then runs one warm-up and three measured calls for each query/mode at 20 candidates/top 5. All 40 Cohere rerank calls are serial with a 6.2-second minimum interval; rerank latency is timed end-to-end.
- Five answer samples use the saved hybrid results from the same benchmark queries. A small wrapper captures LlamaIndex `CompletionResponse.additional_kwargs` token usage and measures answer latency without recording answer text. The available `prompt_tokens` / `completion_tokens` fields confirmed answer token usage was exposed.
- Estimated query embedding tokens use `cl100k_base` and published `text-embedding-3-small` input price; they are explicitly marked estimated, not account usage. The existing LlamaIndex Cohere wrapper does not expose raw rerank response usage.

## T002 — Live benchmark and cost sample

- Command: `uv run --env-file .env python scripts/benchmark_performance.py`.
- Completed on 2026-11-26 UTC against the persisted F001 index: 36,853 nodes, 7,591 distinct source PDF paths and 7,591 circular IDs. No ingestion or embedding rebuild ran.
- Completed 10 queries × 3 modes, each with 10 warm-ups total per mode and 30 measured calls per mode. No terminal Cohere or OpenAI request failure occurred. The full serial run took about 5.5 minutes.
- Retrieval average / p50: dense 0.769 / 0.516 seconds; hybrid 0.698 / 0.521 seconds; hybrid-rerank 1.464 / 1.275 seconds. Each statistic uses 30 measured calls; raw values are in `eval/performance-results.json`.
- Five GPT-4.1-mini answers (using hybrid retrieved passages) averaged 1.863 seconds. OpenAI reported 7,270 input and 228 output tokens. At run-date prices of $0.40/M input and $1.60/M output, estimated answer cost is $0.0032728 total ($0.000655 per sampled answer).
- The 120 retrieval invocations used an estimated total of 2,388 query-embedding tokens (about $0.0000478 at $0.02/M tokens); this is tokenizer-derived, not account-reported usage. Cohere usage/cost is unavailable from the wrapper, and account usage was not queried. No rerank charge is claimed.
- Run-date pricing sources checked 2026-11-26: OpenAI [pricing](https://developers.openai.com/api/docs/pricing), [text-embedding-3-small](https://developers.openai.com/api/docs/models/text-embedding-3-small), and Cohere [Rerank 5 pricing announcement](https://cohere.com/blog/rerank-5). The F001 $0.24 corpus embedding estimate remains a separate one-time estimate and was not incurred by this benchmark.

## T003 — Report and failure examples

- `eval/performance-report.md` reuses F002's 24-query scores (no evaluation rerun): Recall@5 / MRR are 0.4375 / 0.4063 dense, 0.7083 / 0.5708 hybrid, and 0.7292 / 0.7153 hybrid-rerank.
- `eval/failure-analysis.md` records: F002 query 1 exact-ID miss by dense with hybrid recovery; F002 query 14 relevant semantic target lost below reranked top five; and the observed F002 Cohere HTTP 429 followed by a successful 6.2-second-paced retry. No unverified root cause is asserted.
- The comparison report distinguishes per-retrieval embedding estimate from the sampled answer cost and marks Cohere cost unavailable.

## T004 — Evidence reconciliation

- The saved benchmark artifact records the full-index inventory, selected query lines/types, warm-up and measured counts, shared settings, model names, per-call timing samples, answer token usage, dated prices and unavailable Cohere usage.
- Reconciled average/p50 against all 30 timing samples per mode; reconciled answer token totals and cost against five response records; compared report retrieval scores with `eval/results.json`; checked failure examples against F002 saved rankings and journaled rate-limit evidence.
- No automated tests were added or run for this measurement-only work, consistent with the approved plan. Live benchmark completion and artifact reconciliation are recorded separately from automated test evidence.
