# F001 — NSE Corpus Ingestion & Hybrid RAG Plan

## Scope and approach

- **P001** Add a compact ingestion CLI that reads local PDFs and per-file metadata deterministically, extracts page text with PyMuPDF, chunks through LlamaIndex, and writes batches to a fresh local Chroma collection. [R001–R011]
- **P002** Retain the full node set needed for same-run BM25 construction; persist Chroma and required local query state on the same machine as the corpus, then reopen them for queries. Expose dense, RRF hybrid and Cohere-reranked modes with shared candidate/top-k settings. Do not use a managed/remote vector database. [R011–R012]
- **P003** Add a query/answer CLI using GPT-4.1-mini and retrieved passages only, with circular ID, actual PDF page, passage references and an insufficient-evidence response. [R013]
- **P004** Document one-command full-corpus ingestion and query setup. Verify against all local PDFs and inspect exact-ID and semantic retrieval in each mode. [R014, R016]

## Likely files and dependencies

- **P005** Add focused modules under `src/nse_rag/` for ingestion, retrieval and CLI; update `pyproject.toml`/`uv.lock`, README, and focused tests. Avoid changing downloader behavior absent a demonstrated dependency.
- **P006** Add LlamaIndex core/integrations, PyMuPDF, ChromaDB, OpenAI and Cohere dependencies compatible with the selected Python runtime. Store corpus, Chroma data and BM25 state locally; do not upload documents or index data to a hosted database. Use the paid OpenAI API for embeddings and answer generation, and Cohere Rerank v5 Fast for reranking, as confirmed by the user.

## Compatibility matrix

| Area | Status | Evidence / verification |
|---|---|---|
| Python runtime | DECIDED: CPython 3.14 | Initial resolution under 3.15 failed because ChromaDB requires `onnxruntime`, which has no CPython 3.15 wheel. Resolver listed CPython 3.14 wheels. The POC pins 3.14 in `.python-version` and accepts `>=3.14` in `pyproject.toml`. |
| CPU architecture | VERIFIED: arm64 Apple Silicon | Host reports `arm64 Darwin`; package resolution and installation will verify wheel availability on this architecture. |
| Native dependencies | VERIFIED | ChromaDB/onnxruntime and PyMuPDF installed and imported successfully under CPython 3.14. |
| Container format | UNKNOWN / not specified | No container definition found; POC is local CLI and does not require a container. |
| Deployment target | VERIFIED (scope) | Local developer machine: local corpus and persistent local Chroma are required; no hosted database. |
| External services | VERIFIED (decision) | The user confirmed paid OpenAI API use and Cohere Rerank v5 Fast. API credentials/network access are needed; embedding text goes to OpenAI, and candidate passages go to Cohere during reranking. |

Automated compatibility checks: `uv lock`/`uv sync`, import smoke checks for chosen integrations, and focused tests for local configuration and persisted-store reopening. Full live acceptance needs the local corpus plus OpenAI and Cohere API credentials and network access.

### T001 runtime decision

Python 3.15 dependency resolution failed: `chromadb` depends on `onnxruntime>=1.14.1`, and the resolver found no matching CPython 3.15 wheel (available tags included CPython 3.14). CPython 3.14 was selected and verified with a successful lock, sync, integration import smoke check and focused test. This is a compatibility adjustment, not a change to the local-only architecture.

## Risks and mitigations

- **P007** Full-corpus extraction/embedding may be slow or memory-heavy: process sorted paths and bounded batches, report progress/failures, and avoid holding PDF page objects/text beyond need. [R006–R011]
- **P008** Metadata can misdescribe files or contain bad paths: use it only as descriptive input, fall back to PDF stem, preserve actual PDF page numbers, and spot-check extracted identity. [R003–R004, R009–R010]
- **P009** BM25 is in-memory while Chroma is persisted: persist/reconstruct the matching text nodes for querying, and ensure a fresh ingestion creates a single coherent run. [R011–R012]
- **P010** Runtime 3.15 and third-party/native package support are unverified: resolve with `uv` and imports before finalizing dependency choices; record any required runtime adjustment as a plan decision. [R005]
- **P011** OpenAI and Cohere APIs add usage cost, credential needs and external data transfer for embedding, answer generation and reranking. The user approved both services; keep corpus, Chroma and BM25 data local. [R005, R012–R014]

## Acceptance and validation

- **P012** Ingest all discovered local PDFs using one documented command; verify counts, failure log, deterministic file order and memory-bounded batches. [R006–R010, R014.1, R014.4]
- **P013** Verify Chroma persistence/reopen and matching BM25 corpus, then inspect exact-ID and semantic results in all three retrieval configurations. [R011–R012, R014.2–R014.3]
- **P014** Verify answer references use real PDF page numbers and supporting text, and test insufficient-evidence behavior. [R004, R013–R014]
- **P015** Add and run focused automated tests under `uv` for metadata matching/fallback, malformed JSON handling, page preservation/chunk metadata, retrieval configuration and persisted-store reopen. Full-corpus/API verification remains distinct and must be reported as such. [R009–R014]
