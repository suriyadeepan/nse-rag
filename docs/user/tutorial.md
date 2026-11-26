**Goal:** Build a working RAG in under an hour that demonstrates why BM25 + vector search + reranking beats vector search alone.

## 1. Setup

Create a project and install dependencies:

```bash
mkdir nse-rag && cd nse-rag
uv init
uv add llama-index llama-index-vector-stores-chroma \
  llama-index-embeddings-openai llama-index-llms-openai \
  llama-index-retrievers-bm25 llama-index-postprocessor-cohere-rerank \
  chromadb pymupdf
```

Add API keys:

```bash
export OPENAI_API_KEY="your-key"
export COHERE_API_KEY="your-key"
```

Download 4–5 real NSE circular PDFs into:

```text
data/
  NSE_CIRCULAR_001.pdf
  NSE_CIRCULAR_002.pdf
  ...
```

Use actual circular identifiers in filenames.

## 2. Implement RAG

Create `rag.py`:

```python
import os
import glob
import fitz
import chromadb

from llama_index.core import (
    Document, Settings, VectorStoreIndex, StorageContext
)
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.retrievers import QueryFusionRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.retrievers.bm25 import BM25Retriever
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.postprocessor.cohere_rerank import CohereRerank

# Models
Settings.llm = OpenAI(model="gpt-4.1-mini")
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")

# Extract PDFs
documents = []
for path in glob.glob("data/*.pdf"):
    with fitz.open(path) as pdf:
        text = "\n".join(page.get_text() for page in pdf)
    circular_id = os.path.splitext(os.path.basename(path))[0]
    documents.append(Document(
        text=f"Circular ID: {circular_id}\n{text}",
        metadata={"circular_id": circular_id}
    ))

# Chunk
nodes = SentenceSplitter(
    chunk_size=500, chunk_overlap=50
).get_nodes_from_documents(documents)

# ChromaDB
db = chromadb.PersistentClient(path="./chroma")
collection = db.get_or_create_collection("nse")
store = ChromaVectorStore(chroma_collection=collection)
index = VectorStoreIndex(
    nodes, storage_context=StorageContext.from_defaults(vector_store=store)
)

# Dense + BM25 + RRF
bm25 = BM25Retriever.from_defaults(nodes=nodes, similarity_top_k=5)
hybrid = QueryFusionRetriever(
    [index.as_retriever(similarity_top_k=5), bm25],
    similarity_top_k=5, num_queries=1,
    mode="reciprocal_rerank", use_async=False
)

# Three configurations
engines = {
    "Dense": RetrieverQueryEngine.from_args(
        index.as_retriever(similarity_top_k=5)
    ),
    "Hybrid": RetrieverQueryEngine.from_args(hybrid),
    "Hybrid + Reranking": RetrieverQueryEngine.from_args(
        hybrid,
        node_postprocessors=[
            CohereRerank(
                api_key=os.environ["COHERE_API_KEY"],
                model="rerank-v5.0-fast",
                top_n=3
            )
        ]
    )
}

# Benchmark
queries = [
    "ACTUAL_CIRCULAR_IDENTIFIER",
    "Explain market-wide circuit breaker rules",
    "What happens when Nifty falls 15%?"
]

for query in queries:
    print(f"\nQUERY: {query}")
    for name, engine in engines.items():
        response = engine.query(query)
        print(f"\n{name}:\n{response}")
        print("Sources:", [
            n.node.metadata.get("circular_id")
            for n in response.source_nodes
        ])
```

## 3. Run

```bash
uv run python rag.py
```

Compare the same queries across all three configurations.

| Configuration | What it tests |
|---|---|
| Dense | Semantic similarity |
| Hybrid | BM25 + dense + RRF |
| Hybrid + Reranking | Better ordering of retrieved chunks |

**Important:** Run ingestion once for this demo. Delete `chroma/` before rebuilding the index to avoid duplicate records.

## 4. Write the blog

Capture the output for these examples:

1. Exact circular identifier — BM25 should help find the exact match.
2. Market-wide circuit breaker rules — dense retrieval should help find semantically related content.
3. Compare both — hybrid retrieval combines their strengths.
4. Add reranking — demonstrate whether the most relevant chunks move to the top.

**Final takeaway:** Vector search finds similar meanings. BM25 finds matching terms. Reranking improves the order of retrieved results. Enterprise RAG often needs all three.

# Evaluation & Production Readiness

## 5. Build an Evaluation Dataset

Create `eval.jsonl` with 20–30 manually labelled queries.

Cover three query types:

| Type | Example |
|---|---|
| Exact ID | Find NSE circular NSE/CML/2025/01 |
| Semantic | Explain market-wide circuit breaker rules |
| Multi-circular | Compare circuit breaker rules across two circulars |

Each record should contain:

```json
{
  "query": "Find circular NSE/CML/2025/01",
  "type": "exact_id",
  "expected_ids": ["NSE_CML_2025_01"],
  "expected_answer": "..."
}
```

Labels:
- `expected_ids`: manually verified relevant circulars.
- `expected_answer`: manually written reference answer.
- Have a second reviewer verify the labels if possible.

## 6. Measure Retrieval Quality

Compare three configurations:

1. Dense retrieval.
2. BM25 + Dense + RRF.
3. BM25 + Dense + RRF + Reranking.

Calculate:

| Metric | Meaning |
|---|---|
| Recall@5 | Were relevant circulars found in top 5? |
| MRR | How highly was the first relevant result ranked? |
| Faithfulness | Are answer claims supported by retrieved evidence? |

For each query:

```python
def recall_at_k(results, expected, k=5):
    found = {r.circular_id for r in results[:k]}
    return len(found & set(expected)) / len(expected)

def reciprocal_rank(results, expected):
    for rank, result in enumerate(results, 1):
        if result.circular_id in expected:
            return 1 / rank
    return 0
```

Report macro-averages across queries.

For faithfulness, manually review answers against source passages, or use an LLM judge with the retrieved context. Report the percentage of answers whose factual claims are fully supported.

## 7. Measure Latency and Cost

Run each configuration at least 30 times per query, with warm-up runs excluded.

Record:
- Retrieval latency.
- Reranking latency.
- Generation latency.
- Total end-to-end latency.

Report p95 latency.

Cost per query:

```text
Embedding cost = query tokens × embedding price
Reranking cost = reranked documents × rerank price
LLM cost = input tokens × input price
         + output tokens × output price

Total = embedding + reranking + LLM
```

Report ingestion/embedding cost separately and amortize it across the expected query volume.

## 8. Failure Analysis

Create `failure-analysis.md`.

Investigate:
- Exact circular ID not retrieved.
- Tables or structured PDF content extracted incorrectly.
- Superseded circular returned instead of current circular.
- Ambiguous references (e.g. "circuit breaker rules").
- Multi-circular queries missing one relevant document.
- Correct document retrieved, but incorrect answer generated.

Record query, failure, root cause and proposed fix.

## 9. Production Signals

Demonstrate three small improvements.

**A. Incremental ingestion**

Do not rebuild the entire database whenever a circular arrives.

- Assign each circular a stable ID.
- Calculate a document content hash.
- Skip unchanged documents.
- Delete old chunks for changed circulars.
- Insert updated chunks using stable chunk IDs.

Example:

```python
collection.delete(where={"circular_id": circular_id})
index.insert_nodes(updated_nodes)
```

**B. Metadata filtering**

Store metadata with every chunk:

```python
{
    "circular_id": "NSE_CML_2025_01",
    "date": "2025-01-10",
    "department": "Capital Market"
}
```

Support filtering by date and department before retrieval.

**C. Citation validation**

Every generated answer should cite:
- Circular ID.
- Page number.
- Supporting passage.

Reject citations that reference missing circulars or invalid page numbers. Check that cited passages actually support the associated claims.

## 10. Publish Results

Create a final benchmark table:

| Metric | Dense | Hybrid | Hybrid + Rerank |
|---|---:|---:|---:|
| Recall@5 | TBD | TBD | TBD |
| MRR | TBD | TBD | TBD |
| Faithfulness | TBD | TBD | TBD |
| p95 latency (ms) | TBD | TBD | TBD |
| Cost/query ($) | TBD | TBD | TBD |

Also publish:
- Number of documents and queries.
- Query distribution by type.
- Labelling methodology.
- Three representative failures.
- One example of incremental ingestion.
- One example of metadata-filtered retrieval.
