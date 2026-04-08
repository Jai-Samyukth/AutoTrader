# Design Document: Trader AI System

## Overview

The Trader AI System is a fully autonomous multi-agent trading platform that analyzes financial markets, evaluates trading strategies, manages risk, and executes trades on MetaTrader 5. The system employs a sophisticated LangGraph-based workflow architecture with seven specialized agents orchestrated by a central coordinator.

The system interfaces with external services through two Model Context Protocol (MCP) servers:
- **MCP 1 (TradingView)**: Provides market data, news, and technical indicators
- **MCP 2 (MetaTrader 5)**: Handles trade execution and account management

The architecture emphasizes safety through paper trading support, optional human-in-the-loop approval, single trade per cycle constraints, and comprehensive risk management. All agents are stateless, with context flowing through a centralized TraderState object that maintains complete workflow history and enables reproducibility.

Key design principles:
- Stateless agents with stateful graph architecture
- Conditional workflow routing based on strategy and risk gates
- Dynamic scheduling adapting to market conditions
- Explicit awareness of data limitations (3/4 timing indicators available)
- Strict separation between analysis and execution

## Architecture

### System Architecture

The system follows a directed acyclic graph (DAG) workflow pattern implemented using LangGraph's StateGraph. The Orchestrator serves as the entry point and coordinator, delegating tasks to specialized agents based on workflow state.

```
┌─────────────────────────────────────────────────────────────┐
│                    WORKFLOW EXECUTION                        │
│                                                              │
│  START → Orchestrator → Data_Collector                      │
│                              ↓                               │
│                    ┌─────────┴─────────┐                    │
│                    ↓                   ↓                     │
│            Technical_Analyst    News_Analyst                 │
│                    └─────────┬─────────┘                    │
│                              ↓                               │
│                    Strategy_Evaluator                        │
│                              ↓                               │
│                    ┌─────────┴─────────┐                    │
│                    │  strategy_triggered?                    │
│                    ├─────────┬─────────┤                    │
│                   No        Yes                              │
│                    │         ↓                               │
│                    │    Risk_Manager                         │
│                    │         ↓                               │
│                    │  ┌──────┴──────┐                       │
│                    │  │ confidence?  │                       │
│                    │  ├──────┬──────┤                       │
│                    │  Low   High                             │
│                    │   │     ↓                               │
│                    │   │  Trade_Executor                     │
│                    └───┴─────┘                               │
│                         ↓                                    │
│                    Scheduler → END                           │
└─────────────────────────────────────────────────────────────┘
```

### MCP Server Architecture

The system uses two MCP servers as abstraction layers:

**MCP 1 - TradingView Data Server**
- Fetches OHLCV candle data
- Retrieves news articles and market sentiment
- Calculates technical indicators (RSI, MACD, EMA, SMA, Bollinger Bands, ATR, ADX, Stochastic)
- Provides 3 out of 4 timing indicators (limitation explicitly tracked)

**MCP 2 - MetaTrader 5 Execution Server**
- Manages MT5 connection lifecycle
- Executes buy/sell orders with SL/TP parameters
- Queries account information and positions
- Modifies and closes positions
- Provides symbol specifications for position sizing

### State Management

All workflow context flows through the `TraderState` TypedDict, which contains:
- Configuration: symbols, timeframes, run_id, timestamp
- Data: market_data, news_data, indicator_data
- Analysis: technical_analysis, news_analysis
- Decisions: strategy_decision, risk_assessment
- Execution: execution_result
- Scheduling: next_run_time, next_run_interval
- Logging: agent_trace (append-only), errors (append-only)

This centralized state enables:
- Complete workflow reproducibility
- Stateless agent implementations
- Comprehensive audit trails
- Easy debugging and testing

## Components and Interfaces

### Agent Components

#### 1. Orchestrator Agent
- **Role**: Central coordinator and decision-maker
- **LLM**: GPT-4o / Claude 3.5 Sonnet
- **Responsibilities**:
  - Initialize workflow with run_id and timestamp
  - Delegate tasks to specialized agents
  - Maintain agent_trace for audit trail
  - Handle errors gracefully without workflow termination
- **Interface**: Reads/writes full TraderState

#### 2. Data Collector Agent
- **Role**: Fetch comprehensive market data
- **LLM**: GPT-4o-mini (cost-optimized)
- **Tools**: All MCP 1 tools (tv_get_ohlcv, tv_get_news, tv_get_indicator, tv_get_available_indicators, tv_get_market_summary)
- **Input**: symbols, timeframes, indicator_list from state
- **Output**: Populates market_data, news_data, indicator_data
- **Error Handling**: Continues with available data if any request fails

#### 3. Technical Analyst Agent
- **Role**: Interpret technical indicators and price patterns
- **LLM**: GPT-4o
- **Tools**: tv_get_indicator, tv_get_ohlcv (for additional lookups)
- **Input**: indicator_data, market_data from state
- **Output**: technical_analysis containing:
  - trend: "bullish" | "bearish" | "neutral"
  - strength: 0.0 - 1.0
  - key_levels: {support: [], resistance: []}
  - signal: "buy" | "sell" | "hold"
  - indicators_used: list of indicators analyzed
  - indicators_missing: list of unavailable indicators
  - reasoning: detailed explanation

#### 4. News Analyst Agent
- **Role**: Analyze news sentiment and market impact
- **LLM**: GPT-4o
- **Tools**: tv_get_news (for additional lookups)
- **Input**: news_data from state
- **Output**: news_analysis containing:
  - sentiment: "bullish" | "bearish" | "neutral"
  - impact_level: "high" | "medium" | "low"
  - key_events: list of significant events
  - conflict_with_technical: boolean flag
  - reasoning: detailed explanation

#### 5. Strategy Evaluator Agent
- **Role**: Determine if trading strategy conditions are met (Yes/No gate)
- **LLM**: GPT-4o
- **Tools**: None (pure reasoning)
- **Input**: technical_analysis, news_analysis from state
- **Output**: strategy_decision containing:
  - strategy_triggered: boolean
  - direction: "buy" | "sell" | None
  - entry_type: "market" | "limit"
  - suggested_entry: price level
  - reasoning: detailed explanation
- **Routing**: If strategy_triggered is false, workflow routes to Scheduler

#### 6. Risk Manager Agent
- **Role**: Evaluate confidence and calculate position sizing
- **LLM**: GPT-4o
- **Tools**: mt5_get_account_info, mt5_get_positions, mt5_get_symbol_info
- **Input**: strategy_decision, technical_analysis, news_analysis from state
- **Output**: risk_assessment containing:
  - confidence: "high" | "medium" | "low"
  - confidence_score: 0.0 - 1.0
  - risk_reward_ratio: calculated ratio
  - position_size_lots: calculated volume
  - stop_loss: price level
  - take_profit: price level
  - max_risk_percent: risk per trade
  - reasons_for_rejection: list of concerns
  - reasoning: detailed explanation
- **Confidence Thresholds**:
  - high: score >= 0.75 → proceed to execution
  - medium: 0.50 <= score < 0.75 → log but skip execution
  - low: score < 0.50 → reject entirely
- **Missing Indicator Penalty**: Reduces confidence_score by 0.10 per missing timing indicator
- **Routing**: If confidence is not "high", workflow routes to Scheduler

#### 7. Trade Executor Agent
- **Role**: Execute trades with exact risk parameters
- **LLM**: GPT-4o-mini (execution-focused)
- **Tools**: All MCP 2 tools (mt5_buy, mt5_sell, mt5_close_position, etc.)
- **Input**: risk_assessment, strategy_decision from state
- **Output**: execution_result containing:
  - success: boolean
  - ticket: order ticket number
  - error: error information if failed
- **Constraints**:
  - MUST use exact parameters from risk_assessment
  - MUST NOT make independent trading decisions
  - MUST execute at most one trade per cycle
  - Marks cycle as executed to prevent duplicate trades

#### 8. Scheduler Component
- **Role**: Manage cron-based execution timing
- **LLM**: None (deterministic logic)
- **Input**: Complete TraderState to determine next interval
- **Output**: next_run_time, next_run_interval
- **Scheduling Logic**:
  - Trade just executed → 5 minutes
  - Strategy triggered but low confidence → 15 minutes
  - No strategy triggered → 30 minutes
  - Outside market hours → next market open time
- **Implementation**: Uses APScheduler or custom cron manager

### MCP Server Interfaces

#### MCP 1 - TradingView Data Server

**Tools**:
- `tv_get_ohlcv(symbol, timeframe, count)` → List[Candle]
- `tv_get_news(symbol, limit)` → List[NewsItem]
- `tv_get_indicator(symbol, timeframe, indicator_name, params)` → Dict
- `tv_get_available_indicators()` → List[str]
- `tv_get_market_summary(symbol)` → Dict

**Implementation Options**:
- tvDatafeed library (TradingView unofficial API)
- yfinance library (Yahoo Finance)
- Alpha Vantage API
- Twelve Data API

**Supported Indicators**: RSI, MACD, EMA, SMA, Bollinger Bands, ATR, ADX, Stochastic

#### MCP 2 - MetaTrader 5 Execution Server

**Tools**:
- `mt5_initialize(login, password, server, path)` → bool
- `mt5_get_account_info()` → AccountInfo
- `mt5_get_positions(symbol?)` → List[Position]
- `mt5_get_orders(symbol?)` → List[Order]
- `mt5_buy(symbol, volume, sl, tp, comment, magic)` → OrderSendResult
- `mt5_sell(symbol, volume, sl, tp, comment, magic)` → OrderSendResult
- `mt5_close_position(ticket)` → bool
- `mt5_close_all(symbol?)` → int
- `mt5_modify_position(ticket, sl, tp)` → bool
- `mt5_get_symbol_info(symbol)` → SymbolInfo
- `mt5_get_ticks(symbol, count)` → List[Tick]
- `mt5_shutdown()` → bool

**Implementation**: Wrapper around MetaTrader5 Python API with singleton pattern

### Workflow Routing Logic

The LangGraph workflow uses conditional edges for decision gates:

**Strategy Gate** (after Strategy_Evaluator):
```python
def route_strategy(state: TraderState) -> Literal["yes", "no"]:
    return "yes" if state["strategy_decision"]["strategy_triggered"] else "no"
```
- "yes" → Risk_Manager
- "no" → Scheduler

**Risk Gate** (after Risk_Manager):
```python
def route_risk(state: TraderState) -> Literal["high_confidence", "low_confidence"]:
    return (
        "high_confidence"
        if state["risk_assessment"]["confidence"] == "high"
        else "low_confidence"
    )
```
- "high_confidence" → Trade_Executor
- "low_confidence" → Scheduler

## Data Models

### TraderState (LangGraph State)

```python
from typing import TypedDict, Annotated
from operator import add

class TraderState(TypedDict):
    # Configuration
    symbols: list[str]              # Trading symbols (e.g., ["EURUSD", "GBPUSD"])
    timeframes: list[str]           # Analysis timeframes (e.g., ["1h", "4h"])
    run_id: str                     # Unique workflow execution ID
    timestamp: str                  # Workflow start timestamp (ISO 8601)
    
    # Data
    market_data: dict               # OHLCV candles by symbol/timeframe
    news_data: list[dict]           # News articles with sentiment
    indicator_data: dict            # Technical indicator values
    
    # Analysis
    technical_analysis: dict        # Technical assessment output
    news_analysis: dict             # News sentiment assessment output
    
    # Decisions
    strategy_decision: dict         # Strategy evaluation output
    risk_assessment: dict           # Risk management output
    
    # Execution
    execution_result: dict          # Trade execution outcome
    
    # Scheduling
    next_run_time: str              # Next scheduled execution (ISO 8601)
    next_run_interval: str          # Interval description (e.g., "5 minutes")
    
    # Logging (append-only)
    agent_trace: Annotated[list[str], add]  # Agent invocation history
    errors: Annotated[list[str], add]       # Error messages
```

### MCP 2 Data Models (Pydantic)

```python
from pydantic import BaseModel
from typing import Optional
from enum import Enum

class OrderType(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    BUY_LIMIT = "BUY_LIMIT"
    SELL_LIMIT = "SELL_LIMIT"
    BUY_STOP = "BUY_STOP"
    SELL_STOP = "SELL_STOP"

class AccountInfo(BaseModel):
    login: int
    balance: float
    equity: float
    margin: float
    free_margin: float
    margin_level: float
    currency: str
    leverage: int

class Position(BaseModel):
    ticket: int
    symbol: str
    volume: float
    type: OrderType
    price_open: float
    price_current: float
    sl: Optional[float]
    tp: Optional[float]
    profit: float
    comment: str
    magic: int
    time_open: str

class OrderRequest(BaseModel):
    symbol: str
    volume: float
    order_type: OrderType
    price: Optional[float] = None
    sl: Optional[float] = None
    tp: Optional[float] = None
    comment: str = ""
    magic: int = 0
    deviation: int = 20

class ExecutionResult(BaseModel):
    success: bool
    ticket: Optional[int] = None
    error_code: Optional[int] = None
    error_message: Optional[str] = None
    order_id: Optional[int] = None

class SymbolInfo(BaseModel):
    symbol: str
    bid: float
    ask: float
    spread: float
    pip_size: float
    min_lot: float
    max_lot: float
    lot_step: float
    digits: int
    trade_mode: str
```

### Agent Output Schemas

**Technical Analysis Output**:
```python
{
    "trend": "bullish" | "bearish" | "neutral",
    "strength": 0.0 - 1.0,
    "key_levels": {
        "support": [1.0800, 1.0750],
        "resistance": [1.0900, 1.0950]
    },
    "signal": "buy" | "sell" | "hold",
    "indicators_used": ["RSI", "MACD", "EMA"],
    "indicators_missing": ["Bollinger Bands"],
    "reasoning": "Detailed technical analysis explanation..."
}
```

**News Analysis Output**:
```python
{
    "sentiment": "bullish" | "bearish" | "neutral",
    "impact_level": "high" | "medium" | "low",
    "key_events": ["Fed rate decision: hawkish", "ECB maintains rates"],
    "conflict_with_technical": False,
    "reasoning": "Detailed news analysis explanation..."
}
```

**Strategy Decision Output**:
```python
{
    "strategy_triggered": True | False,
    "direction": "buy" | "sell" | None,
    "entry_type": "market" | "limit",
    "suggested_entry": 1.0850,
    "reasoning": "Detailed strategy evaluation explanation..."
}
```

**Risk Assessment Output**:
```python
{
    "confidence": "high" | "medium" | "low",
    "confidence_score": 0.85,
    "risk_reward_ratio": 2.5,
    "position_size_lots": 0.1,
    "stop_loss": 1.0820,
    "take_profit": 1.0920,
    "max_risk_percent": 1.0,
    "reasons_for_rejection": [],
    "reasoning": "Detailed risk assessment explanation..."
}
```


## Correctness Properties

A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.

### Property 1: Workflow Initialization Completeness

For any workflow execution, when the Orchestrator initializes TraderState, the state SHALL contain run_id, timestamp, symbols, and timeframes fields with valid values.

**Validates: Requirements 1.2**

### Property 2: Agent Trace Completeness

For any workflow execution, the agent_trace SHALL contain entries for all agents that were invoked during the workflow.

**Validates: Requirements 1.6**

### Property 3: Error Recording and Continuation

For any agent that encounters an error, the error SHALL be recorded in TraderState.errors and the workflow SHALL continue to completion.

**Validates: Requirements 1.7, 15.1**

### Property 4: Data Collection Completeness

For any set of configured symbols, after Data_Collector execution, TraderState SHALL contain market_data, news_data, and indicator_data for all requested symbols and indicators.

**Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5, 2.6**

### Property 5: Data Collection Error Resilience

For any MCP_1 request that fails, the Data_Collector SHALL record the error in TraderState.errors and continue collecting remaining data.

**Validates: Requirements 2.7**

### Property 6: Technical Analysis Output Schema

For any Technical_Analyst execution, the technical_analysis output SHALL contain all required fields: trend (bullish/bearish/neutral), strength (0.0-1.0), key_levels (support/resistance arrays), signal (buy/sell/hold), indicators_used (list), indicators_missing (list), and reasoning (string).

**Validates: Requirements 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8**

### Property 7: News Analysis Output Schema

For any News_Analyst execution, the news_analysis output SHALL contain all required fields: sentiment (bullish/bearish/neutral), impact_level (high/medium/low), key_events (list), conflict_with_technical (boolean), and reasoning (string).

**Validates: Requirements 4.2, 4.3, 4.4, 4.5, 4.6**

### Property 8: Strategy Decision Output Schema

For any Strategy_Evaluator execution, the strategy_decision output SHALL contain strategy_triggered (boolean), and when strategy_triggered is true, SHALL also contain direction (buy/sell), entry_type (market/limit), suggested_entry (numeric), and reasoning (string).

**Validates: Requirements 5.2, 5.3, 5.4, 5.5, 5.6**

### Property 9: Risk Assessment Output Schema

For any Risk_Manager execution, the risk_assessment output SHALL contain all required fields: confidence (high/medium/low), confidence_score (0.0-1.0), risk_reward_ratio (numeric), position_size_lots (numeric), stop_loss (numeric), take_profit (numeric), max_risk_percent (numeric), reasons_for_rejection (list), and reasoning (string).

**Validates: Requirements 6.5, 6.6, 6.10, 6.11, 6.12, 6.13, 6.15**

### Property 10: Confidence Score to Confidence Level Mapping

For any Risk_Manager execution, the confidence level SHALL be "high" when confidence_score >= 0.75, "medium" when 0.50 <= confidence_score < 0.75, and "low" when confidence_score < 0.50.

**Validates: Requirements 6.7, 6.8, 6.9**

### Property 11: Missing Indicator Confidence Penalty

For any Risk_Manager execution, when timing indicators are missing, the confidence_score SHALL be reduced by 0.10 for each missing indicator, and the reasoning SHALL mention the missing indicators.

**Validates: Requirements 6.14, 19.3, 19.4, 19.5**

### Property 12: Trade Execution Confidence Gate

For any Trade_Executor invocation, trades SHALL only be executed when TraderState.risk_assessment.confidence equals "high".

**Validates: Requirements 7.1**

### Property 13: Trade Direction Correctness

For any Trade_Executor execution, when strategy_decision.direction is "buy", a buy order SHALL be placed, and when strategy_decision.direction is "sell", a sell order SHALL be placed.

**Validates: Requirements 7.2, 7.3**

### Property 14: Trade Parameter Fidelity

For any Trade_Executor execution, the executed trade SHALL use the exact position_size_lots, stop_loss, and take_profit values from TraderState.risk_assessment without modification.

**Validates: Requirements 7.4, 7.5, 7.6, 7.7**

### Property 15: Execution Result Completeness

For any Trade_Executor execution, the execution_result SHALL contain success (boolean), and when success is true, SHALL contain ticket (numeric), and when success is false, SHALL contain error information.

**Validates: Requirements 7.8**

### Property 16: Single Trade Per Cycle Constraint

For any workflow cycle, at most one trade SHALL be executed, and once a trade is executed, the cycle SHALL be marked as executed to prevent additional executions.

**Validates: Requirements 7.9, 18.1, 18.2, 18.3**

### Property 17: Execution Flag Reset

For any new workflow cycle, the execution flag SHALL be reset to allow trade execution in the new cycle.

**Validates: Requirements 18.4**

### Property 18: Dynamic Scheduling Based on Execution

For any Scheduler execution where a trade was just executed (execution_result.success is true), the next_run_interval SHALL be set to 5 minutes.

**Validates: Requirements 9.2**

### Property 19: Dynamic Scheduling Based on Low Confidence

For any Scheduler execution where strategy_triggered is true but confidence is not "high", the next_run_interval SHALL be set to 15 minutes.

**Validates: Requirements 9.3**

### Property 20: Dynamic Scheduling Based on No Strategy

For any Scheduler execution where strategy_triggered is false, the next_run_interval SHALL be set to 30 minutes.

**Validates: Requirements 9.4**

### Property 21: Market Hours Scheduling

For any Scheduler execution where current time is outside market hours, the next_run_time SHALL be set to the next market open time.

**Validates: Requirements 9.5**

### Property 22: Scheduler Output Completeness

For any Scheduler execution, TraderState SHALL be populated with next_run_time and next_run_interval.

**Validates: Requirements 9.1, 9.6**

### Property 23: MCP_1 OHLCV Response Format

For any call to tv_get_ohlcv, the response SHALL be a list of candle objects containing OHLCV data.

**Validates: Requirements 10.6**

### Property 24: MCP_1 News Response Format

For any call to tv_get_news, the response SHALL be a list of news item objects.

**Validates: Requirements 10.7**

### Property 25: MCP_1 Indicator Response Format

For any call to tv_get_indicator, the response SHALL be a dictionary containing indicator values.

**Validates: Requirements 10.8**

### Property 26: TraderState Schema Completeness

For any TraderState instance, it SHALL contain all required fields: symbols, timeframes, run_id, timestamp, market_data, news_data, indicator_data, technical_analysis, news_analysis, strategy_decision, risk_assessment, execution_result, next_run_time, next_run_interval, agent_trace, and errors.

**Validates: Requirements 12.1-12.16**

### Property 27: Paper Trading Mode Connection

For any system execution where paper trading mode is enabled, the MCP_2 connection SHALL be to a demo MT5 account, and all trade logs SHALL contain a paper trading indicator.

**Validates: Requirements 13.1, 13.2, 13.3**

### Property 28: Human-in-the-Loop Pause

For any workflow execution where human-in-the-loop is enabled, the workflow SHALL pause before Trade_Executor and wait for human approval or rejection.

**Validates: Requirements 14.1**

### Property 29: Human-in-the-Loop Routing

For any workflow execution where human-in-the-loop is enabled, when human approves, the workflow SHALL proceed to Trade_Executor, and when human rejects, the workflow SHALL route to Scheduler.

**Validates: Requirements 14.3, 14.4**

### Property 30: MCP_1 Connection Retry

For any MCP_1 connection failure, the Data_Collector SHALL retry up to 3 times with exponential backoff before recording the error.

**Validates: Requirements 15.2**

### Property 31: MCP_2 Connection Failure Handling

For any MCP_2 connection failure, the Trade_Executor SHALL record the error in TraderState.errors and skip trade execution.

**Validates: Requirements 15.3**

### Property 32: Agent Timeout Handling

For any agent timeout, the Orchestrator SHALL record the timeout in TraderState.errors and continue the workflow.

**Validates: Requirements 15.4**

### Property 33: Critical Error Recovery

For any critical error that prevents workflow completion, the Orchestrator SHALL route to Scheduler with an extended interval.

**Validates: Requirements 15.5**

### Property 34: Error Logging Completeness

For any error recorded in the system, the log entry SHALL contain timestamp, agent name, and error details.

**Validates: Requirements 15.6, 16.8**

### Property 35: Workflow Logging Completeness

For any workflow execution, the system SHALL log: workflow execution with run_id and timestamp, all agent invocations, all data collection requests and responses, all analysis outputs with reasoning, all strategy decisions with reasoning, all risk assessments with confidence scores, all trade executions with ticket numbers and parameters, and all errors with stack traces.

**Validates: Requirements 16.1, 16.2, 16.3, 16.4, 16.5, 16.6, 16.7, 16.8**

### Property 36: Configuration Validation

For any system startup, all configuration values SHALL be loaded from environment variables and validated, including: symbols, timeframes, max_risk_per_trade_pct, default_risk_reward_ratio, confidence_threshold, default_analysis_interval, market_open_hour, market_close_hour, LLM API keys, and MT5 connection parameters.

**Validates: Requirements 17.1, 17.2, 17.3, 17.4, 17.5, 17.6, 17.7, 17.8, 17.9, 17.10, 17.11**

## Error Handling

### Error Categories

The system handles errors at multiple levels:

1. **MCP Connection Errors**
   - MCP_1 (TradingView): Retry up to 3 times with exponential backoff (1s, 2s, 4s)
   - MCP_2 (MetaTrader 5): Record error and skip execution
   - Both: Continue workflow with available data

2. **Agent Execution Errors**
   - Record error in TraderState.errors with timestamp and agent name
   - Continue workflow to next agent
   - If critical error prevents completion, route to Scheduler with extended interval (60 minutes)

3. **Agent Timeout Errors**
   - Default timeout: 60 seconds per agent
   - Record timeout in TraderState.errors
   - Continue workflow

4. **Trade Execution Errors**
   - Record in execution_result with error_code and error_message
   - Do not retry (single execution per cycle)
   - Route to Scheduler for next cycle

### Error Recovery Strategy

The system prioritizes workflow continuation over perfection:
- Partial data is acceptable (e.g., missing indicators reduce confidence but don't block analysis)
- Failed data collection continues with available data
- Agent errors are logged but don't terminate the workflow
- Only critical errors that prevent any meaningful analysis trigger extended scheduling

### Error Logging

All errors are logged with:
- ISO 8601 timestamp
- Agent name or component
- Error type and message
- Stack trace (for exceptions)
- Current TraderState snapshot (for debugging)

Logs are written to:
- Console (stdout/stderr)
- File (configurable path, default: ./logs/trader_ai.log)
- Structured JSON format for parsing

## Testing Strategy

### Dual Testing Approach

The system requires both unit testing and property-based testing for comprehensive coverage:

**Unit Tests** focus on:
- Specific examples demonstrating correct behavior
- Integration points between components (MCP servers, LangGraph nodes)
- Edge cases (empty data, missing fields, boundary values)
- Error conditions (connection failures, timeouts, invalid data)
- Configuration loading and validation

**Property-Based Tests** focus on:
- Universal properties that hold for all inputs
- Comprehensive input coverage through randomization
- Invariants that must be maintained across workflow executions
- Schema validation for all agent outputs
- State transitions and workflow routing logic

### Property-Based Testing Configuration

The system uses property-based testing to validate correctness properties:

**Library Selection**:
- Python: Hypothesis (recommended)
- Alternative: pytest-quickcheck

**Test Configuration**:
- Minimum 100 iterations per property test (due to randomization)
- Configurable seed for reproducibility
- Shrinking enabled to find minimal failing examples

**Test Tagging**:
Each property test MUST include a comment tag referencing the design property:
```python
# Feature: trader-ai-system, Property 1: Workflow Initialization Completeness
@given(symbols=st.lists(st.text()), timeframes=st.lists(st.text()))
def test_workflow_initialization_completeness(symbols, timeframes):
    state = initialize_workflow(symbols, timeframes)
    assert "run_id" in state
    assert "timestamp" in state
    assert state["symbols"] == symbols
    assert state["timeframes"] == timeframes
```

### Test Coverage Requirements

**Unit Test Coverage**:
- MCP server wrappers: 90%+ coverage
- Agent implementations: 85%+ coverage
- Workflow routing logic: 100% coverage
- Error handling paths: 90%+ coverage

**Property Test Coverage**:
- All 36 correctness properties MUST have corresponding property tests
- Each property test MUST run minimum 100 iterations
- Each property test MUST be tagged with property number and text

### Integration Testing

Integration tests validate end-to-end workflow execution:
- Mock MCP servers for deterministic testing
- Test complete workflow paths (strategy triggered → high confidence → execution)
- Test all routing paths (no strategy, low confidence, errors)
- Test paper trading mode
- Test human-in-the-loop mode
- Test error recovery and retry logic

### Testing Anti-Patterns to Avoid

- Don't write too many unit tests for input variations (use property tests instead)
- Don't test LLM output quality (test schema compliance only)
- Don't test workflow orchestration logic with unit tests (use integration tests)
- Don't mock TraderState (use real instances for testing)

### Test Data Generation

Property tests use generators for:
- Random symbols (valid forex pairs, stocks, crypto)
- Random timeframes (1m, 5m, 15m, 1h, 4h, 1d)
- Random OHLCV data (realistic price movements)
- Random news articles (various sentiments)
- Random indicator values (within valid ranges)
- Random account balances and positions
- Random confidence scores (0.0-1.0)

Generators MUST produce valid data that respects domain constraints:
- Prices: positive floats with appropriate precision
- Volumes: positive floats within lot size limits
- Timestamps: valid ISO 8601 strings
- Enums: only valid enum values
- Lists: non-empty where required

