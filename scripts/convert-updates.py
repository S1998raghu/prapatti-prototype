#!/usr/bin/env python3
"""Add new rows from index.php's updates table to data/updates.json (newest first)."""

import json
import os
import re
from datetime import datetime
from pathlib import Path

SRC_DIR = Path(os.environ.get("PRAPATTI_SRC", "/Users/sumedharaghu/Desktop/prapatti-backup"))
PHP_FILE = SRC_DIR / "index.php"
OUT_FILE = Path(__file__).parent.parent / "prapatti-hugo" / "data" / "updates.json"
PROXY = "https://prapatti-pdf-proxy.sumedharaghu.workers.dev"

SCRIPT_MAP = {
    "pdf-icon.png": "roman",
    "pdf_kannada.png": "kannada",
    "pdf_bengali.png": "bengali",
    "pdf_malayalam.png": "malayalam",
    "pdf_sanskrit.png": "devanagari",
    "pdf_telugu.png": "telugu",
    "pdf_tamil.png": "tamil",
    "pdf_grantha.png": "grantha",
}
COLUMN_SCRIPTS = ["roman", "kannada", "bengali", "malayalam", "devanagari", "telugu", "tamil", "grantha"]


def clean(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html)).strip()


def normalize_date(d):
    # "Sept 29 2026" / "July 7 2026" -> "Sep 29 2026" / "Jul 07 2026"
    m = re.match(r"([A-Za-z]+)\s+(\d{1,2}),?\s+(\d{4})", d)
    return f"{m.group(1)[:3]} {int(m.group(2)):02d} {m.group(3)}" if m else d


def convert_link(href):
    href = re.sub(r"^https?://(www\.)?prapatti\.com", "", href)
    if href.startswith("/slokas/") or href.startswith("/articles/") or href.startswith("/announcements/"):
        return PROXY + href
    cat = re.match(r"/?categories/([^/]+)\.php$", href)
    if cat:
        return f"/categories/{cat.group(1)}/"
    return href


content = PHP_FILE.read_text(encoding="utf-8", errors="ignore")
table = content.split("PLEASE ADD NEW / LATEST Text UPDATES BELOW THIS LINE", 1)[-1]

parsed = []
for row in re.findall(r"<tr[^>]*>(.*?)</tr>", table, re.DOTALL | re.IGNORECASE):
    tds = re.findall(r"<td[^>]*>(.*?)</td>", row, re.DOTALL | re.IGNORECASE)
    if len(tds) < 3 or not re.match(r"[A-Za-z]+\s+\d{1,2},?\s+\d{4}", clean(tds[0])):
        continue
    links = {}
    for i, td in enumerate(tds[2:]):
        href = re.search(r'href=["\']([^"\']+)["\']', td, re.IGNORECASE)
        if not href:
            continue
        img = re.search(r'src=["\'][^"\']*?([^/]+\.png)["\']', td, re.IGNORECASE)
        if href.group(1).endswith(".mp3"):
            script = "audio"
        else:
            script = SCRIPT_MAP.get(img.group(1).lower()) if img else None
            # Generic icons (e.g. filecollection.png): script comes from column position
            if not script and 1 <= i <= len(COLUMN_SCRIPTS):
                script = COLUMN_SCRIPTS[i - 1]
        if script:
            links[script] = convert_link(href.group(1))
    parsed.append({"date": normalize_date(clean(tds[0])), "description": clean(tds[1]), "links": links})

existing = json.loads(OUT_FILE.read_text())
for e in existing:
    e["date"] = normalize_date(e["date"])
    e["links"] = {k: convert_link(v) for k, v in e.get("links", {}).items()}

def same_update(p, e):
    # Older entries were saved with shortened descriptions ("Srii X." vs "Srii X, available in ...")
    a, b = p["description"].lower(), e["description"].lower().rstrip(".")
    return p["date"] == e["date"] and (a.startswith(b) or a[:40] == b[:40])


new = [p for p in parsed if not any(same_update(p, e) for e in existing)]

merged = sorted(new + existing, key=lambda e: datetime.strptime(e["date"], "%b %d %Y"), reverse=True)
OUT_FILE.write_text(json.dumps(merged, ensure_ascii=False, indent=2) + "\n")
print(f"Added {len(new)} new updates ({len(new) + len(existing)} total)")
for p in new:
    print(f"  {p['date']}  {p['description'][:70]}")
