"""Main entry point for the trading bot."""

import logging
import sys

from auto_trader.utils.logging import setup_logging
from auto_trader.orchestration.scheduler import TradingScheduler
from auto_trader.config import config

logger = logging.getLogger(__name__)


def main() -> None:
    """Main entry point."""
    # Setup logging
    setup_logging()

    logger.info("=" * 60)
    logger.info("AutoTrader - Autonomous Trading System")
    logger.info("=" * 60)
    logger.info(f"LLM Provider: {config.llm_provider}")
    logger.info(f"LLM Model: {config.llm_model}")
    logger.info(f"Symbols: {', '.join(config.symbols)}")
    logger.info(f"Timeframes: {', '.join(config.timeframes)}")
    logger.info(f"Paper Trading: {config.paper_trading_mode}")
    logger.info(f"Max Risk per Trade: {config.max_risk_per_trade_pct}%")
    logger.info(f"Confidence Threshold: {config.confidence_threshold}")
    logger.info("=" * 60)

    # Validate configuration
    if config.is_anthropic and not config.anthropic_api_key:
        logger.error("ANTHROPIC_API_KEY not set")
        sys.exit(1)

    if config.is_openai and not config.openai_api_key:
        logger.error("OPENAI_API_KEY not set")
        sys.exit(1)

    # Start scheduler
    scheduler = TradingScheduler()

    try:
        # Check if running in test mode
        if "--once" in sys.argv:
            logger.info("Running in test mode (single cycle)")
            scheduler.run_once()
        else:
            logger.info("Starting continuous trading mode")
            scheduler.start()

    except KeyboardInterrupt:
        logger.info("Shutdown requested by user")
        scheduler.stop()

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)

    logger.info("AutoTrader stopped")


if __name__ == "__main__":
    main()
