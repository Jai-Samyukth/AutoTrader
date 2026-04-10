# System Design Document

## Overview

AutoTrader is a production-grade autonomous trading system that combines Smart Money Concepts (SMC), multi-timeframe technical analysis, and LLM-driven decision making to execute swing and intraday trades.

## Design Principles

### 1. Layered Architecture

The system follows strict separation of concerns:

- **Data Layer**: Fetches and normalizes data from external sources
- **Feature Layer**: Transforms raw data into trading signals
- **Decision Layer**: Makes trading decisions using LLM reasoning
- **Execution Layer**: Places and manages trades
- **Orchestration Layer**: Coordinates the entire workflow

### 2. Modularity

Each component is:
- Independently testable
- Loosely coupled
- Single responsibility
- Replaceable without affecting others

### 3. Determinism

Given the same inputs:
- Data fetching is consistent
- Feature extraction is reproducible
- Risk calculations are deterministic
- Only LLM reasoning introduces probabilistic behavior

## Component Details

### Data Layer

#### MT5Client (`data/mt5_client.py`)

**Purpose**: Communicate with MetaTrader 5 via HTTP API

**Responsibilities**:
- Fetch account information
- Get open positions
- Retrieve symbol specifications
- Place market orders
- Modify/close positions

**Design**:
- Uses `requests` library with retry logic
- Converts MT5 responses to domain models
- Handles connection failures gracefully
- Logs all API interactions

**Key Methods**:
```python
get_account_info() -> AccountInfo
get_positions(symbol) -> list[Position]
get_symbol_info(symbol) -> SymbolInfo
place_market_order(...) -> dict
```

#### MarketDataProvider (`data/market_data.py`)

**Purpose**: Fetch market data from TradingView and yfinance

**Responsibilities**:
- Get technical indicators via tradingview-ta
- Fetch OHLCV candles via yfinance
- Support multiple timeframes
- Cache data to reduce API calls

**Design**:
- Converts between symbol formats (EURUSD ↔ EUR/USD ↔ EURUSD=X)
- Maps timeframes to provider-specific intervals
- Returns empty data on failure (fail gracefully)
- Logs all data fetching operations

**Key Methods**:
```python
get_indicators(symbol, timeframe) -> IndicatorData
get_ohlcv(symbol, timeframe, periods) -> list[OHLCVData]
get_multi_timeframe_data(symbol, timeframes) -> dict
```

### Feature Layer

#### SMCAnalyzer (`features/smc.py`)

**Purpose**: Extract Smart Money Concepts from price data

**Responsibilities**:
- Identify swing highs and lows
- Detect Break of Structure (BOS)
- Detect Change of Character (CHoCH)
- Find Order Blocks (OB)
- Identify Fair Value Gaps (FVG)
- Locate liquidity zones

**Design**:
- Pure function approach (no side effects)
- Configurable swing period
- Returns structured SMCData model
- Filters mitigated OB/FVG

**Algorithm**:
1. Scan candles for swing points
2. Compare current price to structure
3. Identify institutional footprints
4. Mark zones for potential entries

#### NewsProvider (`features/news.py`)

**Purpose**: Filter trades based on news events

**Responsibilities**:
- Fetch upcoming economic events
- Filter by currency and impact
- Determine if trading should be paused

**Design**:
- Placeholder for news API integration
- Returns empty list by default (allows trading)
- Configurable lookback window
- Supports multiple news sources

**Integration Points**:
- ForexFactory API
- Investing.com calendar
- FXStreet events
- Custom news feeds

### Decision Layer

#### TradingWorkflow (`decision/workflow.py`)

**Purpose**: Orchestrate LLM-based decision making using LangGraph

**Responsibilities**:
- Build context for LLM
- Call LLM with structured prompt
- Parse and validate decision
- Apply risk rules

**Design**:
- LangGraph state machine with 3 nodes:
  1. **Analyze**: Log context summary
  2. **Decide**: Call LLM for decision
  3. **Validate**: Check against thresholds

**Workflow**:
```
Entry → Analyze → Decide → Validate → Exit
```

**LLM Prompt Structure**:
- System: Trading rules and scoring criteria
- User: Market context (indicators, SMC, news, account)
- Output: Structured JSON decision

**Validation Rules**:
- Score must exceed threshold
- RR ratio must meet minimum
- No high-impact news
- Daily limits not exceeded

#### ContextBuilder (`decision/context.py`)

**Purpose**: Build structured context for LLM

**Responsibilities**:
- Aggregate multi-timeframe data
- Format indicators and SMC signals
- Include news and account info
- Create JSON-serializable context

**Design**:
- Static methods (no state)
- Nested dictionary structure
- Handles missing data gracefully
- Converts Decimal to float for JSON

### Execution Layer

#### TradeExecutor (`execution/trade_executor.py`)

**Purpose**: Execute trades via MT5

**Responsibilities**:
- Calculate position size
- Determine SL/TP levels
- Place market orders
- Support paper trading mode

**Design**:
- Validates decision before execution
- Calculates lot size based on risk %
- Rounds to symbol's lot step
- Logs all executions

**Position Sizing Formula**:
```
risk_amount = balance × risk_pct
lot_size = risk_amount / (sl_pips × pip_value × contract_size)
```

**Paper Trading**:
- Simulates execution without real orders
- Logs trade details
- Returns fake ticket number
- Useful for testing and validation

### Orchestration Layer

#### TradingBot (`orchestration/bot.py`)

**Purpose**: Coordinate the entire trading workflow

**Responsibilities**:
- Run analysis cycles
- Fetch all required data
- Call decision workflow
- Execute trades
- Track daily limits

**Design**:
- Single entry point per symbol
- Sequential data fetching
- Error handling at each step
- Continues on non-fatal errors

**Analysis Cycle**:
1. Check risk limits
2. Fetch multi-timeframe data
3. Compute SMC features
4. Fetch news events
5. Get account info
6. Build context
7. Make decision
8. Execute if needed

#### TradingScheduler (`orchestration/scheduler.py`)

**Purpose**: Schedule automated trading cycles

**Responsibilities**:
- Run analysis at intervals
- Reset daily counters
- Handle start/stop

**Design**:
- Uses APScheduler
- Interval trigger for analysis
- Cron trigger for daily reset
- Graceful shutdown on interrupt

## Data Flow

### Complete Trading Cycle

```
1. Scheduler triggers analysis
   ↓
2. Bot fetches market data (TradingView, yfinance)
   ↓
3. Bot computes SMC features
   ↓
4. Bot fetches news events
   ↓
5. Bot gets account info (MT5)
   ↓
6. ContextBuilder aggregates all data
   ↓
7. TradingWorkflow calls LLM
   ↓
8. LLM returns decision (EXECUTE/WATCH/SKIP)
   ↓
9. Workflow validates decision
   ↓
10. If EXECUTE: TradeExecutor places order
    ↓
11. Bot logs result and waits for next cycle
```

## Decision Making

### Scoring System

**Phase 1: Bias + Structure (0-100)**

Evaluates higher timeframe context:
- Weekly/4H trend direction
- BOS/CHoCH alignment
- EMA positioning
- ADX strength

**Phase 2: Entry Quality (0-100)**

Evaluates entry timing:
- Order Block presence
- Fair Value Gap
- Liquidity sweep
- RSI/MACD confirmation

**Total Score**: Average of Phase 1 and Phase 2

### Execution Criteria

Trade executes ONLY if ALL conditions met:

1. `total_score >= confidence_threshold` (default 75)
2. `rr_ratio >= min_rr_ratio` (default 1.5)
3. `phase1_score >= phase1_floor` (default 50)
4. `phase2_score >= phase2_floor` (default 50)
5. No high-impact news within 60 minutes
6. Daily trade limit not exceeded
7. Daily loss limit not exceeded

### Decision Types

**EXECUTE**:
- All criteria met
- Place trade immediately
- Log execution details

**WATCH**:
- Partial criteria met
- Re-evaluate in N minutes
- Monitor for improvement

**SKIP**:
- Criteria not met
- No trade opportunity
- Move to next symbol

## Risk Management

### Position Sizing

```python
risk_amount = account_balance × (max_risk_pct / 100)
sl_distance_pips = entry_price - stop_loss_price (in pips)
pip_value = contract_size × point × 10
lot_size = risk_amount / (sl_distance_pips × pip_value)
```

### Stop Loss Placement

**For BUY**:
- Below recent swing low
- Below Order Block
- Below liquidity zone
- Minimum 20 pips from entry

**For SELL**:
- Above recent swing high
- Above Order Block
- Above liquidity zone
- Minimum 20 pips from entry

### Take Profit Placement

```python
tp_distance = sl_distance × rr_ratio
tp_price = entry_price ± tp_distance
```

Adjusted to:
- Resistance levels (for BUY)
- Support levels (for SELL)
- Psychological levels (round numbers)

### Daily Limits

**Max Trades Per Day**: Prevents overtrading
**Max Daily Loss**: Stops trading after threshold loss
**Reset**: Automatic at midnight

## Error Handling

### Graceful Degradation

- Missing indicators → Continue with available data
- API failure → Log error, skip cycle
- LLM error → Return SKIP decision
- Execution failure → Log, don't retry

### Retry Logic

- MT5 API: 3 retries with exponential backoff
- Market data: No retry (use cached or skip)
- LLM: No retry (too expensive)

### Logging

All operations logged with:
- Timestamp
- Log level (INFO/WARNING/ERROR)
- Component name
- Message

## Configuration

### Environment Variables

All configuration via `.env`:
- LLM settings
- MT5 connection
- Trading pairs
- Risk parameters
- Scheduler settings

### Validation

Configuration validated on startup:
- Required keys present
- Values within acceptable ranges
- API keys valid format

## Testing Strategy

### Unit Tests

- Domain models
- Configuration loading
- Utility functions
- Feature extraction

### Integration Tests

- MT5 client (with mock server)
- Market data fetching
- LLM workflow
- Trade execution

### End-to-End Tests

- Complete analysis cycle
- Paper trading mode
- Error scenarios

## Deployment

### Requirements

- Python 3.11+
- MetaTrader 5 with HTTP server
- Anthropic or OpenAI API access
- Stable internet connection

### Monitoring

- Log file rotation
- Daily performance reports
- Alert on errors
- Track key metrics

### Maintenance

- Review logs daily
- Adjust thresholds based on performance
- Update prompts as needed
- Monitor API usage and costs

## Future Enhancements

1. **Backtesting Engine**: Test strategies on historical data
2. **Performance Analytics**: Track win rate, RR, drawdown
3. **Multi-Account Support**: Manage multiple MT5 accounts
4. **Advanced Order Types**: Limit orders, trailing stops
5. **Machine Learning**: Train models on historical decisions
6. **Web Dashboard**: Real-time monitoring and control
7. **Telegram Notifications**: Trade alerts and updates
8. **Database Integration**: Store trades and performance data

## Security Considerations

- API keys in environment variables (never in code)
- No sensitive data in logs
- Secure MT5 connection (HTTPS recommended)
- Rate limiting on external APIs
- Input validation on all external data

## Performance

- Analysis cycle: ~10-30 seconds per symbol
- LLM call: ~2-5 seconds
- MT5 API: <1 second per call
- Memory usage: <500MB
- CPU usage: Low (mostly I/O bound)

## Conclusion

AutoTrader is designed as a production-grade system with:
- Clean architecture
- Modular components
- Robust error handling
- Comprehensive logging
- Flexible configuration
- Safe risk management

The system is deterministic where possible and uses LLM reasoning only for high-level decision making, ensuring reliability and auditability.
