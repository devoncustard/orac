#!/bin/bash
# Auto-update OrAC docs — run after any code changes
# Usage: ./scripts/update-docs.sh
set -e
cd "$(dirname "$0")/.."
echo "Running mkdocs build..."
mkdocs build 2>&1 | grep -v "WARNING\|fallback"
echo "✓ Docs built to site/"
echo ""
echo "To serve locally: mkdocs serve"
