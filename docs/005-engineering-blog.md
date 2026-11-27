# Exact IDs, better recall, and the evidence behind a small RAG POC

Vector search is good at finding related language. It can still miss a circular when the question hinges on an exact identifier. In a collection of regulatory and exchange documents, that miss can matter as much as semantic relevance.

## Problem: exact phrases and semantic questions

The same corpus has two different search problems: “find circular `0001fd562caa1c25`” and “when does the trading suspension end?” Dense embeddings can match the second by meaning, while exact IDs and phrases often benefit from lexical matching. This POC compares dense retrieval with a BM25 and dense hybrid, then tests a reranker on the fused candidates.

## Corpus: what was indexed

The downloader gets listing and detail information from `exchangecirculars.com`; some responses contain ZIP files from which it extracts PDFs. The resulting collection should not be assumed to contain only NSE circulars. The inspected sample includes a SEBI order concerning Akar Laminators. Metadata can describe a file but does not prove its identity.

In the measured F001 run, 7,614 PDFs were discovered. A separate corpus check found 7,612 per-document metadata JSON files; ingestion loaded 7,611 records, indexed 7,591 documents, skipped 23 and wrote 36,853 chunks. The full ingestion took 11 minutes 46.72 seconds (about 11 minutes 47 seconds). The saved index inventory is 7,591 source PDF paths and 36,853 chunks.

PyMuPDF extracts text with actual page numbers, and LlamaIndex chunks it. Indexed metadata may include circular ID, title, date, category, source and PDF path. IDs and titles are included in searchable text. Metadata `page` refers to an archive listing page, so it is not used as a PDF citation. There is no OCR; textless or otherwise unusable PDFs were among the skipped documents. The run did not include an exhaustive identity or duplicate audit, and duplicate rates or other exhaustive corpus statistics were not measured.

## Solution: combine lexical and semantic retrieval

Dense mode searches local Chroma vectors. Hybrid mode combines dense and BM25 results with Reciprocal Rank Fusion (RRF). Hybrid-rerank sends the fused candidates to Cohere Rerank v5 Fast. The same 20 candidates and final top 5 are used across modes. GPT-4.1-mini answers from retrieved passages; the CLI prints source IDs, actual PDF pages and passages.

## Examples: inspect the source page

- Circular `0001fd562caa1c25`, PDF page 1, says the trading suspension “will be revoked w.e.f. April 09, 2026.” The cited page supports the restart date. Dense retrieval missed this exact-ID target in the benchmark; hybrid placed it second and hybrid-rerank first.
- Circular `00b388f1536c50c4`, PDF page 1, identifies the change from Hercules Hoists Limited to Hercules Investments Limited and gives November 24, 2025 as its effective date. The saved citation review checked the ID against its indexed PDF, confirmed page 1 is in range, and found the supporting text there.

Both page references come from the actual PDF pages, not listing metadata. The [F002 answer evidence](../eval/report.md) and [F004 citation spot-check](../eval/citation-check.md) record the source checks.

## Evidence: retrieval, latency, and cost

F002 labelled 24 queries, six each for exact ID, keyword/phrase, semantic and multi-circular questions. Expected circular IDs were checked against indexed source PDFs and relevant page text. Scores deduplicate repeated chunks from the same circular.

| Metric | Dense | Hybrid | Hybrid + rerank |
|---|---:|---:|---:|
| Recall@5 (24 queries) | 0.4375 | 0.7083 | 0.7292 |
| MRR | 0.4063 | 0.5708 | 0.7153 |
| Retrieval latency average | 0.769 s | 0.698 s | 1.464 s |
| Retrieval latency p50 | 0.516 s | 0.521 s | 1.275 s |

Latency comes from a separate F003 sample of 10 queries (2 exact-ID, 4 keyword/phrase and 4 semantic), with one warm-up and three measured repetitions per query and mode. Rerank time is included. These small-sample measurements describe this run; they are not latency guarantees.

Five sampled GPT-4.1-mini answers used 7,270 input and 228 output tokens. Their estimated cost was $0.0032728 total, about $0.000655 per answer. One query embedding is estimated at roughly $0.0000004; these are estimates rather than account billing. Cohere rerank usage and cost were unavailable, so no rerank charge is included. The one-time F001 corpus embedding estimate was about $0.24 for approximately 11.8 million input tokens; it was not incurred again for F002/F003.

See the saved [retrieval report](../eval/report.md), [ranked results](../eval/results.json), [performance report](../eval/performance-report.md), and [raw performance measurements](../eval/performance-results.json) for query-level details.

## Failure analysis: the trade-offs are real

The exact-ID example shows why lexical retrieval helps: dense missed the expected circular, while hybrid found it. Reranking improved its rank further. The opposite happened on semantic query 14: hybrid put the expected whitebox-provider circular `0006c75b3e7d74a0` first, while reranking omitted it from the final five and returned other provider notices. Compare hybrid results when recall matters.

The first F002 rerank run also hit Cohere HTTP 429 at the trial limit. A retry with requests paced at least 6.2 seconds apart completed. This is an observed service limit, not a retrieval-quality issue. The [failure report](../eval/failure-analysis.md) records all three cases.

## Answer trust: claim labels are prompts to inspect evidence

The CLI labels claims **Supported**, **Unsupported** or **Needs review**, and displays each claim's mapped circular ID, title/date when available, actual PDF page and passage. For example, a claim about the November 21, 2026 SLBM mock session was mapped to circular `cbe480f0ca976c14`, page 3, whose title identifies a June 6 session. That passage says mock trades do not result in fund pay-in or pay-out, but it does not establish the November session; the validator returned **Needs review**.

The check is an automated aid, not a correctness guarantee. Claim splitting and source mapping can be approximate, so readers should inspect the displayed page and passage. The manual F004 review was small, not a comprehensive claim-entailment evaluation. Metadata filters were left out because applying the same condition to dense and BM25 retrieval before fusion needs additional custom behavior beyond this POC. See the [claim-validation review](../eval/claim-validation.md) and [citation integrity check](../eval/citation-check.md).

## Takeaway

For this measured query set, hybrid retrieval substantially improved overall Recall@5 and MRR over dense search, while reranking improved overall ranking quality at higher retrieval latency and lowered recall on the semantic subset. The useful choice depends on the query mix. Whichever mode is used, showing circular IDs, actual PDF pages and source passages makes the result easier to inspect—and makes retrieval misses visible.
