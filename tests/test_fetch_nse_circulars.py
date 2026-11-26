import io
import zipfile
from pathlib import Path

import pytest

from fetch_nse_circulars import (
    download_document,
    extract_pdf_bytes,
    find_document_url,
    parse_detail_page,
)


SAMPLES = Path(__file__).resolve().parents[1] / "data" / "samples"
URLS = {
    "mwpl": "https://exchangecirculars.com/circulars/nse/2026/nse-2026-11-23-46d7bdf657e9ea5d-applicable-mwpl-tm-fiifpi-mf-limits-for-introduction-of-two-individual-securitie/",
    "crystal": "https://exchangecirculars.com/circulars/nse/2026/nse-2026-11-25-eed641b52c072723-listing-of-equity-shares-of-crystal-crop-protection-limited-ipo/",
}


def sample_for(prefix):
    return next(SAMPLES.glob(f"{prefix}*.html"))


@pytest.mark.parametrize(
    "prefix,url,circular_id,category,stocks,document",
    [
        ("Applicable MWPL", URLS["mwpl"], "46d7bdf657e9ea5d", "trading", ["ACUTAAS", "APARINDS"], "CMPT77578.pdf"),
        ("Listing of Equity", URLS["crystal"], "eed641b52c072723", "listing", ["CRYSTALCP"], "CML77612.zip"),
    ],
)
def test_sample_page_contains_complete_metadata_and_document_link(prefix, url, circular_id, category, stocks, document):
    html = sample_for(prefix).read_text(encoding="utf-8", errors="replace")
    data, soup = parse_detail_page(html, url)
    assert data["category"] == category
    assert data["circular_id"] == circular_id
    assert data["description"]
    assert data["summary"]
    assert data["key_points"]
    assert data["impact"]
    assert data["severity"]
    assert data["stocks"] == stocks
    assert data["tags"]
    assert data["source"] == "NSE"
    assert data["links"]
    doc_url = find_document_url(soup, url)
    assert doc_url.endswith(document)


def test_pdf_sample_files_are_valid_pdf():
    for path in SAMPLES.glob("*.pdf"):
        assert extract_pdf_bytes(path.read_bytes()).startswith(b"%PDF-")


def test_extract_pdf_from_zip_and_save_as_pdf(tmp_path):
    original = (SAMPLES / "CML77612.pdf").read_bytes()
    archive_buffer = io.BytesIO()
    with zipfile.ZipFile(archive_buffer, "w") as archive:
        archive.writestr("nested/CML77612.pdf", original)
        archive.writestr("../ignored.txt", "safe to ignore")
    assert extract_pdf_bytes(archive_buffer.getvalue()) == original

    class Response:
        content = archive_buffer.getvalue()

        @staticmethod
        def raise_for_status():
            pass

    class Session:
        @staticmethod
        def get(url, timeout, headers):
            assert headers["Accept"] == "*/*"
            assert headers["Referer"] == "https://www.nseindia.com/"
            assert "Chrome/120.0.0.0" in headers["User-Agent"]
            return Response()

    path = Path(download_document(Session(), "https://example.test/CML77612.zip", tmp_path / "CML77612.pdf"))
    assert path.read_bytes() == original
    assert path.suffix == ".pdf"


def test_rejects_non_pdf_non_zip_payload():
    with pytest.raises(ValueError, match="neither a PDF nor a ZIP"):
        extract_pdf_bytes(b"<html>access denied</html>")
