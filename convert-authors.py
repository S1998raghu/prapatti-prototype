#!/usr/bin/env python3
"""Build author pages from already-converted category JSON data."""

import json, re
from pathlib import Path
from collections import defaultdict

HUGO_DIR = Path("/Users/sumedharaghu/prapatti-prototype/prapatti-hugo")
CAT_DATA_DIR = HUGO_DIR / "data" / "categories"
AUTHOR_DATA_DIR = HUGO_DIR / "data" / "authors"
AUTHOR_CONTENT_DIR = HUGO_DIR / "content" / "authors"

AUTHOR_DATA_DIR.mkdir(parents=True, exist_ok=True)
AUTHOR_CONTENT_DIR.mkdir(parents=True, exist_ok=True)

def slugify(name):
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')

# Collect all stotras grouped by author across all categories
authors = defaultdict(list)

for cat_file in sorted(CAT_DATA_DIR.glob("*.json")):
    category = cat_file.stem
    stotras = json.loads(cat_file.read_text())
    for stotra in stotras:
        author = stotra.get("author", "").strip()
        if not author:
            author = "Unknown"
        authors[author].append({
            "name": stotra["name"],
            "category": category,
            "links": stotra.get("links", {})
        })

print(f"Found {len(authors)} unique authors")

for author, stotras in sorted(authors.items()):
    slug = slugify(author)
    if not slug:
        continue

    # Write data file
    data_file = AUTHOR_DATA_DIR / f"{slug}.json"
    data_file.write_text(json.dumps(stotras, ensure_ascii=False, indent=2))

    # Write content file
    content_file = AUTHOR_CONTENT_DIR / f"{slug}.md"
    content_file.write_text(f"""---
title: "{author}"
slug: "{slug}"
layout: "author"
---
""")

    print(f"  {author} ({len(stotras)} stotras) → {slug}")

# Write index of all authors for the authors list page
author_index = [
    {"name": author, "slug": slugify(author), "count": len(stotras)}
    for author, stotras in sorted(authors.items())
    if slugify(author)
]
(HUGO_DIR / "data" / "authors_index.json").write_text(
    json.dumps(author_index, ensure_ascii=False, indent=2)
)

print(f"\nDone. {len(author_index)} authors written.")
