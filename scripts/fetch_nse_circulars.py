"""Fetch NSE circular pages, their metadata, and attached PDF documents."""

import argparse
import json
import os
import random
import re
import time
import zipfile
from io import BytesIO
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from rich.console import Console
from rich.panel import Panel
from tqdm import tqdm

BASE_URL = "https://exchangecirculars.com"
INDEX_URL = f"{BASE_URL}/circulars/nse/"
DOWNLOAD_INTERVAL_SECONDS = 2.0


class DownloadRateLimiter:
    """Space document download requests by a minimum interval."""

    def __init__(self, interval=DOWNLOAD_INTERVAL_SECONDS):
        self.interval = interval
        self.last_started = None

    def wait(self):
        now = time.monotonic()
        if self.last_started is not None:
            remaining = self.interval - (now - self.last_started)
            if remaining > 0:
                time.sleep(remaining)
        self.last_started = time.monotonic()


_download_rate_limiter = DownloadRateLimiter()


def create_session():
    session = requests.Session()
    retry = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset(("GET",)),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.headers.update({"User-Agent": "Mozilla/5.0 (compatible; NSECircularFetcher/1.0)"})
    return session


def _label_key(value):
    return re.sub(r"[^a-z0-9]+", " ", value.casefold()).strip()


def _field_value(soup, label):
    """Get text following a section heading, tolerating h2-h4 and nested markup."""
    heading = next(
        (h for h in soup.find_all(["h1", "h2", "h3", "h4", "h5"])
         if _label_key(h.get_text(" ", strip=True)) == _label_key(label)),
        None,
    )
    if heading:
        for sibling in heading.find_next_siblings():
            if sibling.name and re.fullmatch(r"h[1-5]", sibling.name):
                break
            if sibling.name in ("p", "ul", "ol", "div"):
                text = sibling.get_text(" ", strip=True)
                if text:
                    return text
    return None


def _metadata_rows(soup):
    values = {}
    for row in soup.select("table tr"):
        cells = row.find_all(["th", "td"], recursive=False)
        if len(cells) < 2:
            cells = row.find_all(["th", "td"])
        if len(cells) >= 2:
            key = _label_key(cells[0].get_text(" ", strip=True))
            if key:
                values[key] = cells[1]
    return values


def parse_detail_page(html, circular_url):
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.get_text(" ", strip=True).split(" | ")[0] if soup.title else None
    data = {
        "title": title,
        "link": circular_url,
        "category": None,
        "circular_id": None,
        "description": _field_value(soup, "Description"),
        "summary": _field_value(soup, "Summary"),
        "key_points": [],
        "impact": None,
        "severity": None,
        "stocks": [],
        "tags": [],
        "source": None,
        "links": [],
        "pdf_local_path": None,
    }

    point_heading = next(
        (h for h in soup.find_all(["h1", "h2", "h3", "h4", "h5"])
         if _label_key(h.get_text(" ", strip=True)) == "key points"),
        None,
    )
    if point_heading:
        for sibling in point_heading.find_next_siblings():
            if sibling.name and re.fullmatch(r"h[1-5]", sibling.name):
                break
            if sibling.name in ("ul", "ol"):
                data["key_points"] = [li.get_text(" ", strip=True) for li in sibling.find_all("li")]
                break

    rows = _metadata_rows(soup)
    for field in ("category", "circular id", "impact", "severity", "stocks", "tags", "source"):
        cell = rows.get(field)
        if cell is None:
            continue
        if field in ("stocks", "tags"):
            data[field.replace(" ", "_")] = [
                a.get_text(" ", strip=True) for a in cell.find_all("a") if a.get_text(strip=True)
            ] or [x.strip() for x in cell.get_text(" ", strip=True).split(",") if x.strip()]
        else:
            key = field.replace(" ", "_")
            data[key] = cell.get_text(" ", strip=True) or None

    for anchor in soup.find_all("a", href=True):
        href = urljoin(circular_url, anchor["href"])
        data["links"].append({"text": anchor.get_text(" ", strip=True), "href": href})
    return data, soup


def find_document_url(soup, page_url):
    candidates = []
    for anchor in soup.find_all("a", href=True):
        href = anchor["href"].strip()
        text = anchor.get_text(" ", strip=True).casefold()
        if ".pdf" in href.casefold() or ".zip" in href.casefold() or "pdf document" in text:
            candidates.append(("pdf" in text, urljoin(page_url, href)))
    if candidates:
        return next((url for preferred, url in candidates if preferred), candidates[0][1])
    for tag in soup.find_all(["iframe", "embed", "object"]):
        src = tag.get("src") or tag.get("data")
        if src:
            return urljoin(page_url, src)
    return None


def _safe_filename(value):
    value = re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("._")
    return value or "nse_circular"


def extract_pdf_bytes(content):
    """Return PDF bytes from a PDF response or a ZIP containing a PDF."""
    if content.startswith(b"%PDF-"):
        return content
    if content.startswith(b"PK\x03\x04"):
        with zipfile.ZipFile(BytesIO(content)) as archive:
            members = [
                info for info in archive.infolist()
                if not info.is_dir() and Path(info.filename).suffix.casefold() == ".pdf"
            ]
            for info in members:
                payload = archive.read(info)
                if payload.startswith(b"%PDF-"):
                    return payload
        raise ValueError("ZIP response contained no valid PDF")
    raise ValueError("Document response is neither a PDF nor a ZIP containing a PDF")


def download_document(session, document_url, destination):
    _download_rate_limiter.wait()
    response = session.get(
        document_url,
        timeout=45,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "*/*",
            "Referer": "https://www.nseindia.com/",
        },
    )
    response.raise_for_status()
    pdf_bytes = extract_pdf_bytes(response.content)
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(pdf_bytes)
    return str(destination)


def fetch_circular(session, circular_url, output_dir="data/pdfs"):
    response = session.get(circular_url, timeout=30)
    response.raise_for_status()
    data, soup = parse_detail_page(response.text, response.url)
    document_url = find_document_url(soup, response.url)
    data["document_url"] = document_url
    identifier = data["circular_id"] or data["title"] or circular_url.rstrip("/").split("/")[-1]
    if document_url:
        filename = _safe_filename(identifier) + ".pdf"
        data["pdf_local_path"] = download_document(session, document_url, Path(output_dir) / filename)
    return data


def fetch_index_page(session, page):
    response = session.get(INDEX_URL, params={"page": page}, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    circulars = []
    rows = soup.select("table tr")
    for row in rows:
        anchors = [
            a for a in row.select('a[href*="/circulars/nse/"]')
            if urljoin(response.url, a["href"]).rstrip("/") != INDEX_URL.rstrip("/")
        ]
        if not anchors:
            continue
        title_anchor = max(anchors, key=lambda a: len(a.get_text(" ", strip=True)))
        title = title_anchor.get_text(" ", strip=True)
        if not title:
            continue
        cells = row.find_all(["td", "th"], recursive=False)
        date = cells[0].get_text(" ", strip=True) if cells else ""
        circulars.append({
            "date": date,
            "title": title,
            "link": urljoin(response.url, title_anchor["href"]),
        })
    if circulars:
        return list({item["link"]: item for item in circulars}.values())

    # Fall back to main content for layouts that stop using a table.
    container = soup.find("main") or soup
    seen = set()
    for anchor in container.select('a[href*="/circulars/nse/"]'):
        href = urljoin(response.url, anchor["href"])
        title = anchor.get_text(" ", strip=True)
        if title and href.rstrip("/") != INDEX_URL.rstrip("/") and href not in seen:
            seen.add(href)
            circulars.append({"date": "", "title": title, "link": href})
    return circulars


def load_completed_circulars(metadata_dir, pdf_dir):
    """Map circular URLs to cached metadata when the associated PDF is valid."""
    completed = {}
    metadata_dir = Path(metadata_dir)
    pdf_dir = Path(pdf_dir)
    for metadata_file in metadata_dir.glob("*.json"):
        try:
            content = json.loads(metadata_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        entries = content if isinstance(content, list) else [content]
        for data in entries:
            if not isinstance(data, dict) or not data.get("link"):
                continue
            pdf_path = Path(data.get("pdf_local_path") or "")
            candidates = [pdf_path]
            if data.get("circular_id"):
                candidates.append(pdf_dir / f"{_safe_filename(data['circular_id'])}.pdf")
            valid_pdf = None
            for candidate in candidates:
                try:
                    with candidate.open("rb") as pdf_file:
                        if pdf_file.read(5) == b"%PDF-":
                            valid_pdf = candidate
                            break
                except OSError:
                    continue
            if valid_pdf:
                cached = dict(data)
                cached["pdf_local_path"] = str(valid_pdf)
                completed[data["link"]] = cached
    return completed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start-page", type=int, default=1)
    parser.add_argument("--end-page", type=int, default=2)
    parser.add_argument("--limit", type=int, help="Stop after this many circulars")
    parser.add_argument("--metadata-dir", default="data/metadata")
    parser.add_argument("--pdf-dir", default="data/pdfs")
    args = parser.parse_args()
    os.makedirs(args.metadata_dir, exist_ok=True)
    os.makedirs(args.pdf_dir, exist_ok=True)
    session = create_session()
    results = []
    completed = load_completed_circulars(args.metadata_dir, args.pdf_dir)
    seen_links = set()
    skipped = 0
    skipped_titles = []
    console = Console()
    console.print(Panel.fit(
        "[bold cyan]NSE Circular Fetcher[/bold cyan]\n"
        f"[dim]PDFs → {args.pdf_dir}  •  Metadata → {args.metadata_dir}[/dim]",
        border_style="bright_magenta",
    ))
    for page in range(args.start_page, args.end_page + 1):
        console.print(f"[bold blue]Fetching index page {page}…[/bold blue]")
        try:
            index_items = fetch_index_page(session, page)
        except requests.RequestException as exc:
            console.print(f"[bold red]Index page {page} failed:[/bold red] {exc}")
            continue
        bar = tqdm(total=len(index_items), desc=f"Page {page}", unit="circular")
        for item in index_items:
            link = item["link"]
            if link in seen_links:
                bar.update(1)
                continue
            seen_links.add(link)
            if link in completed:
                data = dict(completed[link])
                data.update(page=page, date=item["date"], title=data.get("title") or item["title"])
                results.append(data)
                skipped += 1
                skipped_titles.append(item["title"])
                bar.set_postfix_str("cached")
                bar.update(1)
                if args.limit is not None and len(results) >= args.limit:
                    break
                continue
            try:
                data = fetch_circular(session, link, args.pdf_dir)
                data.update(page=page, date=item["date"], title=data["title"] or item["title"])
                results.append(data)
                if data["circular_id"]:
                    target = Path(args.metadata_dir) / f"{_safe_filename(data['circular_id'])}.json"
                    target.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
                if data.get("pdf_local_path"):
                    completed[link] = data
                bar.set_postfix_str("saved")
                time.sleep(random.uniform(0.8, 1.8))
            except (requests.RequestException, ValueError, zipfile.BadZipFile, OSError) as exc:
                bar.set_postfix_str("failed")
                tqdm.write(f"Could not process {link}: {exc}")
            bar.update(1)
            if args.limit is not None and len(results) >= args.limit:
                break
        bar.close()
        if args.limit is not None and len(results) >= args.limit:
            break
    target = Path(args.metadata_dir) / "all_circulars_metadata.json"
    target.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    console.print(Panel.fit(
        f"[bold green]Done![/bold green] {len(results)} circulars in this run\n"
        f"[yellow]Skipped {skipped} already-downloaded circulars[/yellow]"
        + ("\n[dim]Cached: " + "; ".join(skipped_titles) + "[/dim]" if skipped_titles else ""),
        border_style="green",
    ))


if __name__ == "__main__":
    main()
