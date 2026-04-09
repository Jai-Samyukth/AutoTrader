from pathlib import Path
import MetaTrader5 as mt5


def initialize_mt5(
    mt5_login: str,
    mt5_password: str,
    mt5_server: str,
    mt5_path: str | Path,
):
    """
    Initialize the MetaTrader5 API connection I suppose
    """
    mt5.initialize() #type: ignore