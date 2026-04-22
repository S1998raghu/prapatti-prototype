#!/usr/bin/env python3
"""Build a combined stotras index JSON from all category data."""

import json
from pathlib import Path

HUGO_DIR = Path("/Users/sumedharaghu/prapatti-prototype/prapatti-hugo")
CAT_DATA_DIR = HUGO_DIR / "data" / "categories"

all_stotras = []

for cat_file in sorted(CAT_DATA_DIR.glob("*.json")):
    category = cat_file.stem
    stotras = json.loads(cat_file.read_text())
    for s in stotras:
        all_stotras.append({
            "name": s.get("name", ""),
            "author": s.get("author", ""),
            "category": category,
            "links": s.get("links", {})
        })

# Deduplicate by name+author
seen = set()
unique = []
for s in all_stotras:
    key = (s["name"].lower().strip(), s["author"].lower().strip())
    if key not in seen:
        seen.add(key)
        unique.append(s)

unique.sort(key=lambda x: x["name"].lower())

out = HUGO_DIR / "data" / "stotras_index.json"
out.write_text(json.dumps(unique, ensure_ascii=False, indent=2))
print(f"Written {len(unique)} unique stotras to data/stotras_index.json")
