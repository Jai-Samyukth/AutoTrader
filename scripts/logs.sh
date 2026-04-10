#!/usr/bin/bash
# View logs with optional filtering

LOG_FILE="logs/trader_ai.log"

if [ ! -f "$LOG_FILE" ]; then
    echo "❌ Log file not found: $LOG_FILE"
    exit 1
fi

# Check for filter argument
if [ $# -eq 0 ]; then
    echo "📋 Showing all logs (last 50 lines)..."
    tail -n 50 "$LOG_FILE"
else
    case "$1" in
        decisions)
            echo "📊 Showing decision logs..."
            grep "Decision:" "$LOG_FILE" | tail -n 20
            ;;
        trades)
            echo "💰 Showing trade execution logs..."
            grep -E "(Trade executed|Order placed)" "$LOG_FILE" | tail -n 20
            ;;
        errors)
            echo "❌ Showing error logs..."
            grep "ERROR" "$LOG_FILE" | tail -n 20
            ;;
        follow)
            echo "📡 Following logs (Ctrl+C to stop)..."
            tail -f "$LOG_FILE"
            ;;
        *)
            echo "Usage: bash scripts/logs.sh [decisions|trades|errors|follow]"
            exit 1
            ;;
    esac
fi
