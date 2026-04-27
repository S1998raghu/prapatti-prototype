#!/bin/bash
BUCKET="prapatti-files"
SOURCE_DIR="/Users/sumedharaghu/Desktop/prapatti-backup/slokas/mp3"

find "$SOURCE_DIR" -name "*.mp3" | while read -r file; do
  fname=$(basename "$file")
  relative="slokas/mp3/$fname"

  if wrangler r2 object get "$BUCKET/$relative" --remote --pipe > /dev/null 2>&1; then
    echo "Skipping $relative (already exists)"
  else
    echo "Uploading $relative ..."
    wrangler r2 object put "$BUCKET/$relative" --file="$file" --content-type="audio/mpeg" --remote
  fi
done

echo "Done."
