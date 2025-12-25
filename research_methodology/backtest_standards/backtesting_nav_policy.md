# Backtesting NAV Policy (백테스트 NAV 계산 정책)

**Last Updated**: 2025-12-23
**Source**: User requirement (accurate MDD/metrics)
**Importance**: ⭐⭐⭐ Critical - 잘못된 NAV = 잘못된 MDD/Sharpe

---

## Problem Statement

**현재 문제**:
- 포지션 진입/청산 시점에만 NAV 계산
- 중간에 Mark-to-Market (MTM) 평가 안 함
- **결과**: MDD = 0, Sharpe 과대평가, 비현실적 메트릭

**예시**:
```python
# ❌ Bad (진입/청산만 평가)
t=0:  Entry position, NAV = 100,000
t=1:  (no evaluation)
t=2:  (no evaluation)
t=3:  Close position, NAV = 105,000

Result: MDD = 0% (wrong!)
Actual: t=1에서 -10% drawdown 발생했을 수 있음
```

**목표**:
- **Hourly MTM** (또는 최소 daily)
- 실제 intraday drawdown 포착
- 정확한 MDD, Sharpe, 변동성 계산

---

## Mandatory Policy (필수 정책)

### 1. NAV 계산 빈도

**MUST**: Hourly 또는 Daily NAV 계산 (매 timestep)

```python
# ✅ Good (hourly MTM)
for timestamp in hourly_timestamps:
    nav = calculate_nav_mtm(timestamp, portfolio, market_data)
    nav_series[timestamp] = nav
```

**Frequency 선택**:

| Strategy Type | Recommended Frequency | Reason |
|--------------|----------------------|--------|
| Options strategies | **Hourly** | Greeks change rapidly |
| High-frequency trading | **Every tick/minute** | Intraday volatility |
| Daily rebalancing | **Daily** | Acceptable (close only) |
| Low-frequency | **Daily** | Minimum requirement |

**Default**: **Hourly** (unless strategy logic is purely daily)

---

### 2. Mark-to-Market (MTM) Calculation

**Definition**: 모든 포지션을 현재 시장 가격으로 평가

```python
def calculate_nav_mtm(timestamp, portfolio, market_data):
    """
    Calculate NAV with Mark-to-Market at specific timestamp.

    Args:
        timestamp: Current time
        portfolio: Current positions and cash
        market_data: Market prices at timestamp

    Returns:
        nav: Net Asset Value (Mark-to-Market)
    """
    # 1. Start with cash
    nav = portfolio.cash

    # 2. Add realized PnL (already in cash)
    # (No-op, already included in cash)

    # 3. Add unrealized PnL (MTM all positions)
    for position in portfolio.positions:
        # Get current mark price
        if position.instrument_type == 'option':
            # Options: Use mark price (NOT bid/ask)
            mark_price = market_data.loc[timestamp, f"{position.symbol}_mark"]
            current_value = position.quantity * mark_price * position.multiplier

        elif position.instrument_type == 'future':
            # Futures: Use last price or mark price
            mark_price = market_data.loc[timestamp, position.symbol]
            current_value = position.quantity * mark_price * position.multiplier

        elif position.instrument_type == 'spot':
            # Spot: Simple
            current_price = market_data.loc[timestamp, position.symbol]
            current_value = position.quantity * current_price

        else:
            raise ValueError(f"Unknown instrument type: {position.instrument_type}")

        # Calculate unrealized PnL
        entry_value = position.quantity * position.entry_price * position.multiplier
        unrealized_pnl = current_value - entry_value

        nav += unrealized_pnl

    return nav
```

**CRITICAL**:
- Use **mark price** for options (NOT bid/ask, NOT last trade)
- Use **mark price or last** for futures
- Include **ALL open positions**
- Calculate at **every timestep** (not just on trades)

---

### 3. Hourly → Daily Resampling

**MUST**: Resample hourly NAV to daily before calculating metrics

```python
# Step 1: Calculate hourly NAV
nav_hourly = pd.Series(index=hourly_timestamps, dtype=float)
for ts in hourly_timestamps:
    nav_hourly[ts] = calculate_nav_mtm(ts, portfolio, market_data)

# Step 2: Resample to daily (take last value of each day)
nav_daily = nav_hourly.resample('D').last()

# Step 3: Calculate metrics from daily NAV
sharpe = calculate_sharpe(nav_daily)
mdd, mdd_dur, recovery = calculate_mdd(nav_daily)
volatility = calculate_volatility(nav_daily)
```

**Why resample?**:
- Hourly returns too noisy for annualization
- Daily returns standard for Sharpe/Sortino
- MDD calculation stable at daily frequency

---

## Implementation Examples

### Example 1: Options Backtest (Hourly MTM)

```python
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class OptionsBacktester:
    def __init__(self, initial_capital=100000):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.positions = []
        self.nav_series = pd.Series(dtype=float)

    def run(self, strategy, market_data):
        """
        Run backtest with hourly NAV calculation.

        Args:
            strategy: Strategy object (with signal generation)
            market_data: DataFrame with hourly OHLC + mark prices

        Returns:
            nav_series: Hourly NAV time series
        """
        # Get all hourly timestamps
        timestamps = market_data.index

        for timestamp in timestamps:
            # 1. Calculate NAV (Mark-to-Market)
            nav = self._calculate_nav_mtm(timestamp, market_data)
            self.nav_series[timestamp] = nav

            # 2. Generate signals (strategy logic)
            signals = strategy.generate_signals(timestamp, market_data, self.positions)

            # 3. Execute trades
            for signal in signals:
                self._execute_trade(signal, timestamp, market_data)

            # 4. Check expirations (options only)
            self._process_expirations(timestamp, market_data)

            # 5. Log state
            if timestamp.hour == 0:  # Daily log
                print(f"{timestamp.date()}: NAV = ${nav:,.2f}, Positions = {len(self.positions)}")

        return self.nav_series

    def _calculate_nav_mtm(self, timestamp, market_data):
        """Calculate NAV with Mark-to-Market."""
        nav = self.cash

        for position in self.positions:
            # Get mark price
            symbol = position.symbol
            mark_col = f"{symbol}_mark"

            if mark_col not in market_data.columns:
                raise ValueError(f"Mark price column {mark_col} not found")

            mark_price = market_data.loc[timestamp, mark_col]

            # Current value
            current_value = position.quantity * mark_price

            # Entry value (for unrealized PnL)
            entry_value = position.quantity * position.entry_price

            # Unrealized PnL
            unrealized_pnl = current_value - entry_value

            nav += unrealized_pnl

        return nav

    def _execute_trade(self, signal, timestamp, market_data):
        """Execute trade and update portfolio."""
        # Implementation...
        pass

    def _process_expirations(self, timestamp, market_data):
        """Check and process option expirations."""
        # Check if any options expire today
        for position in self.positions[:]:  # Copy to allow removal
            if position.expiry_date == timestamp.date():
                # Settlement
                settlement_price = market_data.loc[timestamp, 'index_price']
                intrinsic = self._calculate_intrinsic(position, settlement_price)

                # Settle position
                self.cash += intrinsic * position.quantity
                self.positions.remove(position)

                print(f"EXPIRED: {position.symbol} @ {settlement_price}, Intrinsic = {intrinsic}")

    def get_metrics(self):
        """Calculate performance metrics from hourly NAV."""
        # Resample to daily
        nav_daily = self.nav_series.resample('D').last()

        # Calculate metrics
        from performance_metrics import calculate_all_metrics
        metrics = calculate_all_metrics(nav_daily, risk_free_rate=0.0)

        return metrics
```

### Example 2: Market Making (Minute MTM)

```python
class MarketMakerBacktester:
    def __init__(self, initial_capital=100000):
        self.cash = initial_capital
        self.inventory = 0  # Current inventory (positive = long, negative = short)
        self.nav_series = pd.Series(dtype=float)

    def run(self, strategy, market_data):
        """
        Run market making backtest with minute-level NAV.

        Args:
            market_data: DataFrame with minute OHLC + depth
        """
        for timestamp in market_data.index:
            # 1. Calculate NAV (MTM inventory)
            nav = self._calculate_nav_mtm(timestamp, market_data)
            self.nav_series[timestamp] = nav

            # 2. Update quotes
            bid, ask = strategy.calculate_quotes(timestamp, market_data, self.inventory)

            # 3. Simulate fills
            fills = self._simulate_fills(bid, ask, timestamp, market_data)

            # 4. Update inventory and cash
            for fill in fills:
                self.inventory += fill.quantity * (1 if fill.side == 'buy' else -1)
                self.cash -= fill.price * fill.quantity * (1 if fill.side == 'buy' else -1)

        return self.nav_series

    def _calculate_nav_mtm(self, timestamp, market_data):
        """Calculate NAV = Cash + Inventory MTM."""
        nav = self.cash

        if self.inventory != 0:
            # MTM inventory at mid price
            mid_price = (market_data.loc[timestamp, 'bid'] + market_data.loc[timestamp, 'ask']) / 2
            inventory_value = self.inventory * mid_price
            nav += inventory_value

        return nav
```

### Example 3: Long-Short Equity (Daily MTM)

```python
class LongShortBacktester:
    def __init__(self, initial_capital=1000000):
        self.cash = initial_capital
        self.positions = {}  # {symbol: quantity}
        self.nav_series = pd.Series(dtype=float)

    def run(self, strategy, market_data):
        """
        Run long-short backtest with daily NAV.

        Args:
            market_data: DataFrame with daily OHLC
        """
        for date in market_data.index:
            # 1. Calculate NAV (MTM all positions)
            nav = self._calculate_nav_mtm(date, market_data)
            self.nav_series[date] = nav

            # 2. Generate signals (daily rebalance)
            signals = strategy.generate_signals(date, market_data)

            # 3. Execute rebalancing
            self._rebalance(signals, date, market_data)

        return self.nav_series

    def _calculate_nav_mtm(self, date, market_data):
        """Calculate NAV = Cash + Positions MTM."""
        nav = self.cash

        for symbol, quantity in self.positions.items():
            if quantity != 0:
                # Get close price
                close_price = market_data.loc[date, (symbol, 'close')]
                position_value = quantity * close_price
                nav += position_value

        return nav
```

---

## Common Mistakes (자주 하는 실수)

### ❌ Mistake 1: Entry/Exit만 평가

```python
# Bad (only on trades)
def execute_trade(signal):
    # Enter position
    nav = calculate_nav()  # ❌ Only here
    nav_series.append(nav)

# Result: MDD = 0 (no intraday evaluation)
```

**Fix**:
```python
# Good (every timestep)
for timestamp in all_timestamps:
    nav = calculate_nav_mtm(timestamp)  # ✅ Always
    nav_series[timestamp] = nav

    # Then execute trades
    if has_signal(timestamp):
        execute_trade()
```

---

### ❌ Mistake 2: Bid/Ask 대신 Last Price 사용

```python
# Bad (last trade price)
mark_price = market_data.loc[timestamp, 'last']  # ❌ Stale
current_value = position.quantity * mark_price
```

**Fix**:
```python
# Good (mark price)
mark_price = market_data.loc[timestamp, 'mark']  # ✅ Current fair value
current_value = position.quantity * mark_price
```

---

### ❌ Mistake 3: Hourly NAV로 바로 Sharpe 계산

```python
# Bad (hourly returns → annual Sharpe)
returns_hourly = nav_hourly.pct_change()
sharpe = returns_hourly.mean() / returns_hourly.std() * np.sqrt(365*24)  # ❌ Too noisy
```

**Fix**:
```python
# Good (resample to daily first)
nav_daily = nav_hourly.resample('D').last()  # ✅ Daily NAV
returns_daily = nav_daily.pct_change()
sharpe = (returns_daily.mean() * 365) / (returns_daily.std() * np.sqrt(365))
```

---

### ❌ Mistake 4: Unrealized PnL 누락

```python
# Bad (only realized PnL)
nav = cash + realized_pnl  # ❌ Missing open positions
```

**Fix**:
```python
# Good (realized + unrealized)
nav = cash + realized_pnl + unrealized_pnl  # ✅ MTM all positions
```

---

### ❌ Mistake 5: 만기일 처리 안 함 (옵션)

```python
# Bad (expired options still in portfolio)
for position in positions:
    nav += position.current_value  # ❌ Expired option = 0 value, not last mark
```

**Fix**:
```python
# Good (check expiry)
for position in positions:
    if position.expiry_date < today:
        # Already settled, value = 0
        continue
    else:
        nav += position.current_value_mtm  # ✅ Only live positions
```

---

## Validation Checklist

**BEFORE reporting backtest results**:

- [ ] ✅ NAV calculated at **every timestep** (hourly or daily)
- [ ] ✅ **Mark-to-Market** used (not last trade, not bid/ask)
- [ ] ✅ **All open positions** included in NAV
- [ ] ✅ Expired options **excluded** from NAV
- [ ] ✅ Hourly NAV **resampled to daily** for metrics
- [ ] ✅ NAV series **length matches** backtest period (no gaps)
- [ ] ✅ Initial NAV = Initial Capital (sanity check)
- [ ] ✅ Final NAV = Cash + Positions MTM (reconciled)

**Sanity checks**:

```python
# 1. NAV never negative (unless leverage allowed)
assert (nav_series >= 0).all() or leverage_allowed

# 2. NAV has values for all days
expected_days = (end_date - start_date).days
actual_days = len(nav_daily)
assert actual_days >= expected_days * 0.95  # Allow 5% holiday gaps

# 3. MDD is not zero (unless perfect strategy)
mdd = calculate_mdd(nav_daily)
if mdd == 0 and len(trades) > 0:
    raise ValueError("MDD = 0 with trades → Missing MTM evaluation!")

# 4. NAV series starts at initial capital
assert abs(nav_series.iloc[0] - initial_capital) < 1e-6
```

---

## Agent Protocol: NAV Calculation

### BEFORE starting backtest:

1. ✅ Read this policy (`backtesting_nav_policy.md`)
2. ✅ Determine NAV frequency:
   - Options/HFT → Hourly
   - Daily strategies → Daily (minimum)
3. ✅ Ensure market data has **mark prices** (or can calculate)
4. ✅ Initialize NAV series with correct index

### DURING backtest:

5. ✅ Calculate NAV at **every timestep** (BEFORE trade execution)
6. ✅ Use Mark-to-Market for all positions
7. ✅ Include unrealized PnL
8. ✅ Handle expirations correctly
9. ✅ Log NAV to series (timestamp → value)

### AFTER backtest:

10. ✅ Resample hourly → daily (if hourly)
11. ✅ Validate NAV series (sanity checks above)
12. ✅ Calculate metrics from daily NAV
13. ✅ Check MDD ≠ 0 (if trades occurred)

### Example Dialogue:

```
User: "백테스트 결과 MDD가 0이라고 나와"

Agent:
  [Reads backtesting_nav_policy.md]

  "MDD = 0 문제 진단:

  ❌ 원인: NAV를 포지션 진입/청산 시점에만 계산
     → 중간 drawdown 포착 못함

  ✅ 해결책:

  1. Hourly NAV 계산 (Mark-to-Market):
     for timestamp in hourly_timestamps:
         nav = calculate_nav_mtm(timestamp, portfolio, market_data)
         nav_series[timestamp] = nav

  2. Daily resample:
     nav_daily = nav_hourly.resample('D').last()

  3. MDD 재계산:
     mdd, mdd_dur, recovery = calculate_mdd(nav_daily)

  예상 결과:
    - MDD: -8% ~ -15% (realistic)
    - Sharpe: 2.4 → 1.8 (하락, 더 정확)
    - Volatility: 3% → 12% (증가, 실제 변동성)

  📚 출처: knowledge/experiments/backtesting_nav_policy.md

  코드 수정할까요?"
```

---

## Performance Impact

**Concern**: "Hourly NAV 계산하면 느려지지 않나요?"

**Answer**: Minimal impact if implemented correctly

```python
# Efficient implementation
def calculate_nav_series(timestamps, portfolio, market_data):
    """
    Vectorized NAV calculation.

    Args:
        timestamps: All timestamps
        portfolio: Portfolio object with position tracking
        market_data: DataFrame with mark prices

    Returns:
        nav_series: Hourly NAV (fast)
    """
    # Pre-allocate
    nav_series = pd.Series(index=timestamps, dtype=float)

    # Get cash time series (from trades)
    cash_series = portfolio.get_cash_series(timestamps)

    # Get unrealized PnL time series (vectorized)
    unrealized_pnl_series = portfolio.calculate_unrealized_pnl_series(
        timestamps,
        market_data
    )

    # Combine (vectorized)
    nav_series = cash_series + unrealized_pnl_series

    return nav_series
```

**Benchmark**:
- Naive loop: ~5 seconds for 1000 hours
- Vectorized: ~0.05 seconds for 1000 hours ✅

**Optimization tips**:
1. Use vectorized operations (pandas/numpy)
2. Pre-load mark prices (don't query per timestamp)
3. Cache position values (only recalculate on trade)
4. Use `.loc` indexing (not `.iloc` loops)

---

## Related Policies

**See also**:
- [Performance Metrics](performance_metrics.md) - How to calculate Sharpe, MDD from NAV
- [Backtesting Integrity](backtesting_integrity.md) - Trade-by-trade reconciliation
- [Common Pitfalls](common_pitfalls.md) - Look-ahead bias, overfitting

**Integration**:
```python
# 1. Calculate NAV (this policy)
nav_hourly = calculate_nav_series_hourly(...)
nav_daily = nav_hourly.resample('D').last()

# 2. Calculate metrics (performance_metrics.md)
from performance_metrics import calculate_all_metrics
metrics = calculate_all_metrics(nav_daily, risk_free_rate=0.0)

# 3. Reconcile (backtesting_integrity.md)
reconcile_nav_with_trades(nav_series, trades, positions)
```

---

## References

- **User Requirement**: "hourly MTM, daily resample for metrics"
- **Related KB**:
  - [Performance Metrics](performance_metrics.md) - Sharpe, MDD calculation
  - [Backtesting Integrity](backtesting_integrity.md) - PnL reconciliation
- **Why hourly**: Captures intraday drawdowns (critical for options)
- **Why daily resample**: Standard for annualized metrics

---

**Version**: 1.0
**Critical**: Hourly MTM → Daily resample → Metrics. 안 하면 MDD = 0.
