#!/usr/bin/bash
# Pre-commit checks and requirements export

set -e

echo "📦 Exporting requirements..."
uv export --no-hashes > requirements.txt
uv export --no-hashes --only-group dev > requirements.dev.txt

echo "🔍 Running linter..."
uv run ruff check src/ tests/

echo "🧪 Running tests..."
uv run pytest tests/ -v

echo "✅ Pre-commit checks passed!"

