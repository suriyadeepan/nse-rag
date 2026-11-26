# F001 — NSE Corpus Ingestion & Hybrid RAG TODO

Canonical task and status source for F001. Mark tasks complete only when their acceptance criteria and required evidence are recorded in the implementation journal.

## T001 — Confirm runtime and dependency compatibility

- **Status:** COMPLETE — `uv lock --check`, `uv sync --locked`, and integration imports passed under CPython 3.14.10 on arm64; runtime decision and resolved versions are recorded in `docs/001-nse-rag.md`.

- **Action:** Resolve the selected LlamaIndex, PyMuPDF, ChromaDB, OpenAI, Cohere and BM25/RRF integrations under the configured Python runtime. Check host architecture/native wheels; record a plan decision before changing the runtime if Python 3.15 is unsupported.
- **Files:** `pyproject.toml`, `uv.lock`, `docs/001-nse-rag-plan.md`, `docs/001-nse-rag.md`
- **Requirements / plan:** R005; P005–P006, P010
- **Acceptance:** `uv lock` and `uv sync` succeed with compatible packages, or a justified runtime adjustment is recorded in the plan; integration imports succeed. Results and versions are journaled.
- **Dependencies:** None.

## T002 — Implement deterministic metadata loading and PDF extraction

- **Status:** COMPLETE — deterministic metadata matching, page-aware streaming extraction/chunking, and focused tests are implemented; evidence is recorded in `docs/001-nse-rag.md`.

- **Action:** Add a small ingestion module that loads one-object metadata JSON files (excluding the aggregate), matches PDFs by local path then ID/stem, falls back to the filename stem, sorts local PDF paths, extracts page text with PyMuPDF, skips/logs malformed, missing, unreadable and textless inputs, chunks pages with `SentenceSplitter` (500/50), and attaches searchable identity plus required metadata and real 1-based page numbers.
- **Files:** `src/nse_rag/ingest.py`, `src/nse_rag/__init__.py`, `tests/test_ingest.py`, `docs/001-nse-rag.md`
- **Requirements / plan:** R001–R004, R006–R010; P001, P007–P008
- **Acceptance:** The intake remains a small POC pipeline that handles the existing local collection without introducing production-grade recovery or reconciliation. Focused tests verify aggregate exclusion, metadata matching/fallback, malformed JSON behavior, deterministic order, text extraction skip behavior, page/chunk metadata and no use of listing page as PDF page. Each emitted chunk has its source PDF path and actual page number; failures are visible in logs.
- **Dependencies:** T001.

## T003 — Build and persist same-run local dense and BM25 indexes

- **Action:** Add bounded-batch embedding and Chroma writes to a fresh local POC collection, using OpenAI `text-embedding-3-small`. Retain/reconstruct the complete matching node corpus for BM25 and query-time reopening; report found, metadata-loaded, indexed and skipped counts and log failures.
- **Files:** `src/nse_rag/ingest.py`, `src/nse_rag/index_store.py`, `tests/test_index_store.py`, `docs/001-nse-rag.md`
- **Requirements / plan:** R005–R008, R011; P001–P002, P006–P009, P012–P013
- **Acceptance:** Unit/integration tests show a fresh run creates a clean local Chroma collection, bounded batches preserve the complete node set, BM25 source nodes match Chroma input nodes, and persisted Chroma can be reopened with query state reconstructed for that run. No remote DB or corpus download is used.
- **Dependencies:** T001, T002.

## T004 — Implement dense, hybrid and Cohere reranked retrieval

- **Action:** Build selectable dense-only, BM25+dense RRF, and BM25+dense RRF+Cohere Rerank v5 Fast configurations over the same persisted corpus and shared candidate/top-k settings. Keep BM25 local; send only reranking candidate passages to Cohere.
- **Files:** `src/nse_rag/retrieval.py`, `tests/test_retrieval.py`, `docs/001-nse-rag.md`
- **Requirements / plan:** R005, R012; P002, P006, P009, P011, P013
- **Acceptance:** Tests verify each mode selection, common candidate/top-k settings, RRF fusion behavior, reranker integration wiring and local query-state/Chroma run consistency. Retrieval has no metadata filters. Cohere credentials and network requirements are documented.
- **Dependencies:** T003.

## T005 — Implement grounded answers and citations

- **Action:** Add GPT-4.1-mini answer generation using retrieved passages only; return circular ID, actual PDF page number and supporting passage, and report insufficient evidence without guessing.
- **Files:** `src/nse_rag/answer.py`, `tests/test_answer.py`, `docs/001-nse-rag.md`
- **Requirements / plan:** R013; P003, P011, P014
- **Acceptance:** Tests verify prompt context is limited to retrieved passages, references contain circular ID and actual PDF page plus passage, metadata listing page is never cited as a PDF page, and insufficient evidence produces an explicit response. OpenAI credential and usage requirements are documented.
- **Dependencies:** T004.

## T006 — Add CLI and reproducible local usage documentation

- **Action:** Wire one-command full-corpus ingestion and query commands into the existing CLI; document local setup, environment variables, index paths, retrieval modes and commands.
- **Files:** `src/nse_rag/__init__.py`, `src/nse_rag/cli.py`, `pyproject.toml`, `README.md`, `docs/001-nse-rag.md`
- **Requirements / plan:** R005–R008, R014, R016; P003–P006, P012
- **Acceptance:** CLI help and smoke tests show one documented ingestion command for all sorted local PDFs and selectable query modes; a fresh setup can configure local storage plus paid OpenAI and Cohere credentials without redownloading data. README matches implemented commands.
- **Dependencies:** T002–T005.

## T007 — Run automated checks and local deployment smoke checks

- **Action:** Run focused unit/integration tests under `uv`, package/import checks, CLI smoke checks, and local persistence/reopen smoke checks. Fix failures and record commands and outcomes.
- **Files:** `tests/test_ingest.py`, `tests/test_index_store.py`, `tests/test_retrieval.py`, `tests/test_answer.py`, `docs/001-nse-rag.md`
- **Requirements / plan:** R009–R014; P006, P010, P013–P015
- **Acceptance:** Automated checks pass under `uv`; local Chroma can be reopened by the query path; all automated and deployment-smoke results are recorded distinctly in the journal. No success is claimed without evidence.
- **Dependencies:** T001–T006.

## T008 — Validate the full corpus and live retrieval modes

- **Action:** Run ingestion against the complete available local `data/pdfs/*.pdf` corpus with API credentials, inspect the summary/failure log and identity spot-checks, then run exact-ID and semantic queries through all three modes and inspect answer citations and evidence sufficiency behavior.
- **Files:** `docs/001-nse-rag.md`, `README.md`
- **Requirements / plan:** R003–R004, R006–R008, R010–R014, R016; P007–P014
- **Acceptance:** Journal records discovered/indexed/skipped counts, command, elapsed/runtime or observed issues, sample exact-ID and semantic passages from the full indexed corpus in dense/hybrid/reranked modes, and answer references with actual PDF pages. Any unavailable credential/service or corpus limitation is reported as an outstanding live check, not passed.
- **Dependencies:** T007 and configured local corpus plus OpenAI/Cohere credentials/network.

## T009 — Reconcile lineage and completion evidence

- **Action:** Verify every applicable requirement and plan item maps through implementation to automated tests or explicit live validation; record completion evidence and any remaining limitation in the journal, then confirm README/tutorial expectations.
- **Files:** `docs/001-nse-rag-todo.md`, `docs/001-nse-rag.md`, `README.md`
- **Requirements / plan:** R001–R014, R016; P001–P015
- **Acceptance:** No broken R→P→T→implementation→test/live-validation links remain; implementation, automated tests, deployment smoke checks and full-corpus/live API verification are reported separately. Create the user-facing tutorial only upon feature completion per project instructions.
- **Dependencies:** T001–T008.

## Lineage coverage

- R001–R004 → P001, P007–P008 → T002/T008 → bounded POC intake/extraction implementation and focused metadata/PDF tests plus identity spot-check.
- R005–R008 → P001–P007, P011–P012 → T001–T003, T006–T008 → dependencies, ingestion implementation/tests and full-corpus run.
- R009–R010 → P001, P007–P008, P015 → T002/T007/T008 → implementation, focused tests and full-corpus validation.
- R011 → P002, P009, P013, P015 → T003/T007/T008 → index implementation, persistence tests and reopen/full-run checks.
- R012 → P002, P006, P013, P015 → T004/T007/T008 → retrieval implementation, configuration tests and live three-mode checks.
- R013 → P003, P014–P015 → T005/T007/T008 → answer implementation, citation/insufficient-evidence tests and live answer inspection.
- R014, R016 → P004, P012–P015 → T006–T009 → documentation, smoke/full-corpus validation and final evidence reconciliation.

All plan items P001–P015 and active requirements R001–R014, R016 are mapped above. No additional scope is introduced.
