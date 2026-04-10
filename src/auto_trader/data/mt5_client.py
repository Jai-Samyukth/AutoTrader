"""MetaTrader 5 MCP client using LangChain tools."""

import logging
from decimal import Decimal
from typing import Any

from langchain_core.tools import tool

from auto_trader.config import config
from auto_trader.domain.models import AccountInfo, Position, SymbolInfo

logger = logging.getLogger(__name__)


# MCP Tools for MetaTrader 5
# These tools will be called by LangChain agents


@tool
def mt5_get_account_info() -> dict[str, Any]:
    """Get MT5 account information including balance, equity, margin, and leverage.
    
    Returns:
        dict: Account information with balance, equity, margin, free_margin, leverage, profit
    """
    # This will be handled by the MCP server
    # The actual implementation connects to MT5 via MCP
    import requests
    
    try:
        response = requests.get(
            f"{config.mt5_base_url}/account",
            timeout=config.mt5_timeout
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Failed to get account info: {e}")
        raise


@tool
def mt5_get_positions(symbol: str = "") -> dict[str, Any]:
    """Get open positions from MT5.
    
    Args:
        symbol: Optional symbol to filter positions (e.g., "EURUSD")
    
    Returns:
        dict: List of open positions with ticket, symbol, type, volume, prices, profit
    """
    import requests
    
    try:
        params = {"symbol": symbol} if symbol else {}
        response = requests.get(
            f"{config.mt5_base_url}/positions",
            params=params,
            timeout=config.mt5_timeout
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Failed to get positions: {e}")
        raise


@tool
def mt5_get_symbol_info(symbol: str) -> dict[str, Any]:
    """Get symbol specification from MT5.
    
    Args:
        symbol: Trading symbol (e.g., "EURUSD", "GBPUSD")
    
    Returns:
        dict: Symbol info with digits, point, min/max lot, spread, bid, ask
    """
    import requests
    
    try:
        response = requests.get(
            f"{config.mt5_base_url}/symbol/{symbol}",
            timeout=config.mt5_timeout
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Failed to get symbol info for {symbol}: {e}")
        raise


@tool
def mt5_place_market_order(
    symbol: str,
    action: str,
    volume: float,
    sl: float = 0.0,
    tp: float = 0.0,
    comment: str = ""
) -> dict[str, Any]:
    """Place a market order in MT5.
    
    Args:
        symbol: Trading symbol (e.g., "EURUSD")
        action: "buy" or "sell"
        volume: Lot size (e.g., 0.01, 0.1, 1.0)
        sl: Stop loss price (optional)
        tp: Take profit price (optional)
        comment: Order comment (optional)
    
    Returns:
        dict: Order result with ticket number and status
    """
    import requests
    
    try:
        payload = {
            "symbol": symbol,
            "action": action.lower(),
            "volume": volume,
            "comment": comment
        }
        
        if sl > 0:
            payload["sl"] = sl
        if tp > 0:
            payload["tp"] = tp
        
        logger.info(f"Placing {action} order: {symbol} {volume} lots")
        response = requests.post(
            f"{config.mt5_base_url}/order/market",
            json=payload,
            timeout=config.mt5_timeout
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Failed to place order: {e}")
        raise


@tool
def mt5_close_position(ticket: int) -> dict[str, Any]:
    """Close an open position in MT5.
    
    Args:
        ticket: Position ticket number
    
    Returns:
        dict: Close result with status
    """
    import requests
    
    try:
        logger.info(f"Closing position: {ticket}")
        response = requests.post(
            f"{config.mt5_base_url}/position/{ticket}/close",
            timeout=config.mt5_timeout
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Failed to close position {ticket}: {e}")
        raise


@tool
def mt5_modify_position(
    ticket: int,
    sl: float = 0.0,
    tp: float = 0.0
) -> dict[str, Any]:
    """Modify stop loss and take profit of an open position.
    
    Args:
        ticket: Position ticket number
        sl: New stop loss price (optional)
        tp: New take profit price (optional)
    
    Returns:
        dict: Modification result with status
    """
    import requests
    
    try:
        payload = {}
        if sl > 0:
            payload["sl"] = sl
        if tp > 0:
            payload["tp"] = tp
        
        logger.info(f"Modifying position {ticket}: SL={sl}, TP={tp}")
        response = requests.post(
            f"{config.mt5_base_url}/position/{ticket}/modify",
            json=payload,
            timeout=config.mt5_timeout
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Failed to modify position {ticket}: {e}")
        raise


# Helper class for backward compatibility
class MT5Client:
    """MT5 client wrapper using MCP tools."""
    
    def __init__(self, base_url: str | None = None, timeout: int | None = None):
        """Initialize MT5 client."""
        # Configuration is handled by the tools
        pass
    
    def get_account_info(self) -> AccountInfo:
        """Get account information."""
        data = mt5_get_account_info.invoke(input={})  # type: ignore
        return AccountInfo(
            balance=Decimal(str(data["balance"])),
            equity=Decimal(str(data["equity"])),
            margin=Decimal(str(data["margin"])),
            free_margin=Decimal(str(data["free_margin"])),
            leverage=data["leverage"],
            profit=Decimal(str(data["profit"])),
        )
    
    def get_positions(self, symbol: str | None = None) -> list[Position]:
        """Get open positions."""
        data = mt5_get_positions.invoke(input={"symbol": symbol or ""})  # type: ignore
        
        positions = []
        for pos in data.get("positions", []):
            positions.append(
                Position(
                    ticket=pos["ticket"],
                    symbol=pos["symbol"],
                    type=pos["type"],
                    volume=Decimal(str(pos["volume"])),
                    open_price=Decimal(str(pos["price_open"])),
                    current_price=Decimal(str(pos["price_current"])),
                    sl=Decimal(str(pos["sl"])) if pos.get("sl") else None,
                    tp=Decimal(str(pos["tp"])) if pos.get("tp") else None,
                    profit=Decimal(str(pos["profit"])),
                    swap=Decimal(str(pos["swap"])),
                    commission=Decimal(str(pos["commission"])),
                )
            )
        return positions
    
    def get_symbol_info(self, symbol: str) -> SymbolInfo:
        """Get symbol specification."""
        data = mt5_get_symbol_info.invoke(input={"symbol": symbol})  # type: ignore
        return SymbolInfo(
            symbol=data["symbol"],
            digits=data["digits"],
            point=Decimal(str(data["point"])),
            min_lot=Decimal(str(data["volume_min"])),
            max_lot=Decimal(str(data["volume_max"])),
            lot_step=Decimal(str(data["volume_step"])),
            contract_size=Decimal(str(data["trade_contract_size"])),
            spread=data["spread"],
            bid=Decimal(str(data["bid"])),
            ask=Decimal(str(data["ask"])),
        )
    
    def get_current_price(self, symbol: str) -> tuple[Decimal, Decimal]:
        """Get current bid/ask price."""
        info = self.get_symbol_info(symbol)
        return info.bid, info.ask
    
    def place_market_order(
        self,
        symbol: str,
        direction: str,
        volume: Decimal,
        sl: Decimal | None = None,
        tp: Decimal | None = None,
        comment: str = "",
    ) -> dict[str, Any]:
        """Place market order."""
        return mt5_place_market_order.invoke(input={  # type: ignore
            "symbol": symbol,
            "action": "buy" if direction.upper() == "BUY" else "sell",
            "volume": float(volume),
            "sl": float(sl) if sl else 0.0,
            "tp": float(tp) if tp else 0.0,
            "comment": comment
        })
    
    def close_position(self, ticket: int) -> dict[str, Any]:
        """Close position by ticket."""
        return mt5_close_position.invoke(input={"ticket": ticket})  # type: ignore
    
    def modify_position(
        self,
        ticket: int,
        sl: Decimal | None = None,
        tp: Decimal | None = None,
    ) -> dict[str, Any]:
        """Modify position SL/TP."""
        return mt5_modify_position.invoke(input={  # type: ignore
            "ticket": ticket,
            "sl": float(sl) if sl else 0.0,
            "tp": float(tp) if tp else 0.0
        })


# Export MCP tools for use in LangChain agents
MT5_TOOLS = [
    mt5_get_account_info,
    mt5_get_positions,
    mt5_get_symbol_info,
    mt5_place_market_order,
    mt5_close_position,
    mt5_modify_position,
]
