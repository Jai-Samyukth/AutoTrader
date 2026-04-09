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
    MT5_LOGIN: str | None
    MT5_PASSWORD: SecretStr | None 
    MT5_SERVER: str | None
    MT5_PATH: str | Path | None

    model_config: SettingsConfigDict = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

