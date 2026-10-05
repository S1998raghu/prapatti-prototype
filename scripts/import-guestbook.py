#!/usr/bin/env python3
"""Import the old site's guestbook_YYYY.json files into the D1 guestbook database.

Usage:
    PRAPATTI_SRC=~/Desktop/prapatti-php-2026-10 python3 scripts/import-guestbook.py          # writes SQL only
    PRAPATTI_SRC=~/Desktop/prapatti-php-2026-10 python3 scripts/import-guestbook.py --apply  # also runs it on D1

Safe to re-run: an entry is skipped if one with the same author and message already exists.
Timestamps are normalised to ISO 8601 (what the worker writes for new entries) so the
guestbook can be sorted by date. Entries marked "pending" in the old files stay unapproved.
"""

import html
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SRC_DIR = Path(os.environ.get("PRAPATTI_SRC", "/Users/sumedharaghu/Desktop/prapatti-backup")).expanduser()
OUT_FILE = Path(__file__).parent / "guestbook-import.sql"
DB = "prapatti-guestbook"

FORMATS = [
    "%A, %B %d, %Y, at %H:%M:%S UTC",  # Monday, December 27, 2004, at 17:22:30 UTC
    "%A, %B %d, %Y at %H:%M:%S UTC",   # Thursday, December 31, 2020 at 20:50:10 UTC
    "%B %d, %Y, %I:%M %p",             # September 30, 2026, 3:48 pm
]


def to_iso(ts):
    ts = re.sub(r"\s+", " ", str(ts)).strip()
    for fmt in FORMATS:
        try:
            return datetime.strptime(ts, fmt).replace(tzinfo=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
        except ValueError:
            pass
    raise ValueError(f"Unrecognised timestamp: {ts!r}")


def clean(s):
    # Old entries are stored as HTML (<br/>, &amp;, Tamil as &#3021; ...); the new page shows plain text
    s = re.sub(r"<\s*br\s*/?\s*>", "\n", str(s or ""), flags=re.IGNORECASE)
    s = re.sub(r"<[^>]+>", "", s)
    return html.unescape(s).strip()


def sql_str(s):
    return "'" + clean(s).replace("'", "''") + "'"


rows = []
for f in sorted((SRC_DIR / "guestbook").glob("guestbook_[0-9][0-9][0-9][0-9].json")):
    for e in json.loads(f.read_text(encoding="utf-8")):
        if not clean(e.get("author")) or not clean(e.get("message")):
            continue
        rows.append((to_iso(e["timestamp"]), e, 0 if e.get("status") == "pending" else 1))

rows.sort(key=lambda r: r[0])  # oldest first

statements = []
for ts, e, approved in rows:
    author, message = sql_str(e.get("author")), sql_str(e.get("message"))
    statements.append(
        "INSERT INTO entries (author, email, location, message, timestamp, approved) "
        f"SELECT {author}, {sql_str(e.get('email'))}, {sql_str(e.get('location'))}, {message}, '{ts}', {approved} "
        f"WHERE NOT EXISTS (SELECT 1 FROM entries WHERE author = {author} AND message = {message});"
    )

OUT_FILE.write_text("\n".join(statements) + "\n", encoding="utf-8")
print(f"{len(rows)} entries ({rows[0][0][:10]} to {rows[-1][0][:10]}), "
      f"{sum(1 for r in rows if not r[2])} pending -> {OUT_FILE}")

if "--apply" in sys.argv:
    result = subprocess.run(["wrangler", "d1", "execute", DB, "--remote", "--file", str(OUT_FILE)],
                            cwd=Path(__file__).parent.parent / "workers" / "guestbook")
    sys.exit(result.returncode)
