"""Trade execution layer."""

import logging
from decimal import Decimal

from auto_trader.config import config
from auto_trader.data.mt5_client import MT5Client
from auto_trader.domain.models import (
    TradingDecision,
    TradeExecution,
    TradeResult,
    Decision,
    TradeDirection,
    SymbolInfo,
    AccountInfo,
)

logger = logging.getLogger(__name__)


class TradeExecutor:
    """Executes trades via MetaTrader 5."""

    def __init__(self, mt5_client: MT5Client | None = None):
        """Initialize trade executor."""
        self.mt5 = mt5_client or MT5Client()

    def execute_decision(
        self, decision: TradingDecision, symbol_info: SymbolInfo, account: AccountInfo
    ) -> TradeResult:
        """Execute trading decision."""
        if decision.decision != Decision.EXECUTE:
            return TradeResult(
                success=False,
                message=f"Decision is {decision.decision}, not EXECUTE",
            )

        if not decision.direction:
            return TradeResult(success=False, message="No direction specified")

        if config.paper_trading_mode:
            logger.info("Paper trading mode - simulating execution")
            return self._simulate_execution(decision, symbol_info, account)

        try:
            # Calculate trade parameters
            execution = self._calculate_execution(decision, symbol_info, account)

            # Place order
            result = self.mt5.place_market_order(
                symbol=decision.pair,
                direction=decision.direction.value,
                volume=execution.lot_size,
                sl=execution.stop_loss,
                tp=execution.take_profit,
                comment=f"AutoTrader RR:{execution.rr_ratio:.2f}",
            )

            logger.info(f"Order placed: {result}")

            return TradeResult(
                success=True,
                ticket=result.get("ticket"),
                message="Trade executed successfully",
                execution=execution,
            )

        except Exception as e:
            logger.error(f"Trade execution failed: {e}")
            return TradeResult(success=False, message=f"Execution error: {e}")

    def _calculate_execution(
        self, decision: TradingDecision, symbol_info: SymbolInfo, account: AccountInfo
    ) -> TradeExecution:
        """Calculate trade execution parameters."""
        if not decision.direction:
            raise ValueError("Direction is required for execution calculation")
        
        # Get current price
        if decision.direction == TradeDirection.BUY:
            entry_price = symbol_info.ask
        else:
            entry_price = symbol_info.bid

        # Calculate SL/TP from pips
        pip_value = symbol_info.point * 10  # Standard pip
        sl_distance = Decimal(str(decision.sl_pips)) * pip_value
        tp_distance = Decimal(str(decision.tp_pips)) * pip_value

        if decision.direction == TradeDirection.BUY:
            stop_loss = entry_price - sl_distance
            take_profit = entry_price + tp_distance
        else:
            stop_loss = entry_price + sl_distance
            take_profit = entry_price - tp_distance

        # Calculate lot size based on risk
        risk_amount = account.balance * Decimal(
            str(config.max_risk_per_trade_pct / 100)
        )
        pip_value_per_lot = symbol_info.contract_size * pip_value

        lot_size = risk_amount / (Decimal(str(decision.sl_pips)) * pip_value_per_lot)

        # Round to lot step
        lot_size = self._round_to_lot_step(lot_size, symbol_info)

        # Ensure within limits
        lot_size = max(symbol_info.min_lot, min(lot_size, symbol_info.max_lot))

        # Calculate expected profit
        expected_profit = lot_size * Decimal(str(decision.tp_pips)) * pip_value_per_lot

        return TradeExecution(
            symbol=decision.pair,
            direction=decision.direction,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            lot_size=lot_size,
            risk_amount=risk_amount,
            expected_profit=expected_profit,
            rr_ratio=decision.rr_ratio or 0.0,
        )

    def _round_to_lot_step(self, lot_size: Decimal, symbol_info: SymbolInfo) -> Decimal:
        """Round lot size to symbol's lot step."""
        step = symbol_info.lot_step
        return (lot_size / step).quantize(Decimal("1")) * step

    def _simulate_execution(
        self, decision: TradingDecision, symbol_info: SymbolInfo, account: AccountInfo
    ) -> TradeResult:
        """Simulate trade execution for paper trading."""
        if not decision.direction:
            return TradeResult(success=False, message="No direction specified for paper trade")
        
        execution = self._calculate_execution(decision, symbol_info, account)

        logger.info(
            f"[PAPER TRADE] {decision.direction.value} {execution.lot_size} lots "
            f"{decision.pair} @ {execution.entry_price}, "
            f"SL: {execution.stop_loss}, TP: {execution.take_profit}, "
            f"RR: {execution.rr_ratio:.2f}"
        )

        return TradeResult(
            success=True,
            ticket=999999,  # Fake ticket for paper trading
            message="Paper trade simulated",
            execution=execution,
        )

    def close_all_positions(self, symbol: str | None = None) -> list[dict]:
        """Close all open positions."""
        positions = self.mt5.get_positions(symbol)
        results = []

        for pos in positions:
            try:
                result = self.mt5.close_position(pos.ticket)
                results.append(result)
                logger.info(f"Closed position {pos.ticket}")
            except Exception as e:
                logger.error(f"Failed to close position {pos.ticket}: {e}")

        return results
