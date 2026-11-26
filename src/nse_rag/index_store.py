"""Local Chroma persistence and same-run BM25 query state."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import chromadb
from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.core.base.embeddings.base import BaseEmbedding
from llama_index.core.schema import TextNode
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.retrievers.bm25 import BM25Retriever
from llama_index.vector_stores.chroma import ChromaVectorStore

from nse_rag.ingest import discover_pdfs, iter_pdf_nodes, load_metadata_for_pdfs

LOGGER = logging.getLogger(__name__)
DEFAULT_PDF_DIR = Path("data/pdfs")
DEFAULT_METADATA_DIR = Path("data/metadata")
DEFAULT_INDEX_DIR = Path("data/index")
DEFAULT_COLLECTION_NAME = "nse_circulars_poc"
NODE_CORPUS_FILENAME = "nodes.jsonl"
DEFAULT_BATCH_SIZE = 128
EMBEDDING_MODEL = "text-embedding-3-small"
ID_READ_BATCH_SIZE = 1000


@dataclass(frozen=True)
class IngestionSummary:
    pdfs_found: int
    metadata_records_loaded: int
    documents_indexed: int
    documents_skipped: int
    nodes_indexed: int


@dataclass(frozen=True)
class LocalIndexes:
    dense_index: VectorStoreIndex
    bm25_retriever: BM25Retriever | None
    node_count: int


@dataclass(frozen=True)
class IndexBuildResult:
    summary: IngestionSummary
    indexes: LocalIndexes


def _read_node_corpus(path: Path) -> list[TextNode]:
    if not path.exists():
        raise FileNotFoundError(f"Local BM25 node corpus is missing: {path}")
    with path.open(encoding="utf-8") as node_file:
        return [TextNode.model_validate_json(line) for line in node_file if line.strip()]


def _write_node_batch(node_file, nodes: list[TextNode]) -> None:
    for node in nodes:
        node_file.write(node.model_dump_json() + "\n")


def _embedding_model(model: BaseEmbedding | None) -> BaseEmbedding:
    return model or OpenAIEmbedding(model=EMBEDDING_MODEL)


def open_local_indexes(
    persist_dir: Path = DEFAULT_INDEX_DIR,
    *,
    collection_name: str = DEFAULT_COLLECTION_NAME,
    embedding_model: BaseEmbedding | None = None,
) -> LocalIndexes:
    """Reopen Chroma and reconstruct BM25 from the exact persisted node corpus."""
    persist_dir = Path(persist_dir)
    client = chromadb.PersistentClient(path=str(persist_dir))
    try:
        collection = client.get_collection(collection_name)
    except chromadb.errors.NotFoundError as error:
        raise FileNotFoundError(
            f"Chroma collection {collection_name!r} is missing in {persist_dir}"
        ) from error

    vector_store = ChromaVectorStore(chroma_collection=collection)
    nodes = _read_node_corpus(persist_dir / NODE_CORPUS_FILENAME)
    chroma_ids: set[str] = set()
    collection_count = collection.count()
    for offset in range(0, collection_count, ID_READ_BATCH_SIZE):
        ids_page = collection.get(
            limit=ID_READ_BATCH_SIZE,
            offset=offset,
            include=[],
        )["ids"]
        chroma_ids.update(ids_page)
    node_ids = {node.node_id for node in nodes}
    if len(nodes) != collection_count or node_ids != chroma_ids:
        raise ValueError(
            "Local BM25 node corpus and Chroma collection do not contain the same nodes "
            f"(nodes={len(nodes)}, Chroma={collection_count})"
        )

    dense_index = VectorStoreIndex.from_vector_store(
        vector_store,
        embed_model=_embedding_model(embedding_model),
    )
    bm25_retriever = BM25Retriever.from_defaults(nodes=nodes) if nodes else None
    return LocalIndexes(dense_index, bm25_retriever, len(nodes))


def build_local_indexes(
    pdf_dir: Path = DEFAULT_PDF_DIR,
    metadata_dir: Path = DEFAULT_METADATA_DIR,
    persist_dir: Path = DEFAULT_INDEX_DIR,
    *,
    batch_size: int = DEFAULT_BATCH_SIZE,
    collection_name: str = DEFAULT_COLLECTION_NAME,
    embedding_model: BaseEmbedding | None = None,
    logger: logging.Logger = LOGGER,
) -> IndexBuildResult:
    """Build a clean local Chroma collection and matching BM25 query state.

    PDF extraction is streamed one document at a time and dense writes are
    bounded to ``batch_size`` nodes. The node corpus persisted alongside Chroma
    is the source used to reconstruct BM25 when the index is reopened.
    """
    if batch_size < 1:
        raise ValueError("batch_size must be at least 1")

    pdf_paths = discover_pdfs(Path(pdf_dir))
    metadata_result = load_metadata_for_pdfs(pdf_paths, Path(metadata_dir), logger=logger)
    persist_dir = Path(persist_dir)
    persist_dir.mkdir(parents=True, exist_ok=True)

    client = chromadb.PersistentClient(path=str(persist_dir))
    if collection_name in {collection.name for collection in client.list_collections()}:
        client.delete_collection(collection_name)
    collection = client.create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},
    )
    vector_store = ChromaVectorStore(chroma_collection=collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    model = _embedding_model(embedding_model)
    dense_index = VectorStoreIndex(
        [],
        storage_context=storage_context,
        embed_model=model,
    )

    pending_nodes: list[TextNode] = []
    documents_indexed = 0
    documents_skipped = 0
    nodes_indexed = 0
    corpus_path = persist_dir / NODE_CORPUS_FILENAME

    def flush(node_file) -> None:
        nonlocal nodes_indexed
        if not pending_nodes:
            return
        dense_index.insert_nodes(pending_nodes)
        _write_node_batch(node_file, pending_nodes)
        nodes_indexed += len(pending_nodes)
        pending_nodes.clear()

    with corpus_path.open("w", encoding="utf-8") as node_file:
        for pdf_path, nodes in iter_pdf_nodes(
            pdf_paths,
            metadata_result.by_pdf,
            logger=logger,
        ):
            if not nodes:
                documents_skipped += 1
                continue
            documents_indexed += 1
            for node in nodes:
                pending_nodes.append(node)
                if len(pending_nodes) == batch_size:
                    flush(node_file)
        flush(node_file)

    summary = IngestionSummary(
        pdfs_found=len(pdf_paths),
        metadata_records_loaded=metadata_result.records_loaded,
        documents_indexed=documents_indexed,
        documents_skipped=documents_skipped,
        nodes_indexed=nodes_indexed,
    )
    logger.info(
        "Ingestion summary: PDFs found=%d metadata records loaded=%d documents indexed=%d "
        "documents skipped=%d nodes indexed=%d",
        summary.pdfs_found,
        summary.metadata_records_loaded,
        summary.documents_indexed,
        summary.documents_skipped,
        summary.nodes_indexed,
    )

    indexes = open_local_indexes(
        persist_dir,
        collection_name=collection_name,
        embedding_model=model,
    )
    return IndexBuildResult(summary, indexes)
