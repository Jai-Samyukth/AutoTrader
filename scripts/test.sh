#!/usr/bin/bash
# Run tests with coverage

set -e

echo "🧪 Running tests..."

# Run pytest with verbose output
uv run pytest tests/ -v --tb=short

echo ""
echo "✅ All tests passed!"
