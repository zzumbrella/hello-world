"""Convert a WebVTT caption file into timestamped paragraphs (one per ~45 seconds)."""
import re
import sys

def parse(path):
    cues, cur = [], None
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        m = re.match(r"(\d+):(\d+):(\d+)\.\d+ -->", line)
        if m:
            h, mi, s = map(int, m.groups())
            cur = [h * 3600 + mi * 60 + s, ""]
            cues.append(cur)
        elif line and cur is not None and not line.isdigit() and line != "WEBVTT":
            cur[1] += (" " if cur[1] else "") + line
    return cues

def paragraphs(cues, span=45):
    out, start, buf = [], None, []
    for t, txt in cues:
        if start is None:
            start = t
        buf.append(txt)
        if t - start >= span:
            out.append((start, " ".join(buf)))
            start, buf = None, []
    if buf:
        out.append((start, " ".join(buf)))
    return out

if __name__ == "__main__":
    for t, txt in paragraphs(parse(sys.argv[1])):
        print(f"[{t//60:02d}:{t%60:02d}] {txt}")
