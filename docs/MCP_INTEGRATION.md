# MCP Integration Guide

## Overview

AutoTrader integrates with MetaTrader 5 using the **direct Python MetaTrader5 package** wrapped as LangChain tools. This provides a standardized way for the LLM to interact with MT5 without requiring a separate MCP server.

## Architecture

```
LangChain LLM
    ↓
LangChain Tools (@tool decorators)
    ↓
MetaTrader5 Python Package
    ↓
MetaTrader 5 Terminal (running locally)
```

## Prerequisites

1. **MetaTrader 5 Terminal** installed and running
2. **MT5 Account** logged in
3. **Python MetaTrader5 package** installed (included in requirements.txt)
4. **MT5 credentials** in `.env` file

## MCP Tools

All tools connect directly to MT5 via the Python MetaTrader5 package. No separate server needed.

### 1. Account Information

```python
from auto_trader.data import mt5_get_account_info

# Get account info
account = mt5_get_account_info.invoke({})
# Returns: {balance, equity, margin, free_margin, leverage, profit}
```

### 2. Get Positions

```python
from auto_trader.data import mt5_get_positions

# Get all positions
positions = mt5_get_positions.invoke({"symbol": ""})

# Get positions for specific symbol
positions = mt5_get_positions.invoke({"symbol": "EURUSD"})
# Returns: {positions: [{ticket, symbol, type, volume, ...}]}
```

### 3. Symbol Information

```python
from auto_trader.data import mt5_get_symbol_info

# Get symbol specs
info = mt5_get_symbol_info.invoke({"symbol": "EURUSD"})
# Returns: {symbol, digits, point, volume_min, volume_max, spread, bid, ask}
```

### 4. Place Market Order

```python
from auto_trader.data import mt5_place_market_order

# Place buy order
result = mt5_place_market_order.invoke({
    "symbol": "EURUSD",
    "action": "buy",
    "volume": 0.01,
    "sl": 1.0820,
    "tp": 1.0920,
    "comment": "AutoTrader"
})
# Returns: {ticket, status}
```

### 5. Close Position

```python
from auto_trader.data import mt5_close_position

# Close position by ticket
result = mt5_close_position.invoke({"ticket": 123456})
# Returns: {status}
```

### 6. Modify Position

```python
from auto_trader.data import mt5_modify_position

# Modify SL/TP
result = mt5_modify_position.invoke({
    "ticket": 123456,
    "sl": 1.0830,
    "tp": 1.0930
})
# Returns: {status}
```

## LangChain Integration

### Using Tools in Agents

```python
from langchain.agents import create_tool_calling_agent
from auto_trader.data import MT5_TOOLS
from auto_trader.decision.llm import get_llm

# Create agent with MT5 tools
llm = get_llm()
agent = create_tool_calling_agent(
    llm=llm,
    tools=MT5_TOOLS,
    prompt=prompt_template
)

# Agent can now call MT5 tools
result = agent.invoke({"input": "Get my account balance"})
```

### Using Tools in LangGraph

```python
from langgraph.prebuilt import create_react_agent
from auto_trader.data import MT5_TOOLS
from auto_trader.decision.llm import get_llm

# Create ReAct agent with tools
llm = get_llm()
agent = create_react_agent(llm, MT5_TOOLS)

# Agent can reason and use tools
result = agent.invoke({
    "messages": [("user", "Place a buy order for EURUSD")]
})
```

## Setup

### 1. Install MetaTrader 5

Download and install MT5 from your broker or from [MetaQuotes](https://www.metatrader5.com/).

### 2. Configure Credentials

Add your MT5 credentials to `.env`:

```env
# MetaTrader 5 Configuration
MT5_LOGIN=your_account_number
MT5_PASSWORD=your_password
MT5_SERVER=your_broker_server

# Examples:
# MT5_LOGIN=12345678
# MT5_PASSWORD=YourPassword123
# MT5_SERVER=MetaQuotes-Demo
# MT5_SERVER=ICMarkets-Demo
# MT5_SERVER=JustMarkets-Demo2
```

### 3. Test Connection

```bash
# Test direct MT5 connection
bash scripts/test_mt5_connection.sh

# Or run Python test directly
python scripts/test_mt5_direct.py
```

### 4. Verify MT5 is Running

Make sure:
- MT5 terminal is open and running
- You're logged into your account
- AutoTrading is enabled (Tools → Options → Expert Advisors → Allow automated trading)

## TradingView-ta Integration

### Usage

```python
from tradingview_ta import TA_Handler, Interval

# Create handler
handler = TA_Handler(
    symbol="EUR/USD",
    screener="forex",
    exchange="FX_IDC",
    interval=Interval.INTERVAL_1_HOUR
)

# Get analysis
analysis = handler.get_analysis()

# Access indicators
rsi = analysis.indicators["RSI"]
macd = analysis.indicators["MACD.macd"]
ema20 = analysis.indicators["EMA20"]
adx = analysis.indicators["ADX"]
```

### Supported Intervals

- `Interval.INTERVAL_1_MINUTE`
- `Interval.INTERVAL_5_MINUTES`
- `Interval.INTERVAL_15_MINUTES`
- `Interval.INTERVAL_1_HOUR`
- `Interval.INTERVAL_4_HOURS`
- `Interval.INTERVAL_1_DAY`
- `Interval.INTERVAL_1_WEEK`
- `Interval.INTERVAL_1_MONTH`

### Available Indicators

- RSI
- MACD (macd, signal, histogram)
- EMA (20, 50, 200)
- SMA (20, 50, 200)
- ADX (+DI, -DI)
- Bollinger Bands (upper, middle, lower)
- Stochastic
- CCI
- ATR
- Supertrend

## LangGraph Workflow

### Current Implementation

```python
from langgraph.graph import StateGraph, START, END

# Define workflow
workflow = StateGraph(WorkflowState)

# Add nodes
workflow.add_node("analyze", analyze_node)
workflow.add_node("decide", decide_node)
workflow.add_node("validate", validate_node)

# Add edges
workflow.add_edge(START, "analyze")
workflow.add_edge("analyze", "decide")
workflow.add_edge("decide", "validate")
workflow.add_edge("validate", END)

# Compile
graph = workflow.compile()

# Run
result = graph.invoke(initial_state)
```

### Structured Output

```python
from langchain_core.pydantic_v1 import BaseModel
from auto_trader.decision.llm import create_structured_llm

# Define output schema
class TradingDecision(BaseModel):
    decision: str
    direction: str | None
    phase1_score: float
    phase2_score: float
    total_score: float
    # ... other fields

# Create LLM with structured output
llm = create_structured_llm(TradingDecision)

# LLM returns typed object
decision = llm.invoke(messages)
# decision is TradingDecision instance
```

## Best Practices

### 1. Error Handling

```python
try:
    result = mt5_get_account_info.invoke({})
except Exception as e:
    logger.error(f"MT5 API error: {e}")
    # Handle gracefully
```

### 2. Tool Validation

```python
# Validate inputs before calling tools
if volume < symbol_info.min_lot:
    raise ValueError(f"Volume {volume} below minimum {symbol_info.min_lot}")
```

### 3. Logging

```python
logger.info(f"Calling MT5 tool: {tool_name}")
result = tool.invoke(params)
logger.info(f"MT5 tool result: {result}")
```

### 4. Retry Logic

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def call_mt5_tool(tool, params):
    return tool.invoke(params)
```

## Troubleshooting

### MT5 Connection Failed

1. **Check MT5 is running**: Open MetaTrader 5 terminal
2. **Verify login**: Make sure you're logged into your account
3. **Check credentials**: Verify `.env` has correct MT5_LOGIN, MT5_PASSWORD, MT5_SERVER
4. **Enable AutoTrading**: Tools → Options → Expert Advisors → Allow automated trading
5. **Check Python package**: `pip install MetaTrader5`

### "MT5 initialization failed"

- Make sure MT5 terminal is running
- Try restarting MT5 terminal
- Check if MT5 is installed in default location

### "Failed to get account info"

- Verify you're logged into MT5
- Check account credentials in `.env`
- Make sure account is active and funded

### Tool Invocation Errors

```python
# Check tool parameters
print(tool.args_schema.schema())

# Validate before calling
params = {"symbol": "EURUSD"}
result = tool.invoke(params)
```

### TradingView Rate Limiting

```python
import time

# Add delay between requests
time.sleep(1)
analysis = handler.get_analysis()
```

## References

- [MetaTrader5 Python Package](https://pypi.org/project/MetaTrader5/)
- [MT5 Python Documentation](https://www.mql5.com/en/docs/python_metatrader5)
- [TradingView-TA Documentation](https://python-tradingview-ta.readthedocs.io/)
- [LangChain Tools](https://python.langchain.com/docs/modules/agents/tools/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
