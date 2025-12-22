# Transaction Cost Model (T-cost)

**Last Updated**: 2025-12-22
**Source**: User specification, OKX fee structure, empirical data
**Importance**: ⭐⭐⭐ Critical for backtest realism

---

## Overview

**Transaction cost (T-cost)** is the total cost of executing a trade, beyond the asset price:

```
T-cost = Exchange Fees + Slippage + Partial Fill Impact
```

**CRITICAL**: Backtest MUST include all three components, or results will be unrealistically optimistic.

---

## Component 1: Exchange Fees

### OKX Fee Structure (User's Account)

**Tier**: DMM (Designated Market Maker) = VIP9 equivalent

| Instrument | Maker | Taker | Notes |
|-----------|-------|-------|-------|
| **Futures** | **-0.5 bps** (-0.005%) | +5 bps | Rebate received |
| **Options** | **-1.0 bps** (-0.01%) | +3 bps | Rebate received |
| **Perpetual** | -0.5 bps | +5 bps | (if applicable) |

**Key Points**:
- ✅ **Maker = negative fee** (you get paid for providing liquidity)
- ✅ **Taker = positive fee** (you pay for taking liquidity)
- ⚠️ Maker rebate only if order sits on book and gets filled passively
- ⚠️ If order crosses spread (immediate fill) = taker fee

### Backtest Usage

```python
# Conservative assumption: Not all orders are maker
MAKER_RATIO = 0.7  # 70% of orders filled as maker, 30% as taker

# Futures
fee_maker = -0.005 / 100  # -0.5 bps
fee_taker = 5 / 100 / 100  # +5 bps

expected_fee_futures = MAKER_RATIO * fee_maker + (1 - MAKER_RATIO) * fee_taker
# = 0.7 * (-0.00005) + 0.3 * (0.0005) = 0.000115 = 1.15 bps

# Options
fee_maker_opt = -0.01 / 100  # -1 bps
fee_taker_opt = 3 / 100 / 100  # +3 bps

expected_fee_options = MAKER_RATIO * fee_maker_opt + (1 - MAKER_RATIO) * fee_taker_opt
# = 0.7 * (-0.0001) + 0.3 * (0.0003) = 0.00002 = 0.2 bps
```

**Risk**: If backtest assumes 100% maker but reality is 50/50, fee estimate off by ~2-3 bps.

---

## Component 2: Slippage

### Definition
**Slippage** = difference between expected price and actual execution price

### Two Scenarios

#### Scenario A: Maker-Only Strategy (No Slippage)
```python
# Strategy: Place limit orders on both sides, wait for fill
# Example: Market making, grid trading

# Step 1: Place bid at $50,000, ask at $50,010
# Step 2: Wait for counterparty to take your orders
# Step 3: Both sides filled → close position

# Slippage: ZERO (you got exactly the price you posted)
# Fee: Maker rebate only (negative fee)
# T-cost: -1 bps (you earn 1 bps from rebate)
```

**Conditions for zero slippage**:
- ✅ Both entry and exit are maker orders
- ✅ Both orders filled before you cancel/modify
- ✅ No urgency (willing to wait)

#### Scenario B: Partial Fill + Reorder (Slippage Possible)
```python
# Strategy: Place order, partial fill, need to reorder

# Step 1: Place 100 contracts @ $50,000
# Step 2: Only 30 filled (partial fill)
# Step 3: Cancel, reorder remaining 70 @ new price
# Step 4: Repeat until fully filled

# Slippage: Depends on price movement between reorders
# Fee: Mix of maker/taker (if reorder crosses spread)
```

**Slippage estimation**:
```python
# Simple model: Slippage = α * spread + β * volatility
spread = ask - bid  # e.g., $10
volatility = realized_vol_1min  # e.g., 0.5% per minute

slippage_bps = 0.5 * (spread / mid_price) + 0.3 * volatility
# Example: 0.5 * (10/50000) + 0.3 * 0.005 = 0.0001 + 0.0015 = 0.0016 = 16 bps
```

**Depth-based model** (better):
```python
# Slippage depends on order size vs order book depth
order_size_usd = 100 * 50000  # 100 contracts * price = $5M
depth_at_best = 200 * 50000   # $10M available at best bid/ask

impact_ratio = order_size_usd / depth_at_best  # 0.5
slippage_bps = impact_ratio * spread_bps * 2  # Heuristic: 2x spread per 100% of depth

# Example: 0.5 * 2 bps * 2 = 2 bps
```

### Backtest Implementation

```python
def calculate_slippage(order_size, market_depth, spread, is_maker):
    """
    Calculate slippage for an order.

    Args:
        order_size: Order size in USD
        market_depth: Available liquidity at best price (USD)
        spread: Bid-ask spread in USD
        is_maker: True if order filled as maker (passive)

    Returns:
        slippage_bps: Slippage in basis points
    """
    if is_maker:
        # Maker order: no slippage (got exact posted price)
        return 0.0

    # Taker order: slippage depends on size vs depth
    impact_ratio = order_size / market_depth
    spread_bps = (spread / mid_price) * 10000

    # Heuristic: slippage = (order_size / depth) * spread * multiplier
    slippage_bps = impact_ratio * spread_bps * 2

    # Cap at reasonable max (e.g., 50 bps for deep OTM options)
    return min(slippage_bps, 50)
```

---

## Component 3: Partial Fill Impact

### Problem
- Order for 100 contracts posted
- Only 30 filled immediately
- Remaining 70 need to wait OR reorder at worse price

### Model Specification (User-Provided)

**Assumptions**:
1. **Fill ratio**: ~30% of order size filled on first attempt
2. **Reorder timing**: Next minute (1-minute bar granularity)
3. **Reorder price**: Depends on price movement in that 1 minute

```python
# Example trade sequence
t=0:   Place order: BUY 100 @ $50,000 (maker)
t=0:   Filled: 30 @ $50,000 (maker, no slippage)
t=0:   Remaining: 70 contracts

t=1:   Price moved to $50,050
t=1:   Reorder: BUY 70 @ $50,050 (maker)
t=1:   Filled: 21 @ $50,050 (0.1% slippage on these 21)
t=1:   Remaining: 49 contracts

t=2:   Price moved to $50,100
...
```

### Simplified Backtest Model (Conservative)

```python
class PartialFillModel:
    def __init__(self, fill_ratio=0.3, reorder_slippage_bps=5):
        """
        fill_ratio: Fraction filled per attempt (default 30%)
        reorder_slippage_bps: Slippage on reorder attempts
        """
        self.fill_ratio = fill_ratio
        self.reorder_slippage_bps = reorder_slippage_bps

    def execute_order(self, order_size, entry_price, bars_data):
        """
        Simulate order execution with partial fills.

        Args:
            order_size: Total contracts to buy/sell
            entry_price: Initial order price
            bars_data: Price data for subsequent bars (for reorder)

        Returns:
            avg_fill_price: Volume-weighted average fill price
            total_filled: Total contracts filled
            num_attempts: Number of reorder attempts
        """
        filled = 0
        total_cost = 0
        attempt = 0

        while filled < order_size and attempt < len(bars_data):
            remaining = order_size - filled
            fill_this_round = int(remaining * self.fill_ratio)

            if fill_this_round == 0:
                fill_this_round = remaining  # Fill remaining on last attempt

            # Price for this fill
            if attempt == 0:
                price = entry_price  # First fill at original price
            else:
                # Reorder at current market price + slippage
                price = bars_data[attempt] * (1 + self.reorder_slippage_bps / 10000)

            filled += fill_this_round
            total_cost += fill_this_round * price
            attempt += 1

        avg_fill_price = total_cost / filled if filled > 0 else entry_price
        return avg_fill_price, filled, attempt

# Usage in backtest
model = PartialFillModel(fill_ratio=0.3, reorder_slippage_bps=5)
avg_price, filled, attempts = model.execute_order(
    order_size=100,
    entry_price=50000,
    bars_data=[50050, 50100, 50080]  # Next 3 bars
)

# avg_price might be ~50,025 (0.05% worse than entry_price)
# This is the "partial fill impact"
```

**Conservative Estimate**:
- If order fills over 3-5 bars (3-5 minutes)
- And price volatility is 0.5% per minute
- Expected slippage from partial fills: ~5-10 bps

---

## Total T-cost Summary

### Maker-Only Strategy (Best Case)
```python
# Both entry and exit are maker, no partial fills
fee = -1 bps (rebate)
slippage = 0 bps
partial_fill_impact = 0 bps

Total T-cost = -1 bps (you earn money from trading!)
```

### Realistic Mixed Strategy
```python
# 70% maker, 30% taker, some partial fills
fee = 0.2 bps (options, mixed maker/taker)
slippage = 2 bps (depth-based)
partial_fill_impact = 5 bps (reorder over 3 bars)

Total T-cost = 7.2 bps (~0.072% per round trip)
```

### Conservative (Worst Case)
```python
# Mostly taker, deep OTM options, large size
fee = 3 bps (taker)
slippage = 10 bps (low depth)
partial_fill_impact = 10 bps (many reorders)

Total T-cost = 23 bps (~0.23% per round trip)
```

---

## Backtest Guidelines

### MANDATORY Checks

1. ✅ **Include all three components** (fee + slippage + partial fill)
2. ✅ **Test sensitivity**: Run backtest at 0.5×, 1×, 2× T-cost
3. ✅ **Conservative default**: Use "Realistic Mixed" (~7 bps)
4. ✅ **Maker assumption**: Verify with historical fill data (if available)

### Example Backtest Config

```python
# config.yaml
transaction_costs:
  # Fees (based on OKX DMM VIP9)
  maker_fee_futures: -0.005%    # -0.5 bps
  taker_fee_futures: 0.05%      # +5 bps
  maker_fee_options: -0.01%     # -1 bps
  taker_fee_options: 0.03%      # +3 bps

  # Maker ratio (conservative)
  maker_ratio: 0.7

  # Slippage
  slippage_model: "depth_based"
  slippage_base_bps: 2          # Base slippage
  slippage_multiplier: 2        # Multiplier for size impact

  # Partial fill
  partial_fill_enabled: true
  fill_ratio_per_bar: 0.3       # 30% fill per minute
  reorder_slippage_bps: 5       # Additional slippage on reorder

  # Sensitivity testing
  cost_multipliers: [0.5, 1.0, 2.0]
```

### Red Flags

❌ **Backtest assumes zero slippage** → Unrealistic for any taker orders
❌ **100% maker assumption** → Unless proven with historical data
❌ **No partial fill model** → Unrealistic for large orders
❌ **Ignores spread** → Even maker orders face bid-ask spread risk
❌ **Strategy Sharpe collapses at 2× cost** → Too cost-sensitive, likely won't work live

---

## References

- [OKX Fee Structure](../exchanges/okx/fee_structure.md) - Fee tiers, rebates
- [OKX Order Execution](../exchanges/okx/order_execution.md) - Partial fill behavior
- User conversation: 2025-12-22 (T-cost specification)
- Experiment: `experiments/2025-12-05_tcost_underestimation/README.md` (lesson learned)

---

**Version**: 1.0
**Critical**: This is the #1 source of backtest-vs-live discrepancy. Get this right.
