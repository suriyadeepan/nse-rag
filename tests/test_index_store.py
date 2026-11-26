import json
from pathlib import Path

import chromadb
import pymupdf
from llama_index.core import VectorStoreIndex
from llama_index.core.embeddings import MockEmbedding

from nse_rag.index_store import (
    DEFAULT_COLLECTION_NAME,
    build_local_indexes,
    open_local_indexes,
)


def write_pdf(path: Path, pages: list[str]) -> Path:
    document = pymupdf.open()
    for text in pages:
        page = document.new_page()
        page.insert_text((72, 72), text)
    document.save(path)
    document.close()
    return path


def write_metadata(directory: Path, name: str, record: dict) -> None:
    (directory / name).write_text(json.dumps(record), encoding="utf-8")


def get_chroma_ids(persist_dir: Path) -> set[str]:
    client = chromadb.PersistentClient(path=str(persist_dir))
    return set(client.get_collection(DEFAULT_COLLECTION_NAME).get()["ids"])


def get_bm25_ids(retriever) -> set[str]:
    return {record["node_id"] for record in retriever.corpus}


def test_build_batches_and_reopen_reconstructs_matching_dense_and_bm25(tmp_path, monkeypatch):
    pdf_dir = tmp_path / "pdfs"
    metadata_dir = tmp_path / "metadata"
    index_dir = tmp_path / "index"
    pdf_dir.mkdir()
    metadata_dir.mkdir()
    pdf_path = write_pdf(
        pdf_dir / "circular-123.pdf",
        ["alpha market rule passage", "beta market rule passage", "gamma market rule passage"],
    )
    write_metadata(
        metadata_dir,
        "circular-123.json",
        {"pdf_local_path": str(pdf_path), "circular_id": "C-123", "title": "Rules"},
    )

    inserted_batch_sizes = []
    original_insert = VectorStoreIndex.insert_nodes

    def track_insert(self, nodes, **kwargs):
        inserted_batch_sizes.append(len(nodes))
        return original_insert(self, nodes, **kwargs)

    monkeypatch.setattr(VectorStoreIndex, "insert_nodes", track_insert)
    model = MockEmbedding(embed_dim=8)
    result = build_local_indexes(
        pdf_dir,
        metadata_dir,
        index_dir,
        batch_size=2,
        embedding_model=model,
    )

    assert inserted_batch_sizes == [2, 1]
    assert result.summary.pdfs_found == 1
    assert result.summary.metadata_records_loaded == 1
    assert result.summary.documents_indexed == 1
    assert result.summary.documents_skipped == 0
    assert result.summary.nodes_indexed == 3
    expected_ids = get_chroma_ids(index_dir)
    assert len(expected_ids) == 3
    assert get_bm25_ids(result.indexes.bm25_retriever) == expected_ids

    reopened = open_local_indexes(index_dir, embedding_model=model)
    assert reopened.node_count == 3
    assert get_bm25_ids(reopened.bm25_retriever) == expected_ids
    assert reopened.dense_index.as_retriever().similarity_top_k == 2


def test_fresh_build_replaces_collection_and_logs_skipped_pdf(tmp_path, caplog):
    pdf_dir = tmp_path / "pdfs"
    metadata_dir = tmp_path / "metadata"
    index_dir = tmp_path / "index"
    pdf_dir.mkdir()
    metadata_dir.mkdir()
    write_pdf(pdf_dir / "first.pdf", ["first run content"])
    write_metadata(metadata_dir, "first.json", {"circular_id": "first"})
    model = MockEmbedding(embed_dim=8)
    first = build_local_indexes(pdf_dir, metadata_dir, index_dir, embedding_model=model)
    first_ids = get_chroma_ids(index_dir)

    (pdf_dir / "first.pdf").unlink()
    (metadata_dir / "first.json").unlink()
    write_pdf(pdf_dir / "second.pdf", [""])
    with caplog.at_level("WARNING"):
        second = build_local_indexes(
            pdf_dir,
            metadata_dir,
            index_dir,
            embedding_model=model,
        )

    assert first.summary.nodes_indexed == 1
    assert first_ids
    assert second.summary.pdfs_found == 1
    assert second.summary.documents_indexed == 0
    assert second.summary.documents_skipped == 1
    assert second.summary.nodes_indexed == 0
    assert get_chroma_ids(index_dir) == set()
    assert second.indexes.bm25_retriever is None
    assert "PDF produced no usable text" in caplog.text
