"""
Yahoo Finance data source wrapper.
"""

from datetime import datetime, timedelta
from typing import Optional, Union
import pandas as pd
import yfinance as yf
from loguru import logger

from ...utils.exceptions import DataSourceException
from ...utils.validators import validate_ticker, validate_date_range, validate_ohlcv_data
from ...core.cache_manager import get_cache_manager


class YahooFinanceSource:
    """
    Yahoo Finance data source for fetching stock data.
    """

    def __init__(
        self,
        use_cache: bool = True,
        cache_ttl: int = 3600,
        timeout: int = 30,
        retry_attempts: int = 3,
    ):
        """
        Initialize Yahoo Finance source.

        Args:
            use_cache: Whether to use caching
            cache_ttl: Cache time-to-live in seconds
            timeout: Request timeout in seconds
            retry_attempts: Number of retry attempts on failure
        """
        self.use_cache = use_cache
        self.cache_ttl = cache_ttl
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        self.cache_manager = get_cache_manager() if use_cache else None

        logger.info("Yahoo Finance source initialized")

    def fetch_ohlcv(
        self,
        ticker: str,
        start_date: Union[str, datetime],
        end_date: Union[str, datetime],
        interval: str = "1d",
    ) -> pd.DataFrame:
        """
        Fetch OHLCV data for a ticker.

        Args:
            ticker: Stock ticker symbol
            start_date: Start date
            end_date: End date
            interval: Data interval (1d, 1h, 1m, etc.)

        Returns:
            DataFrame with OHLCV data

        Raises:
            DataSourceException: If data fetching fails
        """
        # Validate inputs
        ticker = validate_ticker(ticker)
        start, end = validate_date_range(start_date, end_date)

        # Check cache
        cache_key = f"ohlcv:{ticker}:{start.date()}:{end.date()}:{interval}"
        if self.use_cache:
            cached_data = self.cache_manager.get(cache_key, ttl=self.cache_ttl)
            if cached_data is not None:
                logger.info(f"Using cached data for {ticker}")
                return cached_data

            # Try loading from parquet
            parquet_data = self.cache_manager.load_parquet(ticker, "ohlcv")
            if parquet_data is not None:
                # Filter by date range
                mask = (parquet_data.index >= start) & (parquet_data.index <= end)
                filtered_data = parquet_data[mask]
                if not filtered_data.empty:
                    logger.info(f"Using parquet data for {ticker}")
                    self.cache_manager.set(cache_key, filtered_data, expire=self.cache_ttl)
                    return filtered_data

        # Fetch from Yahoo Finance with retries
        for attempt in range(self.retry_attempts):
            try:
                logger.info(
                    f"Fetching {ticker} data from Yahoo Finance "
                    f"({start.date()} to {end.date()}, attempt {attempt + 1})"
                )

                ticker_obj = yf.Ticker(ticker)
                df = ticker_obj.history(
                    start=start,
                    end=end,
                    interval=interval,
                    timeout=self.timeout,
                )

                if df.empty:
                    raise DataSourceException(
                        f"No data returned for {ticker}. "
                        "Check if ticker is valid and market is open."
                    )

                # Validate data
                validate_ohlcv_data(df)

                # Cache the data
                if self.use_cache:
                    self.cache_manager.set(cache_key, df, expire=self.cache_ttl)
                    # Also save to parquet for long-term storage
                    self.cache_manager.save_parquet(df, ticker, "ohlcv")

                logger.info(f"Successfully fetched {len(df)} rows for {ticker}")
                return df

            except Exception as e:
                logger.warning(
                    f"Attempt {attempt + 1} failed for {ticker}: {e}"
                )
                if attempt == self.retry_attempts - 1:
                    raise DataSourceException(
                        f"Failed to fetch data for {ticker} after "
                        f"{self.retry_attempts} attempts: {e}"
                    )

    def fetch_info(self, ticker: str) -> dict:
        """
        Fetch ticker information (company name, sector, etc.).

        Args:
            ticker: Stock ticker symbol

        Returns:
            Dictionary with ticker information

        Raises:
            DataSourceException: If info fetching fails
        """
        ticker = validate_ticker(ticker)

        cache_key = f"info:{ticker}"
        if self.use_cache:
            cached_info = self.cache_manager.get(cache_key, ttl=86400)  # 24h TTL
            if cached_info is not None:
                return cached_info

        try:
            ticker_obj = yf.Ticker(ticker)
            info = ticker_obj.info

            if not info:
                raise DataSourceException(f"No information available for {ticker}")

            # Cache the info
            if self.use_cache:
                self.cache_manager.set(cache_key, info, expire=86400)

            logger.info(f"Fetched info for {ticker}")
            return info

        except Exception as e:
            raise DataSourceException(f"Failed to fetch info for {ticker}: {e}")

    def fetch_dividends(
        self,
        ticker: str,
        start_date: Optional[Union[str, datetime]] = None,
    ) -> pd.Series:
        """
        Fetch dividend history.

        Args:
            ticker: Stock ticker symbol
            start_date: Start date (optional)

        Returns:
            Series with dividend data

        Raises:
            DataSourceException: If data fetching fails
        """
        ticker = validate_ticker(ticker)

        try:
            ticker_obj = yf.Ticker(ticker)
            dividends = ticker_obj.dividends

            if start_date:
                start = validate_date_range(start_date, datetime.now())[0]
                dividends = dividends[dividends.index >= start]

            logger.info(f"Fetched {len(dividends)} dividend records for {ticker}")
            return dividends

        except Exception as e:
            raise DataSourceException(f"Failed to fetch dividends for {ticker}: {e}")

    def fetch_splits(
        self,
        ticker: str,
        start_date: Optional[Union[str, datetime]] = None,
    ) -> pd.Series:
        """
        Fetch stock split history.

        Args:
            ticker: Stock ticker symbol
            start_date: Start date (optional)

        Returns:
            Series with split data

        Raises:
            DataSourceException: If data fetching fails
        """
        ticker = validate_ticker(ticker)

        try:
            ticker_obj = yf.Ticker(ticker)
            splits = ticker_obj.splits

            if start_date:
                start = validate_date_range(start_date, datetime.now())[0]
                splits = splits[splits.index >= start]

            logger.info(f"Fetched {len(splits)} split records for {ticker}")
            return splits

        except Exception as e:
            raise DataSourceException(f"Failed to fetch splits for {ticker}: {e}")

    def search_ticker(self, query: str) -> list[dict]:
        """
        Search for tickers by company name or symbol.

        Args:
            query: Search query

        Returns:
            List of matching tickers with info

        Raises:
            DataSourceException: If search fails
        """
        try:
            # Use yfinance Ticker to search
            # Note: yfinance doesn't have a built-in search, so we'll try the query as a ticker
            ticker_obj = yf.Ticker(query.upper())
            info = ticker_obj.info

            if info and info.get("symbol"):
                return [
                    {
                        "symbol": info.get("symbol"),
                        "name": info.get("longName") or info.get("shortName"),
                        "exchange": info.get("exchange"),
                        "sector": info.get("sector"),
                    }
                ]
            return []

        except Exception as e:
            logger.warning(f"Search failed for '{query}': {e}")
            return []

    def get_latest_price(self, ticker: str) -> float:
        """
        Get the latest available price for a ticker.

        Args:
            ticker: Stock ticker symbol

        Returns:
            Latest price

        Raises:
            DataSourceException: If price fetching fails
        """
        ticker = validate_ticker(ticker)

        try:
            # Fetch recent data (last 5 days to ensure we get something)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=5)

            df = self.fetch_ohlcv(ticker, start_date, end_date)
            if df.empty:
                raise DataSourceException(f"No recent data available for {ticker}")

            latest_price = df["Close"].iloc[-1]
            logger.info(f"Latest price for {ticker}: {latest_price}")
            return float(latest_price)

        except Exception as e:
            raise DataSourceException(
                f"Failed to get latest price for {ticker}: {e}"
            )

    def is_market_open(self, exchange: str = "US") -> bool:
        """
        Check if market is currently open (approximate).

        Args:
            exchange: Market exchange (US, NSE, BSE)

        Returns:
            True if market is likely open
        """
        now = datetime.now()
        day_of_week = now.weekday()  # 0=Monday, 6=Sunday

        # Weekend check
        if day_of_week >= 5:  # Saturday or Sunday
            return False

        # Simple time check (not perfect, doesn't account for holidays)
        hour = now.hour

        if exchange == "US":
            # NYSE: 9:30 AM - 4:00 PM ET (approximate)
            return 9 <= hour < 16
        elif exchange in ["NSE", "BSE"]:
            # Indian markets: 9:15 AM - 3:30 PM IST
            return 9 <= hour < 16
        else:
            # Default to always open for other exchanges
            return True
