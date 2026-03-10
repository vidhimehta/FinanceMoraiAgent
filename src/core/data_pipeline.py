"""
Main data pipeline orchestrator for FinanceMoraiAgent.
Coordinates data fetching, preprocessing, and forecasting.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import pandas as pd
from loguru import logger

from ..data.sources.yahoo_finance import YahooFinanceSource
from ..data.preprocessor import DataPreprocessor
from ..data.feature_engineering import FeatureEngineer
from ..moirai.inference_engine import InferenceEngine
from ..moirai.context_processor import ContextProcessor
from ..core.cache_manager import get_cache_manager
from ..utils.exceptions import DataSourceException, PreprocessingException


class DataPipeline:
    """
    Orchestrates the complete data pipeline from fetching to forecasting.
    """

    def __init__(self, use_cache: bool = True):
        """
        Initialize data pipeline.

        Args:
            use_cache: Whether to use caching
        """
        self.yahoo = YahooFinanceSource(use_cache=use_cache)
        self.preprocessor = DataPreprocessor()
        self.feature_engineer = FeatureEngineer()
        self.inference_engine = InferenceEngine()
        self.context_processor = ContextProcessor()
        self.cache_manager = get_cache_manager() if use_cache else None

        logger.info("DataPipeline initialized")

    def fetch_and_prepare_data(
        self,
        ticker: str,
        start_date: datetime,
        end_date: datetime,
        add_features: bool = True,
    ) -> pd.DataFrame:
        """
        Fetch and prepare data for analysis or forecasting.

        Args:
            ticker: Stock ticker symbol
            start_date: Start date
            end_date: End date
            add_features: Whether to add technical indicators

        Returns:
            Prepared DataFrame

        Raises:
            DataSourceException: If data fetching fails
            PreprocessingException: If preprocessing fails
        """
        logger.info(f"Fetching and preparing data for {ticker}")

        # Fetch data
        df = self.yahoo.fetch_ohlcv(ticker, start_date, end_date)

        # Clean data
        df_clean = self.preprocessor.clean_ohlcv(df)

        # Add features if requested
        if add_features:
            df_clean = self.feature_engineer.add_all_features(df_clean)

        logger.info(f"Data prepared: {len(df_clean)} rows, {len(df_clean.columns)} columns")
        return df_clean

    def generate_forecast(
        self,
        ticker: str,
        horizon: int = 30,
        lookback_days: int = 90,
        use_context: bool = False,
    ) -> Dict[str, Any]:
        """
        Generate forecast for a ticker.

        Args:
            ticker: Stock ticker symbol
            horizon: Forecast horizon in days
            lookback_days: Number of historical days to use
            use_context: Whether to use contextual information

        Returns:
            Dictionary with forecast results
        """
        logger.info(f"Generating {horizon}-day forecast for {ticker}")

        # Fetch historical data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=lookback_days)

        df = self.fetch_and_prepare_data(
            ticker, start_date, end_date, add_features=use_context
        )

        # Prepare context if requested
        context = None
        if use_context:
            context = self._generate_context(ticker, df)

        # Generate forecast
        forecast_result = self.inference_engine.forecast(
            data=df,
            horizon=horizon,
            context=context,
            confidence_level=0.80,
        )

        # Add metadata
        forecast_result["ticker"] = ticker
        forecast_result["generated_at"] = datetime.now().isoformat()
        forecast_result["lookback_days"] = lookback_days
        forecast_result["historical_data"] = df

        logger.info(f"Forecast generated successfully for {ticker}")
        return forecast_result

    def _generate_context(self, ticker: str, df: pd.DataFrame) -> str:
        """
        Generate natural language context from data.

        Args:
            ticker: Stock ticker symbol
            df: Historical data with features

        Returns:
            Context string
        """
        # Extract technical signals
        technical_signals = {}

        if "RSI" in df.columns:
            technical_signals["rsi"] = float(df["RSI"].iloc[-1])

        if "MACD" in df.columns and "MACD_signal" in df.columns:
            macd = df["MACD"].iloc[-1]
            signal = df["MACD_signal"].iloc[-1]
            technical_signals["macd_signal"] = "bullish" if macd > signal else "bearish"

        # Determine trend
        if "SMA_50" in df.columns and "SMA_200" in df.columns:
            sma_50 = df["SMA_50"].iloc[-1]
            sma_200 = df["SMA_200"].iloc[-1]
            if sma_50 > sma_200:
                technical_signals["trend"] = "bullish"
            else:
                technical_signals["trend"] = "bearish"

        # Prepare context
        context = self.context_processor.prepare_context(
            ticker=ticker,
            historical_data=df,
            technical_signals=technical_signals,
        )

        return context

    def backfill_historical_data(
        self,
        ticker: str,
        start_date: datetime,
        end_date: datetime,
    ) -> None:
        """
        Backfill historical data to parquet storage.

        Args:
            ticker: Stock ticker symbol
            start_date: Start date
            end_date: End date
        """
        logger.info(f"Backfilling data for {ticker}")

        df = self.fetch_and_prepare_data(ticker, start_date, end_date)

        if self.cache_manager:
            self.cache_manager.save_parquet(df, ticker, "ohlcv")
            logger.info(f"Backfilled {len(df)} rows to parquet storage")
