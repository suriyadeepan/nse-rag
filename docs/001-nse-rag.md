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

## T007 — Automated and local deployment smoke checks

- Dependency/environment checks passed: `uv lock --check`; `uv sync --locked` (141 packages checked); `uv run python -c 'import nse_rag, nse_rag.cli, nse_rag.answer, nse_rag.index_store; print("package imports OK")'`.
- Automated suite: `PYTHONPATH=scripts uv run pytest -q` passed (23 tests; 6 dependency deprecation warnings). The `PYTHONPATH` exposes the existing downloader module used by its tests.
- Local persistence smoke: `uv run pytest -q tests/test_index_store.py` passed (2 tests), including fresh local Chroma creation, matching BM25 node set, persisted collection reopen through `open_local_indexes`, and replacement of a stale POC collection.
- CLI smoke: `uv run --env-file .env nse-rag --help`, `uv run --env-file .env nse-rag ingest --help`, and `uv run --env-file .env nse-rag query --help` all passed. `.env` was loaded by `uv` but its values were not printed; help commands made no provider calls.
- These are automated and local smoke results only. Full-corpus ingestion, exact-ID/semantic retrieval against that corpus, and live OpenAI/Cohere calls remain for T008.

## T008 — Full-corpus ingestion cost estimate

- Full-corpus ingestion indexed 36,853 chunks. Counting the persisted node text with the `text-embedding-3-small` tokenizer (`tiktoken.encoding_for_model`) yielded approximately 11,798,379 input tokens. At the OpenAI listed price of $0.02 per 1 million input tokens, the estimated corpus embedding charge is **$0.24 USD** (about $0.23597 before rounding).
- This is a local estimate based on persisted indexed text and published pricing, not the provider's account-level billed usage. It excludes query embedding and GPT-4.1-mini answer calls. OpenAI pricing source checked 2026-11-26: https://developers.openai.com/api/docs/models/text-embedding-3-small

## T008 — Full-corpus and live retrieval verification

- Ran the documented full-corpus command: `time uv run --env-file .env nse-rag ingest`. It completed in 11m46.72s: **7,614 PDFs found, 7,611 metadata records loaded, 7,591 documents indexed, 23 skipped, and 36,853 chunks indexed**. Extraction warnings for textless/unusable PDFs were printed during ingestion; the command completed and persisted/reopened the local Chroma collection and matching BM25 node set.
- Spot-checked `data/pdfs/0001fd562caa1c25.pdf` against its JSON. The metadata title, “Revocation of Trading Suspension in Equity Shares of Gayatri Projects Limited,” matches the PDF heading; the PDF itself identifies `NSE/CML/73562` and Circular Ref. No. `0556/2026`. Citation page numbers came from extracted PDF page metadata (page 1), not listing metadata.
- Exact-ID retrieval used `0001fd562caa1c25` with the title. Dense and hybrid returned this circular's page 1; hybrid-rerank returned the same circular and page. Semantic retrieval asked when the revocation takes effect. Dense, hybrid, and hybrid-rerank all answered **April 09, 2026** and cited circular ID `0001fd562caa1c25`, PDF page 1, with the supporting passage. The reranked result included the PDF's `NSE/CML/73562` and `0556/2026` text.
- A bare-ID answer query did not provide enough question context and returned the explicit insufficient-evidence response. This confirms the answer path does not guess when the evidence/query is insufficient.
- All live OpenAI embedding and GPT-4.1-mini requests used in validation succeeded. During ingestion, some embedding requests returned HTTP 429 and were retried successfully; there was no terminal API failure. Four Cohere rerank requests were run sequentially, with no concurrent reranking; all returned HTTP 200.
- Added `data/index/` to `.gitignore` so the generated local Chroma database and BM25 corpus remain local and are not mistaken for source files.

## T009 — Requirement and plan evidence reconciliation

The trace below was checked against the implementation in `src/nse_rag/`, automated tests in `tests/`, and the recorded local/live checks above. Automated tests and real-provider/full-corpus validation are distinct evidence; passing mocks does not imply a live service check.

| Requirements | Plan | Implementation | Automated evidence | Local/live evidence |
|---|---|---|---|---|
| R001–R004, R006–R010 (metadata, PDF extraction, page-aware chunks, skips) | P001, P007–P008, P012, P015 | `ingest.py` | `test_ingest.py`; full suite at T007 | T008: 7,614 discovered; identity/title spot-check; actual PDF page 1 cited |
| R005, R011 (selected stack, local dense/BM25 indexes) | P001–P002, P005–P010, P015 | `index_store.py`, `pyproject.toml`, `uv.lock` | `test_compatibility.py`, `test_index_store.py`; T001 import/sync checks | T007 local Chroma reopen and node-set parity; T008 full build persisted 36,853 chunks |
| R005, R012 (dense, RRF hybrid, Cohere rerank) | P002, P006, P009, P011, P013 | `retrieval.py` | `test_retrieval.py` | T008 exact-ID and semantic queries in all three modes; four sequential Cohere requests returned HTTP 200 |
| R013 (grounded answers and actual-page references) | P003, P014–P015 | `answer.py`, `cli.py` | `test_answer.py`, `test_cli.py` | T008 semantic answers cited circular ID and PDF page 1; bare-ID query returned insufficient evidence |
| R014, R016 (documented end-to-end POC and inspectable results) | P004, P012–P015 | `cli.py`, `README.md`, `docs/tutorial-001-nse-rag.md` | `test_cli.py`; T007 CLI help smoke | T008 full-corpus ingestion and live query checks |

**Verification categories:** Implementation is present for all listed requirement groups. Automated verification: T007 reports 23 tests passed under `uv`; T001 reports locked dependency sync and integration imports. Local deployment smoke: T007 reports CLI help and Chroma/BM25 persistence/reopen. Full-corpus/live API verification: T008 reports 7,591 indexed documents, 23 skipped, three retrieval modes, OpenAI answers/embeddings, and sequential Cohere requests. These results are recorded separately and are not inferred from unit tests.

For this reconciliation, `PYTHONPATH=scripts uv run pytest -q` passed again (23 passed, 6 dependency deprecation warnings). The default `uv run pytest -q` invocation failed during collection because `fetch_nse_circulars` is imported from the existing `scripts/` directory, which is not on the default import path; using the repository's documented `PYTHONPATH=scripts` resolves collection. No test code or application code changed.

**Remaining limits:** No OCR; 23 textless/unusable PDFs were skipped and logged. Identity validation was a spot-check, not an exhaustive metadata audit. Embedding cost is an estimate ($0.24), not account billing. These match the POC scope; no unverified acceptance claim is made.

README review: setup, local paths, ingestion/query commands, modes, citations and test instructions match the CLI and implementation. Added `docs/tutorial-001-nse-rag.md` for the completed feature, consistent with the documentation convention. No README change was needed.
