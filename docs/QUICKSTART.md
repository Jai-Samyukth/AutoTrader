# Quick Start Guide

## 1. Prerequisites

### Install MetaTrader 5 HTTP MCP Server

The bot communicates with MetaTrader 5 via HTTP API. You need to run an MCP server that exposes MT5 functionality.

**Option A: Use existing MCP server**
- Ensure it's running on `http://localhost:8001/api/v1`
- Endpoints required: `/account`, `/positions`, `/symbol/{symbol}`, `/order/market`

**Option B: Configure custom endpoint**
- Set `MT5_BASE_URL` in `.env` to your server URL

### Get API Keys

**For Anthropic (recommended):**
1. Sign up at https://console.anthropic.com
2. Create API key
3. Copy to `.env` as `ANTHROPIC_API_KEY`

**For OpenAI:**
1. Sign up at https://platform.openai.com
2. Create API key
3. Copy to `.env` as `OPENAI_API_KEY`

## 2. Installation

```bash
# Clone repository
git clone <repo-url>
cd auto_trader

# Install with uv (recommended)
uv sync

# Or with pip
pip install -e .
```

## 3. Configuration

```bash
# Copy template
cp .env.example .env

# Edit configuration
nano .env  # or your preferred editor
```

### Minimal Configuration

```env
# Choose one LLM provider
ANTHROPIC_API_KEY=sk-ant-your-key-here
# OPENAI_API_KEY=sk-your-key-here

# MT5 endpoint
MT5_BASE_URL=http://localhost:8001/api/v1

# Trading pairs
SYMBOLS=EURUSD,GBPUSD

# Start in paper trading mode
PAPER_TRADING_MODE=true
```

## 4. First Run (Test Mode)

Run a single analysis cycle to verify everything works:

```bash
uv run trade-bot --once
```

Expected output:
```
2026-04-10 10:30:00 | INFO     | auto_trader.main | AutoTrader - Autonomous Trading System
2026-04-10 10:30:00 | INFO     | auto_trader.main | LLM Provider: anthropic
2026-04-10 10:30:00 | INFO     | auto_trader.main | Symbols: EURUSD, GBPUSD
2026-04-10 10:30:00 | INFO     | auto_trader.orchestration.bot | Starting analysis cycle for EURUSD
2026-04-10 10:30:05 | INFO     | auto_trader.orchestration.bot | Fetching market data...
2026-04-10 10:30:10 | INFO     | auto_trader.decision.workflow | Making trading decision...
2026-04-10 10:30:15 | INFO     | auto_trader.orchestration.bot | Decision: SKIP | Score: 62.50
```

## 5. Continuous Trading

Once verified, start continuous mode:

```bash
uv run trade-bot
```

The bot will:
- Run analysis every 15 minutes (configurable)
- Analyze all configured symbols
- Make trading decisions
- Execute trades (if in live mode)
- Log all activity

## 6. Monitoring

### View Logs

```bash
# Real-time logs
tail -f logs/trader_ai.log

# Search for decisions
grep "Decision:" logs/trader_ai.log

# Search for executions
grep "Trade executed" logs/trader_ai.log
```

### Check Status

The bot logs key metrics:
- Analysis cycles completed
- Decisions made (EXECUTE/WATCH/SKIP)
- Trades executed
- Daily trade count
- Risk limits

## 7. Going Live

⚠️ **IMPORTANT**: Only go live after thorough testing!

### Steps:

1. **Test in paper mode for at least 1 week**
   ```env
   PAPER_TRADING_MODE=true
   ```

2. **Review all paper trades**
   - Check decision quality
   - Verify risk management
   - Analyze win rate and RR

3. **Start with minimal risk**
   ```env
   MAX_RISK_PER_TRADE_PCT=0.5  # Start with 0.5%
   MAX_TRADES_PER_DAY=2
   ```

4. **Enable live trading**
   ```env
   PAPER_TRADING_MODE=false
   ```

5. **Monitor closely**
   - Watch first few trades
   - Verify execution prices
   - Check SL/TP placement

## 8. Troubleshooting

### "MT5 API request failed"

- Check MT5 MCP server is running
- Verify `MT5_BASE_URL` is correct
- Test endpoint: `curl http://localhost:8001/api/v1/account`

### "No JSON found in LLM response"

- Check API key is valid
- Verify LLM provider is correct
- Check internet connection
- Review LLM response in logs

### "Failed to fetch indicators"

- TradingView may be rate limiting
- Try different symbol format
- Check internet connection
- Wait and retry

### "Risk limits exceeded"

- Check `MAX_TRADES_PER_DAY` setting
- Check `MAX_DAILY_LOSS_PCT` setting
- Reset counters at midnight (automatic)

## 9. Customization

### Change Analysis Frequency

```env
DEFAULT_ANALYSIS_INTERVAL=900  # seconds (15 minutes)
```

### Adjust Risk Parameters

```env
MAX_RISK_PER_TRADE_PCT=1.0      # Risk per trade
CONFIDENCE_THRESHOLD=0.75        # Minimum score to execute
MIN_RR_RATIO=1.5                 # Minimum risk/reward
```

### Add More Symbols

```env
SYMBOLS=EURUSD,GBPUSD,USDJPY,AUDUSD
```

### Change Timeframes

```env
TIMEFRAMES=15m,1h,4h,1w
```

## 10. Best Practices

1. **Always start in paper mode**
2. **Monitor logs regularly**
3. **Review decisions daily**
4. **Adjust thresholds based on performance**
5. **Keep risk per trade low (1% or less)**
6. **Use stop losses on all trades**
7. **Don't overtrade (max 3-5 trades/day)**
8. **Respect news events**
9. **Backtest strategy changes**
10. **Keep detailed records**

## Support

For issues or questions:
1. Check logs: `logs/trader_ai.log`
2. Review configuration: `.env`
3. Test components individually
4. Consult documentation

## Next Steps

- Read [Architecture Documentation](../README.md#architecture)
- Review [Risk Management](../README.md#risk-management)
- Study [Decision Logic](../README.md#decision-logic)
- Explore agent prompts in `prompts/`
