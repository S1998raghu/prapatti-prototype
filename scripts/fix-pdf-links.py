#!/usr/bin/env python3
"""Repoint or remove PDF/MP3 links in prapatti-hugo/data that don't exist in R2.

The old site's PHP has typos in links (double slashes, misspelt names, wrong folders),
so run this after the convert-* scripts:

    python3 scripts/fix-pdf-links.py            # report only
    python3 scripts/fix-pdf-links.py --apply    # rewrite the data files

A missing link is repointed when exactly one R2 file matches it (same path after fixing
slashes/case, same file name in the same language folder, a "_ds" variant, or a name at most
2 letters different); otherwise the link is removed.
"""

import glob
import json
import os
import re
import subprocess
import sys
from pathlib import Path

PROXY = "https://prapatti-pdf-proxy.sumedharaghu.workers.dev/"
DATA_DIR = Path(__file__).parent.parent / "prapatti-hugo" / "data"


def r2_files():
    out = subprocess.run(["rclone", "lsf", "-R", "--files-only", "r2:prapatti-files"],
                         capture_output=True, text=True, check=True).stdout
    return {line.strip() for line in out.splitlines() if line.strip()}


def edit_distance(a, b, limit=2):
    # Levenshtein with early exit; returns limit + 1 when over the limit
    if abs(len(a) - len(b)) > limit:
        return limit + 1
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i] + [0] * len(b)
        for j, cb in enumerate(b, 1):
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb))
        if min(cur) > limit:
            return limit + 1
        prev = cur
    return prev[-1]


def resolve(path, files, lower, by_dir_name):
    p = re.sub(r"/+", "/", path).replace("slokas/kannad/", "slokas/kannada/")
    p = re.sub(r"Skandha_0_(\d\d)riimad", r"Skandha_\1/sriimad", p)  # stotras.php typo
    if p in files:
        return p
    if p.lower() in lower:
        return lower[p.lower()]
    parts = p.split("/")
    lang = parts[1] if len(parts) > 2 else ""
    name = parts[-1].lower()
    same_name = [f for f in by_dir_name.get(name, []) if f.split("/")[1] == lang]
    if len(same_name) == 1:
        return same_name[0]
    ds = [f for f in by_dir_name.get(name[:-4] + "_ds" + name[-4:], []) if f.split("/")[1] == lang]
    if len(ds) == 1:
        return ds[0]
    folder = os.path.dirname(p)
    close = sorted((edit_distance(name, os.path.basename(f).lower()), f) for f in files if os.path.dirname(f) == folder)
    close = [c for c in close if c[0] <= 2]
    # Take the nearest name, but only when it is strictly nearer than the runner-up
    if close and (len(close) == 1 or close[0][0] < close[1][0]):
        return close[0][1]
    return None


files = r2_files()
lower = {f.lower(): f for f in files}
by_dir_name = {}
for f in files:
    by_dir_name.setdefault(os.path.basename(f).lower(), []).append(f)

decisions = {}
apply = "--apply" in sys.argv
fixed = removed = 0
for path in sorted(glob.glob(str(DATA_DIR / "**" / "*.json"), recursive=True)):
    text = Path(path).read_text(encoding="utf-8")
    data = json.loads(text)
    changed = False

    def walk(node):
        global fixed, removed
        nonlocal_changed = False
        if isinstance(node, list):
            return any([walk(x) for x in node])
        if not isinstance(node, dict):
            return False
        links = node.get("links")
        if isinstance(links, dict):
            for script, url in list(links.items()):
                if not isinstance(url, str) or not url.startswith(PROXY):
                    continue
                key = url[len(PROXY):]
                if key in files:
                    continue
                if key not in decisions:
                    decisions[key] = resolve(key, files, lower, by_dir_name)
                target = decisions[key]
                if target:
                    links[script] = PROXY + target
                    fixed += 1
                else:
                    del links[script]
                    removed += 1
                nonlocal_changed = True
        return any([walk(v) for v in node.values() if isinstance(v, (list, dict))]) or nonlocal_changed

    if walk(data) and apply:
        Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2) + ("\n" if text.endswith("\n") else ""),
                              encoding="utf-8")

for key, target in sorted(decisions.items()):
    print(f"{'FIX ' if target else 'DROP'}  {key}" + (f"  ->  {target}" if target else ""))
print(f"\n{len(decisions)} broken files: {fixed} links repointed, {removed} removed"
      + ("" if apply else "  (report only; use --apply to write)"))
