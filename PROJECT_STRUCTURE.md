# FinanceMoraiAgent - Project Structure

## Directory Tree

```
FinanceMoraiAgent/
│
├── 📄 Configuration & Setup
│   ├── .env                      # Environment variables (API keys)
│   ├── .env.example              # Environment template
│   ├── .gitignore                # Git ignore rules
│   ├── requirements.txt          # Python dependencies
│   ├── setup.py                  # Package setup
│   ├── install.sh                # Installation script
│   ├── README.md                 # Main documentation
│   ├── QUICKSTART.md             # Quick start guide
│   ├── IMPLEMENTATION_STATUS.md  # Implementation status
│   └── PROJECT_STRUCTURE.md      # This file
│
├── 📁 config/                    # Configuration files
│   ├── __init__.py
│   └── settings.yaml             # Main configuration
│
├── 📁 src/                       # Source code
│   ├── __init__.py
│   ├── main.py                   # ⭐ Entry point
│   │
│   ├── 📁 core/                  # Core components
│   │   ├── __init__.py
│   │   └── cache_manager.py      # ✅ 3-tier caching system
│   │
│   ├── 📁 data/                  # Data handling
│   │   ├── __init__.py
│   │   ├── preprocessor.py       # ✅ Data cleaning
│   │   ├── feature_engineering.py # ✅ Technical indicators
│   │   │
│   │   └── 📁 sources/           # Data sources
│   │       ├── __init__.py
│   │       └── yahoo_finance.py  # ✅ Yahoo Finance API
│   │
│   ├── 📁 moirai/                # Moirai model (Phase 2)
│   │   └── __init__.py           # 🔜 Coming soon
│   │
│   ├── 📁 sentiment/             # Sentiment analysis (Phase 3)
│   │   ├── __init__.py           # 🔜 Coming soon
│   │   └── 📁 models/
│   │       └── __init__.py
│   │
│   ├── 📁 regime/                # Regime detection (Phase 4)
│   │   ├── __init__.py           # 🔜 Coming soon
│   │   └── 📁 methods/
│   │       └── __init__.py
│   │
│   ├── 📁 backtesting/           # Backtesting (Phase 5)
│   │   ├── __init__.py           # 🔜 Coming soon
│   │   └── 📁 strategies/
│   │       └── __init__.py
│   │
│   ├── 📁 cli/                   # Command-line interface
│   │   ├── __init__.py
│   │   ├── menu.py               # ✅ Interactive menu
│   │   └── 📁 commands/
│   │       └── __init__.py
│   │
│   └── 📁 utils/                 # Utilities
│       ├── __init__.py
│       ├── exceptions.py         # ✅ Custom exceptions
│       ├── logger.py             # ✅ Logging setup
│       ├── validators.py         # ✅ Input validation
│       └── helpers.py            # ✅ Helper functions
│
├── 📁 storage/                   # Data storage
│   ├── 📁 cache/                 # Disk cache
│   │   └── .gitkeep
│   ├── 📁 historical/            # Parquet files
│   │   └── .gitkeep
│   ├── 📁 models/                # Downloaded models
│   │   └── .gitkeep
│   └── 📁 results/               # Backtest results
│       └── .gitkeep
│
├── 📁 tests/                     # Test suite
│   ├── __init__.py
│   ├── 📁 unit/                  # Unit tests
│   │   ├── __init__.py
│   │   └── test_validators.py   # ✅ Validator tests
│   ├── 📁 integration/           # Integration tests
│   │   └── __init__.py
│   └── 📁 fixtures/              # Test fixtures
│       └── __init__.py
│
├── 📁 docs/                      # Documentation (future)
│
├── test_basic.py                 # ✅ Basic functionality test
│
└── 📁 venv/                      # Virtual environment
    └── (Python packages)
```

## File Count by Category

### ✅ Implemented (Phase 1)
- **Source Files**: 15 Python files
- **Configuration**: 2 files (settings.yaml, .env)
- **Documentation**: 4 files (README, QUICKSTART, STATUS, STRUCTURE)
- **Tests**: 2 files (test_basic.py, test_validators.py)
- **Scripts**: 1 file (install.sh)

### 🔜 Placeholder (Future Phases)
- **Moirai Integration**: 4 planned files
- **Sentiment Analysis**: 8 planned files
- **Regime Detection**: 6 planned files
- **Backtesting**: 8 planned files

## Key Files Description

### Entry Points
- `src/main.py` - Main application entry point
- `test_basic.py` - Basic functionality tests
- `install.sh` - Installation script

### Core System (Phase 1)
- `src/core/cache_manager.py` - 3-tier caching (memory/disk/parquet)
- `src/data/sources/yahoo_finance.py` - Yahoo Finance API wrapper
- `src/data/preprocessor.py` - Data cleaning and preprocessing
- `src/data/feature_engineering.py` - Technical indicators
- `src/cli/menu.py` - Interactive CLI menu

### Utilities
- `src/utils/exceptions.py` - Custom exception classes
- `src/utils/logger.py` - Logging configuration
- `src/utils/validators.py` - Input validation functions
- `src/utils/helpers.py` - Helper utilities

### Configuration
- `config/settings.yaml` - Main configuration file
- `.env` - Environment variables (API keys)

### Documentation
- `README.md` - Complete project documentation
- `QUICKSTART.md` - Getting started guide
- `IMPLEMENTATION_STATUS.md` - Detailed implementation status
- `PROJECT_STRUCTURE.md` - This file

## Module Dependencies

```
main.py
  ├── cli.menu
  │   ├── data.sources.yahoo_finance
  │   ├── data.preprocessor
  │   ├── data.feature_engineering
  │   ├── core.cache_manager
  │   └── utils.*
  ├── utils.logger
  └── utils.helpers

core.cache_manager
  ├── diskcache (external)
  ├── pandas (external)
  └── utils.helpers

data.sources.yahoo_finance
  ├── yfinance (external)
  ├── core.cache_manager
  └── utils.validators

data.preprocessor
  ├── pandas (external)
  ├── numpy (external)
  └── utils.validators

data.feature_engineering
  ├── pandas (external)
  ├── numpy (external)
  ├── pandas_ta (external)
  └── utils.validators
```

## Storage Organization

```
storage/
├── cache/              # Disk cache (diskcache)
│   └── (automatic)     # Created by cache_manager
│
├── historical/         # Long-term data storage
│   └── *.parquet       # TICKER_datatype.parquet
│
├── models/             # ML model cache (Phase 2+)
│   └── (future)        # Moirai, FinBERT models
│
└── results/            # Backtest results (Phase 5+)
    └── (future)        # CSV, JSON, HTML reports
```

## Import Pattern

All modules use absolute imports from `src/`:

```python
# Good ✅
from data.sources.yahoo_finance import YahooFinanceSource
from utils.validators import validate_ticker
from core.cache_manager import get_cache_manager

# Bad ❌
from ..data.sources import yahoo_finance  # Relative imports
import yahoo_finance  # Missing src prefix
```

## Testing Structure

```
tests/
├── unit/               # Unit tests (fast, isolated)
│   ├── test_validators.py
│   ├── test_cache.py (future)
│   ├── test_preprocessor.py (future)
│   └── ...
│
├── integration/        # Integration tests (slower, multi-component)
│   ├── test_data_pipeline.py (future)
│   ├── test_moirai_integration.py (future)
│   └── ...
│
└── fixtures/           # Shared test data
    └── sample_data.py (future)
```

## Configuration Hierarchy

```
1. Command-line arguments (future)
   ↓
2. Environment variables (.env)
   ↓
3. Config file (config/settings.yaml)
   ↓
4. Default values (in code)
```

## Data Flow (Phase 1)

```
User Input (CLI)
    ↓
Validate Input (validators)
    ↓
Check Cache (cache_manager)
    ├── Hit → Return cached data
    └── Miss ↓
         Fetch from Yahoo Finance (yahoo_finance)
            ↓
         Preprocess (preprocessor)
            ↓
         Add Features (feature_engineer)
            ↓
         Cache Result (cache_manager)
            ↓
         Display to User (CLI)
```

## Future Phases Structure

### Phase 2: Moirai Integration
```
src/moirai/
├── model_loader.py      # Load from HuggingFace
├── inference_engine.py  # Run inference
└── context_processor.py # Prepare context

src/core/
├── context_generator.py # Generate NL context
└── data_pipeline.py     # Orchestrate flow
```

### Phase 3: Sentiment Analysis
```
src/sentiment/
├── analyzer.py          # Main orchestrator
├── nlp_pipeline.py      # Text preprocessing
├── aggregator.py        # Multi-source aggregation
└── models/
    ├── finbert.py       # FinBERT model
    └── lexicon.py       # VADER fallback

src/data/sources/
├── news_collector.py    # News API
├── sec_edgar.py         # SEC filings
├── sebi_client.py       # SEBI filings
└── social_scraper.py    # Reddit/Twitter
```

### Phase 4: Regime Detection
```
src/regime/
├── detector.py          # Main orchestrator
├── transition_analyzer.py
└── methods/
    ├── volatility.py
    ├── trend.py
    ├── hmm.py
    └── context_driven.py
```

### Phase 5: Backtesting
```
src/backtesting/
├── engine.py            # Event-driven engine
├── portfolio.py         # Portfolio management
├── execution.py         # Order execution
├── metrics.py           # Performance metrics
└── strategies/
    ├── base.py
    ├── signal_based.py
    ├── mean_reversion.py
    └── regime_adaptive.py
```

---

## Quick Navigation

- **Start Here**: `README.md`, `QUICKSTART.md`
- **Implementation Details**: `IMPLEMENTATION_STATUS.md`
- **Run Application**: `python src/main.py`
- **Run Tests**: `python test_basic.py`
- **Configuration**: `config/settings.yaml`
- **Logs**: `storage/app.log`

---

**Last Updated**: March 10, 2026
**Phase 1 Status**: ✅ Complete
