"""Main trading bot orchestration."""

import logging

from auto_trader.config import config
from auto_trader.data.mt5_client import MT5Client
from auto_trader.data.market_data import MarketDataProvider
from auto_trader.features.smc import SMCAnalyzer
from auto_trader.features.news import NewsProvider
from auto_trader.decision.context import ContextBuilder
from auto_trader.decision.workflow import TradingWorkflow
from auto_trader.execution.trade_executor import TradeExecutor
from auto_trader.domain.models import TimeFrame, Decision

logger = logging.getLogger(__name__)


class TradingBot:
    """Autonomous trading bot orchestrator."""

    def __init__(self):
        """Initialize trading bot."""
        self.mt5 = MT5Client()
        self.market_data = MarketDataProvider()
        self.smc_analyzer = SMCAnalyzer()
        self.news_provider = NewsProvider()
        self.workflow = TradingWorkflow()
        self.executor = TradeExecutor(self.mt5)

        self.daily_trades = 0
        self.daily_loss = 0.0

        logger.info("Trading bot initialized")

    def run_analysis_cycle(self, symbol: str) -> None:
        """Run a complete analysis cycle for a symbol."""
        logger.info(f"Starting analysis cycle for {symbol}")

        try:
            # 1. Check risk limits
            if not self._check_risk_limits():
                logger.warning("Risk limits exceeded, skipping cycle")
                return

            # 2. Fetch data
            logger.info("Fetching market data...")
            timeframes = [TimeFrame(tf) for tf in config.timeframes]
            multi_tf_data = self.market_data.get_multi_timeframe_data(
                symbol, timeframes
            )

            # 3. Compute SMC features
            logger.info("Computing SMC features...")
            smc_data = {}
            for tf in timeframes:
                candles = multi_tf_data[tf.value]["ohlcv"]
                if candles:
                    smc_data[tf.value] = self.smc_analyzer.analyze(symbol, tf, candles)

            # 4. Fetch news
            logger.info("Fetching news...")
            currencies = self._extract_currencies(symbol)
            news_events = self.news_provider.get_upcoming_news(currencies)

            # Check for high-impact news
            if self.news_provider.has_high_impact_news(currencies):
                logger.warning("High-impact news detected, skipping trade")
                return

            # 5. Get account info
            logger.info("Fetching account info...")
            account = self.mt5.get_account_info()
            positions = self.mt5.get_positions(symbol)
            symbol_info = self.mt5.get_symbol_info(symbol)

            # 6. Build context
            logger.info("Building decision context...")
            context = ContextBuilder.build_full_context(
                symbol=symbol,
                multi_tf_data=multi_tf_data,
                smc_data=smc_data,
                news_events=news_events,
                account=account,
                positions=positions,
                symbol_info=symbol_info,
            )

            # 7. Make decision
            logger.info("Making trading decision...")
            decision = self.workflow.run(context)

            logger.info(
                f"Decision: {decision.decision} | "
                f"Score: {decision.total_score:.2f} | "
                f"Reason: {decision.confidence_reason}"
            )

            # 8. Execute if needed
            if decision.decision == Decision.EXECUTE:
                logger.info("Executing trade...")
                result = self.executor.execute_decision(decision, symbol_info, account)

                if result.success:
                    logger.info(f"Trade executed: {result.message}")
                    self.daily_trades += 1
                else:
                    logger.error(f"Trade execution failed: {result.message}")

            elif decision.decision == Decision.WATCH:
                logger.info(
                    f"Watching - will re-evaluate in {decision.next_check_minutes} minutes"
                )

            else:
                logger.info("Skipping trade opportunity")

        except Exception as e:
            logger.error(f"Analysis cycle failed: {e}", exc_info=True)

    def _check_risk_limits(self) -> bool:
        """Check if risk limits allow trading."""
        if self.daily_trades >= config.max_trades_per_day:
            logger.warning(f"Max daily trades reached: {self.daily_trades}")
            return False

        if self.daily_loss >= config.max_daily_loss_pct:
            logger.warning(f"Max daily loss reached: {self.daily_loss}%")
            return False

        return True

    def _extract_currencies(self, symbol: str) -> list[str]:
        """Extract currency codes from symbol."""
        if len(symbol) == 6:
            return [symbol[:3], symbol[3:]]
        return []

    def run_multi_symbol_cycle(self) -> None:
        """Run analysis for all configured symbols."""
        logger.info("Starting multi-symbol analysis cycle")

        for symbol in config.symbols:
            try:
                self.run_analysis_cycle(symbol)
            except Exception as e:
                logger.error(f"Failed to analyze {symbol}: {e}")

        logger.info("Multi-symbol cycle complete")

    def reset_daily_counters(self) -> None:
        """Reset daily trading counters."""
        logger.info("Resetting daily counters")
        self.daily_trades = 0
        self.daily_loss = 0.0
