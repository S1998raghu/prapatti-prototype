#!/usr/bin/env python3
"""
Enrich stotras_index.json tags using Claude API.

For each stotra with thin tags (< 6 words), asks Claude to add semantic tags:
  - Alternate names for the deity / subject
  - Alternate names / spellings for the author / saint
  - Work type (ashtakam, sahasranamam, stotram, prabandham, etc.)

Run once:
    pip install anthropic
    export ANTHROPIC_API_KEY=...
    python3 scripts/enrich_tags.py

Writes enriched data back to prapatti-hugo/data/stotras_index.json in-place.
Dry-run (no writes): python3 scripts/enrich_tags.py --dry-run
"""

import json
import os
import sys
import time
import argparse
from pathlib import Path

import anthropic

DATA_FILE = Path(__file__).parent.parent / "prapatti-hugo" / "data" / "stotras_index.json"
THIN_THRESHOLD = 6   # stotras with fewer tag words get enriched
BATCH_SIZE = 20      # stotras per Claude call (saves API cost)


SYSTEM = """You are an expert in Sanskrit, Tamil, and Srivaishnava literature.
Your task: given a list of stotras (devotional texts), return extra search tags for each one.

Tags should be lowercase, space-separated words (no punctuation, no commas).
Include:
- Alternate transliterations of the stotra name
- Alternate names / epithets for the deity or subject
- Alternate names / spellings for the author or saint (e.g. "andal goda godadevi kothai")
- The type of work (e.g. ashtakam stotram prabandham sahasranamam kavacham mangalam)
- Any well-known associated terms a devotee might search for

Do NOT repeat words already in the existing tags.
Respond ONLY with a JSON array in the same order as input:
[
  {"id": 0, "new_tags": "word1 word2 word3"},
  ...
]"""


def build_prompt(batch):
    lines = []
    for i, s in enumerate(batch):
        lines.append(f'{i}. name="{s["name"]}" author="{s["author"]}" existing_tags="{s.get("tags","")}"')
    return "\n".join(lines)


def enrich_batch(client, batch):
    prompt = build_prompt(batch)
    msg = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2048,
        system=SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )
    text = msg.content[0].text.strip()
    # strip markdown fences if present
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    return json.loads(text)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--all", action="store_true", help="Enrich all stotras, not just thin ones")
    args = parser.parse_args()

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    data = json.loads(DATA_FILE.read_text())

    if args.all:
        targets = list(range(len(data)))
    else:
        targets = [i for i, s in enumerate(data) if len(s.get("tags", "").split()) < THIN_THRESHOLD]

    print(f"Enriching {len(targets)} stotras (dry_run={args.dry_run})")

    updated = 0
    for start in range(0, len(targets), BATCH_SIZE):
        chunk_idxs = targets[start:start + BATCH_SIZE]
        batch = [data[i] for i in chunk_idxs]

        print(f"  batch {start//BATCH_SIZE + 1}: {[s['name'][:40] for s in batch[:3]]} ...")

        try:
            results = enrich_batch(client, batch)
        except Exception as e:
            print(f"  ERROR on batch: {e}")
            time.sleep(2)
            continue

        for r in results:
            idx = chunk_idxs[r["id"]]
            new_tags = r.get("new_tags", "").strip()
            if new_tags:
                existing = data[idx].get("tags", "")
                existing_words = set(existing.split())
                added = [w for w in new_tags.split() if w not in existing_words]
                if added:
                    data[idx]["tags"] = (existing + " " + " ".join(added)).strip()
                    updated += 1

        time.sleep(0.3)  # be gentle with the API

    print(f"Done. {updated} stotras updated.")

    if not args.dry_run:
        DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2))
        print(f"Written to {DATA_FILE}")
    else:
        print("Dry run — no file written.")
        # Show a sample of what would change
        for i in targets[:5]:
            print(f"  {data[i]['name'][:50]} => {data[i].get('tags','')[:80]}")


if __name__ == "__main__":
    main()
