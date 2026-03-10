"""
Yahoo Finance data source wrapper with rate limit handling.
"""

from datetime import datetime, timedelta
from typing import Optional, Union
import pandas as pd
import yfinance as yf
from loguru import logger
import time

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
        retry_delay: int = 5,
    ):
        """
        Initialize Yahoo Finance source.

        Args:
            use_cache: Whether to use caching
            cache_ttl: Cache time-to-live in seconds
            timeout: Request timeout in seconds
            retry_attempts: Number of retry attempts on failure
            retry_delay: Delay between retries in seconds
        """
        self.use_cache = use_cache
        self.cache_ttl = cache_ttl
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
        self.cache_manager = get_cache_manager() if use_cache else None

        logger.info("Yahoo Finance source initialized")

    def _flatten_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Flatten multi-index columns from yfinance.
        
        Args:
            df: DataFrame with potentially multi-index columns
            
        Returns:
            DataFrame with flattened columns
        """
        if isinstance(df.columns, pd.MultiIndex):
            # New yfinance format: (Price, Ticker) -> Price
            df.columns = df.columns.get_level_values(0)
        return df

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

        # Fetch from Yahoo Finance with retries and rate limit handling
        for attempt in range(self.retry_attempts):
            try:
                logger.info(
                    f"Fetching {ticker} data from Yahoo Finance "
                    f"({start.date()} to {end.date()}, attempt {attempt + 1})"
                )

                # Add delay to avoid rate limiting
                if attempt > 0:
                    delay = self.retry_delay * attempt
                    logger.info(f"Waiting {delay} seconds before retry...")
                    time.sleep(delay)

                # Use yfinance download which is more reliable
                df = yf.download(
                    ticker,
                    start=start,
                    end=end,
                    interval=interval,
                    progress=False,
                    timeout=self.timeout,
                )

                # Flatten multi-index columns (new yfinance format)
                df = self._flatten_columns(df)

                if df.empty:
                    # Try alternative: check if market is open/weekend
                    if end.date() == datetime.now().date() and datetime.now().weekday() >= 5:
                        raise DataSourceException(
                            f"No data returned for {ticker}. "
                            "Market might be closed (weekend/holiday). Try a date range ending on a weekday."
                        )
                    raise DataSourceException(
                        f"No data returned for {ticker}. "
                        "Check if ticker is valid and date range is reasonable."
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

            except DataSourceException:
                # Re-raise our custom exceptions
                raise
            except Exception as e:
                error_msg = str(e).lower()
                
                # Check for rate limiting
                if "429" in error_msg or "too many requests" in error_msg:
                    logger.warning(
                        f"Rate limited by Yahoo Finance (attempt {attempt + 1}). "
                        f"Waiting {self.retry_delay * 2} seconds..."
                    )
                    time.sleep(self.retry_delay * 2)
                    continue
                
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
            # Add small delay to avoid rate limiting
            time.sleep(1)
            
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
