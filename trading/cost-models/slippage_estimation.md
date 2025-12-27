# Slippage Estimation

**Purpose**: 백테스트 슬리피지 추정 모델
**Last Updated**: 2025-12-25
**Version**: 2.0 (Condensed)

---

## 📌 Quick Reference

| Model | Use Case | Accuracy | Data Required |
|-------|----------|----------|---------------|
| **Spread-based** | Taker, low liquidity | Low | Bid/Ask |
| **Depth-based** | Medium orders | Medium | Order book |
| **Impact** | Large orders (>20% vol) | High | Trade history |
| **Zero (Maker)** | Post-only | N/A | None |

**Recommendation**:
- Options (maker): Zero slippage
- Options (taker): Spread-based
- Futures (medium): Depth-based
- Futures (large): Impact function

---

## 📐 Formulas

```python
# Definition
Slippage = |Execution_Price - Reference_Price|
# Reference = mid price (typical)

# Spread-based (simple)
slippage = (ask - bid) / 2

# Depth-based (order book walk)
slippage = weighted_avg_price - mid_price

# Impact function (large orders)
slippage = a * (quantity / avg_volume)^b
# Typical: a=0.02, b=0.6

# Maker-only
slippage = 0  # Filled at limit price
```

---

## 💻 Implementation

### Spread-based

```python
def estimate_slippage_spread(bid, ask):
    """Half spread as slippage."""
    return (ask - bid) / 2

# Example: bid=2825, ask=2875
# slippage = 25.0
```

### Depth-based

```python
def estimate_slippage_depth(mid, order_book, quantity, side):
    """Walk order book for average fill price."""
    remaining = quantity
    total_cost = 0
    for price, qty in order_book:
        fill = min(remaining, qty)
        total_cost += fill * price
        remaining -= fill
        if remaining <= 0:
            break
    avg_price = total_cost / quantity
    return abs(avg_price - mid)
```

### Model Selection

```python
def select_model(quantity, avg_volume):
    ratio = quantity / avg_volume
    if ratio < 0.05:
        return 'spread-based'
    elif ratio < 0.20:
        return 'depth-based'
    else:
        return 'impact-function'
```

---

## 📊 Comparison (100 contracts, mid=$2,850)

| Model | Slippage/contract | Total | Notes |
|-------|-------------------|-------|-------|
| Spread (2%) | $25.00 | $2,500 | Conservative |
| Depth (3 lvl) | $29.00 | $2,900 | More accurate |
| Impact (20% vol) | $19.55 | $1,955 | With fitted params |
| Maker | $0.00 | $0 | Zero slippage |

---

## ⚠️ Common Mistakes

| ❌ Wrong | ✅ Right |
|---------|---------|
| Spread slippage for maker | Maker = zero slippage |
| Ignore partial fill | Track unfilled portion |
| Fixed slippage all conditions | Adapt to vol/spread |
| 100% taker assumption | Mix maker/taker realistic |

---

## 🔗 Integration

```python
def total_cost(mid, quantity, order_type, spread_pct=0.02):
    if order_type == 'maker':
        slippage = 0
        fee_rate = -0.0002  # Rebate
    else:
        slippage = mid * spread_pct / 2 * quantity
        fee_rate = 0.0003

    fees = mid * quantity * fee_rate
    return {'slippage': slippage, 'fees': fees, 'total': slippage + fees}
```

---

## ✅ Checklist

- [ ] Order type: maker vs taker
- [ ] Order size vs volume ratio
- [ ] Model calibrated (vs live execution)
- [ ] Partial fill accounted
- [ ] Market regime (vol, liquidity)

---

## 📚 Related

- T-cost: `transaction_cost_model.md`
- Fill probability: `fill_probability.md`
- Order execution: `../exchanges/okx/order_execution.md`

---

**References**: Almgren & Chriss (2000), OKX execution data (2024-Q4)
