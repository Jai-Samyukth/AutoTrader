# LangChain & LangGraph Integration

## Overview

AutoTrader uses LangChain and LangGraph for LLM-powered decision making with proper tool integration and structured workflows.

## LangChain Components

### 1. LLM Initialization

```python
# src/auto_trader/decision/llm.py

from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI

def get_llm():
    """Get configured LLM instance."""
    if config.is_anthropic:
        return ChatAnthropic(
            model=config.llm_model,
            temperature=config.llm_temperature,
            api_key=config.anthropic_api_key,
        )
    elif config.is_openai:
        return ChatOpenAI(
            model=config.llm_model,
            temperature=config.llm_temperature,
            api_key=config.openai_api_key,
        )
```

### 2. Structured Output

```python
from langchain_core.pydantic_v1 import BaseModel

def create_structured_llm(output_schema: type):
    """Create LLM with structured output."""
    llm = get_llm()
    return llm.with_structured_output(output_schema)

# Usage
llm = create_structured_llm(TradingDecision)
decision = llm.invoke(messages)
# Returns TradingDecision object, not raw text
```

### 3. MCP Tools

```python
from langchain_core.tools import tool

@tool
def mt5_get_account_info() -> dict:
    """Get MT5 account information."""
    # Implementation
    pass

@tool
def mt5_place_market_order(
    symbol: str,
    action: str,
    volume: float,
    sl: float = 0.0,
    tp: float = 0.0
) -> dict:
    """Place a market order in MT5."""
    # Implementation
    pass

# Export for use in agents
MT5_TOOLS = [
    mt5_get_account_info,
    mt5_get_positions,
    mt5_get_symbol_info,
    mt5_place_market_order,
    mt5_close_position,
    mt5_modify_position,
]
```

## LangGraph Workflow

### State Definition

```python
from typing_extensions import TypedDict

class WorkflowState(TypedDict):
    """State for the trading workflow."""
    context: dict[str, Any]
    decision: TradingDecision | None
    error: str | None
```

### Graph Construction

```python
from langgraph.graph import StateGraph, START, END

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
```

### Node Implementation

```python
def analyze_node(state: WorkflowState) -> WorkflowState:
    """Analyze market context."""
    context = state["context"]
    
    # Log analysis
    for tf, data in context["market"]["timeframes"].items():
        indicators = data["indicators"]
        logger.info(f"RSI={indicators.get('rsi')}, ADX={indicators.get('adx')}")
    
    return state

def decide_node(state: WorkflowState) -> WorkflowState:
    """Make trading decision using LLM."""
    context = state["context"]
    
    # Build prompts
    system_prompt = build_system_prompt()
    user_prompt = build_user_prompt(context)
    
    # Call LLM with structured output
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt),
    ]
    
    decision = llm.invoke(messages)  # Returns TradingDecision object
    state["decision"] = decision
    
    return state

def validate_node(state: WorkflowState) -> WorkflowState:
    """Validate decision against risk rules."""
    decision = state["decision"]
    
    if decision.total_score < config.confidence_threshold * 100:
        decision.decision = Decision.WATCH
    
    return state
```

### Execution

```python
# Initialize workflow
workflow = TradingWorkflow()

# Run with context
decision = workflow.run(context)

# decision is TradingDecision object
print(f"Decision: {decision.decision}")
print(f"Score: {decision.total_score}")
print(f"Reason: {decision.confidence_reason}")
```

## Structured Output Schema

```python
from pydantic import BaseModel, Field

class TradingDecision(BaseModel):
    """LLM trading decision output."""
    
    decision: Decision  # EXECUTE, WATCH, SKIP
    pair: str
    direction: TradeDirection | None = None
    phase1_score: float = Field(ge=0, le=100)
    phase2_score: float = Field(ge=0, le=100)
    total_score: float = Field(ge=0, le=100)
    sl_pips: float | None = None
    tp_pips: float | None = None
    rr_ratio: float | None = None
    confidence_reason: str
    next_check_minutes: int
    next_check_reason: str
```

## Prompt Engineering

### System Prompt

```python
system_prompt = """You are an expert quantitative trading analyst.

Analyze market data and make trading decisions based on:
1. Multi-timeframe trend alignment (Weekly → 4H → 1H → 15m)
2. Smart Money Concepts (BOS, CHoCH, Order Blocks, FVG, Liquidity)
3. Technical indicators (RSI, MACD, EMA, ADX, Bollinger Bands)
4. News sentiment and impact
5. Risk management rules

Scoring Rules:
Phase 1 (Bias + Structure) - 0-100 points:
- Higher timeframe alignment: 30 pts
- BOS/CHoCH direction: 20 pts
- Trend strength: 20 pts
- Key levels: 15 pts
- News alignment: 15 pts

Phase 2 (Entry Quality) - 0-100 points:
- Order Block present: 30 pts
- Fair Value Gap: 25 pts
- Liquidity sweep: 20 pts
- RSI/MACD confirmation: 15 pts
- Entry level: 10 pts

Decision Rules:
- EXECUTE: total_score >= 75, RR >= 1.5
- WATCH: 60 <= total_score < 75
- SKIP: total_score < 60
"""
```

### User Prompt

```python
user_prompt = f"""Analyze the following market data:

{json.dumps(context, indent=2)}

Provide your decision with:
- decision: EXECUTE, WATCH, or SKIP
- direction: BUY or SELL (if EXECUTE)
- phase1_score: 0-100 (market context)
- phase2_score: 0-100 (entry quality)
- total_score: average of phase1 and phase2
- sl_pips: stop loss in pips
- tp_pips: take profit in pips
- rr_ratio: risk/reward ratio
- confidence_reason: detailed explanation
- next_check_minutes: when to re-evaluate
- next_check_reason: why this timing
"""
```

## Tool Usage in Agents

### Creating Tool-Calling Agent

```python
from langchain.agents import create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate

# Define prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a trading assistant with access to MT5."),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

# Create agent
agent = create_tool_calling_agent(
    llm=get_llm(),
    tools=MT5_TOOLS,
    prompt=prompt
)

# Use agent
result = agent.invoke({
    "input": "Get my account balance and open positions"
})
```

### Creating ReAct Agent

```python
from langgraph.prebuilt import create_react_agent

# Create ReAct agent with tools
agent = create_react_agent(
    model=get_llm(),
    tools=MT5_TOOLS
)

# Agent can reason and use tools
result = agent.invoke({
    "messages": [("user", "Place a 0.01 lot buy order for EURUSD")]
})
```

## Context Building

```python
class ContextBuilder:
    """Builds structured context for LLM."""
    
    @staticmethod
    def build_market_context(symbol, multi_tf_data, smc_data):
        """Build market analysis context."""
        context = {
            "symbol": symbol,
            "timeframes": {}
        }
        
        for tf, data in multi_tf_data.items():
            context["timeframes"][tf] = {
                "indicators": {
                    "rsi": data["indicators"].rsi,
                    "macd": data["indicators"].macd,
                    "ema_20": data["indicators"].ema_20,
                    "adx": data["indicators"].adx,
                },
                "smc": {
                    "bos_detected": smc_data[tf].bos_detected,
                    "order_blocks": smc_data[tf].order_blocks,
                    "fair_value_gaps": smc_data[tf].fair_value_gaps,
                }
            }
        
        return context
```

## Error Handling

```python
def decide_node(state: WorkflowState) -> WorkflowState:
    """Make trading decision with error handling."""
    try:
        decision = llm.invoke(messages)
        state["decision"] = decision
    except Exception as e:
        logger.error(f"Decision making failed: {e}")
        state["error"] = str(e)
        state["decision"] = TradingDecision(
            decision=Decision.SKIP,
            pair=context["market"]["symbol"],
            phase1_score=0.0,
            phase2_score=0.0,
            total_score=0.0,
            confidence_reason=f"Error: {e}",
            next_check_minutes=15,
            next_check_reason="Retry after error",
        )
    
    return state
```

## Validation

```python
def validate_node(state: WorkflowState) -> WorkflowState:
    """Validate decision against risk rules."""
    decision = state["decision"]
    
    if decision.decision == Decision.EXECUTE:
        # Check score threshold
        if decision.total_score < config.confidence_threshold * 100:
            logger.warning(f"Score {decision.total_score} below threshold")
            decision.decision = Decision.WATCH
        
        # Check RR ratio
        if decision.rr_ratio and decision.rr_ratio < config.min_rr_ratio:
            logger.warning(f"RR {decision.rr_ratio} below minimum")
            decision.decision = Decision.SKIP
    
    return state
```

## Benefits of This Approach

### 1. Type Safety
- Structured output ensures type-safe responses
- Pydantic validation catches errors early
- No manual JSON parsing needed

### 2. Tool Integration
- MCP tools are first-class LangChain tools
- Can be used in any LangChain agent
- Automatic parameter validation

### 3. Workflow Clarity
- LangGraph makes workflow explicit
- Easy to visualize and debug
- State transitions are clear

### 4. Maintainability
- Prompts are separate from code
- Easy to update scoring rules
- Tools are reusable

### 5. Testability
- Each node can be tested independently
- Mock tools for testing
- Deterministic state transitions

## References

- [LangChain Documentation](https://python.langchain.com/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Structured Output Guide](https://python.langchain.com/docs/modules/model_io/output_parsers/structured)
- [Tool Calling Guide](https://python.langchain.com/docs/modules/agents/tools/)
- [MCP Integration](docs/MCP_INTEGRATION.md)
