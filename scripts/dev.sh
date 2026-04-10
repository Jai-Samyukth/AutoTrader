#!/usr/bin/bash
# Development workflow helper

set -e

show_help() {
    echo "AutoTrader Development Helper"
    echo ""
    echo "Usage: bash scripts/dev.sh [command]"
    echo ""
    echo "Commands:"
    echo "  setup       - Initial setup (install + validate)"
    echo "  test        - Run single test cycle"
    echo "  run         - Run continuous mode"
    echo "  check       - Run all checks (format + lint + test)"
    echo "  logs        - View logs (follow mode)"
    echo "  status      - Show current configuration"
    echo "  clean       - Clean cache and artifacts"
    echo "  help        - Show this help message"
    echo ""
}

show_status() {
    echo "📊 AutoTrader Status"
    echo ""
    
    if [ -f .env ]; then
        set -a
        source .env
        set +a
        
        echo "Configuration:"
        echo "  LLM Provider: ${LLM_PROVIDER:-not set}"
        echo "  Symbols: ${SYMBOLS:-not set}"
        echo "  Paper Trading: ${PAPER_TRADING_MODE:-true}"
        echo "  Max Risk: ${MAX_RISK_PER_TRADE_PCT:-1.0}%"
        echo "  Confidence Threshold: ${CONFIDENCE_THRESHOLD:-0.75}"
        echo ""
        
        if [ -f logs/trader_ai.log ]; then
            echo "Recent Activity:"
            echo "  Last 5 decisions:"
            grep "Decision:" logs/trader_ai.log | tail -n 5 | sed 's/^/    /'
        fi
    else
        echo "❌ .env file not found"
        echo "Run: bash scripts/dev.sh setup"
    fi
}

case "${1:-help}" in
    setup)
        echo "🚀 Setting up AutoTrader..."
        bash scripts/install.sh
        bash scripts/validate_env.sh
        ;;
    test)
        echo "🧪 Running test cycle..."
        bash scripts/run_once.sh
        ;;
    run)
        echo "🤖 Starting continuous mode..."
        bash scripts/run.sh
        ;;
    check)
        echo "✅ Running all checks..."
        bash scripts/check.sh
        ;;
    logs)
        echo "📋 Following logs..."
        bash scripts/logs.sh follow
        ;;
    status)
        show_status
        ;;
    clean)
        echo "🧹 Cleaning..."
        bash scripts/clean.sh
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "❌ Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
