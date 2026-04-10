#!/usr/bin/bash
# Install dependencies and setup environment

set -e

echo "📦 Installing AutoTrader..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ Error: uv is not installed"
    echo "Install it from: https://docs.astral.sh/uv/getting-started/installation/"
    exit 1
fi

# Sync dependencies
echo "📥 Syncing dependencies..."
uv sync

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your API keys"
fi

# Create logs directory
mkdir -p logs

echo ""
echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "  1. Edit .env with your API keys"
echo "  2. Ensure MT5 MCP server is running"
echo "  3. Run: uv run trade-bot --once (test mode)"
echo "  4. Run: uv run trade-bot (continuous mode)"
