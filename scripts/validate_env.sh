#!/usr/bin/bash
# Validate environment configuration

set -e

echo "🔍 Validating environment configuration..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found"
    echo "Run: cp .env.example .env"
    exit 1
fi

# Source .env
set -a
source .env
set +a

# Check required variables
ERRORS=0

check_var() {
    local var_name=$1
    local var_value=${!var_name}
    
    if [ -z "$var_value" ]; then
        echo "❌ $var_name is not set"
        ERRORS=$((ERRORS + 1))
    else
        echo "✅ $var_name is set"
    fi
}

echo "Checking LLM configuration..."
if [ "$LLM_PROVIDER" = "anthropic" ]; then
    check_var "ANTHROPIC_API_KEY"
elif [ "$LLM_PROVIDER" = "openai" ]; then
    check_var "OPENAI_API_KEY"
else
    echo "❌ LLM_PROVIDER must be 'anthropic' or 'openai'"
    ERRORS=$((ERRORS + 1))
fi

echo ""
echo "Checking MT5 configuration..."
check_var "MT5_BASE_URL"

echo ""
echo "Checking trading configuration..."
check_var "SYMBOLS"
check_var "TIMEFRAMES"

echo ""
echo "Checking risk management..."
check_var "MAX_RISK_PER_TRADE_PCT"
check_var "CONFIDENCE_THRESHOLD"

echo ""
if [ $ERRORS -eq 0 ]; then
    echo "✅ Environment configuration is valid!"
    
    # Show current mode
    echo ""
    echo "Current configuration:"
    echo "  LLM Provider: $LLM_PROVIDER"
    echo "  Symbols: $SYMBOLS"
    echo "  Paper Trading: ${PAPER_TRADING_MODE:-true}"
    echo "  Max Risk: ${MAX_RISK_PER_TRADE_PCT}%"
else
    echo "❌ Found $ERRORS configuration error(s)"
    exit 1
fi
