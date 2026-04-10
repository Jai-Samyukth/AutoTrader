#!/usr/bin/bash
# Lint code without fixing

set -e

echo "🔍 Running Ruff linter (check only)..."
uv run ruff check src/ tests/

echo ""
echo "✅ Linting complete!"
