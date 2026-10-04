#!/usr/bin/env python3
"""Build stotras_index.json directly from stotras.php — more complete than category JSONs."""

import json
import os
import re
from pathlib import Path

SRC_DIR = Path(os.environ.get("PRAPATTI_SRC", "/Users/sumedharaghu/Desktop/prapatti-backup"))
PHP_FILE = SRC_DIR / "stotras.php"
OUT_FILE = Path("/Users/sumedharaghu/prapatti-prototype/prapatti-hugo/data/stotras_index.json")
PROXY = "https://prapatti-pdf-proxy.sumedharaghu.workers.dev"

SCRIPT_MAP = {
    "english": "roman",
    "kannada": "kannada",
    "bengali": "bengali",
    "malayalam": "malayalam",
    "sanskrit": "devanagari",
    "telugu": "telugu",
    "tamil": "tamil",
    "grantha": "grantha",
}

content = PHP_FILE.read_text(encoding="utf-8", errors="ignore")

# Split into rows
rows = re.split(r"<tr[^>]*>", content, flags=re.IGNORECASE)

stotras = []
skipped = []

for row in rows:
    # Extract all <td> contents
    tds = re.findall(r"<td[^>]*>(.*?)</td>", row, re.DOTALL | re.IGNORECASE)
    if len(tds) < 9:
        continue

    name = re.sub(r"<[^>]+>", "", tds[0]).strip()
    author = re.sub(r"<[^>]+>", "", tds[1]).strip()

    # Skip header row and empty rows
    if not name or name in ("Stotra Name", "Author/Source/Category"):
        continue

    # Extract PDF links (tds[3] = roman, [4]=kannada, [5]=bengali, [6]=malayalam,
    #                      [7]=devanagari, [8]=telugu, [9]=tamil, [10]=grantha)
    script_tds = tds[3:11]
    script_names = ["english", "kannada", "bengali", "malayalam", "sanskrit", "telugu", "tamil", "grantha"]

    links = {}
    is_category_link = False

    for i, td in enumerate(script_tds):
        # Find href
        href_match = re.search(r'href=["\']([^"\']+)["\']', td, re.IGNORECASE)
        if not href_match:
            continue
        href = href_match.group(1)

        if "/slokas/" in href and href.endswith(".pdf"):
            # Direct PDF — rewrite to proxy URL
            path = re.sub(r".*/slokas/", "/slokas/", href)
            links[SCRIPT_MAP[script_names[i]]] = PROXY + path
        elif "/categories/" in href:
            is_category_link = True
            # Store category slug for reference
            slug = re.search(r"/categories/([^.]+)\.php", href)
            if slug:
                links[SCRIPT_MAP[script_names[i]]] = f"/categories/{slug.group(1)}/"

    if not links:
        skipped.append(name)
        continue

    # Extract tags from last <td> (index 10 or 11)
    tags = ""
    for td in tds[10:]:
        t = re.sub(r"<[^>]+>", "", td).strip()
        if t and len(t) > 3:
            tags = t
            break

    entry = {
        "name": name,
        "author": author,
        "category": "general",
        "tags": tags,
        "links": links,
    }
    stotras.append(entry)

# Try to preserve category info from existing index
existing_path = OUT_FILE
if existing_path.exists():
    existing = json.loads(existing_path.read_text())
    # Match by name+author (names repeat across authors), then by PDF URL (stotras
    # get renamed), then by name alone
    existing_exact = {(e["name"].lower(), e.get("author", "").lower()): e for e in existing}
    existing_by_url = {u: e for e in existing for u in e.get("links", {}).values() if u.endswith(".pdf")}
    existing_map = {e["name"].lower(): e for e in existing}
    for s in stotras:
        prev = (existing_exact.get((s["name"].lower(), s["author"].lower()))
                or next((existing_by_url[u] for u in s["links"].values() if u in existing_by_url), None)
                or existing_map.get(s["name"].lower()))
        if prev:
            # Keep links added outside stotras.php (e.g. audio)
            for script, url in prev.get("links", {}).items():
                s["links"].setdefault(script, url)
            s["category"] = prev.get("category", "general")
            # Keep previously enriched tags, adding any new words from the PHP source
            old_tags = prev.get("tags", "")
            extra = [w for w in s["tags"].split() if w not in old_tags.split()]
            s["tags"] = " ".join([old_tags] + extra).strip()

stotras.sort(key=lambda x: x["name"].lower())
OUT_FILE.write_text(json.dumps(stotras, ensure_ascii=False, indent=2))

print(f"Written {len(stotras)} stotras to stotras_index.json")
print(f"Skipped {len(skipped)} (no links): {skipped[:10]}")
