# F004 — POC Quality Checks (Metadata & Citations) Plan

## Scope and approach

- **P001** Reuse `answer_from_passages` and the existing CLI. Preserve the answer text and source tags; add a lightweight claim-check result model that associates each factual claim with cited source references and reports **Supported**, **Unsupported**, or **Needs review**. Run a simple GPT-4.1-mini validation against only the claim's cited retrieved passages. Treat malformed or uncertain output as **Needs review** and label validation as an automated aid. [R003, A005–A006]
- **P002** Extend source references to carry `title` and publication `date` when present in indexed metadata. Include those fields in retrieved evidence and displayed references without inferring or repairing values. If returned passages expose similar/conflicting documents, surface their circular IDs/dates and describe the ambiguity; do not select a winner or implement revision tracking. [R002.1, R004, A007]
- **P003** Do not implement metadata filters. Current dense retrieval (Chroma) and BM25 are separate query paths; consistent pre-RRF metadata filtering needs branch-specific behavior not exposed as a shared simple option. Record this POC limitation in the plan and a durable implementation/evidence document. [R001, A002]
- **P004** Select five representative factual answers from saved F002/F003 evaluation evidence. Manually trace each citation's circular ID to its indexed `pdf_path`, open that PDF, check page bounds and compare passage text with the actual page. Record each citation's result and observed issue in `eval/citation-check.md`; this checks citation integrity, not claim entailment. [R002, A003–A004]
- **P005** Manually review at least five factual claim checks against their displayed cited evidence; record observed correct outcomes and obvious false positives/negatives in a small `eval/claim-validation.md` evidence artifact. [R003, A006]
- **P006** No ingestion, schema migration, index rebuild, new dependency, test framework or production system. Keep validation additive and compatible with persisted F001 indexes. [A001, O001–O006]

## Affected files and dependencies

- **P007** Update `src/nse_rag/answer.py` for claim/result data and lightweight validation; update `src/nse_rag/cli.py` to display statuses, evidence, dates/titles and the automated-aid note; extend focused answer/CLI tests. Add `eval/citation-check.md` and `eval/claim-validation.md`; add F004 TODO and journal documents. [R002–R004, A003–A007]
- **P008** Reuse installed LlamaIndex OpenAI integration and GPT-4.1-mini. No dependency, index format, ingestion metadata schema or persisted data changes. Validation requires OpenAI credentials; manual citation checks require the local persisted index and source PDFs. [A001]

## Architecture compatibility matrix

| Area | Status | Evidence / validation |
|---|---|---|
| Python runtime | VERIFIED for project configuration; implementation uses `uv` | `pyproject.toml` requires Python >=3.14; F001/F002 plans record the CPython 3.14 environment. A local `uv python list` also shows unrelated Python 3.15 interpreters, so prescribed execution remains `uv run`. |
| CPU architecture | VERIFIED: arm64 Darwin | Current `uname -sm` returned `Darwin arm64`; no architecture-specific change is planned. |
| Native dependencies | VERIFIED for current stack | F001/F002 record successful PyMuPDF, ChromaDB, ONNX Runtime and LlamaIndex use; F004 adds no native packages. |
| Container format | UNKNOWN / not applicable | No container configuration is used by this local CLI POC. |
| Deployment target | VERIFIED: local developer machine | F001/F002 use local PDF files and persisted `data/index`; both `data/pdfs` and `data/index` are present. F004 does not rebuild or migrate the index. |
| External services | VERIFIED as existing integrations; F004 validation call pending | The answer flow already uses GPT-4.1-mini. Claim validation adds a lightweight call and requires configured OpenAI credentials/network. No new provider is introduced. |

Compatibility checks: focused `uv run pytest` for answer/CLI behavior; verify CLI retains current citation fields and reports claim statuses, and reopen/read existing indexes without invoking ingestion. Separately perform the manual PDF spot-check and live representative claim review; report credential/service failures as such.

## Risks and mitigations

- **P009** An LLM validator can be wrong or return malformed output: treat it as an aid, show the evidence, fail to **Needs review**, and manually inspect five representative factual claims. [R003.4–R003.6]
- **P010** Claim splitting or mapping citations to individual claims may be incomplete: ask the lightweight validator to return claim-level source tags; keep original answer citations visible and mark incomplete mappings **Needs review**. [R003.1–R003.3]
- **P011** Index metadata may lack titles/dates or retrieved passages may not reveal a document conflict: display only fields already stored, state ambiguity only when evidence exposes it, and never infer supersession. [R004, A007]
- **P012** PDF source text may differ from indexed chunks due to extraction/normalization: compare normalized whitespace for the manual spot-check while recording any mismatch, using the source PDF page as authority. [R002.3–R002.5]

## Acceptance and validation

- **P013** Keep F001 ingestion/index schema unchanged and verify persisted index reopen/query without rebuilding. [A001, A007]
- **P014** Inspect five F002/F003 answers and every citation in each selected answer against source mapping, page bounds and actual PDF page text; publish the exact outcomes in `eval/citation-check.md`. [R002–R002.5, A003–A004]
- **P015** Validate the rendered claim statuses and evidence display, then manually inspect at least five factual claims and record results including obvious false positives/negatives in `eval/claim-validation.md`. [R003, A005–A006]
- **P016** If tests are run, use only the prescribed `uv` environment and focused answer/CLI checks. Keep automated tests, manual PDF verification and live LLM checks separately reported; do not run ingestion or rebuild indexes. [A001–A007]
