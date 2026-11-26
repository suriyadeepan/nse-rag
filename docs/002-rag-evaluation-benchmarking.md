# F002 — RAG Evaluation & Benchmarking

## Implementation record

### T001 — Labelled query set

- Added `eval/eval.jsonl` with 24 questions: six each of `exact_id`, `keyword_phrase`, `semantic`, and `multi_circular`. Each line contains the required `query`, `type`, and `expected_ids`; answerable fact questions also include `expected_answer`.
- Verified every expected ID against the persisted `data/index/nodes.jsonl` metadata and its `pdf_path`, then opened that exact local PDF and checked the cited actual PDF page text. The metadata `page` field from any archive listing was not used. All source PDFs are extractable text PDFs; no OCR or supersession examples were selected.
- Source evidence for each JSONL record, in file order:

| Record | Type | Expected circular ID(s) | Source PDF page and checked evidence |
|---:|---|---|---|
| 1 | exact_id | `0001fd562caa1c25` | `0001fd562caa1c25.pdf`, p. 1: subject names revocation of Gayatri Projects trading suspension. |
| 2 | exact_id | `000205e2a3e7c439` | `000205e2a3e7c439.pdf`, p. 1: title names the November 21, 2026 SLBM mock trading and NEAT SLBM release. |
| 3 | exact_id | `0006c75b3e7d74a0` | `0006c75b3e7d74a0.pdf`, p. 1: subject is provisional empanelment of an algo provider. |
| 4 | exact_id | `002a2392b14074e2` | `002a2392b14074e2.pdf`, p. 1: subject is listing Treasury Bills and SDLs on the Capital Market segment. |
| 5 | exact_id | `00b388f1536c50c4` | `00b388f1536c50c4.pdf`, p. 1: subject is the Hercules Hoists name change. |
| 6 | exact_id | `0277f3f018affc12` | `0277f3f018affc12.pdf`, p. 1: subject is timings on the Muhurat Trading session. |
| 7 | keyword_phrase | `0001fd562caa1c25` | `0001fd562caa1c25.pdf`, p. 1: trading suspension “will be revoked w.e.f. April 09, 2026.” |
| 8 | keyword_phrase | `0006c75b3e7d74a0` | `0006c75b3e7d74a0.pdf`, p. 1: M/s. Neutrino Trading Private Limited; type of algo “Whitebox.” |
| 9 | keyword_phrase | `000205e2a3e7c439` | `000205e2a3e7c439.pdf`, p. 3: “No Financial Obligation”; mock-session trades do not result in fund pay-in or pay-out. |
| 10 | keyword_phrase | `02370ae61ea8c0e5` | `02370ae61ea8c0e5.pdf`, p. 1: RTCM applies to EQ, BE, BZ, SM, ST, and SZ series for symbols in the June 2026 file. |
| 11 | keyword_phrase | `00b388f1536c50c4` | `00b388f1536c50c4.pdf`, p. 1: name change is effective November 24, 2025. |
| 12 | keyword_phrase | `019be8813f32f2c3` | `019be8813f32f2c3.pdf`, p. 2: weekend holidays list includes Mahashivratri, Ramzan-Id, Independence Day/Parsi New Year, and Diwali Amavasya. |
| 13 | semantic | `0001fd562caa1c25` | `0001fd562caa1c25.pdf`, p. 1: says when the suspension is lifted and trading resumes. |
| 14 | semantic | `0006c75b3e7d74a0` | `0006c75b3e7d74a0.pdf`, p. 1: names Neutrino Trading Private Limited and Whitebox algo type. |
| 15 | semantic | `002a2392b14074e2` | `002a2392b14074e2.pdf`, pp. 1–2: Capital Market segment listing effective November 10, 2025; p. 2 annexure identifies the instruments. |
| 16 | semantic | `00b388f1536c50c4` | `00b388f1536c50c4.pdf`, p. 1: HERCULES company name changes from Hercules Hoists Limited to Hercules Investments Limited. |
| 17 | semantic | `0277f3f018affc12` | `0277f3f018affc12.pdf`, p. 1: Muhurat trading is to be held Sunday, November 08, 2026. |
| 18 | semantic | `0056795fa8001874` | `0056795fa8001874.pdf`, p. 1: additional margin imposed on all variants of Silver and Gold Futures; the table lists the applicable contracts and rates. |
| 19 | multi_circular | `00b388f1536c50c4`, `0006ec6de19b9b41` | Both p. 1: Hercules name change effective November 24, 2025; Current Infraprojects moves to rolling segment effective September 17, 2025. |
| 20 | multi_circular | `0001fd562caa1c25`, `0006ec6de19b9b41` | Both p. 1: Gayatri Projects trading suspension revoked April 09, 2026; Current Infraprojects segment transfer effective September 17, 2025. |
| 21 | multi_circular | `002a2392b14074e2`, `0056795fa8001874` | Both p. 1: Treasury Bills/SDL listing effective November 10, 2025; additional margin notice specifies Gold and Silver Futures contracts. |
| 22 | multi_circular | `019be8813f32f2c3`, `0277f3f018affc12` | Both p. 1: one circular covers 2026 commodity settlement holidays; the Muhurat circular gives Sunday, November 08, 2026. |
| 23 | multi_circular | `004593f561909ea9`, `01c1933b3b9a9c71` | Both p. 1: ASM notice dated January 06, 2026; ESM notice dated April 23, 2026. |
| 24 | multi_circular | `02370ae61ea8c0e5`, `00f8f41b17a62f91` | Both p. 1: RTCM notice specifies eligible series and excludes approved securities, Nifty 500 constituents and ETFs; ST-ASM notice specifies Stage I inclusion and 50% or existing margin (whichever higher, capped at 100%). |

- Added `tests/test_eval_data.py` to validate JSONL parsing, required/allowed fields, non-empty values, unique queries and IDs, 24-query balanced type coverage, and at least two expected IDs for multi-circular questions.
- Source identity was cross-checked using each indexed node's `circular_id`, `title`, and `pdf_path`; the named PDF exists locally and its page text supports the associated label. F002's required 7,591-document/36,853-node baseline check remains T003 evidence and is not claimed by this dataset task.

#### Verification

- `uv run pytest -q tests/test_eval_data.py` — passed (1 test).
- Implementation evidence: 24 JSONL records inspected against indexed source identity and actual source PDF page text as listed above.
- Retrieval, full-index comparison, and answer-grounding verification are outside T001 and remain pending their linked tasks.
