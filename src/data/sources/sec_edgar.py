"""
SEC Edgar filing collector for sentiment analysis.
"""

import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from loguru import logger
import re

from ...utils.exceptions import DataSourceException
from ...core.cache_manager import get_cache_manager


class SECEdgarCollector:
    """
    Collects SEC filings from EDGAR database.
    """

    def __init__(self, use_cache: bool = True):
        """
        Initialize SEC Edgar collector.

        Args:
            use_cache: Whether to use caching
        """
        self.use_cache = use_cache
        self.cache_manager = get_cache_manager() if use_cache else None
        self.base_url = "https://www.sec.gov"
        
        # SEC requires User-Agent header
        self.headers = {
            "User-Agent": "FinanceMoraiAgent/1.0 (Educational Research)",
        }
        
        logger.info("SECEdgarCollector initialized")

    def collect_filings(
        self,
        ticker: str,
        filing_types: Optional[List[str]] = None,
        days_back: int = 90,
        max_filings: int = 10,
    ) -> List[Dict]:
        """
        Collect SEC filings for a ticker.

        Args:
            ticker: Stock ticker symbol
            filing_types: Types of filings (10-K, 10-Q, 8-K, etc.)
            days_back: How many days back to search
            max_filings: Maximum filings to return

        Returns:
            List of filings with metadata
        """
        if filing_types is None:
            filing_types = ["10-K", "10-Q", "8-K"]

        logger.info(f"Collecting SEC filings for {ticker}")

        # Check cache
        cache_key = f"sec:{ticker}:{'-'.join(filing_types)}:{days_back}"
        if self.use_cache:
            cached = self.cache_manager.get(cache_key, ttl=7200)  # 2 hour cache
            if cached is not None:
                logger.info(f"Using cached SEC filings for {ticker}")
                return cached

        filings = []

        try:
            # Get CIK (Central Index Key) for the ticker
            cik = self._get_cik(ticker)
            if not cik:
                logger.warning(f"Could not find CIK for ticker {ticker}")
                return []

            # Search for filings
            cutoff_date = datetime.now() - timedelta(days=days_back)

            for filing_type in filing_types:
                try:
                    filing_data = self._search_filings(cik, filing_type, cutoff_date)
                    filings.extend(filing_data[:max_filings // len(filing_types)])
                except Exception as e:
                    logger.warning(f"Failed to collect {filing_type} filings: {e}")

        except Exception as e:
            logger.error(f"SEC filing collection failed: {e}")

        # Cache results
        if self.use_cache and filings:
            self.cache_manager.set(cache_key, filings, expire=7200)

        logger.info(f"Collected {len(filings)} SEC filings for {ticker}")
        return filings

    def _get_cik(self, ticker: str) -> Optional[str]:
        """
        Get CIK (Central Index Key) for a ticker.

        Args:
            ticker: Stock ticker

        Returns:
            CIK string or None
        """
        try:
            # Use SEC's ticker to CIK mapping
            url = "https://www.sec.gov/cgi-bin/browse-edgar"
            params = {
                "action": "getcompany",
                "ticker": ticker.replace(".NS", "").replace(".BO", ""),
                "output": "xml",
            }

            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                # Extract CIK from response
                match = re.search(r'<CIK>(\d+)</CIK>', response.text)
                if match:
                    return match.group(1).zfill(10)  # Pad to 10 digits

        except Exception as e:
            logger.warning(f"Failed to get CIK for {ticker}: {e}")

        return None

    def _search_filings(
        self,
        cik: str,
        filing_type: str,
        cutoff_date: datetime,
    ) -> List[Dict]:
        """Search for specific filing types."""
        filings = []

        try:
            url = "https://www.sec.gov/cgi-bin/browse-edgar"
            params = {
                "action": "getcompany",
                "CIK": cik,
                "type": filing_type,
                "dateb": "",
                "owner": "exclude",
                "count": "10",
                "output": "xml",
            }

            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                # Parse XML response (simplified)
                # In production, use xml.etree or lxml
                filing_matches = re.findall(
                    r'<filing-href>(.*?)</filing-href>.*?<filing-date>(.*?)</filing-date>',
                    response.text,
                    re.DOTALL
                )

                for href, date_str in filing_matches[:10]:
                    try:
                        filing_date = datetime.strptime(date_str, "%Y-%m-%d")
                        if filing_date >= cutoff_date:
                            filings.append({
                                "type": filing_type,
                                "date": date_str,
                                "url": href,
                                "source": "SEC Edgar",
                            })
                    except:
                        continue

        except Exception as e:
            logger.warning(f"Filing search failed: {e}")

        return filings

    def get_filing_text(self, filing_url: str, max_length: int = 10000) -> str:
        """
        Fetch text from a filing.

        Args:
            filing_url: URL to filing
            max_length: Maximum text length to return

        Returns:
            Filing text excerpt
        """
        try:
            response = requests.get(filing_url, headers=self.headers, timeout=15)
            if response.status_code == 200:
                text = response.text
                
                # Remove HTML tags (basic)
                text = re.sub(r'<[^>]+>', ' ', text)
                
                # Clean up whitespace
                text = re.sub(r'\s+', ' ', text).strip()
                
                return text[:max_length]

        except Exception as e:
            logger.warning(f"Failed to fetch filing text: {e}")

        return ""
