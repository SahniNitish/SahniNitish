#!/usr/bin/env python3
"""Scrape the public GitHub contribution calendar (no token needed) and
write data/contributions.json with raw days + derived stats.

GitHub serves the same calendar fragment the profile page uses at
https://github.com/users/<username>/contributions
"""
import json
import os
import re
import sys
from datetime import date, datetime, timezone

import requests
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(__file__))
from config import USERNAME

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "data", "contributions.json")
URL = f"https://github.com/users/{USERNAME}/contributions"


def fetch_days():
    resp = requests.get(URL, headers={"User-Agent": "profile-art/1.0"}, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # Map cell id -> contribution count (from the <tool-tip> siblings).
    counts = {}
    for tip in soup.select("tool-tip"):
        cid = tip.get("for")
        if not cid:
            continue
        m = re.match(r"\s*(\d+)", tip.get_text())
        counts[cid] = int(m.group(1)) if m else 0

    days = []
    for td in soup.select("td.ContributionCalendar-day"):
        d = td.get("data-date")
        if not d:
            continue
        level = int(td.get("data-level", 0))
        cid = td.get("id")
        count = counts.get(cid)
        if count is None:
            # Fallback: parse from aria-label / text like "3 contributions".
            m = re.match(r"\s*(\d+)", td.get_text() or "")
            count = int(m.group(1)) if m else 0
        days.append({"date": d, "level": level, "count": count})

    days.sort(key=lambda x: x["date"])
    return days


def compute_stats(days):
    total = sum(d["count"] for d in days)

    # Streaks (only count up to today; ignore future/empty trailing cells).
    today = date.today().isoformat()
    real = [d for d in days if d["date"] <= today]

    longest = cur = 0
    for d in real:
        if d["count"] > 0:
            cur += 1
            longest = max(longest, cur)
        else:
            cur = 0

    # Current streak: walk backwards from the most recent day.
    current = 0
    for d in reversed(real):
        if d["count"] > 0:
            current += 1
        else:
            break

    best = max(days, key=lambda x: x["count"], default={"date": None, "count": 0})

    # Monthly totals.
    monthly = {}
    for d in days:
        ym = d["date"][:7]
        monthly[ym] = monthly.get(ym, 0) + d["count"]

    return {
        "total": total,
        "current_streak": current,
        "longest_streak": longest,
        "best_day": {"date": best["date"], "count": best["count"]},
        "monthly": monthly,
    }


def main():
    days = fetch_days()
    if not days:
        raise SystemExit("No contribution cells found — did the markup change?")
    stats = compute_stats(days)
    payload = {
        "username": USERNAME,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "days": days,
        "stats": stats,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"Wrote {OUT}: {len(days)} days, {stats['total']} contributions, "
          f"current streak {stats['current_streak']}, longest {stats['longest_streak']}")


if __name__ == "__main__":
    main()
