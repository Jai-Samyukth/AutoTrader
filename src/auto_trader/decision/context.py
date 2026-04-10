"""Context building for LLM decision making."""

import logging
from typing import Any

from auto_trader.domain.models import (
    IndicatorData,
    OHLCVData,
    SMCData,
    NewsEvent,
    AccountInfo,
    Position,
    SymbolInfo,
)

logger = logging.getLogger(__name__)


class ContextBuilder:
    """Builds structured context for LLM decision making."""

    @staticmethod
    def build_market_context(
        symbol: str,
        multi_tf_data: dict[str, dict[str, Any]],
        smc_data: dict[str, SMCData],
    ) -> dict[str, Any]:
        """Build market analysis context."""
        context = {
            "symbol": symbol,
            "timeframes": {},
        }

        for tf, data in multi_tf_data.items():
            indicators: IndicatorData = data["indicators"]
            candles: list[OHLCVData] = data["ohlcv"]
            smc: SMCData = smc_data.get(tf, SMCData(symbol=symbol, timeframe=tf))

            # Get latest candle
            latest_candle = candles[-1] if candles else None

            context["timeframes"][tf] = {
                "indicators": {
                    "rsi": indicators.rsi,
                    "macd": indicators.macd,
                    "macd_signal": indicators.macd_signal,
                    "macd_histogram": indicators.macd_histogram,
                    "ema_20": indicators.ema_20,
                    "ema_50": indicators.ema_50,
                    "ema_200": indicators.ema_200,
                    "adx": indicators.adx,
                    "plus_di": indicators.plus_di,
                    "minus_di": indicators.minus_di,
                    "bb_upper": indicators.bb_upper,
                    "bb_middle": indicators.bb_middle,
                    "bb_lower": indicators.bb_lower,
                    "supertrend": indicators.supertrend,
                },
                "price": {
                    "open": float(latest_candle.open) if latest_candle else None,
                    "high": float(latest_candle.high) if latest_candle else None,
                    "low": float(latest_candle.low) if latest_candle else None,
                    "close": float(latest_candle.close) if latest_candle else None,
                    "volume": float(latest_candle.volume) if latest_candle else None,
                },
                "smc": {
                    "swing_highs": smc.swing_highs,
                    "swing_lows": smc.swing_lows,
                    "bos_detected": smc.bos_detected,
                    "choch_detected": smc.choch_detected,
                    "order_blocks": smc.order_blocks,
                    "fair_value_gaps": smc.fair_value_gaps,
                    "liquidity_zones": smc.liquidity_zones,
                },
            }

        return context

    @staticmethod
    def build_news_context(news_events: list[NewsEvent]) -> dict[str, Any]:
        """Build news context."""
        return {
            "events": [
                {
                    "title": event.title,
                    "description": event.description,
                    "currency": event.currency,
                    "impact": event.impact,
                    "timestamp": event.timestamp.isoformat(),
                }
                for event in news_events
            ],
            "has_high_impact": any(e.impact.lower() == "high" for e in news_events),
        }

    @staticmethod
    def build_account_context(
        account: AccountInfo,
        positions: list[Position],
        symbol_info: SymbolInfo,
    ) -> dict[str, Any]:
        """Build account and risk context."""
        return {
            "account": {
                "balance": float(account.balance),
                "equity": float(account.equity),
                "margin": float(account.margin),
                "free_margin": float(account.free_margin),
                "leverage": account.leverage,
                "profit": float(account.profit),
            },
            "positions": [
                {
                    "ticket": pos.ticket,
                    "symbol": pos.symbol,
                    "type": pos.type,
                    "volume": float(pos.volume),
                    "open_price": float(pos.open_price),
                    "current_price": float(pos.current_price),
                    "profit": float(pos.profit),
                }
                for pos in positions
            ],
            "symbol_info": {
                "symbol": symbol_info.symbol,
                "digits": symbol_info.digits,
                "point": float(symbol_info.point),
                "min_lot": float(symbol_info.min_lot),
                "max_lot": float(symbol_info.max_lot),
                "lot_step": float(symbol_info.lot_step),
                "contract_size": float(symbol_info.contract_size),
                "spread": symbol_info.spread,
                "bid": float(symbol_info.bid),
                "ask": float(symbol_info.ask),
            },
        }

    @staticmethod
    def build_full_context(
        symbol: str,
        multi_tf_data: dict[str, dict[str, Any]],
        smc_data: dict[str, SMCData],
        news_events: list[NewsEvent],
        account: AccountInfo,
        positions: list[Position],
        symbol_info: SymbolInfo,
    ) -> dict[str, Any]:
        """Build complete context for decision making."""
        return {
            "market": ContextBuilder.build_market_context(
                symbol, multi_tf_data, smc_data
            ),
            "news": ContextBuilder.build_news_context(news_events),
            "account": ContextBuilder.build_account_context(
                account, positions, symbol_info
            ),
        }
