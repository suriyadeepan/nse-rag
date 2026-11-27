# F005 — Documentation & Engineering Blog TODO

Canonical task and status source for F005. Record task completion only after its acceptance evidence is documented in the F005 journal.

## T001 — Update practical README documentation

- **Status:** COMPLETE — README content and command syntax reconciled with the CLI and evaluation scripts.
- **Action:** Update the README with the verified architecture, input/index paths, environment and API setup, full-corpus ingest and query commands, retrieval modes, evaluation/benchmark commands and links to the saved reports/results. Check every command against the actual CLI/scripts. Do not describe resume support.
- **Files:** `README.md`, `docs/005-documentation-engineering-blog.md`
- **Requirements / plan:** R001, A001, A007; P001, P003–P006, P011
- **Acceptance:** README covers all R001 subrequirements and uses commands/options present in `src/nse_rag/cli.py`, `scripts/evaluate_rag.py` and `scripts/benchmark_performance.py`. Report/evidence links resolve to existing artifacts. Journal records checked references and outcomes.
- **Dependencies:** None.

## T002 — Write evidence-backed engineering blog

- **Status:** COMPLETE — concise nine-section post written from F001–F004 source evidence.
- **Action:** Write the concise post using the approved structure. Reconcile corpus statistics and provenance with F001, benchmark and failure details with F002/F003 artifacts, and claim-validation examples with F004 evidence. Include at least two verified circular IDs with actual PDF page numbers; distinguish retrieval performance from answer grounding and estimates from measured usage.
- **Files:** `docs/005-engineering-blog.md`, `docs/005-documentation-engineering-blog.md`
- **Requirements / plan:** R002–R005, A002–A008; P002–P003, P005–P006, P007–P009, P012–P014
- **Acceptance:** All required sections appear in order; all facts and numbers match the named saved evidence; data limitations, 23 skipped documents, observed failures, unavailable Cohere cost and validator limits are disclosed. No new measurements, unsupported metrics or production-readiness claims are added. Journal records evidence for examples and metrics.
- **Dependencies:** None.

## T003 — Reconcile documentation and converge

- **Status:** COMPLETE — README/blog content, lineage and evidence links reconciled; staged whitespace check passed.
- **Action:** Review the README and blog against every acceptance criterion and requirement/plan lineage; check local links, command syntax, evidence values and actual-page examples. Record implementation and documentation-review evidence in the journal, then update task status here. Run `git diff --check`; do not run application tests for documentation-only changes.
- **Files:** `README.md`, `docs/005-engineering-blog.md`, `docs/005-documentation-engineering-blog.md`, `docs/005-documentation-engineering-blog-todo.md`
- **Requirements / plan:** R001–R005, A001–A008; P003–P006, P011–P015
- **Acceptance:** Every requirement is covered by an implementation and a recorded documentation/evidence check. No unverified claim remains; any unavailable verification is stated. Whitespace/diff check passes. Automated test and real-world deployment verification are recorded as not applicable for this docs-only change, not as passing.
- **Dependencies:** T001, T002.

## Lineage coverage

- R001 → P001, P005–P006, P010–P011 → T001, T003 → README command and artifact-link review.
- R002 → P002–P003, P006–P008, P012 → T002–T003 → corpus facts/provenance reconciled against F001 journal and downloader evidence.
- R003 → P002–P003, P006–P007, P009, P013 → T002–T003 → benchmark/cost/failure statements reconciled against F002/F003 artifacts.
- R004 → P002–P003, P006–P008, P014 → T002–T003 → claim example and limitations reconciled against F004 artifacts.
- R005 → P002–P003, P006, P009, P015 → T002–T003 → required blog structure and evidence-bound scope reviewed.
- A001–A008 → P001–P006, P011–P015 → T001–T003 → README verification, evidence reconciliation and documentation review.

No application code, tests, dependencies, corpus or index changes are planned. This TODO does not claim automated test or deployment verification for the docs-only scope.
