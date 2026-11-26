# Tutorial: Search the NSE PDF corpus

This proof of concept indexes the PDFs already stored locally, then retrieves supporting passages and answers questions with PDF page citations.

## 1. Configure the environment

Use Python 3.14 with `uv`. From the repository root:

```bash
uv sync
cp -n .env.example .env
```

Add your `OPENAI_API_KEY` to `.env`. Add `COHERE_API_KEY` only if you plan to use reranking. Keep `.env` private; it is ignored by Git.

## 2. Build the full local index

Make sure the existing corpus is under `data/pdfs/` and metadata JSON files are under `data/metadata/`. Ingestion reads these files without downloading them:

```bash
uv run --env-file .env nse-rag ingest
```

The command processes sorted PDFs, creates a fresh Chroma collection and matching BM25 text corpus under `data/index/`, and reports found, indexed, skipped and chunk counts. Embedding text is sent to OpenAI. PDFs without usable extracted text are skipped and reported; this POC does not run OCR.

## 3. Query the index

```bash
uv run --env-file .env nse-rag query "When does the circular take effect?" --mode dense
uv run --env-file .env nse-rag query "Which trading requirements changed?" --mode hybrid
uv run --env-file .env nse-rag query "Which trading requirements changed?" --mode hybrid-rerank
```

- `dense` searches local Chroma vectors.
- `hybrid` combines local BM25 and dense results with reciprocal rank fusion.
- `hybrid-rerank` sends the hybrid candidate passages to Cohere Rerank v5 Fast. Run rerank requests sequentially and follow your account's rate limits.

All modes use the same default candidate and result limits. Answers use GPT-4.1-mini and show cited circular IDs, actual 1-based PDF pages and the supporting passage. If the retrieved passages do not support an answer, the CLI reports insufficient evidence.

See [README.md](../README.md) for optional paths, batch-size settings and development checks.
