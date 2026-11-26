# F001 — NSE Corpus Ingestion & Hybrid RAG Journal

## T001 — Runtime and dependency compatibility

- The configured CPython 3.15 runtime could not resolve ChromaDB because its `onnxruntime>=1.14.1` dependency has no CPython 3.15 wheel. `uv` reported available `onnxruntime` wheel tags through CPython 3.14.
- Host: arm64 Darwin. The plan records the runtime decision to use CPython 3.14 for the POC. `.python-version` is pinned to 3.14 and `requires-python` is `>=3.14`.
- `uv add` resolved and installed the selected stack on CPython 3.14.10; `uv.lock` resolves 142 packages. Relevant installed versions: LlamaIndex core 0.14.26, ChromaDB 1.5.9, PyMuPDF 2.2, OpenAI 3.60.0, Cohere 6.1.0, and ONNX Runtime 1.32.0.
- Compatibility verification passed:
  - `uv lock --check`
  - `uv sync --locked`
  - `uv run python -c '...'` importing PyMuPDF, ChromaDB, OpenAI, Cohere, `SentenceSplitter`, `BM25Retriever`, `ChromaVectorStore`, OpenAI embedding/LLM adapters, and `CohereRerank`; output reported `3.14.10 arm64` and `LlamaIndex imports OK`.
- Import path note: `SentenceSplitter` is provided by `llama_index.core.node_parser`, not re-exported from `llama_index.core` in the resolved version. The compatibility smoke check uses its actual module path.
- No API credentials or external services were used; live API and corpus verification remain for later tasks.

## T002 — Metadata matching and page-aware PDF extraction

- Added `src/nse_rag/ingest.py` with sorted local PDF discovery, per-file JSON loading (excluding the aggregate), exact stored path matching followed by circular-ID/metadata-filename-stem fallback, and filename-stem circular-ID fallback when metadata is absent.
- Extraction streams one PDF at a time, reads text per page with PyMuPDF, skips empty pages, and splits each page with LlamaIndex `SentenceSplitter` configured for 500 tokens and 50-token overlap. Emitted `TextNode`s include the searchable circular ID/title, whitelisted descriptive metadata, source PDF path, and actual 1-based PDF page number; listing `page` is ignored.
- Malformed/non-object metadata, unavailable or unmatched metadata records, unreadable PDFs, extraction failures, and PDFs without usable text are logged. A mismatched stored path still attempts the specified ID/stem fallback.
- `uv run pytest -q tests/test_ingest.py tests/test_compatibility.py` passed (5 tests). `PYTHONPATH=scripts uv run pytest -q` passed (10 tests). Tests cover aggregate exclusion, path/ID/stem matching, malformed JSON and missing-path logs, deterministic order, empty/unreadable input handling, identity fallback, page metadata, and exclusion of archive listing page.
- Full-corpus behavior and metadata/PDF identity spot-checks remain for T008.

## T003 — Local dense and BM25 index persistence

- Added `src/nse_rag/index_store.py`. It creates a fresh local Chroma collection, extracts one PDF at a time, inserts chunks in bounded batches (default 128 nodes), and writes each successfully inserted node to local `nodes.jsonl` with its node ID and metadata.
- The dense embedding adapter defaults to OpenAI `text-embedding-3-small`. Tests inject LlamaIndex `MockEmbedding`, so automated persistence checks make no API calls.
- Reopening reconstructs BM25 from the saved node JSONL and reopens the persisted Chroma collection. It compares the complete node ID set from the JSONL with Chroma IDs (read in bounded pages) and fails if the two indexes differ. The build result includes both query indexes and counts for PDFs found, metadata records loaded, documents indexed/skipped, and nodes indexed.
- `uv run pytest -q tests/test_index_store.py tests/test_ingest.py` passed (6 tests). `tests/test_index_store.py` verifies batch sizes, counts, BM25/Chroma node ID equality, reopen behavior, clean collection replacement, and textless PDF skip reporting.
- No external embedding API or remote database was used. The full-corpus embedding run remains for T008.

## Corpus availability correction

- An earlier `rg --files data/pdfs data/metadata` check returned no files because `.gitignore` excludes corpus PDFs and metadata JSON. That output was incorrectly interpreted as empty directories. Direct filesystem checks found 7,614 PDFs and 7,612 per-document JSON files. No full-corpus ingestion or identity spot-check has yet been run.

## T004 — Dense, hybrid, and reranked retrieval

- Added `src/nse_rag/retrieval.py` with selectable `dense`, `hybrid`, and `hybrid-rerank` modes. Each mode uses `RetrievalSettings` with the same candidate limit (default 20) and final result limit (default 5); there are no metadata filters.
- Hybrid modes combine the reopened local Chroma dense retriever and the matching local BM25 retriever through LlamaIndex `QueryFusionRetriever` in reciprocal-rank fusion mode. Cohere receives only the fused candidate passages, using model `rerank-v5.0-fast`, then returns the shared final top-k. Reranking needs `COHERE_API_KEY` and network access; dense and hybrid retrieval make no Cohere call.
- `uv run pytest -q tests/test_retrieval.py` passed (4 tests). The tests cover all modes and shared limits, RRF overlap ranking, Cohere v5 Fast wiring and candidate-only reranking, and rejection of hybrid queries without BM25.
- `PYTHONPATH=scripts uv run pytest -q` passed (16 tests). Tests use a local temporary Chroma collection and mock embeddings/reranker; no external API calls were made.
- The local corpus is present (7,614 PDFs and 7,612 JSON files), but full-corpus ingestion and live queries remain outstanding for T008.
