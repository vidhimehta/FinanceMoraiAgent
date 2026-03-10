"""
News collection from multiple sources for sentiment analysis.
"""

import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from urllib.parse import quote_plus
from loguru import logger
import feedparser
import os

from ...utils.exceptions import DataSourceException
from ...core.cache_manager import get_cache_manager


class NewsCollector:
    """
    Collects news articles from multiple sources.
    """

    def __init__(self, use_cache: bool = True):
        """
        Initialize news collector.

        Args:
            use_cache: Whether to use caching
        """
        self.use_cache = use_cache
        self.cache_manager = get_cache_manager() if use_cache else None
        
        # Get API key from environment
        self.news_api_key = os.getenv("NEWS_API_KEY")
        
        logger.info("NewsCollector initialized")

    def collect_news(
        self,
        ticker: str,
        company_name: Optional[str] = None,
        days_back: int = 7,
        max_articles: int = 50,
    ) -> List[Dict]:
        """
        Collect news articles about a stock.

        Args:
            ticker: Stock ticker symbol
            company_name: Company name for search
            days_back: How many days of news to fetch
            max_articles: Maximum articles to return

        Returns:
            List of news articles with metadata
        """
        logger.info(f"Collecting news for {ticker} (last {days_back} days)")

        # Check cache
        cache_key = f"news:{ticker}:{days_back}"
        if self.use_cache:
            cached = self.cache_manager.get(cache_key, ttl=1800)  # 30 min cache
            if cached is not None:
                logger.info(f"Using cached news for {ticker}")
                return cached

        articles = []

        # Collect from multiple sources
        try:
            # Source 1: RSS feeds (free, no API key needed)
            rss_articles = self._collect_from_rss(ticker, company_name, days_back)
            articles.extend(rss_articles)

            # Source 2: NewsAPI (if API key available)
            if self.news_api_key:
                api_articles = self._collect_from_newsapi(ticker, company_name, days_back)
                articles.extend(api_articles)
            else:
                logger.info("NewsAPI key not found, using RSS feeds only")

        except Exception as e:
            logger.warning(f"Error collecting news: {e}")

        # Remove duplicates and limit
        articles = self._deduplicate_articles(articles)
        articles = articles[:max_articles]

        # Cache results
        if self.use_cache and articles:
            self.cache_manager.set(cache_key, articles, expire=1800)

        logger.info(f"Collected {len(articles)} news articles for {ticker}")
        return articles

    def _collect_from_rss(
        self,
        ticker: str,
        company_name: Optional[str],
        days_back: int,
    ) -> List[Dict]:
        """Collect from RSS feeds."""
        articles = []
        
        search_term = company_name or ticker
        cutoff_date = datetime.now() - timedelta(days=days_back)

        # Google News RSS
        try:
            # URL encode the search term to handle spaces and special characters
            encoded_search = quote_plus(f"{search_term} stock")
            url = f"https://news.google.com/rss/search?q={encoded_search}&hl=en-US&gl=US&ceid=US:en"
            feed = feedparser.parse(url)

            for entry in feed.entries[:20]:  # Limit to 20 per source
                try:
                    pub_date = datetime(*entry.published_parsed[:6])
                    if pub_date >= cutoff_date:
                        articles.append({
                            "title": entry.title,
                            "description": entry.get("summary", ""),
                            "url": entry.link,
                            "published_at": pub_date.isoformat(),
                            "source": "Google News",
                        })
                except:
                    continue

        except Exception as e:
            logger.warning(f"Google News RSS failed: {e}")

        # Yahoo Finance RSS
        try:
            url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US"
            feed = feedparser.parse(url)

            for entry in feed.entries[:20]:
                try:
                    pub_date = datetime(*entry.published_parsed[:6])
                    if pub_date >= cutoff_date:
                        articles.append({
                            "title": entry.title,
                            "description": entry.get("summary", ""),
                            "url": entry.link,
                            "published_at": pub_date.isoformat(),
                            "source": "Yahoo Finance",
                        })
                except:
                    continue

        except Exception as e:
            logger.warning(f"Yahoo Finance RSS failed: {e}")

        return articles

    def _collect_from_newsapi(
        self,
        ticker: str,
        company_name: Optional[str],
        days_back: int,
    ) -> List[Dict]:
        """Collect from NewsAPI."""
        articles = []

        try:
            search_query = f"{company_name or ticker} stock"
            from_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")

            url = "https://newsapi.org/v2/everything"
            params = {
                "q": search_query,
                "from": from_date,
                "sortBy": "publishedAt",
                "language": "en",
                "apiKey": self.news_api_key,
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            for article in data.get("articles", [])[:30]:
                articles.append({
                    "title": article.get("title", ""),
                    "description": article.get("description", ""),
                    "url": article.get("url", ""),
                    "published_at": article.get("publishedAt", ""),
                    "source": article.get("source", {}).get("name", "NewsAPI"),
                })

        except Exception as e:
            logger.warning(f"NewsAPI collection failed: {e}")

        return articles

    def _deduplicate_articles(self, articles: List[Dict]) -> List[Dict]:
        """Remove duplicate articles based on title similarity."""
        seen_titles = set()
        unique_articles = []

        for article in articles:
            title_lower = article["title"].lower()
            # Simple deduplication by exact title match
            if title_lower not in seen_titles:
                seen_titles.add(title_lower)
                unique_articles.append(article)

        return unique_articles

    def get_article_text(self, url: str) -> str:
        """
        Fetch full article text from URL.

        Args:
            url: Article URL

        Returns:
            Article text
        """
        # This is a placeholder - full implementation would use
        # a library like newspaper3k or beautifulsoup
        # For now, we'll just use title + description
        return ""
