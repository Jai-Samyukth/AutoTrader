"""Feature extraction layer."""

from auto_trader.features.smc import SMCAnalyzer
from auto_trader.features.news import NewsProvider

__all__ = ["SMCAnalyzer", "NewsProvider"]
