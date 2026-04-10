"""Domain models for the trading system."""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


class TimeFrame(str, Enum):
    """Supported timeframes."""

    M15 = "15m"
    H1 = "1h"
    H4 = "4h"
    W1 = "1w"


class TradeDirection(str, Enum):
    """Trade direction."""

    BUY = "BUY"
    SELL = "SELL"


class Decision(str, Enum):
    """Trading decision."""

    EXECUTE = "EXECUTE"
    WATCH = "WATCH"
    SKIP = "SKIP"


class ConfidenceLevel(str, Enum):
    """Confidence level."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class OHLCVData(BaseModel):
    """OHLCV candle data."""

    timestamp: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal


class IndicatorData(BaseModel):
    """Technical indicator data."""

    symbol: str
    timeframe: str
    rsi: float | None = None
    macd: float | None = None
    macd_signal: float | None = None
    macd_histogram: float | None = None
    ema_20: float | None = None
    ema_50: float | None = None
    ema_200: float | None = None
    adx: float | None = None
    plus_di: float | None = None
    minus_di: float | None = None
    bb_upper: float | None = None
    bb_middle: float | None = None
    bb_lower: float | None = None
    supertrend: float | None = None
    timestamp: datetime = Field(default_factory=datetime.now)


class SMCData(BaseModel):
    """Smart Money Concepts data."""

    symbol: str
    timeframe: str
    swing_highs: list[float] = Field(default_factory=list)
    swing_lows: list[float] = Field(default_factory=list)
    bos_detected: bool = False
    choch_detected: bool = False
    order_blocks: list[dict[str, Any]] = Field(default_factory=list)
    fair_value_gaps: list[dict[str, Any]] = Field(default_factory=list)
    liquidity_zones: list[dict[str, Any]] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.now)


class NewsEvent(BaseModel):
    """News event data."""

    title: str
    description: str | None = None
    currency: str
    impact: str  # high, medium, low
    timestamp: datetime
    source: str | None = None


class AccountInfo(BaseModel):
    """MT5 account information."""

    balance: Decimal
    equity: Decimal
    margin: Decimal
    free_margin: Decimal
    leverage: int
    profit: Decimal


class Position(BaseModel):
    """Open position."""

    ticket: int
    symbol: str
    type: str  # buy or sell
    volume: Decimal
    open_price: Decimal
    current_price: Decimal
    sl: Decimal | None = None
    tp: Decimal | None = None
    profit: Decimal
    swap: Decimal
    commission: Decimal


class SymbolInfo(BaseModel):
    """Symbol specification."""

    symbol: str
    digits: int
    point: Decimal
    min_lot: Decimal
    max_lot: Decimal
    lot_step: Decimal
    contract_size: Decimal
    spread: int
    bid: Decimal
    ask: Decimal


class TradingDecision(BaseModel):
    """LLM trading decision output."""

    decision: Decision
    pair: str
    direction: TradeDirection | None = None
    phase1_score: float
    phase2_score: float
    total_score: float
    sl_pips: float | None = None
    tp_pips: float | None = None
    rr_ratio: float | None = None
    confidence_reason: str
    next_check_minutes: int
    next_check_reason: str


class TradeExecution(BaseModel):
    """Trade execution details."""

    symbol: str
    direction: TradeDirection
    entry_price: Decimal
    stop_loss: Decimal
    take_profit: Decimal
    lot_size: Decimal
    risk_amount: Decimal
    expected_profit: Decimal
    rr_ratio: float
    timestamp: datetime = Field(default_factory=datetime.now)


class TradeResult(BaseModel):
    """Trade execution result."""

    success: bool
    ticket: int | None = None
    message: str
    execution: TradeExecution | None = None
