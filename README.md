# AutoTrader - Autonomous Trading System

Production-grade autonomous trading bot using Smart Money Concepts (SMC), multi-timeframe technical analysis, and LLM-driven decision making.

## Features

- **Multi-Timeframe Analysis**: Weekly → 4H → 1H → 15m trend alignment
- **Smart Money Concepts**: BOS, CHoCH, Order Blocks, FVG, Liquidity zones
- **Technical Indicators**: RSI, MACD, EMA, ADX, Bollinger Bands, Supertrend (via TradingView-TA)
- **LLM Decision Engine**: Claude/GPT-powered trade analysis with structured output
- **LangGraph Workflow**: State machine for decision orchestration
- **MCP Integration**: MetaTrader 5 via Model Context Protocol tools
- **Risk Management**: Position sizing, SL/TP calculation, daily limits
- **News Filtering**: Avoid trading during high-impact events
- **Paper Trading**: Test strategies without real money
- **MetaTrader 5 Integration**: Direct execution via MCP HTTP API

## Architecture

### Layered Design

```
┌─────────────────────────────────────────────────────────┐
│                  Orchestration Layer                     │
│              (Scheduler, Bot Coordinator)                │
└─────────────────────────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Decision   │  │  Execution   │  │   Features   │
│    Layer     │  │    Layer     │  │    Layer     │
│  (LangGraph) │  │ (MT5 Client) │  │  (SMC, News) │
└──────────────┘  └──────────────┘  └──────────────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           ▼
                  ┌──────────────┐
                  │  Data Layer  │
                  │ (Market Data)│
                  └──────────────┘
```

### Components

1. **Data Layer** (`data/`)
   - `mt5_client.py`: MetaTrader 5 HTTP client
   - `market_data.py`: TradingView & yfinance integration

2. **Feature Layer** (`features/`)
   - `smc.py`: Smart Money Concepts analyzer
   - `news.py`: News event filtering

3. **Decision Layer** (`decision/`)
   - `workflow.py`: LangGraph trading workflow
   - `context.py`: Context builder for LLM
   - `llm.py`: LLM initialization

4. **Execution Layer** (`execution/`)
   - `trade_executor.py`: Order placement and management

5. **Orchestration Layer** (`orchestration/`)
   - `bot.py`: Main trading bot coordinator
   - `scheduler.py`: Automated scheduling

## Installation

### Prerequisites

- Python 3.11+
- **MetaTrader 5 MCP Server** running on `http://localhost:8001`
  - See [MetaTrader MCP Server Setup](https://github.com/ariadng/metatrader-mcp-server)
  - Install: `git clone https://github.com/ariadng/metatrader-mcp-server && cd metatrader-mcp-server && npm install`
  - Configure: Edit `.env` with MT5 credentials
  - Start: `npm start`
- Anthropic or OpenAI API key

### Setup

```bash
# Clone repository
git clone <repo-url>
cd auto_trader

# Install dependencies
uv sync

# Or with pip
pip install -e .

# Copy environment template
cp .env.example .env

# Edit .env with your credentials
```

### Environment Variables

```env
# LLM Configuration
ANTHROPIC_API_KEY=sk-ant-...
# Or
OPENAI_API_KEY=sk-...

# MT5 Configuration
MT5_BASE_URL=http://localhost:8001/api/v1

# Trading Configuration
SYMBOLS=EURUSD,GBPUSD
TIMEFRAMES=15m,1h,4h,1w

# Risk Management
MAX_RISK_PER_TRADE_PCT=1.0
CONFIDENCE_THRESHOLD=0.75
MIN_RR_RATIO=1.5

# Mode
PAPER_TRADING_MODE=true
```

## Usage

### Quick Start with Scripts

```bash
# Initial setup
bash scripts/dev.sh setup

# Run test cycle
bash scripts/dev.sh test

# Run continuous mode
bash scripts/dev.sh run

# View logs
bash scripts/dev.sh logs

# Check status
bash scripts/dev.sh status
```

### Manual Commands

```bash
# Run continuous trading
uv run trade-bot

# Run single cycle (testing)
uv run trade-bot --once

# View logs
bash scripts/logs.sh follow
bash scripts/logs.sh decisions
bash scripts/logs.sh trades
```

### Development Scripts

All scripts are in the `scripts/` directory:

- `dev.sh` - Development workflow helper
- `install.sh` - Install dependencies
- `validate_env.sh` - Validate configuration
- `run.sh` - Run continuous mode
- `run_once.sh` - Run single cycle
- `logs.sh` - View and filter logs
- `format.sh` - Format code
- `lint.sh` - Lint code
- `test.sh` - Run tests
- `check.sh` - Run all checks
- `clean.sh` - Clean cache
- `pre_commit.sh` - Pre-commit checks

See [scripts/README.md](scripts/README.md) for detailed documentation.

### Paper Trading

Set `PAPER_TRADING_MODE=true` in `.env` to simulate trades without real execution.

## Decision Logic

### Scoring System

**Phase 1: Bias + Structure (0-100)**
- Higher timeframe alignment
- BOS/CHoCH direction
- Trend strength (EMA, ADX)

**Phase 2: Entry Quality (0-100)**
- Order Block / FVG presence
- Liquidity sweep
- Indicator confirmation

**Total Score**: (Phase1 + Phase2) / 2

### Execution Criteria

Trade executes ONLY if:
- `total_score >= 75` (configurable)
- `rr_ratio >= 1.5`
- No high-impact news within 60 minutes
- Daily limits not exceeded

### Decision Types

- **EXECUTE**: Place trade immediately
- **WATCH**: Monitor and re-evaluate
- **SKIP**: No opportunity

## Risk Management

- **Position Sizing**: Based on account balance and risk %
- **Stop Loss**: Calculated from SMC levels or ATR
- **Take Profit**: Based on risk/reward ratio
- **Daily Limits**: Max trades and max loss per day
- **News Filter**: Skip trades during high-impact events

## Logging

Logs are written to:
- Console (stdout)
- File: `./logs/trader_ai.log`

Log level configurable via `LOG_LEVEL` environment variable.

## Development

### Project Structure

```
src/auto_trader/
├── config.py              # Configuration management
├── main.py                # Entry point
├── data/                  # Data fetching
│   ├── mt5_client.py      # MCP tools for MetaTrader 5
│   └── market_data.py     # TradingView-TA integration
├── features/              # Feature extraction
│   ├── smc.py             # Smart Money Concepts
│   └── news.py            # News filtering
├── decision/              # LLM decision making
│   ├── workflow.py        # LangGraph state machine
│   ├── context.py         # Context builder
│   └── llm.py             # LLM initialization
├── execution/             # Trade execution
│   └── trade_executor.py  # Order placement
├── orchestration/         # Bot coordination
│   ├── bot.py             # Main coordinator
│   └── scheduler.py       # Automated scheduling
├── domain/                # Domain models
│   └── models.py          # Pydantic models
└── utils/                 # Utilities
    └── logging.py         # Logging setup
```

### Key Technologies

- **LangChain**: LLM framework with structured output
- **LangGraph**: State machine workflow orchestration
- **TradingView-TA**: Technical indicator library
- **MCP Tools**: MetaTrader 5 integration via @tool decorators
- **Pydantic**: Data validation and settings
- **APScheduler**: Automated scheduling

### MCP Integration

See [MCP Integration Guide](docs/MCP_INTEGRATION.md) for detailed documentation on:
- MetaTrader MCP Server setup
- LangChain tool usage
- TradingView-TA integration
- LangGraph workflow patterns

### Testing

```bash
# Run tests
uv run pytest

# Format code
uv run ruff format .

# Lint
uv run ruff check .
```

## Safety

- Always start with `PAPER_TRADING_MODE=true`
- Test thoroughly before live trading
- Monitor logs and performance
- Set conservative risk limits
- Use stop losses on all trades

## License

MIT

## Disclaimer

This software is for educational purposes. Trading involves risk. Use at your own discretion.
