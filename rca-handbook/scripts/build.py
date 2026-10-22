"""Assemble content/*.html into one book and render it to PDF with WeasyPrint.

Shortcodes used in content files:
  [[c:source-id]] / [[c:source-id@31:08]]   numbered citation (per chapter), optional locator
  {{官网}} {{解读}} {{经验}} {{延伸}}          content labels
  [[fig:image-key|caption]]                  official image with automatic credit + citation
  [[ref:anchor-id]]                          "第 N 页" cross-reference
  <aside class="side book" data-cover="k">   book card: cover and edition line are added automatically
  <aside class="side res" data-url="..." data-kind="纪录片">  resource card: QR code added automatically
"""
import html
import json
import re
import sys
from pathlib import Path

import qrcode

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = ROOT / "output"

SOURCES = json.loads((DATA / "sources.json").read_text())
IMAGES = json.loads((DATA / "images.json").read_text())
COVERS = json.loads((DATA / "covers.json").read_text())

TAGS = {"官网": "t-off", "解读": "t-int", "经验": "t-exp", "延伸": "t-ext"}

# Chapters also written as their own PDF (page numbers stay those of the full book): section id -> file name
EXTRACTS = {"cap": "读懂皇艺-当代艺术实践样章.pdf"}

# Every chapter of the full book, in order. Entries without a file are listed in the TOC as "正式版收录".
MANIFEST = [
    ("front", "00-cover.html"), ("front", "01-howto.html"), ("toc", None), ("front", "02-preface.html"),
    ("part", "第一部分　零基础先补四课"),
    ("chapter", "10-lesson1.html"), ("chapter", "11-lesson2.html"), ("chapter", "12-lesson3.html"), ("chapter", "13-lesson4.html"),
    ("part", "第二部分　29 个专业逐个讲",
     "样书收录三个学院总览，以及三章样章：当代艺术实践（<a class=\"pref\" href=\"#cap\"></a>）、"
     "摄影（<a class=\"pref\" href=\"#photography\"></a>）和信息体验设计（<a class=\"pref\" href=\"#ied\"></a>）。"
     "其余 26 个专业已列在目录里，正式版收录。"),
    ("chapter", "20-school-architecture.html"),
    ("planned", "建筑学 Architecture MArch"), ("planned", "室内设计 Interior Design MA"),
    ("planned", "环境建筑与城市设计 Environmental Architecture & Urban Design MA"), ("planned", "设计实践 Design Practice MArch"),
    ("chapter", "30-school-arts-humanities.html"),
    ("chapter", "32-contemporary-art-practice.html"), ("planned", "绘画 Painting MA"),
    ("chapter", "31-photography.html"),
    ("planned", "版画 Print MA"), ("planned", "雕塑 Sculpture MA"), ("planned", "陶瓷与玻璃 Ceramics & Glass MA"),
    ("planned", "珠宝与金属 Jewellery & Metal MA"), ("planned", "当代艺术策展 Curating Contemporary Art MA"),
    ("planned", "写作 Writing MA"), ("planned", "设计史 V&A/RCA History of Design MA"),
    ("planned", "人工智能与数字艺术 Artificial Intelligence & Digital Art MA/MFA"), ("planned", "研究型硕士 Master of Research RCA (MRes)"),
    ("chapter", "40-school-communication-design.html"),
    ("planned", "动画 Animation MA"), ("planned", "Aardman/RCA 动画（职业驻场）MFA"),
    ("planned", "数字叙事艺术 Digital Narrative Arts MA/MFA"),
    ("chapter", "41-ied.html"),
    ("planned", "视觉传达 Visual Communication MA"), ("planned", "声音实践 Sound Practice MA"),
    ("planned", "产品设计 Design Products MA/MDes"), ("planned", "时装 Fashion MA"), ("planned", "纺织 Textiles MA"),
    ("planned", "服务设计 Service Design MA"), ("planned", "创新设计工程 Innovation Design Engineering MA/MSc"),
    ("planned", "智能出行设计 Intelligent Mobility Design MA/MDes"), ("planned", "设计未来 Design Futures MA"),
    ("part", "第三部分　申请实操",
     "正式版收录：作品集、个人陈述、2 分钟视频；时间线、学费与奖学金。<br>"
     "样书里，申请要求先放在第 1 课「录取看什么、要交什么」（<a class=\"pref\" href=\"#lesson1-admission\"></a>），"
     "准备建议放在三章样章的「零基础怎么准备」（<a class=\"pref\" href=\"#cap-prepare\"></a>、"
     "<a class=\"pref\" href=\"#photo-prepare\"></a>、<a class=\"pref\" href=\"#ied-prepare\"></a>）。"),
    ("planned", "作品集、个人陈述、2 分钟视频"), ("planned", "时间线、学费与奖学金"),
    ("part", "附录",
     "样书收录来源总表（<a class=\"pref\" href=\"#sources\"></a>）。正式版另有：两个研究生文凭与研究型学位、术语中英索引、人名索引。"),
    ("planned", "两个研究生文凭与研究型学位"), ("planned", "术语中英索引、人名索引"),
    ("chapter", "90-sources.html"),
]


def qr_png(url, name):
    path = ROOT / "assets" / "qr" / f"{name}.png"
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        img = qrcode.make(url, box_size=6, border=1)
        img.save(path)
    return path.relative_to(ROOT).as_posix()


def source_for_url(url, accessed="2026-10-18"):
    for sid, s in SOURCES.items():
        if s["url"].rstrip("/") == url.rstrip("/"):
            return sid
    sid = "img-" + re.sub(r"[^a-z0-9]+", "-", url.lower())[-60:]
    SOURCES[sid] = {"url": url, "title": "图片来源页面", "publisher": "Royal College of Art", "kind": "web",
                    "archive": None, "accessed": accessed, "note": ""}
    return sid


def edition_line(info):
    """Turn Douban '#info' text into '译者 · 出版社 · 年份'."""
    def grab(label):
        m = re.search(label + r"\s*[:：]\s*(.+?)(?=\s+\S+\s*[:：]|$)", info)
        return m.group(1).strip() if m else ""
    parts = [grab("作者"), ("译者：" + grab("译者")) if grab("译者") else "", grab("出版社"), grab("出版年")]
    return " · ".join(p for p in parts if p)


class Chapter:
    def __init__(self, cid):
        self.cid = cid
        self.order = []

    def num(self, sid):
        if sid not in SOURCES:
            raise KeyError(f"unknown source id: {sid}")
        if sid not in self.order:
            self.order.append(sid)
        return self.order.index(sid) + 1

    def cite(self, m):
        sid, _, loc = m.group(1).partition("@")
        n = self.num(sid)
        label = f"{n}" + (f"·{loc}" if loc else "")
        return f'<sup class="cite"><a href="#src-{self.cid}-{n}">{label}</a></sup>'

    def fig(self, m):
        key, _, caption = m.group(1).partition("|")
        size = ""
        if caption.endswith(("|mid", "|small")):  # optional size: [[fig:key|caption|mid]]
            caption, _, size = caption.rpartition("|")
        meta = IMAGES[key]
        sid = source_for_url(meta["page"], meta.get("accessed", "2026-10-18"))
        n = self.num(sid)
        w, h = meta["size"]
        cls = ("fig tall" if h > w * 1.2 else "fig") + (f" {size}" if size else "")
        return (f'<figure class="{cls}"><img src="assets/img/{key}.jpg" alt="{html.escape(meta["alt"])}">'
                f'<figcaption>{caption}<span class="credit">© 原作者 / Royal College of Art · 图片来自 RCA 官网'
                f'<sup class="cite"><a href="#src-{self.cid}-{n}">{n}</a></sup></span></figcaption></figure>')

    def sources_html(self):
        if not self.order:
            return ""
        items = []
        for i, sid in enumerate(self.order, 1):
            s = SOURCES[sid]
            kind = {"video": "视频", "pdf": "PDF", "paper": "论文"}.get(s["kind"], "网页")
            arch = "；已存档" if s.get("archive") else ""
            items.append(f'<li id="src-{self.cid}-{i}"><span class="n">[{i}]</span> {html.escape(s["title"])}. '
                         f'{html.escape(s["publisher"])}（{kind}）. <span class="url">{html.escape(s["url"])}</span>'
                         f'<span class="acc">（读取：{s["accessed"]}{arch}）</span></li>')
        return '<div class="chapter-sources"><h3>本章出处</h3><ol>' + "".join(items) + "</ol></div>"


def render_chapter(text, cid):
    ch = Chapter(cid)
    for tag, cls in TAGS.items():
        text = text.replace("{{" + tag + "}}", f'<span class="tag {cls}">{tag}</span>')
    text = re.sub(r"\[\[fig:(.+?)\]\]", ch.fig, text, flags=re.S)
    text = re.sub(r"\[\[c:([^\]]+)\]\]", ch.cite, text)
    text = re.sub(r"\[\[ref:([^\]]+)\]\]", r'<a class="pref" href="#\1"></a>', text)

    def book(m):
        attrs, body = m.group(1), m.group(2)
        key = re.search(r'data-cover="([^"]+)"', attrs).group(1)
        c = COVERS[key]
        ed = edition_line(c.get("info", "")) if c["edition"] == "zh" else f"英文原版 · ISBN {c['isbn']}"
        title = c.get("zh_title") or c["original_title"]
        sid = f"book-{key}"
        n = ch.num(sid)
        # No floats inside a note: WeasyPrint leaves a nested float behind when the note moves to the next page.
        return (f'<aside class="side book"><div class="bk-head"><div class="bk-cover"><img class="cover" src="assets/covers/{key}.jpg"></div>'
                f'<div class="bk-meta"><div class="bk-label">书卡</div><div class="bk-title">{html.escape(title)}</div>'
                f'<div class="bk-ed">{html.escape(ed)}<sup class="cite"><a href="#src-{cid}-{n}">{n}</a></sup></div></div></div>'
                f'{body}</aside>')
    text = re.sub(r'<aside class="side book"([^>]*)>(.*?)</aside>', book, text, flags=re.S)

    def res(m):
        attrs, body = m.group(1), m.group(2)
        url = re.search(r'data-url="([^"]+)"', attrs).group(1)
        kind = re.search(r'data-kind="([^"]+)"', attrs).group(1)
        png = qr_png(url, re.sub(r"[^a-z0-9]+", "-", url.lower())[-50:])
        return (f'<aside class="side res"><div class="res-head"><div class="rk"><span class="res-kind">{kind}</span></div>'
                f'<div class="rq"><img class="qr" src="{png}"></div></div>{body}</aside>')
    text = re.sub(r'<aside class="side res"([^>]*)>(.*?)</aside>', res, text, flags=re.S)
    text = keep_heading_with_text(text)
    text = text.replace("<!--SOURCES-->", ch.sources_html())
    return text.replace("……", '<span class="zh">……</span>')


BLOCK = r'(?:<aside class="side.*?</aside>|<figure.*?</figure>|<div class="figrow">.*?</div>\s*(?:<p class="small">.*?</p>)?)'


def keep_heading_with_text(text):
    """A heading followed directly by side notes or figures gets orphaned at a page foot.
    Move the first paragraph up so that every heading is followed by running text."""
    pat = re.compile(r'(</h[23]>)\s*((?:' + BLOCK + r'\s*)+)(<p\b(?![^>]*class="small").*?</p>)', re.S)
    prev = None
    while prev != text:
        prev = text
        text = pat.sub(lambda m: m.group(1) + "\n" + m.group(3) + "\n" + m.group(2), text)
    return text


def all_sources_html():
    groups = [
        ("RCA 专业页面与专业搜索页", lambda k, v: k.startswith(("prog-", "finder-"))),
        ("RCA 课程规格书", lambda k, v: k.startswith("spec-")),
        ("RCA 新闻、公告、教师与申请页面", lambda k, v: k.startswith(("rca-", "staff-", "redirect-"))),
        ("RCA 毕业展页面", lambda k, v: k.startswith("show")),
        ("视频（含官方开放日录像，字幕已存档）", lambda k, v: k.startswith("vid-")),
        ("书籍（豆瓣读书、维基百科等）", lambda k, v: k.startswith("book-")),
        ("论文、纪录片、艺术作品与其他外部资料", lambda k, v: True),
    ]
    used, out = set(), []
    for title, pred in groups:
        rows = []
        for k, v in sorted(SOURCES.items()):
            if k in used or k.startswith("img-") or not pred(k, v):
                continue
            used.add(k)
            arch = v.get("archive") or "—"
            rows.append(f"<tr><td>{html.escape(v['title'])}<br><span class='small'>{html.escape(v['publisher'])}</span></td>"
                        f"<td class='en' style='word-break:break-all'>{html.escape(v['url'])}</td><td>{v['accessed']}</td></tr>")
        if rows:
            out.append(f"<h2 id='src-{len(out)+1}'>{title}</h2><table class='wide'><tr><th>来源</th><th>网址</th><th>读取</th></tr>{''.join(rows)}</table>")
    return "".join(out)


def toc_html(entries):
    rows = []
    for kind, label, anchor, subs in entries:
        if kind == "part":
            rows.append(f'<li class="toc-part">{label}</li>')
        elif kind == "planned":
            rows.append(f'<li class="toc-planned">{label}<span class="later">正式版收录</span></li>')
        else:
            rows.append(f'<li class="toc-ch"><a href="#{anchor}">{label}</a></li>')
            for sa, sl in subs:
                rows.append(f'<li class="toc-sub"><a href="#{sa}">{sl}</a></li>')
    return ('<section class="toc" id="toc"><h1 class="toc-title">目录</h1><ul>' + "".join(rows) + "</ul></section>")


def element_pages(document):
    """Map (attribute, value) of every numbered element to the set of page indexes it is drawn on."""
    where = {}
    for i, page in enumerate(document.pages):
        for box in page._page_box.descendants():
            el = getattr(box, "element", None)
            if el is None:
                continue
            for attr in ("data-sid", "data-b"):
                v = el.get(attr)
                if v is not None:
                    where.setdefault((attr, v), set()).add(i)
    return where


def render_without_split_sides(doc, wrap, rounds=8):
    """WeasyPrint splits a floated side note across two pages even with break-inside: avoid.
    Render, re-anchor every split note just before the first block that starts on the next page
    (or just after the block that runs onto it), and repeat until no note is split."""
    from bs4 import BeautifulSoup
    from weasyprint import HTML
    soup = BeautifulSoup(doc, "html.parser")
    n = 0
    for sec in soup.select("section.chapter, section.front"):
        for child in sec.find_all(recursive=False):
            child["data-b"] = str(n)
            n += 1
    for i, aside in enumerate(soup.select("aside.side")):
        aside["data-sid"] = str(i)
    for rnd in range(rounds + 1):
        page = wrap(str(soup))
        document = HTML(string=page, base_url=str(ROOT)).render()
        where = element_pages(document)
        split = sorted((k[1] for k, v in where.items() if k[0] == "data-sid" and len(v) > 1), key=int)
        if not split or rnd == rounds:
            if split:
                print("warning: side notes still split:", split)
            return page, document
        print(f"round {rnd + 1}: re-anchoring {len(split)} split side note(s)")
        for sid in split:
            aside = soup.find("aside", attrs={"data-sid": sid})
            first = min(where[("data-sid", sid)])
            for sib in aside.find_next_siblings():
                pages = where.get(("data-b", sib.get("data-b")))
                if sib.name == "aside" or not pages:
                    continue
                if min(pages) > first:
                    # The gap before this block is still at the foot of the old page, so make the
                    # note unbreakable: WeasyPrint then carries it over whole, with the block.
                    sib.insert_before(aside.extract())
                    if not aside.find("div", class_="side-in", recursive=False):
                        inner = soup.new_tag("div", attrs={"class": "side-in"})
                        for c in list(aside.contents):
                            inner.append(c.extract())
                        aside.append(inner)
                    break
                if max(pages) > first:
                    sib.insert_after(aside.extract())
                    break


def cff_fonts(pdf_path):
    """Names of fonts embedded as CFF (FontFile3). MuPDF-based viewers drop their Chinese characters."""
    from pypdf import PdfReader
    bad = set()
    for page in PdfReader(pdf_path).pages:
        for font in page["/Resources"].get_object().get("/Font", {}).values():
            for desc in font.get_object().get("/DescendantFonts", []):
                fd = desc.get_object().get("/FontDescriptor", {})
                if "/FontFile3" in fd.get_object():
                    bad.add(str(fd.get_object()["/FontName"]))
    return sorted(bad)


def main():
    parts, toc_entries, part_no = [], [], 0
    for kind, ref, *note in MANIFEST:
        if kind == "part":
            part_no += 1
            pid = f"part-{part_no}"
            extra = f'<p class="part-note">{note[0]}</p>' if note else ""
            parts.append(f'<section class="part-page" id="{pid}"><h1 class="part-title">{ref}</h1>{extra}</section>')
            toc_entries.append(("part", ref, pid, []))
        elif kind == "planned":
            toc_entries.append(("planned", ref, None, []))
        elif kind == "toc":
            parts.append("<!--TOC-->")
        else:
            if not (ROOT / "content" / ref).exists():
                print("missing (skipped):", ref)
                continue
            raw = (ROOT / "content" / ref).read_text()
            cid = Path(ref).stem
            body = render_chapter(raw, cid)
            parts.append(body)
            if kind in ("chapter", "front") and "<h1" in body:
                h1 = re.search(r'<h1[^>]*id="([^"]+)"[^>]*>(.*?)</h1>', body, flags=re.S)
                subs = re.findall(r'<h2[^>]*id="([^"]+)"[^>]*>(.*?)</h2>', body, flags=re.S)
                strip = lambda s: re.sub(r"<[^>]+>", "", s)
                toc_entries.append(("chapter", strip(h1.group(2)), h1.group(1), [(a, strip(t)) for a, t in subs]))
    doc = "\n".join(parts).replace("<!--TOC-->", toc_html(toc_entries))
    doc = doc.replace("<!--ALLSOURCES-->", all_sources_html())
    # A header row in <thead> is repeated on the next page and never left alone at a page foot.
    doc = re.sub(r"(<table[^>]*>)\s*(<tr>(.*?)</tr>)",
                 lambda m: m.group(0) if "<td" in m.group(3) else f"{m.group(1)}<thead>{m.group(2)}</thead>", doc, flags=re.S)
    css = (ROOT / "styles" / "book.css").read_text()

    def wrap(body):
        return (f'<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>读懂皇艺（样书）</title>'
                f'<meta name="author" content="《读懂皇艺》编写组"><style>{css}</style></head><body>{body}</body></html>')
    OUT.mkdir(exist_ok=True)
    if "--html-only" in sys.argv:
        (OUT / "book.html").write_text(wrap(doc))
        return
    page, document = render_without_split_sides(doc, wrap)
    (OUT / "book.html").write_text(page)
    document.write_pdf(OUT / "读懂皇艺-样书.pdf")
    print(f"PDF written: {OUT / '读懂皇艺-样书.pdf'} ({len(document.pages)} pages)")
    starts = set(re.findall(r'<section class="(?:chapter|part-page|front|toc)[^"]*" id="([^"]+)"', page))
    anchors = [set(pg.anchors) for pg in document.pages]
    for sid, name in EXTRACTS.items():
        first = next(i for i, a in enumerate(anchors) if sid in a)
        # every page of a section carries its anchor, so look for the next *other* section
        end = next((i for i in range(first + 1, len(anchors)) if anchors[i] & (starts - {sid})), len(anchors))
        document.copy(document.pages[first:end]).write_pdf(OUT / name)
        print(f"chapter PDF written: {OUT / name} (pages {first + 1}-{end})")
    bad = cff_fonts(OUT / "读懂皇艺-样书.pdf")
    if bad:
        print("warning: fonts embedded as CFF, Chinese will be missing in MuPDF-based viewers; run scripts/setup_fonts.sh:", bad)


if __name__ == "__main__":
    main()
