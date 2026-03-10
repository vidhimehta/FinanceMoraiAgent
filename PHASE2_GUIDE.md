# Phase 2: Forecasting - User Guide 🚀

## What's New in Phase 2?

FinanceMoraiAgent now includes **AI-powered stock price forecasting**! You can now:

✅ Generate 7-day, 14-day, or 30-day forecasts
✅ Get confidence intervals (uncertainty bounds)
✅ Visualize forecasts with ASCII plots
✅ Export forecasts to CSV
✅ Use technical indicators as context for better predictions

---

## How to Use Forecasting

### Step 1: Start the Application

```bash
cd "/Users/vidhi.mehta/Desktop/Cursor Projects/FinanceMoraiAgent"
./venv/bin/python run.py
```

### Step 2: Select Option 4 (Generate Forecast)

You'll see it's now active (not "coming soon")!

```
Main Menu
──────────────────────────────────────────────────
  [1] Fetch Market Data
  [2] Sentiment Analysis.......... (Coming in Phase 3)
  [3] Regime Detection............ (Coming in Phase 4)
  [4] Generate Forecast........... AI-powered price forecasting ← NEW!
  [5] Run Backtest................ (Coming in Phase 5)
  [6] View Cache Stats
  [7] Settings
  [0] Exit
──────────────────────────────────────────────────
```

### Step 3: Follow the Prompts

**Example: Forecast Apple Stock for 30 Days**

```
Enter your choice: 4

Enter stock ticker: AAPL

Forecast Horizon:
  1. 7 days (1 week)
  2. 14 days (2 weeks)
  3. 30 days (1 month)
  4. Custom
Select horizon: 3

Lookback period (days of historical data): 90

Use technical indicators as context? (y/n): y

Generating 30-day forecast for AAPL...
```

### Step 4: View the Results

You'll see a detailed forecast table:

```
✓ Forecast generated successfully!

Forecast Summary: AAPL
┌──────────────────┬────────────────┐
│ Method           │ exponential_smoothing │
│ Horizon          │ 30 days        │
│ Confidence Level │ 80%            │
│                  │                │
│ Current Price    │ $165.42        │
│ Forecast (Final) │ $172.30        │
│ Expected Return  │ +4.16%         │
│ Min Forecast     │ $167.20        │
│ Max Forecast     │ $177.40        │
└──────────────────┴────────────────┘
```

### Step 5: View Visualization (Optional)

```
Show forecast plot? (y/n): y
```

You'll see an ASCII chart showing:
- Historical prices (last 30 days)
- Forecasted prices
- Upper and lower confidence bounds

### Step 6: Export (Optional)

```
Export forecast to CSV? (y/n): y

✓ Forecast exported to: storage/results/AAPL_forecast_20260310_141500.csv
```

---

## Forecasting Methods

### Current Method: Exponential Smoothing

Phase 2 uses **Holt's Exponential Smoothing** which:
- Captures both level and trend in the data
- Adapts quickly to recent changes
- Provides reliable short-term forecasts
- Includes confidence intervals based on historical volatility

**Best for:**
- Short to medium-term forecasts (7-30 days)
- Stocks with clear trends
- Quick predictions without heavy computation

### Future Enhancement: Moirai Model

Phase 2 is designed to support Salesforce's Moirai model (coming soon):
- Deep learning time-series model
- Context-aware predictions
- Better long-term accuracy
- Uses sentiment and regime information

---

## Understanding the Results

### Forecast Metrics Explained

**Current Price**
- Latest closing price from your data

**Forecast (Final)**
- Predicted price at the end of the horizon
- Example: If forecasting 30 days, this is the Day 30 prediction

**Expected Return**
- Percentage change from current to forecasted price
- Positive = price expected to rise
- Negative = price expected to fall

**Min/Max Forecast**
- Range of forecast values over the horizon
- Shows volatility in predictions

**Confidence Level**
- Default 80% means we're 80% confident the actual price will fall within the bounds
- You can interpret this as "4 out of 5 times, the price will be within these bounds"

### Forecast Preview Table

```
Date        Forecast    Lower Bound    Upper Bound
2026-03-11  $165.80     $163.20        $168.40
2026-03-12  $166.20     $162.50        $169.90
2026-03-13  $166.60     $161.80        $171.40
...
2026-04-09  $172.30     $157.50        $187.10
```

**Columns:**
- **Date**: Future trading day
- **Forecast**: Expected price
- **Lower Bound**: Lower confidence bound (worst case)
- **Upper Bound**: Upper confidence bound (best case)

**Note:** Bounds widen over time because uncertainty increases the further you forecast.

---

## Best Practices

### 1. Choose Appropriate Horizons

**7 days (1 week):**
- Most accurate
- Good for day trading decisions
- Narrow confidence bounds

**14 days (2 weeks):**
- Balance of accuracy and planning
- Good for swing trading

**30 days (1 month):**
- Longer-term view
- Wider confidence bounds
- Good for position trading

**Don't forecast > 30 days:**
- Statistical methods lose accuracy
- Too much uncertainty
- Use for reference only

### 2. Use Enough Historical Data

**Recommended lookback periods:**
- For 7-day forecast: 60-90 days
- For 14-day forecast: 90-120 days
- For 30-day forecast: 90-180 days

**Why?**
- More data = better trend detection
- Captures seasonality and patterns
- Improves confidence intervals

### 3. Enable Technical Context

Always say **Yes** to "Use technical indicators as context?"

**Benefits:**
- RSI, MACD, trend info helps prediction
- Better understands current market state
- More accurate forecasts

### 4. Compare Multiple Forecasts

Try forecasting the same stock with different settings:
- 7 days vs 30 days
- Different lookback periods
- With/without context

This gives you a better sense of the prediction range.

### 5. Use Confidence Bounds

**Don't just look at the forecast line!**

The confidence bounds tell you:
- How certain the forecast is
- Worst/best case scenarios
- Risk of holding the position

Example:
```
Forecast: $170
Lower: $155
Upper: $185
```
This means: Most likely $170, but could reasonably be anywhere from $155-$185.

---

## Examples

### Example 1: Day Trading (7-day forecast)

```
Ticker: AAPL
Horizon: 7 days
Lookback: 60 days
Context: Yes

Result:
Current: $165.42
Forecast Day 7: $168.20
Expected Return: +1.68%
Confidence: 80%

Interpretation: Slight upward trend expected this week.
```

### Example 2: Swing Trading (14-day forecast)

```
Ticker: MSFT
Horizon: 14 days
Lookback: 90 days
Context: Yes

Result:
Current: $430.25
Forecast Day 14: $445.80
Expected Return: +3.61%
Bounds: $425-$465

Interpretation: Strong upward momentum. Consider entry if RSI not overbought.
```

### Example 3: Position Trading (30-day forecast)

```
Ticker: TCS.NS
Horizon: 30 days
Lookback: 120 days
Context: Yes

Result:
Current: ₹2527
Forecast Day 30: ₹2680
Expected Return: +6.06%
Bounds: ₹2400-₹2950

Interpretation: Bullish outlook, but wide bounds suggest holding risk.
```

---

## Tips for Indian Stocks

**Works great with NSE/BSE stocks!**

Popular tickers to try:
- TCS.NS - Tata Consultancy Services
- RELIANCE.NS - Reliance Industries
- INFY.NS - Infosys
- HDFCBANK.NS - HDFC Bank
- WIPRO.NS - Wipro

**Same process:**
1. Enter ticker with .NS or .BO suffix
2. Choose horizon
3. Get forecast in ₹ (Rupees)

---

## Troubleshooting

### Issue: "Not enough data"
**Solution:** Increase lookback period or choose earlier date range

### Issue: Forecast seems too volatile
**Solution:** 
- Increase lookback period for smoother trend
- Check if stock had major events (earnings, splits)
- Consider shorter horizon

### Issue: Very wide confidence bounds
**Solution:**
- Normal for longer horizons (30 days)
- Stock might be highly volatile
- Use shorter horizon for tighter bounds

### Issue: Export fails
**Solution:**
- Check if storage/results directory exists
- Ensure write permissions
- Close any open CSV files with same name

---

## What's Coming Next

### Phase 3: Sentiment Analysis
- News sentiment integration
- SEC/SEBI filing analysis
- Social media sentiment
- Context-enhanced forecasts

### Phase 4: Regime Detection
- Bull/bear market detection
- Volatility regime identification
- Regime-adaptive forecasting

### Phase 5: Backtesting
- Test forecast accuracy historically
- Strategy development
- Performance metrics

---

## Technical Details

### Exponential Smoothing Algorithm

```
Level[t] = α × Price[t] + (1-α) × (Level[t-1] + Trend[t-1])
Trend[t] = β × (Level[t] - Level[t-1]) + (1-β) × Trend[t-1]
Forecast[t+h] = Level[t] + h × Trend[t]
```

Where:
- α (alpha) = 0.3 (level smoothing)
- β (beta) = 0.1 (trend smoothing)
- h = forecast horizon

### Confidence Intervals

Based on historical volatility:
```
Uncertainty[h] = Forecast[h] × σ × √h × z
```

Where:
- σ = Standard deviation of returns
- h = Periods ahead
- z = Z-score (1.28 for 80% confidence)

---

## Files Created in Phase 2

```
src/moirai/
├── model_loader.py          # Model management
├── inference_engine.py      # Forecast generation
└── context_processor.py     # Context formatting

src/core/
└── data_pipeline.py         # Data orchestration

src/cli/commands/
└── forecast_cmd.py          # CLI forecast interface
```

---

## Quick Reference

```bash
# Start application
./venv/bin/python run.py

# Select option 4
# Enter ticker (AAPL, MSFT, TCS.NS, etc.)
# Choose horizon (1-4)
# Set lookback (60-180 days recommended)
# Enable context (recommended)
# View results
# Optional: plot and export
```

**Enjoy forecasting! 📈**
