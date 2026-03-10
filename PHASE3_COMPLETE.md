# Phase 3: Sentiment Analysis - Complete!

## What's New in Phase 3

Phase 3 adds **multi-source sentiment analysis** for stocks. The system collects and analyzes financial sentiment from:

1. **News Articles** - Google News RSS, Yahoo Finance RSS, optional NewsAPI
2. **SEC Filings** - 8-K reports from EDGAR (US stocks)
3. **SEBI Announcements** - NSE/BSE filings (Indian stocks, placeholder)

### AI-Powered Analysis

- **FinBERT Model** (optional) - Domain-specific financial sentiment AI
- **VADER Lexicon** - Fast, reliable lexicon-based sentiment (default)
- **Multi-source Aggregation** - Weighted combination of all sources
- **Time Decay** - Recent sentiment weighted more than old news

---

## How to Use Sentiment Analysis

### CLI Interface

```bash
# Run the application
./venv/bin/python run.py

# Select option 2: Sentiment Analysis
Enter your choice: 2

# Enter stock details
Enter stock ticker: AAPL
Enter company name (optional): Apple Inc
Select time period: 7 days

# View results
Overall Sentiment: positive (0.314)
Confidence: 15.0%

Source Breakdown:
- NEWS: 5 articles, positive (+0.314)
- SEC: 0 filings, neutral (0.000)
```

### What the Results Mean

**Sentiment Score Range:**
- `+0.05 to +1.00` = Positive (bullish sentiment)
- `-0.05 to +0.05` = Neutral (no clear direction)
- `-1.00 to -0.05` = Negative (bearish sentiment)

**Confidence:**
- Higher confidence = more data sources analyzed
- Lower confidence = limited data available

**Source Breakdown:**
- **News**: 60% weight in overall score
- **SEC/SEBI**: 20% weight in overall score
- Time decay applied: recent sentiment weighted more

---

## Technical Details

### Architecture

```
User Request
    ↓
SentimentCommand (CLI)
    ↓
SentimentAnalyzer
    ↓
    ├── NewsCollector → Google RSS, Yahoo RSS, NewsAPI (optional)
    ├── SECEdgarCollector → EDGAR 8-K filings
    ├── SEBICollector → NSE/BSE announcements (placeholder)
    ↓
VADERAnalyzer or FinBERTModel
    ↓
Weighted Aggregation → Final Score
```

### Files Created in Phase 3

**Data Collection:**
- `src/data/sources/news_collector.py` - News aggregation
- `src/data/sources/sec_edgar.py` - SEC filings
- `src/data/sources/sebi_client.py` - SEBI announcements

**Analysis:**
- `src/sentiment/analyzer.py` - Main orchestrator
- `src/sentiment/models/lexicon.py` - VADER sentiment
- `src/sentiment/models/finbert.py` - FinBERT AI model

**CLI:**
- `src/cli/commands/sentiment_cmd.py` - User interface

---

## Testing Phase 3

### Automated Test

```bash
./venv/bin/python test_phase3.py
```

Expected output:
```
✓ PASS     News Collection
✓ PASS     VADER Sentiment
✓ PASS     Full Sentiment Analysis
✓ PASS     Indian Stock Support
```

### Manual Testing

**Test US Stock:**
```bash
./venv/bin/python run.py
> Option 2
> Ticker: AAPL
> Company: Apple Inc
> Period: 7 days
```

**Test Indian Stock:**
```bash
./venv/bin/python run.py
> Option 2
> Ticker: TCS.NS
> Company: Tata Consultancy Services
> Period: 7 days
```

---

## Optional: NewsAPI Integration

Phase 3 works without any API keys using free RSS feeds. For better news coverage, you can add NewsAPI:

1. Get free API key: https://newsapi.org
2. Add to `.env`:
   ```
   NEWS_API_KEY=your_key_here
   ```
3. Restart application

With NewsAPI:
- More news sources (100+)
- Better article quality
- Filtered by relevance

---

## Known Limitations

1. **SEC Edgar**: CIK lookup not yet implemented
   - Workaround: Using direct ticker search
   - Future: Add CIK mapping database

2. **SEBI Announcements**: NSE/BSE APIs require complex session management
   - Current: Placeholder implementation
   - Future: Add proper authentication flow

3. **FinBERT Model**: Requires 1GB+ model download
   - Default: VADER (fast, no download)
   - Optional: Enable FinBERT in settings

---

## Performance

| Operation | Time | Cached |
|-----------|------|--------|
| News collection (RSS) | 1-2s | <100ms |
| VADER analysis | 50-100ms | - |
| FinBERT analysis | 2-5s | - |
| Full sentiment analysis | 2-3s | <200ms |

All results are cached for 1 hour.

---

## Next Steps

**Phase 4: Regime Detection** (Coming Soon)
- Volatility-based regime detection
- Trend-based regime analysis
- Hidden Markov Models
- Moirai-enhanced context

**Integration:**
- Sentiment scores feed into Moirai forecasts as context
- "Strong positive sentiment from earnings..." improves predictions

---

## Troubleshooting

### No news articles found
- Check internet connection
- Try a more popular ticker (AAPL, GOOGL, etc.)
- RSS feeds may be rate-limited (wait a few minutes)

### SEC filings not loading
- CIK lookup requires ticker-to-CIK mapping
- Currently a known limitation
- News sentiment still works

### Sentiment score is 0.0
- Not enough data in selected time period
- Try longer period (14 or 30 days)
- Check if ticker is correct

---

## Repository Updates

Phase 3 is complete and pushed to GitHub:
- ✅ Multi-source sentiment analysis
- ✅ US and Indian stock support
- ✅ Caching and performance optimization
- ✅ CLI integration
- ✅ Automated tests

**Status**: Phase 3 Complete! (March 10, 2026)

**Next**: Phase 4 - Regime Detection

---

Happy analyzing! 📊
