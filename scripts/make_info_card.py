#!/usr/bin/env python3
"""Hand-author a neofetch-style info card SVG. Rows fade/slide in on a stagger.

Content lives in scripts/config.py (INFO_TITLE / INFO_ROWS).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from config import ASCII_BG, INFO_ROWS, INFO_TITLE, PALETTE

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "info-card.svg")

KEY_COLOR = PALETTE[4]     # neon green for keys
VAL_COLOR = "#c9d1d9"
DIM = "#8b949e"
FS = 13
LINE = 26
PAD = 18
KEY_W = 92                 # px reserved for the key column


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def render(static=False):
    title_h = 40
    n = len(INFO_ROWS)
    # width: value column starts at PAD+KEY_W; size to the longest value.
    CHAR = 8.2  # px per monospace glyph at FS=13
    max_val = max(len(v) for _, v in INFO_ROWS)
    title_len = len(INFO_TITLE) + len(" — neofetch")
    width = int(max(PAD + KEY_W + max_val * CHAR + PAD,
                    PAD + 60 + title_len * 7 + PAD))
    height = title_h + n * LINE + PAD + 14

    p = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">',
        f'<style>@keyframes in{{from{{opacity:0;transform:translateX(-10px);}}'
        f'to{{opacity:1;transform:none;}}}}'
        f'.row{{opacity:{1 if static else 0};'
        f'{"" if static else "animation:in .5s ease-out forwards;"}}}'
        f'text{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;}}'
        f'</style>',
        f'<rect width="{width}" height="{height}" rx="10" fill="{ASCII_BG}"/>',
        f'<rect width="{width}" height="{height}" rx="10" fill="none" '
        f'stroke="#21262d" stroke-width="1"/>',
    ]

    # title bar: red/yellow/green dots + title
    cy = PAD + 4
    for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        p.append(f'<circle cx="{PAD + 6 + i * 16}" cy="{cy}" r="5" fill="{c}"/>')
    p.append(
        f'<text x="{PAD + 60}" y="{cy + 4}" fill="{DIM}" font-size="12">'
        f'{esc(INFO_TITLE)} — neofetch</text>')
    p.append(f'<line x1="0" y1="{title_h - 8}" x2="{width}" y2="{title_h - 8}" '
             f'stroke="#21262d"/>')

    # rows
    y = title_h + 6
    for i, (k, v) in enumerate(INFO_ROWS):
        delay = round(0.15 + i * 0.12, 2)
        ty = y + i * LINE + FS
        p.append(f'<g class="row" style="animation-delay:{delay}s">')
        p.append(f'<text x="{PAD}" y="{ty}" fill="{KEY_COLOR}" font-size="{FS}" '
                 f'font-weight="bold">{esc(k)}</text>')
        p.append(f'<text x="{PAD}" y="{ty}" fill="{DIM}" font-size="{FS}">'
                 f'{" " * (len(k) + 1)}</text>')  # spacer (visual)
        p.append(f'<text x="{PAD + KEY_W}" y="{ty}" fill="{VAL_COLOR}" '
                 f'font-size="{FS}">{esc(v)}</text>')
        p.append('</g>')

    p.append("</svg>")
    return "\n".join(p)


def main():
    static = bool(os.environ.get("STATIC"))
    out = OUT.replace(".svg", ".static.svg") if static else OUT
    svg = render(static=static)
    with open(out, "w") as f:
        f.write(svg)
    print(f"Wrote {out} ({len(svg)} bytes)")


if __name__ == "__main__":
    main()
