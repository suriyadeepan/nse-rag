# F005 --- Documentation & Engineering Blog

## Objective

Publish a reproducible engineering case study showing the strengths and
trade-offs of dense, hybrid and reranked RAG over the existing NSE PDF
corpus.

## Requirements

### R001 --- Project documentation

Document: - Architecture and technology choices. - Source and downloader
workflow. - Corpus layout: `data/pdfs/*.pdf` and
`data/metadata/*.json`. - Metadata schema, matching rules and known
data-quality limitations. - Setup, ingestion, resume and query
instructions. - Retrieval configurations and evaluation methodology. -
How to reproduce benchmark results.

### R002 --- Corpus facts and provenance

Report measured values, not assumptions: - PDF count and metadata JSON
count. - Matched records, unmatched PDFs/metadata, invalid files and
duplicates. - Document date range and available categories/sources. -
Extractable, empty and scanned/image-only PDFs. - Chunk count, index
size and ingestion duration.

Explain that the downloader obtains NSE listing pages from
`exchangecirculars.com` and may extract PDFs from ZIP responses.
Validate document contents and metadata before describing the entire
corpus as NSE circulars. The supplied sample PDF is a SEBI order
concerning Akar Laminators Limited; its metadata `page` field refers to
an archive listing page, not a PDF page.

### R003 --- Publish benchmark evidence

Include: - Number of labelled queries and query distribution. -
Labelling and verification methodology. - Recall@5, MRR and
faithfulness. - p50/p95 latency and cost/query. - Three representative
failure cases and fixes. - Corpus size, chunk count and ingestion
performance.

### R004 --- Demonstrate production signals

Include reproducible examples of: - Incremental ingestion of a
new/changed PDF. - Metadata-filtered retrieval. - Citation validation
using actual PDF page numbers. - Handling of duplicates, missing
metadata and superseded documents.

### R005 --- Blog structure

-   **Hook:** Why vector search alone isn't enough for enterprise RAG.
-   **Problem:** Exact-match identifiers versus semantic search.
-   **Corpus:** Approximately 7,500 PDFs plus metadata; report validated
    counts and limitations.
-   **Solution:** BM25 + dense retrieval + RRF + reranking.
-   **Example:** Use real, verified circular IDs and rules found in the
    corpus. Do not use placeholder IDs or assume the sample SEBI order
    is a market-wide circuit-breaker circular.
-   **Evidence:** Measured retrieval quality, latency and cost.
-   **Failure analysis:** PDF extraction, metadata quality, duplicates,
    supersession and ambiguous queries.
-   **Production considerations:** Incremental ingestion, metadata
    filters and citation validation.
-   **Takeaway:** Combine complementary retrieval methods, measure
    trade-offs and validate evidence.

## Acceptance criteria

-   README contains reproducible setup and execution instructions.
-   Corpus statistics are generated from the actual files.
-   Benchmark tables contain actual measured values.
-   Blog examples cite real documents and actual PDF pages.
-   Data-source limitations and failures are disclosed.
-   No fabricated performance claims.
-   F001--F004 deliverables are linked or referenced.
