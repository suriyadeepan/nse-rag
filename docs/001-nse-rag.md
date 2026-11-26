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
- The supplied local `data/pdfs` and `data/metadata` directories contain no corpus files in this checkout, so full-corpus behavior and metadata/PDF identity spot-checks have not been performed; those remain for T008.
