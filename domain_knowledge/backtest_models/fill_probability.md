# Fill Probability

**Purpose**: Maker order fill probability 추정 (OKX 옵션 기준 ~30%)
**Last Updated**: 2025-12-25
**Version**: 2.0 (Condensed)

---

## 📌 Quick Reference

| Order Type | Fill Ratio | Fill Time | Notes |
|------------|-----------|-----------|-------|
| **Maker (post-only)** | 30% | 1-5 min | OKX BTC options 실측 |
| **Taker (market)** | 100% | Immediate | By definition |
| **Maker (aggressive)** | 60-80% | <1 min | Near mid |
| **Maker (passive)** | 10-20% | >10 min | Far from mid |

**Key Insight**:
- OKX BTC options maker = **30% fill** (287 orders, 2024-Q4)
- 100% fill 가정 → PnL 과대평가
- Fill probability는 시장 조건 의존, **fee tier와 무관**

---

## 📊 Empirical Data (OKX BTC Options)

| Distance from Mid | Fill Ratio | Sample |
|-------------------|-----------|--------|
| At mid (±$5) | 72% | 18 |
| 1 tick | 45% | 67 |
| 2-3 ticks | 29% | 142 |
| 4-5 ticks | 14% | 48 |
| >5 ticks | 6% | 12 |

**Distribution**:
- 0% fill: 16% of orders
- 1-50% fill: 70% of orders
- 100% fill: 4% of orders

---

## 💻 Implementation

### Fixed Ratio (Simple)

```python
def estimate_fill(quantity, fill_ratio=0.3):
    return {
        'filled': quantity * fill_ratio,
        'unfilled': quantity * (1 - fill_ratio)
    }
```

### Spread-Dependent

```python
import numpy as np

def estimate_fill_spread(limit, mid, spread, side):
    """Fill probability based on distance from mid."""
    if side == 'buy':
        distance = mid - limit
    else:
        distance = limit - mid

    if distance < 0:
        return 1.0  # Aggressive (taker)

    norm_dist = distance / (spread / 2)
    return max(0.01, 0.7 * np.exp(-1.5 * norm_dist))
```

---

## 🧪 Backtest Integration

### ❌ Wrong (100% fill)

```python
for signal in signals:
    execute(signal['quantity'])  # Overestimates PnL
# Result: Sharpe 3.2, MDD -8% (과대평가)
```

### ✅ Correct (30% fill)

```python
for signal in signals:
    filled = signal['quantity'] * 0.3
    execute(filled)
    unfilled_queue.append(signal['quantity'] - filled)

# Repost unfilled
for unfilled in unfilled_queue:
    if still_valid(unfilled):
        repost_at_aggressive_price(unfilled)

# Result: Sharpe 2.1, MDD -12% (현실적)
```

### Impact

| Metric | 100% Fill | 30% Fill | Difference |
|--------|-----------|----------|------------|
| PnL | $10,000 | $6,000 | -40% |
| Sharpe | 3.2 | 2.1 | -35% |
| Trades | 100 | 60 | -40% |

---

## ⚠️ Common Mistakes

| ❌ Wrong | ✅ Right |
|---------|---------|
| 100% fill for maker | 30% fill (empirical) |
| Ignore unfilled | Track + repost unfilled |
| Same fill all conditions | Adapt to vol/spread |
| Fill depends on fee tier | Fill depends on market only |

---

## 📐 Total Cost with Partial Fill

```python
def total_cost_partial(quantity, fill_ratio=0.3, fee_maker=-0.0002, reposts=2):
    filled = 0
    remaining = quantity
    total_fees = 0

    for _ in range(reposts + 1):
        fill_this = remaining * fill_ratio
        filled += fill_this
        total_fees += fill_this * fee_maker
        remaining -= fill_this
        if remaining < 0.1:
            break

    return {
        'filled': filled,
        'unfilled': remaining,
        'fees': total_fees,  # Negative = rebate
        'effective_fill': filled / quantity
    }

# 3 reposts: 10 qty → 6.57 filled (65.7%)
```

---

## ✅ Checklist

- [ ] Fill ratio calibrated (from live data)
- [ ] Unfilled tracked (not ignored)
- [ ] Repost logic implemented
- [ ] Market conditions considered
- [ ] Sharpe not inflated by 100% assumption

---

## 📚 Related

- Slippage: `slippage_estimation.md`
- T-cost: `transaction_cost_model.md`
- Order execution: `../exchanges/okx/order_execution.md`

---

**Data Source**: OKX BTC options (287 orders, 2024-Q4)
**Key**: 30% avg fill, distance from mid = strongest predictor
