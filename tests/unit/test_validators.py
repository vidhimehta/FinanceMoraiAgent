"""
Unit tests for validators module.
"""

import pytest
from datetime import datetime, date

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from utils.validators import (
    validate_ticker,
    validate_date,
    validate_date_range,
    validate_dataframe,
    validate_ohlcv_data,
    validate_percentage,
    validate_positive_number,
    validate_horizon,
)
from utils.exceptions import ValidationException
import pandas as pd
import numpy as np


class TestTickerValidation:
    """Test ticker validation."""

    def test_valid_us_ticker(self):
        """Test valid US ticker."""
        assert validate_ticker("AAPL") == "AAPL"
        assert validate_ticker("googl") == "GOOGL"
        assert validate_ticker("BRK.B") == "BRK.B"

    def test_valid_indian_ticker(self):
        """Test valid Indian ticker."""
        assert validate_ticker("TCS.NS") == "TCS.NS"
        assert validate_ticker("reliance.bo") == "RELIANCE.BO"

    def test_invalid_ticker(self):
        """Test invalid ticker."""
        with pytest.raises(ValidationException):
            validate_ticker("")

        with pytest.raises(ValidationException):
            validate_ticker("AAPL@#$")

        with pytest.raises(ValidationException):
            validate_ticker(None)


class TestDateValidation:
    """Test date validation."""

    def test_valid_date_string(self):
        """Test valid date string."""
        result = validate_date("2024-01-01")
        assert isinstance(result, datetime)
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 1

    def test_valid_datetime(self):
        """Test datetime object."""
        dt = datetime(2024, 1, 1)
        result = validate_date(dt)
        assert result == dt

    def test_valid_date_object(self):
        """Test date object."""
        d = date(2024, 1, 1)
        result = validate_date(d)
        assert isinstance(result, datetime)
        assert result.date() == d

    def test_invalid_date(self):
        """Test invalid date."""
        with pytest.raises(ValidationException):
            validate_date("invalid-date")

        with pytest.raises(ValidationException):
            validate_date(123)


class TestDateRangeValidation:
    """Test date range validation."""

    def test_valid_date_range(self):
        """Test valid date range."""
        start, end = validate_date_range("2024-01-01", "2024-12-31")
        assert start < end
        assert start.year == 2024
        assert end.year == 2024

    def test_invalid_date_range(self):
        """Test invalid date range (start after end)."""
        with pytest.raises(ValidationException):
            validate_date_range("2024-12-31", "2024-01-01")

    def test_future_date(self):
        """Test future date."""
        with pytest.raises(ValidationException):
            validate_date_range("2024-01-01", "2030-12-31")


class TestDataFrameValidation:
    """Test DataFrame validation."""

    def test_valid_dataframe(self):
        """Test valid DataFrame."""
        df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
        validate_dataframe(df, required_columns=["A", "B"], min_rows=2)

    def test_missing_columns(self):
        """Test DataFrame with missing columns."""
        df = pd.DataFrame({"A": [1, 2, 3]})
        with pytest.raises(ValidationException):
            validate_dataframe(df, required_columns=["A", "B"])

    def test_insufficient_rows(self):
        """Test DataFrame with insufficient rows."""
        df = pd.DataFrame({"A": [1]})
        with pytest.raises(ValidationException):
            validate_dataframe(df, min_rows=5)

    def test_empty_dataframe(self):
        """Test empty DataFrame."""
        df = pd.DataFrame()
        with pytest.raises(ValidationException):
            validate_dataframe(df)


class TestOHLCVValidation:
    """Test OHLCV data validation."""

    def test_valid_ohlcv(self):
        """Test valid OHLCV data."""
        df = pd.DataFrame({
            "Open": [100, 101, 102],
            "High": [105, 106, 107],
            "Low": [99, 100, 101],
            "Close": [104, 105, 106],
            "Volume": [1000, 1100, 1200],
        })
        validate_ohlcv_data(df)

    def test_negative_prices(self):
        """Test negative prices."""
        df = pd.DataFrame({
            "Open": [-100, 101, 102],
            "High": [105, 106, 107],
            "Low": [99, 100, 101],
            "Close": [104, 105, 106],
            "Volume": [1000, 1100, 1200],
        })
        with pytest.raises(ValidationException):
            validate_ohlcv_data(df)

    def test_high_less_than_low(self):
        """Test high < low."""
        df = pd.DataFrame({
            "Open": [100, 101, 102],
            "High": [99, 100, 101],
            "Low": [105, 106, 107],
            "Close": [104, 105, 106],
            "Volume": [1000, 1100, 1200],
        })
        with pytest.raises(ValidationException):
            validate_ohlcv_data(df)


class TestPercentageValidation:
    """Test percentage validation."""

    def test_valid_percentage(self):
        """Test valid percentage."""
        validate_percentage(50.0)
        validate_percentage(0)
        validate_percentage(100)

    def test_invalid_percentage(self):
        """Test invalid percentage."""
        with pytest.raises(ValidationException):
            validate_percentage(-10)

        with pytest.raises(ValidationException):
            validate_percentage(150)


class TestPositiveNumberValidation:
    """Test positive number validation."""

    def test_valid_positive_number(self):
        """Test valid positive number."""
        validate_positive_number(1.0)
        validate_positive_number(100)

    def test_invalid_positive_number(self):
        """Test invalid positive number."""
        with pytest.raises(ValidationException):
            validate_positive_number(0)

        with pytest.raises(ValidationException):
            validate_positive_number(-10)


class TestHorizonValidation:
    """Test horizon validation."""

    def test_valid_horizon(self):
        """Test valid horizon."""
        validate_horizon(1)
        validate_horizon(30)
        validate_horizon(365)

    def test_invalid_horizon(self):
        """Test invalid horizon."""
        with pytest.raises(ValidationException):
            validate_horizon(0)

        with pytest.raises(ValidationException):
            validate_horizon(400)

        with pytest.raises(ValidationException):
            validate_horizon(1.5)
