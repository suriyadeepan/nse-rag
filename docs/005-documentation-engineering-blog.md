# F005 — Documentation & Engineering Blog Journal

## Implementation

- Updated `README.md` with the local architecture, input and index paths, metadata/page behavior, source provenance, environment/API setup, ingest/query commands, retrieval modes, evaluator/benchmark commands, saved evidence links, corpus facts, cost boundaries, and claim-validation caveat.
- Added `docs/005-engineering-blog.md` with the approved nine-part case-study structure. It distinguishes retrieval scores from answer grounding, actual costs from estimates, and available Cohere pricing from unavailable usage data.
- No application code, dependency, corpus, persisted index, evaluation result or benchmark script changed. No new measurements, API requests or corpus audit were run.

## Evidence and fact reconciliation

- Corpus facts in README and the post were checked against the F001 journal: 7,614 PDFs discovered; a separate check found 7,612 per-document metadata JSON files; ingestion loaded 7,611 metadata records; 7,591 documents indexed; 23 skipped; 36,853 chunks; full run 11m46.72s. The 7,612 discovery count and 7,611 loaded count are explicitly distinguished.
- The post describes `exchangecirculars.com` listing/detail provenance and ZIP extraction based on the existing downloader/F001 record. It qualifies the corpus as not exclusively NSE circulars and notes the inspected SEBI order concerning Akar Laminators. It states that metadata `page` is an archive listing page and that actual PDF citation pages come from PyMuPDF. No exhaustive identity or duplicate audit is claimed.
- The 24 labelled query count and six-per-type breakdown, source-PDF labelling method, Recall@5/MRR figures and query-type semantic rerank limitation were checked against `eval/report.md`, `eval/results.json`, F002's journal and the F003 report.
- Latency figures were copied from the F003 performance report: 10 representative queries, one warm-up and three measured repetitions per query/mode; 30 measured calls per mode. The post marks the sample as descriptive, not a guarantee.
- Cost figures were reconciled with F003: five sampled answers used 7,270 input / 228 output tokens, estimated at $0.0032728 total; query embedding is an approximately $0.0000004 estimate; Cohere usage and cost are unavailable; the one-time corpus embedding estimate is approximately $0.24 and was not incurred again. No p95, faithfulness percentage or Cohere charge was added.
- The two post examples were checked against source-verification artifacts: `0001fd562caa1c25`, p. 1 (Gayatri Projects revocation effective April 09, 2026) and `00b388f1536c50c4`, p. 1 (Hercules name change effective November 24, 2025). The answer-trust example uses F004's conservative **Needs review** for a November 21, 2026 SLBM claim mapped to `cbe480f0ca976c14`, p. 3, a June 6 session passage.
- Failure descriptions match `eval/failure-analysis.md`: dense exact-ID miss recovered by hybrid; reranking removed the expected semantic result from top five; and the initial Cohere HTTP 429 followed by successful sequential pacing at 6.2 seconds.
- F004's claim labels, displayed evidence, manual spot-check scope and metadata-filter omission are linked and described as approximate/non-comprehensive. README and post point to F002/F003/F004 reports and saved results.

## Verification

- README command syntax was compared with `src/nse_rag/cli.py` and the argument/configuration definitions in `scripts/evaluate_rag.py` and `scripts/benchmark_performance.py`. Both analysis scripts open the existing persisted index and use the saved evaluation query data; no ingestion path is invoked by those commands.
- Local artifact links in the README and blog were checked against the repository paths. The two PDF page examples rely on previously recorded manual PDF verification in F002/F004 evidence; PDFs were not re-audited for this documentation feature.
- Local-link check — passed for the README and blog (all Markdown link targets exist in the repository).
- `git diff --cached --check` — passed after staging the six F005 documentation files; the staged changes were reviewed.
- Automated tests: not run (documentation-only change; no application code changed).
- Real-world/deployment verification: not applicable to this documentation change; no deployment or live provider request was made.

## Convergence review — 2026-11-27

- Traced R001–R005 and A001–A008 through plan items P001–P015 and TODO tasks T001–T003. The README, blog, evidence links, metrics, cost boundaries, corpus limitations and F004 claim example satisfy the approved scope.
- Reviewed the implementation against the local CLI and analysis script definitions and checked all local Markdown targets. No runtime, dependency, index, evaluation or deployment behavior changed.
- `git diff --cached --check` passed. Application tests and deployment/live checks were not run because this is a documentation-only feature; the plan requires no new tests or provider validation.
- **Convergence status: CONVERGED.** No requirement gaps or remaining implementation tasks were found.
