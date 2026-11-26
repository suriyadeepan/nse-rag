# NSE Circular RAG

A local proof of concept for searching the existing NSE PDF/metadata collection with dense or hybrid retrieval and generating answers with inspectable PDF citations.

## Requirements

- Python 3.14 and [`uv`](https://docs.astral.sh/uv/)
- Existing files under `data/pdfs/*.pdf` and `data/metadata/*.json`
- An OpenAI API key for embedding and answer generation
- A Cohere trial/API key only when using `hybrid-rerank`

Corpus PDFs and metadata are local inputs and are not downloaded by these commands. Chroma vectors and BM25 node data are stored locally under `data/index/`. PDF text is sent to OpenAI for embeddings; retrieved candidate passages are sent to Cohere only in `hybrid-rerank` mode. Keep Cohere queries sequential and within your account's rate limits.

## Setup

```bash
uv sync
cp -n .env.example .env
```

Edit `.env` and set `OPENAI_API_KEY`. Set `COHERE_API_KEY` to enable reranking. Keep `.env` private; it is ignored by Git. Commands below load it through `uv`.

If your corpus is not already present, use the existing downloader separately. RAG ingestion itself uses only local files.

## Build the full local index

```bash
uv run --env-file .env nse-rag ingest
```

This processes all sorted `data/pdfs/*.pdf` files, matches per-document JSON metadata under `data/metadata/`, and builds a fresh local Chroma collection plus its matching BM25 corpus. The command reports PDFs found, metadata records loaded, documents indexed/skipped and chunks indexed. Re-running `ingest` replaces the POC collection and `data/index/nodes.jsonl`.

Optional input/output paths and embedding batch size:

```bash
uv run --env-file .env nse-rag ingest \
  --pdf-dir data/pdfs \
  --metadata-dir data/metadata \
  --index-dir data/index \
  --batch-size 128
```

## Ask questions

```bash
uv run --env-file .env nse-rag query "What changed in circular NSE/CMTR/123?" --mode dense
uv run --env-file .env nse-rag query "Which trading requirements changed?" --mode hybrid
uv run --env-file .env nse-rag query "Which trading requirements changed?" --mode hybrid-rerank
```

Modes are `dense`, `hybrid` (local BM25 + dense retrieval with reciprocal rank fusion), and `hybrid-rerank` (hybrid followed by one Cohere rerank request). All use the same defaults: 20 candidates and 5 final passages. Adjust them with `--candidate-top-k` and `--top-k`; the candidate limit must be at least the result limit.

Answers use GPT-4.1-mini and display cited circular IDs, actual 1-based PDF page numbers, and supporting passages. The CLI also checks answer claims against their cited sources and labels each **Supported**, **Unsupported**, or **Needs review**. If a check fails or source mapping is incomplete, it defaults to **Needs review**; claim splitting and source mapping can be approximate, so labels are an aid rather than a guarantee. The linked source passages remain visible for inspection. If retrieved evidence is insufficient or cannot be cited, the CLI says so rather than guessing. The listing metadata `page` field is never used as a PDF page citation.

## Retrieval evaluation

We compared dense, hybrid (BM25 + dense with reciprocal rank fusion), and hybrid with Cohere reranking on the persisted full index: 7,591 PDFs and 36,853 chunks. F002 used the same 24 source-verified queries and retrieval limits (20 candidates, top 5) for each mode. Scores are document-level; duplicate chunks from one circular count once. F003 measured latency separately using 10 representative queries (2 exact-ID, 4 keyword/phrase, 4 semantic), with one warm-up and three measured repetitions per query/mode.

| Metric | Dense | Hybrid | Hybrid + Rerank |
|---|---:|---:|---:|
| Recall@5 | 0.4375 | 0.7083 | 0.7292 |
| MRR | 0.4063 | 0.5708 | 0.7153 |
| Supported answers (sample) | 3/3 | 3/3 | 3/3 |
| Retrieval latency — average (F003) | 0.769 s | 0.698 s | 1.464 s |
| Retrieval latency — p50 (F003) | 0.516 s | 0.521 s | 1.275 s |
| Approx. query cost | ~$0.0000004* | ~$0.0000004* | ~$0.0000004*; Cohere unavailable |

Nine GPT-4.1-mini answers (three per mode) were manually checked against cited passages; all nine were supported. The separate F003 answer sample used hybrid retrieval: five answers averaged 1.863 s and cost $0.0032728 total (about $0.000655 per sampled answer, or $0.000656 including one estimated query embedding). The `~$0.0000004` table estimates are query-embedding cost only, not account usage; Cohere usage was unavailable. F001's one-time full-corpus embedding cost remains an approximately $0.24 estimate and was not incurred again. OpenAI prices were checked on 2026-11-26.

Reranking improved the overall scores, though semantic-query Recall@5 fell to 0.5000, below dense and hybrid (both 0.6667). See the [F002 evaluation report](eval/report.md) for query-type breakdowns and answer evidence; [ranked results](eval/results.json) contain per-query IDs and metrics. See the [F003 performance report](eval/performance-report.md), [raw measurements](eval/performance-results.json), and [failure analysis](eval/failure-analysis.md) for benchmark details and limitations.

## Development checks

```bash
uv run pytest
```

The test suite uses mock embeddings, answer models and rerankers; it does not make paid API calls. Full-corpus embedding and live API validation are separate checks.
