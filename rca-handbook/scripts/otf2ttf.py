"""Convert a CFF-flavoured OpenType font (.otf) to TrueType outlines (.ttf).

WeasyPrint embeds Noto CJK .otf fonts as CID-keyed CFF ("CID Type 0C (OT)"). MuPDF-based viewers,
common in phone apps, then show missing or wrong Chinese characters. A TrueType copy embeds as
"CID TrueType", which every viewer reads. Advance widths and OpenType layout tables are unchanged,
so the layout is identical.

Usage: python -I scripts/otf2ttf.py IN.otf OUT.ttf
Adapted from the fontTools snippet Snippets/otf2ttf.py.
"""
import sys

from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont, newTable


def otf_to_ttf(font, max_err=1.0):
    assert font.sfntVersion == "OTTO" and "CFF " in font, "not a CFF-flavoured OpenType font"
    order = font.getGlyphOrder()
    glyphset = font.getGlyphSet()
    glyf = newTable("glyf")
    glyf.glyphOrder = order
    glyf.glyphs = {}
    for name in order:
        pen = TTGlyphPen(glyphset)
        # CFF contours run counter-clockwise; TrueType expects clockwise.
        glyphset[name].draw(Cu2QuPen(pen, max_err, reverse_direction=True))
        glyf.glyphs[name] = pen.glyph()
    font["loca"] = newTable("loca")
    font["glyf"] = glyf
    for tag in ("CFF ", "VORG"):
        if tag in font:
            del font[tag]
    glyf.compile(font)
    hmtx = font["hmtx"]
    for name, g in glyf.glyphs.items():
        if hasattr(g, "xMin"):
            hmtx[name] = (hmtx[name][0], g.xMin)

    maxp = newTable("maxp")
    maxp.tableVersion = 0x00010000
    maxp.numGlyphs = len(order)
    for field in ("maxZones",):
        setattr(maxp, field, 1)
    for field in ("maxTwilightPoints", "maxStorage", "maxFunctionDefs", "maxInstructionDefs",
                  "maxStackElements", "maxSizeOfInstructions"):
        setattr(maxp, field, 0)
    maxp.maxComponentElements = max((len(getattr(g, "components", []) or []) for g in glyf.glyphs.values()), default=0)
    font["maxp"] = maxp

    # CID-keyed fonts have no meaningful glyph names: post format 3 stores none.
    post = font["post"]
    post.formatType = 3.0
    post.extraNames = []
    post.mapping = {}
    font["head"].glyphDataFormat = 0
    font.sfntVersion = "\x00\x01\x00\x00"


def main(src, dst):
    font = TTFont(src)
    otf_to_ttf(font)
    font.save(dst)


if __name__ == "__main__":
    main(*sys.argv[1:3])
