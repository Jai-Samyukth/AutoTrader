#!/usr/bin/bash
# Clean build artifacts and cache

set -e

echo "🧹 Cleaning build artifacts..."

# Remove Python cache
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true

# Remove pytest cache
rm -rf .pytest_cache 2>/dev/null || true

# Remove ruff cache
rm -rf .ruff_cache 2>/dev/null || true

# Remove build directories
rm -rf build dist 2>/dev/null || true

echo "✅ Cleanup complete!"
