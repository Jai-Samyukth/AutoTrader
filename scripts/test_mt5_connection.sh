#!/bin/bash
# Test MT5 Direct Connection
# This script tests the direct Python MT5 connection

set -e

echo "============================================================"
echo "Testing MT5 Direct Connection"
echo "============================================================"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "ERROR: .env file not found"
    echo ""
    echo "Please create .env file with your MT5 credentials:"
    echo "  cp .env.example .env"
    echo "  nano .env"
    exit 1
fi

# Run Python test
python scripts/test_mt5_direct.py

echo ""
echo "============================================================"
echo "Connection test complete!"
echo "============================================================"
