#!/bin/bash
# Start MetaTrader 5 MCP Server
# This script starts the MT5 MCP server on port 8001

set -e

echo "============================================================"
echo "Starting MetaTrader 5 MCP Server"
echo "============================================================"

# Check if uvx is installed
if ! command -v uvx &> /dev/null; then
    echo "ERROR: uvx is not installed"
    echo ""
    echo "Please install uv first:"
    echo "  Windows (PowerShell): irm https://astral.sh/uv/install.ps1 | iex"
    echo "  macOS/Linux: curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo ""
    echo "Or install via pip: pip install uv"
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "ERROR: .env file not found"
    echo ""
    echo "Please create .env file with your MT5 credentials:"
    echo "  cp .env.example .env"
    echo "  nano .env"
    echo ""
    echo "Required variables:"
    echo "  MT5_LOGIN=your_login_id"
    echo "  MT5_PASSWORD=your_password"
    echo "  MT5_SERVER=your_broker_server"
    exit 1
fi

# Load environment variables
source .env

# Check required variables
if [ -z "$MT5_LOGIN" ] || [ -z "$MT5_PASSWORD" ] || [ -z "$MT5_SERVER" ]; then
    echo "ERROR: Missing MT5 credentials in .env file"
    echo ""
    echo "Please add these to your .env file:"
    echo "  MT5_LOGIN=your_login_id"
    echo "  MT5_PASSWORD=your_password"
    echo "  MT5_SERVER=your_broker_server"
    echo ""
    echo "Example:"
    echo "  MT5_LOGIN=12345678"
    echo "  MT5_PASSWORD=YourPassword123"
    echo "  MT5_SERVER=MetaQuotes-Demo"
    exit 1
fi

echo "MT5 Login: $MT5_LOGIN"
echo "MT5 Server: $MT5_SERVER"
echo "Starting server on http://localhost:8001..."
echo ""
echo "Press Ctrl+C to stop the server"
echo "============================================================"
echo ""

# Start the MT5 MCP server
# The server will connect to MT5 and provide HTTP API on port 8001
uvx metatrader-mcp-server \
    --login "$MT5_LOGIN" \
    --password "$MT5_PASSWORD" \
    --server "$MT5_SERVER" \
    --transport sse \
    --host localhost \
    --port 8001
