#!/bin/bash
# Uploads PDFs from prapatti-backup to R2, skipping files that already exist

BUCKET="prapatti-files"
SOURCE_DIR="/Users/sumedharaghu/Desktop/prapatti-backup/slokas"

find "$SOURCE_DIR" -name "*.pdf" | while read -r file; do
  relative="slokas/${file#$SOURCE_DIR/}"

  # Check if object already exists in R2
  if wrangler r2 object get "$BUCKET/$relative" --remote --pipe > /dev/null 2>&1; then
    echo "Skipping $relative (already exists)"
  else
    echo "Uploading $relative ..."
    wrangler r2 object put "$BUCKET/$relative" --file="$file" --content-type="application/pdf" --remote
  fi
done

echo "Done."
