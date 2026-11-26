# F001 — NSE Corpus Ingestion & Hybrid RAG (POC)

## Objective

Build a small, working RAG proof of concept over the existing NSE PDF/metadata collection. Prioritize the shortest reliable implementation; do not build production-grade ingestion infrastructure. [R001]

## Inputs and data constraints

- PDFs are in `data/pdfs/*.pdf`; per-document metadata is in `data/metadata/*.json`. The downloader is `fetch_nse_circulars.py`; optional aggregate metadata is `data/metadata/all_circulars_metadata.json`. Metadata may contain document identity, descriptive text, classifications, affected stocks/tags, source links, local path and listing page. [R002]
- Treat metadata as descriptive input, not proof of PDF contents. Spot-check extracted title/ID against the PDF. The supplied sample is a SEBI order concerning Akar Laminators despite its NSE listing. [R003]
- Metadata `page` is an archive listing page. Extract actual PDF page numbers using PyMuPDF. Do not assume every file is unique or an NSE circular. [R004]

## Technology

- Python + `uv`, LlamaIndex, PyMuPDF, ChromaDB, OpenAI `text-embedding-3-small`, GPT-4.1-mini, LlamaIndex BM25Retriever, and Cohere Rerank v5 Fast. [R005]

## POC scope

- Process the full existing corpus (approximately 7,500 PDFs), deterministically, using local files only; do not redownload. [R006]
- Prefer a simple one-pass ingestion script over a general framework. Batch extraction, embedding, and index writes to bound memory. [R007]
- Keep validation basic: log and skip unreadable PDFs or unusable metadata; avoid complex recovery. [R008]

## Requirements

### R009 — Load documents and metadata

- Read per-document JSON files and exclude `all_circulars_metadata.json`. Match primarily by `pdf_local_path`, then by `circular_id`/filename stem. Use the PDF stem as fallback ID. [R009.1]
- Assume one JSON object per metadata file. Log and skip malformed JSON, missing PDFs and unreadable PDFs. [R009.2]
- Print a compact summary of PDFs found, metadata records loaded, documents indexed and skipped. [R009.3]
- Do not build exhaustive duplicate detection, schema migration or metadata reconciliation. [R009.4]

### R010 — Extract and chunk PDFs

- Extract text page by page with PyMuPDF, retaining actual 1-based page number for every page/chunk. Skip pages without text and log PDFs with no usable text. No OCR. [R010.1]
- Use LlamaIndex `SentenceSplitter`, initially 500 tokens with 50-token overlap. [R010.2]
- Attach available `circular_id`, `title`, `date`, `category`, `source`, `pdf_path` and `page_number`; include circular ID/title in searchable text where useful. [R010.3]

### R011 — Build indexes

- Persist dense vectors in a local ChromaDB collection. Build BM25 from the same in-memory nodes used for Chroma. [R011.1]
- Batch processing as needed for the entire corpus; BM25 and dense indexing must use the same complete set of extracted nodes. [R011.2]
- Use a clean POC collection for a fresh run; deleting/recreating it is acceptable. Do not implement hashes, stable chunk IDs, resumability, incremental updates or index version management. [R011.3]

### R012 — Retrieval configurations

Provide selectable configurations over the same full corpus: (1) dense retrieval, (2) BM25 + dense + Reciprocal Rank Fusion (RRF), and (3) BM25 + dense + RRF + Cohere reranking. Use the same top-k settings/candidate corpus for fair comparison; metadata filters are out of scope. Ensure BM25 and Chroma are built from the same run. [R012]

### R013 — Answers and references

- GPT-4.1-mini answers from retrieved passages only. [R013.1]
- Return circular ID, actual PDF page number and supporting passage. If evidence is insufficient, say so instead of guessing. Never cite metadata listing `page` as a PDF page. [R013.2]

## Acceptance criteria

- A fresh checkout can ingest all local PDFs with one documented command; report found, indexed and skipped counts. [R014.1]
- Exact-ID and semantic queries return inspectable passages; dense, hybrid and reranked modes run against the same full corpus. [R014.2]
- Answers show circular IDs and actual PDF page numbers. Chroma persists and reopens for querying. [R014.3]
- Skips and extraction failures are printed or saved in a simple log; no silent failure. [R014.4]

## Implementation principle

Build and validate end to end against the full corpus. Keep implementation small and add complexity only when a measured POC failure requires it. [R016]
