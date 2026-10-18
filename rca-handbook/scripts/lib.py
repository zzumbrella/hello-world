"""Shared helpers: fetching (plain or browser-rendered), archiving, text extraction."""
import hashlib
import json
import os
import re
import subprocess
import time
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
ARCHIVE = ROOT / "archive"
DATA = ROOT / "data"
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/141.0 Safari/537.36")
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
TODAY = date.today().isoformat()


def archive_path(url, ext):
    u = urlparse(url)
    slug = (u.path.strip("/") or "index").replace("/", "__")
    if u.query:
        slug += "__" + hashlib.md5(u.query.encode()).hexdigest()[:8]
    p = ARCHIVE / u.netloc / f"{slug[:150]}.{ext}"
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def fetch(url, render=False, binary=False, budget=20000, retries=3, force=False):
    """Fetch url and archive it. Returns (bytes_or_text, archive_path)."""
    ext = "html"
    if binary:
        ext = url.rsplit(".", 1)[-1].split("?")[0].lower()[:4] or "bin"
    path = archive_path(url, ext)
    if path.exists() and path.stat().st_size > (200 if binary else 5000) and not force:
        data = path.read_bytes()
        return (data if binary else data.decode("utf-8", "replace")), path
    for attempt in range(retries):
        if render:
            cmd = [CHROME, "--headless=new", "--no-sandbox", "--disable-gpu",
                   "--disable-dev-shm-usage",
                   f"--proxy-server={os.environ['HTTPS_PROXY']}",
                   f"--virtual-time-budget={budget}", "--dump-dom", url]
            r = subprocess.run(cmd, capture_output=True, timeout=180)
            data = r.stdout
        else:
            r = subprocess.run(["curl", "-sS", "-L", "-A", UA, "-m", "90",
                                "-w", "\n%{http_code}", url],
                               capture_output=True, timeout=120)
            body, _, code = r.stdout.rpartition(b"\n")
            data = body if code.strip() == b"200" else b""
        if len(data) > (200 if binary else 5000):
            path.write_bytes(data)
            time.sleep(1.0)
            return (data if binary else data.decode("utf-8", "replace")), path
        time.sleep(3 * (attempt + 1))
    raise RuntimeError(f"fetch failed: {url}")


def page_text(html, main_only=True):
    s = BeautifulSoup(html, "html.parser")
    for x in s(["script", "style", "noscript", "svg"]):
        x.decompose()
    for x in s.select('[id*="onetrust"],[class*="onetrust"]'):
        x.decompose()
    root = (s.find("main") if main_only else None) or s.body or s
    return " ".join(root.get_text(" ", strip=True).split())


def pdf_text(path):
    r = subprocess.run(["pdftotext", "-layout", str(path), "-"],
                       capture_output=True, text=True)
    return r.stdout


def between(text, start, end=None, maxlen=4000):
    i = text.find(start)
    if i < 0:
        return ""
    i += len(start)
    j = text.find(end, i) if end else -1
    return text[i:(j if j > 0 else i + maxlen)].strip()


class Sources:
    """Registry of every source cited in the book (Perplexity-style numbering per chapter)."""

    def __init__(self):
        self.path = DATA / "sources.json"
        self.items = json.loads(self.path.read_text()) if self.path.exists() else {}

    def add(self, sid, url, title, publisher, kind="web", archive=None, accessed=TODAY, note=""):
        self.items[sid] = {
            "url": url, "title": title, "publisher": publisher, "kind": kind,
            "archive": str(archive.relative_to(ROOT)) if archive else None,
            "accessed": accessed, "note": note,
        }

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.items, ensure_ascii=False, indent=1))
