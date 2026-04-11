"""Scheduler for automated trading cycles."""

import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

from auto_trader.config import config
from auto_trader.orchestration.bot import TradingBot

logger = logging.getLogger(__name__)


class TradingScheduler:
    """Schedules and manages trading bot execution."""

    def __init__(self):
        """Initialize scheduler."""
        self.bot = TradingBot()
        self.scheduler = BlockingScheduler()

    def setup_jobs(self) -> None:
        """Setup scheduled jobs."""
        # Main analysis cycle
        self.scheduler.add_job(
            func=self.bot.run_multi_symbol_cycle,
            trigger=IntervalTrigger(seconds=config.default_analysis_interval),
            id="analysis_cycle",
            name="Run analysis cycle",
            replace_existing=True,
        )

        # Daily reset at midnight
        self.scheduler.add_job(
            func=self.bot.reset_daily_counters,
            trigger=CronTrigger(hour=0, minute=0),
            id="daily_reset",
            name="Reset daily counters",
            replace_existing=True,
        )

        logger.info("Scheduled jobs configured")

    def start(self) -> None:
        """Start the scheduler."""
        logger.info("Starting trading scheduler...")
        self.setup_jobs()

        # Run initial analysis immediately
        logger.info("Running initial analysis cycle...")
        self.bot.run_multi_symbol_cycle()

        try:
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            logger.info("Scheduler stopped by user")
            self.stop()

    def stop(self) -> None:
        """Stop the scheduler."""
        logger.info("Stopping scheduler...")
        self.scheduler.shutdown()

    def run_once(self) -> None:
        """Run analysis cycle once (for testing)."""
        logger.info("Running single analysis cycle...")
        self.bot.run_multi_symbol_cycle()
