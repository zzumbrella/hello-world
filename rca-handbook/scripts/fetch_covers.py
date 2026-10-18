"""Download book covers for the side-note book cards (Chinese edition first, then Open Library)."""
import json
import re
import subprocess
import sys
import time
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
from lib import DATA, ROOT, TODAY, UA  # noqa: E402

OUT = ROOT / "assets" / "covers"

# key: (douban subject id or None, ISBN of original edition, original title)
BOOKS = {
    "ways-of-seeing": ("26427579", "9780140135152", "Ways of Seeing"),
    "speculative-everything": ("28522614", "9780262019842", "Speculative Everything"),
    "thinking-in-systems": ("11528220", "9781603580557", "Thinking in Systems"),
    "mushroom": ("35059450", "9780691162751", "The Mushroom at the End of the World"),
    "simians": ("26874448", "9780415903875", "Simians, Cyborgs, and Women"),
    "creativity": ("26285299", "9780060928209", "Creativity"),
    "art-practice-research": (None, "9780761929215", "Art Practice as Research"),
    "on-photography": ("4282084", "9780312420093", "On Photography"),
    "camera-lucida": ("6068109", "9780374521349", "Camera Lucida"),
    "spell-sensuous": (None, "9780679776390", "The Spell of the Sensuous"),
    "black-skin": (None, "9780802143006", "Black Skin, White Masks"),
    "technology-china": ("34954806", "9780995455010", "The Question Concerning Technology in China"),
}


def curl(url, dest=None, referer=None):
    cmd = ["curl", "-sS", "-L", "-A", UA, "-m", "60"]
    if referer:
        cmd += ["-H", f"Referer: {referer}"]
    if dest:
        cmd += ["-o", str(dest), "-w", "%{http_code}"]
    cmd.append(url)
    r = subprocess.run(cmd, capture_output=True)
    return r.stdout


def douban_cover(subject, dest):
    html = curl(f"https://book.douban.com/subject/{subject}/").decode("utf-8", "replace")
    m = re.search(r'<a class="nbg"\s+href="([^"]+)"', html) or re.search(r'"image":\s*"([^"]+)"', html)
    title = re.search(r"<title>\s*(.+?)\s*\(豆瓣\)", html)
    if not m:
        return None
    url = m.group(1).replace("/s/public/", "/l/public/")
    code = curl(url, dest, referer="https://book.douban.com/")
    if code.strip() == b"200" and dest.stat().st_size > 3000:
        return {"src": url, "page": f"https://book.douban.com/subject/{subject}/",
                "edition": "zh", "title": title.group(1) if title else ""}
    return None


def openlibrary_cover(isbn, dest):
    url = f"https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg?default=false"
    code = curl(url, dest)
    if code.strip() == b"200" and dest.stat().st_size > 3000:
        return {"src": url, "page": f"https://openlibrary.org/isbn/{isbn}", "edition": "original"}
    return None


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    path = DATA / "covers.json"
    meta = json.loads(path.read_text()) if path.exists() else {}
    for key, (subject, isbn, title) in BOOKS.items():
        raw = OUT / f"{key}.orig.jpg"
        if key in meta and meta[key]["isbn"] == isbn and (meta[key]["edition"] == "zh" or not subject):
            continue
        info = douban_cover(subject, raw) if subject else None
        if subject:
            time.sleep(6)
        info = info or openlibrary_cover(isbn, raw)
        if not info:
            print("MISSING", key)
            continue
        im = Image.open(raw).convert("RGB")
        im.thumbnail((500, 750))
        im.save(OUT / f"{key}.jpg", quality=85)
        meta[key] = {**info, "isbn": isbn, "original_title": title, "accessed": TODAY}
        print("ok", key, info["edition"], im.size)
    (DATA / "covers.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
