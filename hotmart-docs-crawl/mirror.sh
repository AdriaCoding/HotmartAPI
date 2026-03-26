#!/usr/bin/env bash
# Optional: static mirror of Hotmart Developers docs for offline browsing / grep.
# Respect robots.txt and site rate limits; run manually when needed.
#
# Usage (from repo root):
#   mkdir -p docs/hotmart-docs-mirror
#   bash scripts/hotmart-docs-crawl/mirror.sh
#
# Requires: wget

set -euo pipefail

DEST="${HOTMART_DOCS_MIRROR_DEST:-docs/hotmart-docs-mirror}"
mkdir -p "$DEST"

wget \
  --mirror \
  --page-requisites \
  --adjust-extension \
  --convert-links \
  --no-parent \
  --domains developers.hotmart.com \
  --accept-regex '/docs/en/' \
  --wait=1 \
  --random-wait \
  --user-agent='OrganicEcom-docs-crawler/1.0' \
  -P "$DEST" \
  'https://developers.hotmart.com/docs/en/'

echo "Mirror complete under $DEST"
