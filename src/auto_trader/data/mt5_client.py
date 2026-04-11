"""MetaTrader 5 client using direct MT5 Python package."""

import logging
from decimal import Decimal
from typing import Any

import MetaTrader5 as mt5
from langchain_core.tools import tool

from auto_trader.config import config
from auto_trader.domain.models import AccountInfo, Position, SymbolInfo

logger = logging.getLogger(__name__)


# Initialize MT5 connection
def _ensure_mt5_initialized() -> bool:
    """Ensure MT5 is initialized and connected."""
    if not mt5.initialize():
        logger.error("MT5 initialization failed")
        return False
    
    # Login if credentials are provided
    if config.mt5_login and config.mt5_password and config.mt5_server:
        if not mt5.login(
            login=int(config.mt5_login),
            password=config.mt5_password,
            server=config.mt5_server
        ):
            logger.error(f"MT5 login failed: {mt5.last_error()}")
            return False
    
    return True


# MCP Tools for MetaTrader 5
# These tools will be called by LangChain agents


@tool
def mt5_get_account_info() -> dict[str, Any]:
    """Get MT5 account information including balance, equity, margin, and leverage.
    
    Returns:
        dict: Account information with balance, equity, margin, free_margin, leverage, profit
    """
    if not _ensure_mt5_initialized():
        raise RuntimeError("MT5 not initialized")
    
    try:
        account = mt5.account_info()
        if account is None:
            raise RuntimeError(f"Failed to get account info: {mt5.last_error()}")
        
        return {
            "balance": account.balance,
            "equity": account.equity,
            "margin": account.margin,
            "free_margin": account.margin_free,
            "leverage": account.leverage,
            "profit": account.profit,
        }
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
    if not _ensure_mt5_initialized():
        raise RuntimeError("MT5 not initialized")
    
    try:
        # Get positions - pass symbol with .m suffix if needed
        if symbol:
            # Try with symbol as-is first
            positions = mt5.positions_get(symbol=symbol)
            # If not found and doesn't have .m, try with .m
            if positions is None or len(positions) == 0:
                if not symbol.endswith('.m'):
                    positions = mt5.positions_get(symbol=f"{symbol}.m")
        else:
            positions = mt5.positions_get()
        
        if positions is None:
            # Empty tuple is OK, None means error
            error = mt5.last_error()
            if error[0] != 1:  # 1 = RET_OK
                raise RuntimeError(f"Failed to get positions: {error}")
        
        result = []
        for pos in positions:
            result.append({
                "ticket": pos.ticket,
                "symbol": pos.symbol,
                "type": "buy" if pos.type == mt5.ORDER_TYPE_BUY else "sell",
                "volume": pos.volume,
                "price_open": pos.price_open,
                "price_current": pos.price_current,
                "sl": pos.sl,
                "tp": pos.tp,
                "profit": pos.profit,
                "swap": pos.swap,
                "commission": pos.commission,
            })
        
        return {"positions": result}
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
    if not _ensure_mt5_initialized():
        raise RuntimeError("MT5 not initialized")
    
    try:
        info = mt5.symbol_info(symbol)
        if info is None:
            raise RuntimeError(f"Failed to get symbol info for {symbol}: {mt5.last_error()}")
        
        # Get current tick for bid/ask
        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            raise RuntimeError(f"Failed to get tick for {symbol}: {mt5.last_error()}")
        
        return {
            "symbol": info.name,
            "digits": info.digits,
            "point": info.point,
            "volume_min": info.volume_min,
            "volume_max": info.volume_max,
            "volume_step": info.volume_step,
            "trade_contract_size": info.trade_contract_size,
            "spread": info.spread,
            "bid": tick.bid,
            "ask": tick.ask,
        }
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
    if not _ensure_mt5_initialized():
        raise RuntimeError("MT5 not initialized")
    
    try:
        # Get current price
        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            raise RuntimeError(f"Failed to get tick for {symbol}: {mt5.last_error()}")
        
        # Determine order type and price
        order_type = mt5.ORDER_TYPE_BUY if action.lower() == "buy" else mt5.ORDER_TYPE_SELL
        price = tick.ask if action.lower() == "buy" else tick.bid
        
        # Prepare request
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": order_type,
            "price": price,
            "deviation": 20,
            "magic": 234000,
            "comment": comment or "AutoTrader",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        if sl > 0:
            request["sl"] = sl
        if tp > 0:
            request["tp"] = tp
        
        logger.info(f"Placing {action} order: {symbol} {volume} lots")
        result = mt5.order_send(request)
        
        if result is None:
            raise RuntimeError(f"Order send failed: {mt5.last_error()}")
        
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            raise RuntimeError(f"Order failed: {result.comment} (code: {result.retcode})")
        
        return {
            "ticket": result.order,
            "status": "success",
            "retcode": result.retcode,
            "comment": result.comment,
        }
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
    if not _ensure_mt5_initialized():
        raise RuntimeError("MT5 not initialized")
    
    try:
        # Get position info
        position = mt5.positions_get(ticket=ticket)
        if not position:
            raise RuntimeError(f"Position {ticket} not found")
        
        pos = position[0]
        
        # Determine close order type (opposite of position type)
        order_type = mt5.ORDER_TYPE_SELL if pos.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
        
        # Get current price
        tick = mt5.symbol_info_tick(pos.symbol)
        if tick is None:
            raise RuntimeError(f"Failed to get tick for {pos.symbol}: {mt5.last_error()}")
        
        price = tick.bid if order_type == mt5.ORDER_TYPE_SELL else tick.ask
        
        # Prepare close request
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": pos.symbol,
            "volume": pos.volume,
            "type": order_type,
            "position": ticket,
            "price": price,
            "deviation": 20,
            "magic": 234000,
            "comment": "AutoTrader close",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        logger.info(f"Closing position: {ticket}")
        result = mt5.order_send(request)
        
        if result is None:
            raise RuntimeError(f"Close order failed: {mt5.last_error()}")
        
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            raise RuntimeError(f"Close failed: {result.comment} (code: {result.retcode})")
        
        return {
            "status": "success",
            "retcode": result.retcode,
            "comment": result.comment,
        }
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
    if not _ensure_mt5_initialized():
        raise RuntimeError("MT5 not initialized")
    
    try:
        # Get position info
        position = mt5.positions_get(ticket=ticket)
        if not position:
            raise RuntimeError(f"Position {ticket} not found")
        
        pos = position[0]
        
        # Prepare modify request
        request = {
            "action": mt5.TRADE_ACTION_SLTP,
            "symbol": pos.symbol,
            "position": ticket,
            "sl": sl if sl > 0 else pos.sl,
            "tp": tp if tp > 0 else pos.tp,
        }
        
        logger.info(f"Modifying position {ticket}: SL={sl}, TP={tp}")
        result = mt5.order_send(request)
        
        if result is None:
            raise RuntimeError(f"Modify order failed: {mt5.last_error()}")
        
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            raise RuntimeError(f"Modify failed: {result.comment} (code: {result.retcode})")
        
        return {
            "status": "success",
            "retcode": result.retcode,
            "comment": result.comment,
        }
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
