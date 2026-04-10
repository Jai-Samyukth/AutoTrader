"""MetaTrader 5 HTTP client."""

import logging
from decimal import Decimal
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from auto_trader.config import config
from auto_trader.domain.models import AccountInfo, Position, SymbolInfo

logger = logging.getLogger(__name__)


class MT5Client:
    """HTTP client for MetaTrader 5 MCP server."""

    def __init__(self, base_url: str | None = None, timeout: int | None = None):
        """Initialize MT5 client."""
        self.base_url = base_url or config.mt5_base_url
        self.timeout = timeout or config.mt5_timeout

        # Configure session with retries
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _request(self, method: str, endpoint: str, **kwargs: Any) -> dict[str, Any]:
        """Make HTTP request with error handling."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            response = self.session.request(method, url, timeout=self.timeout, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"MT5 API request failed: {e}")
            raise

    def get_account_info(self) -> AccountInfo:
        """Get account information."""
        data = self._request("GET", "/account")
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
        params = {"symbol": symbol} if symbol else {}
        data = self._request("GET", "/positions", params=params)

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
        data = self._request("GET", f"/symbol/{symbol}")
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
        payload = {
            "symbol": symbol,
            "action": "buy" if direction.upper() == "BUY" else "sell",
            "volume": float(volume),
            "comment": comment,
        }

        if sl is not None:
            payload["sl"] = float(sl)
        if tp is not None:
            payload["tp"] = float(tp)

        logger.info(f"Placing {direction} order: {symbol} {volume} lots")
        return self._request("POST", "/order/market", json=payload)

    def close_position(self, ticket: int) -> dict[str, Any]:
        """Close position by ticket."""
        logger.info(f"Closing position: {ticket}")
        return self._request("POST", f"/position/{ticket}/close")

    def modify_position(
        self,
        ticket: int,
        sl: Decimal | None = None,
        tp: Decimal | None = None,
    ) -> dict[str, Any]:
        """Modify position SL/TP."""
        payload = {}
        if sl is not None:
            payload["sl"] = float(sl)
        if tp is not None:
            payload["tp"] = float(tp)

        logger.info(f"Modifying position {ticket}: SL={sl}, TP={tp}")
        return self._request("POST", f"/position/{ticket}/modify", json=payload)
