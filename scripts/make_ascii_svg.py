#!/usr/bin/env python3
"""Turn a photo (or the GitHub avatar) into a self-typing monochrome ASCII SVG.

Light pipeline — Pillow only. Each row wipes in left-to-right with a small
cursor block, staggered top to bottom (SMIL, which GitHub plays). Prints once
and freezes.
"""
import io
import os
import sys

import requests
from PIL import Image, ImageOps

sys.path.insert(0, os.path.dirname(__file__))
from config import ASCII_BG, ASCII_COLS, ASCII_FILL, PORTRAIT_SOURCE, RAMP, USERNAME

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "avi-ascii.svg")
SRC = os.path.join(HERE, PORTRAIT_SOURCE)

# monospace cell metrics (px)
CH_W = 6.0
CH_H = 11.0
FS = 10.5
CHAR_ASPECT = CH_W / CH_H  # correct for tall glyphs when sampling rows


def load_image():
    if os.path.exists(SRC):
        print(f"Using local photo: {SRC}")
        return Image.open(SRC)
    url = f"https://github.com/{USERNAME}.png?size=480"
    print(f"No local photo — fetching avatar: {url}")
    r = requests.get(url, headers={"User-Agent": "profile-art/1.0"}, timeout=30)
    r.raise_for_status()
    return Image.open(io.BytesIO(r.content))


def to_ascii_rows(img):
    img = img.convert("L")
    img = ImageOps.autocontrast(img, cutoff=2)
    w, h = img.size
    cols = ASCII_COLS
    rows = max(1, int(cols * (h / w) * CHAR_ASPECT))
    img = img.resize((cols, rows))
    px = img.load()
    ramp = RAMP
    n = len(ramp) - 1
    out = []
    for y in range(rows):
        line = []
        for x in range(cols):
            # bright pixel -> low index (sparse). 255 -> ramp[0] (space).
            v = px[x, y]
            line.append(ramp[int((255 - v) / 255 * n + 0.5)])
        out.append("".join(line).rstrip())  # trim trailing spaces
    return out


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render(rows, static=False):
    ncols = max((len(r) for r in rows), default=0)
    width = int(ncols * CH_W) + 24
    height = int(len(rows) * CH_H) + 24
    x0, y0 = 12, 16
    row_dur = 0.45
    stagger = 0.055

    p = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">',
        f'<rect width="{width}" height="{height}" rx="8" fill="{ASCII_BG}"/>',
        f'<style>text{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;'
        f'font-size:{FS}px;white-space:pre;fill:{ASCII_FILL};}}</style>',
    ]

    for i, row in enumerate(rows):
        if not row:
            continue
        full = len(row) * CH_W
        y = y0 + i * CH_H
        begin = round(i * stagger, 3)
        if static:
            # frozen final frame: full text, no wipe, no cursor
            p.append(
                f'<text x="{x0}" y="{y}" xml:space="preserve">{esc(row)}</text>')
            continue
        clip = f"clip{i}"
        # clip rect wipes from 0 -> full width
        p.append(
            f'<clipPath id="{clip}"><rect x="{x0}" y="{y - CH_H}" width="0" height="{CH_H + 4}">'
            f'<animate attributeName="width" from="0" to="{full:.1f}" dur="{row_dur}s" '
            f'begin="{begin}s" fill="freeze"/></rect></clipPath>')
        p.append(
            f'<text x="{x0}" y="{y}" clip-path="url(#{clip})" xml:space="preserve">'
            f'{esc(row)}</text>')
        # cursor block riding the wipe edge, fades out at the end
        p.append(
            f'<rect y="{y - CH_H + 1}" width="{CH_W:.1f}" height="{CH_H}" fill="{ASCII_FILL}" '
            f'opacity="0"><animate attributeName="x" from="{x0}" to="{x0 + full:.1f}" '
            f'dur="{row_dur}s" begin="{begin}s" fill="freeze"/>'
            f'<animate attributeName="opacity" values="0;.8;.8;0" keyTimes="0;.05;.9;1" '
            f'dur="{row_dur}s" begin="{begin}s" fill="freeze"/></rect>')

    p.append("</svg>")
    return "\n".join(p)


def main():
    static = bool(os.environ.get("STATIC"))
    out = OUT.replace(".svg", ".static.svg") if static else OUT
    img = load_image()
    rows = to_ascii_rows(img)
    svg = render(rows, static=static)
    with open(out, "w") as f:
        f.write(svg)
    print(f"Wrote {out} ({len(rows)} rows, {len(svg)} bytes)")


if __name__ == "__main__":
    main()
