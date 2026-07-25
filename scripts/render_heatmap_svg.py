#!/usr/bin/env python3
"""Render data/contributions.json as an animated 53x7 contribution heatmap SVG.

Boxes slide in diagonally on load (CSS keyframes), then freeze. No looping.
"""
import json
import os
import sys
from datetime import date, datetime

sys.path.insert(0, os.path.dirname(__file__))
from config import PALETTE, USERNAME

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(HERE, "data", "contributions.json")
OUT = os.path.join(HERE, "contrib-heatmap.svg")

CELL = 11          # box size
GAP = 3            # gap between boxes
PITCH = CELL + GAP # 14
PAD = 20           # outer padding
TOP = 34           # room for month labels
BOTTOM = 46        # room for legend + footer
DOW_W = 26         # room for weekday labels on the left

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def build_columns(days):
    """Group days into GitHub-style columns (weeks starting Sunday)."""
    if not days:
        return []
    first = date.fromisoformat(days[0]["date"])
    # Sunday index for GitHub: Sun=0 .. Sat=6
    first_dow = (first.weekday() + 1) % 7
    origin = first.toordinal() - first_dow  # ordinal of the first column's Sunday

    columns = {}
    for d in days:
        dt = date.fromisoformat(d["date"])
        col = (dt.toordinal() - origin) // 7
        row = (dt.weekday() + 1) % 7
        columns.setdefault(col, {})[row] = d
    return [columns[c] for c in sorted(columns)]


def month_labels(columns):
    """Return (col_index, 'Mon') where a new month first appears."""
    labels = []
    last = None
    for ci, col in enumerate(columns):
        # use the first day present in the column
        day = next((col[r] for r in range(7) if r in col), None)
        if not day:
            continue
        m = date.fromisoformat(day["date"]).month
        if m != last:
            labels.append((ci, MONTHS[m - 1]))
            last = m
    return labels


def render(payload):
    days = payload["days"]
    stats = payload["stats"]
    columns = build_columns(days)
    ncols = len(columns)

    grid_w = ncols * PITCH - GAP
    grid_x = PAD + DOW_W
    grid_y = PAD + TOP
    width = grid_x + grid_w + PAD
    height = grid_y + 7 * PITCH - GAP + BOTTOM

    # Diagonal reveal: delay grows with (col + row).
    step = 0.014  # seconds per diagonal step
    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" font-family="ui-monospace,SFMono-Regular,'
        f'Menlo,Consolas,monospace">')

    # style / keyframes
    parts.append(
        "<style>"
        "@keyframes pop{from{opacity:0;transform:translateY(-6px) scale(.6);}"
        "to{opacity:1;transform:none;}}"
        ".cell{opacity:0;animation:pop .45s ease-out forwards;transform-box:fill-box;"
        "transform-origin:center;}"
        "@keyframes fade{to{opacity:1;}}"
        ".fade{opacity:0;animation:fade .6s ease-out forwards;}"
        f".t{{fill:#8b949e;font-size:9px;}}.title{{fill:{PALETTE[4]};font-size:12px;}}"
        "</style>")

    # background
    parts.append(f'<rect width="{width}" height="{height}" rx="8" fill="#0d1117"/>')

    # title
    parts.append(
        f'<text x="{grid_x}" y="{PAD + 14}" class="title fade" style="animation-delay:.1s">'
        f'{esc(payload["username"])}’s contributions</text>')

    # weekday labels (Mon/Wed/Fri)
    for row, lab in [(1, "Mon"), (3, "Wed"), (5, "Fri")]:
        cy = grid_y + row * PITCH + CELL - 2
        parts.append(f'<text x="{PAD}" y="{cy}" class="t">{lab}</text>')

    # month labels
    for ci, lab in month_labels(columns):
        mx = grid_x + ci * PITCH
        parts.append(f'<text x="{mx}" y="{grid_y - 8}" class="t">{lab}</text>')

    # cells
    for ci, col in enumerate(columns):
        for row in range(7):
            d = col.get(row)
            if not d:
                continue
            lvl = min(d["level"], len(PALETTE) - 1)
            x = grid_x + ci * PITCH
            y = grid_y + row * PITCH
            delay = round((ci + row) * step, 3)
            parts.append(
                f'<rect class="cell" x="{x}" y="{y}" width="{CELL}" height="{CELL}" '
                f'rx="2.5" fill="{PALETTE[lvl]}" style="animation-delay:{delay}s">'
                f'<title>{d["count"]} on {d["date"]}</title></rect>')

    # legend (Less -> More) bottom-right
    ly = height - PAD - 6
    legend_x = width - PAD - (len(PALETTE) * PITCH) - 60
    parts.append(f'<text x="{legend_x}" y="{ly + CELL - 2}" class="t">Less</text>')
    for i, c in enumerate(PALETTE):
        lx = legend_x + 32 + i * PITCH
        parts.append(f'<rect x="{lx}" y="{ly}" width="{CELL}" height="{CELL}" rx="2.5" fill="{c}"/>')
    more_x = legend_x + 32 + len(PALETTE) * PITCH + 4
    parts.append(f'<text x="{more_x}" y="{ly + CELL - 2}" class="t">More</text>')

    # footer stats bottom-left
    s = stats
    footer = (f'{s["total"]:,} contributions in the last year  ·  '
              f'current streak {s["current_streak"]}d  ·  '
              f'longest {s["longest_streak"]}d  ·  '
              f'best day {s["best_day"]["count"]}')
    parts.append(
        f'<text x="{PAD}" y="{ly + CELL - 2}" class="t fade" style="animation-delay:'
        f'{round(len([c for c in columns]) * 7 * step + 0.3, 2)}s">{esc(footer)}</text>')

    parts.append("</svg>")
    return "\n".join(parts)


def main():
    with open(DATA) as f:
        payload = json.load(f)
    svg = render(payload)
    with open(OUT, "w") as f:
        f.write(svg)
    print(f"Wrote {OUT} ({len(svg)} bytes)")


if __name__ == "__main__":
    main()
