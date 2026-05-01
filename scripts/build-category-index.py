#!/usr/bin/env python3
"""Build category index JSON with titles and stotra counts."""

import json
from pathlib import Path

HUGO_DIR = Path("/Users/sumedharaghu/prapatti-prototype/prapatti-hugo")
CAT_DATA_DIR = HUGO_DIR / "data" / "categories"
CAT_CONTENT_DIR = HUGO_DIR / "content" / "categories"

index = []
for cat_file in sorted(CAT_DATA_DIR.glob("*.json")):
    slug = cat_file.stem
    stotras = json.loads(cat_file.read_text())
    # Get title from content frontmatter
    content_file = CAT_CONTENT_DIR / f"{slug}.md"
    title = slug.replace("-", " ").title()
    if content_file.exists():
        for line in content_file.read_text().splitlines():
            if line.startswith("title:"):
                title = line.split(":", 1)[1].strip().strip('"')
                break
    index.append({"slug": slug, "title": title, "count": len(stotras)})

out = HUGO_DIR / "data" / "categories_index.json"
out.write_text(json.dumps(index, ensure_ascii=False, indent=2))
print(f"Written {len(index)} categories")
