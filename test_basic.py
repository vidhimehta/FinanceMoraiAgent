"""
Basic functionality test for FinanceMoraiAgent Phase 1.
Run this after installation to verify everything works.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    try:
        from data.sources.yahoo_finance import YahooFinanceSource
        from data.preprocessor import DataPreprocessor
        from data.feature_engineering import FeatureEngineer
        from core.cache_manager import CacheManager
        from utils.validators import validate_ticker
        from utils.helpers import normalize_ticker
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False


def test_yahoo_finance():
    """Test Yahoo Finance data fetching."""
    print("\nTesting Yahoo Finance data fetching...")
    try:
        from data.sources.yahoo_finance import YahooFinanceSource

        yahoo = YahooFinanceSource(use_cache=False)  # Disable cache for test

        # Fetch AAPL data for last 7 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)

        df = yahoo.fetch_ohlcv("AAPL", start_date, end_date)

        if df.empty:
            print("✗ No data returned")
            return False

        print(f"✓ Fetched {len(df)} rows for AAPL")
        print(f"  Columns: {list(df.columns)}")
        print(f"  Date range: {df.index.min().date()} to {df.index.max().date()}")
        return True
    except Exception as e:
        print(f"✗ Yahoo Finance test failed: {e}")
        return False


def test_preprocessing():
    """Test data preprocessing."""
    print("\nTesting data preprocessing...")
    try:
        from data.sources.yahoo_finance import YahooFinanceSource
        from data.preprocessor import DataPreprocessor

        yahoo = YahooFinanceSource(use_cache=False)
        preprocessor = DataPreprocessor()

        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        df = yahoo.fetch_ohlcv("AAPL", start_date, end_date)

        df_clean = preprocessor.clean_ohlcv(df)

        print(f"✓ Preprocessed data: {len(df)} → {len(df_clean)} rows")

        # Validate data quality
        quality = preprocessor.validate_data_quality(df_clean)
        print(f"  Total rows: {quality['total_rows']}")
        print(f"  Missing values: {sum(quality['missing_values'].values())}")
        return True
    except Exception as e:
        print(f"✗ Preprocessing test failed: {e}")
        return False


def test_feature_engineering():
    """Test feature engineering."""
    print("\nTesting feature engineering...")
    try:
        from data.sources.yahoo_finance import YahooFinanceSource
        from data.feature_engineering import FeatureEngineer

        yahoo = YahooFinanceSource(use_cache=False)
        engineer = FeatureEngineer()

        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)
        df = yahoo.fetch_ohlcv("AAPL", start_date, end_date)

        df_features = engineer.add_all_features(df)

        print(f"✓ Added features: {len(df.columns)} → {len(df_features.columns)} columns")

        # Show some feature names
        new_features = set(df_features.columns) - set(df.columns)
        print(f"  New features: {', '.join(list(new_features)[:10])}...")
        return True
    except Exception as e:
        print(f"✗ Feature engineering test failed: {e}")
        return False


def test_cache():
    """Test cache functionality."""
    print("\nTesting cache manager...")
    try:
        from core.cache_manager import CacheManager
        import tempfile

        # Use temporary directory for test
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = CacheManager(cache_dir=tmpdir + "/cache", parquet_dir=tmpdir + "/parquet")

            # Test set/get
            cache.set("test_key", "test_value")
            value = cache.get("test_key")

            if value != "test_value":
                print("✗ Cache set/get failed")
                return False

            print("✓ Cache set/get working")

            # Test stats
            stats = cache.get_cache_stats()
            print(f"  Memory items: {stats['memory_items']}")
            print(f"  Disk items: {stats['disk_items']}")
            return True
    except Exception as e:
        print(f"✗ Cache test failed: {e}")
        return False


def test_validators():
    """Test validators."""
    print("\nTesting validators...")
    try:
        from utils.validators import validate_ticker, validate_date_range
        from datetime import datetime

        # Test ticker validation
        ticker = validate_ticker("AAPL")
        assert ticker == "AAPL"

        ticker = validate_ticker("tcs.ns")
        assert ticker == "TCS.NS"

        print("✓ Ticker validation working")

        # Test date validation
        start, end = validate_date_range("2024-01-01", "2024-12-31")
        assert start.year == 2024
        assert end.year == 2024

        print("✓ Date validation working")
        return True
    except Exception as e:
        print(f"✗ Validator test failed: {e}")
        return False


def run_all_tests():
    """Run all tests."""
    print("="*60)
    print("FinanceMoraiAgent Phase 1 - Basic Functionality Test")
    print("="*60)

    tests = [
        ("Imports", test_imports),
        ("Yahoo Finance", test_yahoo_finance),
        ("Preprocessing", test_preprocessing),
        ("Feature Engineering", test_feature_engineering),
        ("Cache Manager", test_cache),
        ("Validators", test_validators),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ {name} test crashed: {e}")
            results.append((name, False))

    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:10} {name}")

    print("="*60)
    print(f"Results: {passed}/{total} tests passed")
    print("="*60)

    if passed == total:
        print("\n🎉 All tests passed! Phase 1 is working correctly.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check the output above.")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
