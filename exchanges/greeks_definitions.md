# Greeks Definitions: OKX (PA vs BS) and Deribit

**Last Updated**: 2025-12-23
**Source**: OKX API verification, practical testing
**Importance**: ⭐⭐⭐ Critical - 잘못된 Greeks 사용 = 잘못된 헷지

---

## Problem Statement

**봇이 혼동하는 이유**:
- OKX는 **두 가지 Greeks**를 제공: PA (Practical Approach) vs BS (Black-Scholes)
- **단위가 다름**: PA = BTC, BS = USD
- **값 차이가 수천~수만 배**: Gamma 5만배, Theta 10만배 차이
- 어떤 것을 써야 하는지 명확하지 않음

**결과**: 잘못된 Greeks → 잘못된 헷지 → 손실

---

## OKX: PA (Practical Approach) vs BS (Black-Scholes)

### Summary (결론부터)

| Greek | PA (Practical Approach) | BS (Black-Scholes) | When to Use |
|-------|------------------------|-------------------|-------------|
| **Unit** | **BTC** | **USD** | PA: BTC-margined accounts<br>BS: USD-margined or comparison |
| **Delta** | BTC exposure per BTC price change | USD exposure per $1 price change | PA: Direct hedge size<br>BS: Standard definition |
| **Gamma** | Delta change per BTC price change | Delta change per $1 price change | PA: Rehedge frequency<br>BS: Standard definition |
| **Theta** | **BTC/day** | **USD/day** | PA: Daily PnL in BTC<br>BS: Daily PnL in USD |
| **Vega** | **BTC per 1% IV** | **USD per 1% IV** | PA: IV hedge in BTC<br>BS: IV hedge in USD |

**Critical**:
- **PA × BTC_price ≈ BS** (for Theta, Vega, Delta)
- **Gamma 단위가 다름** (PA는 특이함, 아래 참조)

### Detailed Comparison

#### Example: BTC-USD-251226-84000-C (ATM Call)

**Market Conditions**:
- BTC Forward Price: $88,526
- Distance from ATM: -5.1% (slightly ITM)
- Mark Vol: 45.3%

**Greeks Comparison**:

```
Delta:
  PA:   0.843052 BTC
  BS:   0.897051 (dimensionless, standard)

  Interpretation:
    - BS: BTC 가격 $1 상승 → 옵션 가격 $0.897 상승
    - PA: BTC 가격 1 BTC 상승 → 옵션 가격 0.843 BTC 상승
    - Conversion: PA ≈ BS (already normalized)

Gamma:
  PA:   2.497699 (unit unclear, likely BTC per BTC move)
  BS:   0.0000472 (delta change per $1 BTC move)

  Interpretation:
    - BS: BTC 가격 $1 상승 → Delta가 0.0000472 증가
    - PA: ??? (OKX 문서 불명확)
    - **WARNING: PA Gamma 단위 확인 필요**

Theta:
  PA:  -0.001172 BTC/day
  BS: -110.387250 USD/day

  Interpretation:
    - BS: 하루 지나면 옵션 가격 $110.39 감소
    - PA: 하루 지나면 옵션 가격 0.001172 BTC 감소
    - Conversion: PA × $88,526 = -103.75 USD/day ≈ BS ✅

Vega:
  PA:   0.000169 BTC per 1% IV
  BS:  15.012560 USD per 1% IV

  Interpretation:
    - BS: IV 1% 상승 → 옵션 가격 $15.01 상승
    - PA: IV 1% 상승 → 옵션 가격 0.000169 BTC 상승
    - Conversion: PA × $88,526 = 14.96 USD ≈ BS ✅
```

### Conversion Formula

**BTC → USD**:
```python
theta_usd = theta_pa * btc_price
vega_usd = vega_pa * btc_price
delta_usd = delta_pa * btc_price * contract_size  # For position value
```

**USD → BTC**:
```python
theta_btc = theta_bs / btc_price
vega_btc = vega_bs / btc_price
```

**Verified Accuracy**:
- Theta conversion: PA × BTC_price / BS = **1.05x** (5% error, acceptable)
- Vega conversion: PA × BTC_price / BS = **1.00x** (perfect match ✅)

---

## When to Use Which Greeks

### Use PA (Practical Approach) if:

1. ✅ **BTC-margined account** (most crypto traders)
   - Position sizing in BTC
   - PnL tracked in BTC
   - Margin requirements in BTC

2. ✅ **Direct hedging calculations**
   - "How many BTC do I need to hedge?"
   - "What's my BTC exposure?"

3. ✅ **Daily Theta tracking in BTC**
   - Portfolio decay in BTC terms
   - "How much BTC am I losing per day?"

**Example**:
```python
# Portfolio: Long 10 BTC call options
theta_pa = -0.001172 BTC/day per contract

# Daily decay
daily_decay_btc = 10 * theta_pa
# = -0.01172 BTC/day

# After 7 days
weekly_decay_btc = daily_decay_btc * 7
# = -0.08204 BTC
```

### Use BS (Black-Scholes) if:

1. ✅ **USD-margined account** (traditional)
   - USDT/USDC collateral
   - PnL in USD

2. ✅ **Academic comparison**
   - Comparing with traditional finance
   - Standard textbook formulas

3. ✅ **Cross-exchange comparison**
   - Different exchanges use different units
   - BS is more standardized

4. ✅ **Implied Volatility calculations**
   - BS model assumptions
   - IV surface modeling

**Example**:
```python
# Portfolio: Long 10 BTC call options
theta_bs = -110.39 USD/day per contract

# Daily decay
daily_decay_usd = 10 * theta_bs
# = -$1,103.90/day

# After 7 days
weekly_decay_usd = daily_decay_usd * 7
# = -$7,727.30
```

---

## Deribit Greeks

### ⚠️ Status: Pending Verification

**Known**:
- Deribit is BTC-margined only
- Likely uses **BTC-denominated Greeks** (similar to OKX PA)
- Need API verification (currently blocked)

**TODO**:
```bash
# Verify Deribit Greeks units
curl "https://deribit.com/api/v2/public/ticker?instrument_name=BTC-27DEC24-90000-C"

# Check fields:
# - greeks.delta (BTC or dimensionless?)
# - greeks.gamma (BTC or standard?)
# - greeks.theta (BTC/day or USD/day?)
# - greeks.vega (BTC per 1% IV or USD?)
```

**Hypothesis** (to be verified):
- Deribit Greeks = BTC units (like OKX PA)
- No USD Greeks (since Deribit is BTC-only)
- Direct comparison: Deribit Greeks ≈ OKX PA Greeks

**Update this section after verification** ⚠️

---

## Backtest Implications

### 1. Theta Decay Simulation

**MUST specify unit**:

```python
def calculate_theta_decay(position, days_elapsed, btc_price, greeks_type='PA'):
    """
    Calculate theta decay for options position.

    Args:
        position: Option position
        days_elapsed: Days passed
        btc_price: Current BTC price
        greeks_type: 'PA' or 'BS'

    Returns:
        decay: Theta decay (in BTC if PA, USD if BS)
    """
    if greeks_type == 'PA':
        # PA theta is in BTC/day
        theta_per_day_btc = position.theta_pa
        total_decay_btc = theta_per_day_btc * days_elapsed
        return total_decay_btc

    elif greeks_type == 'BS':
        # BS theta is in USD/day
        theta_per_day_usd = position.theta_bs
        total_decay_usd = theta_per_day_usd * days_elapsed
        return total_decay_usd

    else:
        raise ValueError(f"Unknown greeks_type: {greeks_type}")

# Example
position_theta_pa = -0.001172  # BTC/day
days = 7
decay_btc = position_theta_pa * days
# = -0.008204 BTC

# Convert to USD if needed
decay_usd = decay_btc * btc_price
# = -0.008204 * 88526 = -$726.38
```

### 2. Delta Hedging

**Use PA for BTC-margined**:

```python
def calculate_hedge_size(position, greeks_type='PA'):
    """
    Calculate hedge size for delta-neutral position.

    For BTC-margined accounts, use PA delta (BTC units).
    For USD-margined accounts, use BS delta (USD units).
    """
    if greeks_type == 'PA':
        # PA delta is in BTC
        delta_btc = position.delta_pa * position.quantity
        hedge_size_btc = -delta_btc  # Opposite side
        return hedge_size_btc

    elif greeks_type == 'BS':
        # BS delta is dimensionless (0-1)
        # Need to convert to USD notional
        delta_ratio = position.delta_bs
        contract_notional_usd = position.quantity * btc_price
        delta_usd = delta_ratio * contract_notional_usd
        hedge_size_usd = -delta_usd
        return hedge_size_usd

# Example: Long 10 call options
# Delta (PA) = 0.843 BTC per contract
# Delta (BS) = 0.897 (dimensionless)

# BTC-margined hedge
hedge_btc = -0.843 * 10
# = -8.43 BTC (short 8.43 BTC in futures)

# USD-margined hedge
hedge_usd = -0.897 * 10 * 88526
# = -$793,998 (short ~$794k in futures)
```

### 3. Gamma Scalping

**WARNING: PA Gamma unit unclear**

```python
# Use BS Gamma for standard calculations
gamma_bs = 0.0000472  # Delta change per $1 BTC move

# If BTC moves $1000
btc_move = 1000
delta_change = gamma_bs * btc_move
# = 0.0472 (Delta increases by 4.72%)

# Rehedge needed
rehedge_size_btc = delta_change * position_quantity
```

**Do NOT use PA Gamma** until unit is clarified ⚠️

---

## Common Mistakes

### ❌ Mistake 1: Mixing PA and BS

```python
# Bad (mixing units)
theta_pa = -0.001172  # BTC/day
btc_price = 88526
daily_decay = theta_pa  # WRONG: Forgot to convert

# Good (consistent units)
theta_pa_btc = -0.001172  # BTC/day
theta_pa_usd = theta_pa_btc * btc_price  # USD/day
# = -103.75 USD/day
```

### ❌ Mistake 2: Assuming BS = Standard

```python
# Bad (assuming BS is always right)
vega_bs = 15.01  # USD per 1% IV
# Using this for BTC-margined account → Wrong units

# Good (use correct Greek for account type)
if account_margin_currency == 'BTC':
    vega = vega_pa  # BTC per 1% IV
else:
    vega = vega_bs  # USD per 1% IV
```

### ❌ Mistake 3: Ignoring BTC Price Changes

```python
# Bad (using stale BTC price for conversion)
theta_pa = -0.001172 BTC/day
btc_price_yesterday = 88000
theta_usd = theta_pa * btc_price_yesterday  # WRONG: Stale price

# Good (use current BTC price)
theta_pa = -0.001172 BTC/day
btc_price_now = get_current_btc_price()
theta_usd = theta_pa * btc_price_now
```

### ❌ Mistake 4: Using PA Gamma blindly

```python
# Bad (PA Gamma unit unclear)
gamma_pa = 2.498
position_change = gamma_pa * btc_move  # WRONG: Unit unknown

# Good (use BS Gamma for standard calculations)
gamma_bs = 0.0000472
delta_change = gamma_bs * btc_move_usd
```

---

## API Fields Reference

### OKX `/api/v5/public/opt-summary`

```json
{
  "delta": 0.843052,          // PA: BTC units
  "deltaBS": 0.897051,        // BS: dimensionless (standard)

  "gamma": 2.497699,          // PA: ⚠️ Unit unclear
  "gammaBS": 0.0000472,       // BS: delta change per $1 BTC move

  "theta": -0.001172,         // PA: BTC/day
  "thetaBS": -110.387,        // BS: USD/day

  "vega": 0.000169,           // PA: BTC per 1% IV
  "vegaBS": 15.0126,          // BS: USD per 1% IV

  "fwdPx": 88526.11           // BTC forward price (for conversion)
}
```

### Deribit `/api/v2/public/ticker` (Pending Verification)

```json
{
  "greeks": {
    "delta": 0.xxx,           // ⚠️ BTC or dimensionless? (TODO)
    "gamma": 0.xxx,           // ⚠️ Unit? (TODO)
    "theta": -0.xxx,          // ⚠️ BTC/day or USD/day? (TODO)
    "vega": 0.xxx             // ⚠️ BTC or USD per 1% IV? (TODO)
  }
}
```

---

## Agent Protocol: Greeks Usage

### BEFORE using Greeks:

1. ✅ **Check exchange**: OKX (PA/BS), Deribit (?), Binance (?)
2. ✅ **Check account margin currency**: BTC or USD/USDT
3. ✅ **Choose correct Greek**:
   - BTC-margined → Use PA (OKX) or native (Deribit)
   - USD-margined → Use BS (OKX)
4. ✅ **Get current BTC price** for conversions
5. ✅ **Document which Greek used** in logs

### DURING calculations:

6. ✅ **Specify units explicitly**:
   ```python
   theta_decay_btc = theta_pa * days  # BTC
   theta_decay_usd = theta_decay_btc * btc_price  # USD
   ```

7. ✅ **Avoid PA Gamma** (unit unclear)
8. ✅ **Log conversions**:
   ```python
   logger.info(f"Theta (PA): {theta_pa:.6f} BTC/day")
   logger.info(f"Theta (USD): {theta_pa * btc_price:.2f} USD/day")
   logger.info(f"BTC Price: ${btc_price:,.2f}")
   ```

### AFTER backtest:

9. ✅ **Report in both units** (BTC and USD)
10. ✅ **Verify conversions**: PA × BTC_price ≈ BS (within 5%)

### Example Dialogue:

```
User: "옵션 포트폴리오 Theta 얼마야?"

Agent:
  [Reads knowledge/exchanges/greeks_definitions.md]
  [Checks account type: BTC-margined]
  [Uses PA Greeks]

  "포트폴리오 Theta (2025-12-23):

  | Contract | Quantity | Theta (PA) | Theta (USD) |
  |----------|----------|------------|-------------|
  | BTC-251226-84000-C | 10 | -0.0117 BTC/day | -$1,036/day |
  | BTC-251226-90000-C | -5 | +0.0043 BTC/day | +$381/day |
  | Total | | -0.0074 BTC/day | -$655/day |

  BTC Price: $88,526
  Conversion: -0.0074 × $88,526 = -$655 ✅

  📚 출처: knowledge/exchanges/greeks_definitions.md (PA Greeks for BTC-margined)"
```

---

## Next Steps (TODO)

1. ⚠️ **Verify Deribit Greeks units** (API currently blocked)
   - Delta: BTC or dimensionless?
   - Gamma: BTC or standard?
   - Theta: BTC/day or USD/day?
   - Vega: BTC or USD per 1% IV?

2. ⚠️ **Clarify OKX PA Gamma unit**
   - Contact OKX support
   - Reverse-engineer from position changes
   - Compare with BS Gamma × BTC_price

3. ✅ **Add to other exchanges** as needed
   - Binance Options (if used)
   - Bybit Options (if used)

4. ✅ **Create unit conversion utility**
   ```python
   # ~/knowledge/exchanges/greeks_converter.py
   def convert_greeks(greeks, from_type, to_type, btc_price):
       """Convert between PA and BS Greeks."""
       # Implementation
   ```

---

## References

- **OKX API**: `/api/v5/public/opt-summary` (verified 2025-12-23)
- **Verification Script**: `/tmp/verify_hypothesis.py` (Theta/Vega conversion: 1.00-1.05x ✅)
- **Related KB**:
  - [Options Specifications](okx/options_specifications.md) - Expiry, settlement
  - [Performance Metrics](../experiments/performance_metrics.md) - PnL calculation

---

**Version**: 1.0
**Critical**: OKX PA = BTC units, BS = USD units. Always check account margin currency.
**Status**: Deribit pending verification ⚠️
