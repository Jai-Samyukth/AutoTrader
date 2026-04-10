from MetaTrader5 import initialize as _initialize  # type: ignore
from MetaTrader5 import shutdown as _shutdown  # type: ignore
from MetaTrader5 import login as _login  # type: ignore
from auto_trader.config import get_mt5_settings as settings
from auto_trader.utils.logger import logger

mt5_settings = settings()


def initialize_mt5():
    """
    Initialize the MetaTrader5 connection.

    Returns:
        bool: True if initialization is successful, False otherwise.
    """
    try:
        if _initialize(  # type: ignore
            login=mt5_settings.MT5_LOGIN,
            password=mt5_settings.MT5_PASSWORD.get_secret_value(),  # type: ignore
            server=mt5_settings.MT5_SERVER,
            path=mt5_settings.MT5_PATH,
        ):
            logger.info("Initialized MT5 connection")
            logger.debug(
                f"Login: {mt5_settings.MT5_LOGIN}"
                f"Password: {mt5_settings.MT5_PASSWORD}"
                f"Server: {mt5_settings.MT5_SERVER}"
                f"Terminal Path: {mt5_settings.MT5_PATH}"
            )
            return True
    except Exception as err:
        logger.exception(f"Encountered Exception: {err}")
        return False


def shutdown_mt5():
    """
    Shutdown the MetaTrader5 connection.
    """
    logger.warning("Shutting down the MT5 Connection")
    _shutdown()


def login_mt5():
    """Login to the MetaTrader5 trading account"""
    try:
        logger.info("Logging into the account")
        _login(
            login=mt5_settings.MT5_LOGIN,
            password=mt5_settings.MT5_PASSWORD,
            server=mt5_settings.MT5_SERVER,
        )
        logger.info(f"Logged into the [{mt5_settings.MT5_LOGIN}] account successfully")
        return True

    except Exception as err:
        logger.exception(f"Encountered exception: {err}")
        return False
