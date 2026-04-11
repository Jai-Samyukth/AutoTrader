"""LangGraph workflow for trading decisions."""

import json
import logging
import re
from typing import Any

from langgraph.graph import StateGraph, END, START
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel, Field

from auto_trader.config import config
from auto_trader.decision.llm import create_structured_llm, get_llm
from auto_trader.domain.models import (
    Decision,
    TradingDecision,
)

logger = logging.getLogger(__name__)


def parse_llm_response(text: str) -> dict:
    """Parse LLM response that may contain JSON wrapped in markdown or malformed.
    
    Args:
        text: Raw LLM response text
        
    Returns:
        Parsed JSON dictionary
        
    Raises:
        ValueError: If JSON cannot be extracted
    """
    if not text or not text.strip():
        raise ValueError("Empty response from LLM")
    
    text = text.strip()
    
    # Try direct JSON parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    # Try extracting JSON from markdown code block
    match = re.search(r'```(?:json)?\s*\n?(.*?)\n?\s*```', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass
    
    # Try finding JSON object boundaries
    start, end = text.find('{'), text.rfind('}')
    if start != -1 and end > start:
        try:
            return json.loads(text[start:end+1])
        except json.JSONDecodeError:
            pass
    
    raise ValueError(f"Cannot parse JSON from response: {text[:200]}")


class WorkflowState(BaseModel):
    """State for the trading workflow."""

    context: dict[str, Any] = Field(default_factory=dict)
    decision: TradingDecision | None = None
    error: str | None = None


class TradingWorkflow:
    """LangGraph workflow for trading decisions."""

    def __init__(self):
        """Initialize trading workflow."""
        # Keep structured LLM for primary path
        self.structured_llm = create_structured_llm(TradingDecision)
        # Regular LLM for fallback
        self.regular_llm = get_llm()
        self.graph = self._build_graph()

    def _build_graph(self) -> Any:
        """Build the LangGraph workflow."""
        workflow = StateGraph(WorkflowState)

        # Add nodes
        workflow.add_node("analyze", self._analyze_node)
        workflow.add_node("decide", self._decide_node)
        workflow.add_node("validate", self._validate_node)

        # Add edges
        workflow.add_edge(START, "analyze")
        workflow.add_edge("analyze", "decide")
        workflow.add_edge("decide", "validate")
        workflow.add_edge("validate", END)

        return workflow.compile()

    def _analyze_node(self, state: WorkflowState) -> dict[str, Any]:
        """Analyze market context."""
        logger.info("Analyzing market context...")

        context = state.context

        # Extract key information for analysis
        symbol = context["market"]["symbol"]
        timeframes = context["market"]["timeframes"]

        # Log analysis summary
        for tf, data in timeframes.items():
            indicators = data["indicators"]
            logger.info(
                f"{symbol} {tf}: RSI={indicators.get('rsi')}, "
                f"MACD={indicators.get('macd')}, ADX={indicators.get('adx')}"
            )

        return {"context": context, "decision": state.decision, "error": state.error}

    def _decide_node(self, state: WorkflowState) -> dict[str, Any]:
        """Make trading decision using LLM with structured output and fallback."""
        logger.info("🧠 Making trading decision...")

        context = state.context

        # Build prompt for LLM
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(context)

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]

        decision = None
        
        # Try structured output first (primary path)
        try:
            logger.debug("Attempting structured output...")
            decision = self.structured_llm.invoke(messages)
            logger.info(f"✅ Decision (structured): {decision.decision} - {decision.confidence_reason[:100]}")
            return {"context": context, "decision": decision, "error": None}
        except Exception as e:
            logger.warning(f"⚠️  Structured output failed: {e}, trying manual parse...")
        
        # Fallback: Manual JSON parsing
        try:
            logger.debug("Attempting manual JSON parse...")
            response = self.regular_llm.invoke(messages)
            # Handle response.content which can be str or list
            content = response.content if isinstance(response.content, str) else str(response.content)
            parsed = parse_llm_response(content)
            decision = TradingDecision(**parsed)
            logger.info(f"✅ Decision (manual parse): {decision.decision} - {decision.confidence_reason[:100]}")
            return {"context": context, "decision": decision, "error": None}
        except Exception as parse_error:
            logger.error(f"❌ Manual parse failed: {parse_error}, using hardcoded SKIP...")
        
        # Ultimate fallback: Hardcoded SKIP decision
        try:
            error_decision = TradingDecision(
                decision=Decision.SKIP,
                pair=context["market"]["symbol"],
                direction="NONE",
                phase1_score=0.0,
                phase2_score=0.0,
                total_score=0.0,
                sl_pips=None,
                tp_pips=None,
                rr_ratio=None,
                confidence_reason=f"LLM parse failed: {str(parse_error)[:200]}",
                next_check_minutes=15,
                next_check_reason="LLM error - retry later",
            )
            logger.warning("⚠️  Using fallback SKIP decision due to LLM errors")
            return {"context": context, "decision": error_decision, "error": str(parse_error)}
        except Exception as final_error:
            logger.error(f"💥 Critical error in decision node: {final_error}")
            return {"context": context, "decision": None, "error": str(final_error)}

    def _validate_node(self, state: WorkflowState) -> dict[str, Any]:
        """Validate decision against risk rules."""
        logger.info("Validating decision...")

        decision = state.decision
        if not decision:
            return {
                "context": state.context,
                "decision": decision,
                "error": state.error,
            }

        # Validate against config thresholds
        if decision.decision == Decision.EXECUTE:
            if decision.total_score < config.confidence_threshold * 100:
                logger.warning(
                    f"Score {decision.total_score} below threshold "
                    f"{config.confidence_threshold * 100}, changing to WATCH"
                )
                decision.decision = Decision.WATCH

            if decision.rr_ratio and decision.rr_ratio < config.min_rr_ratio:
                logger.warning(
                    f"RR ratio {decision.rr_ratio} below minimum "
                    f"{config.min_rr_ratio}, changing to SKIP"
                )
                decision.decision = Decision.SKIP

        return {"context": state.context, "decision": decision, "error": state.error}

    def _build_system_prompt(self) -> str:
        """Build system prompt for LLM."""
        return """You are an expert quantitative trading analyst specializing in Smart Money Concepts (SMC) and multi-timeframe technical analysis.

Your task is to analyze market data and make trading decisions based on:
1. Multi-timeframe trend alignment (Weekly > 4H > 1H > 15m)
2. Smart Money Concepts (BOS, CHoCH, Order Blocks, FVG, Liquidity)
3. Technical indicators (RSI, MACD, EMA, ADX, Bollinger Bands)
4. News sentiment and impact
5. Risk management rules

Scoring Rules:
Phase 1 (Bias + Structure) - 0-100 points:
- Higher timeframe alignment (Weekly/4H bullish or bearish): 30 pts
- BOS/CHoCH direction matches higher TF: 20 pts
- Trend strength (ADX > 25, EMA alignment): 20 pts
- Key levels identified (support/resistance): 15 pts
- News alignment with technical: 15 pts

Phase 2 (Entry Quality) - 0-100 points:
- Order Block present and active (not mitigated): 30 pts
- Fair Value Gap present and unfilled: 25 pts
- Liquidity sweep detected: 20 pts
- RSI/MACD confirmation: 15 pts
- Entry at optimal level: 10 pts

Total Score: (Phase1 + Phase2) / 2

Decision Rules:
- EXECUTE: total_score >= 75, RR >= 1.5, no high-impact news
- WATCH: 60 <= total_score < 75, monitor for improvement
- SKIP: total_score < 60 or conflicting signals

IMPORTANT: You MUST respond with ONLY a valid JSON object. No markdown formatting, no ## headers, no explanations outside the JSON. Start with { and end with }."""

    def _build_user_prompt(self, context: dict[str, Any]) -> str:
        """Build user prompt with context."""
        return f"""Analyze the following market data and make a trading decision:

{json.dumps(context, indent=2, default=str)}

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
- next_check_reason: why this timing"""

    def run(self, context: dict[str, Any]) -> TradingDecision:
        """Run the workflow."""
        initial_state = WorkflowState(
            context=context,
            decision=None,
            error=None,
        )

        final_state = self.graph.invoke(initial_state)

        if final_state.get("error"):
            logger.error(f"Workflow error: {final_state['error']}")

        return final_state.get("decision")
