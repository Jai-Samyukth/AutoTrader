"""Test domain models."""

from decimal import Decimal
from datetime import datetime

from auto_trader.domain.models import (
    TimeFrame,
    TradeDirection,
    Decision,
    OHLCVData,
    IndicatorData,
    TradingDecision,
)


def test_timeframe_enum():
    """Test TimeFrame enum."""
    assert TimeFrame.M15.value == "15m"
    assert TimeFrame.H1.value == "1h"
    assert TimeFrame.H4.value == "4h"
    assert TimeFrame.W1.value == "1w"


def test_trade_direction_enum():
    """Test TradeDirection enum."""
    assert TradeDirection.BUY.value == "BUY"
    assert TradeDirection.SELL.value == "SELL"


def test_decision_enum():
    """Test Decision enum."""
    assert Decision.EXECUTE.value == "EXECUTE"
    assert Decision.WATCH.value == "WATCH"
    assert Decision.SKIP.value == "SKIP"


def test_ohlcv_data():
    """Test OHLCVData model."""
    candle = OHLCVData(
        timestamp=datetime.now(),
        open=Decimal("1.0850"),
        high=Decimal("1.0900"),
        low=Decimal("1.0800"),
        close=Decimal("1.0875"),
        volume=Decimal("1000"),
    )

    assert candle.open == Decimal("1.0850")
    assert candle.high == Decimal("1.0900")
    assert candle.low == Decimal("1.0800")
    assert candle.close == Decimal("1.0875")


def test_indicator_data():
    """Test IndicatorData model."""
    indicators = IndicatorData(
        symbol="EURUSD",
        timeframe="1h",
        rsi=55.0,
        macd=0.0015,
        ema_20=1.0850,
        ema_50=1.0820,
        adx=28.5,
    )

    assert indicators.symbol == "EURUSD"
    assert indicators.timeframe == "1h"
    assert indicators.rsi == 55.0
    assert indicators.adx == 28.5


def test_trading_decision():
    """Test TradingDecision model."""
    decision = TradingDecision(
        decision=Decision.EXECUTE,
        pair="EURUSD",
        direction=TradeDirection.BUY,
        phase1_score=75.0,
        phase2_score=80.0,
        total_score=77.5,
        sl_pips=30.0,
        tp_pips=60.0,
        rr_ratio=2.0,
        confidence_reason="Strong bullish setup",
        next_check_minutes=15,
        next_check_reason="Monitor for continuation",
    )

    assert decision.decision == Decision.EXECUTE
    assert decision.direction == TradeDirection.BUY
    assert decision.total_score == 77.5
    assert decision.rr_ratio == 2.0
