#!/usr/bin/bash
# Run AutoTrader in continuous mode

set -e

echo "🤖 Starting AutoTrader in continuous mode..."
echo "⚠️  Press Ctrl+C to stop"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found"
    echo "Run: cp .env.example .env"
    exit 1
fi

# Check if paper trading mode
if grep -q "PAPER_TRADING_MODE=false" .env; then
    echo "⚠️  WARNING: LIVE TRADING MODE ENABLED"
    echo "Press Ctrl+C within 5 seconds to cancel..."
    sleep 5
fi

uv run trade-bot
