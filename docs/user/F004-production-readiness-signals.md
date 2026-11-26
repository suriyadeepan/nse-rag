# F004 --- Production-Readiness Signals

## Objective

Demonstrate reliable corpus maintenance, metadata filtering and
evidence-backed citations without adding unnecessary infrastructure.

## Requirements

### R001 --- Incremental and resumable ingestion

-   Treat `data/pdfs/*.pdf` and `data/metadata/*.json` as source inputs;
    never mutate them.
-   Use stable circular IDs and deterministic chunk IDs.
-   Calculate content hashes for PDFs and normalized metadata.
-   Skip unchanged documents.
-   Detect new, changed, missing and deleted source records.
-   Replace only affected chunks when a PDF or relevant metadata
    changes.
-   Make ingestion idempotent and resumable after interruption.
-   Keep dense and BM25 indexes on the same corpus version.
-   Record ingestion state and errors in a manifest or lightweight local
    database.
-   Handle the aggregate `all_circulars_metadata.json` separately from
    per-document JSON files to avoid duplicate ingestion.

### R002 --- Metadata normalization and filtering

-   Normalize available metadata including circular ID, date, source,
    category, title, tags, stocks and department where reliably
    available.
-   Preserve missing values as unknown; do not invent fields.
-   Distinguish archive listing page from actual PDF page.
-   Support filters by date range, category/source and department when
    present.
-   Apply equivalent filters to dense and BM25 retrieval before fusion.
-   Test filters against documents with missing or inconsistent
    metadata.

### R003 --- Supersession and document relationships

-   Preserve duplicate documents and possible revisions as separate
    source records until their relationship is verified.
-   Where metadata or source text establishes a supersession/revision
    relationship, store it explicitly.
-   Do not infer that a newer publication automatically supersedes an
    older circular.
-   Allow retrieval and answers to identify date and version context.

### R004 --- Citation validation

-   Cite circular ID, title, actual PDF page number and supporting
    passage.
-   Verify that each cited circular exists in the corpus and each page
    number is within the PDF's page count.
-   Verify that the cited passage is present on the cited page.
-   Flag unsupported claims and missing evidence; do not present
    citation existence as proof of entailment.
-   Reject malformed or unverifiable citations.

## Acceptance criteria

-   New documents can be ingested without rebuilding the full index.
-   Unchanged documents create no duplicate chunks.
-   Changed documents replace their prior chunks.
-   Interrupted ingestion can resume safely.
-   Metadata filters return consistent results across retrieval
    branches.
-   Supersession is represented only when supported by evidence.
-   Invalid IDs, page numbers and passages are detected by citation
    checks.
