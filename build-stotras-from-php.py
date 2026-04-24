#!/usr/bin/env python3
"""Build stotras_index.json directly from stotras.php — more complete than category JSONs."""

import json
import re
from pathlib import Path

PHP_FILE = Path("/Users/sumedharaghu/Desktop/prapatti-backup/stotras.php")
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
    existing_map = {e["name"].lower(): e.get("category", "general") for e in existing}
    for s in stotras:
        cat = existing_map.get(s["name"].lower())
        if cat:
            s["category"] = cat

stotras.sort(key=lambda x: x["name"].lower())
OUT_FILE.write_text(json.dumps(stotras, ensure_ascii=False, indent=2))

print(f"Written {len(stotras)} stotras to stotras_index.json")
print(f"Skipped {len(skipped)} (no links): {skipped[:10]}")
