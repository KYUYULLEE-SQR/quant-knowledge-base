# Slippage Estimation

**Purpose**: 백테스트 및 전략 실행 시 슬리피지 추정 모델 (Depth-based, Spread-based, Impact function)

**Last Updated**: 2025-12-23
**Owner**: sqr
**Environment**: micky (data), spice (backtest), vultr (trading)

---

## 📌 Quick Reference

| Model Type | Use Case | Data Required | Accuracy | Complexity |
|------------|----------|---------------|----------|------------|
| **Spread-based** | Taker orders, low liquidity | Bid/Ask spread | Low | Simple |
| **Depth-based** | Medium orders, stable liquidity | Order book depth | Medium | Medium |
| **Impact function** | Large orders, price impact | Historical trades + volume | High | Complex |
| **Zero (Maker-only)** | Post-only orders, maker fee | None (assumes 100% fill at limit) | N/A | Simple |

**Recommendation**:
- **Options (maker-only)**: Zero slippage (post-only orders, maker rebate if VIP tier)
- **Options (taker)**: Spread-based (low liquidity, wide spreads)
- **Futures (medium size)**: Depth-based
- **Futures (large size)**: Impact function

---

## 🎯 Slippage Definition

**Slippage**: 실제 체결 가격과 의사결정 시점 가격의 차이

```
Slippage (per contract) = |Execution_Price - Reference_Price|

Total Slippage Cost = Slippage × Quantity × Contract_Value
```

**Reference Price**:
- **Mid price**: `(bid + ask) / 2` (가장 흔한 기준)
- **Last price**: 마지막 체결가
- **Mark price**: 거래소 공식 mark price (옵션)

**Direction**:
- **Buy**: Slippage = Execution_Price - Reference_Price (positive)
- **Sell**: Slippage = Reference_Price - Execution_Price (positive)

**Example**:
```
Bid: $2,825, Ask: $2,875, Mid: $2,850

Buy market order:
  Execution: $2,875 (ask)
  Slippage: $2,875 - $2,850 = $25

Sell market order:
  Execution: $2,825 (bid)
  Slippage: $2,850 - $2,825 = $25
```

---

## 📊 Model 1: Spread-Based (Simple)

### Formula

```python
slippage = spread / 2

where:
  spread = ask - bid
```

**Assumption**: Taker order가 bid/ask 중간 지점에서 체결

### Implementation

```python
def estimate_slippage_spread(bid: float, ask: float) -> float:
    """
    Spread-based slippage estimation.

    Args:
        bid: Best bid price
        ask: Best ask price

    Returns:
        Estimated slippage per contract
    """
    if bid <= 0 or ask <= 0 or ask < bid:
        raise ValueError(f"Invalid bid/ask: {bid}/{ask}")

    spread = ask - bid
    slippage = spread / 2.0

    return slippage

# Example
bid = 2825
ask = 2875
slippage = estimate_slippage_spread(bid, ask)  # = 25.0
```

### When to Use

**✅ Good for**:
- **Low liquidity markets** (옵션, exotic instruments)
- **Wide spreads** (spread > 1% of mid)
- **Quick estimation** (no order book data)
- **Taker orders** (market orders, aggressive limit orders)

**❌ Not suitable for**:
- **High liquidity** (spread-based overestimates)
- **Large orders** (depth matters)
- **Maker orders** (no slippage if filled at limit)

### Backtest Integration

```python
def calculate_transaction_cost_spread(
    mid_price: float,
    spread_pct: float,
    quantity: int,
    side: str,
    fee_rate: float = 0.0003  # 0.03% taker fee
) -> dict:
    """
    Calculate total transaction cost (fees + slippage).

    Args:
        mid_price: Mid price at decision time
        spread_pct: Bid-ask spread as % of mid (e.g., 0.02 = 2%)
        quantity: Order size (contracts)
        side: 'buy' or 'sell'
        fee_rate: Taker fee rate

    Returns:
        {'slippage': X, 'fees': Y, 'total_cost': Z}
    """
    spread = mid_price * spread_pct
    slippage_per_contract = spread / 2.0

    # Execution price
    if side == 'buy':
        execution_price = mid_price + slippage_per_contract
    else:
        execution_price = mid_price - slippage_per_contract

    # Costs
    notional = execution_price * quantity
    slippage_cost = slippage_per_contract * quantity
    fees = notional * fee_rate

    return {
        'execution_price': execution_price,
        'slippage': slippage_cost,
        'fees': fees,
        'total_cost': slippage_cost + fees,
        'slippage_bps': (slippage_per_contract / mid_price) * 10000
    }

# Example
cost = calculate_transaction_cost_spread(
    mid_price=2850,
    spread_pct=0.0175,  # 1.75% spread (50 / 2850)
    quantity=10,
    side='buy'
)
# Result: {'slippage': 250, 'fees': 8.55, 'total_cost': 258.55}
```

---

## 📈 Model 2: Depth-Based (Medium)

### Formula

```python
slippage = weighted_avg_price - reference_price

where weighted_avg_price is calculated by walking the order book
```

**Method**: "Order book walk" - 주문량만큼 order book을 소진하며 평균 체결가 계산

### Implementation

```python
from typing import List, Tuple

def estimate_slippage_depth(
    reference_price: float,
    order_book: List[Tuple[float, float]],  # [(price, quantity), ...]
    quantity: float,
    side: str
) -> dict:
    """
    Depth-based slippage estimation via order book walk.

    Args:
        reference_price: Mid price or mark price
        order_book: List of (price, quantity) tuples (sorted: asks asc, bids desc)
        quantity: Order size to fill
        side: 'buy' (walk asks) or 'sell' (walk bids)

    Returns:
        {
            'avg_execution_price': weighted average fill price,
            'slippage': total slippage,
            'slippage_pct': slippage as % of reference,
            'levels_consumed': number of price levels used,
            'unfilled_quantity': if order book insufficient
        }
    """
    if quantity <= 0:
        raise ValueError("Quantity must be positive")

    if not order_book:
        raise ValueError("Order book is empty")

    remaining_qty = quantity
    total_cost = 0.0
    levels_consumed = 0

    for price, available_qty in order_book:
        if remaining_qty <= 0:
            break

        fill_qty = min(remaining_qty, available_qty)
        total_cost += fill_qty * price
        remaining_qty -= fill_qty
        levels_consumed += 1

    if remaining_qty > 0:
        # Order book insufficient - extrapolate or raise error
        avg_execution_price = total_cost / (quantity - remaining_qty) if quantity > remaining_qty else order_book[-1][0]
        unfilled = remaining_qty
    else:
        avg_execution_price = total_cost / quantity
        unfilled = 0

    # Calculate slippage
    if side == 'buy':
        slippage = avg_execution_price - reference_price
    else:
        slippage = reference_price - avg_execution_price

    slippage_total = slippage * (quantity - unfilled)
    slippage_pct = (slippage / reference_price) * 100

    return {
        'avg_execution_price': avg_execution_price,
        'slippage_per_contract': slippage,
        'slippage_total': slippage_total,
        'slippage_pct': slippage_pct,
        'slippage_bps': slippage_pct * 100,
        'levels_consumed': levels_consumed,
        'unfilled_quantity': unfilled
    }

# Example: Buy 100 contracts
asks = [
    (2875, 50),   # 50 @ $2,875
    (2880, 30),   # 30 @ $2,880
    (2885, 20),   # 20 @ $2,885
    (2890, 10)    # 10 @ $2,890
]

result = estimate_slippage_depth(
    reference_price=2850,  # Mid price
    order_book=asks,
    quantity=100,
    side='buy'
)

# Result:
# avg_execution_price = (50*2875 + 30*2880 + 20*2885) / 100 = 2879.0
# slippage_per_contract = 2879.0 - 2850 = 29.0
# slippage_total = 29.0 * 100 = 2,900
# levels_consumed = 3
```

### Backtest Integration

```python
import pandas as pd

def backtest_with_depth_slippage(
    signals: pd.DataFrame,  # columns: timestamp, side, quantity
    orderbook_data: pd.DataFrame,  # columns: timestamp, bids, asks
    fee_rate: float = 0.0003
) -> pd.DataFrame:
    """
    Backtest with depth-based slippage.

    Args:
        signals: Trading signals with timestamp, side, quantity
        orderbook_data: Order book snapshots (bids/asks as list of tuples)
        fee_rate: Taker fee rate

    Returns:
        DataFrame with execution details and costs
    """
    trades = []

    for _, signal in signals.iterrows():
        timestamp = signal['timestamp']
        side = signal['side']
        quantity = signal['quantity']

        # Get order book at signal time
        book = orderbook_data.loc[orderbook_data['timestamp'] == timestamp]

        if book.empty:
            print(f"Warning: No order book at {timestamp}")
            continue

        mid_price = (book['best_bid'].iloc[0] + book['best_ask'].iloc[0]) / 2

        # Select order book side
        if side == 'buy':
            order_book = book['asks'].iloc[0]  # List of (price, qty)
        else:
            order_book = book['bids'].iloc[0]

        # Estimate slippage
        slip_result = estimate_slippage_depth(
            reference_price=mid_price,
            order_book=order_book,
            quantity=quantity,
            side=side
        )

        # Calculate costs
        execution_price = slip_result['avg_execution_price']
        notional = execution_price * quantity
        fees = notional * fee_rate

        trades.append({
            'timestamp': timestamp,
            'side': side,
            'quantity': quantity,
            'mid_price': mid_price,
            'execution_price': execution_price,
            'slippage': slip_result['slippage_total'],
            'slippage_bps': slip_result['slippage_bps'],
            'fees': fees,
            'total_cost': slip_result['slippage_total'] + fees,
            'levels_consumed': slip_result['levels_consumed']
        })

    return pd.DataFrame(trades)
```

### When to Use

**✅ Good for**:
- **Medium liquidity** markets
- **Moderate order sizes** (not too large to walk through entire book)
- **Order book data available** (historical or real-time)
- **More accurate than spread-based**

**❌ Not suitable for**:
- **Very large orders** (order book insufficient, need impact model)
- **No order book data** (use spread-based instead)
- **Maker orders** (assumes taker execution)

---

## 📉 Model 3: Impact Function (Advanced)

### Formula

```python
slippage = a * (quantity / avg_volume)^b

where:
  a, b = fitted parameters (from historical data)
  avg_volume = average market volume
```

**Rationale**: Large orders move the market proportionally to their size relative to volume

### Implementation

```python
import numpy as np
from scipy.optimize import curve_fit

def price_impact_function(quantity_ratio: float, a: float, b: float) -> float:
    """
    Price impact as % of mid price.

    Args:
        quantity_ratio: Order size / Average volume
        a: Impact coefficient
        b: Impact exponent (typically 0.5-0.7)

    Returns:
        Price impact as fraction (e.g., 0.001 = 0.1%)
    """
    return a * (quantity_ratio ** b)

def fit_impact_model(
    historical_trades: pd.DataFrame  # columns: quantity, volume, slippage_pct
) -> Tuple[float, float]:
    """
    Fit impact function parameters from historical trade data.

    Args:
        historical_trades: DataFrame with:
            - quantity: Order size
            - volume: Market volume at time of trade
            - slippage_pct: Realized slippage (%)

    Returns:
        (a, b): Fitted parameters
    """
    # Calculate quantity ratio
    historical_trades['qty_ratio'] = historical_trades['quantity'] / historical_trades['volume']

    # Fit power law: slippage = a * (qty_ratio)^b
    x = historical_trades['qty_ratio'].values
    y = historical_trades['slippage_pct'].values / 100  # Convert to fraction

    # Initial guess: a=0.01, b=0.5
    params, _ = curve_fit(
        lambda x, a, b: a * (x ** b),
        x, y,
        p0=[0.01, 0.5],
        bounds=([0, 0], [1, 2])  # a in [0, 1], b in [0, 2]
    )

    a, b = params
    return a, b

def estimate_slippage_impact(
    quantity: float,
    avg_volume: float,
    mid_price: float,
    a: float = 0.02,
    b: float = 0.6
) -> dict:
    """
    Estimate slippage using impact function.

    Args:
        quantity: Order size
        avg_volume: Average market volume (recent period)
        mid_price: Current mid price
        a, b: Impact function parameters

    Returns:
        Slippage estimate
    """
    if avg_volume <= 0:
        raise ValueError("Average volume must be positive")

    qty_ratio = quantity / avg_volume
    impact_pct = price_impact_function(qty_ratio, a, b)

    slippage_per_contract = mid_price * impact_pct
    slippage_total = slippage_per_contract * quantity

    return {
        'qty_ratio': qty_ratio,
        'impact_pct': impact_pct * 100,
        'slippage_per_contract': slippage_per_contract,
        'slippage_total': slippage_total,
        'slippage_bps': impact_pct * 10000
    }

# Example
result = estimate_slippage_impact(
    quantity=100,
    avg_volume=500,  # Average volume: 500 contracts/hour
    mid_price=2850,
    a=0.02,
    b=0.6
)

# qty_ratio = 100/500 = 0.2
# impact_pct = 0.02 * (0.2^0.6) = 0.00686 = 0.686%
# slippage_per_contract = 2850 * 0.00686 = 19.55
# slippage_total = 19.55 * 100 = 1,955
```

### Parameter Fitting Example

```python
# Historical trade data (from execution logs)
historical_trades = pd.DataFrame({
    'timestamp': [...],
    'quantity': [10, 25, 50, 100, 200],
    'volume': [500, 480, 510, 490, 505],  # Market volume
    'slippage_pct': [0.05, 0.12, 0.25, 0.68, 1.42]  # Realized slippage %
})

# Fit impact model
a, b = fit_impact_model(historical_trades)
print(f"Impact model: slippage% = {a:.4f} × (qty/vol)^{b:.2f}")

# Example output:
# Impact model: slippage% = 0.0213 × (qty/vol)^0.58

# Use fitted parameters for future estimates
estimate_slippage_impact(quantity=150, avg_volume=500, mid_price=2850, a=a, b=b)
```

### When to Use

**✅ Good for**:
- **Large orders** (quantity > 10% of avg volume)
- **Systematic strategies** with execution history
- **Algorithms** (TWAP, VWAP, iceberg)
- **High accuracy requirements**

**❌ Not suitable for**:
- **No historical data** (can't fit parameters)
- **Small orders** (overkill, use depth-based)
- **Low liquidity** (impact function unreliable)

---

## 🎯 Model 4: Zero Slippage (Maker-Only)

### Assumption

**Post-only (maker) orders have zero slippage** if filled at limit price.

**Rationale**:
- Maker order is placed at limit price (e.g., mid - $5)
- If filled, execution price = limit price exactly
- No slippage (by definition of limit order)

**Exception**: Partial fill risk (see `modeling/fill_probability.md`)

### Implementation

```python
def estimate_slippage_maker(fill_ratio: float = 0.3) -> dict:
    """
    Maker-only slippage (zero if filled).

    Args:
        fill_ratio: Expected fill probability (default 30%)

    Returns:
        Slippage estimate (0 for filled portion)
    """
    # For filled portion: zero slippage
    # For unfilled portion: opportunity cost (not slippage)

    return {
        'slippage_per_contract': 0.0,
        'slippage_total': 0.0,
        'fill_ratio_expected': fill_ratio,
        'note': 'Maker orders have zero slippage. Use fill_probability model for partial fill impact.'
    }
```

### When to Use

**✅ Good for**:
- **Maker-only strategies** (post-only orders)
- **VIP tier with maker rebate** (negative fees, e.g., VIP9 -0.02%)
- **Patient execution** (willing to wait for fill)

**❌ Caveats**:
- **Partial fill risk**: Only 30% fill on average (OKX options)
- **Opportunity cost**: Unfilled orders miss alpha
- **Reorder cost**: Need to repost unfilled quantity (see transaction_cost_model.md)

---

## 📏 Model Comparison

### Backtest: 100 Contracts, Mid = $2,850

| Model | Slippage (per contract) | Total Slippage | Complexity | Data Required |
|-------|-------------------------|----------------|------------|---------------|
| **Spread-based** (2% spread) | $25.00 | $2,500 | Low | Bid/Ask |
| **Depth-based** (3 levels) | $29.00 | $2,900 | Medium | Order book |
| **Impact** (qty/vol = 0.2) | $19.55 | $1,955 | High | Trade history |
| **Maker-only** | $0.00 | $0 | Low | None |

**Observations**:
- **Spread-based**: Simple but overestimates (assumes worst case)
- **Depth-based**: More accurate for medium orders
- **Impact function**: Best for large orders with fitted params
- **Maker-only**: Zero slippage but requires fill probability model

### Recommendation by Order Size

```python
def select_slippage_model(quantity: float, avg_volume: float) -> str:
    """
    Select appropriate slippage model based on order size.

    Args:
        quantity: Order size
        avg_volume: Average market volume

    Returns:
        Model name
    """
    qty_ratio = quantity / avg_volume

    if qty_ratio < 0.05:  # <5% of volume
        return 'spread-based'  # Simple, sufficient accuracy
    elif qty_ratio < 0.20:  # 5-20% of volume
        return 'depth-based'  # Medium accuracy
    else:  # >20% of volume
        return 'impact-function'  # High accuracy needed

# Example
select_slippage_model(quantity=25, avg_volume=500)  # → 'spread-based'
select_slippage_model(quantity=100, avg_volume=500) # → 'depth-based'
select_slippage_model(quantity=200, avg_volume=500) # → 'impact-function'
```

---

## 🔬 Validation & Calibration

### 1. Backtest vs Reality Gap

**Method**: Compare estimated slippage with realized slippage from live trading

```python
def validate_slippage_model(
    estimated: pd.Series,  # Estimated slippage (backtest)
    realized: pd.Series    # Realized slippage (live trading)
) -> dict:
    """
    Validate slippage model accuracy.

    Returns:
        Validation metrics (RMSE, bias, correlation)
    """
    from sklearn.metrics import mean_squared_error, mean_absolute_error

    rmse = np.sqrt(mean_squared_error(realized, estimated))
    mae = mean_absolute_error(realized, estimated)
    bias = (estimated - realized).mean()
    correlation = estimated.corr(realized)

    return {
        'rmse': rmse,
        'mae': mae,
        'bias': bias,  # Positive = overestimate
        'correlation': correlation,
        'rmse_pct': rmse / realized.mean() * 100
    }

# Example
estimated = pd.Series([25, 30, 28, 26, 29])  # Backtest estimates
realized = pd.Series([22, 28, 25, 24, 27])   # Live execution

validation = validate_slippage_model(estimated, realized)
# Result: {'rmse': 2.83, 'bias': 2.4, 'correlation': 0.95}
# → Model overestimates by $2.4 on average (acceptable if conservative)
```

### 2. Calibration

**If model is biased**, recalibrate:

```python
def calibrate_slippage_model(
    estimated: pd.Series,
    realized: pd.Series
) -> float:
    """
    Calibrate slippage model via linear regression.

    Returns:
        Calibration factor (multiply estimates by this)
    """
    from sklearn.linear_model import LinearRegression

    model = LinearRegression(fit_intercept=False)
    model.fit(estimated.values.reshape(-1, 1), realized.values)

    calibration_factor = model.coef_[0]
    return calibration_factor

# Example
calibration_factor = calibrate_slippage_model(estimated, realized)
# Result: 0.87 (reduce estimates by 13%)

# Apply calibration
calibrated_estimates = estimated * calibration_factor
```

---

## ⚙️ Integration with Transaction Cost Model

**See**: `modeling/transaction_cost_model.md`

**Total Transaction Cost**:
```
T-Cost = Fees + Slippage + Partial Fill Impact

where:
  Fees = execution_price × quantity × fee_rate
  Slippage = estimate_slippage(...) × quantity
  Partial Fill Impact = (1 - fill_ratio) × reorder_cost
```

**Example Integration**:
```python
def total_transaction_cost(
    mid_price: float,
    quantity: float,
    side: str,
    order_type: str,  # 'maker' or 'taker'
    spread_pct: float = 0.02,
    fee_rate_maker: float = -0.0002,  # -0.02% maker rebate (VIP9 tier)
    fee_rate_taker: float = 0.0003,   # 0.03% taker fee
    fill_ratio: float = 0.3  # 30% fill ratio (market condition dependent)
) -> dict:
    """
    Calculate total transaction cost (fees + slippage + partial fill).

    Returns:
        Cost breakdown
    """
    if order_type == 'maker':
        # Maker: zero slippage, negative fee, partial fill risk
        slippage = 0
        execution_price = mid_price  # Assume filled at limit
        fee_rate = fee_rate_maker
        partial_fill_impact = (1 - fill_ratio) * (slippage + abs(fee_rate * mid_price))

    else:  # taker
        # Taker: spread slippage, positive fee, full fill
        slippage_per_contract = (mid_price * spread_pct) / 2
        execution_price = mid_price + slippage_per_contract if side == 'buy' else mid_price - slippage_per_contract
        slippage = slippage_per_contract * quantity
        fee_rate = fee_rate_taker
        partial_fill_impact = 0  # Taker fills immediately

    notional = execution_price * quantity
    fees = notional * fee_rate  # Negative if maker rebate

    total_cost = slippage + fees + partial_fill_impact

    return {
        'execution_price': execution_price,
        'slippage': slippage,
        'fees': fees,
        'partial_fill_impact': partial_fill_impact,
        'total_cost': total_cost,
        'total_cost_bps': (total_cost / (mid_price * quantity)) * 10000
    }

# Example: Maker order (VIP9 tier)
cost_maker = total_transaction_cost(
    mid_price=2850,
    quantity=10,
    side='buy',
    order_type='maker',
    spread_pct=0.02,
    fill_ratio=0.3  # 30% fill (market dependent, not tier dependent)
)
# Result: {'slippage': 0, 'fees': -5.7, 'partial_fill_impact': 4.0, 'total_cost': -1.7}
# Net cost: -$1.7 (maker rebate > partial fill cost)

# Example: Taker order
cost_taker = total_transaction_cost(
    mid_price=2850,
    quantity=10,
    side='buy',
    order_type='taker',
    spread_pct=0.02
)
# Result: {'slippage': 250, 'fees': 8.55, 'total_cost': 258.55}
```

---

## 📚 Related Documentation

- **Transaction Cost Model**: `modeling/transaction_cost_model.md` - Full T-cost framework
- **Fill Probability**: `modeling/fill_probability.md` - Maker order fill rates
- **OKX API**: `exchanges/okx/api_reference.md` - Order book endpoint
- **Order Execution**: `exchanges/okx/order_execution.md` - Maker/taker mechanics

---

## ⚠️ Common Mistakes

### 1. Using Spread-based for Maker Orders

**Wrong**:
```python
# Maker order with spread slippage (incorrect)
slippage = (ask - bid) / 2  # ❌ Maker fills at limit, not mid
```

**Correct**:
```python
# Maker order: zero slippage
slippage = 0  # ✅ Filled at limit price
```

### 2. Ignoring Partial Fill Impact

**Wrong**:
```python
# Assume 100% fill (incorrect for maker orders)
cost = fees + slippage  # ❌ Misses 70% unfilled portion
```

**Correct**:
```python
# Account for partial fill
filled_cost = (fees + slippage) * fill_ratio
unfilled_cost = opportunity_cost * (1 - fill_ratio)
total_cost = filled_cost + unfilled_cost  # ✅
```

### 3. Static Slippage Assumption

**Wrong**:
```python
# Fixed slippage for all orders (incorrect)
slippage = 0.001 * mid_price  # ❌ Ignores market conditions
```

**Correct**:
```python
# Dynamic slippage based on spread/depth/volume
if volatility > threshold:
    slippage = estimate_slippage_depth(...)  # ✅ Adapts to conditions
```

---

## 🎯 Checklist: Slippage Model Selection

- [ ] **Order type determined** (maker vs taker)
- [ ] **Order size relative to volume** (<5%, 5-20%, >20%)
- [ ] **Data availability** (spread only, order book, trade history)
- [ ] **Accuracy requirement** (quick estimate vs precise)
- [ ] **Model calibrated** (validated against live execution)
- [ ] **Partial fill accounted for** (maker orders)
- [ ] **Market regime considered** (volatility, liquidity)

---

**Last Updated**: 2025-12-23
**Version**: 1.0
**Maintainer**: sqr

**References**:
- Almgren & Chriss (2000): "Optimal Execution of Portfolio Transactions"
- Kissell & Glantz (2003): "Optimal Trading Strategies"
- OKX execution data (2024-Q4)
