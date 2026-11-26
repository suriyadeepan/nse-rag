# F002 — RAG Retrieval Evaluation

## Setup

- 24 source-verified queries: 6 each for exact ID, keyword/phrase, semantic, and multi-circular questions.
- Full persisted index: 36,853 nodes, 7,591 source PDF paths, and 7,591 distinct circular IDs.
- All retrieval modes used 20 candidates and final top 5. Repeated chunks were collapsed by circular ID for Recall@5 and MRR.

## Retrieval comparison

| Metric | Dense | Hybrid | Hybrid + Rerank |
|---|---:|---:|---:|
| Recall@5 | 0.4375 | 0.7083 | 0.7292 |
| MRR | 0.4063 | 0.5708 | 0.7153 |
| Supported answers (sample) | 3/3 | 3/3 | 3/3 |

Retrieval means by query type:

| Query type | Dense R@5 / MRR | Hybrid R@5 / MRR | Hybrid + Rerank R@5 / MRR |
|---|---:|---:|---:|
| Exact ID | 0.0000 / 0.0000 | 1.0000 / 0.5000 | 1.0000 / 1.0000 |
| Keyword/phrase | 0.6667 / 0.6667 | 0.6667 / 0.6667 | 0.8333 / 0.8333 |
| Semantic | 0.6667 / 0.4583 | 0.6667 / 0.6667 | 0.5000 / 0.4167 |
| Multi-circular | 0.4167 / 0.5000 | 0.5000 / 0.4500 | 0.5833 / 0.6111 |

Examples from the saved per-query results:

- **Exact-ID improvement:** Query 1 expected circular `0001fd562caa1c25`. Dense did not retrieve it in its unique top five; hybrid placed it second and hybrid-rerank placed it first.
- **Semantic rerank miss:** Query 14 expected `0006c75b3e7d74a0`. Dense found it at rank 4 and hybrid at rank 1; reranking did not return that circular in its top five. Its generated answer instead listed other provisionally empanelled firms supported by the returned circulars, showing that a grounded answer can still miss the labelled target when the question admits multiple answers.
- **Multi-circular tie:** Query 19 expected `00b388f1536c50c4` and `0006ec6de19b9b41`. All three modes retrieved both in their top five; dense and hybrid-rerank ranked the Hercules circular first, while hybrid ranked the Current Infraprojects circular second.

## Answer grounding spot-check

Nine answers were generated with the existing GPT-4.1-mini answer pipeline: three queries per retrieval mode. Classification was manual and based on the answer's cited retrieved passages. PDF page numbers below are the actual source PDF page metadata, not archive listing pages.

The same nine cases were generated a second time to recover complete citation details after the first command's console output was truncated. The classifications below cover the final nine-answer set; 18 model completions were made in total.

| Mode | Query | Generated answer summary | Cited passage checked | Classification |
|---|---|---|---|---|
| Dense | Gayatri Projects trading restart date (query 13) | Trading restarts April 09, 2026. | `0001fd562caa1c25`, p. 1: suspension revoked effective April 09, 2026; the answer also cited the closing effective-date statement on p. 1. | Supported |
| Dense | HERCULES company name change (query 16) | Hercules Hoists Limited changes to Hercules Investments Limited effective November 24, 2025. | `00b388f1536c50c4`, p. 1: existing/new company names and effective date are listed. | Supported |
| Dense | Whitebox algo providers (query 14) | Listed provisionally empanelled firms including Neutrino Trading and other whitebox vendors. | `2e05513156afee5a`, p. 14: current provider list pairs vendor names with algo type; cited individual provider circulars also confirm listed empanelments. | Supported |
| Hybrid | Subject of circular `0001fd562caa1c25` (query 1) | Revocation of trading suspension in Gayatri Projects shares, effective April 09, 2026. | `0001fd562caa1c25`, p. 1: subject, revocation date, and compliance explanation. | Supported |
| Hybrid | Whitebox algo providers (query 14) | Listed Neutrino, Stockwiz, Quick Algoplus, Modern Algos, and AlgoBulls. | `0006c75b3e7d74a0`, `075fa795bfc794af`, `4b351d4b68e3378c`, `0fca1b4b5e9a09b8`, and `450491def5758600`, all p. 1: cited passages identify the relevant provider and whitebox status/provisional history. | Supported |
| Hybrid | Hercules name change and Current Infraprojects segment transfer dates (query 19) | November 24, 2025; September 17, 2025. | `00b388f1536c50c4`, p. 1: Hercules effective date; `0006ec6de19b9b41`, p. 1: transfer to rolling segment date. | Supported |
| Hybrid + Rerank | Subject of circular `000205e2a3e7c439` (query 2) | November 21, 2026 SLBM mock trading and NEAT SLBM 1.3.4 release, with schedule and participation guidance. | `000205e2a3e7c439`, pp. 1–4: title/date/version and cited schedule and guidance. | Supported |
| Hybrid + Rerank | SLBM mock-session fund obligations (query 9) | Mock trades do not cause fund pay-in or pay-out. | `000205e2a3e7c439`, p. 3 and `dd3f93aa3d3d8565`, p. 3: both state no fund pay-in or pay-out for mock-session trades. | Supported |
| Hybrid + Rerank | Whitebox algo providers (query 14) | Listed Koti Labs, Quartgen, Quick Algoplus, Futures Unchained, and AlgoBulls. | `578b584051d67986`, `a9ed0d1da406450d`, `4b351d4b68e3378c`, `685ef1eb32d7f89f`, and `1ed973f00593342a`, all p. 1: each cited circular names the provider and provisional empanelment; the passages identify whitebox algo status. | Supported |

| Grounding class | Dense | Hybrid | Hybrid + Rerank | Total |
|---|---:|---:|---:|---:|
| Supported | 3 | 3 | 3 | 9 |
| Unsupported | 0 | 0 | 0 | 0 |
| Insufficient evidence | 0 | 0 | 0 | 0 |

The reranked query 14 answer is supported by the passages it cited, but those passages concern different valid providers from the labelled expected circular. Grounding classification does not override the retrieval metric miss.

Detailed ranked IDs and retrieval metrics for all 24 queries are in [`results.json`](results.json). The evaluator's Cohere request pacing, first-attempt rate-limit failure, and successful retry are documented in the F002 journal.
