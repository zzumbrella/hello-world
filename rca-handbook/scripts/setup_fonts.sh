#!/usr/bin/env bash
# Install the fonts the book is set in: Noto Serif/Sans SC for Chinese, Noto Serif/Sans for Latin text.
# Latin fonts come first in the CSS font stack, so English quotes and apostrophes are not full-width.
# The Chinese .otf files are converted to TrueType outlines (scripts/otf2ttf.py): embedded as CFF,
# their characters go missing in MuPDF-based PDF viewers.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
py="${PYTHON:-$HOME/.venvs/rca/bin/python}"
dest="${HOME}/.local/share/fonts"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
mkdir -p "$dest"
cjk="https://raw.githubusercontent.com/notofonts/noto-cjk/main"
latin="https://raw.githubusercontent.com/notofonts/notofonts.github.io/main/fonts"
for f in Serif/SubsetOTF/SC/NotoSerifSC-{Regular,SemiBold,Bold}.otf Sans/SubsetOTF/SC/NotoSansSC-{Regular,Medium,Bold}.otf; do
  name="$(basename "$f" .otf)"
  curl -sSfL -o "$tmp/$name.otf" "$cjk/$f"
  "$py" -I "$here/otf2ttf.py" "$tmp/$name.otf" "$dest/$name.ttf"
  rm -f "$dest/$name.otf"
done
for f in NotoSerif/hinted/ttf/NotoSerif-{Regular,Bold,Italic}.ttf NotoSans/hinted/ttf/NotoSans-{Regular,Medium,SemiBold,Bold}.ttf; do
  curl -sSfL -o "$dest/$(basename "$f")" "$latin/$f"
done
fc-cache -f "$dest" >/dev/null
fc-list : family file | grep -E ": Noto (Serif|Sans)( SC)?(,|$)" | sort
