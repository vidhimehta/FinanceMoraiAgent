"""
3-tier caching system: Memory → Disk → Parquet files
"""

import os
from pathlib import Path
from typing import Any, Optional, Callable
import pickle
from datetime import datetime, timedelta
import pandas as pd
from diskcache import Cache
from loguru import logger
from functools import wraps

from ..utils.exceptions import CacheException
from ..utils.helpers import ensure_directory, generate_cache_key


class CacheManager:
    """
    Manages 3-tier caching: Memory → Disk → Parquet
    """

    def __init__(
        self,
        cache_dir: str = "storage/cache",
        parquet_dir: str = "storage/historical",
        memory_size_mb: int = 512,
        disk_size_gb: int = 10,
    ):
        """
        Initialize cache manager.

        Args:
            cache_dir: Directory for disk cache
            parquet_dir: Directory for parquet files
            memory_size_mb: Maximum memory cache size in MB
            disk_size_gb: Maximum disk cache size in GB
        """
        self.cache_dir = ensure_directory(cache_dir)
        self.parquet_dir = ensure_directory(parquet_dir)

        # Memory cache (simple dict)
        self._memory_cache: dict[str, tuple[Any, datetime]] = {}
        self.memory_size_mb = memory_size_mb

        # Disk cache (using diskcache)
        self._disk_cache = Cache(
            str(self.cache_dir),
            size_limit=disk_size_gb * 1024**3,  # Convert GB to bytes
        )

        logger.info(
            f"Cache manager initialized: "
            f"memory={memory_size_mb}MB, disk={disk_size_gb}GB"
        )

    def get(
        self,
        key: str,
        ttl: Optional[int] = None,
        default: Any = None,
    ) -> Optional[Any]:
        """
        Get value from cache (memory → disk → None).

        Args:
            key: Cache key
            ttl: Time-to-live in seconds (None = no expiration check)
            default: Default value if not found

        Returns:
            Cached value or default
        """
        # Check memory cache
        if key in self._memory_cache:
            value, timestamp = self._memory_cache[key]
            if ttl is None or (datetime.now() - timestamp).seconds < ttl:
                logger.debug(f"Cache hit (memory): {key}")
                return value
            else:
                # Expired
                del self._memory_cache[key]
                logger.debug(f"Cache expired (memory): {key}")

        # Check disk cache
        try:
            cached_item = self._disk_cache.get(key)
            if cached_item is not None:
                value, timestamp = cached_item
                if ttl is None or (datetime.now() - timestamp).seconds < ttl:
                    # Promote to memory cache
                    self._memory_cache[key] = (value, timestamp)
                    logger.debug(f"Cache hit (disk): {key}")
                    return value
                else:
                    # Expired
                    del self._disk_cache[key]
                    logger.debug(f"Cache expired (disk): {key}")
        except Exception as e:
            logger.warning(f"Error reading from disk cache: {e}")

        logger.debug(f"Cache miss: {key}")
        return default

    def set(
        self,
        key: str,
        value: Any,
        expire: Optional[int] = None,
    ) -> None:
        """
        Set value in cache (memory + disk).

        Args:
            key: Cache key
            value: Value to cache
            expire: Expiration time in seconds (for disk cache)
        """
        timestamp = datetime.now()

        # Store in memory cache
        self._memory_cache[key] = (value, timestamp)

        # Store in disk cache
        try:
            self._disk_cache.set(key, (value, timestamp), expire=expire)
            logger.debug(f"Cached: {key}")
        except Exception as e:
            logger.warning(f"Error writing to disk cache: {e}")

    def delete(self, key: str) -> None:
        """
        Delete key from all cache tiers.

        Args:
            key: Cache key
        """
        if key in self._memory_cache:
            del self._memory_cache[key]

        try:
            del self._disk_cache[key]
        except KeyError:
            pass

        logger.debug(f"Deleted from cache: {key}")

    def clear(self) -> None:
        """Clear all caches."""
        self._memory_cache.clear()
        self._disk_cache.clear()
        logger.info("All caches cleared")

    def save_parquet(
        self,
        df: pd.DataFrame,
        ticker: str,
        data_type: str = "ohlcv",
    ) -> Path:
        """
        Save DataFrame to parquet file.

        Args:
            df: DataFrame to save
            ticker: Stock ticker
            data_type: Type of data (ohlcv, sentiment, etc.)

        Returns:
            Path to saved file
        """
        filename = f"{ticker}_{data_type}.parquet"
        filepath = self.parquet_dir / filename

        try:
            df.to_parquet(filepath, compression="snappy", index=True)
            logger.debug(f"Saved parquet: {filepath}")
            return filepath
        except Exception as e:
            raise CacheException(f"Failed to save parquet file: {e}")

    def load_parquet(
        self,
        ticker: str,
        data_type: str = "ohlcv",
    ) -> Optional[pd.DataFrame]:
        """
        Load DataFrame from parquet file.

        Args:
            ticker: Stock ticker
            data_type: Type of data

        Returns:
            DataFrame or None if not found
        """
        filename = f"{ticker}_{data_type}.parquet"
        filepath = self.parquet_dir / filename

        if not filepath.exists():
            logger.debug(f"Parquet file not found: {filepath}")
            return None

        try:
            df = pd.read_parquet(filepath)
            logger.debug(f"Loaded parquet: {filepath}")
            return df
        except Exception as e:
            logger.warning(f"Error loading parquet file: {e}")
            return None

    def get_cache_stats(self) -> dict:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache stats
        """
        return {
            "memory_items": len(self._memory_cache),
            "disk_items": len(self._disk_cache),
            "disk_size_mb": self._disk_cache.volume() / (1024**2),
        }


# Decorator for automatic caching
def cached(
    ttl: Optional[int] = 3600,
    cache_manager: Optional[CacheManager] = None,
    key_prefix: str = "",
):
    """
    Decorator to cache function results.

    Args:
        ttl: Time-to-live in seconds
        cache_manager: CacheManager instance (if None, creates new one)
        key_prefix: Prefix for cache keys

    Example:
        @cached(ttl=3600, key_prefix="ticker_data")
        def fetch_data(ticker: str):
            return expensive_operation(ticker)
    """

    def decorator(func: Callable) -> Callable:
        # Use global cache manager if not provided
        _cache = cache_manager or CacheManager()

        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{func.__name__}:{generate_cache_key(*args, **kwargs)}"

            # Try to get from cache
            result = _cache.get(cache_key, ttl=ttl)
            if result is not None:
                return result

            # Execute function and cache result
            result = func(*args, **kwargs)
            _cache.set(cache_key, result, expire=ttl)

            return result

        return wrapper

    return decorator


# Global cache manager instance
_global_cache: Optional[CacheManager] = None


def get_cache_manager() -> CacheManager:
    """
    Get global cache manager instance.

    Returns:
        CacheManager instance
    """
    global _global_cache
    if _global_cache is None:
        _global_cache = CacheManager()
    return _global_cache
