#!/bin/bash
# Replaces /slokas/ PDF paths with R2 URL in all content and data files

NEW_URL="https://prapatti-pdf-proxy.sumedharaghu.workers.dev"
HUGO_DIR="$(dirname "$0")/prapatti-hugo"

find "$HUGO_DIR/content" "$HUGO_DIR/data" -name "*.md" -o -name "*.json" | while read -r file; do
  if grep -qE 'https?://files\.prapatti\.com|"/slokas/' "$file"; then
    echo "Updating $file ..."
    sed -i '' "s|https://files\.prapatti\.com|$NEW_URL|g" "$file"
    sed -i '' "s|\"\/slokas\/|\"$NEW_URL\/slokas\/|g" "$file"
  fi
done

echo "Done."
