# F003 --- Performance, Cost & Failure Analysis

## Objective

Measure retrieval trade-offs at the scale of the existing approximately
7,500-PDF corpus and identify important failure modes.

## Requirements

### R001 --- Latency measurement

-   Benchmark all three configurations: Dense, Hybrid and Hybrid +
    Rerank.
-   Run at least 30 measured repetitions per query/configuration after
    warm-up; report the number of queries and runs.
-   Measure retrieval, reranking, generation and end-to-end latency
    separately.
-   Report p50 and p95 latency.
-   Record hardware, concurrency, cache state, candidate limits and
    model/provider versions.
-   Separate cold-start/index-loading latency from warm query latency.

### R002 --- Cost measurement

Calculate: - Query embedding cost using actual token usage and provider
pricing. - Reranking cost using actual billed units and provider
pricing. - LLM input/output cost using actual token usage and provider
pricing. - Total variable cost per query. - One-time corpus
ingestion/embedding cost separately. - Estimated amortized ingestion
cost per query at stated query volumes.

Do not estimate reranking cost from document count unless that matches
the provider's billing model. Record price date and currency.

### R003 --- Failure analysis

Create `failure-analysis.md`.

Investigate: - Exact circular ID not retrieved. - Metadata/PDF mismatch
or missing metadata. - Duplicate or superseded circular returned instead
of the applicable version. - Ambiguous references and multi-circular
omissions. - Tables, scanned pages or structured content extracted
incorrectly. - PDF page attribution or citation errors. - Correct
retrieval but incorrect or unsupported generated answer. - BM25/vector
corpus-version mismatch or stale index.

For each failure record: - Query and query type. - Expected and actual
circular IDs/pages. - Observed failure. - Root cause and evidence. -
Proposed fix and regression test.

### R004 --- Consolidated benchmark

Publish:

  Metric               Dense   Hybrid   Hybrid + Rerank
  ------------------ ------- -------- -----------------
  Recall@5               TBD      TBD               TBD
  MRR                    TBD      TBD               TBD
  Faithfulness (%)       TBD      TBD               TBD
  p50 latency (ms)       TBD      TBD               TBD
  p95 latency (ms)       TBD      TBD               TBD
  Cost/query             TBD      TBD               TBD

Also report corpus size, chunk count, index size, ingestion duration and
failure counts.

## Acceptance criteria

-   Latency and cost reported for all configurations under documented
    conditions.
-   At least three representative failures documented with root causes.
-   Costs use measured token/usage data and dated provider prices.
-   Comparisons use actual measurements and the same corpus snapshot.
