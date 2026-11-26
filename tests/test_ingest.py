import json
import logging
from pathlib import Path

import pymupdf

from nse_rag.ingest import (
    discover_pdfs,
    extract_pdf_nodes,
    iter_pdf_nodes,
    load_metadata_for_pdfs,
)


def write_pdf(path: Path, pages: list[str]) -> Path:
    document = pymupdf.open()
    for text in pages:
        page = document.new_page()
        if text:
            page.insert_text((72, 72), text)
    document.save(path)
    document.close()
    return path


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value), encoding="utf-8")


def test_metadata_loading_excludes_aggregate_matches_path_then_id_and_stem(tmp_path, caplog):
    pdf_dir = tmp_path / "pdfs"
    metadata_dir = tmp_path / "metadata"
    pdf_dir.mkdir()
    metadata_dir.mkdir()
    by_path = write_pdf(pdf_dir / "path-match.pdf", ["page text"])
    by_id = write_pdf(pdf_dir / "id-match.pdf", ["page text"])
    by_stem = write_pdf(pdf_dir / "stem-match.pdf", ["page text"])

    write_json(
        metadata_dir / "path-record.json",
        {"pdf_local_path": str(by_path), "circular_id": "different-id", "title": "Path"},
    )
    write_json(metadata_dir / "id-record.json", {"circular_id": "id-match", "title": "ID"})
    write_json(metadata_dir / "stem-match.json", {"title": "Stem"})
    write_json(
        metadata_dir / "all_circulars_metadata.json",
        {"circular_id": "stem-match", "title": "Aggregate must not match"},
    )

    result = load_metadata_for_pdfs([by_stem, by_id, by_path], metadata_dir)
    assert result.records_loaded == 3
    assert result.by_pdf[by_path]["title"] == "Path"
    assert result.by_pdf[by_id]["title"] == "ID"
    assert result.by_pdf[by_stem]["title"] == "Stem"


def test_metadata_loading_logs_malformed_and_missing_paths_and_uses_stem_fallback(
    tmp_path, caplog
):
    pdf_dir = tmp_path / "pdfs"
    metadata_dir = tmp_path / "metadata"
    pdf_dir.mkdir()
    metadata_dir.mkdir()
    pdf_path = write_pdf(pdf_dir / "fallback.pdf", ["usable text"])
    (metadata_dir / "bad.json").write_text("{", encoding="utf-8")
    write_json(
        metadata_dir / "fallback.json",
        {"pdf_local_path": "/no/longer/present/fallback.pdf", "title": "Fallback"},
    )
    write_json(
        metadata_dir / "orphan.json",
        {"pdf_local_path": "/missing/orphan.pdf", "circular_id": "not-local"},
    )

    with caplog.at_level(logging.WARNING):
        result = load_metadata_for_pdfs([pdf_path], metadata_dir)

    assert result.records_loaded == 2
    assert result.by_pdf[pdf_path]["title"] == "Fallback"
    assert "Skipping malformed metadata" in caplog.text
    assert "Metadata PDF path is missing locally" in caplog.text
    assert "Skipping metadata with no matching local PDF" in caplog.text


def test_pdf_discovery_and_iteration_are_sorted_and_page_metadata_is_real(tmp_path):
    pdf_dir = tmp_path / "pdfs"
    metadata_dir = tmp_path / "metadata"
    pdf_dir.mkdir()
    metadata_dir.mkdir()
    second = write_pdf(
        pdf_dir / "b.pdf", ["", "text on actual page two", "second page text"]
    )
    first = write_pdf(pdf_dir / "a.pdf", ["actual page one"])
    found = discover_pdfs(pdf_dir)
    assert found == [first, second]

    metadata = {
        second: {
            "circular_id": "B-42",
            "title": "Description",
            "date": "2026-01-01",
            "category": "listing",
            "source": "NSE",
            "page": 900,
        }
    }
    result = list(iter_pdf_nodes([second, first], metadata))
    assert [path for path, _ in result] == [first, second]
    second_nodes = result[1][1]
    assert len(second_nodes) == 2
    assert second_nodes[0].metadata == {
        "circular_id": "B-42",
        "title": "Description",
        "date": "2026-01-01",
        "category": "listing",
        "source": "NSE",
        "pdf_path": str(second),
        "page_number": 2,
    }
    assert second_nodes[1].metadata["page_number"] == 3
    assert "page" not in second_nodes[0].metadata
    assert "Circular ID: B-42 | Title: Description" in second_nodes[0].text


def test_missing_identity_uses_pdf_stem_and_unreadable_or_textless_are_logged(tmp_path, caplog):
    unreadable = tmp_path / "unreadable.pdf"
    unreadable.write_text("not a PDF", encoding="utf-8")
    textless = tmp_path / "textless.pdf"
    write_pdf(textless, [""])

    with caplog.at_level(logging.WARNING):
        assert extract_pdf_nodes(unreadable) == []
        assert extract_pdf_nodes(textless) == []

    assert "Skipping unreadable PDF" in caplog.text
    assert "PDF produced no usable text" in caplog.text

    titled = write_pdf(tmp_path / "fallback-id.pdf", ["Some extracted text"])
    nodes = extract_pdf_nodes(titled)
    assert nodes[0].metadata["circular_id"] == "fallback-id"
    assert "Circular ID: fallback-id" in nodes[0].text
