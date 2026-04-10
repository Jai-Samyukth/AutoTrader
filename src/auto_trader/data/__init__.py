"""Data layer for market data and MT5 integration."""

from auto_trader.data.mt5_client import (
    MT5Client,
    MT5_TOOLS,
    mt5_get_account_info,
    mt5_get_positions,
    mt5_get_symbol_info,
    mt5_place_market_order,
    mt5_close_position,
    mt5_modify_position,
)
from auto_trader.data.market_data import MarketDataProvider

__all__ = [
    "MT5Client",
    "MT5_TOOLS",
    "mt5_get_account_info",
    "mt5_get_positions",
    "mt5_get_symbol_info",
    "mt5_place_market_order",
    "mt5_close_position",
    "mt5_modify_position",
    "MarketDataProvider",
]
