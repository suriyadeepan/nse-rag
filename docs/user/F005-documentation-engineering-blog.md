# F005 — Documentation & Engineering Blog

## Objective

Publish a concise, reproducible engineering case study showing what worked, what did not, and the trade-offs between dense, hybrid and reranked RAG over the full NSE PDF collection. Reuse the completed F001–F004 work; do not build extra tooling just for documentation.

## Requirements

### R001 — Practical project documentation

Ensure the README explains:

- Architecture and the main technology choices.
- Where the existing PDFs and metadata live.
- How to set up the environment and API keys.
- The one-command full-corpus ingestion and query commands.
- Dense, hybrid and hybrid-rerank modes.
- How to run the evaluation and benchmark scripts.
- Where to find saved evaluation, performance, failure and claim-validation results.

Keep instructions aligned with the commands that actually work. No separate resume workflow or extensive operational runbook.

### R002 — Report verified corpus facts

Use the measured F001 results:

- PDFs discovered, metadata records loaded, documents indexed/skipped and chunks indexed.
- Index inventory and ingestion duration.
- Basic explanation of the metadata fields used for retrieval and citations.
- Known limitations, including textless/unusable PDFs and the fact that metadata does not always prove PDF identity.

Current verified baseline from F001:
- 7,614 PDFs discovered.
- 7,612 per-document metadata JSON files were found in the corpus check; 7,611 metadata records loaded during ingestion.
- 7,591 documents indexed; 23 skipped.
- 36,853 chunks indexed.
- Full ingestion took approximately 11 minutes 47 seconds.

Explain provenance accurately: the downloader obtains listing/detail information from `exchangecirculars.com` and may extract PDFs from ZIP responses. Do not describe every file as an NSE circular without qualification. The inspected sample SEBI order is not an NSE circular, and metadata `page` is an archive listing page, not a PDF page number. Cite actual PDF page numbers from PyMuPDF.

Do not add new exhaustive corpus audits or complex corpus-statistics tooling. Use existing logs/index artifacts and clearly label unavailable statistics as not measured.

### R003 — Present benchmark evidence

Reuse F002/F003 results. Include:

- Labelled query count and query types.
- Labelling approach and source-PDF verification.
- Recall@5 and MRR for all three retrieval modes.
- Measured average and p50 retrieval latency.
- Measured answer token usage and cost estimate; mark unavailable Cohere usage/cost clearly.
- One-time corpus embedding estimate separately from query-time cost.
- A few representative failure cases and their practical implications.

Use the actual saved reports/results. Do not rerun ingestion or the full benchmark solely to write the blog. Do not invent p95, faithfulness percentages, or cost figures that were not measured.

### R004 — Explain user-facing evidence and claim validation

Demonstrate the answer experience from F004:

- Answers show claim-level **Supported**, **Unsupported**, or **Needs review** statuses.
- Each claim shows its circular ID, title/date where available, actual PDF page and supporting passage.
- Explain with one real example how the validator checks a claim against its cited passage.
- State clearly that automated validation is an aid, not a guarantee; users should inspect the cited evidence.
- Mention that metadata filters were left out because applying consistent filters to both dense and BM25 branches would require extra custom implementation beyond this.

Use the existing `eval/claim-validation.md` and `eval/citation-check.md` evidence. Do not claim comprehensive claim-entailment validation.

### R005 — Engineering blog

Write one concise blog post using this structure:

1. **Hook:** Why vector search alone can miss exact identifiers in enterprise documents.
2. **Problem:** Exact circular IDs/phrases versus semantic questions.
3. **Corpus:** The measured full-corpus counts and important data limitations.
4. **Solution:** BM25 + dense retrieval + Reciprocal Rank Fusion + reranking.
5. **Example:** Use real, verified circular IDs, source passages and actual PDF pages.
6. **Evidence:** Actual retrieval metrics, latency and cost measurements.
7. **Failure analysis:** Show a few real misses or operational issues and what they taught us.
8. **Answer trust:** Show claim-level validation and its limitations.
9. **Takeaway:** Choose retrieval methods based on measured query needs and make source evidence inspectable.

Keep the post focused on the project and its measured findings. Avoid generic production-readiness claims.

## Acceptance criteria

- README setup, ingestion, query and evaluation instructions match the working implementation.
- Corpus statistics match F001's recorded run.
- Benchmark tables match F002/F003 saved results.
- At least two examples use verified circular IDs and actual PDF pages.
- Claim-validation behavior and its limitations are explained accurately.
- Data-source limitations, skipped documents and observed failures are disclosed.
- F001–F004 documentation and evaluation artifacts are linked or referenced.
- No fabricated metrics, unverified examples or production-readiness claims.

## Out of scope

- New ingestion, benchmarking or corpus-audit tooling.
- Incremental/resumable ingestion documentation beyond noting it is not implemented.
- Production deployment, monitoring, scaling or operational runbooks.
- Exhaustive metadata, duplicate or supersession analysis.
- A long-form research paper or comprehensive RAG survey.

## Implementation principle

Write from the evidence already produced by F001–F004. Keep the README practical and the blog concise. If a metric or corpus fact was not measured, say so instead of adding work to manufacture it.
