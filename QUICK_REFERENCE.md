# AutoTrader Quick Reference

## Essential Commands

### First Time Setup
```bash
bash scripts/install.sh          # Install dependencies
cp .env.example .env             # Create config file
nano .env                        # Edit with your API keys
bash scripts/validate_env.sh     # Validate configuration
```

### Running the System (2 Terminals Required)

**Terminal 1: MT5 Server (MUST RUN FIRST)**
```bash
bash scripts/start_mt5_server.sh    # Bash
.\scripts\start_mt5_server.ps1      # PowerShell
```

**Terminal 2: Trading Bot**
```bash
bash scripts/run_once.sh         # Single cycle (testing)
bash scripts/run.sh              # Continuous mode
```

**Terminal 3: Monitoring (Optional)**
```bash
bash scripts/logs.sh follow      # Real-time logs
```

### Testing & Validation
```bash
bash scripts/test_mt5_connection.sh  # Test MT5 server
bash scripts/run_once.sh             # Test single cycle
bash scripts/validate_env.sh         # Validate config
```

### Development
```bash
bash scripts/format.sh           # Format code
bash scripts/lint.sh             # Check code quality
bash scripts/test.sh             # Run tests
bash scripts/check.sh            # Format + lint + test
```

### Monitoring
```bash
bash scripts/logs.sh             # View recent logs
bash scripts/logs.sh follow      # Real-time streaming
bash scripts/logs.sh decisions   # Trading decisions only
bash scripts/logs.sh trades      # Trade executions only
bash scripts/logs.sh errors      # Errors only
```

### Maintenance
```bash
bash scripts/clean.sh            # Clean cache files
bash scripts/pre_commit.sh       # Pre-commit checks
```

## Configuration Files

### `.env` - Main Configuration
```env
# LLM Provider (choose one)
LLM_PROVIDER=openai              # or anthropic, groq
OPENAI_API_KEY=sk-...            # Your API key

# MetaTrader 5 Credentials (REQUIRED)
MT5_LOGIN=12345678               # Your MT5 login ID
MT5_PASSWORD=YourPassword123     # Your MT5 password
MT5_SERVER=MetaQuotes-Demo       # Your broker's server

# Trading Settings
PAPER_TRADING_MODE=true          # ALWAYS start with true!
SYMBOLS=EURUSD,GBPUSD            # Trading pairs
TIMEFRAMES=15m,1h,4h,1w          # Analysis timeframes

# Risk Management
MAX_RISK_PER_TRADE_PCT=1.0       # Max 1% per trade
MAX_DAILY_LOSS_PCT=3.0           # Stop at 3% daily loss
MAX_TRADES_PER_DAY=5             # Max 5 trades per day

# Decision Thresholds
CONFIDENCE_THRESHOLD=0.75        # Min confidence to trade
MIN_RR_RATIO=2.0                 # Min risk:reward ratio
```

**To find MT5 credentials:**
1. Open MetaTrader 5
2. Tools → Options → Server tab
3. Note Login ID and Server name

## Common Issues & Solutions

### MT5 Server Not Running
```
ERROR: 404 Client Error: Not Found for url: http://localhost:8001/api/v1/account
```
**Solution:**
```bash
# Terminal 1: Start MT5 server
bash scripts/start_mt5_server.sh
```

### Missing MT5 Credentials
```
ERROR: Missing MT5 credentials in .env file
```
**Solution:** Add to `.env`:
```env
MT5_LOGIN=your_login_id
MT5_PASSWORD=your_password
MT5_SERVER=your_server_name
```

### Invalid MT5 Credentials
```
ERROR: Authorization failed
```
**Solution:**
1. Verify in MT5: Tools → Options → Server
2. Check server name matches exactly
3. Try logging into MT5 terminal first

### uvx Not Found
```
ERROR: uvx is not installed
```
**Solution:**
```bash
# Windows PowerShell
irm https://astral.sh/uv/install.ps1 | iex

# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Port 8001 In Use
```bash
# Windows
netstat -ano | findstr :8001
taskkill /PID <PID> /F

# Linux/macOS
lsof -i :8001
kill -9 <PID>
```

### No Trading Decisions
**Check:**
1. Confidence threshold too high → Lower in `.env`
2. Risk limits too strict → Adjust in `.env`
3. No valid setups → Normal, wait for opportunities

### API Rate Limits
**Solution:**
- Use Groq (free tier with high limits)
- Reduce analysis frequency
- Check API key quotas

## File Structure

```
AutoTrader/
├── src/auto_trader/          # Main source code
│   ├── data/                 # Data fetching (MT5, market data)
│   ├── features/             # SMC, news analysis
│   ├── decision/             # LLM decision engine
│   ├── execution/            # Trade execution
│   ├── orchestration/        # Bot coordinator
│   └── utils/                # Logging, helpers
├── scripts/                  # Utility scripts
├── docs/                     # Documentation
├── tests/                    # Unit tests
├── logs/                     # Log files
├── .env                      # Configuration (create from .env.example)
└── pyproject.toml           # Project metadata
```

## Key Concepts

### Trading Decision Flow
```
1. Fetch market data (OHLCV, indicators)
2. Calculate SMC features (BOS, OB, FVG, etc.)
3. Check news calendar
4. Get account info from MT5
5. Build context for LLM
6. LLM makes decision (EXECUTE/WATCH/SKIP)
7. If EXECUTE: Calculate position size, place order
8. If WATCH: Schedule next check
9. If SKIP: Log reason and continue
```

### Risk Management
- **Position Sizing**: Based on account balance and risk %
- **Stop Loss**: Calculated from SMC levels
- **Take Profit**: Based on risk:reward ratio
- **Daily Limits**: Stop trading after max loss or trades
- **News Filter**: Skip trades during high-impact news

### Paper Trading
- Simulates trades without real money
- Logs all decisions and executions
- Perfect for testing strategies
- **ALWAYS test in paper mode first!**

## API Keys Required

### LLM Provider (choose one)
- **OpenAI**: [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- **Anthropic**: [console.anthropic.com](https://console.anthropic.com/)
- **Groq**: [console.groq.com](https://console.groq.com/) (Free tier!)

### News API (optional)
- **NewsAPI**: [newsapi.org](https://newsapi.org/) (Free tier available)

## Safety Checklist

Before live trading:
- [ ] Tested in paper mode for at least 1 week
- [ ] Verified all API connections work
- [ ] Confirmed risk limits are appropriate
- [ ] Started with small position sizes
- [ ] Set up monitoring and alerts
- [ ] Have emergency stop plan
- [ ] Understand all parameters
- [ ] Backed up configuration

## Documentation

- [Startup Guide](docs/STARTUP_GUIDE.md) - Complete setup
- [MT5 Server Setup](MT5_SERVER_SETUP.md) - MT5 server details
- [Scripts Guide](docs/SCRIPTS_GUIDE.md) - All scripts explained
- [System Design](docs/SYSTEM_DESIGN.md) - Architecture
- [MCP Integration](docs/MCP_INTEGRATION.md) - MT5 integration
- [LangChain Integration](docs/LANGCHAIN_INTEGRATION.md) - LLM workflow

## Support

**Check logs first:**
```bash
bash scripts/logs.sh errors
```

**Common log locations:**
- Main log: `logs/trader_ai.log`
- Error messages: Search for `ERROR` in logs
- Decisions: Search for `EXECUTE`, `WATCH`, `SKIP`

**Debugging:**
1. Check MT5 server is running
2. Check MT5 is logged in
3. Verify API keys in `.env`
4. Test connection: `bash scripts/test_mt5_connection.sh`
5. Run single cycle: `bash scripts/run_once.sh`
6. Check logs: `bash scripts/logs.sh errors`

## Quick Start (Copy-Paste)

```bash
# Setup
bash scripts/install.sh
cp .env.example .env
nano .env  # Add your API keys
bash scripts/validate_env.sh

# Terminal 1: Start MT5 server
bash scripts/start_mt5_server.sh

# Terminal 2: Run bot
bash scripts/run_once.sh  # Test first
bash scripts/run.sh       # Then continuous

# Terminal 3: Monitor
bash scripts/logs.sh follow
```

---

**Remember:**
1. Always start MT5 server first (Terminal 1)
2. Always test in paper mode first
3. Monitor logs regularly
4. Start with small positions
5. Never risk more than you can afford to lose

**Trading involves significant risk. This system does not guarantee profits.**
