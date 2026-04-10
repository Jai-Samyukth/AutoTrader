"""Test configuration loading."""

from auto_trader.config import TradingConfig


def test_config_defaults():
    """Test default configuration values."""
    config = TradingConfig()

    assert config.llm_provider in ["anthropic", "openai"]
    assert config.max_risk_per_trade_pct == 1.0
    assert config.confidence_threshold == 0.75
    assert config.min_rr_ratio == 1.5
    assert config.paper_trading_mode is True


def test_config_symbols():
    """Test symbols configuration."""
    config = TradingConfig()

    assert isinstance(config.symbols, list)
    assert len(config.symbols) > 0
    assert all(isinstance(s, str) for s in config.symbols)


def test_config_timeframes():
    """Test timeframes configuration."""
    config = TradingConfig()

    assert isinstance(config.timeframes, list)
    assert len(config.timeframes) > 0
    assert all(isinstance(tf, str) for tf in config.timeframes)


def test_config_risk_limits():
    """Test risk limit configurations."""
    config = TradingConfig()

    assert 0 < config.max_risk_per_trade_pct <= 5.0
    assert 0 < config.max_daily_loss_pct <= 10.0
    assert config.max_trades_per_day > 0
