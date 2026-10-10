#!/usr/bin/env python3
"""Add a new stotra to the site after its PDFs are uploaded to R2 (no A2 involved).

    python3 scripts/add-stotra.py hayagriivastuti \
        --name "Hayagriiva Stuti" --author "Vedaanta Desikan" \
        --update "Hayagriiva Stuti by Swami Desikan, available in all scripts."

Looks up slokas/<script>/<file>.pdf (and slokas/mp3/<file>.mp3) in R2, then adds the
stotra to the All Stotras list and, with --update, a row at the top of Latest Updates.
Running it again for the same name replaces the earlier entry. --dry-run prints only.

Do not run build-stotras-from-php.py after this: it rebuilds the list from A2's
stotras.php and would drop stotras added here.
"""

import argparse
import json
import re
import subprocess
from datetime import date
from pathlib import Path

PROXY = "https://prapatti-pdf-proxy.sumedharaghu.workers.dev/"
DATA_DIR = Path(__file__).parent.parent / "prapatti-hugo" / "data"
# R2 folder -> column on the site, in the site's column order
FOLDERS = {"english": "roman", "kannada": "kannada", "bengali": "bengali", "malayalam": "malayalam",
           "sanskrit": "devanagari", "telugu": "telugu", "tamil": "tamil", "grantha": "grantha"}

ap = argparse.ArgumentParser()
ap.add_argument("file", help="PDF file name without .pdf, e.g. hayagriivastuti")
ap.add_argument("--name", required=True)
ap.add_argument("--author", default="")
ap.add_argument("--tags", default="", help="extra search words (the name is always searchable)")
ap.add_argument("--update", help="description for a new Latest Updates row")
ap.add_argument("--date", default=date.today().strftime("%b %d %Y"), help='e.g. "Oct 10 2026"')
ap.add_argument("--dry-run", action="store_true")
args = ap.parse_args()

stem = re.sub(r"\.pdf$", "", args.file)
out = subprocess.run(["rclone", "lsf", "-R", "--files-only", "r2:prapatti-files/slokas",
                      "--include", f"/*/{stem}.pdf", "--include", f"/mp3/{stem}.mp3"],
                     capture_output=True, text=True, check=True).stdout
found = {line.split("/")[0] for line in out.split()}

links = {}
if "mp3" in found:
    links["audio"] = f"{PROXY}slokas/mp3/{stem}.mp3"
for folder, script in FOLDERS.items():
    if folder in found:
        links[script] = f"{PROXY}slokas/{folder}/{stem}.pdf"
if not any(k != "audio" for k in links):
    raise SystemExit(f"No slokas/<script>/{stem}.pdf in R2 - upload the PDFs first.")

stotra = {"name": args.name, "author": args.author, "category": "general",
          "tags": " ".join([args.name.lower(), args.author.lower(), args.tags.lower()]).strip(),
          "links": links}
print("Scripts found:", ", ".join(k for k in links))
print(json.dumps(stotra, ensure_ascii=False, indent=2))

index_file = DATA_DIR / "stotras_index.json"
stotras = [s for s in json.loads(index_file.read_text(encoding="utf-8")) if s["name"] != args.name]
stotras.append(stotra)
stotras.sort(key=lambda s: s["name"].lower())

updates_file = DATA_DIR / "updates.json"
updates = json.loads(updates_file.read_text(encoding="utf-8"))
if args.update:
    updates = [u for u in updates if u["description"] != args.update]
    updates.insert(0, {"date": args.date, "description": args.update, "links": links})
    print(f'Latest Updates row dated {args.date}')

if args.dry_run:
    print("(dry run - nothing written)")
else:
    # newline="\n" keeps Unix line endings on Windows too, so git sees only the added entries
    with open(index_file, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(stotras, ensure_ascii=False, indent=2))
    with open(updates_file, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(updates, ensure_ascii=False, indent=2) + "\n")
    print(f"Written. {len(stotras)} stotras. Preview with: cd prapatti-hugo; hugo server")
