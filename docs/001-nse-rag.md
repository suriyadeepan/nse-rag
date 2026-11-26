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
