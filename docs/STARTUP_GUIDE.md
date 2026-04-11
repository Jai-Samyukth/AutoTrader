# AutoTrader Startup Guide

Complete guide to get AutoTrader running from scratch.

## Prerequisites

### 1. Install Required Software

#### Python 3.11+
- Download from [python.org](https://www.python.org/downloads/)
- Make sure to check "Add Python to PATH" during installation

#### UV Package Manager
UV is a fast Python package manager that includes `uvx` for running packages.

**Windows (PowerShell):**
```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

**Linux/macOS:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Or via pip:**
```bash
pip install uv
```

Verify installation:
```bash
uv --version
uvx --version
```

#### MetaTrader 5
- Download from [MetaTrader 5](https://www.metatrader5.com/)
- Install and create/login to a trading account
- Keep MT5 running while using AutoTrader

### 2. API Keys

You'll need API keys for:

1. **LLM Provider** (choose one):
   - OpenAI: [platform.openai.com](https://platform.openai.com/api-keys)
   - Anthropic: [console.anthropic.com](https://console.anthropic.com/)
   - Groq: [console.groq.com](https://console.groq.com/)

2. **News API** (optional):
   - [newsapi.org](https://newsapi.org/) - Free tier available

## Installation Steps

### Step 1: Clone and Setup

```bash
# Navigate to project directory
cd AutoTrader

# Install dependencies
bash scripts/install.sh
```

This will:
- Install all Python dependencies
- Create `.env` file from template
- Create logs directory

### Step 2: Configure Environment

Edit `.env` file with your API keys and MT5 credentials:

```bash
# Open .env in your editor
nano .env  # or use any text editor
```

**Minimum required configuration:**

```env
# LLM Configuration (choose one provider)
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here

# OR use Groq (free tier available)
# LLM_PROVIDER=groq
# GROQ_API_KEY=your-groq-key

# MetaTrader 5 Credentials (REQUIRED)
MT5_LOGIN=12345678
MT5_PASSWORD=YourPassword123
MT5_SERVER=MetaQuotes-Demo

# Trading Configuration
PAPER_TRADING_MODE=true  # IMPORTANT: Start with paper trading!
SYMBOLS=EURUSD,GBPUSD
TIMEFRAMES=15m,1h,4h,1w

# Risk Management
MAX_RISK_PER_TRADE_PCT=1.0
MAX_DAILY_LOSS_PCT=3.0
MAX_TRADES_PER_DAY=5

# News API (optional)
# NEWS_API_KEY=your-news-api-key
```

**To find your MT5 credentials:**
1. Open MetaTrader 5
2. Go to: Tools → Options → Server tab
3. Note your Login ID and Server name
4. Password is what you use to login to MT5

### Step 3: Validate Configuration

```bash
bash scripts/validate_env.sh
```

This checks:
- `.env` file exists
- Required API keys are set
- Configuration is valid

## Running AutoTrader

### Two-Terminal Setup (REQUIRED)

You need TWO terminals running simultaneously:

#### Terminal 1: MT5 MCP Server

**Bash (Git Bash, Linux, macOS):**
```bash
bash scripts/start_mt5_server.sh
```

**PowerShell (Windows):**
```powershell
.\scripts\start_mt5_server.ps1
```

**What you should see:**
```
============================================================
Starting MetaTrader 5 MCP Server
============================================================
MT5 Login: 12345678
MT5 Server: MetaQuotes-Demo
Starting server on http://localhost:8001...

Press Ctrl+C to stop the server
============================================================

Connecting to MT5...
Connected successfully!
Server running on http://localhost:8001
```

**Keep this terminal open!** The server must run continuously.

#### Terminal 2: AutoTrader Bot

**Test with single cycle first:**
```bash
bash scripts/run_once.sh
```

**If successful, run continuous mode:**
```bash
bash scripts/run.sh
```

## Monitoring

### View Logs

**Real-time log streaming:**
```bash
bash scripts/logs.sh follow
```

**View recent logs:**
```bash
bash scripts/logs.sh
```

**Filter by type:**
```bash
bash scripts/logs.sh decisions  # Trading decisions
bash scripts/logs.sh trades     # Trade executions
bash scripts/logs.sh errors     # Errors only
```

### What to Look For

**Successful startup:**
```
2026-04-11 12:31:34 | INFO | AutoTrader - Autonomous Trading System
2026-04-11 12:31:34 | INFO | LLM Provider: openai
2026-04-11 12:31:34 | INFO | Paper Trading: True
2026-04-11 12:31:34 | INFO | Starting continuous trading mode
```

**Successful MT5 connection:**
```
2026-04-11 12:31:41 | INFO | Account info retrieved: Balance=10000.00
2026-04-11 12:31:41 | INFO | Starting analysis cycle for EURUSD
```

**Common errors and fixes:**
```
ERROR: 404 Client Error: Not Found for url: http://localhost:8001/api/v1/account
→ MT5 MCP server is not running. Start it in Terminal 1.

ERROR: Exchange or symbol not found
→ TradingView doesn't have data for this symbol/timeframe. This is normal for some pairs.

ERROR: Failed to get account info: Connection refused
→ MT5 is not running or not logged in. Start MT5 first.
```

## Troubleshooting

### MT5 MCP Server Issues

**Missing credentials error:**
```
ERROR: Missing MT5 credentials in .env file
```
**Solution:** Add to `.env`:
```env
MT5_LOGIN=your_login_id
MT5_PASSWORD=your_password
MT5_SERVER=your_server_name
```

**Invalid credentials:**
```
ERROR: Authorization failed
```
**Solution:**
1. Verify credentials in MT5: Tools → Options → Server
2. Check server name exactly matches (case-sensitive)
3. Try logging into MT5 terminal to verify credentials work

**Server won't start:**
```bash
# Check if uvx is installed
uvx --version

# If not, install uv
curl -LsSf https://astral.sh/uv/install.sh | sh  # Linux/Mac
irm https://astral.sh/uv/install.ps1 | iex       # Windows PowerShell
```

**Port 8001 already in use:**
```bash
# Windows
netstat -ano | findstr :8001
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :8001
kill -9 <PID>
```

**MT5 not connecting:**
1. Check MT5 credentials in `.env` are correct
2. Verify server name matches exactly (Tools → Options → Server in MT5)
3. Try logging into MT5 terminal with same credentials
4. Check internet connection
5. Restart the MCP server

### Bot Issues

**No trading decisions:**
- Check if paper trading mode is enabled (should be `true` for testing)
- Check confidence threshold in `.env` (lower it for testing: `CONFIDENCE_THRESHOLD=0.5`)
- View logs to see decision reasoning

**API rate limits:**
- Use Groq for free tier with high limits
- Reduce analysis frequency in config
- Check API key quotas

**Missing dependencies:**
```bash
bash scripts/clean.sh
bash scripts/install.sh
```

## Development Workflow

### Before Making Changes

```bash
# Format code
bash scripts/format.sh

# Run tests
bash scripts/test.sh

# Run all checks
bash scripts/check.sh
```

### Testing Changes

```bash
# Single analysis cycle
bash scripts/run_once.sh

# Check logs
bash scripts/logs.sh
```

### Pre-commit

```bash
bash scripts/pre_commit.sh
```

## Safety Checklist

Before going live (IMPORTANT):

- [ ] Tested thoroughly in paper trading mode
- [ ] Verified all API connections work
- [ ] Confirmed risk limits are appropriate
- [ ] Tested with small position sizes first
- [ ] Monitored for at least 1 week in paper mode
- [ ] Reviewed all trading decisions manually
- [ ] Set up proper monitoring and alerts
- [ ] Have a plan to stop the bot quickly
- [ ] Understand all configuration parameters
- [ ] Backed up configuration and logs

**To enable live trading:**
```env
PAPER_TRADING_MODE=false  # Change to false ONLY after thorough testing
```

## Quick Start Summary

```bash
# 1. Install dependencies
bash scripts/install.sh

# 2. Configure .env with your API keys
nano .env

# 3. Validate configuration
bash scripts/validate_env.sh

# 4. Terminal 1: Start MT5 server (keep running)
bash scripts/start_mt5_server.sh

# 5. Terminal 2: Test the bot
bash scripts/run_once.sh

# 6. Terminal 2: Run continuous mode
bash scripts/run.sh

# 7. Terminal 3: Monitor logs
bash scripts/logs.sh follow
```

## Getting Help

1. Check logs: `bash scripts/logs.sh errors`
2. Review configuration: `bash scripts/validate_env.sh`
3. Check documentation in `docs/` folder
4. Review error messages carefully - they usually indicate the issue

## Next Steps

Once running successfully:

1. Monitor paper trading for several days
2. Review trading decisions and adjust parameters
3. Fine-tune confidence thresholds and risk limits
4. Test different symbols and timeframes
5. Gradually increase position sizes
6. Consider adding custom indicators or strategies

## Important Notes

- **ALWAYS start with paper trading mode**
- Keep MT5 MCP server running in a separate terminal
- Monitor logs regularly
- Start with small position sizes
- Test thoroughly before live trading
- Have a stop-loss strategy
- Never risk more than you can afford to lose
- Trading involves significant risk

---

**Remember**: This is an autonomous trading system. While it includes risk management, you are ultimately responsible for all trades. Start small, test thoroughly, and never risk more than you can afford to lose.
