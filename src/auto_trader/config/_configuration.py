"""
Contains the settings file for this system
"""

from pathlib import Path
from pydantic.types import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class MT5Settings(BaseSettings):
    """
    MetaTrader5 Settings, .env files will be loaded first
    """

    MT5_LOGIN: str | None = None
    MT5_PASSWORD: SecretStr | None = None
    MT5_SERVER: str | None = None
    MT5_PATH: str | Path | None = None

    model_config: SettingsConfigDict = SettingsConfigDict(  # pyright: ignore[reportIncompatibleVariableOverride]
        env_file="../../../.env", env_file_encoding="utf-8", extra="ignore"
    )


class LoggingSettings(BaseSettings):
    """Logging Config for the AutoTrader's Logging"""

    LEVEL: str | int = "DEBUG"
    LOG_DIR: Path = Path.cwd() / "ATLogs"
    LOG_FILE_FORMAT: str = "Auto_Trader_%B_%d_%Y.log"
    DEVELOPMENT_MODE: bool = True
    model_config: SettingsConfigDict = SettingsConfigDict(  # pyright: ignore[reportIncompatibleVariableOverride]
        env_file="../../../.env", env_file_encoding="utf-8", extra="ignore"
    )


def get_mt5_settings() -> MT5Settings:
    """
    Returns the MT5 settings
    """
    return MT5Settings()


def get_auto_trader_log_settings() -> LoggingSettings:
    """Returns the AutoTrader's Logging config"""
    return LoggingSettings()
