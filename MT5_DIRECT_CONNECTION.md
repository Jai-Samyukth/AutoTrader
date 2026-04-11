# MT5 Direct Connection Setup

## What Changed?

The system now uses the **direct Python MetaTrader5 package** instead of a separate MCP server. This is simpler, faster, and more reliable.

### Old Architecture (MCP Server)
```
AutoTrader → HTTP → MCP Server → MT5 Terminal
```

### New Architecture (Direct)
```
AutoTrader → MetaTrader5 Python Package → MT5 Terminal
```

## Benefits

✅ **No separate server needed** - One less thing to manage  
✅ **Faster** - Direct connection, no HTTP overhead  
✅ **Simpler** - Just run MT5 terminal and your code  
✅ **More reliable** - Fewer points of failure  
✅ **Better error messages** - Direct access to MT5 errors  

## Setup

### 1. Install MetaTrader 5

Download from your broker or [MetaQuotes](https://www.metatrader5.com/)

### 2. Configure `.env`

```env
# MetaTrader 5 Credentials
MT5_LOGIN=1100383854
MT5_PASSWORD=your_password
MT5_SERVER=JustMarkets-Demo2
```

### 3. Enable AutoTrading in MT5

1. Open MT5 Terminal
2. Go to **Tools → Options → Expert Advisors**
3. Check **"Allow automated trading"**
4. Check **"Allow DLL imports"**
5. Click **OK**

### 4. Test Connection

```bash
# Test the connection
bash scripts/test_mt5_connection.sh

# Or run Python test directly
python scripts/test_mt5_direct.py
```

Expected output:
```
============================================================
Testing Direct MT5 Connection
============================================================

1. Testing account info...
✓ Account Balance: $10000.00
✓ Account Equity: $10000.00
✓ Leverage: 1:100

2. Testing positions...
✓ Open Positions: 0

3. Testing symbol info (EURUSD)...
✓ Symbol: EURUSD
✓ Bid: 1.08450
✓ Ask: 1.08452
✓ Spread: 2 points

============================================================
✓ All tests passed!
============================================================
```

## Running the Bot

```bash
# Start the trading bot
bash scripts/run.sh

# Or run once
bash scripts/run_once.sh
```

## Troubleshooting

### "MT5 initialization failed"

**Solution:**
- Make sure MT5 terminal is **running**
- Try restarting MT5
- Check if MT5 is installed

### "MT5 login failed"

**Solution:**
- Verify credentials in `.env` are correct
- Check you can login manually in MT5
- Make sure account is active

### "Failed to get account info"

**Solution:**
- Verify you're **logged in** to MT5 terminal
- Check account has funds
- Try reconnecting in MT5

### "Symbol not found"

**Solution:**
- Right-click in Market Watch → Show All
- Make sure symbol exists for your broker
- Check symbol name spelling (e.g., "EURUSD" not "EUR/USD")

## What About the MCP Server?

You **don't need it anymore**. The `scripts/start_mt5_server.sh` script is no longer required.

If you want to use the MCP server for other purposes (like connecting from other tools), you can still run it, but AutoTrader doesn't use it.

## Code Changes

The main changes are in `src/auto_trader/data/mt5_client.py`:

- Removed HTTP requests
- Added direct MT5 Python package calls
- Added proper error handling
- Improved logging

All the LangChain tools (`@tool` decorators) remain the same, so the rest of your code doesn't need changes.

## Testing

Run the test suite:

```bash
# Run all tests
bash scripts/test.sh

# Test MT5 connection only
python scripts/test_mt5_direct.py
```

## Next Steps

1. ✅ Test connection: `bash scripts/test_mt5_connection.sh`
2. ✅ Verify account info is correct
3. ✅ Run the bot: `bash scripts/run_once.sh`
4. ✅ Monitor logs: `tail -f logs/trader_ai.log`

## Questions?

Check the documentation:
- `docs/MCP_INTEGRATION.md` - Updated integration guide
- `docs/QUICKSTART.md` - Quick start guide
- `README.md` - Main documentation
