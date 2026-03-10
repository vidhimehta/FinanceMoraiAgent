"""
Input validation utilities for FinanceMoraiAgent.
"""

import re
from datetime import datetime, date
from typing import Optional, Union
import pandas as pd
from .exceptions import ValidationException


def validate_ticker(ticker: str) -> str:
    """
    Validate stock ticker symbol.

    Args:
        ticker: Stock ticker symbol

    Returns:
        Validated and normalized ticker

    Raises:
        ValidationException: If ticker is invalid
    """
    if not ticker or not isinstance(ticker, str):
        raise ValidationException("Ticker must be a non-empty string")

    ticker = ticker.strip().upper()

    # Allow alphanumeric characters, dots, and hyphens
    if not re.match(r"^[A-Z0-9\.\-]+$", ticker):
        raise ValidationException(
            f"Invalid ticker format: {ticker}. "
            "Must contain only letters, numbers, dots, and hyphens."
        )

    # Check for common Indian market suffixes
    if ticker.endswith((".NS", ".BO")):
        base_ticker = ticker.rsplit(".", 1)[0]
        if not base_ticker:
            raise ValidationException(f"Invalid ticker: {ticker}")

    return ticker


def validate_date(
    date_input: Union[str, datetime, date], date_name: str = "date"
) -> datetime:
    """
    Validate and convert date input to datetime.

    Args:
        date_input: Date as string, datetime, or date object
        date_name: Name of the date field for error messages

    Returns:
        datetime object

    Raises:
        ValidationException: If date is invalid
    """
    if isinstance(date_input, datetime):
        return date_input
    elif isinstance(date_input, date):
        return datetime.combine(date_input, datetime.min.time())
    elif isinstance(date_input, str):
        # Try common date formats
        formats = [
            "%Y-%m-%d",
            "%Y/%m/%d",
            "%d-%m-%Y",
            "%d/%m/%Y",
            "%Y%m%d",
            "%m-%d-%Y",
            "%m/%d/%Y",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_input, fmt)
            except ValueError:
                continue

        raise ValidationException(
            f"Invalid {date_name} format: {date_input}. "
            "Expected format: YYYY-MM-DD"
        )
    else:
        raise ValidationException(
            f"{date_name} must be a string, datetime, or date object"
        )


def validate_date_range(
    start_date: Union[str, datetime, date],
    end_date: Union[str, datetime, date],
) -> tuple[datetime, datetime]:
    """
    Validate a date range.

    Args:
        start_date: Start date
        end_date: End date

    Returns:
        Tuple of (start_datetime, end_datetime)

    Raises:
        ValidationException: If date range is invalid
    """
    start = validate_date(start_date, "start_date")
    end = validate_date(end_date, "end_date")

    if start >= end:
        raise ValidationException(
            f"start_date ({start.date()}) must be before end_date ({end.date()})"
        )

    # Check if date range is reasonable (not too far in the past or future)
    now = datetime.now()
    max_past = datetime(1900, 1, 1)

    if start < max_past:
        raise ValidationException(f"start_date cannot be before {max_past.date()}")

    if end > now:
        raise ValidationException("end_date cannot be in the future")

    return start, end


def validate_dataframe(
    df: pd.DataFrame,
    required_columns: Optional[list[str]] = None,
    min_rows: int = 1,
) -> None:
    """
    Validate a pandas DataFrame.

    Args:
        df: DataFrame to validate
        required_columns: List of required column names
        min_rows: Minimum number of rows required

    Raises:
        ValidationException: If DataFrame is invalid
    """
    if not isinstance(df, pd.DataFrame):
        raise ValidationException("Input must be a pandas DataFrame")

    if df.empty:
        raise ValidationException("DataFrame is empty")

    if len(df) < min_rows:
        raise ValidationException(
            f"DataFrame has {len(df)} rows, but {min_rows} required"
        )

    if required_columns:
        missing = set(required_columns) - set(df.columns)
        if missing:
            raise ValidationException(
                f"DataFrame missing required columns: {missing}"
            )


def validate_ohlcv_data(df: pd.DataFrame) -> None:
    """
    Validate OHLCV (Open, High, Low, Close, Volume) data.

    Args:
        df: DataFrame with OHLCV data

    Raises:
        ValidationException: If OHLCV data is invalid
    """
    required_columns = ["Open", "High", "Low", "Close", "Volume"]
    validate_dataframe(df, required_columns=required_columns)

    # Check for negative values
    for col in ["Open", "High", "Low", "Close"]:
        if (df[col] < 0).any():
            raise ValidationException(f"Negative values found in {col} column")

    # Check high >= low
    if (df["High"] < df["Low"]).any():
        raise ValidationException("High price is less than Low price in some rows")

    # Check for NaN values
    if df[required_columns].isna().any().any():
        raise ValidationException("NaN values found in OHLCV data")


def validate_percentage(value: float, name: str = "value") -> None:
    """
    Validate a percentage value (0-100).

    Args:
        value: Percentage value
        name: Name of the field for error messages

    Raises:
        ValidationException: If percentage is invalid
    """
    if not isinstance(value, (int, float)):
        raise ValidationException(f"{name} must be a number")

    if value < 0 or value > 100:
        raise ValidationException(f"{name} must be between 0 and 100")


def validate_positive_number(value: float, name: str = "value") -> None:
    """
    Validate a positive number.

    Args:
        value: Number to validate
        name: Name of the field for error messages

    Raises:
        ValidationException: If number is invalid
    """
    if not isinstance(value, (int, float)):
        raise ValidationException(f"{name} must be a number")

    if value <= 0:
        raise ValidationException(f"{name} must be positive")


def validate_horizon(horizon: int) -> None:
    """
    Validate forecast horizon.

    Args:
        horizon: Forecast horizon in days

    Raises:
        ValidationException: If horizon is invalid
    """
    if not isinstance(horizon, int):
        raise ValidationException("Horizon must be an integer")

    if horizon < 1:
        raise ValidationException("Horizon must be at least 1 day")

    if horizon > 365:
        raise ValidationException("Horizon cannot exceed 365 days")
