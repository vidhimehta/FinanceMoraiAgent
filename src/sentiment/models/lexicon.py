"""
Lexicon-based sentiment analysis using VADER.
"""

from typing import Dict
from loguru import logger


class VADERAnalyzer:
    """
    VADER sentiment analysis (lexicon-based).
    Fast fallback method when FinBERT is not available.
    """

    def __init__(self):
        """Initialize VADER analyzer."""
        self.analyzer = None
        logger.info("VADER analyzer initialized")

    def load_model(self) -> None:
        """Load VADER sentiment analyzer."""
        try:
            from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
            self.analyzer = SentimentIntensityAnalyzer()
            logger.info("✓ VADER analyzer loaded")
        except ImportError:
            logger.error("vaderSentiment not installed")
            raise

    def analyze_sentiment(self, text: str) -> Dict:
        """
        Analyze sentiment using VADER.

        Args:
            text: Text to analyze

        Returns:
            Dictionary with sentiment scores
        """
        if self.analyzer is None:
            self.load_model()

        try:
            scores = self.analyzer.polarity_scores(text)

            # Normalize to match FinBERT format
            compound = scores["compound"]
            
            # Convert compound score to positive/negative/neutral
            if compound >= 0.05:
                positive = (compound + 1) / 2
                negative = 0.0
                neutral = 1 - positive
                label = "positive"
            elif compound <= -0.05:
                negative = abs((compound - 1) / 2)
                positive = 0.0
                neutral = 1 - negative
                label = "negative"
            else:
                positive = 0.0
                negative = 0.0
                neutral = 1.0
                label = "neutral"

            return {
                "positive": positive,
                "negative": negative,
                "neutral": neutral,
                "compound": compound,
                "label": label,
            }

        except Exception as e:
            logger.error(f"VADER sentiment analysis failed: {e}")
            return {
                "positive": 0.0,
                "negative": 0.0,
                "neutral": 1.0,
                "compound": 0.0,
                "label": "neutral",
                "error": str(e),
            }

    def is_loaded(self) -> bool:
        """Check if analyzer is loaded."""
        return self.analyzer is not None
