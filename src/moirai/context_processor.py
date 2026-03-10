"""
Context processor for preparing natural language context for forecasting.
"""

from typing import Optional, Dict, Any
from loguru import logger


class ContextProcessor:
    """
    Processes and formats context information for time-series models.
    """

    def __init__(self, max_length: int = 256):
        """
        Initialize context processor.

        Args:
            max_length: Maximum context length in characters
        """
        self.max_length = max_length
        logger.info(f"ContextProcessor initialized with max_length={max_length}")

    def prepare_context(
        self,
        ticker: str,
        historical_data: Any,
        sentiment: Optional[Dict] = None,
        regime: Optional[Dict] = None,
        technical_signals: Optional[Dict] = None,
    ) -> str:
        """
        Prepare natural language context from various signals.

        Args:
            ticker: Stock ticker symbol
            historical_data: Historical price data
            sentiment: Sentiment analysis results
            regime: Market regime information
            technical_signals: Technical indicator signals

        Returns:
            Formatted context string
        """
        context_parts = []

        # Add ticker information
        context_parts.append(f"Stock: {ticker}")

        # Add technical signals if available
        if technical_signals:
            tech_context = self._format_technical_signals(technical_signals)
            if tech_context:
                context_parts.append(tech_context)

        # Add sentiment if available
        if sentiment:
            sentiment_context = self._format_sentiment(sentiment)
            if sentiment_context:
                context_parts.append(sentiment_context)

        # Add regime if available
        if regime:
            regime_context = self._format_regime(regime)
            if regime_context:
                context_parts.append(regime_context)

        # Combine and truncate if needed
        context = ". ".join(context_parts)
        
        if len(context) > self.max_length:
            context = context[:self.max_length - 3] + "..."

        logger.debug(f"Prepared context: {context[:100]}...")
        return context

    def _format_technical_signals(self, signals: Dict) -> str:
        """Format technical indicator signals."""
        parts = []

        if "rsi" in signals:
            rsi = signals["rsi"]
            if rsi > 70:
                parts.append("RSI indicates overbought conditions")
            elif rsi < 30:
                parts.append("RSI indicates oversold conditions")

        if "macd_signal" in signals:
            signal = signals["macd_signal"]
            if signal == "bullish":
                parts.append("MACD shows bullish momentum")
            elif signal == "bearish":
                parts.append("MACD shows bearish momentum")

        if "trend" in signals:
            parts.append(f"{signals['trend']} trend detected")

        return ". ".join(parts) if parts else ""

    def _format_sentiment(self, sentiment: Dict) -> str:
        """Format sentiment information."""
        if "score" in sentiment:
            score = sentiment["score"]
            if score > 0.5:
                return f"Positive market sentiment (score: {score:.2f})"
            elif score < -0.5:
                return f"Negative market sentiment (score: {score:.2f})"
            else:
                return "Neutral market sentiment"
        return ""

    def _format_regime(self, regime: Dict) -> str:
        """Format market regime information."""
        if "state" in regime:
            state = regime["state"]
            return f"Market regime: {state}"
        return ""

    def validate_context(self, context: str) -> bool:
        """
        Validate context string.

        Args:
            context: Context string to validate

        Returns:
            True if valid
        """
        if not isinstance(context, str):
            return False

        if len(context) == 0:
            return False

        if len(context) > self.max_length:
            logger.warning(f"Context exceeds max length: {len(context)} > {self.max_length}")
            return False

        return True
