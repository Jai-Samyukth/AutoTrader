#!/usr/bin/bash
# Format and lint code

set -e

echo "🔍 Running Ruff formatter..."
uv run ruff format src/ tests/

echo "🔧 Running Ruff linter with auto-fix..."
uv run ruff check --fix src/ tests/

echo "✅ Code formatting complete!"