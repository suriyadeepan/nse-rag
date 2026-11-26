# NSE Circular RAG

**Turn thousands of exchange PDFs into answers you can inspect, page by page.**

NSE circulars can change what businesses and investors need to do—but the important details are often buried in dense documents. NSE Circular RAG helps make those changes clear: ask a question in plain language and get an explanation of what changed, who may be affected, and where to find the supporting passage.

The planned pipeline extracts PDF text and real page numbers, combines ChromaDB vector search with LlamaIndex BM25 and reciprocal rank fusion, and can rerank results with Cohere
before LLM answers from cited passages.

## Requirements at a glance

- Ingest the full local PDF and per-document metadata collection, with basic
  logging for malformed metadata and unreadable or textless PDFs.
- Preserve actual PDF page numbers and return circular IDs, pages, and evidence
  passages with answers.
- Offer dense, hybrid, and hybrid-plus-reranking retrieval over the same corpus.
- Persist vectors locally; keep ingestion deterministic and simple to rerun.

The planned stack is Python 3.15+, `uv`, PyMuPDF, LlamaIndex, ChromaDB, OpenAI
embeddings (`text-embedding-3-small`) and GPT-4.1-mini, plus Cohere Rerank v5
Fast for reranking.

## What’s complete

- A downloader for circular listings, metadata, and PDF or ZIP-wrapped PDF files.
- Parser and download tests, with saved HTML and PDF samples.

**The full-corpus ingestion and retrieval pipeline is not implemented yet.** The
RAG components and their API keys will be needed when that work is added.

## Local development

```bash
uv sync
uv run pytest
```

Downloaded corpus files belong under `data/pdfs/` and `data/metadata/`; these
directories are excluded from Git. Sample files are in `data/samples/`.
