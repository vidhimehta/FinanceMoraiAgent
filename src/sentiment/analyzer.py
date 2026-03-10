"""
Main sentiment analyzer orchestrator.
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from loguru import logger
import numpy as np

from ..data.sources.news_collector import NewsCollector
from ..data.sources.sec_edgar import SECEdgarCollector
from ..data.sources.sebi_client import SEBICollector
from .models.lexicon import VADERAnalyzer
from ..utils.helpers import exponential_decay


class SentimentAnalyzer:
    """
    Orchestrates sentiment analysis from multiple sources.
    """

    def __init__(
        self,
        use_finbert: bool = False,  # Disabled by default (requires download)
        use_cache: bool = True,
    ):
        """
        Initialize sentiment analyzer.

        Args:
            use_finbert: Whether to use FinBERT (requires model download)
            use_cache: Whether to use caching
        """
        self.use_finbert = use_finbert
        
        # Initialize data collectors
        self.news_collector = NewsCollector(use_cache=use_cache)
        self.sec_collector = SECEdgarCollector(use_cache=use_cache)
        self.sebi_collector = SEBICollector(use_cache=use_cache)
        
        # Initialize sentiment models
        self.vader = VADERAnalyzer()
        self.finbert = None
        
        if use_finbert:
            try:
                from .models.finbert import FinBERTAnalyzer
                self.finbert = FinBERTAnalyzer()
                logger.info("FinBERT enabled for sentiment analysis")
            except Exception as e:
                logger.warning(f"FinBERT not available: {e}, using VADER only")
        
        logger.info("SentimentAnalyzer initialized")

    def analyze_stock_sentiment(
        self,
        ticker: str,
        company_name: Optional[str] = None,
        days_back: int = 7,
        include_news: bool = True,
        include_filings: bool = True,
    ) -> Dict:
        """
        Analyze overall sentiment for a stock.

        Args:
            ticker: Stock ticker symbol
            company_name: Company name (optional)
            days_back: Days of history to analyze
            include_news: Include news sentiment
            include_filings: Include SEC/SEBI filings

        Returns:
            Comprehensive sentiment analysis result
        """
        logger.info(f"Analyzing sentiment for {ticker}")

        results = {
            "ticker": ticker,
            "analyzed_at": datetime.now().isoformat(),
            "days_analyzed": days_back,
            "sources": {},
            "overall": {},
        }

        # Collect and analyze news
        if include_news:
            news_sentiment = self._analyze_news_sentiment(ticker, company_name, days_back)
            results["sources"]["news"] = news_sentiment

        # Collect and analyze filings
        if include_filings:
            if ticker.endswith((".NS", ".BO")):
                # Indian stock - use SEBI
                filing_sentiment = self._analyze_sebi_sentiment(ticker, days_back)
                results["sources"]["sebi"] = filing_sentiment
            else:
                # US stock - use SEC
                filing_sentiment = self._analyze_sec_sentiment(ticker, days_back)
                results["sources"]["sec"] = filing_sentiment

        # Calculate overall sentiment
        overall = self._calculate_overall_sentiment(results["sources"])
        results["overall"] = overall

        logger.info(f"Sentiment analysis complete for {ticker}: {overall['label']} ({overall['score']:.2f})")
        return results

    def _analyze_news_sentiment(
        self,
        ticker: str,
        company_name: Optional[str],
        days_back: int,
    ) -> Dict:
        """Analyze news sentiment."""
        try:
            articles = self.news_collector.collect_news(
                ticker, company_name, days_back, max_articles=30
            )

            if not articles:
                return {
                    "article_count": 0,
                    "sentiment": {"compound": 0.0, "label": "neutral"},
                    "confidence": 0.0,
                }

            # Analyze sentiment of each article
            sentiments = []
            weights = []
            
            for article in articles:
                # Combine title and description
                text = f"{article['title']}. {article.get('description', '')}"
                
                # Analyze with available model
                if self.finbert and self.finbert.is_loaded():
                    sentiment = self.finbert.analyze_sentiment(text)
                else:
                    sentiment = self.vader.analyze_sentiment(text)
                
                sentiments.append(sentiment)
                
                # Weight by recency
                try:
                    pub_date = datetime.fromisoformat(article['published_at'].replace('Z', '+00:00'))
                    days_ago = (datetime.now() - pub_date.replace(tzinfo=None)).days
                    weight = exponential_decay(days_ago, half_life=3)
                except:
                    weight = 1.0
                
                weights.append(weight)

            # Aggregate sentiments
            avg_sentiment = self._aggregate_sentiments(sentiments, weights)

            return {
                "article_count": len(articles),
                "sentiment": avg_sentiment,
                "confidence": min(len(articles) / 20.0, 1.0),  # More articles = more confidence
            }

        except Exception as e:
            logger.error(f"News sentiment analysis failed: {e}")
            return {
                "article_count": 0,
                "sentiment": {"compound": 0.0, "label": "neutral"},
                "confidence": 0.0,
                "error": str(e),
            }

    def _analyze_sec_sentiment(self, ticker: str, days_back: int) -> Dict:
        """Analyze SEC filing sentiment."""
        try:
            filings = self.sec_collector.collect_filings(
                ticker, filing_types=["8-K"], days_back=days_back, max_filings=5
            )

            if not filings:
                return {
                    "filing_count": 0,
                    "sentiment": {"compound": 0.0, "label": "neutral"},
                    "confidence": 0.0,
                }

            # For now, return neutral sentiment
            # Full implementation would analyze filing text
            return {
                "filing_count": len(filings),
                "sentiment": {"compound": 0.0, "label": "neutral"},
                "confidence": 0.3,
                "note": "Filing text analysis not fully implemented",
            }

        except Exception as e:
            logger.warning(f"SEC sentiment analysis failed: {e}")
            return {
                "filing_count": 0,
                "sentiment": {"compound": 0.0, "label": "neutral"},
                "confidence": 0.0,
            }

    def _analyze_sebi_sentiment(self, ticker: str, days_back: int) -> Dict:
        """Analyze SEBI announcement sentiment."""
        try:
            announcements = self.sebi_collector.collect_announcements(
                ticker, days_back=days_back, max_announcements=10
            )

            if not announcements:
                return {
                    "announcement_count": 0,
                    "sentiment": {"compound": 0.0, "label": "neutral"},
                    "confidence": 0.0,
                }

            # For now, return neutral sentiment
            return {
                "announcement_count": len(announcements),
                "sentiment": {"compound": 0.0, "label": "neutral"},
                "confidence": 0.3,
                "note": "SEBI announcement analysis not fully implemented",
            }

        except Exception as e:
            logger.warning(f"SEBI sentiment analysis failed: {e}")
            return {
                "announcement_count": 0,
                "sentiment": {"compound": 0.0, "label": "neutral"},
                "confidence": 0.0,
            }

    def _aggregate_sentiments(
        self,
        sentiments: List[Dict],
        weights: Optional[List[float]] = None,
    ) -> Dict:
        """Aggregate multiple sentiment scores."""
        if not sentiments:
            return {"compound": 0.0, "label": "neutral"}

        if weights is None:
            weights = [1.0] * len(sentiments)

        # Normalize weights
        total_weight = sum(weights)
        weights = [w / total_weight for w in weights]

        # Calculate weighted average
        compounds = [s["compound"] for s in sentiments]
        avg_compound = sum(c * w for c, w in zip(compounds, weights))

        # Determine label
        if avg_compound >= 0.05:
            label = "positive"
        elif avg_compound <= -0.05:
            label = "negative"
        else:
            label = "neutral"

        return {
            "compound": avg_compound,
            "label": label,
            "positive": np.mean([s.get("positive", 0) for s in sentiments]),
            "negative": np.mean([s.get("negative", 0) for s in sentiments]),
            "neutral": np.mean([s.get("neutral", 1) for s in sentiments]),
        }

    def _calculate_overall_sentiment(self, sources: Dict) -> Dict:
        """Calculate overall sentiment from all sources."""
        # Weights for different sources
        source_weights = {
            "news": 0.6,
            "sec": 0.2,
            "sebi": 0.2,
        }

        sentiments = []
        weights = []

        for source_name, source_data in sources.items():
            if source_data and "sentiment" in source_data:
                sentiment = source_data["sentiment"]
                confidence = source_data.get("confidence", 0.5)
                
                # Weight by source importance and confidence
                weight = source_weights.get(source_name, 0.5) * confidence
                
                sentiments.append(sentiment)
                weights.append(weight)

        if not sentiments:
            return {
                "score": 0.0,
                "label": "neutral",
                "confidence": 0.0,
            }

        # Aggregate
        aggregated = self._aggregate_sentiments(sentiments, weights)

        return {
            "score": aggregated["compound"],
            "label": aggregated["label"],
            "confidence": min(sum(weights), 1.0),
            "details": aggregated,
        }
