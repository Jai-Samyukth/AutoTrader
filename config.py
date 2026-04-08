"""
Configuration management for Trader AI System.
Loads and validates all environment variables required for system operation.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class ConfigurationError(Exception):
    """Raised when configuration is missing or invalid."""
    pass


class Config:
    """Global configuration for Trader AI System."""
    
    # LLM Configuration
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    
    # MT5 Configuration
    MT5_LOGIN: Optional[str] = os.getenv("MT5_LOGIN")
    MT5_PASSWORD: Optional[str] = os.getenv("MT5_PASSWORD")
    MT5_SERVER: Optional[str] = os.getenv("MT5_SERVER")
    MT5_PATH: Optional[str] = os.getenv("MT5_PATH")
    MT5_DEMO: bool = os.getenv("MT5_DEMO", "true").lower() == "true"
    
    # TradingView Data Configuration
    TV_DATA_SOURCE: str = os.getenv("TV_DATA_SOURCE", "yfinance")
    ALPHA_VANTAGE_KEY: Optional[str] = os.getenv("ALPHA_VANTAGE_KEY")
    
    # Trading Configuration
    SYMBOLS: list[str] = os.getenv("SYMBOLS", "EURUSD,GBPUSD").split(",")
    TIMEFRAMES: list[str] = os.getenv("TIMEFRAMES", "1h,4h").split(",")
    
    # Risk Management Configuration
    MAX_RISK_PER_TRADE_PCT: float = float(os.getenv("MAX_RISK_PER_TRADE_PCT", "1.0"))
    DEFAULT_RISK_REWARD_RATIO: float = float(os.getenv("DEFAULT_RISK_REWARD_RATIO", "2.0"))
    CONFIDENCE_THRESHOLD: float = float(os.getenv("CONFIDENCE_THRESHOLD", "0.75"))
    
    # Scheduler Configuration
    DEFAULT_ANALYSIS_INTERVAL: int = int(os.getenv("DEFAULT_ANALYSIS_INTERVAL", "900"))  # seconds
    MARKET_OPEN_HOUR: int = int(os.getenv("MARKET_OPEN_HOUR", "0"))  # UTC
    MARKET_CLOSE_HOUR: int = int(os.getenv("MARKET_CLOSE_HOUR", "22"))  # UTC
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_TO_FILE: bool = os.getenv("LOG_TO_FILE", "true").lower() == "true"
    LOG_FILE_PATH: str = os.getenv("LOG_FILE_PATH", "./logs/trader_ai.log")
    
    # Human-in-the-Loop Configuration
    HUMAN_IN_THE_LOOP: bool = os.getenv("HUMAN_IN_THE_LOOP", "false").lower() == "true"
    
    # Paper Trading Configuration
    PAPER_TRADING_MODE: bool = os.getenv("PAPER_TRADING_MODE", "true").lower() == "true"
    
    @classmethod
    def validate(cls) -> None:
        """
        Validate all required configuration values.
        Raises ConfigurationError if any required values are missing or invalid.
        """
        errors = []
        
        # Validate LLM API keys (at least one required)
        if not cls.OPENAI_API_KEY and not cls.ANTHROPIC_API_KEY:
            errors.append("At least one LLM API key required: OPENAI_API_KEY or ANTHROPIC_API_KEY")
        
        # Validate MT5 configuration
        if not cls.MT5_LOGIN:
            errors.append("MT5_LOGIN is required")
        if not cls.MT5_PASSWORD:
            errors.append("MT5_PASSWORD is required")
        if not cls.MT5_SERVER:
            errors.append("MT5_SERVER is required")
        
        # Validate symbols
        if not cls.SYMBOLS or len(cls.SYMBOLS) == 0:
            errors.append("At least one symbol must be configured in SYMBOLS")
        
        # Validate timeframes
        if not cls.TIMEFRAMES or len(cls.TIMEFRAMES) == 0:
            errors.append("At least one timeframe must be configured in TIMEFRAMES")
        
        # Validate risk parameters
        if cls.MAX_RISK_PER_TRADE_PCT <= 0 or cls.MAX_RISK_PER_TRADE_PCT > 100:
            errors.append("MAX_RISK_PER_TRADE_PCT must be between 0 and 100")
        
        if cls.DEFAULT_RISK_REWARD_RATIO <= 0:
            errors.append("DEFAULT_RISK_REWARD_RATIO must be greater than 0")
        
        if cls.CONFIDENCE_THRESHOLD < 0 or cls.CONFIDENCE_THRESHOLD > 1:
            errors.append("CONFIDENCE_THRESHOLD must be between 0 and 1")
        
        # Validate market hours
        if cls.MARKET_OPEN_HOUR < 0 or cls.MARKET_OPEN_HOUR > 23:
            errors.append("MARKET_OPEN_HOUR must be between 0 and 23")
        
        if cls.MARKET_CLOSE_HOUR < 0 or cls.MARKET_CLOSE_HOUR > 23:
            errors.append("MARKET_CLOSE_HOUR must be between 0 and 23")
        
        # Validate log level
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if cls.LOG_LEVEL.upper() not in valid_log_levels:
            errors.append(f"LOG_LEVEL must be one of: {', '.join(valid_log_levels)}")
        
        if errors:
            raise ConfigurationError(
                "Configuration validation failed:\n" + "\n".join(f"  - {error}" for error in errors)
            )
    
    @classmethod
    def get_llm_provider(cls) -> str:
        """Determine which LLM provider to use based on available API keys."""
        if cls.OPENAI_API_KEY:
            return "openai"
        elif cls.ANTHROPIC_API_KEY:
            return "anthropic"
        else:
            raise ConfigurationError("No LLM API key configured")


# Validate configuration on module import
try:
    Config.validate()
except ConfigurationError as e:
    print(f"WARNING: {e}")
    print("Please configure the required environment variables in .env file")
