"""
Data preprocessing and cleaning utilities.
"""

import pandas as pd
import numpy as np
from loguru import logger
from typing import Optional

from ..utils.exceptions import PreprocessingException
from ..utils.validators import validate_dataframe


class DataPreprocessor:
    """
    Preprocessor for cleaning and normalizing financial data.
    """

    def __init__(self, fill_method: str = "ffill"):
        """
        Initialize preprocessor.

        Args:
            fill_method: Method for filling missing values (ffill, bfill, interpolate)
        """
        self.fill_method = fill_method
        logger.info(f"DataPreprocessor initialized with fill_method={fill_method}")

    def clean_ohlcv(
        self,
        df: pd.DataFrame,
        remove_outliers: bool = True,
        outlier_std: float = 4.0,
    ) -> pd.DataFrame:
        """
        Clean OHLCV data.

        Args:
            df: DataFrame with OHLCV data
            remove_outliers: Whether to remove outliers
            outlier_std: Number of standard deviations for outlier detection

        Returns:
            Cleaned DataFrame

        Raises:
            PreprocessingException: If cleaning fails
        """
        try:
            validate_dataframe(df, required_columns=["Open", "High", "Low", "Close", "Volume"])

            df_clean = df.copy()

            # Handle missing values
            df_clean = self.handle_missing_values(df_clean)

            # Remove duplicates
            df_clean = df_clean[~df_clean.index.duplicated(keep="first")]

            # Ensure high >= low
            df_clean.loc[df_clean["High"] < df_clean["Low"], "High"] = df_clean["Low"]

            # Remove rows with zero or negative prices
            for col in ["Open", "High", "Low", "Close"]:
                df_clean = df_clean[df_clean[col] > 0]

            # Remove outliers if requested
            if remove_outliers:
                df_clean = self.remove_outliers(df_clean, std_threshold=outlier_std)

            # Sort by date
            df_clean = df_clean.sort_index()

            logger.info(
                f"Cleaned OHLCV data: {len(df)} → {len(df_clean)} rows "
                f"({len(df) - len(df_clean)} removed)"
            )

            return df_clean

        except Exception as e:
            raise PreprocessingException(f"Failed to clean OHLCV data: {e}")

    def handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Handle missing values in DataFrame.

        Args:
            df: DataFrame with potential missing values

        Returns:
            DataFrame with filled missing values
        """
        if df.isna().sum().sum() == 0:
            return df

        df_filled = df.copy()

        if self.fill_method == "ffill":
            # Forward fill
            df_filled = df_filled.fillna(method="ffill")
        elif self.fill_method == "bfill":
            # Backward fill
            df_filled = df_filled.fillna(method="bfill")
        elif self.fill_method == "interpolate":
            # Linear interpolation
            df_filled = df_filled.interpolate(method="linear", limit_direction="both")
        else:
            # Default to forward fill
            df_filled = df_filled.fillna(method="ffill")

        # Drop any remaining NaN rows
        df_filled = df_filled.dropna()

        missing_before = df.isna().sum().sum()
        missing_after = df_filled.isna().sum().sum()

        if missing_before > 0:
            logger.debug(
                f"Filled missing values: {missing_before} → {missing_after}"
            )

        return df_filled

    def remove_outliers(
        self,
        df: pd.DataFrame,
        columns: Optional[list[str]] = None,
        std_threshold: float = 4.0,
    ) -> pd.DataFrame:
        """
        Remove outliers using standard deviation method.

        Args:
            df: DataFrame
            columns: Columns to check for outliers (default: Close, Volume)
            std_threshold: Number of standard deviations for outlier threshold

        Returns:
            DataFrame with outliers removed
        """
        if columns is None:
            columns = ["Close", "Volume"]

        df_clean = df.copy()
        initial_rows = len(df_clean)

        for col in columns:
            if col not in df_clean.columns:
                continue

            # Calculate z-scores
            mean = df_clean[col].mean()
            std = df_clean[col].std()

            if std == 0:
                continue

            z_scores = np.abs((df_clean[col] - mean) / std)

            # Remove outliers
            df_clean = df_clean[z_scores < std_threshold]

        removed_rows = initial_rows - len(df_clean)
        if removed_rows > 0:
            logger.debug(f"Removed {removed_rows} outlier rows")

        return df_clean

    def normalize_prices(
        self,
        df: pd.DataFrame,
        method: str = "minmax",
        columns: Optional[list[str]] = None,
    ) -> pd.DataFrame:
        """
        Normalize price data.

        Args:
            df: DataFrame with price data
            method: Normalization method (minmax, zscore, percent)
            columns: Columns to normalize (default: OHLC)

        Returns:
            DataFrame with normalized prices
        """
        if columns is None:
            columns = ["Open", "High", "Low", "Close"]

        df_norm = df.copy()

        for col in columns:
            if col not in df_norm.columns:
                continue

            if method == "minmax":
                # Min-max normalization [0, 1]
                min_val = df_norm[col].min()
                max_val = df_norm[col].max()
                if max_val > min_val:
                    df_norm[f"{col}_norm"] = (df_norm[col] - min_val) / (max_val - min_val)
                else:
                    df_norm[f"{col}_norm"] = 0.5

            elif method == "zscore":
                # Z-score normalization
                mean = df_norm[col].mean()
                std = df_norm[col].std()
                if std > 0:
                    df_norm[f"{col}_norm"] = (df_norm[col] - mean) / std
                else:
                    df_norm[f"{col}_norm"] = 0.0

            elif method == "percent":
                # Percentage change from first value
                first_val = df_norm[col].iloc[0]
                if first_val > 0:
                    df_norm[f"{col}_norm"] = (df_norm[col] / first_val - 1) * 100
                else:
                    df_norm[f"{col}_norm"] = 0.0

        logger.debug(f"Normalized prices using method={method}")
        return df_norm

    def adjust_for_splits(
        self,
        df: pd.DataFrame,
        splits: pd.Series,
    ) -> pd.DataFrame:
        """
        Adjust prices for stock splits.

        Args:
            df: DataFrame with OHLCV data
            splits: Series with split ratios

        Returns:
            Split-adjusted DataFrame
        """
        if splits.empty:
            return df

        df_adjusted = df.copy()

        # Sort splits by date (oldest first)
        splits = splits.sort_index()

        # Apply split adjustments
        for split_date, split_ratio in splits.items():
            # Adjust all prices before split date
            mask = df_adjusted.index < split_date
            for col in ["Open", "High", "Low", "Close"]:
                df_adjusted.loc[mask, col] = df_adjusted.loc[mask, col] / split_ratio

            # Adjust volume
            df_adjusted.loc[mask, "Volume"] = df_adjusted.loc[mask, "Volume"] * split_ratio

        logger.info(f"Adjusted for {len(splits)} stock splits")
        return df_adjusted

    def resample(
        self,
        df: pd.DataFrame,
        freq: str = "1W",
        agg_method: Optional[dict] = None,
    ) -> pd.DataFrame:
        """
        Resample data to different frequency.

        Args:
            df: DataFrame with time-series data
            freq: Frequency string (e.g., '1D', '1W', '1M')
            agg_method: Aggregation methods for each column

        Returns:
            Resampled DataFrame
        """
        if agg_method is None:
            agg_method = {
                "Open": "first",
                "High": "max",
                "Low": "min",
                "Close": "last",
                "Volume": "sum",
            }

        # Filter agg_method to only include existing columns
        agg_method = {k: v for k, v in agg_method.items() if k in df.columns}

        df_resampled = df.resample(freq).agg(agg_method)
        df_resampled = df_resampled.dropna()

        logger.info(f"Resampled data to {freq}: {len(df)} → {len(df_resampled)} rows")
        return df_resampled

    def validate_data_quality(self, df: pd.DataFrame) -> dict:
        """
        Validate data quality and return metrics.

        Args:
            df: DataFrame to validate

        Returns:
            Dictionary with quality metrics
        """
        metrics = {
            "total_rows": len(df),
            "missing_values": df.isna().sum().to_dict(),
            "duplicate_rows": df.duplicated().sum(),
            "date_range": {
                "start": df.index.min(),
                "end": df.index.max(),
                "days": (df.index.max() - df.index.min()).days,
            },
        }

        # Check for price anomalies
        if "Close" in df.columns:
            metrics["price_stats"] = {
                "min": float(df["Close"].min()),
                "max": float(df["Close"].max()),
                "mean": float(df["Close"].mean()),
                "std": float(df["Close"].std()),
            }

            # Check for extreme price changes
            returns = df["Close"].pct_change()
            metrics["extreme_returns"] = {
                "max_gain": float(returns.max()),
                "max_loss": float(returns.min()),
                "std": float(returns.std()),
            }

        logger.debug(f"Data quality metrics: {metrics['total_rows']} rows, "
                    f"{sum(metrics['missing_values'].values())} missing values")

        return metrics
