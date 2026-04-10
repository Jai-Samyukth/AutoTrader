"""LangGraph workflow for trading decisions."""

import logging
from typing import Any, TypedDict

from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage, HumanMessage

from auto_trader.config import config
from auto_trader.decision.llm import get_llm
from auto_trader.domain.models import (
    Decision,
    TradingDecision,
    TradeDirection,
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
        self.llm = get_llm()
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        workflow = StateGraph(WorkflowState)

        # Add nodes
        workflow.add_node("analyze", self._analyze_node)
        workflow.add_node("decide", self._decide_node)
        workflow.add_node("validate", self._validate_node)

        # Add edges
        workflow.set_entry_point("analyze")
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
        """Make trading decision using LLM."""
        logger.info("Making trading decision...")

        context = state["context"]

        # Build prompt for LLM
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(context)

        try:
            # Call LLM
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt),
            ]

            response = self.llm.invoke(messages)
            decision_text = response.content

            # Parse decision (simplified - in production use structured output)
            decision = self._parse_decision(decision_text, context)

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
            if decision.total_score < config.confidence_threshold:
                logger.warning(
                    f"Score {decision.total_score} below threshold "
                    f"{config.confidence_threshold}, changing to WATCH"
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

You MUST output a JSON decision with:
- decision: "EXECUTE", "WATCH", or "SKIP"
- direction: "BUY" or "SELL" (if EXECUTE)
- phase1_score: Higher timeframe bias score (0-100)
- phase2_score: Entry quality score (0-100)
- total_score: Combined score (0-100)
- sl_pips: Stop loss in pips
- tp_pips: Take profit in pips
- rr_ratio: Risk/reward ratio
- confidence_reason: Detailed explanation
- next_check_minutes: When to re-evaluate
- next_check_reason: Why this timing

Scoring Rules:
Phase 1 (Bias + Structure): Higher TF alignment, BOS/CHoCH direction, trend strength
Phase 2 (Entry Quality): OB/FVG presence, liquidity sweep, indicator confirmation

DO NOT EXECUTE if:
- RR < 1.5
- total_score < 75
- High-impact news within 60 minutes
- Conflicting signals across timeframes"""

    def _build_user_prompt(self, context: dict[str, Any]) -> str:
        """Build user prompt with context."""
        import json

        return f"""Analyze the following market data and make a trading decision:

{json.dumps(context, indent=2, default=str)}

Provide your decision in JSON format."""

    def _parse_decision(
        self, decision_text: str, context: dict[str, Any]
    ) -> TradingDecision:
        """Parse LLM decision output."""
        import json
        import re

        # Extract JSON from response
        json_match = re.search(r"\{.*\}", decision_text, re.DOTALL)
        if not json_match:
            raise ValueError("No JSON found in LLM response")

        decision_data = json.loads(json_match.group())

        return TradingDecision(
            decision=Decision(decision_data.get("decision", "SKIP")),
            pair=context["market"]["symbol"],
            direction=(
                TradeDirection(decision_data["direction"])
                if decision_data.get("direction")
                else None
            ),
            phase1_score=float(decision_data.get("phase1_score", 0)),
            phase2_score=float(decision_data.get("phase2_score", 0)),
            total_score=float(decision_data.get("total_score", 0)),
            sl_pips=float(decision_data["sl_pips"])
            if decision_data.get("sl_pips")
            else None,
            tp_pips=float(decision_data["tp_pips"])
            if decision_data.get("tp_pips")
            else None,
            rr_ratio=float(decision_data["rr_ratio"])
            if decision_data.get("rr_ratio")
            else None,
            confidence_reason=decision_data.get("confidence_reason", ""),
            next_check_minutes=int(decision_data.get("next_check_minutes", 15)),
            next_check_reason=decision_data.get("next_check_reason", ""),
        )

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
