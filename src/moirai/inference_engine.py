"""
Inference engine for generating forecasts using Moirai or statistical methods.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from loguru import logger

from ..utils.exceptions import ModelException
from ..utils.validators import validate_dataframe


class InferenceEngine:
    """
    Generates time-series forecasts using multiple methods.
    """

    def __init__(
        self,
        model_loader = None,
        fallback_method: str = "statistical",
    ):
        """
        Initialize inference engine.

        Args:
            model_loader: MoiraiModelLoader instance (optional)
            fallback_method: Method to use if model not available
        """
        self.model_loader = model_loader
        self.fallback_method = fallback_method
        
        logger.info(f"InferenceEngine initialized with fallback={fallback_method}")

    def forecast(
        self,
        data: pd.DataFrame,
        horizon: int = 30,
        context: Optional[str] = None,
        confidence_level: float = 0.80,
    ) -> Dict[str, Any]:
        """
        Generate forecast for time series data.

        Args:
            data: Historical OHLCV data
            horizon: Number of periods to forecast
            context: Natural language context (optional)
            confidence_level: Confidence level for intervals (0.80 = 80%)

        Returns:
            Dictionary with forecast results
        """
        validate_dataframe(data, required_columns=["Close"], min_rows=10)
        
        logger.info(f"Generating {horizon}-period forecast")
        
        # Try Moirai model first if available
        if self.model_loader and self.model_loader.is_loaded():
            try:
                return self._forecast_with_moirai(data, horizon, context, confidence_level)
            except Exception as e:
                logger.warning(f"Moirai forecast failed: {e}, using fallback")
        
        # Use statistical fallback
        return self._forecast_statistical(data, horizon, confidence_level)

    def _forecast_with_moirai(
        self,
        data: pd.DataFrame,
        horizon: int,
        context: Optional[str],
        confidence_level: float,
    ) -> Dict[str, Any]:
        """
        Generate forecast using Moirai model.

        Args:
            data: Historical data
            horizon: Forecast horizon
            context: Natural language context
            confidence_level: Confidence level

        Returns:
            Forecast results
        """
        logger.info("Using Moirai model for forecast")
        
        # Prepare data for Moirai
        prices = data["Close"].values
        
        # TODO: Implement Moirai-specific inference
        # For now, use statistical method
        raise NotImplementedError("Moirai inference not yet implemented")

    def _forecast_statistical(
        self,
        data: pd.DataFrame,
        horizon: int,
        confidence_level: float,
    ) -> Dict[str, Any]:
        """
        Generate forecast using statistical methods.

        Args:
            data: Historical data
            horizon: Forecast horizon
            confidence_level: Confidence level

        Returns:
            Forecast results
        """
        logger.info("Using statistical forecasting")
        
        prices = data["Close"].values
        dates = data.index
        
        # Use exponential smoothing with trend
        forecast, lower, upper = self._exponential_smoothing_forecast(
            prices, horizon, confidence_level
        )
        
        # Generate future dates
        last_date = dates[-1]
        future_dates = pd.date_range(
            start=last_date + timedelta(days=1),
            periods=horizon,
            freq='D'
        )
        
        # Calculate forecast statistics
        last_price = prices[-1]
        forecast_return = (forecast[-1] - last_price) / last_price
        
        return {
            "method": "exponential_smoothing",
            "horizon": horizon,
            "dates": future_dates,
            "forecast": forecast,
            "lower_bound": lower,
            "upper_bound": upper,
            "confidence_level": confidence_level,
            "statistics": {
                "last_price": float(last_price),
                "forecast_final": float(forecast[-1]),
                "expected_return": float(forecast_return),
                "min_forecast": float(forecast.min()),
                "max_forecast": float(forecast.max()),
            },
        }

    def _exponential_smoothing_forecast(
        self,
        prices: np.ndarray,
        horizon: int,
        confidence_level: float,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Exponential smoothing with trend (Holt's method).

        Args:
            prices: Historical prices
            horizon: Forecast horizon
            confidence_level: Confidence level for bounds

        Returns:
            Tuple of (forecast, lower_bound, upper_bound)
        """
        # Parameters for exponential smoothing
        alpha = 0.3  # Level smoothing
        beta = 0.1   # Trend smoothing
        
        # Initialize
        level = prices[0]
        trend = prices[1] - prices[0] if len(prices) > 1 else 0
        
        # Fit the model
        for price in prices[1:]:
            level_prev = level
            level = alpha * price + (1 - alpha) * (level + trend)
            trend = beta * (level - level_prev) + (1 - beta) * trend
        
        # Generate forecast
        forecast = np.zeros(horizon)
        for h in range(horizon):
            forecast[h] = level + (h + 1) * trend
        
        # Calculate confidence intervals based on historical volatility
        returns = np.diff(prices) / prices[:-1]
        volatility = np.std(returns)
        
        # Z-score for confidence level
        z_score = {
            0.80: 1.28,
            0.90: 1.645,
            0.95: 1.96,
            0.99: 2.576,
        }.get(confidence_level, 1.645)
        
        # Expand uncertainty over time
        uncertainty = np.array([
            forecast[h] * volatility * np.sqrt(h + 1) * z_score
            for h in range(horizon)
        ])
        
        lower_bound = forecast - uncertainty
        upper_bound = forecast + uncertainty
        
        return forecast, lower_bound, upper_bound

    def _simple_moving_average_forecast(
        self,
        prices: np.ndarray,
        horizon: int,
        window: int = 20,
    ) -> np.ndarray:
        """
        Simple moving average forecast.

        Args:
            prices: Historical prices
            horizon: Forecast horizon
            window: Moving average window

        Returns:
            Forecast array
        """
        # Calculate moving average
        ma = np.mean(prices[-window:])
        
        # Calculate trend
        trend = (prices[-1] - prices[-window]) / window
        
        # Generate forecast
        forecast = np.array([ma + trend * (h + 1) for h in range(horizon)])
        
        return forecast
