"""
Feature engineering for technical indicators and derived features.
Manual implementation without pandas-ta dependency.
"""

import pandas as pd
import numpy as np
from loguru import logger
from typing import Optional, List

from ..utils.exceptions import PreprocessingException
from ..utils.validators import validate_dataframe


class FeatureEngineer:
    """
    Generate technical indicators and features from OHLCV data.
    """

    def __init__(self):
        """Initialize feature engineer."""
        logger.info("FeatureEngineer initialized")

    def add_all_features(
        self,
        df: pd.DataFrame,
        include_price_ma: bool = True,
        include_momentum: bool = True,
        include_volatility: bool = True,
        include_volume: bool = True,
    ) -> pd.DataFrame:
        """
        Add all technical indicators to DataFrame.

        Args:
            df: DataFrame with OHLCV data
            include_price_ma: Include moving averages
            include_momentum: Include momentum indicators
            include_volatility: Include volatility indicators
            include_volume: Include volume indicators

        Returns:
            DataFrame with added features
        """
        try:
            validate_dataframe(df, required_columns=["Open", "High", "Low", "Close", "Volume"])

            df_features = df.copy()

            if include_price_ma:
                df_features = self.add_moving_averages(df_features)

            if include_momentum:
                df_features = self.add_momentum_indicators(df_features)

            if include_volatility:
                df_features = self.add_volatility_indicators(df_features)

            if include_volume:
                df_features = self.add_volume_indicators(df_features)

            # Add returns
            df_features = self.add_returns(df_features)

            logger.info(f"Added features: {len(df_features.columns)} total columns")
            return df_features

        except Exception as e:
            raise PreprocessingException(f"Failed to add features: {e}")

    def add_moving_averages(
        self,
        df: pd.DataFrame,
        periods: Optional[List[int]] = None,
    ) -> pd.DataFrame:
        """
        Add moving averages (SMA and EMA).

        Args:
            df: DataFrame with price data
            periods: List of periods (default: [20, 50, 200])

        Returns:
            DataFrame with moving averages
        """
        if periods is None:
            periods = [20, 50, 200]

        df_ma = df.copy()

        for period in periods:
            # Simple Moving Average
            df_ma[f"SMA_{period}"] = df_ma["Close"].rolling(window=period).mean()

            # Exponential Moving Average
            df_ma[f"EMA_{period}"] = df_ma["Close"].ewm(span=period, adjust=False).mean()

        logger.debug(f"Added moving averages for periods: {periods}")
        return df_ma

    def add_momentum_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add momentum indicators (RSI, MACD, ROC).

        Args:
            df: DataFrame with OHLCV data

        Returns:
            DataFrame with momentum indicators
        """
        df_momentum = df.copy()

        # RSI (Relative Strength Index)
        df_momentum["RSI"] = self._calculate_rsi(df_momentum["Close"], period=14)

        # MACD (Moving Average Convergence Divergence)
        macd_data = self._calculate_macd(df_momentum["Close"])
        df_momentum["MACD"] = macd_data["macd"]
        df_momentum["MACD_signal"] = macd_data["signal"]
        df_momentum["MACD_hist"] = macd_data["histogram"]

        # Rate of Change (ROC)
        df_momentum["ROC"] = df_momentum["Close"].pct_change(periods=12) * 100

        # Stochastic Oscillator
        stoch_data = self._calculate_stochastic(
            df_momentum["High"], df_momentum["Low"], df_momentum["Close"]
        )
        df_momentum["Stoch_K"] = stoch_data["K"]
        df_momentum["Stoch_D"] = stoch_data["D"]

        logger.debug("Added momentum indicators")
        return df_momentum

    def add_volatility_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add volatility indicators (ATR, Bollinger Bands).

        Args:
            df: DataFrame with OHLCV data

        Returns:
            DataFrame with volatility indicators
        """
        df_vol = df.copy()

        # Average True Range (ATR)
        df_vol["ATR"] = self._calculate_atr(
            df_vol["High"], df_vol["Low"], df_vol["Close"], period=14
        )

        # Bollinger Bands
        bb_data = self._calculate_bollinger_bands(df_vol["Close"], period=20, std=2)
        df_vol["BB_upper"] = bb_data["upper"]
        df_vol["BB_middle"] = bb_data["middle"]
        df_vol["BB_lower"] = bb_data["lower"]

        # Historical Volatility (rolling std of returns)
        returns = df_vol["Close"].pct_change()
        df_vol["HV_20"] = returns.rolling(window=20).std() * np.sqrt(252)  # Annualized

        logger.debug("Added volatility indicators")
        return df_vol

    def add_volume_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add volume indicators (OBV, Volume MA).

        Args:
            df: DataFrame with OHLCV data

        Returns:
            DataFrame with volume indicators
        """
        df_vol = df.copy()

        # On-Balance Volume (OBV)
        df_vol["OBV"] = self._calculate_obv(df_vol["Close"], df_vol["Volume"])

        # Volume Moving Average
        df_vol["Volume_SMA_20"] = df_vol["Volume"].rolling(window=20).mean()

        # Volume Ratio
        df_vol["Volume_Ratio"] = df_vol["Volume"] / df_vol["Volume_SMA_20"]

        logger.debug("Added volume indicators")
        return df_vol

    def add_returns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add return calculations.

        Args:
            df: DataFrame with price data

        Returns:
            DataFrame with returns
        """
        df_ret = df.copy()

        # Simple returns
        df_ret["Returns"] = df_ret["Close"].pct_change()

        # Log returns
        df_ret["Log_Returns"] = np.log(df_ret["Close"] / df_ret["Close"].shift(1))

        # Cumulative returns
        df_ret["Cum_Returns"] = (1 + df_ret["Returns"]).cumprod() - 1

        logger.debug("Added return calculations")
        return df_ret

    def add_trend_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add trend indicators (ADX).

        Args:
            df: DataFrame with OHLCV data

        Returns:
            DataFrame with trend indicators
        """
        df_trend = df.copy()

        # Average Directional Index (ADX)
        adx_data = self._calculate_adx(
            df_trend["High"], df_trend["Low"], df_trend["Close"], period=14
        )
        df_trend["ADX"] = adx_data["adx"]
        df_trend["DI_plus"] = adx_data["di_plus"]
        df_trend["DI_minus"] = adx_data["di_minus"]

        logger.debug("Added trend indicators")
        return df_trend

    def add_price_patterns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add price pattern features.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            DataFrame with pattern features
        """
        df_patterns = df.copy()

        # Higher highs / Lower lows
        df_patterns["HH"] = df_patterns["High"] > df_patterns["High"].shift(1)
        df_patterns["LL"] = df_patterns["Low"] < df_patterns["Low"].shift(1)

        # Gap detection
        df_patterns["Gap_Up"] = df_patterns["Open"] > df_patterns["Close"].shift(1)
        df_patterns["Gap_Down"] = df_patterns["Open"] < df_patterns["Close"].shift(1)

        # Candle body and wick sizes
        df_patterns["Body"] = abs(df_patterns["Close"] - df_patterns["Open"])
        df_patterns["Upper_Wick"] = df_patterns["High"] - df_patterns[["Open", "Close"]].max(axis=1)
        df_patterns["Lower_Wick"] = df_patterns[["Open", "Close"]].min(axis=1) - df_patterns["Low"]

        # Bullish/Bearish candle
        df_patterns["Bullish"] = df_patterns["Close"] > df_patterns["Open"]

        logger.debug("Added price pattern features")
        return df_patterns

    # Helper methods for indicator calculations

    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index."""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def _calculate_macd(
        self, prices: pd.Series, fast=12, slow=26, signal=9
    ) -> dict:
        """Calculate MACD indicator."""
        ema_fast = prices.ewm(span=fast, adjust=False).mean()
        ema_slow = prices.ewm(span=slow, adjust=False).mean()
        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        histogram = macd - signal_line
        return {"macd": macd, "signal": signal_line, "histogram": histogram}

    def _calculate_atr(
        self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14
    ) -> pd.Series:
        """Calculate Average True Range."""
        high_low = high - low
        high_close = np.abs(high - close.shift())
        low_close = np.abs(low - close.shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        atr = true_range.rolling(window=period).mean()
        return atr

    def _calculate_bollinger_bands(
        self, prices: pd.Series, period: int = 20, std: float = 2
    ) -> dict:
        """Calculate Bollinger Bands."""
        middle = prices.rolling(window=period).mean()
        std_dev = prices.rolling(window=period).std()
        upper = middle + (std_dev * std)
        lower = middle - (std_dev * std)
        return {"upper": upper, "middle": middle, "lower": lower}

    def _calculate_obv(self, close: pd.Series, volume: pd.Series) -> pd.Series:
        """Calculate On-Balance Volume."""
        obv = (np.sign(close.diff()) * volume).fillna(0).cumsum()
        return obv

    def _calculate_stochastic(
        self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14
    ) -> dict:
        """Calculate Stochastic Oscillator."""
        lowest_low = low.rolling(window=period).min()
        highest_high = high.rolling(window=period).max()
        k = 100 * (close - lowest_low) / (highest_high - lowest_low)
        d = k.rolling(window=3).mean()
        return {"K": k, "D": d}

    def _calculate_adx(
        self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14
    ) -> dict:
        """Calculate Average Directional Index."""
        # Calculate +DM and -DM
        high_diff = high.diff()
        low_diff = -low.diff()
        
        plus_dm = high_diff.where((high_diff > low_diff) & (high_diff > 0), 0)
        minus_dm = low_diff.where((low_diff > high_diff) & (low_diff > 0), 0)
        
        # Calculate ATR
        atr = self._calculate_atr(high, low, close, period)
        
        # Calculate +DI and -DI
        plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)
        
        # Calculate DX and ADX
        dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=period).mean()
        
        return {"adx": adx, "di_plus": plus_di, "di_minus": minus_di}

    def create_lag_features(
        self,
        df: pd.DataFrame,
        columns: List[str],
        lags: List[int],
    ) -> pd.DataFrame:
        """
        Create lagged features.

        Args:
            df: DataFrame
            columns: Columns to create lags for
            lags: List of lag periods

        Returns:
            DataFrame with lag features
        """
        df_lagged = df.copy()

        for col in columns:
            if col not in df.columns:
                continue

            for lag in lags:
                df_lagged[f"{col}_lag_{lag}"] = df_lagged[col].shift(lag)

        logger.debug(f"Created lag features for {len(columns)} columns with lags {lags}")
        return df_lagged

    def create_rolling_features(
        self,
        df: pd.DataFrame,
        column: str,
        windows: List[int],
        functions: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """
        Create rolling window features.

        Args:
            df: DataFrame
            column: Column to create rolling features for
            windows: List of window sizes
            functions: List of functions (mean, std, min, max)

        Returns:
            DataFrame with rolling features
        """
        if functions is None:
            functions = ["mean", "std", "min", "max"]

        df_rolling = df.copy()

        for window in windows:
            for func in functions:
                feature_name = f"{column}_rolling_{func}_{window}"
                if func == "mean":
                    df_rolling[feature_name] = df_rolling[column].rolling(window).mean()
                elif func == "std":
                    df_rolling[feature_name] = df_rolling[column].rolling(window).std()
                elif func == "min":
                    df_rolling[feature_name] = df_rolling[column].rolling(window).min()
                elif func == "max":
                    df_rolling[feature_name] = df_rolling[column].rolling(window).max()

        logger.debug(f"Created rolling features for {column}")
        return df_rolling

    def get_feature_importance(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate basic feature importance metrics.

        Args:
            df: DataFrame with features

        Returns:
            DataFrame with feature statistics
        """
        numeric_cols = df.select_dtypes(include=[np.number]).columns

        stats = []
        for col in numeric_cols:
            stats.append(
                {
                    "feature": col,
                    "missing_pct": df[col].isna().sum() / len(df) * 100,
                    "unique_values": df[col].nunique(),
                    "mean": df[col].mean(),
                    "std": df[col].std(),
                    "min": df[col].min(),
                    "max": df[col].max(),
                }
            )

        return pd.DataFrame(stats).sort_values("std", ascending=False)
