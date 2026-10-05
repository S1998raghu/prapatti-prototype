#!/usr/bin/env python3
"""Convert PHP category pages to Hugo data + content files."""

import os, re, json
from pathlib import Path

SRC_DIR = Path(os.environ.get("PRAPATTI_SRC", "/Users/sumedharaghu/Desktop/prapatti-backup"))
BACKUP_CATS = SRC_DIR / "categories"
HUGO_DIR = Path("/Users/sumedharaghu/prapatti-prototype/prapatti-hugo")
DATA_DIR = HUGO_DIR / "data" / "categories"
CONTENT_DIR = HUGO_DIR / "content" / "categories"
R2_BASE = "https://prapatti-pdf-proxy.sumedharaghu.workers.dev"

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
# /slokas/<folder>/ names the script reliably; icons are sometimes copy-pasted wrongly
FOLDER_SCRIPTS = {"english": "roman", "kannada": "kannada", "bengali": "bengali", "malayalam": "malayalam",
                  "sanskrit": "devanagari", "telugu": "telugu", "tamil": "tamil", "grantha": "grantha"}

DATA_DIR.mkdir(parents=True, exist_ok=True)
CONTENT_DIR.mkdir(parents=True, exist_ok=True)

php_files = [f for f in BACKUP_CATS.glob("*.php")
             if not f.name.startswith("splevents_") and f.name not in ("Categories.code-workspace",)]

for php_file in sorted(php_files):
    slug = php_file.stem
    content = php_file.read_text(encoding="utf-8", errors="ignore")

    # Extract page title from <h3>
    h3 = re.search(r'<h3[^>]*>(.*?)</h3>', content, re.IGNORECASE)
    title = h3.group(1).strip() if h3 else slug.replace("-", " ").title()

    # Extract table rows — each stotra is a <tr> block
    rows = re.findall(r'<tr>(.*?)</tr>', content, re.DOTALL | re.IGNORECASE)

    stotras = []
    for row in rows:
        tds = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL | re.IGNORECASE)
        if len(tds) < 3:
            continue

        # First td: name, second td: author (sometimes), rest: PDF links
        name_raw = re.sub(r'<[^>]+>', '', tds[0]).strip()
        if not name_raw or 'Search' in name_raw or 'input' in tds[0].lower():
            continue

        # Find author — second td if it has no PDF link
        author = ""
        link_start = 1
        if len(tds) > 1 and 'href' not in tds[1] and 'input' not in tds[1].lower():
            author = re.sub(r'<[^>]+>', '', tds[1]).strip()
            link_start = 2

        links = {}
        for i, td in enumerate(tds[link_start:], start=link_start):
            href = re.search(r'href=["\']([^"\']+\.pdf)["\']', td, re.IGNORECASE)
            # Hub pages (e.g. bhaagavatam.php) link to sub-category pages instead of PDFs
            cat_href = re.search(r'href=["\'][^"\']*/categories/([^"\'/]+)\.php["\']', td, re.IGNORECASE)
            img = re.search(r'src=["\'][^"\']*?([^/]+\.png)["\']', td, re.IGNORECASE)
            if (href or cat_href) and img:
                folder = re.search(r"/slokas/([^/]+)/", href.group(1)) if href else None
                script = (FOLDER_SCRIPTS.get(folder.group(1).lower()) if folder else None) or SCRIPT_MAP.get(img.group(1).lower())
                # Generic collection icon: script comes from column position
                # (name, author, audio, then the 8 script columns)
                if img.group(1).lower() == "filecollection.png" and 3 <= i < 3 + len(COLUMN_SCRIPTS):
                    script = COLUMN_SCRIPTS[i - 3]
                if script and href:
                    path = href.group(1)
                    links[script] = R2_BASE + path if path.startswith("/") else path
                elif script:
                    links[script] = f"/categories/{cat_href.group(1)}/"

        if links:
            stotra = {"name": name_raw}
            if author:
                stotra["author"] = author
            stotra["links"] = links
            stotras.append(stotra)

    if not stotras:
        print(f"SKIP {slug} — no stotras found")
        continue

    # Write data file
    data_file = DATA_DIR / f"{slug}.json"
    data_file.write_text(json.dumps(stotras, ensure_ascii=False, indent=2))

    # Write content file
    content_file = CONTENT_DIR / f"{slug}.md"
    content_file.write_text(f"""---
title: "{title}"
slug: "{slug}"
layout: "category"
---
""")

    print(f"OK {slug} — {len(stotras)} stotras")

print("\nDone.")
