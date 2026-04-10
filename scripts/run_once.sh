#!/usr/bin/bash
# Run a single analysis cycle (test mode)

set -e

echo "🤖 Running AutoTrader in test mode (single cycle)..."
echo ""

uv run trade-bot --once

echo ""
echo "✅ Test cycle complete!"
echo "📊 Check logs/trader_ai.log for details"
