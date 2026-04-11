# ✅ READY TO TRADE

## Status: Bot is WORKING

Your AutoTrader bot is configured and ready. Here's what's working:

✅ MT5 connection established  
✅ Account info retrieved ($3000 balance, 1:2000 leverage)  
✅ Market data fetching (Yahoo Finance + TradingView)  
✅ SMC analysis running  
✅ News filtering active  
✅ Paper trading mode enabled  

## Quick Start

### 1. Make Sure MT5 is Running

**IMPORTANT:** Open MetaTrader 5 terminal and log in before running the bot.

### 2. Run the Bot

```bash
# Test run (single cycle)
uv run python -m auto_trader.main --once

# Continuous trading
uv run python -m auto_trader.main
```

### 3. Monitor Logs

```bash
tail -f logs/trader_ai.log
```

## Current Configuration

- **Account:** JustMarkets-Demo2 ($3000)
- **Symbols:** EURUSD.m, GBPUSD.m
- **Timeframes:** 15m, 1h, 4h, 1w
- **Risk per Trade:** 1.0%
- **Confidence Threshold:** 0.75
- **Paper Trading:** ✅ ENABLED (safe mode)

## What Happens Next

1. **Bot analyzes** market data every 15 minutes
2. **LLM evaluates** trading opportunities using SMC strategy
3. **Risk manager** validates trade parameters
4. **Paper trades** are logged (no real money)
5. **You review** performance in logs

## When to Go Live

**DO NOT go live until:**

1. ✅ Bot runs for 1+ week in paper mode
2. ✅ You review ALL paper trade decisions
3. ✅ Win rate is >55% and profit factor >1.5
4. ✅ Risk management is working correctly
5. ✅ You understand every trade the bot makes

## Going Live Checklist

When ready to trade real money:

1. Set `PAPER_TRADING_MODE=false` in `.env`
2. Reduce `MAX_RISK_PER_TRADE_PCT` to 0.5%
3. Set `MAX_TRADES_PER_DAY` to 2-3
4. Start with SMALL account ($100-500)
5. Monitor EVERY trade for first week
6. Scale up SLOWLY

## Troubleshooting

### "Terminal: Not found"
**Solution:** Open MT5 terminal and log in

### "Symbol not found"
**Solution:** Symbols are correct (EURUSD.m, GBPUSD.m)

### Bot not making trades
**Normal:** Bot is selective. May take hours/days to find good setups.

## Performance Tracking

Track these metrics in paper trading:

- **Win Rate:** % of profitable trades
- **Profit Factor:** Gross profit / Gross loss
- **Max Drawdown:** Largest peak-to-trough decline
- **Average R:R:** Average risk/reward ratio
- **Trade Frequency:** Trades per day/week

## Next Steps

1. **Run bot in paper mode:** `uv run python -m auto_trader.main`
2. **Let it run for 1 week**
3. **Review logs daily:** `tail -100 logs/trader_ai.log`
4. **Track performance** in a spreadsheet
5. **Adjust parameters** based on results

## Support

- Check logs: `logs/trader_ai.log`
- Test connection: `uv run python scripts/test_mt5_direct.py`
- List symbols: `uv run python scripts/list_mt5_symbols.py`

---

**Remember:** The goal is to make money CONSISTENTLY, not quickly. Take your time in paper trading.
