"""
Custom exception classes for FinanceMoraiAgent.
"""


class FinanceMoraiAgentException(Exception):
    """Base exception for all FinanceMoraiAgent errors."""
    pass


class DataSourceException(FinanceMoraiAgentException):
    """Raised when data source operations fail."""
    pass


class CacheException(FinanceMoraiAgentException):
    """Raised when cache operations fail."""
    pass


class ModelException(FinanceMoraiAgentException):
    """Raised when model operations fail."""
    pass


class ValidationException(FinanceMoraiAgentException):
    """Raised when input validation fails."""
    pass


class ConfigurationException(FinanceMoraiAgentException):
    """Raised when configuration is invalid."""
    pass


class PreprocessingException(FinanceMoraiAgentException):
    """Raised when data preprocessing fails."""
    pass


class SentimentAnalysisException(FinanceMoraiAgentException):
    """Raised when sentiment analysis fails."""
    pass


class RegimeDetectionException(FinanceMoraiAgentException):
    """Raised when regime detection fails."""
    pass


class BacktestingException(FinanceMoraiAgentException):
    """Raised when backtesting operations fail."""
    pass
