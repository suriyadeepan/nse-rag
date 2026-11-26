from pathlib import Path

import pymupdf
import pytest
from llama_index.core.embeddings import MockEmbedding
from llama_index.core.retrievers.fusion_retriever import FUSION_MODES
from llama_index.core.schema import NodeWithScore, TextNode

import nse_rag.retrieval as retrieval_module
from nse_rag.index_store import build_local_indexes
from nse_rag.retrieval import (
    COHERE_RERANK_MODEL,
    RetrievalMode,
    RetrievalSettings,
    build_hybrid_retriever,
    retrieve,
)


def write_pdf(path: Path, text: str) -> None:
    document = pymupdf.open()
    page = document.new_page()
    page.insert_text((72, 72), text)
    document.save(path)
    document.close()


def make_indexes(tmp_path):
    pdf_dir = tmp_path / "pdfs"
    metadata_dir = tmp_path / "metadata"
    pdf_dir.mkdir()
    metadata_dir.mkdir()
    for number in range(1, 6):
        write_pdf(
            pdf_dir / f"circular-{number}.pdf",
            f"market circular {number} compliance rules and trading details",
        )
    return build_local_indexes(
        pdf_dir,
        metadata_dir,
        tmp_path / "index",
        embedding_model=MockEmbedding(embed_dim=8),
    ).indexes


def test_dense_and_hybrid_modes_use_local_indexes_and_shared_limits(tmp_path, monkeypatch):
    indexes = make_indexes(tmp_path)
    settings = RetrievalSettings(candidate_top_k=4, top_k=2)
    monkeypatch.setattr(
        retrieval_module,
        "_create_cohere_reranker",
        lambda top_n: (_ for _ in ()).throw(AssertionError("Cohere should not run")),
    )

    dense = retrieve("market compliance", indexes, mode=RetrievalMode.DENSE, settings=settings)
    hybrid = retrieve("market compliance", indexes, mode=RetrievalMode.HYBRID, settings=settings)

    assert len(dense) == 2
    assert len(hybrid) == 2
    assert indexes.bm25_retriever.similarity_top_k == 4
    fusion = build_hybrid_retriever(indexes, candidate_top_k=4)
    assert fusion.mode == FUSION_MODES.RECIPROCAL_RANK
    assert fusion.similarity_top_k == 4
    assert fusion.num_queries == 1
    assert fusion.use_async is False


def test_rrf_promotes_a_node_ranked_by_both_retrievers():
    common = TextNode(text="common result")
    dense_only = TextNode(text="dense only")
    bm25_only = TextNode(text="BM25 only")
    fusion = retrieval_module.QueryFusionRetriever(
        retrievers=[None, None],
        mode=FUSION_MODES.RECIPROCAL_RANK,
        similarity_top_k=3,
        num_queries=1,
        use_async=False,
    )

    fused = fusion._reciprocal_rerank_fusion(
        {
            ("query", 0): [
                NodeWithScore(node=dense_only, score=1.0),
                NodeWithScore(node=common, score=0.5),
            ],
            ("query", 1): [
                NodeWithScore(node=bm25_only, score=1.0),
                NodeWithScore(node=common, score=0.5),
            ],
        }
    )

    assert fused[0].node.node_id == common.node_id
    assert fused[0].score == 2 / 61


def test_reranked_mode_sends_only_hybrid_candidates_to_v5_fast(tmp_path, monkeypatch):
    indexes = make_indexes(tmp_path)
    settings = RetrievalSettings(candidate_top_k=4, top_k=2)
    calls = {}

    class FakeReranker:
        def postprocess_nodes(self, nodes, *, query_bundle):
            calls["candidate_count"] = len(nodes)
            calls["query"] = query_bundle.query_str
            calls["candidate_ids"] = [item.node.node_id for item in nodes]
            return list(reversed(nodes))

    def fake_constructor(*, model, top_n):
        calls["model"] = model
        calls["top_n"] = top_n
        return FakeReranker()

    monkeypatch.setattr(retrieval_module, "CohereRerank", fake_constructor)
    results = retrieve(
        "market compliance",
        indexes,
        mode=RetrievalMode.HYBRID_RERANK,
        settings=settings,
    )

    assert calls["model"] == COHERE_RERANK_MODEL == "rerank-v5.0-fast"
    assert calls["top_n"] == 2
    assert calls["candidate_count"] == 4
    assert calls["query"] == "market compliance"
    assert len(set(calls["candidate_ids"])) == 4
    assert len(results) == 2


def test_hybrid_modes_require_bm25_and_settings_validate_shared_top_k(tmp_path):
    indexes = make_indexes(tmp_path)
    from dataclasses import replace

    no_bm25 = replace(indexes, bm25_retriever=None)
    with pytest.raises(ValueError, match="BM25"):
        retrieve("query", no_bm25, mode=RetrievalMode.HYBRID)

    with pytest.raises(ValueError, match="candidate_top_k"):
        RetrievalSettings(candidate_top_k=3, top_k=4)
