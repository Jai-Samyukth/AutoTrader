import logging
from rich.console import Console
from rich.logging import RichHandler
from rich.theme import Theme
from auto_trader.config import get_auto_trader_log_settings as settings

# Load settings
logging_settings = settings()

# ================================
# 🎨 Theme Configuration
# ================================
LOG_THEME = Theme(
    {
        "debug": "dim cyan",
        "info": "bold bright_white",
        "warning": "bold yellow",
        "error": "bold bright_red",
        "critical": "bold white on red",
        "timestamp": "dim #6c7086",
        "module": "bold #89b4fa",
        "function": "italic #74c7ec",
        "line": "dim #9399b2",
        "success": "bold green",
        "highlight": "bold magenta",
        "muted": "dim",
        "http": "bold cyan",
        "db": "bold blue",
        "cache": "bold #f9e2af",
    }
)

# Create a shared console with theme
console = Console(theme=LOG_THEME)


# ================================
# 🔧 Internal Handler Setup
# ================================
def _attach_handler(logger: logging.Logger) -> logging.Logger:
    """Attach a Rich handler safely (no duplicates)."""

    # Prevent duplicate handlers (CRITICAL)
    if logger.handlers:
        return logger

    handler = RichHandler(
        console=console,
        # level=logger.level,
        log_time_format="%Y-%m-%d %H:%M:%S",  # ✅ fixed format (no invalid %s)
        rich_tracebacks=True,
        tracebacks_show_locals=logging_settings.DEVELOPMENT_MODE,
        show_path=True,  # shows file + line
    )

    logger.addHandler(handler)
    return logger


# ================================
# 🚀 Public Logger Factory
# ================================
def getLogger(
    name: str,
    *,
    level: str | int = logging_settings.LEVEL,
) -> logging.Logger:
    """
    Create or retrieve a configured logger.

    Features:
    - Rich formatting
    - Environment-aware tracebacks
    - No duplicate handlers
    """

    logger = logging.getLogger(name)

    # Prevent double logging via root logger
    logger.propagate = False

    # Set level
    logger.setLevel(level)

    return _attach_handler(logger)


# ================================
# 🌍 Default App Logger
# ================================
logger = getLogger("auto_trader")
