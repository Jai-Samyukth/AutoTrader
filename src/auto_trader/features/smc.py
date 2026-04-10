"""Smart Money Concepts (SMC) feature extraction."""

from typing import Any

import logging

from auto_trader.domain.models import OHLCVData, SMCData, TimeFrame

logger = logging.getLogger(__name__)


class SMCAnalyzer:
    """Analyzes Smart Money Concepts from price data."""

    def __init__(self, swing_period: int = 5):
        """Initialize SMC analyzer."""
        self.swing_period = swing_period

    def analyze(
        self, symbol: str, timeframe: TimeFrame, candles: list[OHLCVData]
    ) -> SMCData:
        """Perform SMC analysis on candle data."""
        if len(candles) < self.swing_period * 2:
            logger.warning(
                f"Insufficient data for SMC analysis: {len(candles)} candles"
            )
            return SMCData(symbol=symbol, timeframe=timeframe.value)

        swing_highs = self._find_swing_highs(candles)
        swing_lows = self._find_swing_lows(candles)
        bos_detected = self._detect_bos(candles, swing_highs, swing_lows)
        choch_detected = self._detect_choch(candles, swing_highs, swing_lows)
        order_blocks = self._find_order_blocks(candles)
        fvgs = self._find_fair_value_gaps(candles)
        liquidity = self._find_liquidity_zones(candles, swing_highs, swing_lows)

        return SMCData(
            symbol=symbol,
            timeframe=timeframe.value,
            swing_highs=swing_highs,
            swing_lows=swing_lows,
            bos_detected=bos_detected,
            choch_detected=choch_detected,
            order_blocks=order_blocks,
            fair_value_gaps=fvgs,
            liquidity_zones=liquidity,
        )

    def _find_swing_highs(self, candles: list[OHLCVData]) -> list[float]:
        """Identify swing high points."""
        swing_highs = []
        period = self.swing_period

        for i in range(period, len(candles) - period):
            current_high = float(candles[i].high)
            is_swing_high = True

            # Check if current high is higher than surrounding candles
            for j in range(i - period, i + period + 1):
                if j != i and float(candles[j].high) >= current_high:
                    is_swing_high = False
                    break

            if is_swing_high:
                swing_highs.append(current_high)

        return swing_highs[-10:]  # Return last 10 swing highs

    def _find_swing_lows(self, candles: list[OHLCVData]) -> list[float]:
        """Identify swing low points."""
        swing_lows = []
        period = self.swing_period

        for i in range(period, len(candles) - period):
            current_low = float(candles[i].low)
            is_swing_low = True

            # Check if current low is lower than surrounding candles
            for j in range(i - period, i + period + 1):
                if j != i and float(candles[j].low) <= current_low:
                    is_swing_low = False
                    break

            if is_swing_low:
                swing_lows.append(current_low)

        return swing_lows[-10:]  # Return last 10 swing lows

    def _detect_bos(
        self,
        candles: list[OHLCVData],
        swing_highs: list[float],
        swing_lows: list[float],
    ) -> bool:
        """Detect Break of Structure (BOS)."""
        if len(candles) < 3 or not swing_highs or not swing_lows:
            return False

        recent_close = float(candles[-1].close)
        prev_close = float(candles[-2].close)

        # Bullish BOS: price breaks above recent swing high
        if swing_highs and recent_close > swing_highs[-1] > prev_close:
            return True

        # Bearish BOS: price breaks below recent swing low
        if swing_lows and recent_close < swing_lows[-1] < prev_close:
            return True

        return False

    def _detect_choch(
        self,
        candles: list[OHLCVData],
        swing_highs: list[float],
        swing_lows: list[float],
    ) -> bool:
        """Detect Change of Character (CHoCH)."""
        if len(candles) < 5 or len(swing_highs) < 2 or len(swing_lows) < 2:
            return False

        # CHoCH occurs when price breaks counter-trend structure
        # Simplified: detect when recent swing pattern reverses
        recent_high_trend = swing_highs[-1] > swing_highs[-2]
        recent_low_trend = swing_lows[-1] > swing_lows[-2]

        # Bullish CHoCH: lows making higher lows while highs were making lower highs
        if recent_low_trend and not recent_high_trend:
            return True

        # Bearish CHoCH: highs making lower highs while lows were making higher lows
        if not recent_low_trend and recent_high_trend:
            return True

        return False

    def _find_order_blocks(self, candles: list[OHLCVData]) -> list[dict[str, Any]]:
        """Identify order blocks (OB)."""
        order_blocks = []

        for i in range(1, len(candles) - 1):
            current_candle = candles[i]
            next_candle = candles[i + 1]

            # Bullish OB: down candle followed by strong up move
            if (
                float(current_candle.close) < float(current_candle.open)
                and float(next_candle.close) > float(next_candle.open)
                and float(next_candle.close) > float(current_candle.high)
            ):
                order_blocks.append(
                    {
                        "type": "bullish",
                        "high": float(current_candle.high),
                        "low": float(current_candle.low),
                        "mitigated": False,
                    }
                )

            # Bearish OB: up candle followed by strong down move
            if (
                float(current_candle.close) > float(current_candle.open)
                and float(next_candle.close) < float(next_candle.open)
                and float(next_candle.close) < float(current_candle.low)
            ):
                order_blocks.append(
                    {
                        "type": "bearish",
                        "high": float(current_candle.high),
                        "low": float(current_candle.low),
                        "mitigated": False,
                    }
                )

        return order_blocks[-5:]  # Return last 5 order blocks

    def _find_fair_value_gaps(self, candles: list[OHLCVData]) -> list[dict[str, Any]]:
        """Identify Fair Value Gaps (FVG).

        FVG occurs when there's a gap between candle 1 and candle 3,
        with candle 2 in between (the gap candle).
        """
        fvgs = []

        for i in range(2, len(candles)):
            candle1 = candles[i - 2]
            candle3 = candles[i]

            # Bullish FVG: gap between candle1 high and candle3 low
            # Price moved up so fast that candle2 left a gap
            if float(candle3.low) > float(candle1.high):
                fvgs.append(
                    {
                        "type": "bullish",
                        "top": float(candle3.low),
                        "bottom": float(candle1.high),
                        "filled": False,
                    }
                )

            # Bearish FVG: gap between candle1 low and candle3 high
            # Price moved down so fast that candle2 left a gap
            if float(candle3.high) < float(candle1.low):
                fvgs.append(
                    {
                        "type": "bearish",
                        "top": float(candle1.low),
                        "bottom": float(candle3.high),
                        "filled": False,
                    }
                )

        return fvgs[-5:]  # Return last 5 FVGs

    def _find_liquidity_zones(
        self,
        candles: list[OHLCVData],
        swing_highs: list[float],
        swing_lows: list[float],
    ) -> list[dict[str, Any]]:
        """Identify liquidity zones (areas where stops likely cluster)."""
        liquidity = []

        # Liquidity typically sits above swing highs and below swing lows
        for high in swing_highs[-3:]:
            liquidity.append({"type": "sell_side", "level": high})

        for low in swing_lows[-3:]:
            liquidity.append({"type": "buy_side", "level": low})

        return liquidity
