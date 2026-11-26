"""Command line interface for full-corpus indexing and grounded queries."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Sequence

from nse_rag.answer import ClaimStatus, answer_from_passages
from nse_rag.index_store import (
    DEFAULT_INDEX_DIR,
    DEFAULT_METADATA_DIR,
    DEFAULT_PDF_DIR,
    build_local_indexes,
    open_local_indexes,
)
from nse_rag.retrieval import RetrievalMode, RetrievalSettings, retrieve

LOGGER = logging.getLogger("nse_rag")


def _add_ingest_parser(subparsers) -> None:
    parser = subparsers.add_parser(
        "ingest",
        help="extract all local PDFs and build fresh local Chroma and BM25 indexes",
    )
    parser.add_argument("--pdf-dir", type=Path, default=DEFAULT_PDF_DIR)
    parser.add_argument("--metadata-dir", type=Path, default=DEFAULT_METADATA_DIR)
    parser.add_argument("--index-dir", type=Path, default=DEFAULT_INDEX_DIR)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.set_defaults(handler=_ingest)


def _add_query_parser(subparsers) -> None:
    parser = subparsers.add_parser("query", help="retrieve passages and answer a question")
    parser.add_argument("question", nargs="+", help="question to answer")
    parser.add_argument(
        "--mode",
        choices=[mode.value for mode in RetrievalMode],
        default=RetrievalMode.DENSE.value,
        help="dense, hybrid (BM25 + dense RRF), or hybrid-rerank (adds one Cohere rerank call)",
    )
    parser.add_argument("--index-dir", type=Path, default=DEFAULT_INDEX_DIR)
    parser.add_argument("--candidate-top-k", type=int, default=20)
    parser.add_argument("--top-k", type=int, default=5)
    parser.set_defaults(handler=_query)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nse-rag",
        description="Build and query a local NSE PDF RAG index.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    _add_ingest_parser(subparsers)
    _add_query_parser(subparsers)
    return parser


def _ingest(args: argparse.Namespace) -> None:
    result = build_local_indexes(
        args.pdf_dir,
        args.metadata_dir,
        args.index_dir,
        batch_size=args.batch_size,
    )
    summary = result.summary
    print(
        "Ingestion complete: "
        f"PDFs found={summary.pdfs_found}, "
        f"metadata records loaded={summary.metadata_records_loaded}, "
        f"documents indexed={summary.documents_indexed}, "
        f"documents skipped={summary.documents_skipped}, "
        f"chunks indexed={summary.nodes_indexed}"
    )
    print(f"Local index: {args.index_dir}")


def _query(args: argparse.Namespace) -> None:
    question = " ".join(args.question).strip()
    settings = RetrievalSettings(
        candidate_top_k=args.candidate_top_k,
        top_k=args.top_k,
    )
    indexes = open_local_indexes(args.index_dir)
    passages = retrieve(question, indexes, mode=args.mode, settings=settings)
    answer = answer_from_passages(question, passages)

    print(f"Question: {question}\n")
    print(answer.answer)
    for reference in answer.references:
        details = []
        if reference.title:
            details.append(f"Title: {reference.title}")
        if reference.date:
            details.append(f"Date: {reference.date}")
        details_text = f" | {' | '.join(details)}" if details else ""
        print(
            f"\n[{reference.source_id}] Circular ID: {reference.circular_id}"
            f"{details_text} | PDF page: {reference.page_number}\n{reference.passage}"
        )
    if answer.claims:
        print(f"\nClaim checks ({answer.validation_note})")
        for claim in answer.claims:
            print(f"\n[{claim.status.value}] {claim.claim}")
            if not claim.references:
                print("  Evidence: no citation could be mapped; review required.")
            for reference in claim.references:
                title = f" | Title: {reference.title}" if reference.title else ""
                date = f" | Date: {reference.date}" if reference.date else ""
                print(
                    f"  Evidence: Circular ID: {reference.circular_id}{title}{date}"
                    f" | PDF page: {reference.page_number}\n  {reference.passage}"
                )
    if answer.insufficient_evidence:
        LOGGER.info("No supported answer found in retrieved passages")


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI. Credentials can be supplied with ``uv run --env-file``."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    args = _build_parser().parse_args(argv)
    args.handler(args)
    return 0
