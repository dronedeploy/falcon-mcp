#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "=== Step 1: Generate module documentation ==="
cd "$PROJECT_ROOT"
uv run python scripts/generate_module_docs.py

echo "=== Step 2: Copy changelog ==="
{
  echo '---'
  echo 'title: Changelog'
  echo 'description: Release history for the Falcon MCP Server.'
  echo '---'
  echo ''
  cat CHANGELOG.md
} > docs-site/src/content/docs/changelog.md

echo "=== Step 3: Build Starlight site ==="
cd "$PROJECT_ROOT/docs-site"
npm ci
npm run build

echo "=== Done ==="
echo "Output: docs-site/dist/"
