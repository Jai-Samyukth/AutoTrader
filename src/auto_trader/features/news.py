"""News data fetching and filtering."""

import logging

from auto_trader.config import config
from auto_trader.domain.models import NewsEvent

logger = logging.getLogger(__name__)


class NewsProvider:
    """Fetches and filters news events."""

    def __init__(self):
        """Initialize news provider."""
        self.cache: dict[str, list[NewsEvent]] = {}

    def get_upcoming_news(
        self, currencies: list[str] | None = None, lookback_minutes: int | None = None
    ) -> list[NewsEvent]:
        """Get upcoming high-impact news events."""
        if currencies is None:
            currencies = config.high_impact_currencies

        if lookback_minutes is None:
            lookback_minutes = config.news_lookback_minutes

        # In production, integrate with economic calendar API
        # For now, return empty list (placeholder)
        logger.info(f"Checking news for {currencies} within {lookback_minutes} minutes")

        # TODO: Integrate with actual news API
        # Example APIs: ForexFactory, Investing.com, FXStreet
        # For now, return empty to allow trading
        return []

    def has_high_impact_news(
        self, currencies: list[str], lookback_minutes: int | None = None
    ) -> bool:
        """Check if high-impact news is upcoming."""
        news = self.get_upcoming_news(currencies, lookback_minutes)
        return any(event.impact.lower() == "high" for event in news)

    def filter_by_currency(
        self, news_events: list[NewsEvent], currencies: list[str]
    ) -> list[NewsEvent]:
        """Filter news events by currency."""
        return [event for event in news_events if event.currency in currencies]

    def filter_by_impact(
        self, news_events: list[NewsEvent], min_impact: str = "medium"
    ) -> list[NewsEvent]:
        """Filter news events by impact level."""
        impact_order = {"low": 0, "medium": 1, "high": 2}
        min_level = impact_order.get(min_impact.lower(), 1)

        return [
            event
            for event in news_events
            if impact_order.get(event.impact.lower(), 0) >= min_level
        ]
