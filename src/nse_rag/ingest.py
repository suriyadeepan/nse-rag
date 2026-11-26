"""Small, deterministic PDF and metadata intake for the local RAG corpus."""

from __future__ import annotations

import json
import logging
from collections.abc import Iterable, Iterator, Mapping
from dataclasses import dataclass
from pathlib import Path

import pymupdf
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import TextNode

LOGGER = logging.getLogger(__name__)
AGGREGATE_METADATA = "all_circulars_metadata.json"
NODE_METADATA_FIELDS = (
    "circular_id",
    "title",
    "date",
    "category",
    "source",
    "pdf_path",
    "page_number",
)


@dataclass(frozen=True)
class MetadataMatchResult:
    """Metadata matched to local PDFs, plus the number of valid records read."""

    by_pdf: dict[Path, dict[str, object]]
    records_loaded: int


def discover_pdfs(pdf_dir: Path) -> list[Path]:
    """Return local PDF files in reproducible path order."""
    return sorted(Path(pdf_dir).glob("*.pdf"))


def _path_key(value: str | Path) -> str:
    return str(Path(value).expanduser().resolve())


def _identity_key(value: object) -> str | None:
    if value is None:
        return None
    normalized = str(value).strip()
    return normalized.casefold() if normalized else None


def load_metadata_for_pdfs(
    pdf_paths: Iterable[Path],
    metadata_dir: Path,
    *,
    logger: logging.Logger = LOGGER,
) -> MetadataMatchResult:
    """Read one-object metadata JSON files and match them to local PDF paths.

    Exact ``pdf_local_path`` matches take precedence. If the stored path is no
    longer present, circular ID and metadata filename stem are used as simple
    fallbacks. The aggregate metadata file is intentionally ignored.
    """
    ordered_pdfs = sorted((Path(path) for path in pdf_paths), key=lambda path: str(path))
    by_resolved_path = {_path_key(path): path for path in ordered_pdfs}

    path_records: dict[str, dict[str, object]] = {}
    id_records: dict[str, dict[str, object]] = {}
    stem_records: dict[str, dict[str, object]] = {}
    records: list[tuple[Path, dict[str, object]]] = []
    records_loaded = 0
    metadata_paths = sorted(
        path
        for path in Path(metadata_dir).glob("*.json")
        if path.name != AGGREGATE_METADATA
    )

    for metadata_path in metadata_paths:
        try:
            with metadata_path.open(encoding="utf-8") as metadata_file:
                record = json.load(metadata_file)
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            logger.warning("Skipping malformed metadata %s: %s", metadata_path, error)
            continue
        if not isinstance(record, dict):
            logger.warning("Skipping metadata that is not a JSON object: %s", metadata_path)
            continue

        records_loaded += 1
        records.append((metadata_path, record))
        local_path = record.get("pdf_local_path")
        if isinstance(local_path, str) and local_path.strip():
            path_key = _path_key(local_path)
            if path_key in by_resolved_path:
                path_records.setdefault(path_key, record)
            else:
                logger.warning(
                    "Metadata PDF path is missing locally; trying ID/stem fallback: %s (%s)",
                    metadata_path,
                    local_path,
                )

        circular_id = _identity_key(record.get("circular_id"))
        if circular_id:
            id_records.setdefault(circular_id, record)
        stem_records.setdefault(metadata_path.stem.casefold(), record)

    matched_records: dict[Path, dict[str, object]] = {}
    for pdf_path in ordered_pdfs:
        record = path_records.get(_path_key(pdf_path))
        if record is None:
            record = id_records.get(pdf_path.stem.casefold())
        if record is None:
            record = stem_records.get(pdf_path.stem.casefold())
        if record is not None:
            matched_records[pdf_path] = record

    matched_record_ids = {id(record) for record in matched_records.values()}
    for metadata_path, record in records:
        if id(record) not in matched_record_ids:
            logger.warning("Skipping metadata with no matching local PDF: %s", metadata_path)

    return MetadataMatchResult(matched_records, records_loaded)


def extract_pdf_nodes(
    pdf_path: Path,
    metadata: Mapping[str, object] | None = None,
    *,
    splitter: SentenceSplitter | None = None,
    logger: logging.Logger = LOGGER,
) -> list[TextNode]:
    """Extract and chunk non-empty PDF pages, retaining actual 1-based pages."""
    pdf_path = Path(pdf_path)
    splitter = splitter or SentenceSplitter(chunk_size=500, chunk_overlap=50)
    record = metadata or {}
    circular_id = str(record.get("circular_id") or pdf_path.stem)
    title = record.get("title")
    identity = f"Circular ID: {circular_id}"
    if isinstance(title, str) and title.strip():
        identity += f" | Title: {title.strip()}"

    nodes: list[TextNode] = []
    try:
        document = pymupdf.open(pdf_path)
    except (OSError, ValueError, RuntimeError) as error:
        logger.warning("Skipping unreadable PDF %s: %s", pdf_path, error)
        return nodes

    try:
        for page_index, page in enumerate(document, start=1):
            page_text = page.get_text("text").strip()
            if not page_text:
                continue
            text = f"{identity}\n\n{page_text}"
            page_metadata = {
                key: record[key]
                for key in NODE_METADATA_FIELDS
                if key in record and record[key] is not None
            }
            page_metadata.update(
                circular_id=circular_id,
                pdf_path=str(pdf_path),
                page_number=page_index,
            )
            if isinstance(title, str) and title.strip():
                page_metadata["title"] = title

            for chunk in splitter.split_text(text):
                nodes.append(TextNode(text=chunk, metadata=page_metadata.copy()))
    except (OSError, ValueError, RuntimeError) as error:
        logger.warning("PDF text extraction failed for %s: %s", pdf_path, error)
        return []
    finally:
        document.close()

    if not nodes:
        logger.warning("PDF produced no usable text: %s", pdf_path)
    return nodes


def iter_pdf_nodes(
    pdf_paths: Iterable[Path],
    metadata_by_pdf: Mapping[Path, Mapping[str, object]],
    *,
    splitter: SentenceSplitter | None = None,
    logger: logging.Logger = LOGGER,
) -> Iterator[tuple[Path, list[TextNode]]]:
    """Yield one PDF's nodes at a time to keep extraction memory bounded."""
    ordered_paths = sorted((Path(path) for path in pdf_paths), key=lambda path: str(path))
    for pdf_path in ordered_paths:
        yield pdf_path, extract_pdf_nodes(
            pdf_path,
            metadata_by_pdf.get(pdf_path),
            splitter=splitter,
            logger=logger,
        )
