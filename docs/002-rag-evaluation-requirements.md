# F002 — RAG Evaluation & Benchmarking

## Objective

Compare dense, hybrid and reranked retrieval on the **full indexed NSE corpus** with a small labelled test set. Reuse F001's indexes and retrieval code; avoid building an evaluation framework. [R001]

## Baseline

- F001 indexed **7,591 of 7,614 PDFs** (36,853 chunks); 23 were skipped. [R002]
- Reuse persisted Chroma and BM25 indexes. **No re-ingestion or re-embedding.** [R003]
- Compare `dense`, `hybrid` (BM25 + dense + RRF), and `hybrid-rerank` (Cohere v5 Fast). [R004]
- Keep F001 defaults fixed: 20 candidates, final top 5. [R005]

## Requirements

### R006 — Labelled queries

- Create `eval/eval.jsonl` with **20–30 manually verified queries**, drawn from documents in the index. [R006.1]
- Cover **exact ID**, **keyword/phrase**, **semantic**, and **multi-circular** queries. [R006.2]
- Prefer straightforward, source-verifiable examples. No metadata filters, OCR or supersession cases. [R006.3]
- Required fields: `query`, `type`, `expected_ids`. Optional: `expected_answer`. [R006.4]
- Verify IDs against source PDFs/metadata; do not confuse archive listing page with actual PDF page. [R006.5]

Example:

```json
{"query": "When does the revocation of Gayatri Projects' trading suspension take effect?", "type": "semantic", "expected_ids": ["0001fd562caa1c25"], "expected_answer": "April 09, 2026"}
```

### R007 — Retrieval metrics

- Run every query through all three modes against the **same full index**. [R007.1]
- Compute **Recall@5** and **MRR** from expected circular IDs. Multiple chunks from the same PDF count as one document. [R007.2]
- Report overall scores and a simple breakdown by query type. [R007.3]
- Save per-query ranked IDs and metric values to `eval/results.json` or CSV. [R007.4]
- Make Cohere rerank calls sequentially to respect trial limits. [R007.5]

### R008 — Answer grounding spot-check

- Generate answers for **5–10 representative queries** using the existing GPT-4.1-mini pipeline. [R008.1]
- Manually classify each as **supported**, **unsupported**, or **insufficient evidence** based on cited passages. [R008.2]
- Report counts; no LLM judge or automated claim-level validator. [R008.3]

### R009 — Concise report

Produce a Markdown table:

| Metric | Dense | Hybrid | Hybrid + Rerank |
|---|---:|---:|---:|
| Recall@5 | TBD | TBD | TBD |
| MRR | TBD | TBD | TBD |
| Supported answers (sample) | TBD | TBD | TBD |

- Include query count, fixed retrieval settings and **2–3 real examples** of improvement, ties or failures. [R009.1]
- Report actual results even if hybrid/reranking performs worse. [R009.2]

## Acceptance criteria

- 20–30 source-verified queries tested against **all 7,591 indexed PDFs**, not a reduced corpus. [R010.1]
- Identical queries, indexes and retrieval limits across all three modes. [R010.2]
- Recall@5, MRR and per-query results saved. [R010.3]
- 5–10 generated answers manually checked for grounding. [R010.4]
- A short Markdown comparison report produced without fabricated scores. [R010.5]

## Out of scope

- Large evaluation datasets, multiple reviewers and significance testing. [R011.1]
- Metadata-constrained queries, difficult extraction edge cases and exhaustive failure taxonomy. [R011.2]
- LLM-as-judge pipelines, experiment platforms, dashboards and CI benchmarking. [R011.3]

## Implementation principle

Build **one small evaluation script** using existing F001 functions. Prioritize a working, reproducible comparison over infrastructure. [R012]
