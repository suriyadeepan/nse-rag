# F005 — Documentation & Engineering Blog (POC) Requirements

## Objective

Publish a concise, reproducible engineering case study showing what worked, what did not, and the trade-offs between dense, hybrid and reranked RAG over the full NSE PDF collection. Reuse completed F001–F004 work; do not build extra tooling for documentation. [R001]

## Requirements

### R001 — Practical project documentation

- **R001.1** Ensure the README explains the architecture and main technology choices.
- **R001.2** Document where existing PDFs and metadata live.
- **R001.3** Document environment setup and API key configuration.
- **R001.4** Document the one-command full-corpus ingestion and query commands.
- **R001.5** Explain dense, hybrid and hybrid-rerank modes.
- **R001.6** Document how to run the existing evaluation and benchmark scripts.
- **R001.7** Link or point to saved evaluation, performance, failure and claim-validation results.
- **R001.8** Keep instructions aligned with working commands. Do not add a separate resume workflow or extensive operational runbook.

### R002 — Report verified corpus facts

- **R002.1** Use measured F001 counts: 7,614 PDFs discovered; 7,612 per-document metadata JSON files found in the corpus check; 7,611 metadata records loaded during ingestion; 7,591 documents indexed; 23 skipped; and 36,853 chunks indexed.
- **R002.2** Report the measured full-ingestion duration of approximately 11 minutes 47 seconds and the existing index inventory.
- **R002.3** Briefly explain metadata fields used for retrieval and citations.
- **R002.4** Disclose known limitations, including textless or unusable PDFs and that metadata does not always prove PDF identity.
- **R002.5** Describe provenance accurately: the downloader obtains listing/detail information from `exchangecirculars.com` and may extract PDFs from ZIP responses. Do not state that every file is an NSE circular without qualification; the inspected sample SEBI order is not an NSE circular.
- **R002.6** Explain that metadata `page` is an archive listing page, not a PDF page number; cite actual PDF pages from PyMuPDF.
- **R002.7** Reuse existing logs and index artifacts. Do not add exhaustive audits or complex corpus-statistics tooling; label unavailable statistics as not measured.

### R003 — Present benchmark evidence

- **R003.1** Reuse F002/F003 results, including 24 source-verified labelled queries: six each for exact ID, keyword/phrase, semantic and multi-circular queries.
- **R003.2** Summarize the labelling approach and source-PDF verification.
- **R003.3** Report Recall@5 and MRR for dense, hybrid and hybrid-rerank.
- **R003.4** Report measured average and p50 retrieval latency for all three modes.
- **R003.5** Report measured answer token usage and cost estimate; clearly mark Cohere usage/cost unavailable.
- **R003.6** Report the one-time corpus embedding estimate separately from query-time costs.
- **R003.7** Include a few representative observed failure cases and practical implications.
- **R003.8** Use saved reports/results. Do not rerun ingestion or the full benchmark solely for the blog, and do not invent p95, faithfulness percentages or unmeasured costs.

### R004 — Explain evidence and claim validation

- **R004.1** Demonstrate F004's answer experience: claim-level **Supported**, **Unsupported** or **Needs review** statuses.
- **R004.2** Explain that each claim displays its linked circular ID, title/date when available, actual PDF page and supporting passage.
- **R004.3** Use one real example to show how the validator checks a claim against the cited passage.
- **R004.4** State that automated validation is an aid, not a guarantee, and users should inspect cited evidence.
- **R004.5** Explain that metadata filters were omitted because consistent filtering of dense and BM25 branches requires custom implementation beyond this POC.
- **R004.6** Use `eval/claim-validation.md` and `eval/citation-check.md`; do not claim comprehensive claim-entailment validation.

### R005 — Engineering blog

- **R005.1** Write one concise post with these sections, in order: hook (why vector search alone can miss exact identifiers); problem (exact IDs/phrases versus semantic questions); corpus (measured counts and data limits); solution (BM25 + dense + Reciprocal Rank Fusion + reranking); example (real verified IDs, passages and actual PDF pages); evidence (measured retrieval metrics, latency and cost); failure analysis (real misses or operational issues and lessons); answer trust (claim validation and limitations); takeaway (choose retrieval based on measured query needs and make source evidence inspectable).
- **R005.2** Keep the post focused on this POC and its measured findings. Avoid generic production-readiness claims.

## Acceptance criteria

- **A001** README setup, ingestion, query and evaluation instructions match the working implementation.
- **A002** Corpus statistics match F001's recorded run.
- **A003** Benchmark tables match saved F002/F003 results.
- **A004** At least two examples use verified circular IDs and actual PDF pages.
- **A005** Claim-validation behavior and limitations are accurate.
- **A006** Data-source limitations, skipped documents and observed failures are disclosed.
- **A007** F001–F004 documentation and evaluation artifacts are linked or referenced.
- **A008** No fabricated metrics, unverified examples or production-readiness claims are included.

## Out of scope

- **O001** New ingestion, benchmarking or corpus-audit tooling.
- **O002** Incremental/resumable ingestion documentation beyond noting that it is not implemented.
- **O003** Production deployment, monitoring, scaling or operational runbooks.
- **O004** Exhaustive metadata, duplicate or supersession analysis.
- **O005** A long-form research paper or comprehensive RAG survey.

## Implementation principle

Write only from evidence already produced by F001–F004. Keep the README practical and the blog concise. If a metric or corpus fact was not measured, state that rather than manufacturing evidence. [R001–R005]
