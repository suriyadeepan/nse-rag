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

Answers use GPT-4.1-mini and display cited circular IDs, actual 1-based PDF page numbers, and supporting passages. If retrieved evidence is insufficient or cannot be cited, the CLI says so rather than guessing. The listing metadata `page` field is never used as a PDF page citation.

## Retrieval evaluation

We compared dense, hybrid (BM25 + dense with reciprocal rank fusion), and hybrid with Cohere reranking on the persisted full index: 7,591 PDFs and 36,853 chunks. The same 24 source-verified queries and retrieval limits (20 candidates, top 5) were used for each mode. Scores are document-level; duplicate chunks from one circular count once.

| Metric | Dense | Hybrid | Hybrid + Rerank |
|---|---:|---:|---:|
| Recall@5 | 0.4375 | 0.7083 | 0.7292 |
| MRR | 0.4063 | 0.5708 | 0.7153 |
| Supported answers (sample) | 3/3 | 3/3 | 3/3 |

Nine GPT-4.1-mini answers (three per mode) were manually checked against cited passages; all nine were supported. Reranking improved the overall scores, though semantic-query Recall@5 fell to 0.5000, below dense and hybrid (both 0.6667). See the [full report](eval/report.md) for query-type breakdowns, examples, and per-answer evidence; [ranked results](eval/results.json) contain per-query IDs and metrics.

## Development checks

```bash
uv run pytest
```

The test suite uses mock embeddings, answer models and rerankers; it does not make paid API calls. Full-corpus embedding and live API validation are separate checks.
