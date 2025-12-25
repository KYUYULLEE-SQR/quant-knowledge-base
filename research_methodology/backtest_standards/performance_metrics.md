# Performance Metrics Calculation Standards

**Last Updated**: 2025-12-23
**Source**: User requirement (correct annualization for crypto)
**Importance**: ⭐⭐⭐ Critical - 잘못된 계산 = 잘못된 의사결정

---

## Overview

**Problem**: 전통 금융 시장 기준(255일)으로 계산하면 crypto 전략 성과 왜곡

**Solution**: 365일 기준 연율화 + Mark-to-Market NAV

**Critical**:
- ❌ 255일 annualization (전통 시장)
- ❌ Hourly returns 직접 annualization
- ✅ 365일 annualization (crypto 24/7)
- ✅ Hourly/Daily NAV → Daily resample → Annualize

---

## Standard Calculation Pipeline

```python
# Standard workflow
Step 1: Calculate NAV (Mark-to-Market) at every timestep (hourly or daily)
Step 2: Resample to daily (if using hourly data)
Step 3: Calculate daily returns
Step 4: Annualize metrics using 365-day factor
```

---

## 1. NAV Calculation (Mark-to-Market)

### Definition

**NAV (Net Asset Value)** = 특정 시점의 전체 자산 가치

```python
NAV = Cash + Unrealized PnL + Realized PnL
    = Initial Capital + Cumulative PnL

# Mark-to-Market (MTM)
Unrealized PnL = sum(position * (current_price - entry_price))
```

### Implementation

```python
def calculate_nav(timestamp, portfolio, market_data):
    """
    Calculate NAV at specific timestamp (Mark-to-Market).

    Args:
        timestamp: Current time
        portfolio: Current positions and cash
        market_data: Current market prices

    Returns:
        nav: Net Asset Value
    """
    cash = portfolio.cash

    # Mark all positions to market
    unrealized_pnl = 0
    for position in portfolio.positions:
        current_price = market_data.loc[timestamp, position.symbol]

        if position.instrument_type == 'option':
            # Options: Use mark price (not bid/ask)
            mark_price = market_data.loc[timestamp, f"{position.symbol}_mark"]
            position_value = position.quantity * mark_price * position.multiplier
        else:
            # Futures/Spot: Use last price or mid
            position_value = position.quantity * current_price

        entry_value = position.quantity * position.entry_price
        unrealized_pnl += (position_value - entry_value)

    nav = cash + unrealized_pnl

    return nav

# Generate NAV time series
nav_series = pd.Series(index=timestamps, dtype=float)
for ts in timestamps:
    nav_series[ts] = calculate_nav(ts, portfolio, market_data)
```

### Frequency

**Recommended**:
- **High-frequency strategies**: Hourly NAV
- **Daily strategies**: Daily NAV (at consistent time, e.g., UTC 00:00)
- **Options strategies**: Hourly NAV (Greeks change rapidly)

---

## 2. Daily Resampling

### Why Resample?

**Hourly returns → too noisy for annualization**
- Intraday volatility ≠ daily volatility
- Sharpe ratio unstable with hourly data

**Solution**: Resample to daily, then annualize

### Implementation

```python
# If NAV is hourly
nav_hourly = pd.Series(...)  # Hourly NAV

# Resample to daily (take last value of each day)
nav_daily = nav_hourly.resample('D').last()

# Or if you want specific hour (e.g., UTC 00:00)
nav_daily = nav_hourly.resample('D', offset='0h').first()
```

---

## 3. Annualization Factor

### Critical Rule

**Crypto markets trade 24/7** → **365 days per year**

```python
ANNUALIZATION_FACTOR = 365  # NOT 252, NOT 255
```

**❌ Wrong (Traditional markets)**:
```python
DAYS_PER_YEAR = 252  # US stock market trading days
DAYS_PER_YEAR = 255  # Some international markets
```

**✅ Correct (Crypto)**:
```python
DAYS_PER_YEAR = 365  # Crypto markets never close
```

---

## 4. Sharpe Ratio

### Definition

**Sharpe Ratio** = 위험 대비 초과 수익률

```
Sharpe = (Mean Return - Risk-Free Rate) / Std Dev of Returns
```

**Annualized**:
```
Sharpe (annualized) = (Mean Daily Return * 365 - RFR) / (Std Daily Return * sqrt(365))
```

### Implementation

```python
def calculate_sharpe(nav_daily, risk_free_rate=0.0):
    """
    Calculate annualized Sharpe ratio.

    Args:
        nav_daily: Daily NAV series
        risk_free_rate: Annual risk-free rate (default 0 for crypto)

    Returns:
        sharpe: Annualized Sharpe ratio
    """
    # Calculate daily returns
    returns_daily = nav_daily.pct_change().dropna()

    if len(returns_daily) == 0:
        return 0.0

    # Mean and std of daily returns
    mean_daily_return = returns_daily.mean()
    std_daily_return = returns_daily.std()

    if std_daily_return == 0:
        return 0.0

    # Annualize (365 days)
    annual_return = mean_daily_return * 365
    annual_volatility = std_daily_return * np.sqrt(365)

    # Risk-free rate (already annualized)
    sharpe = (annual_return - risk_free_rate) / annual_volatility

    return sharpe

# Example
nav_daily = pd.Series([100000, 100500, 101000, 100800, 101500, ...])
sharpe = calculate_sharpe(nav_daily, risk_free_rate=0.0)
print(f"Sharpe Ratio: {sharpe:.2f}")
```

### Interpretation

| Sharpe | Quality |
|--------|---------|
| < 0 | Losing money |
| 0 - 1 | Sub-par |
| 1 - 2 | Good |
| 2 - 3 | Very good |
| > 3 | Excellent (verify for bugs!) |

---

## 5. Sortino Ratio

### Definition

**Sortino Ratio** = Sharpe와 유사하지만, **하방 변동성만** 패널티

```
Sortino = (Mean Return - Target) / Downside Deviation
```

**Downside Deviation** = 목표 이하 수익률의 표준편차

### Implementation

```python
def calculate_sortino(nav_daily, target_return=0.0, risk_free_rate=0.0):
    """
    Calculate annualized Sortino ratio.

    Args:
        nav_daily: Daily NAV series
        target_return: Minimum acceptable return (annualized)
        risk_free_rate: Annual risk-free rate

    Returns:
        sortino: Annualized Sortino ratio
    """
    # Daily returns
    returns_daily = nav_daily.pct_change().dropna()

    if len(returns_daily) == 0:
        return 0.0

    # Convert target return to daily
    target_daily = target_return / 365

    # Downside returns (below target)
    downside_returns = returns_daily[returns_daily < target_daily]

    if len(downside_returns) == 0:
        # No downside → infinite Sortino (cap at 10)
        return 10.0

    # Downside deviation
    downside_std = downside_returns.std()

    if downside_std == 0:
        return 0.0

    # Annualize
    mean_daily_return = returns_daily.mean()
    annual_return = mean_daily_return * 365
    annual_downside_std = downside_std * np.sqrt(365)

    sortino = (annual_return - risk_free_rate) / annual_downside_std

    return sortino

# Example
sortino = calculate_sortino(nav_daily, target_return=0.0)
print(f"Sortino Ratio: {sortino:.2f}")
```

### Interpretation

**Sortino > Sharpe** → Upside volatility > Downside volatility (좋음)
**Sortino < Sharpe** → Downside volatility > Upside volatility (나쁨)

---

## 6. Maximum Drawdown (MDD)

### Definition

**MDD** = 최고점 대비 최대 하락폭 (%)

```
MDD = max(Peak - Trough) / Peak
```

### Implementation

```python
def calculate_mdd(nav_daily):
    """
    Calculate Maximum Drawdown.

    Args:
        nav_daily: Daily NAV series

    Returns:
        mdd: Maximum Drawdown (negative value, e.g., -0.15 = -15%)
        mdd_duration: Days from peak to trough
        recovery_duration: Days from trough to recovery (or None if not recovered)
    """
    # Calculate running maximum
    running_max = nav_daily.expanding().max()

    # Calculate drawdown at each point
    drawdown = (nav_daily - running_max) / running_max

    # Maximum drawdown (most negative value)
    mdd = drawdown.min()

    # Find MDD period
    mdd_end_idx = drawdown.idxmin()
    mdd_end_date = drawdown.index[drawdown.idxmin()]

    # Find peak before MDD
    peak_idx = running_max[:mdd_end_date].idxmax()
    peak_date = running_max[:mdd_end_date].index[running_max[:mdd_end_date].idxmax()]

    # Drawdown duration
    mdd_duration = (mdd_end_date - peak_date).days

    # Recovery (if any)
    peak_value = nav_daily[peak_date]
    recovery_dates = nav_daily[mdd_end_date:][nav_daily[mdd_end_date:] >= peak_value]

    if len(recovery_dates) > 0:
        recovery_date = recovery_dates.index[0]
        recovery_duration = (recovery_date - mdd_end_date).days
    else:
        recovery_duration = None  # Not recovered yet

    return mdd, mdd_duration, recovery_duration

# Example
mdd, mdd_dur, recovery_dur = calculate_mdd(nav_daily)
print(f"Max Drawdown: {mdd:.2%}")
print(f"Drawdown Duration: {mdd_dur} days")
print(f"Recovery Duration: {recovery_dur} days" if recovery_dur else "Not recovered")
```

### Interpretation

| MDD | Tolerance |
|-----|-----------|
| > -5% | Very low risk |
| -5% to -10% | Low risk |
| -10% to -20% | Moderate risk |
| -20% to -30% | High risk |
| < -30% | Very high risk |

---

## 7. Volatility (Annualized)

### Definition

**Volatility** = 수익률의 표준편차 (연율화)

```
Volatility (annualized) = Std(Daily Returns) * sqrt(365)
```

### Implementation

```python
def calculate_volatility(nav_daily):
    """
    Calculate annualized volatility.

    Args:
        nav_daily: Daily NAV series

    Returns:
        volatility: Annualized volatility (e.g., 0.25 = 25% annual vol)
    """
    # Daily returns
    returns_daily = nav_daily.pct_change().dropna()

    if len(returns_daily) == 0:
        return 0.0

    # Std of daily returns
    std_daily = returns_daily.std()

    # Annualize (365 days)
    annual_volatility = std_daily * np.sqrt(365)

    return annual_volatility

# Example
vol = calculate_volatility(nav_daily)
print(f"Annualized Volatility: {vol:.2%}")
```

### Interpretation

| Volatility | Strategy Type |
|-----------|---------------|
| < 10% | Very low risk (arbitrage, market making) |
| 10-20% | Low-moderate risk (delta-neutral) |
| 20-40% | Moderate-high risk (directional) |
| > 40% | High risk (leveraged, options) |

---

## 8. Returns (Annualized)

### Definition

**Return** = 기간 동안 수익률 (연율화)

```
Annualized Return = (Final NAV / Initial NAV) ^ (365 / Days) - 1
```

### Implementation

```python
def calculate_returns(nav_daily):
    """
    Calculate annualized return.

    Args:
        nav_daily: Daily NAV series

    Returns:
        total_return: Total return (e.g., 0.50 = 50%)
        annualized_return: Annualized return (CAGR)
        daily_return: Average daily return
    """
    if len(nav_daily) < 2:
        return 0.0, 0.0, 0.0

    # Total return
    initial_nav = nav_daily.iloc[0]
    final_nav = nav_daily.iloc[-1]
    total_return = (final_nav / initial_nav) - 1

    # Days
    days = (nav_daily.index[-1] - nav_daily.index[0]).days

    if days == 0:
        return total_return, 0.0, 0.0

    # Annualized return (CAGR)
    annualized_return = (final_nav / initial_nav) ** (365 / days) - 1

    # Average daily return
    returns_daily = nav_daily.pct_change().dropna()
    daily_return = returns_daily.mean()

    return total_return, annualized_return, daily_return

# Example
total_ret, annual_ret, daily_ret = calculate_returns(nav_daily)
print(f"Total Return: {total_ret:.2%}")
print(f"Annualized Return (CAGR): {annual_ret:.2%}")
print(f"Average Daily Return: {daily_ret:.4%}")
```

---

## 9. Complete Metrics Function

### All-in-One

```python
def calculate_all_metrics(nav_daily, risk_free_rate=0.0):
    """
    Calculate all standard performance metrics.

    Args:
        nav_daily: Daily NAV series
        risk_free_rate: Annual risk-free rate (default 0)

    Returns:
        dict: All metrics
    """
    import numpy as np
    import pandas as pd

    # Returns
    total_ret, annual_ret, daily_ret = calculate_returns(nav_daily)

    # Sharpe
    sharpe = calculate_sharpe(nav_daily, risk_free_rate)

    # Sortino
    sortino = calculate_sortino(nav_daily, risk_free_rate=risk_free_rate)

    # MDD
    mdd, mdd_dur, recovery_dur = calculate_mdd(nav_daily)

    # Volatility
    vol = calculate_volatility(nav_daily)

    # Additional metrics
    returns_daily = nav_daily.pct_change().dropna()
    win_rate = (returns_daily > 0).sum() / len(returns_daily) if len(returns_daily) > 0 else 0

    metrics = {
        'total_return': total_ret,
        'annualized_return': annual_ret,
        'sharpe_ratio': sharpe,
        'sortino_ratio': sortino,
        'max_drawdown': mdd,
        'mdd_duration_days': mdd_dur,
        'recovery_duration_days': recovery_dur,
        'annualized_volatility': vol,
        'daily_return_mean': daily_ret,
        'daily_return_std': returns_daily.std() if len(returns_daily) > 0 else 0,
        'win_rate': win_rate,
        'total_days': (nav_daily.index[-1] - nav_daily.index[0]).days,
    }

    return metrics

# Example usage
metrics = calculate_all_metrics(nav_daily, risk_free_rate=0.0)

# Save to JSON
import json
with open('results/metrics.json', 'w') as f:
    # Convert numpy types to native Python
    metrics_serializable = {k: float(v) if v is not None else None
                           for k, v in metrics.items()}
    json.dump(metrics_serializable, f, indent=2)

# Print table
print("\n=== Performance Metrics ===")
print(f"Total Return:        {metrics['total_return']:>8.2%}")
print(f"Annualized Return:   {metrics['annualized_return']:>8.2%}")
print(f"Sharpe Ratio:        {metrics['sharpe_ratio']:>8.2f}")
print(f"Sortino Ratio:       {metrics['sortino_ratio']:>8.2f}")
print(f"Max Drawdown:        {metrics['max_drawdown']:>8.2%}")
print(f"Volatility (Annual): {metrics['annualized_volatility']:>8.2%}")
print(f"Win Rate:            {metrics['win_rate']:>8.2%}")
```

---

## 10. Common Mistakes

### ❌ Mistake 1: Wrong Annualization Factor

```python
# Bad (Traditional markets)
annual_return = daily_return * 252  # WRONG for crypto

# Good (Crypto 24/7)
annual_return = daily_return * 365  # CORRECT
```

### ❌ Mistake 2: Hourly → Annual Direct

```python
# Bad (Too noisy)
returns_hourly = nav_hourly.pct_change()
sharpe = returns_hourly.mean() / returns_hourly.std() * np.sqrt(365*24)  # WRONG

# Good (Resample first)
nav_daily = nav_hourly.resample('D').last()
returns_daily = nav_daily.pct_change()
sharpe = (returns_daily.mean() * 365) / (returns_daily.std() * np.sqrt(365))  # CORRECT
```

### ❌ Mistake 3: Not Using Mark-to-Market

```python
# Bad (Only realized PnL)
nav = cash + realized_pnl  # WRONG (ignores open positions)

# Good (MTM)
nav = cash + realized_pnl + unrealized_pnl  # CORRECT
```

### ❌ Mistake 4: Ignoring Fees in NAV

```python
# Bad
nav = cash + positions_value  # WRONG (fees not deducted)

# Good
nav = cash - cumulative_fees + positions_value  # CORRECT
```

### ❌ Mistake 5: MDD from Equity, Not NAV

```python
# Bad (Using equity curve, not NAV)
equity = cumulative_pnl  # Starts at 0
mdd = equity.min() / equity.max()  # WRONG

# Good (Using NAV)
nav = initial_capital + cumulative_pnl  # Starts at initial capital
running_max = nav.expanding().max()
mdd = ((nav - running_max) / running_max).min()  # CORRECT
```

---

## 11. Standard Output Format

### File: `results/metrics.json`

```json
{
  "period": {
    "start": "2024-10-01",
    "end": "2024-10-07",
    "total_days": 7
  },
  "returns": {
    "total_return": 0.0369,
    "annualized_return": 2.4567,
    "daily_return_mean": 0.0053,
    "daily_return_std": 0.0142
  },
  "risk_adjusted": {
    "sharpe_ratio": 2.41,
    "sortino_ratio": 3.12,
    "calmar_ratio": 14.5
  },
  "risk": {
    "max_drawdown": -0.1234,
    "mdd_duration_days": 3,
    "recovery_duration_days": 2,
    "annualized_volatility": 0.2456,
    "var_95": -0.0234,
    "cvar_95": -0.0312
  },
  "trades": {
    "total_trades": 145,
    "win_rate": 0.623,
    "avg_trade_pnl": 245.67,
    "largest_win": 1234.56,
    "largest_loss": -876.54
  }
}
```

---

## 12. Agent Protocol: Performance Metrics

### BEFORE reporting backtest results:

1. ✅ Calculate NAV at every timestep (hourly or daily)
2. ✅ Resample to daily if using hourly
3. ✅ Calculate all metrics using **365-day annualization**
4. ✅ Save metrics to `results/metrics.json`
5. ✅ Include metrics table in README

### MANDATORY checks:

- ✅ Annualization factor = 365 (NOT 252, NOT 255)
- ✅ NAV includes unrealized PnL (Mark-to-Market)
- ✅ Fees deducted from cash/NAV
- ✅ MDD calculated from NAV (not equity)
- ✅ Daily resample before annualization

### Example Dialogue:

```
User: "백테스트 결과 보여줘"

Agent:
  [Reads knowledge/experiments/performance_metrics.md]

  "백테스트 완료. 성능 지표 (2024-10-01 ~ 2024-10-07, 7일):

  | Metric | Value | Note |
  |--------|-------|------|
  | Total Return | +3.69% | 7일간 |
  | Annualized Return | +245.67% | CAGR (365일 기준) |
  | Sharpe Ratio | 2.41 | 365일 annualization |
  | Sortino Ratio | 3.12 | Downside deviation |
  | Max Drawdown | -12.34% | 3일 지속, 2일 회복 |
  | Volatility | 24.56% | Annualized (365일) |
  | Win Rate | 62.3% | 145 trades |

  📚 출처: knowledge/experiments/performance_metrics.md
  📊 상세: results/metrics.json"
```

---

## References

- **Annualization Standards**: 365 days (crypto), NOT 252/255 (traditional markets)
- **User Requirement**: "hourly or daily로 NAV를 Mark to market으로 구하고, daily resample을 한다음에 거기서 365일 해야하는데"
- **Related KB**:
  - [Experiment Methodology](methodology.md) - Validation requirements
  - [Common Pitfalls](../lessons_learned/common_pitfalls.md) - Overfitting detection

---

**Version**: 1.0
**Critical**: 365-day annualization. 255일 쓰면 = 틀린 지표.
