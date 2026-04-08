# Trader AI — Multi-Agent Autonomous Trading System
> Steering file for you!.
> Yes, you the Genius.
## 1. System Overview

Trader AI is a fully autonomous trading system powered by a multi-agent architecture built on **LangChain** and **LangGraph**. It uses two **Model Context Protocol (MCP)** servers to interface with external systems — TradingView for data and MetaTrader 5 for execution. The Orchestrator agent coordinates the entire workflow, making strategic decisions and delegating tasks to specialized sub-agents.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        TRADER AI SYSTEM                                 │
│                                                                         │
│  ┌─────────────┐                                                        │
│  │  Scheduler   │──(cron wake-up)──▶┌──────────────────┐               │
│  │  Agent (A1)  │◀──(set next run)──│                  │               │
│  └─────────────┘                    │   ORCHESTRATOR   │               │
│                                     │     AGENT        │               │
│  ┌──────────────────────────┐       │                  │               │
│  │       MCP 1               │◀──────┼─▶┌────────────┐  │               │
│  │   (TradingView)           │       │  │  Data       │  │               │
│  │                          │       │  │  Collector  │  │               │
│  │  • Price Data (OHLCV)    │       │  │  Agent      │  │               │
│  │  • News Data             │       │  └────────────┘  │               │
│  │  • Timing Indicators     │       │                  │               │
│  │    (3/4 available)       │       │  ┌────────────┐  │               │
│  └──────────────────────────┘       │  │  Technical  │  │               │
│                                     │  │  Analyst    │  │               │
│                                     │  │  Agent      │  │               │
│                                     │  └────────────┘  │               │
│                                     │                  │               │
│                                     │  ┌────────────┐  │               │
│                                     │  │   News      │  │               │
│                                     │  │  Analyst    │  │               │
│                                     │  │  Agent      │  │               │
│                                     │  └────────────┘  │               │
│                                     │                  │               │
│                                     │         ┌───────▼───────┐        │
│                                     │         │   Strategy     │        │
│                                     │         │   Evaluator    │        │
│                                     │         │   Agent        │        │
│                                     │         │  (Yes / No?)   │        │
│                                     │         └───────┬───────┘        │
│                                     │                 │                │
│                                     │          Yes    │    No           │
│                                     │                 ▼                │
│                                     │         ┌───────────────┐        │
│                                     │         │   Risk        │        │
│                                     │         │   Manager     │        │
│                                     │         │   Agent       │        │
│                                     │         │(High Conf?)   │        │
│                                     │         └───────┬───────┘        │
│                                     │                 │                │
│                                     │     High        │    Low         │
│                                     │     Conf.       ▼    Conf.        │
│                                     │  ┌─────────────────┐    │         │
│                                     │  │  Trade          │    │         │
│                                     │  │  Executor       │    │         │
│                                     │  │  Agent          │    │         │
│                                     │  └────────┬────────┘    │         │
│                                     │           │             │         │
│                                     │           ▼             │         │
│                                     │  ┌─────────────────┐    │         │
│                                     │  │     MCP 2        │    │         │
│                                     │  │ (MetaTrader 5)   │    │         │
│                                     │  │                  │    │         │
│                                     │  │  • Place Orders  │    │         │
│                                     │  │  • Close Orders  │    │         │
│                                     │  │  • Modify SL/TP  │    │         │
│                                     │  │  • Get Positions │    │         │
│                                     │  │  • Account Info  │    │         │
│                                     │  └─────────────────┘    │         │
│                                     │                          │         │
│                                     └──────────┬───────────────┘         │
│                                                │                         │
│                                    No / Low ◀──┘                         │
│                                    Confidence                            │
│                                        │                                │
│                                        ▼                                │
│                                   ┌──────────┐                          │
│                                   │Scheduler │──(cron: next analysis)──▶│
│                                   │ Agent A1 │                          │
│                                   └──────────┘                          │
│                                                                        │
└─────────────────────────────────────────────────────────────────────────┘
```

## 2. MCP Server Definitions

### MCP 1 — TradingView Data Server

Responsible for fetching all market data, news, and technical indicators.

| Tool Name | Description | Input Parameters | Output |
|-----------|-------------|------------------|--------|
| `tv_get_ohlcv` | Get OHLCV candle data | `symbol`, `timeframe`, `count` | `List[Candle]` |
| `tv_get_news` | Get latest news for symbol | `symbol`, `limit` | `List[NewsItem]` |
| `tv_get_indicator` | Get technical indicator value | `symbol`, `timeframe`, `indicator_name`, `params` | `Dict` |
| `tv_get_available_indicators` | List available indicators | — | `List[str]` |
| `tv_get_market_summary` | Get market overview/sentiment | `symbol` | `Dict` |

**Indicator Notes:** The system has access to 3 out of 4 timing indicators as noted in the architecture. The missing indicator should be flagged in strategy evaluation as a confidence reducer.

### MCP 2 — MetaTrader 5 Execution Server

Responsible for all order management and account interactions via the MT5 Python API.

| Tool Name | Description | Input Parameters | Output |
|-----------|-------------|------------------|--------|
| `mt5_initialize` | Initialize MT5 connection | `login`, `password`, `server`, `path` | `bool` |
| `mt5_get_account_info` | Get account balance, equity, margin | — | `AccountInfo` |
| `mt5_get_positions` | Get open positions | `symbol?` | `List[Position]` |
| `mt5_get_orders` | Get pending orders | `symbol?` | `List[Order]` |
| `mt5_order_send` | Place/modify/close an order | `order_request: OrderRequest` | `OrderSendResult` |
| `mt5_buy` | Open a buy position | `symbol`, `volume`, `sl`, `tp`, `comment`, `magic` | `OrderSendResult` |
| `mt5_sell` | Open a sell position | `symbol`, `volume`, `sl`, `tp`, `comment`, `magic` | `OrderSendResult` |
| `mt5_close_position` | Close a position by ticket | `ticket` | `bool` |
| `mt5_close_all` | Close all open positions | `symbol?` | `int` (count closed) |
| `mt5_modify_position` | Modify SL/TP of position | `ticket`, `sl`, `tp` | `bool` |
| `mt5_get_symbol_info` | Get symbol specifications | `symbol` | `SymbolInfo` |
| `mt5_get_ticks` | Get recent tick data | `symbol`, `count` | `List[Tick]` |
| `mt5_shutdown` | Shutdown MT5 connection | — | `bool` |

---

## 3. Agent Definitions

### 3.1 Orchestrator Agent

| Property | Value |
|----------|-------|
| **Role** | Central decision-maker and task delegator |
| **LLM** | GPT-4o / Claude 3.5 Sonnet (high reasoning) |
| **Framework** | LangGraph `StateGraph` — acts as the supervisor node |
| **Tools** | None directly — delegates to sub-agents via tool calls |
| **State** | Full `TraderState` (see Section 5) |
| **Behavior** | Reads current state, decides which agent to invoke next, evaluates final strategy and risk decisions |

**Decision Logic (encoded in prompt + graph edges):**
```
START → data_collection → analysis → strategy_eval
  → [No] → schedule_next
  → [Yes] → risk_check
      → [Low Confidence] → schedule_next
      → [High Confidence] → trade_execution → schedule_next
```

### 3.2 Data Collector Agent

| Property | Value |
|----------|-------|
| **Role** | Fetch all required market data via MCP 1 |
| **LLM** | GPT-4o-mini (fast, low cost) |
| **Framework** | LangChain `create_tool_calling_agent` |
| **Tools** | All MCP 1 tools |
| **Input** | `symbols`, `timeframes`, `indicator_list` from state |
| **Output** | Populates `state.market_data`, `state.news_data`, `state.indicator_data` |

### 3.3 Technical Analyst Agent

| Property | Value |
|----------|-------|
| **Role** | Interpret technical indicators and price action |
| **LLM** | GPT-4o |
| **Framework** | LangChain `create_tool_calling_agent` |
| **Tools** | `tv_get_indicator`, `tv_get_ohlcv` (for additional lookups) |
| **Input** | `state.indicator_data`, `state.market_data` |
| **Output** | Populates `state.technical_analysis` with structured assessment |

**Output Structure:**
```python
{
    "trend": "bullish" | "bearish" | "neutral",
    "strength": 0.0 - 1.0,
    "key_levels": {"support": [...], "resistance": [...]},
    "signal": "buy" | "sell" | "hold",
    "indicators_used": ["RSI", "MACD", "EMA"],
    "indicators_missing": ["Bollinger Bands"],
    "reasoning": "..."
}
```

### 3.4 News Analyst Agent

| Property | Value |
|----------|-------|
| **Role** | Analyze news sentiment and impact on trade decisions |
| **LLM** | GPT-4o |
| **Framework** | LangChain `create_tool_calling_agent` |
| **Tools** | `tv_get_news` (for additional lookups if needed) |
| **Input** | `state.news_data` |
| **Output** | Populates `state.news_analysis` with sentiment assessment |

**Output Structure:**
```python
{
    "sentiment": "bullish" | "bearish" | "neutral",
    "impact_level": "high" | "medium" | "low",
    "key_events": ["Fed rate decision: hawkish", "..."],
    "conflict_with_technical": False,
    "reasoning": "..."
}
```

### 3.5 Strategy Evaluator Agent

| Property | Value |
|----------|-------|
| **Role** | Determines if a trade strategy is triggered (Yes/No gate) |
| **LLM** | GPT-4o |
| **Framework** | LangChain `create_tool_calling_agent` (no external tools) |
| **Tools** | None — pure reasoning over state |
| **Input** | `state.technical_analysis`, `state.news_analysis` |
| **Output** | Populates `state.strategy_decision` |

**Output Structure:**
```python
{
    "strategy_triggered": True | False,
    "direction": "buy" | "sell" | None,
    "entry_type": "market" | "limit",
    "suggested_entry": 1.0850,
    "reasoning": "..."
}
```

### 3.6 Risk Manager Agent

| Property | Value |
|----------|-------|
| **Role** | Evaluates confidence and calculates position sizing |
| **LLM** | GPT-4o |
| **Framework** | LangChain `create_tool_calling_agent` |
| **Tools** | `mt5_get_account_info`, `mt5_get_positions`, `mt5_get_symbol_info` |
| **Input** | `state.strategy_decision`, `state.technical_analysis`, `state.news_analysis` |
| **Output** | Populates `state.risk_assessment` |

**Output Structure:**
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
    "reasoning": "..."
}
```

**Confidence Thresholds:**
- `high`: score >= 0.75 → proceed to execution
- `medium`: 0.50 <= score < 0.75 → log but do NOT execute
- `low`: score < 0.50 → reject entirely

### 3.7 Trade Executor Agent

| Property | Value |
|----------|-------|
| **Role** | Execute trades on MT5 via MCP 2 |
| **LLM** | GPT-4o-mini (execution-focused, minimal reasoning) |
| **Framework** | LangChain `create_tool_calling_agent` |
| **Tools** | All MCP 2 tools |
| **Input** | `state.risk_assessment`, `state.strategy_decision` |
| **Output** | Populates `state.execution_result` |

**Behavior:** This agent is tightly constrained — it MUST follow the risk parameters exactly. It should NOT make independent trading decisions.

### 3.8 Scheduler Agent (A1)

| Property | Value |
|----------|-------|
| **Role** | Manage cron-based wake-up schedules for the orchestrator |
| **LLM** | None — deterministic logic |
| **Framework** | Python `APScheduler` / custom cron manager |
| **Tools** | None |
| **Input** | `state.analysis_result` (to determine next interval) |
| **Output** | Sets cron job; populates `state.next_run_time` |

**Scheduling Logic:**
```python
def determine_next_interval(state: TraderState) -> str:
    """
    Dynamic interval based on market conditions:
    - High volatility / active trade just executed → 5 min
    - Strategy triggered but low confidence → 15 min
    - No strategy triggered, quiet market → 30 min
    - Outside market hours → next market open
    """
```

---

## 4. LangGraph Workflow Definition

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Literal, Annotated
from operator import add


class TraderState(TypedDict):
    # Configuration
    symbols: list[str]
    timeframes: list[str]
    run_id: str
    timestamp: str

    # Data
    market_data: dict
    news_data: list[dict]
    indicator_data: dict

    # Analysis
    technical_analysis: dict
    news_analysis: dict

    # Decisions
    strategy_decision: dict
    risk_assessment: dict

    # Execution
    execution_result: dict

    # Scheduling
    next_run_time: str
    next_run_interval: str

    # Logging
    agent_trace: Annotated[list[str], add]
    errors: Annotated[list[str], add]


def build_graph() -> StateGraph:
    graph = StateGraph(TraderState)

    # Add nodes
    graph.add_node("orchestrator", orchestrator_node)
    graph.add_node("data_collector", data_collector_node)
    graph.add_node("technical_analyst", technical_analyst_node)
    graph.add_node("news_analyst", news_analyst_node)
    graph.add_node("strategy_evaluator", strategy_evaluator_node)
    graph.add_node("risk_manager", risk_manager_node)
    graph.add_node("trade_executor", trade_executor_node)
    graph.add_node("scheduler", scheduler_node)

    # Set entry point
    graph.set_entry_point("orchestrator")

    # Orchestrator → Data Collection
    graph.add_edge("orchestrator", "data_collector")

    # Data Collection → Parallel Analysis
    graph.add_edge("data_collector", "technical_analyst")
    graph.add_edge("data_collector", "news_analyst")

    # Analysis → Strategy Evaluation (join)
    graph.add_edge("technical_analyst", "strategy_evaluator")
    graph.add_edge("news_analyst", "strategy_evaluator")

    # Strategy gate
    graph.add_conditional_edges(
        "strategy_evaluator",
        route_strategy,
        {
            "yes": "risk_manager",
            "no": "scheduler",
        }
    )

    # Risk gate
    graph.add_conditional_edges(
        "risk_manager",
        route_risk,
        {
            "high_confidence": "trade_executor",
            "low_confidence": "scheduler",
        }
    )

    # Execution → Scheduler
    graph.add_edge("trade_executor", "scheduler")

    # Scheduler → END (cron will restart)
    graph.add_edge("scheduler", END)

    return graph.compile()


def route_strategy(state: TraderState) -> Literal["yes", "no"]:
    return "yes" if state["strategy_decision"]["strategy_triggered"] else "no"


def route_risk(state: TraderState) -> Literal["high_confidence", "low_confidence"]:
    return (
        "high_confidence"
        if state["risk_assessment"]["confidence"] == "high"
        else "low_confidence"
    )
```

---

## 5. MT5 API Wrapper Specification

The following wrapper classes must be implemented as the backend for MCP 2 tools.

```
project-root/
├── mcp_servers/
│   └── mt5_server/
│       ├── server.py              # MCP server entry point
│       ├── mt5_wrapper.py         # Core MT5 API wrapper
│       ├── models.py              # Pydantic models for MT5 data
│       └── tools.py               # Tool definitions
```

### `mt5_wrapper.py` — Required Interface

```python
import MetaTrader5 as mt5
from typing import Optional
from pydantic import BaseModel


class MT5Wrapper:
    """Singleton wrapper around MetaTrader5 Python API."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def initialize(
        self,
        login: int,
        password: str,
        server: str,
        path: Optional[str] = None,
        timeout: int = 30000,
    ) -> bool:
        """Initialize MT5 connection. Must be called before any other method."""
        ...

    def shutdown(self) -> bool:
        """Shutdown MT5 connection."""
        ...

    @property
    def is_connected(self) -> bool:
        """Check if MT5 is connected."""
        ...

    def get_account_info(self) -> dict:
        """Return account balance, equity, margin, free margin, margin level."""
        ...

    def get_positions(self, symbol: Optional[str] = None) -> list[dict]:
        """Get all open positions, optionally filtered by symbol."""
        ...

    def get_orders(self, symbol: Optional[str] = None) -> list[dict]:
        """Get pending orders, optionally filtered by symbol."""
        ...

    def get_symbol_info(self, symbol: str) -> dict:
        """Get symbol specification: pip size, min lot, max lot, etc."""
        ...

    def get_ticks(self, symbol: str, count: int = 100) -> list[dict]:
        """Get recent tick data."""
        ...

    def buy(
        self,
        symbol: str,
        volume: float,
        sl: Optional[float] = None,
        tp: Optional[float] = None,
        comment: str = "",
        magic: int = 0,
        deviation: int = 20,
    ) -> dict:
        """
        Open a BUY position.
        Returns: {"success": bool, "ticket": int|None, "error": str|None}
        """
        ...

    def sell(
        self,
        symbol: str,
        volume: float,
        sl: Optional[float] = None,
        tp: Optional[float] = None,
        comment: str = "",
        magic: int = 0,
        deviation: int = 20,
    ) -> dict:
        """
        Open a SELL position.
        Returns: {"success": bool, "ticket": int|None, "error": str|None}
        """
        ...

    def close_position(self, ticket: int) -> dict:
        """Close a specific position by ticket."""
        ...

    def close_all(self, symbol: Optional[str] = None) -> dict:
        """Close all open positions, optionally filtered by symbol."""
        ...

    def modify_position(
        self, ticket: int, sl: Optional[float] = None, tp: Optional[float] = None
    ) -> dict:
        """Modify stop loss and/or take profit of an open position."""
        ...

    def place_limit_order(
        self,
        symbol: str,
        order_type: str,  # "buy_limit" | "sell_limit" | "buy_stop" | "sell_stop"
        volume: float,
        price: float,
        sl: Optional[float] = None,
        tp: Optional[float] = None,
        comment: str = "",
        magic: int = 0,
    ) -> dict:
        """Place a pending order."""
        ...

    def cancel_order(self, ticket: int) -> dict:
        """Cancel a pending order."""
        ...
```

### `models.py` — Pydantic Schemas

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

---

## 6. TradingView MCP Server Specification

```
project-root/
├── mcp_servers/
│   └── tradingview_server/
│       ├── server.py              # MCP server entry point
│       ├── tv_wrapper.py          # TradingView data fetcher
│       ├── models.py              # Pydantic models
│       └── tools.py               # Tool definitions
```

### Data Sources for TV Wrapper

```python
class TradingViewWrapper:
    """
    Fetches market data. Implementation can use:
    - TradingView unofficial API (tvDatafeed library)
    - Yahoo Finance (yfinance library)
    - Alpha Vantage / Twelve Data API
    - Custom screener endpoints
    """

    def get_ohlcv(
        self, symbol: str, timeframe: str = "1h", count: int = 100
    ) -> list[dict]:
        """Return OHLCV candle data."""
        ...

    def get_news(self, symbol: str, limit: int = 10) -> list[dict]:
        """Return recent news articles related to symbol."""
        ...

    def get_indicator(
        self, symbol: str, timeframe: str, indicator: str, **params
    ) -> dict:
        """
        Calculate/return technical indicator values.
        Supported: RSI, MACD, EMA, SMA, Bollinger Bands, ATR, ADX, Stochastic
        """
        ...

    def get_available_indicators(self) -> list[str]:
        """Return list of indicators this system can provide (3 of 4)."""
        ...

    def get_market_summary(self, symbol: str) -> dict:
        """Return market overview, sector performance, correlations."""
        ...
```

---

## 7. Environment Configuration

```env
# .env

# LLM
OPENAI_API_KEY=sk-...
# Or for Anthropic
ANTHROPIC_API_KEY=sk-ant-...

# MT5
MT5_LOGIN=12345678
MT5_PASSWORD=your_password
MT5_SERVER=Broker-Demo
MT5_PATH=/path/to/MetaTrader 5/terminal64.exe

# TradingView Data
TV_DATA_SOURCE=yfinance  # yfinance | alphavantage | tvdatafeed
ALPHA_VANTAGE_KEY=...

# Scheduler
DEFAULT_ANALYSIS_INTERVAL=900  # seconds (15 min)
MARKET_OPEN_HOUR=0            # UTC (Forex: 0 = Sunday open)
MARKET_CLOSE_HOUR=22          # UTC (Forex: 22 = Friday close)

# Risk
MAX_RISK_PER_TRADE_PCT=1.0
DEFAULT_RISK_REWARD_RATIO=2.0
CONFIDENCE_THRESHOLD=0.75

# Logging
LOG_LEVEL=INFO
LOG_TO_FILE=true
LOG_FILE_PATH=./logs/trader_ai.log
```

---

## 8. Project Structure

```
trader-ai/
├── AGENTS.md                          # This file
├── ORCHESTRATOR_PROMPT.md             # System prompt for orchestrator
├── .env
├── pyproject.toml
├── main.py                            # Entry point: starts scheduler + graph
├── config.py                          # Load env, global settings
│
├── graph/
│   ├── __init__.py
│   ├── workflow.py                    # LangGraph StateGraph definition
│   ├── state.py                       # TraderState TypedDict
│   ├── nodes.py                       # All agent node functions
│   └── routers.py                     # Conditional edge routers
│
├── agents/
│   ├── __init__.py
│   ├── orchestrator.py                # Orchestrator agent + prompt
│   ├── data_collector.py
│   ├── technical_analyst.py
│   ├── news_analyst.py
│   ├── strategy_evaluator.py
│   ├── risk_manager.py
│   ├── trade_executor.py
│   └── scheduler.py
│
├── mcp_servers/
│   ├── tradingview_server/
│   │   ├── server.py
│   │   ├── tv_wrapper.py
│   │   ├── models.py
│   │   └── tools.py
│   └── mt5_server/
│       ├── server.py
│       ├── mt5_wrapper.py
│       ├── models.py
│       └── tools.py
│
├── prompts/
│   ├── orchestrator.md
│   ├── technical_analyst.md
│   ├── news_analyst.md
│   ├── strategy_evaluator.md
│   ├── risk_manager.md
│   └── trade_executor.md
│
├── utils/
│   ├── __init__.py
│   ├── logger.py
│   ├── notifications.py               # Telegram/email alerts
│   └── formatters.py                  # Format MT5 data for LLM consumption
│
└── tests/
    ├── test_mt5_wrapper.py
    ├── test_tv_wrapper.py
    ├── test_agents.py
    └── test_workflow.py
```

---

## 9. Key Design Principles

1. **Human-in-the-Loop (Optional):** Before any live execution, add `interrupt_before=["trade_executor"]` in LangGraph to require human approval.
2. **Paper Trading First:** Always run with `MT5_DEMO=true` before going live.
3. **Single Execution per Cycle:** The system executes at most ONE trade per analysis cycle to prevent overtrading.
4. **Missing Indicator Awareness:** The system is explicitly aware that only 3/4 timing indicators are available and factors this into confidence scoring.
5. **No Hallucinated Trades:** The Trade Executor agent MUST use exact values from `risk_assessment` — no independent decisions.
6. **Stateless Agents, Stateful Graph:** Individual agents are stateless; all context flows through `TraderState`.
7. **Deterministic Scheduler:** The scheduler does NOT use an LLM — it uses fixed rules based on state outcomes.