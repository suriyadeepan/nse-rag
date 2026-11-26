# F005 — Documentation & Engineering Blog (POC) Plan

## Scope and approach

- **P001** Update `README.md` with the implemented local architecture and technology choices, corpus paths, environment/API setup, ingestion/query commands, retrieval modes, existing evaluation/benchmark commands and links to saved evidence. Preserve current supported commands; document no resume workflow. [R001]
- **P002** Add a concise blog at `docs/005-engineering-blog.md`, grounded in F001–F004 journals and saved eval artifacts. Cover the required nine-part narrative, report actual source-PDF examples with real page numbers, distinguish measurements from estimates, and disclose observed misses and data limitations. [R002–R005]
- **P003** Validate every reported count, score, latency, token/cost estimate, failure and example against the existing canonical journal or artifact. Do not run ingestion, benchmarks, extra audits or provider calls to generate new blog evidence. [R002–R004, A002–A008]
- **P004** Record implementation decisions and evidence in this feature journal and keep completion status in the F005 TODO only. [A001–A008]

## Affected files and dependencies

- **P005** Update `README.md`; add `docs/005-engineering-blog.md`; add `docs/005-documentation-engineering-blog-todo.md` and `docs/005-documentation-engineering-blog.md`; update local `.current`. [R001–R005]
- **P006** No code, script, dependency, index, corpus or evaluation artifact changes are planned. Reuse `docs/001-nse-rag.md`, `docs/002-rag-evaluation-benchmarking.md`, `docs/003-performance-cost-failure-analysis.md`, `docs/004-poc-quality-checks.md`, and the saved `eval/` reports/results. [R001–R005]

## Architecture compatibility matrix

| Area | Status | Evidence / verification |
|---|---|---|
| Python runtime | VERIFIED for project configuration | `.python-version` is 3.14 and `pyproject.toml` requires Python >=3.14; F001 records successful CPython 3.14.10 dependency/import verification. F005 changes no runtime behavior. |
| CPU architecture | VERIFIED for current host | `uname -sm` returned `Darwin arm64`; F001 records native dependency verification on arm64. F005 adds no native package. |
| Native dependencies | VERIFIED for existing implementation | Existing PyMuPDF, ChromaDB/ONNX Runtime and LlamaIndex integrations are recorded as imported and exercised in F001/F002; F005 changes documentation only. |
| Container format | UNKNOWN / not applicable | No container configuration or container deployment target is used by this local POC. |
| Deployment target | VERIFIED for existing POC scope | The CLI uses local `data/pdfs`, `data/metadata`, and persisted `data/index`; F005 introduces no deployment target or runtime change. |
| External services | VERIFIED as existing behavior | OpenAI supplies embeddings/answers/claim checks; Cohere is used only for hybrid-rerank. F005 only documents established behavior and results; no service calls are planned. |

Automated compatibility checks: inspect README commands against `pyproject.toml`, `src/nse_rag/cli.py`, `scripts/evaluate_rag.py`, and `scripts/benchmark_performance.py`. Documentation acceptance is fact reconciliation against saved reports and source artifacts; no application compatibility change is expected.

## Risks and mitigations

- **P007** Documentation can overstate measurements or conflate answer support with retrieval-target recall: verify all numbers against saved artifacts and describe these as separate checks. [R003, R004, A003, A008]
- **P008** Corpus records have inconsistent provenance and metadata: accurately describe downloader provenance, qualify the corpus, and use actual source PDF pages rather than metadata listing pages. [R002, A002, A004, A006]
- **P009** The small F002/F003 sample can be mistaken for broad guarantees: state query count/types, repetitions, limits and evidence boundaries; do not add unmeasured metrics. [R003, R005, A003, A008]
- **P010** README commands could drift from implementation: verify the command syntax and env loading directly against CLI/script entry points during implementation. [R001, A001]

## Acceptance and validation

- **P011** Check README setup, corpus locations, API keys, one-command ingestion/query, all retrieval modes, evaluator/benchmark commands and evidence links against current implementation and artifact paths. [R001, A001, A007]
- **P012** Reconcile all corpus facts, duration, metadata behavior and provenance against F001's journal and downloader; disclose 23 skipped documents and unmeasured corpus statistics. [R002, A002, A006]
- **P013** Reconcile query count/type/labels, metrics, latency, sampled token/cost data, unavailable Cohere usage and failures against F002/F003 artifacts. Include no p95 or unsupported claims. [R003, A003, A008]
- **P014** Check the claim-status explanation and example against F004 artifacts; verify at least two circular ID/page examples against existing source-verified evidence and state the validator's limits and filter omission. [R004, A004–A005]
- **P015** Review the blog against its required structure, citations/links and concise POC scope. Run `git diff --check`; do not add or run tests for documentation-only changes unless implementation reveals a code behavior change. [R005, A001–A008]

## Architecture decisions

- **D001** Keep the feature's durable journal at the required `docs/005-documentation-engineering-blog.md` path and put the separate user-facing post at `docs/005-engineering-blog.md` to avoid conflating implementation history with the blog deliverable. This follows the repository's canonical journal convention. [P005]
- **D002** Reuse existing measurements and clearly label estimates/unavailable values; no new benchmark or corpus measurement will be run for writing. [P003, R002–R004]
