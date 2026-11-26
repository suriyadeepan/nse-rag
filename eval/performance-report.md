# F003 Performance, Cost & Failure Report

## Run context

- **Run date:** 2026-11-26 UTC
- **Index:** Full persisted F001 corpus — 7,591 source PDF paths, 36,853 chunks, 7,591 distinct circular IDs.
- **Benchmark sample:** 10 F002 queries: 2 exact-ID, 4 keyword/phrase, 4 semantic.
- **Runs:** One warm-up plus three measured repetitions per query/mode; 30 measured calls and 10 warm-ups per mode. Sequential; Cohere requests spaced by at least 6.2 seconds.
- **Limits/models:** 20 candidates, final top 5; `text-embedding-3-small`, `rerank-v5.0-fast`, `gpt-4.1-mini`.

## Comparison

| Metric | Dense | Hybrid | Hybrid + Rerank |
|---|---:|---:|---:|
| Recall@5 (F002, 24 queries) | 0.4375 | 0.7083 | 0.7292 |
| MRR@5 (F002, 24 queries) | 0.4063 | 0.5708 | 0.7153 |
| Retrieval latency — average | 0.769 s | 0.698 s | 1.464 s |
| Retrieval latency — p50 | 0.516 s | 0.521 s | 1.275 s |
| Approx. query cost | ~$0.0000004 embedding estimate | ~$0.0000004 embedding estimate; answer sample below | ~$0.0000004 embedding estimate; Cohere charge unavailable |

F002 scores are reused from [`results.json`](results.json); the 24-query evaluation was not rerun. Timings include retrieval and, for hybrid-rerank, the Cohere call. Averages and p50 use 30 measured calls per mode. Timing spread was substantial in a few local retrieval calls, so these small-sample figures are descriptive rather than latency guarantees.

The embedding estimate per retrieval is based on an average 19.9 input tokens per selected query and OpenAI's $0.02/M-token `text-embedding-3-small` price. It is not account usage. Five GPT-4.1-mini answers used 7,270 input and 228 output tokens, costing **$0.0032728 total** at $0.40/M input and $1.60/M output (about **$0.000655 per sampled answer**). Adding one estimated query embedding gives about **$0.000656 per sampled hybrid answer query**, excluding unavailable Cohere charges. Those answer samples used hybrid retrieval; answer latency averaged 1.863 seconds. The answer sample is separate from the per-retrieval estimates in the table.

Cohere cost is **unavailable**: the existing LlamaIndex wrapper does not expose the raw rerank response's usage, and account-level usage was not queried. No rerank cost is included in the table. OpenAI prices were checked on 2026-11-26 against the [official pricing page](https://developers.openai.com/api/docs/pricing); embedding price is also listed on the [text-embedding-3-small page](https://developers.openai.com/api/docs/models/text-embedding-3-small). Cohere's [Rerank 5 pricing announcement](https://cohere.com/blog/rerank-5) lists Rerank 5 Fast at $0.02/M tokens, but the measured token usage needed to calculate this run's charge is unavailable.

F001's one-time corpus embedding cost remains a separate **approximately $0.24 estimate** for 36,853 chunks / 11.8M tokens. It was not incurred again for F003 and is not account billing.

Raw timing samples and usage are in [`performance-results.json`](performance-results.json). Three observed failures are in [`failure-analysis.md`](failure-analysis.md). Commands, source checks and reconciliation evidence are in the F003 journal.
