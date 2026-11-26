"""Dense, reciprocal-rank-fused, and Cohere-reranked retrieval modes."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol

from llama_index.core.base.base_retriever import BaseRetriever
from llama_index.core.postprocessor.types import BaseNodePostprocessor
from llama_index.core.retrievers import QueryFusionRetriever
from llama_index.core.retrievers.fusion_retriever import FUSION_MODES
from llama_index.core.schema import NodeWithScore, QueryBundle
from llama_index.postprocessor.cohere_rerank import CohereRerank

from nse_rag.index_store import LocalIndexes

COHERE_RERANK_MODEL = "rerank-v5.0-fast"


class RetrievalMode(StrEnum):
    DENSE = "dense"
    HYBRID = "hybrid"
    HYBRID_RERANK = "hybrid-rerank"


@dataclass(frozen=True)
class RetrievalSettings:
    """Shared candidate and result limits for fair mode comparisons."""

    candidate_top_k: int = 20
    top_k: int = 5

    def __post_init__(self) -> None:
        if self.top_k < 1:
            raise ValueError("top_k must be at least 1")
        if self.candidate_top_k < self.top_k:
            raise ValueError("candidate_top_k must be greater than or equal to top_k")


class Reranker(Protocol):
    def postprocess_nodes(
        self,
        nodes: list[NodeWithScore],
        *,
        query_bundle: QueryBundle,
    ) -> list[NodeWithScore]: ...


def build_hybrid_retriever(
    indexes: LocalIndexes,
    *,
    candidate_top_k: int,
) -> QueryFusionRetriever:
    """Combine local BM25 and Chroma retrievers with LlamaIndex RRF."""
    if indexes.bm25_retriever is None:
        raise ValueError("Hybrid retrieval requires a non-empty BM25 node corpus")
    dense_retriever = indexes.dense_index.as_retriever(
        similarity_top_k=candidate_top_k
    )
    indexes.bm25_retriever.similarity_top_k = candidate_top_k
    return QueryFusionRetriever(
        retrievers=[dense_retriever, indexes.bm25_retriever],
        mode=FUSION_MODES.RECIPROCAL_RANK,
        similarity_top_k=candidate_top_k,
        num_queries=1,
        use_async=False,
    )


def _create_cohere_reranker(top_n: int) -> CohereRerank:
    """Create Cohere's v5 Fast reranker; the SDK reads COHERE_API_KEY."""
    return CohereRerank(model=COHERE_RERANK_MODEL, top_n=top_n)


def retrieve(
    query: str,
    indexes: LocalIndexes,
    *,
    mode: RetrievalMode | str = RetrievalMode.DENSE,
    settings: RetrievalSettings = RetrievalSettings(),
    reranker: Reranker | BaseNodePostprocessor | None = None,
) -> list[NodeWithScore]:
    """Retrieve passages from the persisted local corpus in a selected mode.

    Only the reranked mode sends candidate passage text to Cohere. Dense and
    BM25 retrieval stay local; all modes use the same candidate and final top-k
    settings and the same Chroma/BM25 corpus pair.
    """
    if not query.strip():
        raise ValueError("query must not be empty")
    selected_mode = RetrievalMode(mode)
    if selected_mode == RetrievalMode.DENSE:
        dense_retriever = indexes.dense_index.as_retriever(
            similarity_top_k=settings.candidate_top_k
        )
        return dense_retriever.retrieve(query)[: settings.top_k]

    hybrid_retriever = build_hybrid_retriever(
        indexes,
        candidate_top_k=settings.candidate_top_k,
    )
    candidates = hybrid_retriever.retrieve(query)
    if selected_mode == RetrievalMode.HYBRID:
        return candidates[: settings.top_k]

    reranker = reranker or _create_cohere_reranker(settings.top_k)
    reranked_nodes = reranker.postprocess_nodes(
        candidates,
        query_bundle=QueryBundle(query_str=query),
    )
    return reranked_nodes[: settings.top_k]
