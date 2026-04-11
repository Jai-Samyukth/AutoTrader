"""Logging configuration with loguru."""

import sys
from pathlib import Path
from loguru import logger

from auto_trader.config import config


def setup_logging() -> None:
    """Configure loguru logging with emojis and colors."""
    # Remove default handler
    logger.remove()
    
    # Console handler with colors and emojis
    # Use UTF-8 encoding for Windows console to support emojis
    try:
        # Try to reconfigure stdout to use UTF-8
        if sys.platform == "win32":
            import io
            sys.stdout = io.TextIOWrapper(
                sys.stdout.buffer,
                encoding='utf-8',
                errors='replace',
                line_buffering=True
            )
    except Exception:
        pass  # If reconfiguration fails, continue with default
    
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level=config.log_level,
        colorize=True,
        enqueue=True,
    )
    
    # File handler
    if config.log_to_file:
        log_path = Path(config.log_file_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.add(
            log_path,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} | {message}",
            level=config.log_level,
            rotation="10 MB",
            retention="7 days",
            compression="zip",
            enqueue=True,
            encoding="utf-8",
        )
    
    # Suppress noisy loggers
    import logging
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    
    logger.info("✅ Logging configured")
