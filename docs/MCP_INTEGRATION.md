# MCP Integration Guide

## Overview

AutoTrader integrates with MetaTrader 5 using the Model Context Protocol (MCP) through LangChain tools. This provides a standardized way for the LLM to interact with MT5.

## Architecture

```
LangChain LLM
    ↓
LangChain Tools (@tool decorators)
    ↓
HTTP Requests
    ↓
MetaTrader MCP Server (http://localhost:8001)
    ↓
MetaTrader 5 Terminal
```

## MCP Tools

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

## MetaTrader MCP Server Setup

### Installation

```bash
# Clone the MCP server
git clone https://github.com/ariadng/metatrader-mcp-server.git
cd metatrader-mcp-server

# Install dependencies
npm install

# Configure
cp .env.example .env
# Edit .env with your MT5 credentials
```

### Configuration (.env)

```env
# MetaTrader 5 Configuration
MT5_LOGIN=your_account_number
MT5_PASSWORD=your_password
MT5_SERVER=your_broker_server
MT5_PATH=C:\Program Files\MetaTrader 5\terminal64.exe

# Server Configuration
PORT=8001
HOST=localhost
```

### Start Server

```bash
# Development mode
npm run dev

# Production mode
npm start
```

### Verify Server

```bash
# Test account endpoint
curl http://localhost:8001/api/v1/account

# Test symbol endpoint
curl http://localhost:8001/api/v1/symbol/EURUSD
```

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

### MCP Server Not Running

```bash
# Check if server is running
curl http://localhost:8001/api/v1/account

# If not, start it
cd metatrader-mcp-server
npm start
```

### MT5 Connection Failed

1. Check MT5 terminal is running
2. Verify credentials in MCP server .env
3. Check MT5 allows API connections
4. Verify firewall settings

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

- [TradingView-TA Documentation](https://python-tradingview-ta.readthedocs.io/)
- [MetaTrader MCP Server](https://github.com/ariadng/metatrader-mcp-server)
- [LangChain Tools](https://python.langchain.com/docs/modules/agents/tools/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
