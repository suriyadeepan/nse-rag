# F003 Failure Analysis

### Exact circular ID missing in dense retrieval

- **Query or operation:** F002 query 1, “What is the subject of NSE circular 0001fd562caa1c25?”
- **Expected and actual result:** Expected `0001fd562caa1c25`. Dense top five contained `2e05513156afee5a`, `a8a431fa3b16ab37`, and `c650334c86e22de2`; hybrid retrieved the expected circular at rank 2; hybrid-rerank ranked it first.
- **What failed and likely cause:** Dense retrieval missed the exact-ID target. The specific cause is unknown; the result shows dense matching did not surface the exact identifier.
- **Practical fix or limitation:** Use hybrid retrieval when exact circular identifiers are part of the query workload.

### Relevant semantic result lowered by reranking

- **Query or operation:** F002 query 14, “Which firm received provisional approval to offer whitebox algorithmic trading solutions to NSE members?”
- **Expected and actual result:** Expected `0006c75b3e7d74a0`. Hybrid ranked it first; hybrid-rerank omitted it from the final five and returned other provider circulars.
- **What failed and likely cause:** Reranking lowered a relevant semantic result below the final cutoff. Why Cohere preferred the other provider circulars is not established by the available evidence.
- **Practical fix or limitation:** Treat reranked semantic results as fallible; compare against hybrid when recall matters.

### Cohere trial rate limit on F002 evaluation

- **Query or operation:** F002 rerank request sequence.
- **Expected and actual result:** Expected the sequential rerank evaluation to complete. The first attempt returned HTTP 429 under the trial limit of 10 calls per minute; the sequential retry completed after adding a 6.2-second minimum interval.
- **What failed and likely cause:** The request rate exceeded the Cohere trial limit on the first attempt.
- **Practical fix or limitation:** Pace requests by at least 6.2 seconds and retry the run sequentially after a 429.
