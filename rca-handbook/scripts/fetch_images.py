"""Download the official images the sample book uses, with caption/credit metadata."""
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
from lib import DATA, ROOT, TODAY, UA  # noqa: E402

OUT = ROOT / "assets" / "img"
P = {p["slug"]: p for p in json.loads((DATA / "programmes.json").read_text())}


def gallery_src(slug, needle):
    for g in P[slug]["gallery"]:
        if needle.lower() in g["alt"].lower():
            return g["src"], g["alt"], P[slug]["url"]
    raise KeyError(f"{slug}: {needle}")


# key -> (programme slug + alt needle) or explicit (url, alt, page)
WANT = {
    # Lesson 2
    "l2-climate": ("digital-narrative-arts-ma-mfa", "Our Gods are Angry"),
    "l2-tech": ("innovation-design-engineering-ma-msc", "The Aleta Index"),
    "l2-nonhuman": ("information-experience-design-ma", "Melting + Myth"),
    "l2-body": ("fashion-ma", "Meret Baer"),
    "l2-meaning": ("visual-communication-ma", "What have you noticed today"),
    "l2-memory": ("visual-communication-ma", "Inbetween"),
    "l2-identity": ("visual-communication-ma", "We Knead to Talk"),
    "l2-labour": ("curating-contemporary-art-ma", "Visitors and curators in Ruth Beale"),
    # Lesson 3
    "l3-participation": ("curating-contemporary-art-ma", "Lynn Lu, The Weight of raindrops"),
    "l3-futures": ("design-futures-ma", "Preferable Futures of Urban Architecture"),
    # School overviews
    "school-arch": ("architecture-m-arch", "Borrowed Atmospheres"),
    "school-ah": ("painting-ma", "Visitors view works by MA Painting students"),
    "school-cd": ("digital-narrative-arts-ma-mfa", "Visitors at the RCA2026 Festival of Communication"),
    # IED chapter
    "ied-yiran-liu": ("information-experience-design-ma", "Meeting with Your Boulder by Yiran Liu (MA"),
    "ied-tingxuan-xu": ("information-experience-design-ma", "Cloud Gravity"),
    "ied-yuening-du": ("information-experience-design-ma", "What the Body Keeps"),
    "ied-cohort": ("information-experience-design-ma", "Work by MA Information Experience Design students"),
    # Photography chapter
    "photo-issaka": ("photography-ma", "Blueprint 6"),
    "photo-dada": ("photography-ma", "Dada"),
    "photo-tutorial-eve": ("photography-ma", "Tutorial Eve"),
    "photo-liang": ("photography-ma", "Mountain of A"),
}

EXPLICIT = {
    "ied-luyi-bi-1": ("https://2026.rca.ac.uk/files/2026/03/DSCF1770-2-1b402164b10db086-rotated-e1785702174604.jpg",
                      "An 8-inch Sony CRT monitor and headphones present a single-channel broadcast",
                      "https://2026.rca.ac.uk/school-of-communication/information-experience-design-ma/profile/luyi-bi/"),
    "ied-luyi-bi-2": ("https://2026.rca.ac.uk/files/2026/03/DSCF1771-2-87ee2a8d1be64918-rotated-e1785702196453.jpg",
                      "An A5 calendar presented as the local shop owner's diary.",
                      "https://2026.rca.ac.uk/school-of-communication/information-experience-design-ma/profile/luyi-bi/"),
    "ied-luyi-bi-3": ("https://2026.rca.ac.uk/files/2026/03/DSCF1775-2-bfce9308df9b5715-rotated-e1785702232444.jpg",
                      "A wooden shuttered window, accompanied by a suspended metal bucket.",
                      "https://2026.rca.ac.uk/school-of-communication/information-experience-design-ma/profile/luyi-bi/"),
    "photo-yang-zou-1": ("https://2024.rca.ac.uk/files/2024/07/ILY_still5-950x572.jpg",
                         "A color image of a woman standing on stairs with a cigarette in her hand",
                         "https://2024.rca.ac.uk/school-of-arts-humanities/photography-ma/profile/yang-zou/"),
    "photo-yang-zou-2": ("https://2024.rca.ac.uk/files/2024/07/ILY_still2-950x534.jpg",
                         "An elderly person with graying hair looking into the distance with binoculars on a train",
                         "https://2024.rca.ac.uk/school-of-arts-humanities/photography-ma/profile/yang-zou/"),
    "photo-yang-zou-3": ("https://2024.rca.ac.uk/files/2024/07/ILY_still1-950x534.jpg",
                         "A brutalist building",
                         "https://2024.rca.ac.uk/school-of-arts-humanities/photography-ma/profile/yang-zou/"),
}


def download(url, dest):
    r = subprocess.run(["curl", "-sS", "-L", "-A", UA, "-m", "90", "-o", str(dest), "-w", "%{http_code}", url],
                       capture_output=True, text=True)
    return r.stdout.strip() == "200" and dest.exists() and dest.stat().st_size > 1000


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    meta = {}
    items = {k: gallery_src(*v) for k, v in WANT.items()}
    items.update(EXPLICIT)
    for key, (url, alt, page) in items.items():
        ext = url.rsplit(".", 1)[-1].split("?")[0].lower()
        raw = OUT / f"{key}.orig.{ext}"
        if not raw.exists() and not download(url, raw):
            print("FAIL", key, url)
            continue
        im = Image.open(raw).convert("RGB")
        if im.width > 1400:
            im = im.resize((1400, round(im.height * 1400 / im.width)))
        im.save(OUT / f"{key}.jpg", quality=85, optimize=True)
        meta[key] = {"src": url, "alt": alt, "page": page, "accessed": TODAY, "size": im.size}
        print("ok", key, im.size)
    (DATA / "images.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
