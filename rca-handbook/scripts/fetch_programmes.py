"""Archive every RCA programme page and extract the facts the book uses."""
import json
import re
import sys

from bs4 import BeautifulSoup

sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from lib import DATA, Sources, between, fetch, page_text  # noqa: E402

BASE = "https://www.rca.ac.uk/study/programme-finder/"
CATEGORIES = {
    "taught": "36-taught-masters",
    "pre-masters": "38-pre-masters",
    "research": "37-postgraduate-research",
}


def finder(category):
    url = f"{BASE}?full-time=true&part-time=true&category=programme_types&value={category}"
    html, path = fetch(url, render=True)
    s = BeautifulSoup(html, "html.parser")
    out = []
    for a in s.find_all("a", href=True):
        m = re.search(r"/programme-finder/([a-z0-9-]+)/?$", a["href"])
        if not m or any(o["slug"] == m.group(1) for o in out):
            continue
        heads = [x.get_text(" ", strip=True) for x in a.find_all(["h2", "h3", "h4"])]
        paras = [x.get_text(" ", strip=True) for x in a.find_all("p")]
        text = " ".join(a.get_text(" ", strip=True).split())
        out.append({"slug": m.group(1), "url": BASE + m.group(1) + "/",
                    "card_text": text, "card_heads": heads, "card_paras": paras})
    return out, url, path


def sections(html):
    """Split the main content into (heading, text) blocks in document order."""
    s = BeautifulSoup(html, "html.parser")
    for x in s(["script", "style", "noscript", "svg"]):
        x.decompose()
    for x in s.select('[id*="onetrust"],[class*="onetrust"]'):
        x.decompose()
    main = s.find("main") or s.body
    blocks, cur = [], {"h": "", "t": []}
    for el in main.find_all(["h1", "h2", "h3", "p", "li"]):
        txt = " ".join(el.get_text(" ", strip=True).split())
        if not txt:
            continue
        if el.name in ("h1", "h2", "h3"):
            blocks.append(cur)
            cur = {"h": txt, "t": []}
        elif not cur["t"] or cur["t"][-1] != txt:
            cur["t"].append(txt)
    blocks.append(cur)
    return [b for b in blocks if b["h"] or b["t"]]


def gallery(html):
    s = BeautifulSoup(html, "html.parser")
    out = []
    for h in s.find_all(["h2", "h3"]):
        if h.get_text(strip=True) != "Gallery":
            continue
        box = h.find_parent(["section"]) or h.parent
        for im in box.find_all("img"):
            src = im.get("data-src") or im.get("src")
            if src and src.startswith("http"):
                out.append({"src": src, "alt": im.get("alt", "")})
    return out


def staff(html):
    s = BeautifulSoup(html, "html.parser")
    out = []
    for a in s.find_all("a", href=True):
        if re.search(r"/more/staff/[a-z0-9-]+/?$", a["href"]):
            parts = [x.get_text(" ", strip=True) for x in a.find_all(["h2", "h3", "h4", "p", "span"])]
            parts = [p for p in parts if p]
            if parts and not any(o["href"] == a["href"] for o in out):
                out.append({"href": "https://www.rca.ac.uk" + a["href"] if a["href"].startswith("/") else a["href"],
                            "parts": parts[:3]})
    return out


def main():
    src = Sources()
    lists = {}
    for key, cat in CATEGORIES.items():
        items, url, path = finder(cat)
        lists[key] = items
        src.add(f"finder-{key}", url, f"Programme finder ({key})", "Royal College of Art", archive=path)
        print(key, len(items))
    programmes = []
    for key in ("taught", "pre-masters"):
        for it in lists[key]:
            html, path = fetch(it["url"], render=True, budget=15000)
            text = page_text(html)
            pdfs = re.findall(r'href="([^"]+?\.pdf)"', html)
            fees = between(text, "Fees for September 2027", "Deposit", 900) or between(text, "Fees for new students", "Deposit", 900)
            prog = {
                **it,
                "category": key,
                "archive": str(path),
                "key_details": between(text, "Key details", "School or Centre", 200),
                "school": between(text, "School or Centre", "Current location", 80),
                "location": between(text, "Current location", "Next", 60),
                "next_event": between(text, "Next open event", "Next application deadline", 80),
                "deadline": between(text, "Next application deadline", "", 60),
                "fees": fees,
                "move": (re.search(r"From August 2027,[^.]*\.", text) or [None])[0],
                "flags": [k for k, v in [("revalidation", "subject to revalidation"),
                                          ("validation", "subject to validation"),
                                          ("no-intake-2027", "will not have an intake in 2027"),
                                          ("first-intake-2027", "first intake for this programme will be September 2027")]
                          if v in text],
                "spec_pdfs": sorted(set(pdfs)),
                "sections": sections(html),
                "gallery": gallery(html),
                "staff": staff(html),
            }
            programmes.append(prog)
            src.add(f"prog-{it['slug']}", it["url"], f"{it['card_heads'][0] if it['card_heads'] else it['slug']} programme page",
                    "Royal College of Art", archive=path)
            print("ok", it["slug"], prog["school"], prog["location"], len(prog["gallery"]), "imgs", len(prog["staff"]), "staff")
    DATA.mkdir(exist_ok=True)
    (DATA / "programmes.json").write_text(json.dumps(programmes, ensure_ascii=False, indent=1))
    (DATA / "research_programmes.json").write_text(json.dumps(lists["research"], ensure_ascii=False, indent=1))
    src.save()


if __name__ == "__main__":
    main()
