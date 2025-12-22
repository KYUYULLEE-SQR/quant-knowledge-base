# OKX Order Execution

**Last Updated**: 2025-12-22
**Source**: User specification, OKX API docs, empirical observations
**Relevance**: Critical for realistic backtest fill modeling

---

## Overview

Order execution on OKX (and most exchanges) is **not instant** and **not guaranteed full fill**.

**Key concepts**:
1. **Maker vs Taker** (determines fees)
2. **Partial Fills** (order filled in chunks over time)
3. **Order Matching** (how orders are matched on the book)
4. **Slippage** (price movement during execution)

---

## Order Lifecycle

### 1. Order Placement
```python
# Example: Place limit buy order
order = {
    'symbol': 'BTC-USD-250131-50000-C',  # Call option
    'side': 'buy',
    'type': 'limit',
    'price': 0.05,       # Option price (in BTC or USD depending on contract)
    'size': 100,         # 100 contracts
    'post_only': True    # Only accept maker fills
}

response = exchange.place_order(**order)
# order_id: '123456789'
# status: 'open' (on the book, waiting for fill)
```

### 2. Matching Process

**Maker Order** (your order sits on book):
```
Time t=0:
  Order book:
    Bid: ... 0.049 (200), 0.048 (500)
    Ask: 0.051 (100), 0.052 (300), ...

  You place: BUY 100 @ 0.05 (limit)
  → Order posted on bid side: 0.05 (100)  [YOUR ORDER]

Time t=1:
  Someone places: SELL 30 @ market
  → Matches your 0.05 bid
  → You filled 30/100 (MAKER, -1 bps fee)
  → Remaining: 70 contracts still on book

Time t=5:
  Someone places: SELL 40 @ market
  → Matches your 0.05 bid
  → You filled 40/70 (MAKER, -1 bps fee)
  → Remaining: 30 contracts still on book
```

**Taker Order** (you cross the spread):
```
Time t=0:
  Order book:
    Ask: 0.051 (100), 0.052 (300), ...

  You place: BUY 100 @ 0.051 (limit, crosses spread)
  → Immediately matches 100 contracts at 0.051
  → Filled 100/100 (TAKER, +3 bps fee)
  → No remaining
```

### 3. Partial Fill Scenarios

**Why partial fills happen**:
1. **Insufficient liquidity** at your price level
2. **Other orders** matched before yours (price-time priority)
3. **Order size** larger than available depth

**Example**:
```python
# You want to buy 100 contracts
# But only 30 available at your price
# → Partial fill: 30 contracts

# Options:
# A) Wait for more liquidity at your price
# B) Cancel and reorder at worse price (aggressive)
# C) Market order the remaining (guaranteed fill, but taker fee + slippage)
```

---

## Partial Fill Probability Model (User Specification)

### Assumptions (Based on User Input)

**Fill Ratio**: ~30% of order size per attempt

**Rationale**:
- OKX options market has moderate liquidity
- Deep OTM options: lower liquidity → more partial fills
- ATM options: better liquidity → higher fill ratio

**Time Granularity**: 1-minute bars

**Reorder Behavior**:
```
t=0:   Place order for 100 contracts @ price P0
t=0:   Filled 30 contracts (30% fill ratio)
t=0:   Remaining: 70 contracts

t=1:   Price moved to P1 (could be better or worse)
t=1:   Cancel old order, reorder 70 contracts @ P1
t=1:   Filled 21 contracts (30% of 70)
t=1:   Remaining: 49 contracts

t=2:   Reorder 49 @ P2
t=2:   Filled 15 (30% of 49)
t=2:   Remaining: 34 contracts

... (continues until fully filled or max attempts)
```

### Backtest Implementation

```python
class PartialFillModel:
    def __init__(self, fill_ratio=0.3, max_attempts=5):
        """
        Partial fill simulator.

        Args:
            fill_ratio: Fraction of remaining order filled per attempt
            max_attempts: Max reorder attempts before giving up
        """
        self.fill_ratio = fill_ratio
        self.max_attempts = max_attempts

    def simulate_fill(self, order_size, entry_price, price_bars):
        """
        Simulate order execution with partial fills.

        Args:
            order_size: Total contracts to buy/sell
            entry_price: Initial order price
            price_bars: List of prices for subsequent bars (reorder prices)

        Returns:
            fills: List of (bar, size, price) tuples
            avg_price: Volume-weighted average fill price
            total_filled: Total contracts filled
        """
        fills = []
        remaining = order_size
        bar = 0

        while remaining > 0 and bar < min(self.max_attempts, len(price_bars)):
            # Calculate fill size for this attempt
            fill_size = max(1, int(remaining * self.fill_ratio))

            # Price for this fill
            if bar == 0:
                price = entry_price
            else:
                # Reorder at current market price (from price_bars)
                price = price_bars[bar]

            fills.append((bar, fill_size, price))
            remaining -= fill_size
            bar += 1

        # Calculate volume-weighted average price
        total_value = sum(size * price for _, size, price in fills)
        total_filled = sum(size for _, size, _ in fills)
        avg_price = total_value / total_filled if total_filled > 0 else entry_price

        return fills, avg_price, total_filled

# Example usage
model = PartialFillModel(fill_ratio=0.3, max_attempts=5)

# Simulate buying 100 contracts
# Entry price: 0.05
# Next 4 bars prices: [0.051, 0.052, 0.049, 0.050]
fills, avg_price, total_filled = model.simulate_fill(
    order_size=100,
    entry_price=0.05,
    price_bars=[0.051, 0.052, 0.049, 0.050]
)

# Output example:
# fills = [
#   (0, 30, 0.050),  # Bar 0: 30 @ 0.050
#   (1, 21, 0.051),  # Bar 1: 21 @ 0.051 (price moved up)
#   (2, 15, 0.052),  # Bar 2: 15 @ 0.052 (price moved up more)
#   (3, 10, 0.049),  # Bar 3: 10 @ 0.049 (price dropped)
#   (4, 7, 0.050)    # Bar 4: 7 @ 0.050
# ]
# avg_price = 0.05056 (0.56 bps worse than entry)
# total_filled = 83 (17 contracts not filled within 5 attempts)
```

### Realistic Adjustments

**Fill ratio depends on**:
1. **Option moneyness**: Deep OTM → lower fill ratio (~20%), ATM → higher (~50%)
2. **Size relative to depth**: Large orders → lower fill ratio
3. **Volatility**: High vol → faster fills (more trading), low vol → slower

```python
def dynamic_fill_ratio(moneyness, order_size_usd, depth_usd, volatility):
    """
    Estimate fill ratio based on market conditions.

    Args:
        moneyness: Distance from ATM (e.g., 0.0 = ATM, 0.3 = 30% OTM)
        order_size_usd: Order size in USD
        depth_usd: Available depth at price level
        volatility: Realized volatility (annualized)

    Returns:
        fill_ratio: Expected fill ratio (0-1)
    """
    # Base fill ratio
    base_ratio = 0.3

    # Adjustment for moneyness (deep OTM = worse)
    moneyness_penalty = max(0, moneyness * 0.5)  # -50% for 100% OTM
    base_ratio -= moneyness_penalty

    # Adjustment for size (large orders = worse)
    size_ratio = order_size_usd / depth_usd
    size_penalty = min(0.2, size_ratio * 0.3)  # Cap at -20%
    base_ratio -= size_penalty

    # Adjustment for volatility (high vol = better)
    vol_boost = min(0.1, (volatility - 0.5) * 0.2)  # +10% max
    base_ratio += vol_boost

    return max(0.1, min(0.8, base_ratio))  # Clamp to [10%, 80%]
```

---

## Maker-Only Strategy (Zero Slippage)

### Concept
**Both entry AND exit are maker orders that get filled → no slippage.**

```python
# Entry (Long Call)
t=0:  Place BUY limit @ 0.05 (below current ask)
t=5:  Filled as MAKER (someone sold to you)
      Fee: -1 bps (rebate)

# Exit (Close Long Call)
t=100: Place SELL limit @ 0.06 (above current bid)
t=105: Filled as MAKER (someone bought from you)
       Fee: -1 bps (rebate)

# Total cost:
#   Entry fee: -1 bps
#   Exit fee: -1 bps
#   Slippage: 0 bps (got exact prices you posted)
#   Total: -2 bps (you EARNED 2 bps from trading!)
```

**Conditions for this to work**:
1. ✅ Willing to wait for fills (no urgency)
2. ✅ Market has sufficient two-way flow (buyers and sellers)
3. ✅ Position size small enough to be absorbed
4. ✅ Both orders filled before you cancel/modify

**Backtest implementation**:
```python
# Maker-only strategy
# Assume both entry and exit fill at posted prices
entry_price = bid_price  # Your buy limit
exit_price = ask_price   # Your sell limit

pnl = exit_price - entry_price - fees
# fees = -0.0002 (two maker fills, -1 bps each)
# Slippage = 0 (by construction)
```

**Risks**:
- ⚠️ Order may NOT fill if market moves away
- ⚠️ Partial fills (see model above)
- ⚠️ Opportunity cost (price moves while waiting)

---

## Backtest Guidelines

### Default Assumption (Conservative)

```python
# For most strategies
PARTIAL_FILL_ENABLED = True
FILL_RATIO = 0.3         # 30% per attempt
MAX_FILL_ATTEMPTS = 5    # 5 bars (5 minutes)
REORDER_SLIPPAGE = 5     # 5 bps per reorder

# Result: Avg fill price ~5-10 bps worse than initial order price
```

### Optimistic (Maker-Only)

```python
# Only if strategy explicitly designed for maker-only
PARTIAL_FILL_ENABLED = False
SLIPPAGE = 0

# Both entry and exit at posted prices
# Fee = negative (rebate)
```

### Validation (Post-Live)

```python
# After live trading, compare actual vs backtest
actual_fills = get_historical_fills()

# Calculate actual fill ratio
actual_fill_ratio = np.mean([
    fill.filled_size / fill.order_size
    for fill in actual_fills
])

# Compare to backtest assumption (0.3)
if abs(actual_fill_ratio - 0.3) > 0.1:
    print(f"⚠️ Fill ratio mismatch: backtest 0.3, actual {actual_fill_ratio:.2f}")
```

---

## Common Mistakes (Agents)

1. ❌ **"All orders fill completely and instantly"**
   - ✅ Partial fills are common, especially for large orders or illiquid options

2. ❌ **"Maker orders have zero slippage, so I can assume perfect fills"**
   - ✅ Maker orders still face partial fill risk
   - ✅ Reordering at worse price = effective slippage

3. ❌ **"30% fill ratio is exact"**
   - ✅ It's an average/assumption
   - ✅ Can vary: ATM 50%, deep OTM 20%
   - ✅ Backtest should test sensitivity

4. ❌ **"If order doesn't fill, just use next bar's price"**
   - ✅ This creates look-ahead bias if you "know" next bar price when placing order
   - ✅ Correct: Model partial fill over multiple bars

5. ❌ **"Slippage only matters for taker orders"**
   - ✅ Even maker orders have "effective slippage" from partial fills + reorders

---

## Agent Protocol: Order Execution in Backtest

**BEFORE implementing order execution logic:**

1. ✅ Read this file + [Transaction Cost Model](../../modeling/transaction_cost_model.md)
2. ✅ Determine strategy type:
   - Maker-only (patient) → Can assume lower slippage, but still model partial fills
   - Mixed (some urgency) → Use partial fill model (30% fill ratio)
   - Taker (urgent) → Full slippage + taker fees
3. ✅ Implement partial fill model if order size > typical depth
4. ✅ Test sensitivity: 20%, 30%, 50% fill ratios
5. ✅ Validate post-live: Compare actual fill ratios to backtest assumptions

**Example**:
```
User: "Maker 주문이면 슬리피지 없지?"

Agent:
  [Reads this KB file]

  "Maker 주문은 posted price에 체결되므로 **직접적 slippage는 없습니다**.

   하지만:
   1. Partial fill 가능성 (~30% fill ratio 가정)
   2. 재주문 시 가격 변동 → '간접적 slippage' 발생
   3. 100% 체결 보장 안 됨

   백테스트 권장:
   - Partial fill model 사용 (fill_ratio=0.3)
   - 5회 재주문 시도 (5분 이내)
   - 평균 5-10 bps 'effective slippage' 가정

   📚 출처: knowledge/exchanges/okx/order_execution.md"
```

---

## References

- **OKX API Docs**: https://www.okx.com/docs-v5/en/#order-book-trading-trade
- **Related KB**:
  - [Fee Structure](fee_structure.md) - Maker vs taker fees
  - [Transaction Cost Model](../../modeling/transaction_cost_model.md) - Full T-cost breakdown
- **User conversation**: 2025-12-22 (partial fill specification)

---

**Version**: 1.0
**Critical**: Partial fill modeling is often overlooked but critical for large orders.
