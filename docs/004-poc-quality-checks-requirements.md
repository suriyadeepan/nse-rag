# F004 — POC Quality Checks (Metadata & Citations) Requirements

## Objective

Add only a small amount of evidence-backed validation to the completed F001–F003 RAG POC. Do not turn the project into a production ingestion or document-governance system. [R001]

## Requirements

### R001 — Basic metadata filters (only if straightforward)

- **R001.1** Expose simple optional filters for `category`, `source`, or `date` using metadata already stored in the index.
- **R001.2** Apply the same selected filters to dense and BM25 retrieval before RRF.
- **R001.3** Missing metadata means the document will not match a filter on that field; do not build metadata repair or normalization workflows.
- **R001.4** If consistent filtering across both retrieval branches is non-trivial, leave filters out and document the limitation. Do not build custom filtering infrastructure.

### R002 — Citation integrity spot-check

- **R002.1** Reuse F001's answer and citation format: circular ID, title where available, actual PDF page number, and supporting passage.
- **R002.2** Manually inspect 5 representative answers from the existing F002/F003 evaluation.
- **R002.3** For each citation, verify that the circular ID maps to an indexed source PDF, the page number is within that PDF's page range, and the supporting passage appears on that actual PDF page.
- **R002.4** Record pass/fail and any observed issue in `eval/citation-check.md`.
- **R002.5** Treat this as a citation integrity check, not proof that every generated claim is entailed by its cited passage.

### R003 — User-facing claim validation

- **R003.1** Add a lightweight validation step for generated answers: check whether each factual claim is supported by the retrieved passage(s) cited for it.
- **R003.2** Show the result directly with the answer, using statuses **Supported**, **Unsupported**, or **Needs review**.
- **R003.3** For each claim, show its supporting circular ID, actual PDF page, and passage so the user can inspect the evidence.
- **R003.4** Mark a claim **Supported** only when cited PDF evidence confirms it; otherwise mark **Unsupported** or **Needs review**.
- **R003.5** Keep the validator simple: use an LLM-based check or equivalent lightweight approach. Do not build a comprehensive fact-checking framework.
- **R003.6** Make clear that this is an automated aid, not a guarantee of correctness. Never silently present an unsupported claim as verified.

### R004 — Minimal document relationship handling

- **R004.1** Do not implement supersession or revision tracking.
- **R004.2** Preserve the existing source circular ID and publication date in retrieved passages where available.
- **R004.3** If a query exposes a likely duplicate or conflicting version, show the IDs/dates and describe the ambiguity; do not automatically decide which document supersedes another.

## Acceptance criteria

- **A001** Existing F001 ingestion and indexes continue to work without rebuild or schema migration.
- **A002** If simple metadata filters are implemented, the same filter is applied to dense and BM25 retrieval before fusion; otherwise, the limitation is documented.
- **A003** Five answer citations are checked against the source PDF and actual page text.
- **A004** Citation-check results are saved in `eval/citation-check.md`.
- **A005** Generated answers display a claim-level status and the evidence used for each claim.
- **A006** At least five representative factual claims are checked; results and any obvious false positives/negatives are recorded.
- **A007** No unsupported supersession decisions or fabricated metadata are introduced.

## Out of scope

- **O001** Incremental, resumable or idempotent ingestion.
- **O002** Content hashing, deterministic chunk IDs, manifests or ingestion databases.
- **O003** Metadata normalization, repair, exhaustive validation or complex filter combinations.
- **O004** Supersession detection, version graphs or automatic conflict resolution.
- **O005** Comprehensive claim-entailment or citation-validation framework; only the lightweight user-facing check above is in scope.
- **O006** Production monitoring, dashboards, APIs or deployment infrastructure.

## Implementation principle

Reuse the completed pipeline. Prefer a small manual validation artifact over new infrastructure. Implement metadata filters only if they fit cleanly into the existing retrieval code; otherwise, document them as out of scope for this POC.
