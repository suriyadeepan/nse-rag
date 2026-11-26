# F002 --- RAG Evaluation & Benchmarking

## Objective

Build a labelled evaluation set and quantitatively compare dense, hybrid
and reranked retrieval over the validated corpus of approximately 7,500
PDFs.

## Requirements

### R001 --- Evaluation query set

-   Create `eval.jsonl` with 30--50 manually labelled queries initially.
-   Sample across the corpus, dates, categories/departments and document
    types.
-   Cover:
    -   **Exact ID:** retrieve a known `circular_id`.
    -   **Exact phrase/keyword:** find a specific rule or phrase.
    -   **Semantic:** explain a regulatory requirement in natural
        language.
    -   **Multi-circular:** compare or trace a rule across multiple
        circulars.
    -   **Metadata-constrained:** retrieve within a
        date/category/department filter where metadata supports it.
-   Include difficult cases: duplicate/superseded documents, ambiguous
    wording, tables and poor extraction.

Each record must contain: - `query` - `type` - `filters` (optional) -
`expected_ids` (relevant circular IDs) - `expected_pages` (optional,
actual PDF page numbers) - `expected_answer` or reference facts

Example:

``` json
{
  "query": "Find circular 93c9fd2077d9f39b",
  "type": "exact_id",
  "filters": {},
  "expected_ids": ["93c9fd2077d9f39b"],
  "expected_pages": [1],
  "expected_answer": "The document is a SEBI order concerning Akar Laminators Limited."
}
```

The sample identifier and answer above are based on the supplied sample
metadata/PDF; validate all labels against source documents. Have a
second reviewer verify labels where practical.

### R002 --- Retrieval metrics

For each configuration calculate: - Recall@5: fraction of labelled
relevant circulars found in the top 5. - MRR: reciprocal rank of the
first relevant result. - Report macro-averages overall and by query
type. - For multi-circular queries, count all expected relevant
circulars in the recall denominator.

### R003 --- Answer quality

-   Measure faithfulness against retrieved passages.
-   Use manual claim-level review or an LLM judge supplied with the
    answer and retrieved evidence.
-   Report supported-claim rate and the number of unsupported answers.
-   Keep retrieval relevance separate from answer faithfulness.

### R004 --- Controlled comparison

Compare: 1. Dense. 2. BM25 + dense + RRF. 3. BM25 + dense + RRF +
reranking.

Use identical queries, corpus snapshot, metadata filters, candidate
limits and generation settings. Save raw ranked results and evaluation
outputs.

### R005 --- Benchmark report

Publish:

  Metric               Dense   Hybrid   Hybrid + Rerank
  ------------------ ------- -------- -----------------
  Recall@5               TBD      TBD               TBD
  MRR                    TBD      TBD               TBD
  Faithfulness (%)       TBD      TBD               TBD

Break down retrieval metrics by exact-ID, keyword, semantic,
multi-circular and metadata-constrained query types.

## Acceptance criteria

-   At least 30 labelled queries, with category counts reported.
-   Every expected circular ID and page is verified against the source.
-   All configurations evaluated against identical test cases and corpus
    snapshot.
-   Metrics reproducible from saved results.
-   No fabricated or selectively reported scores.
