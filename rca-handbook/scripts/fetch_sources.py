"""Archive every non-programme page the sample book cites, and register it as a source."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib import Sources, fetch  # noqa: E402

RCA = "https://www.rca.ac.uk"
S26 = "https://2026.rca.ac.uk/school-of-communication/information-experience-design-ma/profile/"

# (id, url, title, publisher, render, binary)
PAGES = [
    ("rca-new-school", f"{RCA}/news-and-events/news/royal-college-of-art-announces-new-school-of-communication-design/",
     "RCA announces new School of Communication & Design (1 Sep 2026)", "Royal College of Art", False, False),
    ("rca-new-programmes", f"{RCA}/news-and-events/news/royal-college-of-art-launches-innovative-new-academic-programmes-for-202728/",
     "Royal College of Art launches innovative new academic programmes for 2027/28 (16 Sep 2026)", "Royal College of Art", False, False),
    ("rca-campus", f"{RCA}/study/the-rca-experience/our-campus/kensington-transformation/",
     "Kensington transformation / future programme locations", "Royal College of Art", False, False),
    ("rca-undergrad", f"{RCA}/study/undergraduate-study/", "Undergraduate study", "Royal College of Art", False, False),
    ("rca-apply", f"{RCA}/study/apply-to-study/master-application-process/", "Master's application process", "Royal College of Art", False, False),
    ("rca-acrossrca", f"{RCA}/study/acrossrca/", "AcrossRCA", "Royal College of Art", False, False),
    ("rca-luyi-bi", f"{RCA}/news-and-events/news/life-at-the-rca-finding-your-direction/",
     "Life at the RCA: finding your own direction (Luyi Bi, 28 Jul 2026)", "Royal College of Art", False, False),
    ("rca-melting-myth", f"{RCA}/news-and-events/news/sun-aijia-ma-information-experience-design-wins-the-lumen-prize-hua-award-for-melting-myth/",
     "Sun Aijia (MA Information Experience Design) wins the Lumen Prize HUA Award for Melting Myth (21 Oct 2022)", "Royal College of Art", False, False),
    ("rca-nc2024", f"{RCA}/news-and-events/news/5-rca-artists-join-bloomberg-new-contemporaries-2024/",
     "5 RCA artists join Bloomberg New Contemporaries 2024", "Royal College of Art", False, False),
    ("rca-coupe-appointed", f"{RCA}/news-and-events/news/royal-college-of-art-appoints-james-coupe-as-head-of-programme-for-photography/",
     "Royal College of Art appoints James Coupe as Head of Programme for Photography", "Royal College of Art", False, False),
    ("rca-barrios-appointed", f"{RCA}/news-and-events/news/dr-danielle-barrios-oneill-appointed-head-of-programme-for-ma-information-experience-design/",
     "Dr Danielle Barrios-O'Neill appointed Head of Programme for MA Information Experience Design", "Royal College of Art", False, False),
    ("rca-turner2019", f"{RCA}/news-and-events/news/turner-prize-2019-rca-staff-and-alumni-create-bold-commentary-on-turbulent-times/",
     "Turner Prize 2019 – RCA staff and alumni create bold commentary on turbulent times", "Royal College of Art", False, False),
    ("rca-millar-writing", f"{RCA}/news-and-events/news/head-of-programme-jeremy-millar-on-ma-writing-at-the-rca/",
     "Head of Programme Jeremy Millar on MA Writing at the RCA", "Royal College of Art", False, False),
    ("staff-angus-main", f"{RCA}/more/staff/angus-main1/", "Angus Main – staff profile", "Royal College of Art", False, False),
    ("staff-james-coupe", f"{RCA}/more/staff/james-coupe/", "Professor James Coupe – staff profile", "Royal College of Art", False, False),
    ("show26-ied", "https://2026.rca.ac.uk/school/information-experience-design-ma/",
     "Information Experience Design (MA) – Student Profiles 2026", "Royal College of Art", True, False),
    ("show26-luyi-bi", S26 + "luyi-bi/", "Luyi Bi – Student Profiles 2026", "Royal College of Art", True, False),
    ("show26-yiran-liu", S26 + "yiran-liu/", "Yiran Liu – Student Profiles 2026", "Royal College of Art", True, False),
    ("show26-tingxuan-xu", S26 + "tingxuan-xu/", "Tingxuan Xu – Student Profiles 2026", "Royal College of Art", True, False),
    ("show26-yuening-du", S26 + "yuening-du/", "Yuening Du – Student Profiles 2026", "Royal College of Art", True, False),
    ("show26-photo", "https://2026.rca.ac.uk/school/photography-ma/", "Photography (MA) – Student Profiles 2026", "Royal College of Art", True, False),
    ("show24-yang-zou", "https://2024.rca.ac.uk/school-of-arts-humanities/photography-ma/profile/yang-zou/",
     "Yang Zou – Student Profiles 2024", "Royal College of Art", True, False),
    ("nc-yang-zou", "https://www.newcontemporaries.org.uk/artists/yang-zou", "Yang Zou", "New Contemporaries", False, False),
    ("ibi-warm-data", "https://batesoninstitute.org/warm-data", "Warm Data", "International Bateson Institute", True, False),
    ("dunne-raby-bio", "https://dunneandraby.co.uk/content/biography", "Biography", "Dunne & Raby", False, False),
    ("lumen-hua-2022", "https://www.lumenprize.com/2022-winners/hua-award-winner", "HUA Award Winner 2022", "The Lumen Prize", True, False),
    ("steyerl-poor-image", "https://www.e-flux.com/journal/10/61362/in-defense-of-the-poor-image/",
     "Hito Steyerl, In Defense of the Poor Image, e-flux journal #10 (2009)", "e-flux", True, False),
    ("frayling-1993", "https://arl.human.cornell.edu/879Readings/Frayling_Research%20through%20Design.pdf",
     "Christopher Frayling, Research in Art and Design, Royal College of Art Research Papers 1(1), 1993", "Royal College of Art (copy hosted by Cornell)", False, True),
    ("spec-ied", "https://rca-media2.rca.ac.uk/documents/2026-27-rca-ma-information-experience-design-programme-specification.pdf",
     "MA Information Experience Design programme specification 2026-27", "Royal College of Art", False, True),
    ("spec-photo", "https://rca-media2.rca.ac.uk/documents/2026-27-rca-ma-photography-programme-specification.pdf",
     "MA Photography programme specification 2026-27", "Royal College of Art", False, True),
]

VIDEOS = [
    ("vid-ied-openday", "https://vimeo.com/1233793549", "Information Experience Design MA – Online Open Day (Angus Main)",
     "Royal College of Art (Vimeo)", "archive/vimeo/1233793549.vtt"),
    ("vid-photo-openday", "https://vimeo.com/1233688527", "Photography MA – Online Open Day (James Coupe)",
     "Royal College of Art (Vimeo)", "archive/vimeo/1233688527.vtt"),
    ("vid-yang-zou", "https://youtu.be/ZboIIDF9PLY", "Yang Zou, I love you, life. I hope it's great again (2024), full film",
     "YouTube (linked from RCA 2024 profile)", None),
    ("vid-rca-portfolio", "https://vimeo.com/showcase/10767574?video=1144943551", "Portfolio advice from the programme team",
     "Royal College of Art (Vimeo, linked from programme pages)", None),
]


def main():
    src = Sources()
    root = Path(__file__).resolve().parent.parent
    for sid, url, title, pub, render, binary in PAGES:
        try:
            _, path = fetch(url, render=render, binary=binary)
            src.add(sid, url, title, pub, kind="pdf" if binary else "web", archive=path)
            print("ok", sid)
        except Exception as e:  # keep going; report missing ones
            print("FAIL", sid, e)
    for sid, url, title, pub, arch in VIDEOS:
        src.add(sid, url, title, pub, kind="video", archive=(root / arch) if arch else None)
    src.save()


if __name__ == "__main__":
    main()
