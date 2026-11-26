# F001 --- NSE Corpus Ingestion & Hybrid RAG (POC)

## Objective

Build a small, working RAG proof of concept over the existing NSE
PDF/metadata collection. Prioritize the shortest reliable
implementation; do not build production-grade ingestion infrastructure.

## Existing inputs

-   PDFs: `data/pdfs/*.pdf`
-   Per-document metadata: `data/metadata/*.json`
-   Downloader: `fetch_nse_circulars.py`
-   Optional aggregate metadata:
    `data/metadata/all_circulars_metadata.json`

The downloader fetches circular listing pages from
`exchangecirculars.com`, extracts detail-page metadata and downloads PDF
or ZIP-wrapped PDF documents. Metadata may include `circular_id`,
`title`, `date`, `category`, `description`, `summary`, `key_points`,
`impact`, `severity`, `stocks`, `tags`, `source`, `link`,
`document_url`, `pdf_local_path` and listing `page`.

**Data caveats** - Treat JSON metadata as descriptive input, not proof
that the PDF content matches it. Spot-check extracted title/ID against
the PDF. - The supplied sample PDF is a SEBI order concerning Akar
Laminators, despite being listed in the NSE collection. - Metadata
`page` is the archive listing page, not a PDF page number. Extract
actual PDF page numbers directly from PyMuPDF. - Do not assume every
file is unique or is an NSE circular.

## Technology

-   Python + uv
-   LlamaIndex
-   PyMuPDF
-   ChromaDB
-   OpenAI `text-embedding-3-small`
-   GPT-4.1-mini
-   BM25Retriever
-   Cohere Rerank v5 Fast

## POC scope

-   Process the full existing corpus of approximately 7,500 PDFs in
    `data/pdfs/*.pdf`; do not limit ingestion to a 100--200 PDF sample.
-   Select documents deterministically (e.g. sorted file paths) so runs
    are reproducible.
-   Use the existing local files. Do not redownload documents.
-   Prefer a simple, one-pass ingestion script over a general ingestion
    framework.
-   Batch extraction, embedding and index writes as needed to handle all
    7,500 PDFs without excessive memory use.
-   Keep only basic validation. Log and skip unreadable PDFs or
    unusable metadata; do not build complex recovery workflows.

## Requirements

### R001 --- Load documents and metadata

-   Read per-document JSON files from `data/metadata/*.json`.
-   Exclude `all_circulars_metadata.json` from per-document loading to
    avoid duplicate records.
-   Match metadata to PDFs primarily using `pdf_local_path`; fall back
    to `circular_id`/filename stem.
-   Use the PDF filename stem as a fallback ID when metadata is missing.
-   For the POC, assume one JSON object per metadata file, as in the
    supplied sample.
-   Log and skip malformed JSON, missing PDFs and unreadable PDFs.
-   Print a compact summary: PDFs found, metadata records loaded,
    documents indexed and documents skipped.
-   Do not implement exhaustive duplicate detection, schema migration or
    a metadata reconciliation engine.

### R002 --- Extract and chunk PDFs

-   Extract text page by page using PyMuPDF.
-   Retain the actual 1-based PDF page number on each page/chunk.
-   Skip pages with no extracted text; log PDFs that produce no usable
    text.
-   Do not add OCR in this POC.
-   Use LlamaIndex `SentenceSplitter` with an initial target of 500
    tokens and 50-token overlap.
-   Attach `circular_id`, `title`, `date`, `category`, `source`,
    `pdf_path` and `page_number` where available.
-   Add the circular ID and title to searchable text where useful.

### R003 --- Build the indexes

-   Persist dense vectors in a local ChromaDB collection.
-   Build BM25 from the same in-memory nodes used to create the Chroma
    index.
-   Process all 7,500 PDFs in batches where needed to keep memory
    usage reasonable. Build the BM25 corpus from the same complete set
    of extracted nodes used for dense indexing.
-   Use a clean POC collection for a fresh run; deleting/recreating the
    POC index is acceptable.
-   Do not implement content hashes, stable chunk IDs, resumable
    ingestion, incremental updates or index-version management in this
    feature.

### R004 --- Implement retrieval configurations

Provide three selectable configurations over the same full indexed corpus:

1.  Dense vector retrieval.
2.  BM25 + dense retrieval + Reciprocal Rank Fusion (RRF).
3.  BM25 + dense retrieval + RRF + Cohere reranking.

-   Use the same top-k settings and candidate corpus for fair
    comparison.
-   Keep metadata filters out of scope for this feature.
-   Ensure the BM25 index and Chroma collection are built from the same
    run.

### R005 --- Generate answers with source references

-   Use GPT-4.1-mini to answer from retrieved passages only.
-   Return circular ID, actual PDF page number and supporting passage.
-   If retrieved evidence is insufficient, say so rather than guessing.
-   Do not use the metadata listing `page` field as a PDF page citation.

## Acceptance criteria

-   A fresh checkout can ingest the full 7,500-PDF corpus using one
    documented command.
-   The script reports how many PDFs were found, indexed and skipped.
-   At least one exact-ID query and one semantic query return
    inspectable passages from the full corpus.
-   Dense, hybrid and hybrid-plus-reranking modes all run against the
    same full corpus.
-   Generated answers show circular IDs and actual PDF page numbers.
-   ChromaDB persists and can be reopened for querying.
-   No silent failure: skipped files and extraction failures are printed
    or saved to a simple log.

## Out of scope

-   Production-grade incremental ingestion, content hashing and
    resumability.
-   OCR and complex table extraction.
-   Exhaustive duplicate detection or supersession tracking.
-   Metadata filtering by date/department.
-   Citation entailment validation.
-   API server, frontend, deployment, monitoring or distributed
    infrastructure.
-   Comprehensive corpus cleaning. Handle basic failures by logging and
    skipping.

## Implementation principle

Build and validate the end-to-end pipeline against the full 7,500-PDF
corpus. Keep the implementation small; add complexity only when a
measured POC failure requires it.
