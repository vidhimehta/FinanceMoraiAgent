"""
Helper utilities for FinanceMoraiAgent.
"""

import os
from pathlib import Path
from typing import Any, Optional, Dict
import yaml
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from loguru import logger


def load_config(config_path: str = "config/settings.yaml") -> Dict[str, Any]:
    """
    Load configuration from YAML file.

    Args:
        config_path: Path to configuration file

    Returns:
        Configuration dictionary
    """
    try:
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_file, "r") as f:
            config = yaml.safe_load(f)

        logger.info(f"Configuration loaded from {config_path}")
        return config

    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        raise


def get_env_variable(name: str, default: Optional[str] = None) -> Optional[str]:
    """
    Get environment variable with optional default.

    Args:
        name: Environment variable name
        default: Default value if not found

    Returns:
        Environment variable value or default
    """
    return os.environ.get(name, default)


def ensure_directory(path: str) -> Path:
    """
    Ensure directory exists, create if it doesn't.

    Args:
        path: Directory path

    Returns:
        Path object
    """
    dir_path = Path(path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def format_currency(value: float, currency: str = "USD") -> str:
    """
    Format value as currency.

    Args:
        value: Numeric value
        currency: Currency code (USD, INR, etc.)

    Returns:
        Formatted currency string
    """
    if currency == "INR":
        return f"₹{value:,.2f}"
    elif currency == "USD":
        return f"${value:,.2f}"
    else:
        return f"{currency} {value:,.2f}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """
    Format value as percentage.

    Args:
        value: Numeric value (0.1 = 10%)
        decimals: Number of decimal places

    Returns:
        Formatted percentage string
    """
    return f"{value * 100:.{decimals}f}%"


def calculate_returns(prices: pd.Series, method: str = "simple") -> pd.Series:
    """
    Calculate returns from price series.

    Args:
        prices: Price series
        method: 'simple' or 'log' returns

    Returns:
        Returns series
    """
    if method == "log":
        return np.log(prices / prices.shift(1))
    else:  # simple
        return prices.pct_change()


def calculate_volatility(
    returns: pd.Series, window: int = 20, annualize: bool = True
) -> pd.Series:
    """
    Calculate rolling volatility.

    Args:
        returns: Returns series
        window: Rolling window size
        annualize: Whether to annualize (multiply by sqrt(252))

    Returns:
        Volatility series
    """
    vol = returns.rolling(window=window).std()
    if annualize:
        vol = vol * np.sqrt(252)  # Assume 252 trading days
    return vol


def resample_ohlcv(
    df: pd.DataFrame, freq: str = "1W", agg_volume: str = "sum"
) -> pd.DataFrame:
    """
    Resample OHLCV data to different frequency.

    Args:
        df: DataFrame with OHLCV data
        freq: Frequency string (e.g., '1D', '1W', '1M')
        agg_volume: How to aggregate volume ('sum' or 'mean')

    Returns:
        Resampled DataFrame
    """
    resampled = df.resample(freq).agg(
        {
            "Open": "first",
            "High": "max",
            "Low": "min",
            "Close": "last",
            "Volume": agg_volume,
        }
    )
    return resampled.dropna()


def normalize_ticker(ticker: str) -> tuple[str, str]:
    """
    Normalize ticker and identify market.

    Args:
        ticker: Raw ticker symbol

    Returns:
        Tuple of (normalized_ticker, market)
    """
    ticker = ticker.strip().upper()

    if ticker.endswith(".NS"):
        return ticker, "NSE"
    elif ticker.endswith(".BO"):
        return ticker, "BSE"
    else:
        return ticker, "US"


def get_trading_days(start_date: datetime, end_date: datetime) -> int:
    """
    Calculate number of trading days between dates (approximate).

    Args:
        start_date: Start date
        end_date: End date

    Returns:
        Approximate number of trading days
    """
    total_days = (end_date - start_date).days
    # Approximate: 5/7 of days are trading days, minus ~10 holidays per year
    trading_days = int(total_days * (5 / 7)) - int(total_days / 365 * 10)
    return max(trading_days, 0)


def chunk_list(lst: list, chunk_size: int) -> list[list]:
    """
    Split list into chunks.

    Args:
        lst: List to split
        chunk_size: Size of each chunk

    Returns:
        List of chunks
    """
    return [lst[i : i + chunk_size] for i in range(0, len(lst), chunk_size)]


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers, returning default if denominator is zero.

    Args:
        numerator: Numerator
        denominator: Denominator
        default: Default value if division by zero

    Returns:
        Result of division or default
    """
    try:
        return numerator / denominator if denominator != 0 else default
    except (ZeroDivisionError, TypeError):
        return default


def exponential_decay(days: int, half_life: int = 7) -> float:
    """
    Calculate exponential decay weight for time-based weighting.

    Args:
        days: Number of days ago
        half_life: Half-life in days

    Returns:
        Decay weight (0-1)
    """
    return 0.5 ** (days / half_life)


def format_timedelta(td: timedelta) -> str:
    """
    Format timedelta as human-readable string.

    Args:
        td: Timedelta object

    Returns:
        Formatted string
    """
    days = td.days
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if seconds > 0 or not parts:
        parts.append(f"{seconds}s")

    return " ".join(parts)


def get_project_root() -> Path:
    """
    Get the project root directory.

    Returns:
        Path to project root
    """
    # Assuming this file is in src/utils/
    return Path(__file__).parent.parent.parent


def generate_cache_key(*args, **kwargs) -> str:
    """
    Generate cache key from arguments.

    Args:
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        Cache key string
    """
    parts = [str(arg) for arg in args]
    parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
    return ":".join(parts)
