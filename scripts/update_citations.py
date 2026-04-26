#!/usr/bin/env python3
"""Scrape Google Scholar profile for citation counts and write citations.json.

Used by .github/workflows/update-citations.yml on a daily schedule.
Reads the user's Scholar profile page with a browser User-Agent, parses each
publication row, and matches titles against a known DOI map.

Output schema:
    {
      "updated": "YYYY-MM-DD",
      "total": <int>,
      "counts": {"<doi>": <int>, ...}
    }
"""

import datetime as dt
import json
import re
import sys
import urllib.request
from pathlib import Path

SCHOLAR_USER = "ZYvKJF4AAAAJ"
URL = (
    f"https://scholar.google.com/citations?user={SCHOLAR_USER}"
    f"&hl=en&cstart=0&pagesize=100"
)
UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)

# Lower-case substring of the Scholar title -> canonical DOI used on the site.
TITLE_TO_DOI = {
    "topoflow": "10.1038/s41612-026-01417-5",
    "cross-resolution attention": "10.48550/arXiv.2603.11725",
    "inverse neural operator": "10.48550/arXiv.2603.11854",
    "deep spatio-temporal": "10.1007/978-3-031-95911-0_6",
}


def fetch_html() -> str:
    req = urllib.request.Request(URL, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace")


def parse_counts(html: str) -> dict[str, int]:
    """Return {doi: citation_count} extracted from Scholar HTML."""
    rows = re.findall(r'<tr class="gsc_a_tr">(.*?)</tr>', html, re.DOTALL)
    counts: dict[str, int] = {}
    for row in rows:
        m_title = re.search(r'class="gsc_a_at"[^>]*>([^<]+)<', row)
        if not m_title:
            continue
        title = m_title.group(1).strip().lower()
        m_count = re.search(r'class="gsc_a_ac[^"]*"[^>]*>(\d*)</a>', row)
        count = int(m_count.group(1)) if (m_count and m_count.group(1)) else 0
        for needle, doi in TITLE_TO_DOI.items():
            if needle in title:
                # Take the max if a paper appears twice (preprint + published)
                counts[doi] = max(counts.get(doi, 0), count)
                break
    return counts


def main() -> int:
    try:
        html = fetch_html()
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: fetch failed: {exc}", file=sys.stderr)
        return 1

    counts = parse_counts(html)
    if not counts:
        print("ERROR: no publications matched (HTML structure may have changed)",
              file=sys.stderr)
        return 1

    payload = {
        "updated": dt.date.today().isoformat(),
        "source": "Google Scholar",
        "total": sum(counts.values()),
        "counts": counts,
    }

    out = Path(__file__).resolve().parent.parent / "citations.json"
    out.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"Wrote {out}: {payload}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
