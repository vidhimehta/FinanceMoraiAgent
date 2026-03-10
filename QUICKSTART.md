# Quick Start Guide

## Installation

### Step 1: Run the installation script

```bash
cd "/Users/vidhi.mehta/Desktop/Cursor Projects/FinanceMoraiAgent"
chmod +x install.sh
./install.sh
```

### Step 2: Activate the virtual environment

```bash
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

### Step 3: Run the application

```bash
python run.py
```

## First Use - Try These Commands

### 1. Fetch Apple Stock Data

1. Run `python run.py`
2. Select option `1` (Fetch Market Data)
3. Enter ticker: `AAPL`
4. Select date range: `1` (Last 30 days)
5. View the results!

### 2. Fetch Indian Stock Data

1. Select option `1` (Fetch Market Data)
2. Enter ticker: `TCS.NS` (Tata Consultancy Services on NSE)
3. Select date range: `2` (Last 90 days)
4. View the results!

### 3. Check Cache Statistics

1. Select option `6` (View Cache Stats)
2. See how much data is cached
3. Optionally clear cache

## Common Tickers to Try

**US Stocks:**
- AAPL (Apple)
- GOOGL (Google)
- MSFT (Microsoft)
- TSLA (Tesla)
- NVDA (NVIDIA)
- META (Meta/Facebook)
- AMZN (Amazon)

**Indian Stocks (NSE):**
- TCS.NS (Tata Consultancy Services)
- RELIANCE.NS (Reliance Industries)
- INFY.NS (Infosys)
- HDFCBANK.NS (HDFC Bank)
- ICICIBANK.NS (ICICI Bank)
- WIPRO.NS (Wipro)

**Indian Stocks (BSE):**
- TCS.BO
- RELIANCE.BO
- INFY.BO

## Manual Installation (if script fails)

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Run the application
python run.py
```

## Troubleshooting

### "No module named ..."
- Make sure virtual environment is activated: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`

### "Failed to fetch data"
- Check internet connection
- Verify ticker symbol is correct
- Try a different ticker

### "Permission denied" on install.sh
- Run: `chmod +x install.sh`
- Then: `./install.sh`

## Testing the System

Run a quick test to verify everything works:

```bash
# Activate virtual environment
source venv/bin/activate

# Run tests (when implemented)
pytest tests/ -v

# Or run a simple Python test
python3 -c "
from src.data.sources.yahoo_finance import YahooFinanceSource
from datetime import datetime, timedelta

yahoo = YahooFinanceSource()
end_date = datetime.now()
start_date = end_date - timedelta(days=7)
df = yahoo.fetch_ohlcv('AAPL', start_date, end_date)
print(f'✓ Successfully fetched {len(df)} rows for AAPL')
print(df.tail())
"
```

## Next Steps

Once Phase 1 is working:

1. **Explore different tickers** - Try both US and Indian stocks
2. **Experiment with date ranges** - Compare different time periods
3. **Check technical indicators** - Look at RSI, MACD, etc. in the data
4. **Monitor cache performance** - See how caching speeds up queries

## Phase 2 Coming Soon

- Moirai model integration for forecasting
- Context-aware predictions
- Forecast visualization

## Getting Help

- Check the main README.md for detailed documentation
- Review config/settings.yaml for configuration options
- Look at example tickers and date ranges above

---

**Current Status**: Phase 1 (Foundation) - Ready to use!

Enjoy exploring the financial markets with FinanceMoraiAgent! 🚀
