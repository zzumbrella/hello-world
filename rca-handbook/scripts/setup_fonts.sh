#!/usr/bin/env bash
# Install the fonts the book is set in: Noto Serif/Sans SC for Chinese, Noto Serif/Sans for Latin text.
# Latin fonts come first in the CSS font stack, so English quotes and apostrophes are not full-width.
set -euo pipefail
dest="${HOME}/.local/share/fonts"
mkdir -p "$dest"
cjk="https://raw.githubusercontent.com/notofonts/noto-cjk/main"
latin="https://raw.githubusercontent.com/notofonts/notofonts.github.io/main/fonts"
for f in Serif/SubsetOTF/SC/NotoSerifSC-{Regular,SemiBold,Bold}.otf Sans/SubsetOTF/SC/NotoSansSC-{Regular,Medium,Bold}.otf; do
  curl -sSfL -o "$dest/$(basename "$f")" "$cjk/$f"
done
for f in NotoSerif/hinted/ttf/NotoSerif-{Regular,Bold,Italic}.ttf NotoSans/hinted/ttf/NotoSans-{Regular,Medium,SemiBold,Bold}.ttf; do
  curl -sSfL -o "$dest/$(basename "$f")" "$latin/$f"
done
fc-cache -f "$dest" >/dev/null
fc-list : family | grep -E "^Noto (Serif|Sans)( SC)?$" | sort -u
