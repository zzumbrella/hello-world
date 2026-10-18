"""Archive the external (non-RCA) resources used in side notes: book pages, papers, films, artworks."""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib import DATA, Sources, fetch, page_text  # noqa: E402

PAGES = [
    ("bbc-ways-of-seeing", "https://www.bbc.co.uk/programmes/b00drsjf", "Ways of Seeing, Episode 1 (1972)", "BBC Two", False),
    ("film-ecology-of-mind", "https://bullfrogfilms.com/catalog/eminhv.html", "An Ecology of Mind (2010), dir. Nora Bateson", "Bullfrog Films", False),
    ("dear-data", "https://www.dear-data.com/theproject", "Dear Data – The Project", "Giorgia Lupi & Stefanie Posavec", False),
    ("ridler-mosaic", "https://annaridler.com/works/mosaic-2019", "Anna Ridler, Mosaic Virus", "annaridler.com", False),
    ("haraway-1988", "https://www.jstor.org/stable/3178066",
     "Donna Haraway, Situated Knowledges: The Science Question in Feminism and the Privilege of Partial Perspective, Feminist Studies 14(3), 1988",
     "JSTOR", True),
    ("krauss-1979", "https://www.jstor.org/stable/778224", "Rosalind Krauss, Sculpture in the Expanded Field, October 8, 1979", "JSTOR", True),
]
DOI_ONLY = [
    ("cascone-2000", "https://doi.org/10.1162/014892600559489",
     "Kim Cascone, The Aesthetics of Failure: 'Post-Digital' Tendencies in Contemporary Computer Music, Computer Music Journal 24(4), 2000",
     "MIT Press"),
]


def main():
    src = Sources()
    for sid, url, title, pub, render in PAGES:
        try:
            _, path = fetch(url, render=render)
            src.add(sid, url, title, pub, archive=path)
            print("ok", sid)
        except Exception as e:
            print("FAIL", sid, e)
    for sid, url, title, pub in DOI_ONLY:
        src.add(sid, url, title, pub, kind="paper")
    covers = json.loads((DATA / "covers.json").read_text())
    for key, c in covers.items():
        try:
            html, path = fetch(c["page"])
            if "douban" in c["page"]:
                t = page_text(html, main_only=False)
                i = t.find("内容简介")
                c["blurb"] = t[i + 4:i + 900] if i >= 0 else ""
                time.sleep(8)
            src.add(f"book-{key}", c["page"], c.get("zh_title") or c["original_title"],
                    "豆瓣读书" if "douban" in c["page"] else "Open Library", archive=path)
            print("ok book", key)
        except Exception as e:
            print("FAIL book", key, e)
    (DATA / "covers.json").write_text(json.dumps(covers, ensure_ascii=False, indent=1))
    src.save()


if __name__ == "__main__":
    main()
