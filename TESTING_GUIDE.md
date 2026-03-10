# Testing Guide for FinanceMoraiAgent

## Quick Test (5 minutes)

### Step 1: Install Dependencies
```bash
cd "/Users/vidhi.mehta/Desktop/Cursor Projects/FinanceMoraiAgent"
chmod +x install.sh
./install.sh
```

This will:
- Create virtual environment
- Install all dependencies
- Set up storage directories
- Create .env file

### Step 2: Run Basic Test Script
```bash
source venv/bin/activate
python test_basic.py
```

This runs automated tests for:
- Module imports
- Yahoo Finance data fetching
- Data preprocessing
- Feature engineering
- Cache functionality
- Input validation

**Expected output:**
```
============================================================
FinanceMoraiAgent Phase 1 - Basic Functionality Test
============================================================

Testing imports...
✓ All imports successful

Testing Yahoo Finance data fetching...
✓ Fetched 5 rows for AAPL
  Columns: ['Open', 'High', 'Low', 'Close', 'Volume', ...]
  Date range: 2026-03-03 to 2026-03-10

Testing data preprocessing...
✓ Preprocessed data: 30 → 30 rows
  Total rows: 30
  Missing values: 0

Testing feature engineering...
✓ Added features: 6 → 50+ columns
  New features: RSI, MACD, SMA_20, EMA_20, ...

Testing cache manager...
✓ Cache set/get working
  Memory items: 1
  Disk items: 1

Testing validators...
✓ Ticker validation working
✓ Date validation working

============================================================
Test Summary
============================================================
✓ PASS     Imports
✓ PASS     Yahoo Finance
✓ PASS     Preprocessing
✓ PASS     Feature Engineering
✓ PASS     Cache Manager
✓ PASS     Validators
============================================================
Results: 6/6 tests passed
============================================================

🎉 All tests passed! Phase 1 is working correctly.
```

---

## Interactive Test (10 minutes)

### Step 1: Launch the CLI Application
```bash
source venv/bin/activate
python run.py
```

### Step 2: Test US Stock Data
1. Select option **1** (Fetch Market Data)
2. Enter ticker: **AAPL**
3. Select date range: **1** (Last 30 days)
4. View the results
5. Answer "yes" to show detailed data
6. Answer "yes" to save to cache

**What to look for:**
- ✓ Data fetched successfully
- ✓ Summary table shows price stats
- ✓ Date range is correct
- ✓ No error messages
- ✓ Latest price displayed

### Step 3: Test Indian Stock Data
1. Select option **1** again
2. Enter ticker: **TCS.NS**
3. Select date range: **2** (Last 90 days)
4. View results

**What to look for:**
- ✓ Market identified as "NSE"
- ✓ Data fetches successfully
- ✓ Indian stock data works

### Step 4: Test Cache
1. Repeat Step 2 (fetch AAPL again)
2. Notice it's much faster (cache hit)
3. Select option **6** (View Cache Stats)
4. Check cache statistics

**What to look for:**
- ✓ Second fetch is instantaneous
- ✓ Cache shows items stored
- ✓ Parquet files created

### Step 5: Exit
- Select option **0** to exit

---

## Unit Tests (5 minutes)

### Run Pytest Tests
```bash
source venv/bin/activate
pytest tests/unit/test_validators.py -v
```

**Expected output:**
```
tests/unit/test_validators.py::TestTickerValidation::test_valid_us_ticker PASSED
tests/unit/test_validators.py::TestTickerValidation::test_valid_indian_ticker PASSED
tests/unit/test_validators.py::TestTickerValidation::test_invalid_ticker PASSED
tests/unit/test_validators.py::TestDateValidation::test_valid_date_string PASSED
...
======================== 20 passed in 1.23s ========================
```

### Run All Tests with Coverage
```bash
pytest tests/ -v --cov=src --cov-report=html
```

This creates a coverage report in `htmlcov/index.html`

---

## Manual Component Testing

### Test 1: Yahoo Finance Module
```bash
source venv/bin/activate
python3 << 'EOF'
from src.data.sources.yahoo_finance import YahooFinanceSource
from datetime import datetime, timedelta

yahoo = YahooFinanceSource()
end_date = datetime.now()
start_date = end_date - timedelta(days=7)

# Fetch AAPL data
df = yahoo.fetch_ohlcv("AAPL", start_date, end_date)
print(f"✓ Fetched {len(df)} rows for AAPL")
print(f"  Date range: {df.index.min().date()} to {df.index.max().date()}")
print(f"  Latest close: ${df['Close'].iloc[-1]:.2f}")
print("\nFirst few rows:")
print(df.head())

# Test Indian stock
df_india = yahoo.fetch_ohlcv("TCS.NS", start_date, end_date)
print(f"\n✓ Fetched {len(df_india)} rows for TCS.NS")
EOF
```

### Test 2: Data Preprocessing
```bash
python3 << 'EOF'
from src.data.sources.yahoo_finance import YahooFinanceSource
from src.data.preprocessor import DataPreprocessor
from datetime import datetime, timedelta

yahoo = YahooFinanceSource()
preprocessor = DataPreprocessor()

end_date = datetime.now()
start_date = end_date - timedelta(days=30)
df = yahoo.fetch_ohlcv("AAPL", start_date, end_date)

# Clean data
df_clean = preprocessor.clean_ohlcv(df)
print(f"✓ Cleaned: {len(df)} → {len(df_clean)} rows")

# Validate quality
quality = preprocessor.validate_data_quality(df_clean)
print(f"  Missing values: {sum(quality['missing_values'].values())}")
print(f"  Date range: {quality['date_range']['days']} days")
print(f"  Price range: ${quality['price_stats']['min']:.2f} - ${quality['price_stats']['max']:.2f}")
EOF
```

### Test 3: Feature Engineering
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

# Add all features
df_features = engineer.add_all_features(df)
print(f"✓ Added features: {len(df.columns)} → {len(df_features.columns)} columns")

# Show some indicators
print("\nLatest Technical Indicators:")
latest = df_features.iloc[-1]
if 'RSI' in df_features.columns:
    print(f"  RSI: {latest['RSI']:.2f}")
if 'MACD_12_26_9' in df_features.columns:
    print(f"  MACD: {latest['MACD_12_26_9']:.4f}")
if 'SMA_20' in df_features.columns:
    print(f"  SMA(20): ${latest['SMA_20']:.2f}")
if 'ATR_14' in df_features.columns:
    print(f"  ATR(14): {latest['ATR_14']:.2f}")
EOF
```

### Test 4: Cache System
```bash
python3 << 'EOF'
from src.core.cache_manager import CacheManager
import time

cache = CacheManager()

# Test set/get
print("Testing cache operations...")
cache.set("test_key", "test_value")
value = cache.get("test_key")
print(f"✓ Cache set/get: {value}")

# Test TTL
cache.set("ttl_key", "expires_soon", expire=2)
print(f"✓ With TTL: {cache.get('ttl_key')}")
time.sleep(3)
print(f"✓ After expiry: {cache.get('ttl_key', default='EXPIRED')}")

# Test stats
stats = cache.get_cache_stats()
print(f"\nCache Statistics:")
print(f"  Memory items: {stats['memory_items']}")
print(f"  Disk items: {stats['disk_items']}")
print(f"  Disk size: {stats['disk_size_mb']:.2f} MB")
EOF
```

---

## Performance Testing

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
start_time = time.time()
df1 = yahoo.fetch_ohlcv("AAPL", start_date, end_date)
uncached_time = time.time() - start_time

# Second fetch (cached)
start_time = time.time()
df2 = yahoo.fetch_ohlcv("AAPL", start_date, end_date)
cached_time = time.time() - start_time

print(f"Performance Test:")
print(f"  Uncached: {uncached_time:.2f} seconds")
print(f"  Cached: {cached_time:.2f} seconds")
print(f"  Speedup: {uncached_time/cached_time:.1f}x faster")
EOF
```

---

## Common Test Scenarios

### Scenario 1: Multiple Tickers
```bash
python3 << 'EOF'
from src.data.sources.yahoo_finance import YahooFinanceSource
from datetime import datetime, timedelta

yahoo = YahooFinanceSource()
end_date = datetime.now()
start_date = end_date - timedelta(days=7)

tickers = ["AAPL", "GOOGL", "MSFT", "TCS.NS", "RELIANCE.NS"]

print("Fetching multiple tickers...")
for ticker in tickers:
    try:
        df = yahoo.fetch_ohlcv(ticker, start_date, end_date)
        latest_price = df['Close'].iloc[-1]
        print(f"✓ {ticker:12} - ${latest_price:8.2f} ({len(df)} rows)")
    except Exception as e:
        print(f"✗ {ticker:12} - Error: {e}")
EOF
```

### Scenario 2: Different Date Ranges
```bash
python3 << 'EOF'
from src.data.sources.yahoo_finance import YahooFinanceSource
from datetime import datetime, timedelta

yahoo = YahooFinanceSource()
end_date = datetime.now()

ranges = [
    ("1 week", 7),
    ("1 month", 30),
    ("3 months", 90),
    ("1 year", 365),
]

print("Testing different date ranges for AAPL:")
for name, days in ranges:
    start_date = end_date - timedelta(days=days)
    df = yahoo.fetch_ohlcv("AAPL", start_date, end_date)
    print(f"✓ {name:10} - {len(df):3} rows")
EOF
```

---

## Troubleshooting Tests

### If imports fail:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### If Yahoo Finance fails:
- Check internet connection
- Try a different ticker
- Yahoo Finance may be rate-limiting (wait a few minutes)

### If tests are slow:
- First run downloads data (2-5 seconds per ticker)
- Subsequent runs use cache (< 100ms)
- Clear cache: `rm -rf storage/cache/*`

### View logs:
```bash
tail -f storage/app.log
```

---

## Success Checklist

✅ **Installation**
- [ ] Virtual environment created
- [ ] All dependencies installed
- [ ] No import errors

✅ **Basic Functionality**
- [ ] test_basic.py passes all 6 tests
- [ ] US stock data fetches successfully
- [ ] Indian stock data fetches successfully
- [ ] Cache works properly

✅ **CLI Application**
- [ ] Menu displays correctly
- [ ] Can fetch and view data
- [ ] Data summary shows correctly
- [ ] Cache stats display

✅ **Unit Tests**
- [ ] All validator tests pass
- [ ] No test failures

✅ **Performance**
- [ ] Uncached fetch: 2-5 seconds
- [ ] Cached fetch: < 100ms
- [ ] Cache speedup > 10x

---

## Quick Test Command Summary

```bash
# Full test suite
cd "/Users/vidhi.mehta/Desktop/Cursor Projects/FinanceMoraiAgent"
source venv/bin/activate
python test_basic.py                    # Basic tests
pytest tests/unit/ -v                   # Unit tests
python run.py                      # Interactive CLI

# Quick smoke test
python3 -c "from src.data.sources.yahoo_finance import YahooFinanceSource; print('✓ Imports work')"
```

---

**Recommended Testing Order:**
1. Run `test_basic.py` first (5 min)
2. Try CLI application (10 min)
3. Run unit tests (5 min)
4. Try manual tests as needed

Good luck! 🚀
