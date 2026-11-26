# F002 — RAG Evaluation & Benchmarking (POC)

## Objective

Compare dense, hybrid and reranked retrieval on the **full indexed NSE corpus** with a small labelled test set. Reuse F001's indexes and retrieval code; avoid building an evaluation framework.

## Baseline

- F001 indexed **7,591 of 7,614 PDFs** (36,853 chunks); 23 were skipped.
- Reuse persisted Chroma and BM25 indexes. **No re-ingestion or re-embedding.**
- Compare `dense`, `hybrid` (BM25 + dense + RRF), and `hybrid-rerank` (Cohere v5 Fast).
- Keep F001 defaults fixed: 20 candidates, final top 5.

## Requirements

### R001 — Labelled queries

- Create `eval/eval.jsonl` with **20–30 manually verified queries**, drawn from documents in the index.
- Cover **exact ID**, **keyword/phrase**, **semantic**, and **multi-circular** queries.
- Prefer straightforward, source-verifiable examples. No metadata filters, OCR or supersession cases.
- Required fields: `query`, `type`, `expected_ids`. Optional: `expected_answer`.
- Verify IDs against source PDFs/metadata; do not confuse archive listing page with actual PDF page.

Example:

```json
{"query": "When does the revocation of Gayatri Projects' trading suspension take effect?", "type": "semantic", "expected_ids": ["0001fd562caa1c25"], "expected_answer": "April 09, 2026"}
```

### R002 — Retrieval metrics

- Run every query through all three modes against the **same full index**.
- Compute **Recall@5** and **MRR** from expected circular IDs. Multiple chunks from the same PDF count as one document.
- Report overall scores and a simple breakdown by query type.
- Save per-query ranked IDs and metric values to `eval/results.json` or CSV.
- Make Cohere rerank calls sequentially to respect trial limits.

### R003 — Answer grounding spot-check

- Generate answers for **5–10 representative queries** using the existing GPT-4.1-mini pipeline.
- Manually classify each as **supported**, **unsupported**, or **insufficient evidence** based on cited passages.
- Report counts; no LLM judge or automated claim-level validator.

### R004 — Concise report

Produce a Markdown table:

| Metric | Dense | Hybrid | Hybrid + Rerank |
|---|---:|---:|---:|
| Recall@5 | TBD | TBD | TBD |
| MRR | TBD | TBD | TBD |
| Supported answers (sample) | TBD | TBD | TBD |

Include query count, fixed retrieval settings and **2–3 real examples** of improvement, ties or failures. Report actual results even if hybrid/reranking performs worse.

## Acceptance criteria

- 20–30 source-verified queries tested against **all 7,591 indexed PDFs**, not a reduced corpus.
- Identical queries, indexes and retrieval limits across all three modes.
- Recall@5, MRR and per-query results saved.
- 5–10 generated answers manually checked for grounding.
- A short Markdown comparison report produced without fabricated scores.

## Out of scope

- Large evaluation datasets, multiple reviewers and significance testing.
- Metadata-constrained queries, difficult extraction edge cases and exhaustive failure taxonomy.
- LLM-as-judge pipelines, experiment platforms, dashboards and CI benchmarking.

## Implementation principle

Build **one small evaluation script** using existing F001 functions. Prioritize a working, reproducible comparison over infrastructure.
