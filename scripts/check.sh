#!/usr/bin/bash
# Run all checks (format, lint, test)

set -e

echo "🔍 Running all checks..."
echo ""

echo "1️⃣ Formatting code..."
bash scripts/format.sh

echo ""
echo "2️⃣ Linting code..."
bash scripts/lint.sh

echo ""
echo "3️⃣ Running tests..."
bash scripts/test.sh

echo ""
echo "✅ All checks passed!"
