# How to Test FinanceMoraiAgent - Quick Guide

## ✅ System is Ready!

All dependencies are installed and the system is working. Here's how to test it:

---

## Method 1: Quick CLI Test (Recommended - 2 minutes)

### Run the Application

```bash
cd "/Users/vidhi.mehta/Desktop/Cursor Projects/FinanceMoraiAgent"
./venv/bin/python run.py
```

Or use the launcher:
```bash
./financemorai
```

### Try These Operations

**Test 1: Fetch Apple Stock Data**
```
Enter your choice: 1
Enter stock ticker: AAPL
Select date range: 1
Show detailed data?: yes
Save data to cache?: yes
```

Expected: You'll see a data summary with latest price, date range, and a table with OHLCV data.

**Test 2: Fetch Indian Stock Data**
```
Enter your choice: 1
Enter stock ticker: TCS.NS
Select date range: 2
```

Expected: System identifies market as "NSE" and fetches Indian stock data.

**Test 3: Check Cache**
```
Enter your choice: 6
```

Expected: Shows cache statistics (memory items, disk items, parquet files).

**Test 4: Exit**
```
Enter your choice: 0
```

---

## Method 2: Automated Test Script (5 minutes)

### Run Basic Tests

```bash
cd "/Users/vidhi.mehta/Desktop/Cursor Projects/FinanceMoraiAgent"
source venv/bin/activate
python test_basic.py
```

This tests:
- ✓ Module imports
- ✓ Yahoo Finance data fetching
- ✓ Data preprocessing
- ✓ Feature engineering (50+ indicators)
- ✓ Cache functionality
- ✓ Input validation

Expected output: "6/6 tests passed"

---

## Method 3: Manual Python Tests

### Test Data Fetching

```bash
source venv/bin/activate
python3 << 'EOF'
from src.data.sources.yahoo_finance import YahooFinanceSource
from datetime import datetime, timedelta

yahoo = YahooFinanceSource()
end_date = datetime.now()
start_date = end_date - timedelta(days=7)

# Test US stock
df = yahoo.fetch_ohlcv("AAPL", start_date, end_date)
print(f"✓ Fetched {len(df)} rows for AAPL")
print(f"Latest close: ${df['Close'].iloc[-1]:.2f}")

# Test Indian stock
df_india = yahoo.fetch_ohlcv("TCS.NS", start_date, end_date)
print(f"✓ Fetched {len(df_india)} rows for TCS.NS")
EOF
```

### Test Technical Indicators

```bash
python3 << 'EOF'
from src.data.sources.yahoo_finance import YahooFinanceSource
from src.data.feature_engineering import FeatureEngineer
from datetime import datetime, timedelta

yahoo = YahooFinanceSource()
engineer = FeatureEngineer()

end_date = datetime.now()
start_date = end_date - timedelta(days=90)
df = yahoo.fetch_ohlcv("AAPL", start_date, end_date)

# Add all technical indicators
df_features = engineer.add_all_features(df)
print(f"✓ Added features: {len(df.columns)} → {len(df_features.columns)} columns")

# Show latest indicators
latest = df_features.iloc[-1]
print(f"\nLatest Technical Indicators:")
print(f"  Close: ${latest['Close']:.2f}")
print(f"  RSI: {latest['RSI']:.2f}")
print(f"  MACD: {latest['MACD']:.4f}")
print(f"  SMA_20: ${latest['SMA_20']:.2f}")
print(f"  ATR: {latest['ATR']:.2f}")
EOF
```

### Test Cache Performance

```bash
python3 << 'EOF'
from src.data.sources.yahoo_finance import YahooFinanceSource
from datetime import datetime, timedelta
import time

yahoo = YahooFinanceSource(use_cache=True)
end_date = datetime.now()
start_date = end_date - timedelta(days=30)

# First fetch (uncached)
print("First fetch (uncached)...")
start_time = time.time()
df1 = yahoo.fetch_ohlcv("MSFT", start_date, end_date)
uncached_time = time.time() - start_time
print(f"  Time: {uncached_time:.2f}s")

# Second fetch (cached)
print("Second fetch (cached)...")
start_time = time.time()
df2 = yahoo.fetch_ohlcv("MSFT", start_date, end_date)
cached_time = time.time() - start_time
print(f"  Time: {cached_time:.4f}s")

print(f"\n✓ Cache speedup: {uncached_time/cached_time:.0f}x faster!")
EOF
```

---

## Method 4: Unit Tests (Advanced)

```bash
source venv/bin/activate
pytest tests/unit/test_validators.py -v
```

Expected: All 20+ unit tests pass.

---

## What to Look For

### ✅ Success Indicators

1. **Application starts** - No import errors
2. **Menu displays** - Colorful banner and menu options
3. **Data fetches** - Stock data downloads successfully
4. **Cache works** - Second fetch is instant
5. **Indicators calculate** - RSI, MACD, etc. show values
6. **No errors** - Clean execution

### ⚠️ Common Warnings (Safe to Ignore)

```
NotOpenSSLWarning: urllib3 v2 only supports OpenSSL 1.1.1+
```
This is a known issue with macOS LibreSSL and doesn't affect functionality.

---

## Troubleshooting

### Issue: "ModuleNotFoundError"
**Solution:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: "No data returned for ticker"
**Solution:**
- Check internet connection
- Verify ticker is correct (use `.NS` for NSE, `.BO` for BSE)
- Try a different ticker

### Issue: "Permission denied: ./financemorai"
**Solution:**
```bash
chmod +x financemorai
```

---

## Quick Command Reference

```bash
# Activate environment
source venv/bin/activate

# Run application
python run.py
# or
./financemorai

# Run basic tests
python test_basic.py

# Run unit tests
pytest tests/unit/ -v

# Check what's installed
pip list | grep -E "pandas|yfinance|rich"

# View logs
tail -f storage/app.log
```

---

## Test Data Suggestions

### US Stocks to Try
- AAPL (Apple) - Tech, high volume
- GOOGL (Google) - Tech
- MSFT (Microsoft) - Tech
- JPM (JP Morgan) - Finance
- XOM (Exxon) - Energy

### Indian Stocks to Try (NSE)
- TCS.NS (Tata Consultancy Services)
- RELIANCE.NS (Reliance Industries)
- INFY.NS (Infosys)
- HDFCBANK.NS (HDFC Bank)
- ICICIBANK.NS (ICICI Bank)

### Date Ranges to Try
- Last 7 days - Quick test
- Last 30 days - Good for indicators
- Last 90 days - Better trends
- Last year - Full analysis

---

## Expected Performance

Based on Phase 1 implementation:

| Operation | Time | Notes |
|-----------|------|-------|
| First data fetch | 2-5s | Downloads from Yahoo Finance |
| Cached data fetch | <100ms | Retrieves from cache |
| Preprocessing | <500ms | Cleans and validates |
| Feature engineering | 1-2s | Calculates 50+ indicators |
| Cache speedup | 10-50x | Depending on data size |

---

## Next Steps After Testing

Once you've verified Phase 1 works:

1. **Explore different tickers** - Try various US and Indian stocks
2. **Check technical indicators** - Look at RSI, MACD values
3. **Monitor cache performance** - See speedup on repeated queries
4. **Review logs** - Check `storage/app.log` for detailed info
5. **Prepare for Phase 2** - Moirai model integration

---

## Quick Validation Checklist

- [ ] Application runs without errors
- [ ] Can fetch US stock data (AAPL)
- [ ] Can fetch Indian stock data (TCS.NS)
- [ ] Technical indicators calculate correctly
- [ ] Cache works (second fetch is faster)
- [ ] Cache stats display
- [ ] Data can be saved to parquet
- [ ] All menu options respond
- [ ] Can exit cleanly

---

## Getting Help

- **Full testing guide**: See `TESTING_GUIDE.md`
- **Quick start**: See `QUICKSTART.md`
- **Full docs**: See `README.md`
- **Implementation status**: See `IMPLEMENTATION_STATUS.md`

---

**Status**: Phase 1 is fully functional and ready to use! 🚀

**Repository**: https://github.com/vidhimehta/FinanceMoraiAgent

Happy testing!
