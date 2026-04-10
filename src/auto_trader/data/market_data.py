"""Market data fetching layer."""

from typing import Any

import logging
from decimal import Decimal

import yfinance as yf
from tradingview_ta import TA_Handler, Interval

from auto_trader.domain.models import IndicatorData, OHLCVData, TimeFrame

logger = logging.getLogger(__name__)


class MarketDataProvider:
    """Fetches market data from multiple sources."""

    TIMEFRAME_MAP = {
        TimeFrame.M15: Interval.INTERVAL_15_MINUTES,
        TimeFrame.H1: Interval.INTERVAL_1_HOUR,
        TimeFrame.H4: Interval.INTERVAL_4_HOURS,
        TimeFrame.W1: Interval.INTERVAL_1_WEEK,
    }

    def __init__(self):
        """Initialize market data provider."""
        self.cache: dict[str, Any] = {}

    def get_indicators(self, symbol: str, timeframe: TimeFrame) -> IndicatorData:
        """Fetch technical indicators using tradingview-ta."""
        try:
            # Convert symbol format (EURUSD -> EUR/USD for TradingView)
            tv_symbol = f"{symbol[:3]}/{symbol[3:]}" if len(symbol) == 6 else symbol

            handler = TA_Handler(
                symbol=tv_symbol,
                screener="forex",
                exchange="FX_IDC",
                interval=self.TIMEFRAME_MAP.get(timeframe, Interval.INTERVAL_1_HOUR),
            )

            analysis = handler.get_analysis()
            indicators = analysis.indicators

            return IndicatorData(
                symbol=symbol,
                timeframe=timeframe.value,
                rsi=indicators.get("RSI"),
                macd=indicators.get("MACD.macd"),
                macd_signal=indicators.get("MACD.signal"),
                macd_histogram=indicators.get("MACD.histogram"),
                ema_20=indicators.get("EMA20"),
                ema_50=indicators.get("EMA50"),
                ema_200=indicators.get("EMA200"),
                adx=indicators.get("ADX"),
                plus_di=indicators.get("ADX+DI"),
                minus_di=indicators.get("ADX-DI"),
                bb_upper=indicators.get("BB.upper"),
                bb_middle=indicators.get("BB.middle"),
                bb_lower=indicators.get("BB.lower"),
                supertrend=indicators.get("Supertrend"),
            )

        except Exception as e:
            logger.error(f"Failed to fetch indicators for {symbol} {timeframe}: {e}")
            # Return empty indicator data
            return IndicatorData(symbol=symbol, timeframe=timeframe.value)

    def get_ohlcv(
        self, symbol: str, timeframe: TimeFrame, periods: int = 100
    ) -> list[OHLCVData]:
        """Fetch OHLCV data using yfinance."""
        try:
            # Convert symbol format (EURUSD -> EURUSD=X for yfinance)
            yf_symbol = f"{symbol}=X" if len(symbol) == 6 else symbol

            # Determine interval and period
            interval_map = {
                TimeFrame.M15: "15m",
                TimeFrame.H1: "1h",
                TimeFrame.H4: "4h",
                TimeFrame.W1: "1wk",
            }
            interval = interval_map.get(timeframe, "1h")

            # Calculate period
            period_map = {
                TimeFrame.M15: "5d",
                TimeFrame.H1: "1mo",
                TimeFrame.H4: "3mo",
                TimeFrame.W1: "2y",
            }
            period = period_map.get(timeframe, "1mo")

            ticker = yf.Ticker(yf_symbol)
            df = ticker.history(period=period, interval=interval)

            if df.empty:
                logger.warning(f"No OHLCV data for {symbol} {timeframe}")
                return []

            # Convert to OHLCVData models
            candles = []
            for idx, row in df.iterrows():
                candles.append(
                    OHLCVData(
                        timestamp=idx.to_pydatetime(),
                        open=Decimal(str(row["Open"])),
                        high=Decimal(str(row["High"])),
                        low=Decimal(str(row["Low"])),
                        close=Decimal(str(row["Close"])),
                        volume=Decimal(str(row["Volume"])),
                    )
                )

            return candles[-periods:]  # Return last N periods

        except Exception as e:
            logger.error(f"Failed to fetch OHLCV for {symbol} {timeframe}: {e}")
            return []

    def get_multi_timeframe_data(
        self, symbol: str, timeframes: list[TimeFrame]
    ) -> dict[str, dict[str, Any]]:
        """Fetch data across multiple timeframes."""
        result = {}

        for tf in timeframes:
            result[tf.value] = {
                "indicators": self.get_indicators(symbol, tf),
                "ohlcv": self.get_ohlcv(symbol, tf),
            }

        return result
