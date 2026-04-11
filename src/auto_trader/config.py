"""Configuration management for the trading system."""

from typing import Literal
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class TradingConfig(BaseSettings):
    """Trading system configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_parse_none_str="",
    )

    # LLM Configuration
    llm_api_key: str = Field(default="", alias="LLM_API_KEY")
    llm_base_url: str = Field(default="", alias="LLM_BASE_URL")
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    llm_provider: Literal["anthropic", "openai", "groq"] = Field(default="anthropic")
    llm_model: str = Field(default="claude-3-5-sonnet-20241022")
    llm_temperature: float = Field(default=0.0)

    # MT5 Configuration
    mt5_login: str = Field(default="", alias="MT5_LOGIN")
    mt5_password: str = Field(default="", alias="MT5_PASSWORD")
    mt5_server: str = Field(default="", alias="MT5_SERVER")
    mt5_base_url: str = Field(default="http://localhost:8001/api/v1")
    mt5_timeout: int = Field(default=30)

    # Trading Pairs
    symbols: list[str] = Field(default=["EURUSD.m", "GBPUSD.m"])
    timeframes: list[str] = Field(default=["15m", "1h", "4h", "1w"])

    # Risk Management
    max_risk_per_trade_pct: float = Field(default=1.0)
    default_risk_reward_ratio: float = Field(default=2.0)
    confidence_threshold: float = Field(default=0.75)
    phase1_floor: float = Field(default=0.50)
    phase2_floor: float = Field(default=0.50)
    min_rr_ratio: float = Field(default=1.5)
    max_daily_loss_pct: float = Field(default=3.0)
    max_trades_per_day: int = Field(default=5)

    # News Filter
    news_lookback_minutes: int = Field(default=60)
    high_impact_currencies: list[str] = Field(default=["USD", "EUR", "GBP"])

    # Scheduler
    default_analysis_interval: int = Field(default=900)  # 15 minutes
    market_open_hour: int = Field(default=0)
    market_close_hour: int = Field(default=22)

    # Logging
    log_level: str = Field(default="DEBUG")
    log_to_file: bool = Field(default=True)
    log_file_path: str = Field(default="./logs/trader_ai.log")

    # Mode
    paper_trading_mode: bool = Field(default=True)
    human_in_the_loop: bool = Field(default=False)

    @field_validator('symbols', 'timeframes', 'high_impact_currencies', mode='before')
    @classmethod
    def parse_comma_separated(cls, v):
        """Parse comma-separated strings into lists."""
        if isinstance(v, str):
            return [item.strip() for item in v.split(',') if item.strip()]
        return v

    @property
    def is_anthropic(self) -> bool:
        """Check if using Anthropic."""
        return self.llm_provider == "anthropic"

    @property
    def is_openai(self) -> bool:
        """Check if using OpenAI."""
        return self.llm_provider == "openai"

    @property
    def is_groq(self) -> bool:
        """Check if using GROQ."""
        return self.llm_provider == "groq"


# Global config instance
config = TradingConfig()
