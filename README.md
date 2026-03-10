# FinanceMoraiAgent

A quantitative finance system that leverages Salesforce's Moirai time-series foundation model for context-aware stock market forecasting, sentiment analysis, regime detection, and backtesting.

## Features

### Phase 1: Foundation (✅ Implemented)
- **Market Data Fetching**: Download OHLCV data from Yahoo Finance for US and Indian markets
- **3-Tier Caching**: Memory → Disk → Parquet for efficient data storage
- **Data Preprocessing**: Clean, normalize, and validate financial data
- **Technical Indicators**: 50+ indicators including RSI, MACD, Bollinger Bands, ATR, and more
- **CLI Interface**: User-friendly command-line interface with Rich library

### Coming Soon
- **Phase 2**: Moirai Model Integration (Forecasting)
- **Phase 3**: Sentiment Analysis (News, SEC/SEBI filings, social media)
- **Phase 4**: Regime Detection (Volatility, trend, HMM, context-driven)
- **Phase 5**: Backtesting Engine (Strategy testing and performance metrics)

## Why This Approach?

- **Open-source & Free**: Uses Hugging Face Moirai model (no API costs)
- **Context-aware forecasting**: Integrates sentiment and regime analysis
- **Multi-market support**: US (NYSE, NASDAQ) and India (NSE, BSE)
- **CLI-first**: Simple command-line interface for quick analysis
- **Modular design**: Easy to extend with new strategies or data sources

## Installation

### Prerequisites
- Python 3.9 or higher
- 8GB+ RAM (16GB recommended for GPU inference)
- Optional: NVIDIA GPU with CUDA support or Apple Silicon (MPS)

### Setup

1. **Clone the repository**
```bash
cd /Users/vidhi.mehta/Desktop/Cursor\ Projects/FinanceMoraiAgent
```

2. **Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env and add your API keys (optional for Phase 1)
```

5. **Verify installation**
```bash
python src/main.py
```

## Usage

### Basic Usage

Run the CLI interface:
```bash
python src/main.py
```

### Fetching Market Data

1. Select option `1` from the main menu
2. Enter a ticker symbol:
   - US stocks: `AAPL`, `GOOGL`, `MSFT`
   - Indian stocks: `TCS.NS`, `RELIANCE.BO`, `INFY.NS`
3. Choose date range (30 days, 90 days, 1 year, or custom)
4. Data is automatically cached for faster access

### Supported Tickers

**US Markets (NYSE, NASDAQ)**
- Examples: AAPL, GOOGL, MSFT, TSLA, NVDA, META, AMZN

**Indian Markets**
- NSE (National Stock Exchange): Add `.NS` suffix
  - Examples: TCS.NS, RELIANCE.NS, INFY.NS, HDFCBANK.NS
- BSE (Bombay Stock Exchange): Add `.BO` suffix
  - Examples: TCS.BO, RELIANCE.BO, INFY.BO

## Project Structure

```
FinanceMoraiAgent/
├── config/
│   └── settings.yaml          # Configuration settings
├── src/
│   ├── core/                  # Core components
│   │   └── cache_manager.py   # 3-tier caching system
│   ├── data/
│   │   ├── sources/
│   │   │   └── yahoo_finance.py  # Yahoo Finance wrapper
│   │   ├── preprocessor.py    # Data cleaning
│   │   └── feature_engineering.py  # Technical indicators
│   ├── cli/
│   │   └── menu.py            # CLI interface
│   ├── utils/                 # Utilities
│   └── main.py                # Entry point
├── storage/
│   ├── cache/                 # Disk cache
│   ├── historical/            # Parquet files
│   └── models/                # Model cache
└── tests/                     # Test suite
```

## Configuration

### Main Configuration (`config/settings.yaml`)

Key settings you can customize:
- **Data sources**: Enable/disable sources, set timeouts
- **Caching**: TTL for different data types
- **Technical indicators**: Configure periods and parameters
- **Logging**: Set log level and output

### Environment Variables (`.env`)

Optional API keys for future phases:
- `NEWS_API_KEY`: NewsAPI key for sentiment analysis
- `REDDIT_CLIENT_ID/SECRET`: Reddit API for social sentiment
- `TWITTER_BEARER_TOKEN`: Twitter API for social sentiment

## Technical Indicators

The system includes 50+ technical indicators:

**Price Indicators**
- Simple Moving Average (SMA)
- Exponential Moving Average (EMA)
- Bollinger Bands

**Momentum Indicators**
- Relative Strength Index (RSI)
- MACD (Moving Average Convergence Divergence)
- Stochastic Oscillator
- Rate of Change (ROC)
- Commodity Channel Index (CCI)

**Volatility Indicators**
- Average True Range (ATR)
- Historical Volatility
- True Range

**Volume Indicators**
- On-Balance Volume (OBV)
- Money Flow Index (MFI)
- Volume Moving Averages

**Trend Indicators**
- Average Directional Index (ADX)
- Supertrend
- Parabolic SAR

## Data Caching

The system uses a 3-tier caching strategy:

1. **Memory Cache**: Fast access for recent queries
2. **Disk Cache**: Persistent cache using diskcache
3. **Parquet Files**: Long-term storage with compression

Benefits:
- Faster subsequent queries (100x speedup)
- Reduced API calls
- Offline access to historical data
- Minimal storage footprint with Parquet compression

## Development

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black src/
```

### Type Checking

```bash
mypy src/
```

## Performance

**Typical performance metrics**:
- Data fetch (cached): < 100ms
- Data fetch (uncached): 2-5 seconds
- Preprocessing: < 500ms
- Feature engineering: 1-2 seconds for 1 year of daily data

## Troubleshooting

### Issue: "No data returned for ticker"
- **Solution**: Verify ticker symbol is correct. Use `.NS` for NSE or `.BO` for BSE stocks.

### Issue: "Failed to fetch data after retries"
- **Solution**: Check internet connection. Yahoo Finance may be rate-limiting.

### Issue: "Invalid ticker format"
- **Solution**: Tickers should be alphanumeric. Indian stocks need `.NS` or `.BO` suffix.

### Issue: Cache is too large
- **Solution**: Use option 6 (View Cache Stats) to clear cache.

## Roadmap

### Phase 2: Moirai Integration (Week 3-4)
- Load Moirai model from Hugging Face
- Local inference engine
- Context integration for forecasts

### Phase 3: Sentiment Analysis (Week 5-6)
- News API integration
- SEC/SEBI filings analysis
- FinBERT sentiment model
- Multi-source aggregation

### Phase 4: Regime Detection (Week 7-8)
- Volatility-based detection
- Trend analysis
- Hidden Markov Models
- Context-driven regimes

### Phase 5: Backtesting (Week 9-11)
- Event-driven engine
- Multiple strategies
- Performance metrics
- Walk-forward validation

### Phase 6: Polish (Week 12-13)
- Social media integration
- Advanced visualization
- Parameter optimization
- Strategy comparison tools

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Acknowledgments

- **Salesforce Moirai**: Time-series foundation model
- **Yahoo Finance**: Market data via yfinance
- **ProsusAI FinBERT**: Financial sentiment analysis model
- **Rich**: Beautiful terminal UI

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check the documentation in `docs/`

---

**Status**: Phase 1 (Foundation) Complete ✅

**Last Updated**: March 2026
