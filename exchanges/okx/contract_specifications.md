# OKX Contract Specifications

**Last Updated**: 2025-12-22
**Source**: OKX API, official docs
**Importance**: ⭐⭐⭐ Critical - 주문 전 필수 확인

---

## Overview

**Contract specifications** = 거래 가능한 최소/최대 단위, 가격 단위

**Why Critical**: 잘못된 주문 → 거부 or 예상과 다른 체결

---

## Futures Contracts

### Contract Structure

**Symbol Format**:
```
{COIN}-{SETTLEMENT_CURRENCY}-{EXPIRY}

Examples:
  BTC-USD-SWAP        # Perpetual (no expiry)
  BTC-USD-250328      # Quarterly (expires 2025-03-28)
  BTC-USDT-SWAP       # USDT-margined perpetual
```

### Contract Multiplier

**BTC Futures**:
- 1 contract = **1 BTC** exposure
- Example: 10 contracts @ $50,000 = $500,000 notional

**ETH Futures**:
- 1 contract = **1 ETH** exposure
- Example: 100 contracts @ $3,000 = $300,000 notional

**Alt Futures** (varies by coin):
- Check API: `GET /api/v5/public/instruments?instType=FUTURES`

### Tick Size (최소 가격 변동)

**BTC/ETH Futures**:
```
Tick Size: $0.1

Valid prices: $50,000.0, $50,000.1, $50,000.2, ...
Invalid: $50,000.05 (not multiple of $0.1)
```

**Verify**: API response field `tickSz`

### Lot Size (최소 주문 수량)

**BTC/ETH Futures**:
```
Lot Size: 1 contract

Valid quantities: 1, 2, 3, ...
Invalid: 0.5, 1.5 (must be integer multiples)
```

**Verify**: API response field `lotSz`

### Order Size Limits

**Min Order Size**:
```
BTC Futures: 1 contract (minimum)
ETH Futures: 1 contract
```

**Max Order Size** (single order):
```
BTC Futures: 10,000 contracts (typical)
ETH Futures: 50,000 contracts

Note: Varies by market conditions
```

**Max Position Size** (total):
```
Tier-based (see Position Limits section)

Example (BTC):
  Tier 1 (0-50 BTC): 50 BTC max
  Tier 2 (50-200 BTC): 200 BTC max
  Tier 3 (200-500 BTC): 500 BTC max
  ...
```

---

## Options Contracts

### Contract Structure

**Symbol Format**:
```
{UNDERLYING}-{CURRENCY}-{EXPIRY}-{STRIKE}-{TYPE}

Examples:
  BTC-USD-250131-50000-C   # Call
  BTC-USD-250131-50000-P   # Put
```

### Contract Multiplier

**BTC Options**:
- 1 contract = **1 BTC** exposure
- Premium quoted in **BTC** or **USD** (check `quoteCcy`)

**Example**:
```
Buy 10 BTC-USD-250131-50000-C @ 0.05 BTC premium

Position:
  - 10 call options
  - 50,000 strike
  - Premium paid: 10 * 0.05 = 0.5 BTC ($25,000 @ $50k BTC)
  - Max loss: 0.5 BTC (premium)
  - Max gain: Unlimited
```

### Tick Size (Options)

**Depends on option price**:
```
Option Price < 0.01 BTC:  Tick = 0.0001 BTC
Option Price >= 0.01 BTC: Tick = 0.0005 BTC

Example:
  Premium = 0.005 BTC  → Tick = 0.0001 BTC
  Premium = 0.05 BTC   → Tick = 0.0005 BTC
```

**Verify**: API `/api/v5/public/instruments?instType=OPTION`

### Lot Size (Options)

```
BTC Options: 1 contract minimum
ETH Options: 1 contract minimum
```

### Strike Price Intervals

**BTC Options**:
```
ATM ± 10%: $500 intervals
  (e.g., 49500, 50000, 50500)

ATM ± 10-20%: $1,000 intervals
  (e.g., 45000, 46000, 47000)

Deep OTM (>20%): $2,000 - $5,000 intervals
```

**Dynamic**: OKX adjusts based on volatility

---

## Position Limits

### Per-Contract Limits

**Futures** (approximate, verify with API):
```
BTC-USD-SWAP: 10,000 - 50,000 contracts
ETH-USD-SWAP: 50,000 - 200,000 contracts
```

### Per-Account Limits (Tier-Based)

**Example: BTC Futures**

| Tier | Position Size | Max Leverage | Maintenance Margin |
|------|--------------|--------------|-------------------|
| 1 | 0 - 50 BTC | 100× | 0.5% |
| 2 | 50 - 200 BTC | 50× | 1% |
| 3 | 200 - 500 BTC | 20× | 2.5% |
| 4 | 500 - 1000 BTC | 10× | 5% |
| 5 | 1000+ BTC | 5× | 10% |

**Implications**:
- As position grows → Leverage auto-reduces
- Maintenance margin increases
- Liquidation risk increases

**Check Current Limits**:
```bash
GET /api/v5/account/max-size?instId=BTC-USD-SWAP
```

### Options Position Limits

**Single Option Contract**:
```
BTC: 5,000 - 10,000 contracts (typical)
ETH: 10,000 - 50,000 contracts
```

**Total Open Interest** (across all strikes/expiries):
```
Risk-based calculation (portfolio margin)
No hard limit, but margin requirements increase
```

---

## Trading Restrictions

### Minimum Notional Value

**Futures**:
```
Minimum order value: ~$10 - $100 (varies)

Example: BTC @ $50,000
  Min: 1 contract * $50,000 = $50,000 notional (OK)
```

**Options**:
```
No strict minimum (premium can be tiny)

Example: Deep OTM put @ 0.0001 BTC
  1 contract * 0.0001 * $50,000 = $5 notional (OK)
```

### Price Limit (Circuit Breaker)

**Max price deviation from mark price**:
```
±5% - ±10% (depending on instrument)

Example: BTC Mark = $50,000
  Max bid: $55,000 (+10%)
  Min ask: $45,000 (-10%)
```

**Order rejected if**:
- Limit price > 110% of mark (buy)
- Limit price < 90% of mark (sell)

### Self-Trade Prevention

**OKX Default**: Cancel both orders if self-match

**Options**:
- Cancel taker (keep maker)
- Cancel maker (keep taker)
- Cancel both

---

## Backtest Implications

### 1. Order Validation

```python
def validate_order(symbol, side, price, quantity):
    """
    Validate order against contract specs.

    Returns:
        is_valid: bool
        error_msg: str (if invalid)
    """
    specs = get_contract_specs(symbol)  # From API or cached

    # Check tick size
    if price % specs['tick_size'] != 0:
        return False, f"Price {price} not multiple of tick size {specs['tick_size']}"

    # Check lot size
    if quantity % specs['lot_size'] != 0:
        return False, f"Quantity {quantity} not multiple of lot size {specs['lot_size']}"

    # Check min/max
    if quantity < specs['min_size']:
        return False, f"Quantity {quantity} below minimum {specs['min_size']}"

    if quantity > specs['max_size']:
        return False, f"Quantity {quantity} above maximum {specs['max_size']}"

    # Check position limits (simplified)
    current_position = get_position(symbol)
    new_position = current_position + (quantity if side == 'buy' else -quantity)

    if abs(new_position) > specs['position_limit']:
        return False, f"Position {new_position} exceeds limit {specs['position_limit']}"

    return True, ""

# In backtest
is_valid, error = validate_order('BTC-USD-SWAP', 'buy', 50000.0, 10)
if not is_valid:
    logger.error(f"Order rejected: {error}")
    # Don't execute trade in backtest
```

### 2. Tier-Based Leverage Adjustment

```python
def calculate_effective_leverage(position_size_btc):
    """
    Calculate effective leverage based on position tier.

    OKX reduces leverage as position grows.
    """
    tiers = [
        (50, 100),    # 0-50 BTC: 100× max
        (200, 50),    # 50-200 BTC: 50× max
        (500, 20),    # 200-500 BTC: 20× max
        (1000, 10),   # 500-1000 BTC: 10× max
        (float('inf'), 5)  # 1000+ BTC: 5× max
    ]

    for threshold, max_lev in tiers:
        if position_size_btc <= threshold:
            return max_lev

    return 5  # Default minimum

# Backtest check
position_size = 250  # BTC
max_leverage = calculate_effective_leverage(position_size)
# Returns 20× (Tier 3)

# If strategy uses 50× → ERROR, not realistic
```

### 3. Strike Price Availability

```python
def get_available_strikes(underlying_price, dte):
    """
    Estimate which strikes are available.

    OKX provides strikes around ATM with varying intervals.
    """
    strikes = []

    # ATM ± 10%: $500 intervals
    atm = round(underlying_price / 500) * 500
    for i in range(-20, 21):  # ±10%
        strike = atm + i * 500
        strikes.append(strike)

    # ATM ± 10-20%: $1000 intervals
    for i in range(-40, -20):  # -20% to -10%
        strike = atm + i * 500
        if strike % 1000 == 0:
            strikes.append(strike)

    for i in range(21, 41):  # +10% to +20%
        strike = atm + i * 500
        if strike % 1000 == 0:
            strikes.append(strike)

    return sorted(set(strikes))

# Backtest: Only trade strikes that actually exist
available = get_available_strikes(underlying_price=50000, dte=7)
# [45000, 46000, ..., 49500, 50000, 50500, ..., 55000]

# If strategy tries to trade 50250 strike → Not available, skip
```

---

## Common Mistakes

1. ❌ **"Any price is valid"**
   - ✅ Must be multiple of tick size
   - ✅ Backtest with price rounding: `price = round(price / tick_size) * tick_size`

2. ❌ **"Can trade fractional contracts"**
   - ✅ Futures/Options: Integer contracts only
   - ✅ Backtest: `quantity = int(quantity)`

3. ❌ **"Position limits don't matter in backtest"**
   - ✅ Large backtests can exceed limits
   - ✅ Simulate tier-based leverage reduction

4. ❌ **"All strikes available"**
   - ✅ OKX only lists ~50-100 strikes per expiry
   - ✅ Deep OTM may not exist

5. ❌ **"Order size doesn't affect leverage"**
   - ✅ Tier-based: 1000 BTC position = max 5× leverage (not 100×)

---

## Agent Protocol: Contract Specs Check

**BEFORE placing order (backtest or live):**

1. ✅ Read contract specs (API or KB)
2. ✅ Validate price (tick size)
3. ✅ Validate quantity (lot size, min/max)
4. ✅ Check position limit
5. ✅ Calculate effective leverage (tier-based)
6. ✅ Verify strike exists (options)

**Example**:
```
User: "50 BTC @ $50,000.05 매수"

Agent:
  [1] Reads knowledge/exchanges/okx/contract_specifications.md
  [2] Checks tick size: $0.1
  [3] Detects: $50,000.05 invalid (not multiple of $0.1)
  [4] Responds:

  "❌ 주문 불가: 가격 $50,000.05는 tick size $0.1의 배수가 아닙니다.

   올바른 가격:
   - $50,000.0 ✅
   - $50,000.1 ✅

   📚 출처: knowledge/exchanges/okx/contract_specifications.md"
```

---

## References

- **OKX API - Instruments**: `GET /api/v5/public/instruments`
- **OKX Trading Specs**: https://www.okx.com/trade-info
- **Related KB**:
  - [Margin & Leverage](margin_and_leverage.md) - Position tier limits
  - [Fee Structure](fee_structure.md) - Trading costs
- **Verification**: Always check API for latest specs (updated frequently)

---

**Version**: 1.0
**Critical**: Validate every order. Invalid orders = backtest unrealistic.
