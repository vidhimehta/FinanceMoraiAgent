"""
Logging configuration for FinanceMoraiAgent.
"""

import sys
from pathlib import Path
from loguru import logger
from typing import Optional
import yaml


def setup_logger(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    rotation: str = "100 MB",
    retention: str = "30 days",
    console_output: bool = True,
) -> None:
    """
    Configure the logger for the application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file, None to disable file logging
        rotation: Log rotation size
        retention: Log retention period
        console_output: Whether to output to console
    """
    # Remove default handler
    logger.remove()

    # Custom format
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )

    # Add console handler if enabled
    if console_output:
        logger.add(
            sys.stderr,
            format=log_format,
            level=log_level,
            colorize=True,
        )

    # Add file handler if log_file is specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        logger.add(
            log_file,
            format=log_format,
            level=log_level,
            rotation=rotation,
            retention=retention,
            compression="zip",
        )

    logger.info(f"Logger initialized with level: {log_level}")


def load_logging_config(config_path: str = "config/settings.yaml") -> dict:
    """
    Load logging configuration from YAML file.

    Args:
        config_path: Path to configuration file

    Returns:
        Dictionary with logging configuration
    """
    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
            return config.get("logging", {})
    except Exception as e:
        logger.warning(f"Failed to load logging config: {e}. Using defaults.")
        return {}


def get_logger(name: str):
    """
    Get a logger instance with the given name.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    return logger.bind(name=name)
