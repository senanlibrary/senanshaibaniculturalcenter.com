#!/usr/bin/env python3
"""Produce the cataloging figures for the monthly note.

Traffic numbers come from the Cloudflare dashboard; these are the figures
that go up every month and belong at the top of the report. Reporting notes
are kept locally under private/ rather than published with the code.
"""
import json
import os
import sys
from collections import Counter

# The center's own estimate of total holdings, used for the coverage figure.
ESTIMATED_HOLDINGS = 20000


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main(path=None):
    path = path or os.path.join(ROOT, "data", "catalog.json")
    data = json.load(open(path, encoding="utf-8"))
    items = data["items"]

    libraries = Counter(i["library"] for i in items)
    languages = Counter(l for i in items for l in i["languages"])
    decades = Counter(
        f"{i['year'] // 10 * 10}s" for i in items if i["year"]
    )
    with_subjects = sum(1 for i in items if i["subjects"])
    arabic = sum(1 for i in items if i["titleArabic"])

    print(f"Records cataloged            {len(items):,}")
    print(f"Share of estimated holdings  {len(items) / ESTIMATED_HOLDINGS:.1%}")
    print(f"Records with subject terms   {with_subjects:,} ({with_subjects / len(items):.0%})")
    print(f"Records with Arabic titles   {arabic:,} ({arabic / len(items):.0%})")
    print(f"Individual record pages      {len(items):,}")
    dist = os.path.join(ROOT, "site", "dist")
    if os.path.isdir(dist):
        html_pages = sum(
            name.endswith(".html")
            for _, _, names in os.walk(dist)
            for name in names
        )
        print(f"Static HTML pages published  {html_pages:,}")
    print()
    print("By library")
    for name, n in libraries.most_common():
        print(f"  {name:42} {n:,}")
    print()
    print("By language")
    for name, n in languages.most_common(6):
        print(f"  {name:42} {n:,}")
    print()
    print("Oldest and newest imprint")
    years = sorted(i["year"] for i in items if i["year"])
    if years:
        print(f"  {years[0]} – {years[-1]}")
    print()
    print("Best-represented decades")
    for name, n in decades.most_common(5):
        print(f"  {name:42} {n:,}")


if __name__ == "__main__":
    main(*sys.argv[1:])
