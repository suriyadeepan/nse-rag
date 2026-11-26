# F002 — RAG Evaluation & Benchmarking Plan

## Scope and approach

- **P001** Add 24 manually source-verified queries in `eval/eval.jsonl`, balanced across exact-ID, keyword/phrase, semantic and multi-circular query types. Verify expected circular IDs against indexed PDF identity and metadata; keep to straightforward evidence, with no filters, OCR or supersession cases. [R006]
- **P002** Implement one small script that opens the existing `data/index` with F001's `open_local_indexes`, runs identical questions through `retrieve` in dense, hybrid and hybrid-rerank modes, and keeps `RetrievalSettings(20, 5)` fixed. Never call ingestion or embedding setup. Collapse repeated chunks to unique circular IDs for metrics. [R002–R005, R007]
- **P003** Save per-query top-five IDs, Recall@5 and reciprocal rank, plus aggregate and query-type metrics, in `eval/results.json`. Keep reranker calls sequential and report dataset/index counts and execution configuration. [R007]
- **P004** Generate nine grounded answers (three representative queries per mode) through the existing GPT-4.1-mini answer path; manually classify each as supported, unsupported or insufficient evidence from its cited passages. Record labels and concise evidence notes in `eval/report.md`; show supported/total by mode in the comparison table and all three classification counts in detail. [R008–R009]
- **P005** Produce a concise report in `eval/report.md` with retrieval scores, answer grounding counts, query count/settings and two or three actual examples of improvements, ties or failures. Record execution commands, actual results and evidence boundaries in the F002 journal. [R009–R010]
- **P006** Do not modify F001 retrieval/index behavior or dependencies. Do not re-ingest/re-embed, create an evaluation framework, add automated answer judging, or report unrun or inferred results as measured. [R001–R005, R011–R012]

## Affected files and dependencies

- **P007** Add `eval/eval.jsonl`, one evaluation script under `scripts/`, `eval/results.json`, `eval/report.md`, and the F002 implementation journal `docs/002-rag-evaluation-benchmarking.md`; update only F002 feature state as needed. Reuse `nse_rag.index_store`, `nse_rag.retrieval`, and `nse_rag.answer`. [R001–R012]
- **P008** Use the existing Python 3.14 `uv` environment and locked dependencies. Retrieval needs local `data/index`; reranking needs the configured Cohere API, and answer sampling needs OpenAI credentials. No new dependency is planned. [R002–R005, R007–R008]

## Compatibility matrix

| Area | Status | Evidence / validation |
|---|---|---|
| Python runtime | VERIFIED: CPython 3.14 project runtime | `.python-version` is 3.14; F001 records successful `uv` resolution, sync and imports on 3.14.10. Run the script with `uv`. |
| CPU architecture | VERIFIED: arm64 Darwin host | `uname -sm` reports `Darwin arm64`; F001 records local native dependency verification on this host. |
| Native dependencies | VERIFIED for existing stack | F001 successfully imported ChromaDB, ONNX Runtime, PyMuPDF and LlamaIndex integrations under the pinned environment. F002 adds no native dependency. |
| Container format | UNKNOWN / not specified | No container configuration is present or needed for this local evaluation. |
| Deployment target | VERIFIED: local developer machine | Reuses ignored local `data/index` (Chroma plus `nodes.jsonl`); current local index directory is present. No remote index or corpus transfer is introduced. |
| External services | VERIFIED by F001 configuration; live F002 calls pending | F001 journal records local OpenAI and Cohere credentials configured and successful prior live calls. Confirm availability at run time without printing secrets; use Cohere sequentially. |

Automated compatibility checks: run the evaluator under `uv` and confirm it opens the persisted index, sees the expected unique document/node counts, preserves the fixed limits, and writes parseable JSON results. Live acceptance also needs available API credentials/network for reranking and sampled answers. No corpus-wide rebuild is part of validation.

## Risks and mitigations

- **P009** Hand labels or expected IDs can be wrong: choose direct, source-verifiable examples and check PDF identity/content against metadata, treating source PDF pages as authoritative rather than archive listing pages. [R006]
- **P010** Repeated chunks can inflate retrieval scores: rank each circular only at its first occurrence before computing Recall@5 and MRR; keep raw ranked IDs in result evidence. [R007]
- **P011** Cohere trial limits or API failures can interrupt runs: issue rerank requests sequentially, record failures, and do not compare partial rerank results as complete. [R007.5]
- **P012** Answer-grounding labels are subjective and the total sample is small: inspect cited passages manually, show the 3-per-mode denominator and separate supported, unsupported and insufficient-evidence counts. [R008–R009]
- **P013** Existing local index can be stale or incomplete: before retrieval, verify 36,853 persisted nodes and 7,591 distinct indexed source PDF paths from node `pdf_path` metadata against F001's baseline. Report circular-ID coverage separately; do not use unique circular-ID count as a proxy for source-document count. Stop and report a baseline mismatch rather than rebuilding. [R002–R003, R010]

## Acceptance and validation

- **P014** Validate 20–30 source-backed labelled queries across all four requested types, with correct expected circular IDs and no out-of-scope query constraints. [R006, R010.1]
- **P015** Run the same query set against the same persisted full index in all three modes using 20 candidates and final top 5; deduplicate document IDs for Recall@5/MRR and save per-query plus overall/type results. Confirm Cohere requests were sequential. [R002–R007, R010.1–R010.3]
- **P016** Manually inspect nine generated GPT-4.1-mini answers (three per mode) against their cited passages and record all three grounding classes and evidence notes. [R008–R010.4]
- **P017** Report measured scores, settings, query count and two or three real result examples in `eval/report.md`; document commands, outcomes, failures and verification limits in the journal. No scores are filled in during planning. [R009–R010.5]
- **P018** Do not run tests or evaluation during planning. During implementation, run only prescribed `uv` checks relevant to the evaluator and record actual evidence; full-corpus/live-service execution is a separate acceptance check. [R002–R012]
