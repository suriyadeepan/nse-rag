# F004 — POC Quality Checks (Metadata & Citations)

## Objective

Add only a small amount of evidence-backed validation to the completed F001–F003 RAG POC. Do not turn the project into a production ingestion or document-governance system.

## Requirements

### R001 — Basic metadata filters (only if straightforward)

- Expose simple optional filters for `category`, `source`, or `date` using metadata already stored in the index.
- Apply the same selected filters to dense and BM25 retrieval before RRF.
- Missing metadata means the document will not match a filter on that field; do not build metadata repair or normalization workflows.
- If consistent filtering across both retrieval branches is non-trivial, leave filters out and document the limitation. Do not build custom filtering infrastructure.

### R002 — Citation integrity spot-check

- Reuse F001's answer and citation format: circular ID, title where available, actual PDF page number, and supporting passage.
- Manually inspect **5 representative answers** from the existing F002/F003 evaluation.
- For each citation, verify:
  - The circular ID maps to an indexed source PDF.
  - The page number is within that PDF's page range.
  - The supporting passage appears on that actual PDF page.
- Record pass/fail and any observed issue in `eval/citation-check.md`.
- Treat this as a citation integrity check, not proof that every generated claim is entailed by its cited passage.

### R003 — User-facing claim validation

- Add a lightweight validation step for generated answers: check whether each factual claim is supported by the retrieved passage(s) cited for it.
- Show the result directly with the answer, using simple statuses such as **Supported**, **Unsupported**, or **Needs review**.
- For each claim, show its supporting circular ID, actual PDF page, and passage so the user can inspect the evidence.
- Example: for the claim “Trading suspension was revoked on April 9, 2026,” check the cited PDF page. Mark it **Supported** if the page confirms the date; otherwise mark it **Unsupported** or **Needs review**.
- Keep the validator simple: use an LLM-based check or equivalent lightweight approach. Do not build a comprehensive fact-checking framework.
- Make clear that this is an automated aid, not a guarantee of correctness. Never silently present an unsupported claim as verified.

### R004 — Minimal document relationship handling

- Do not implement supersession or revision tracking.
- Preserve the existing source circular ID and publication date in retrieved passages where available.
- If a query exposes a likely duplicate or conflicting version, show the IDs/dates and describe the ambiguity; do not automatically decide which document supersedes another.

## Acceptance criteria

- Existing F001 ingestion and indexes continue to work without rebuild or schema migration.
- If simple metadata filters are implemented, the same filter is applied to dense and BM25 retrieval before fusion; otherwise, the limitation is documented.
- Five answer citations are checked against the source PDF and actual page text.
- Citation-check results are saved in `eval/citation-check.md`.
- Generated answers display a claim-level status and the evidence used for each claim.
- At least five representative factual claims are checked; results and any obvious false positives/negatives are recorded.
- No unsupported supersession decisions or fabricated metadata are introduced.

## Out of scope

- Incremental, resumable or idempotent ingestion.
- Content hashing, deterministic chunk IDs, manifests or ingestion databases.
- Metadata normalization, repair, exhaustive validation or complex filter combinations.
- Supersession detection, version graphs or automatic conflict resolution.
- Comprehensive claim-entailment or citation-validation framework; only the lightweight user-facing check above is in scope.
- Production monitoring, dashboards, APIs or deployment infrastructure.

## Implementation principle

Reuse the completed pipeline. Prefer a small manual validation artifact over new infrastructure. Implement metadata filters only if they fit cleanly into the existing retrieval code; otherwise, document them as out of scope for this POC.
