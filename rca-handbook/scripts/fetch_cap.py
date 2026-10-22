"""Archive the sources for the Contemporary Art Practice MA/MFA chapter and register them.

Also downloads the auto-generated captions of the programme's online Open Day (Vimeo), the chapter's
images and book covers, and keeps the 18 October copy of the programme page, which dates the
requirements update of 20 October. Existing entries in data/*.json are kept as they are.
"""
import json
import re
import subprocess
import sys
import time
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
from fetch_covers import douban_cover  # noqa: E402
from lib import ARCHIVE, DATA, ROOT, TODAY, UA, Sources, fetch, page_text  # noqa: E402

RCA = "https://www.rca.ac.uk"
NEWS = f"{RCA}/news-and-events/news/"
S26 = "https://2026.rca.ac.uk/school-of-arts-humanities/contemporary-art-practice-ma/profile/"
PROG = f"{RCA}/study/programme-finder/contemporary-art-practice-ma-mfa/"
RCA_PUB = "Royal College of Art"

# (id, url, title, publisher, render, binary)
PAGES = [
    ("prog-contemporary-art-practice-ma-mfa", PROG, "Contemporary Art Practice MA/MFA programme page", RCA_PUB, True, False),
    ("spec-cap", f"{RCA}/documents2/1483/2026-27-rca-ma-contemporary-art-practice-programme-specification.pdf",
     "MA Contemporary Art Practice programme specification 2026-27", RCA_PUB, False, True),
    ("rca-key-dates", f"{RCA}/study/apply-to-study/eligibility-and-key-dates/", "Eligibility and key dates", RCA_PUB, False, False),
    ("staff-harold-offeh", f"{RCA}/more/staff/harold-offeh/", "Dr Harold Offeh – staff profile", RCA_PUB, False, False),
    ("rca-offeh-sweet", NEWS + "it-could-be-sweet-harold-offeh-on-art-play-and-possibility/",
     "It Could Be Sweet: Harold Offeh on art, play and possibility (10 Nov 2025)", RCA_PUB, False, False),
    ("rca-cap-beyond-surface", NEWS + "going-beyond-the-surface-with-ma-contemporary-art-practice/",
     "Going beyond the surface with MA Contemporary Art Practice (16 May 2023)", RCA_PUB, False, False),
    ("rca-diasporas-now", NEWS + "how-diasporas-now-met-at-the-rca/", "How Diasporas Now met at the RCA (19 Mar 2024)", RCA_PUB, False, False),
    ("rca-thantrey", NEWS + "meet-leverhulme-arts-scholar-and-contemporary-art-practice-ma-graduate-yasmeen-fathima-thantrey/",
     "Meet Leverhulme Arts Scholar and Contemporary Art Practice MA graduate Yasmeen Fathima Thantrey (25 Mar 2024)", RCA_PUB, False, False),
    ("rca-chloe-abrahams", NEWS + "meet-chloe-abrahams-the-rca-alumna-exploring-the-malleability-of-memory/",
     "Meet Chloe Abrahams the RCA alumna exploring the malleability of memory (28 Feb 2023)", RCA_PUB, False, False),
    ("rca-paola-estrella", NEWS + "harnessing-the-imaginary-with-contemporary-art-practice-alumna-paola-estrella/",
     "Harnessing the imaginary with Contemporary Art Practice alumna Paola Estrella (16 Feb 2023)", RCA_PUB, False, False),
    ("rca-nc2022", NEWS + "seven-rca-artists-selected-for-bloomberg-new-contemporaries-2022/",
     "Seven RCA artists selected for Bloomberg New Contemporaries 2022 (28 Jul 2022)", RCA_PUB, False, False),
    ("rca-creative-health", NEWS + "art-care-and-creative-health-what-can-creativity-offer-that-medicine-alone-cannot/",
     "Art, care and creative health: what can creativity offer that medicine alone cannot? (21 Jan 2026)", RCA_PUB, False, False),
    ("show26-cap", "https://2026.rca.ac.uk/school/contemporary-art-practice-ma/",
     "Contemporary Art Practice (MA) – Student Profiles 2026", RCA_PUB, True, False),
]

# 2026 graduate profiles cited in the chapter: (slug, name)
PROFILES = [
    ("zhaodong-wang", "Zhaodong Wang"), ("helena-ospina-lizarralde", "Helena Ospina Lizarralde"), ("haoyu-xue", "Haoyu Xue"),
    ("nuo-liu", "Nuo Liu"), ("minjun-shin", "Minjun Shin"), ("lingyi-zhang", "Lingyi Zhang"), ("siyuan-wu-sammi", "Siyuan (Sammi) Wu"),
    ("yingqi-wang", "Yingqi Wang"), ("wenyu-yang", "Wenyu Yang"), ("ruby-chen", "Ruby Chen"), ("quang-dai-tran", "Quang-Dai Tran"),
    ("garima-gautam", "Garima Gautam"),
]

# Explainers and resources outside the RCA (the chapter's side notes): (id, url, title, publisher, render)
EXTERNAL = [
    ("krauss-1999", "https://csmt.uchicago.edu/annotations/kraussvoyage.htm",
     "Rosalind Krauss, A Voyage on the North Sea: Art in the Age of the Post-Medium Condition (1999), annotation",
     "University of Chicago, Theories of Media keywords", False),
    ("tate-relational", "https://www.tate.org.uk/art/art-terms/r/relational-aesthetics", "Art term: Relational aesthetics", "Tate", False),
    ("tate-performance", "https://www.tate.org.uk/art/art-terms/p/performance-art", "Art term: Performance art", "Tate", False),
    ("art21", "https://art21.org/", "Art21 – contemporary artists on film", "Art21", False),
    ("new-contemporaries", "https://www.newcontemporaries.org.uk/", "New Contemporaries", "New Contemporaries", False),
    ("harold-offeh-site", "https://www.haroldoffeh.com/", "Harold Offeh – artist website", "Harold Offeh", False),
]

# Vimeo videos embedded on the programme page: (id, vimeo id, title)
VIDEOS = [
    ("vid-cap-openday", "1233710137", "Contemporary Art Practice MA/MFA – Online Open Day (Harold Offeh, Jordan Baseman)"),
    ("vid-cap-portfolio", "1144944083", "How to make a good portfolio (video on the programme page)"),
]

# key: (image url, alt text from the page, page the image appears on)
IMAGES = {
    "cap-wang-1": ("https://2026.rca.ac.uk/files/2026/07/10_wage_system_installation_view-c43d21330e062d42.png",
                   "Installation view of Wage System showing a temporary workstation with a monitor and thermal printer.", S26 + "zhaodong-wang/"),
    "cap-wang-2": ("https://2026.rca.ac.uk/files/2026/07/12_wage_system_certificate-5cfd9ba92666d65e.png",
                   "Certificate screen from Wage System showing the recorded shift and payment.", S26 + "zhaodong-wang/"),
    "cap-ospina-1": ("https://2026.rca.ac.uk/files/2026/06/DSC02685-bd11d55ba167d42b.jpg",
                     "Waiting room for uncertain futures", S26 + "helena-ospina-lizarralde/"),
    "cap-ospina-2": ("https://2026.rca.ac.uk/files/2026/06/DSC02572-9f4364420ef5bfe0.jpg",
                     "Ticket machine with tickets to be ripped by visitors (turn tickets with text)", S26 + "helena-ospina-lizarralde/"),
    "cap-xue-1": ("https://2026.rca.ac.uk/files/2026/08/IMG_2368-912d5854c778efd1.JPG",
                  'Installation view of "zzZ", 2026, featuring a handmade quilt (Baijia Bei), bed, and interactive audio-mechanical elements',
                  S26 + "haoyu-xue/"),
    "cap-liu-1": ("https://2026.rca.ac.uk/files/2026/08/Nuo-LIu3dinners-2-520036d4c4172078.png",
                  "The photo of Performance-Three Dinners", S26 + "nuo-liu/"),
    "cap-liu-2": ("https://2026.rca.ac.uk/files/2026/08/3dinners-2-71108fbd4bd93804.png",
                  "The first picture of the sound installation Three Dinners.", S26 + "nuo-liu/"),
    "cap-shin-1": ("https://2026.rca.ac.uk/files/2026/07/The-Un-arrived-Homeland-1-3c8ad0ce20a48dc9.jpg",
                   "Installation view of The Un-arrived Homeland in a bright gallery.", S26 + "minjun-shin/"),
    "cap-quasi-1": ("https://2026.rca.ac.uk/files/2026/07/DSCF6381-9-57df4576cfe517af.jpg",
                    "QUASI_BEING, installation view, CAP 2026 Degree Show.", S26 + "siyuan-wu-sammi/"),
    "cap-playground-1": ("https://2026.rca.ac.uk/files/2026/08/IMG_2999-6688558cc0f2effe.jpg",
                         "Front view of Playground, showing a video monitor inside a house-shaped timber structure.", S26 + "yingqi-wang/"),
    "cap-fitter-1": ("https://2026.rca.ac.uk/files/2026/06/Wenyu-Yang_Fitter-Families-2_installation_Wenyu-Yang-12e06b939f337d29.jpg",
                     "Vintage wooden box containing archival imagery, displayed with a magnifying glass.", S26 + "wenyu-yang/"),
    "cap-offeh-covers": ("https://rca-media2.rca.ac.uk/images/Betty_Davis_HQ_copy.2e16d0ba.fill-880x660.jpg",
                         "Harold Offeh, Covers. After Betty Davis. They Say I'm Different, 1974, 2013. C-print, courtesy the artist",
                         NEWS + "it-could-be-sweet-harold-offeh-on-art-play-and-possibility/"),
    "cap-festival": ("https://rca-media2.rca.ac.uk/images/Performance_at_Dada_Ball_CAP_Festi.2e16d0ba.fill-829x585.jpg",
                     "Performance at Dada Ball, CAP Festival 2024, Hangar Gallery. Photo: Harold Offeh", PROG),
}

# key: (douban subject id, original title)
BOOKS = {
    "story-contemporary-art": ("37835730", "The Story of Contemporary Art"),
    "artificial-hells": ("36872327", "Artificial Hells: Participatory Art and the Politics of Spectatorship"),
    "relational-aesthetics": ("24722064", "Esthétique relationnelle / Relational Aesthetics"),
    "homo-ludens": ("26059062", "Homo Ludens"),
    "themes-contemporary-art": ("21233389", "Themes of Contemporary Art: Visual Art after 1980"),
}


def vimeo_captions(vid):
    """Save the auto-generated captions and a cleaned metadata file. Returns the .vtt path or None."""
    out = ARCHIVE / "vimeo"
    out.mkdir(parents=True, exist_ok=True)
    head = ["-H", f"Referer: {RCA}/", "-A", UA]
    r = subprocess.run(["curl", "-sS", "-m", "60", *head, f"https://player.vimeo.com/video/{vid}/config"],
                       capture_output=True, timeout=90)
    try:
        cfg = json.loads(r.stdout)
    except ValueError:
        print("  no player config for", vid)
        return None
    video, tracks = cfg["video"], cfg["request"].get("text_tracks", [])
    meta = {
        "id": video["id"], "title": video["title"], "duration_seconds": video["duration"], "url": video["url"],
        "owner": {"name": video["owner"]["name"], "url": video["owner"]["url"]},
        "caption_tracks": [{k: t.get(k) for k in ("label", "lang", "kind")} for t in tracks],
        "note": "Player config fetched with Referer https://www.rca.ac.uk/ (the video is embedded on the RCA programme page). "
                "Session tokens and signed media URLs are not kept; the captions are in the .vtt next to this file.",
    }
    (out / f"{vid}.meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2))
    if not tracks:
        print("  no captions for", vid)
        return None
    vtt = out / f"{vid}.vtt"
    track = tracks[0]["url"]
    track = track if track.startswith("http") else "https://player.vimeo.com" + track
    subprocess.run(["curl", "-sS", "-m", "60", *head, "-o", str(vtt), track],
                   check=True, timeout=90)
    txt = subprocess.run([sys.executable, "-I", str(Path(__file__).parent / "vtt2txt.py"), str(vtt)],
                         capture_output=True, text=True, check=True).stdout
    (out / f"{vid}.txt").write_text(txt)
    print("  captions:", vtt.name, video["title"], video["duration"], "s")
    return vtt


def keep_old_programme_page(src):
    """The 18 October archive was overwritten by the re-fetch; restore it from git under a dated name."""
    rel = "archive/www.rca.ac.uk/study__programme-finder__contemporary-art-practice-ma-mfa.html"
    dated = ROOT / rel.replace(".html", ".2026-10-18.html")
    if not dated.exists():
        old = subprocess.run(["git", "show", f"1bfc3d3:rca-handbook/{rel}"], cwd=ROOT,
                             capture_output=True, check=True).stdout
        dated.write_bytes(old)
    src.add("prog-cap-2026-10-18", PROG, "Contemporary Art Practice MA/MFA programme page (earlier copy)",
            RCA_PUB, archive=dated, accessed="2026-10-18",
            note="Kept to date the requirements update marked 'Updated 20 October 2027' on the live page.")


def fetch_images():
    path = DATA / "images.json"
    meta = json.loads(path.read_text())
    out = ROOT / "assets" / "img"
    for key, (url, alt, page) in IMAGES.items():
        if key in meta:
            continue
        ext = url.rsplit(".", 1)[-1].split("?")[0].lower()
        raw = out / f"{key}.orig.{ext}"
        r = subprocess.run(["curl", "-sS", "-L", "-A", UA, "-m", "90", "-o", str(raw), "-w", "%{http_code}", url],
                           capture_output=True, text=True)
        if r.stdout.strip() != "200":
            print("FAIL image", key, url)
            continue
        im = Image.open(raw).convert("RGB")
        if im.width > 1400:
            im = im.resize((1400, round(im.height * 1400 / im.width)))
        im.save(out / f"{key}.jpg", quality=85, optimize=True)
        meta[key] = {"src": url, "alt": alt, "page": page, "accessed": TODAY, "size": im.size}
        print("ok image", key, im.size)
    path.write_text(json.dumps(meta, ensure_ascii=False, indent=1))


def fetch_books(src):
    """Chinese edition (Douban): cover, edition info and blurb for the book cards."""
    path = DATA / "covers.json"
    covers = json.loads(path.read_text())
    out = ROOT / "assets" / "covers"
    for key, (subject, original) in BOOKS.items():
        if key not in covers:
            info = douban_cover(subject, out / f"{key}.orig.jpg")
            if not info:
                print("FAIL cover", key)
                continue
            im = Image.open(out / f"{key}.orig.jpg").convert("RGB")
            im.thumbnail((500, 750))
            im.save(out / f"{key}.jpg", quality=85)
            covers[key] = {**info, "isbn": None, "original_title": original, "accessed": TODAY}
            time.sleep(8)
        c = covers[key]
        html, archived = fetch(c["page"])
        t = page_text(html, main_only=False)
        m = re.search(r"作者\s*[:：].{0,400}?ISBN\s*[:：]\s*\d+", t)
        c["info"] = m.group(0) if m else c.get("info", "")
        c["zh_title"] = re.sub(r"\s*\(豆瓣\)$", "", c.get("title", "")).strip()
        i = t.find("内容简介")
        c["blurb"] = t[i + 4:i + 900] if i >= 0 else ""
        src.add(f"book-{key}", c["page"], c["zh_title"] or original, "豆瓣读书", archive=archived)
        print("ok book", key, "|", c["zh_title"], "|", c["info"][:80])
        time.sleep(8)
    path.write_text(json.dumps(covers, ensure_ascii=False, indent=1))


def main():
    src = Sources()
    keep_old_programme_page(src)
    pages = PAGES + [(f"show26-cap-{slug}", S26 + slug + "/", f"{name} – Student Profiles 2026", RCA_PUB, True, False)
                     for slug, name in PROFILES]
    pages += [(sid, url, title, pub, render, False) for sid, url, title, pub, render in EXTERNAL]
    for sid, url, title, pub, render, binary in pages:
        try:
            _, path = fetch(url, render=render, binary=binary)
            src.add(sid, url, title, pub, kind="pdf" if binary else "web", archive=path)
            print("ok", sid)
        except Exception as e:  # keep going; report missing ones
            print("FAIL", sid, e)
    for sid, vid, title in VIDEOS:
        vtt = vimeo_captions(vid)
        src.add(sid, f"https://vimeo.com/{vid}", title, "Royal College of Art (Vimeo)", kind="video", archive=vtt)
    fetch_images()
    fetch_books(src)
    src.save()


if __name__ == "__main__":
    main()
