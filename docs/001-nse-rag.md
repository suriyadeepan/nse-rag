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

## API configuration note

- The user has configured OpenAI and Cohere trial API keys in the local `.env`; secret values are not recorded here. `.env` is ignored by Git and must remain untracked.
- Keep Cohere usage within the active trial account's rate limits during live validation. Use small, sequential rerank checks and avoid concurrent or repeated requests; verify observed limits in the Cohere account before increasing request volume.

## T005 — Grounded answers and citations

- Added `src/nse_rag/answer.py` with GPT-4.1-mini answer generation from only the supplied retrieved passages and their indexed circular ID/actual `page_number`. It never reads the metadata listing `page` field.
- Prompt requires `[S#]` evidence citations and an `INSUFFICIENT_EVIDENCE` marker where the passages do not support an answer. Returned references include circular ID, actual PDF page and passage; references are included only when cited by a valid source tag. Missing/invalid citation tags or unusable page metadata produce an explicit insufficient-evidence response.
- The LlamaIndex OpenAI adapter reads `OPENAI_API_KEY`; this implementation and its tests do not make live API calls. Credentials and external usage remain for end-to-end validation.
- `uv run pytest -q tests/test_answer.py` passed (4 tests). `PYTHONPATH=scripts uv run pytest -q` passed (20 tests; 6 dependency deprecation warnings). Coverage verifies prompt evidence bounds, actual PDF page citation rather than listing page, full source references, explicit insufficiency and rejection of unknown/missing citation tags.

## T006 — CLI and local usage documentation

- Replaced the placeholder package entry point with `nse-rag ingest` and `nse-rag query`. Ingestion defaults to all sorted local PDFs and metadata, writes the local index, and prints discovered/loaded/indexed/skipped/chunk counts. Query reopens local Chroma and its matching BM25 corpus, selects dense/hybrid/hybrid-rerank, uses shared candidate/result settings, generates a grounded answer, and prints each cited passage with circular ID and actual PDF page.
- Added README setup and commands, local storage paths, API key configuration, mode descriptions, and a `.env.example` template. `uv run --env-file .env` loads credentials without adding a dotenv dependency; `.env.example` is copied with `cp -n` so an existing local key file is preserved. Cohere mode makes one rerank request per query; docs instruct sequential use within account limits.
- `uv run pytest -q tests/test_cli.py` passed (3 tests). CLI entry-point smoke checks passed for `nse-rag --help`, `nse-rag ingest --help`, and `nse-rag query --help`. These checks use mocks/help only; no full-corpus embedding or live provider request was made.
