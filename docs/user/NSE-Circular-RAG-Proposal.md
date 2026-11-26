# NSE Circular RAG --- Project Proposal

## Objective

Build and evaluate a hybrid RAG system over an existing collection of
approximately 7,500 NSE-listed circular PDF documents and associated
JSON metadata. Demonstrate, using reproducible evidence, when BM25 +
dense retrieval + reranking improves on dense retrieval alone.

## Existing assets

``` text
data/
├── pdfs/
│   └── *.pdf
└── metadata/
    └── *.json

fetch_nse_circulars.py
```

The downloader: - Fetches paginated NSE circular listings from
`exchangecirculars.com`. - Parses circular detail pages for metadata. -
Finds PDF or ZIP document links and extracts PDFs. - Saves PDF files
under `data/pdfs/`. - Saves per-circular JSON metadata under
`data/metadata/`. - Writes an aggregate `all_circulars_metadata.json`.

Available metadata fields include circular ID, title, date, category,
description, summary, key points, impact, severity, stocks, tags,
source, links, document URL, local PDF path and archive listing page.

**Data-quality caveat:** The supplied sample PDF is a SEBI order
concerning Akar Laminators Limited, although its metadata labels the
source as NSE. The downloader's `page` field is the listing-page number,
not the PDF page. Therefore, validate every PDF/metadata pair and use
actual PDF page numbers extracted from the PDF. Do not assume all files
are unique, valid, text-searchable NSE circulars.

## Technology

  Layer                      Technology
  -------------------------- ---------------------------------------------------------
  Language/package manager   Python + uv
  RAG orchestration          LlamaIndex
  PDF extraction             PyMuPDF
  Chunking                   SentenceSplitter, initial 500-token chunks / 50 overlap
  Embeddings                 OpenAI `text-embedding-3-small`
  Vector store               ChromaDB
  Keyword retrieval          BM25Retriever
  Fusion                     Reciprocal Rank Fusion (RRF)
  Reranking                  Cohere Rerank v5 Fast
  Generation                 GPT-4.1-mini

## Architecture

1.  Inventory and validate PDF/JSON pairs.
2.  Normalize metadata and preserve provenance.
3.  Extract PDF text page by page, retaining actual page numbers.
4.  Chunk documents and attach stable IDs and metadata.
5.  Batch-ingest into persistent ChromaDB and a matching BM25 index.
6.  Run dense, hybrid and hybrid-plus-reranking retrieval.
7.  Generate evidence-grounded answers with circular/page citations.
8.  Evaluate quality, latency, cost and failure modes.
9.  Demonstrate incremental ingestion, metadata filtering and citation
    validation.

## Feature plan

  --------------------------------------------------------------------------
  Order            Feature          Scope                           Estimate
  ---------------- ---------------- ------------------ ---------------------
  1                F001 --- Corpus  Validate 7,500-PDF            60--90 min
                   Ingestion &      corpus, extract,   
                   Hybrid RAG       chunk, index and   
                                    query              

  2                F002 ---         Label 30--50                  45--60 min
                   Evaluation &     queries; Recall@5, 
                   Benchmarking     MRR, faithfulness  

  3                F003 ---         p50/p95 latency,              30--45 min
                   Performance,     cost, failure      
                   Cost & Failures  analysis           

  4                F004 ---         Incremental                   45--60 min
                   Production       ingestion,         
                   Signals          metadata filters,  
                                    citation checks    

  5                F005 ---         Reproducibility,              20--30 min
                   Documentation &  results and        
                   Blog             engineering case   
                                    study              
  --------------------------------------------------------------------------

Estimates are implementation targets, not guarantees; corpus validation
and extraction problems may increase the time.

## Evaluation design

Create `eval.jsonl` with at least 30--50 manually labelled queries: -
Exact circular ID. - Exact phrase/keyword. - Semantic rule question. -
Multi-circular comparison. - Metadata-constrained query.

Each query records its type, optional filters, expected circular IDs,
optional expected PDF pages and reference answer/facts. Verify labels
against source PDFs; obtain a second review where practical.

Compare: 1. Dense retrieval. 2. BM25 + dense + RRF. 3. BM25 + dense +
RRF + reranking.

Metrics: - Recall@5 and MRR, overall and by query type. - Answer
faithfulness against retrieved passages. - p50 and p95 latency, split
into retrieval, reranking, generation and total. - Actual cost/query for
embeddings, reranking and LLM usage. - One-time ingestion/embedding cost
separately, with amortization assumptions stated.

Use the same corpus snapshot, query set, filters and generation settings
for all configurations.

## Production signals

-   Idempotent, resumable, batched ingestion with content hashes and
    stable chunk IDs.
-   Skip unchanged PDFs; replace chunks only for changed documents.
-   Keep BM25 and dense indexes on the same corpus version.
-   Normalize and filter by available date, category/source and
    department metadata.
-   Track duplicate and possible supersession relationships without
    assuming newer means superseding.
-   Validate citations against circular existence, actual PDF page count
    and source passage.

## Deliverables

-   Working RAG over the validated corpus.
-   Corpus inventory and data-quality report.
-   Persistent ChromaDB and reproducible BM25 index.
-   Three retrieval configurations.
-   Labelled evaluation dataset and benchmark outputs.
-   Latency/cost report and `failure-analysis.md`.
-   Demonstrations of incremental ingestion, metadata filtering and
    citation validation.
-   README and short engineering blog with real circular examples and
    measured results.

## Constraints

-   Reuse the downloaded corpus; do not redownload by default.
-   Keep code, dependencies and configuration minimal.
-   No frontend, API server, deployment or additional database unless
    evidence requires it.
-   Process the corpus in batches; do not assume all documents/chunks
    fit in memory.
-   Preserve raw PDFs and metadata.
-   Do not fabricate metrics, metadata, circular relationships or
    citations.
-   Record important decisions as VERIFIED / ASSUMED / UNKNOWN.

## Blog outline

**Hook:** Why vector search alone isn't enough for enterprise RAG.

**Problem:** Dense search can miss exact identifiers; keyword search can
miss semantic matches.

**Solution:** BM25 + dense retrieval + RRF + reranking.

**Example:** Use verified exact-ID and semantic queries from the
downloaded corpus.

**Evidence:** Compare Recall@5, MRR, faithfulness, p95 latency and cost.

**Failure analysis:** Show real failures involving extraction, metadata,
duplicates, supersession or ambiguity.

**Production lesson:** Incremental ingestion, metadata filters and
citation validation matter as much as retrieval quality.
