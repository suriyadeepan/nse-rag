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

### T002 — Compact evaluator and metrics

- Added `scripts/evaluate_rag.py`. It loads the labelled JSONL, opens the existing local indexes through `open_local_indexes`, and uses F001's `retrieve` with fixed `RetrievalSettings(candidate_top_k=20, top_k=5)`.
- Each query runs sequentially through dense, hybrid, and hybrid-rerank. This keeps Cohere calls serialized. The evaluator saves the first-ranked unique circular IDs used for metrics, the raw circular IDs from returned chunks, and each query's Recall@5 and MRR. It also computes overall and per-type arithmetic means.
- The script counts persisted nodes, distinct `pdf_path` values, and circular IDs. It stops before retrieval if the node count or unique source-PDF path count differs from the F001 baseline (36,853 / 7,591). It never invokes ingestion; `eval/results.json` is written only after a complete run and remains for T003, when the real full-index evaluation is run.
- Added `tests/test_eval_metrics.py` for duplicate-chunk collapse, multiple expected IDs, reciprocal rank, Recall@5 cutoff, overall/type aggregation, sequential identical-mode settings, inventory counts, baseline mismatch handling, and JSON serialization.

#### Verification

- `uv run pytest -q tests/test_eval_metrics.py tests/test_eval_data.py` — passed (8 tests; third-party deprecation warnings only).
- `uv run python scripts/evaluate_rag.py --help` — passed; confirms the CLI loads without contacting retrieval services.
- `git diff --check` — passed.
- The evaluator was not run against the live index in this task, so no retrieval scores or `eval/results.json` are claimed. Full-index retrieval and Cohere behavior remain T003 verification.

### T003 — Full-index retrieval comparison

- Ran `uv run --env-file .env python scripts/evaluate_rag.py` against the existing `data/index`; no ingestion or embedding was run. The inventory check found **36,853 persisted nodes**, **7,591 distinct source `pdf_path` values**, and **7,591 distinct circular IDs**. The source-PDF count confirms the F001 baseline; circular-ID coverage is reported as a separate count.
- Evaluated all 24 identical labelled queries in `dense`, `hybrid`, and `hybrid-rerank` with `candidate_top_k=20` and `top_k=5`. Each mode has 24 per-query records. Metrics collapse repeated chunks by circular ID before computing Recall@5 and MRR. `eval/results.json` contains per-query unique ranked IDs, raw retrieved chunk IDs, expected IDs, query-level metrics, overall means, and means by query type.
- The first live attempt reached Cohere's trial limit and stopped with HTTP 429 (trial key limit: 10 calls/minute); it did not save a partial results file. Added a 6.2-second minimum interval between rerank requests and a pacing regression test, then reran successfully. All 24 rerank requests were issued sequentially. The successful evaluator run took about 3 minutes, excluding the cooldown before retry.
- The rerank pacing setting is included in result metadata. Cohere service limit and configured interval are recorded to make the live run reproducible.

#### Live retrieval results

| Mode | Overall Recall@5 | Overall MRR |
|---|---:|---:|
| Dense | 0.4375 | 0.4063 |
| Hybrid | 0.7083 | 0.5708 |
| Hybrid + Rerank | 0.7292 | 0.7153 |

Per-type means are saved in `eval/results.json`. In brief: dense exact-ID queries scored 0.0000 Recall@5 / 0.0000 MRR, while hybrid and hybrid-rerank scored 1.0000 Recall@5; reranking improved exact-ID MRR to 1.0000. On semantic queries, reranking scored 0.5000 Recall@5 / 0.4167 MRR, below dense and hybrid (both 0.6667 Recall@5; MRR 0.4583 and 0.6667 respectively). Final report examples and answer-grounding checks are recorded below and in `eval/report.md`.

#### Verification

- `uv run pytest -q tests/test_eval_metrics.py tests/test_eval_data.py` — passed (9 tests; third-party deprecation warnings only), including a regression check that rerank requests are separated by at least 6.2 seconds.
- `uv run --env-file .env python scripts/evaluate_rag.py` — completed: 24 queries × 3 modes; results saved to `eval/results.json`.
- Parsed the saved JSON and verified 24 records exist for each mode, settings are 20 candidates/top 5, and inventory is 36,853 nodes / 7,591 source PDFs / 7,591 circular IDs.
- First live attempt failed at the Cohere trial rate limit (HTTP 429); the paced retry completed successfully. This failure is retained here as execution evidence.

### T004 — Answer grounding spot-check

- Generated nine answers (three per mode) with `answer_from_passages` in `nse_rag.answer`, which uses GPT-4.1-mini. For each sample, retrieved passages again from the same persisted indexes with `RetrievalSettings(20, 5)`; Cohere calls for the three reranked samples were sequential and separated by at least 6.2 seconds.
- The nine-case generation command was run twice because the first command's console output was truncated before all citation details could be inspected. The report classifies the final nine-answer set; 18 model completions were made in total. This duplicated generation was not part of the planned 5–10 reported samples.
- Manually checked each answer's cited passages against the recorded circular ID and actual PDF page number. The nine query/mode selections, concise answer summaries, cited circulars/pages, and evidence notes are in `eval/report.md`.
- Grounding counts: dense supported 3, unsupported 0, insufficient evidence 0; hybrid supported 3, unsupported 0, insufficient evidence 0; hybrid-rerank supported 3, unsupported 0, insufficient evidence 0. Each mode denominator is three.
- Query 14 is a useful caveat: the reranked answer cited passages that support the listed whitebox algo providers, but those were different provider circulars from the query's single labelled expected ID. It is supported as a statement grounded in its citations while remaining a retrieval-target miss; the two judgments are recorded separately.

#### Verification

- `uv run --env-file .env python -` — opened existing local indexes, retrieved the nine selected query/mode passage sets, and generated each answer using the existing GPT-4.1-mini answer path; completed successfully.
- Manual review — all nine answer citations were inspected against their cited passage content and PDF page metadata. No LLM judge or automated claim-level validator was used.

### T005 — Report and evidence reconciliation

- Completed `eval/report.md` with overall and per-type Recall@5/MRR, full-index size, fixed 20-candidate/top-five settings, and 3/3 supported-answer counts per mode. It includes three examples checked against `eval/results.json`: exact-ID recovery, the semantic rerank miss on query 14, and the multi-circular query 19 ranking comparison.
- Reconciled the report with the saved result artifact: 24 queries appear in each of the three modes; results record 36,853 nodes, 7,591 source PDF paths and 7,591 distinct circular IDs. The reported query-type aggregates and examples agree with the saved per-query data.
- The answer-grounding table covers nine manually reviewed answers (three per mode). All nine were supported by their cited passages; unsupported and insufficient-evidence counts are zero. The report discloses that the same cases were generated a second time after truncated console output, for 18 completions total, while only the final nine were classified.
- No new implementation or architecture decision was needed. The Cohere first-attempt HTTP 429 and paced successful rerun, as well as the duplicated answer-generation execution, remain documented as actual failures/limitations.

#### Verification

- `uv run pytest -q tests/test_eval_metrics.py tests/test_eval_data.py` — passed (9 tests; third-party deprecation warnings only).
- Parsed `eval/results.json` and checked the three examples and aggregate values against the report; all matched. Confirmed 24 queries and 24 records for each mode, the full-index inventory, and fixed retrieval limits.
- Manual grounding evidence is recorded in the report and T004 journal section; it is distinct from automated test evidence and live retrieval evidence.
