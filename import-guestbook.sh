#!/bin/bash
# Import historical guestbook JSON files into D1

GUESTBOOK_DIR="/Users/sumedharaghu/Desktop/prapatti-backup/guestbook"
DB="prapatti-guestbook"

for f in "$GUESTBOOK_DIR"/guestbook_*.json; do
  year=$(basename "$f" .json | sed 's/guestbook_//')
  echo "Importing $year..."

  python3 - "$f" <<'EOF'
import json, sys, subprocess, tempfile, os

path = sys.argv[1]
entries = json.loads(open(path).read())

sql_lines = []
for e in entries:
    def esc(s):
        return str(s or '').replace("'", "''")
    sql_lines.append(
        f"INSERT INTO entries (author, email, location, message, timestamp, approved) VALUES "
        f"('{esc(e.get('author',''))}', '{esc(e.get('email',''))}', '{esc(e.get('location',''))}', "
        f"'{esc(e.get('message',''))}', '{esc(e.get('timestamp',''))}', 1);"
    )

sql = '\n'.join(sql_lines)
with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as tmp:
    tmp.write(sql)
    tmp_path = tmp.name

result = subprocess.run(
    ['wrangler', 'd1', 'execute', 'prapatti-guestbook', '--file', tmp_path, '--remote'],
    capture_output=True, text=True
)
os.unlink(tmp_path)
print(f"  {len(sql_lines)} entries — {'OK' if result.returncode == 0 else 'FAILED'}")
if result.returncode != 0:
    print(result.stderr[:300])
EOF

done

echo "Done."
