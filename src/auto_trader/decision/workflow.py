"""LangGraph workflow for trading decisions."""

import json
import logging
from typing import Any

from langgraph.graph import StateGraph, END, START
from langchain_core.messages import SystemMessage, HumanMessage
from typing_extensions import TypedDict

from auto_trader.config import config
from auto_trader.decision.llm import create_structured_llm
from auto_trader.domain.models import (
    Decision,
    TradingDecision,
)

logger = logging.getLogger(__name__)


class WorkflowState(TypedDict):
    """State for the trading workflow."""

    context: dict[str, Any]
    decision: TradingDecision | None
    error: str | None


class TradingWorkflow:
    """LangGraph workflow for trading decisions."""

    def __init__(self):
        """Initialize trading workflow."""
        # Use structured output for reliable JSON parsing
        self.llm = create_structured_llm(TradingDecision)
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

    def _analyze_node(self, state: WorkflowState) -> WorkflowState:
        """Analyze market context."""
        logger.info("Analyzing market context...")

        context = state["context"]

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

        return state

    def _decide_node(self, state: WorkflowState) -> WorkflowState:
        """Make trading decision using LLM with structured output."""
        logger.info("Making trading decision...")

        context = state["context"]

        # Build prompt for LLM
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(context)

        try:
            # Call LLM with structured output
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt),
            ]

            # LLM returns structured TradingDecision object
            decision = self.llm.invoke(messages)

            state["decision"] = decision
            logger.info(f"Decision: {decision.decision} - {decision.confidence_reason}")

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

    def _validate_node(self, state: WorkflowState) -> WorkflowState:
        """Validate decision against risk rules."""
        logger.info("Validating decision...")

        decision = state["decision"]
        if not decision:
            return state

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

        return state

    def _build_system_prompt(self) -> str:
        """Build system prompt for LLM."""
        return """You are an expert quantitative trading analyst specializing in Smart Money Concepts (SMC) and multi-timeframe technical analysis.

Your task is to analyze market data and make trading decisions based on:
1. Multi-timeframe trend alignment (Weekly → 4H → 1H → 15m)
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

Output the decision with all required fields."""

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
        initial_state: WorkflowState = {
            "context": context,
            "decision": None,
            "error": None,
        }

        final_state = self.graph.invoke(initial_state)

        if final_state["error"]:
            logger.error(f"Workflow error: {final_state['error']}")

        return final_state["decision"]
