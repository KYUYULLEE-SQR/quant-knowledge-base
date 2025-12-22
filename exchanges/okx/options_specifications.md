# OKX Options Specifications

**Last Updated**: 2025-12-22
**Source**: OKX API docs (https://www.okx.com/docs-v5/en/#options-trading), user verification needed
**Importance**: Critical for backtest accuracy (expiry, Greeks, settlement)

---

## ⚠️ IMPORTANT: Verify with Official Docs

**This KB is a summary. ALWAYS verify critical details at:**
- https://www.okx.com/docs-v5/en/#options-trading
- https://www.okx.com/trade-info/options

**Agent Protocol**:
1. Read this KB for quick reference
2. If user asks specific question (e.g., "만기일 정확히 언제?") → Check official docs
3. If discrepancy found → Update this KB + notify user

---

## Contract Specifications

### Symbol Format
```
{UNDERLYING}-{CURRENCY}-{EXPIRY}-{STRIKE}-{TYPE}

Examples:
  BTC-USD-250131-50000-C   # BTC Call, expires 2025-01-31, strike $50,000, USD-settled
  BTC-USD-250131-50000-P   # BTC Put, expires 2025-01-31, strike $50,000, USD-settled
  ETH-USD-250228-3000-C    # ETH Call, expires 2025-02-28, strike $3,000
```

### Contract Size
- **1 contract** = Option on 1 unit of underlying
  - BTC options: 1 contract = 1 BTC exposure
  - ETH options: 1 contract = 1 ETH exposure

### Settlement Currency
- **USD-margined**: Settled in USD (USDT/USDC)
- **Coin-margined**: Settled in underlying (BTC/ETH)

**User's account**: Likely USD-margined (verify in account settings)

---

## Expiry & Settlement

### ⚠️ CRITICAL: Expiry Time

**VERIFIED with OKX API** (2025-12-22): OKX options expiry time is **UTC 08:00** ✅
- Verified via `/api/v5/public/instruments` endpoint
- All 646 BTC-USD options expire at 08:00:00 UTC
- Consistent across weekly, monthly, quarterly contracts

**Confirmed expiry time**:
```
UTC: 08:00 (8:00 AM)
KST: 17:00 (5:00 PM, UTC+9)
EST: 03:00 (3:00 AM, UTC-5)
```

**Expiry Structure**:

OKX options have three expiry types, all at **UTC 08:00**:

1. **Daily Expiry**: 매일 08:00 UTC
2. **Weekly Expiry**: 매주 금요일 08:00 UTC
3. **Monthly Expiry**: 매달 마지막 금요일 08:00 UTC

**Tenor Terminology** (정확한 용어):

| Tenor | Definition | Notes |
|-------|-----------|-------|
| **Front day (FD)** | 가장 가까운 daily expiry | 오늘 or 내일 |
| **Front week (FW)** | 가장 가까운 weekly expiry | 이번주 금요일 |
| **Front month (FM)** | 가장 가까운 monthly expiry | 이번달 마지막 금요일 (아직 만기 안됨) |
| **Second day** | FD 다음 daily expiry | |
| **Second week** | FW 다음 weekly expiry | 다음주 금요일 |
| **Third week** | Second week 다음 | |
| ... | (계속) | |

**⚠️ 중요**:
- 금요일 당일: **Front day = Front week** (같은 만기)
- 마지막 금요일 당일: **Front day = Front week = Front month** (모두 같음)
- ❌ **"Next week (NW)"** 같은 용어는 존재하지 않음 (쓰지 말 것)

**Example** (2025-12-23 월요일 기준):
```
Today: 2025-12-23 (월)

Front day: 2025-12-24 (화) 08:00 UTC
Front week: 2025-12-27 (금) 08:00 UTC  ← 이번주 금요일
Front month: 2026-01-31 (금) 08:00 UTC ← 1월 마지막 금요일

Second day: 2025-12-25 (수) 08:00 UTC
Second week: 2026-01-03 (금) 08:00 UTC ← 다음주 금요일
```

**Example** (2025-12-27 금요일 당일 기준):
```
Today: 2025-12-27 (금)

Front day = Front week: 2025-12-27 (금) 08:00 UTC ← 같은 만기!
Front month: 2026-01-31 (금) 08:00 UTC

Second day: 2025-12-28 (토) 08:00 UTC
Second week: 2026-01-03 (금) 08:00 UTC
```

### Settlement Process

**At expiry (UTC 08:00)**:
1. **Index price snapshot** taken at expiry time
2. **ITM options** automatically exercised
3. **OTM options** expire worthless
4. **Settlement PnL** = Intrinsic value - Premium paid

**Settlement calculation**:
```python
# Call option
intrinsic_value = max(0, settlement_price - strike_price)

# Put option
intrinsic_value = max(0, strike_price - settlement_price)

# PnL = intrinsic_value - premium_paid
```

**Example**:
```
Long Call: BTC-USD-250131-50000-C
Purchase price: 0.05 BTC (premium)
Settlement price at expiry: $52,000

Intrinsic value = max(0, 52000 - 50000) = $2,000
Premium paid = 0.05 BTC * $52,000 = $2,600
PnL = $2,000 - $2,600 = -$600 (loss)

Note: Need to convert BTC premium to USD for P&L calculation
      (depends on contract quote currency)
```

### Early Exercise

**American vs European**:
- OKX options: **European-style** (no early exercise)
- Can only be exercised at expiry
- Before expiry: Close by selling the option

---

## Greeks

### Source of Greeks

**OKX provides Greeks via API**:
```python
# GET /api/v5/public/option-summary
# Returns: delta, gamma, theta, vega for each option contract
```

**⚠️ Important**: OKX Greeks ≠ Black-Scholes Greeks
- OKX uses proprietary model (likely adjusted for skew, smile)
- Greeks update in real-time
- **Do NOT calculate Greeks yourself** in backtest (use OKX's)

### Greeks Definitions (OKX)

**Delta (Δ)**:
- Call: 0 to 1
- Put: -1 to 0
- Measures: Price change per $1 move in underlying

**Gamma (Γ)**:
- Always positive (for long options)
- Measures: Delta change per $1 move
- Peaks at ATM, decays as expiry approaches

**Theta (Θ)**:
- Always negative (for long options)
- Measures: Price decay per day (time value erosion)
- **OKX definition**: Expected mark price change in 24 hours (all else equal)

**Vega (ν)**:
- Always positive (for long options)
- Measures: Price change per 1% IV move

### Greeks in Backtest

**CRITICAL**: Use historical Greeks from OKX, NOT calculated Greeks

```python
# ❌ BAD: Calculate Greeks yourself
from scipy.stats import norm

def black_scholes_delta(S, K, T, r, sigma):
    d1 = (np.log(S/K) + (r + 0.5*sigma**2)*T) / (sigma*np.sqrt(T))
    return norm.cdf(d1)

delta = black_scholes_delta(S=50000, K=50000, T=7/365, r=0.05, sigma=0.6)
# This will NOT match OKX's delta (different model, skew, etc.)
```

```python
# ✅ GOOD: Use OKX historical Greeks
# Store Greeks at every timestamp in your database

# micky database (example)
CREATE TABLE options_greeks (
    timestamp TIMESTAMP,
    symbol VARCHAR(50),
    delta FLOAT,
    gamma FLOAT,
    theta FLOAT,
    vega FLOAT,
    mark_price FLOAT,
    underlying_price FLOAT
);

# In backtest: Fetch historical Greeks
greeks = fetch_greeks(symbol='BTC-USD-250131-50000-C', timestamp='2024-10-05 12:00:00')
delta = greeks['delta']  # Use OKX's delta, not calculated
```

**Why this matters**:
- OKX Greeks reflect actual market (skew, smile, supply/demand)
- Black-Scholes assumes flat IV (unrealistic)
- Mismatch can cause 10-20% error in delta hedging

---

## Pricing & Quotes

### Mark Price
**Mark price** = Fair value price used for liquidation and unrealized PnL

**OKX Mark Price Formula**:
```
Mark Price = Index Price × (1 + Basis)
```
- **Index Price**: Weighted average of spot prices (e.g., BTC index)
- **Basis**: Options-specific basis (derived from order book)

**Mark price used for**:
- Unrealized PnL calculation
- Liquidation triggers
- Margin requirements

### Bid/Ask Spread

**Typical spreads** (varies by moneyness and volume):
- ATM options: 1-2% of mark price
- 10% OTM: 2-5%
- 20%+ OTM: 5-10% (or wider)

**Example**:
```
BTC-USD-250131-50000-C (ATM)
  Mark price: 0.05 BTC
  Bid: 0.049 BTC
  Ask: 0.051 BTC
  Spread: 0.002 BTC (4% of mark)
```

### Tick Size

**Minimum price increment**:
- Depends on option price
- Typically: 0.0001 BTC (for BTC options)

**Verify**: Check API response or https://www.okx.com/trade-info/options

---

## Trading Hours

**OKX Options**: 24/7 trading (no downtime except maintenance)

**Maintenance windows** (rare):
- Usually announced 24h in advance
- Typically <30 minutes

---

## Position Limits & Margin

### Position Limits

**Per contract**: Varies (check API)
- Typical: 10,000-50,000 contracts per option

**Per account**: Risk-based (depends on margin tier)

### Margin Requirements

**Initial Margin**: Required to open position
**Maintenance Margin**: Required to keep position open

**Calculation** (simplified):
```
Margin = max(
    Premium,
    Underlying_Price * (Margin_Rate + |Delta|) - OTM_Amount
)
```

**Margin rates**: Vary by tier (VIP9 likely has lower rates)

**Verify**: Use API endpoint `/api/v5/account/max-size` to check available size

---

## Backtest Implications

### 1. Expiry Handling

**CRITICAL**: Close positions BEFORE expiry in backtest (unless modeling settlement)

```python
# Recommended: Close 1 day before expiry
EXPIRY_CLOSE_DAYS = 1

if days_to_expiry <= EXPIRY_CLOSE_DAYS:
    close_position(reason='approaching_expiry')
```

**Why**:
- Greeks unreliable <24h to expiry (gamma explosion)
- Spreads widen significantly
- Settlement price may differ from mark price
- Easier to model: avoid settlement logic complexity

### 2. Greeks Tracking

**MANDATORY**: Store historical Greeks in database

```python
# Backtest loop
for timestamp in backtest_period:
    # Fetch historical Greeks (from DB, not calculated)
    greeks = db.query(f"SELECT * FROM options_greeks WHERE timestamp='{timestamp}'")

    # Use OKX Greeks for delta hedging, PnL attribution
    portfolio_delta = sum(position.size * greeks[position.symbol]['delta'])
```

### 3. Theta Decay

**Model theta decay** using OKX's theta (not Black-Scholes)

```python
# Daily mark-to-market with theta decay
mtm_pnl = (current_mark_price - prev_mark_price) * position_size
theta_pnl = greeks['theta'] * position_size  # Theta = $/day

total_pnl = mtm_pnl + theta_pnl
```

**Common mistake**: Assuming theta is constant or linear
- ✅ Theta accelerates near expiry
- ✅ Use actual historical theta from OKX

---

## Common Mistakes (Agents)

1. ❌ **"Expiry is at midnight"**
   - ✅ UTC 08:00 (verify!)

2. ❌ **"I can calculate Greeks with Black-Scholes"**
   - ✅ Use OKX's historical Greeks (reflects market reality)

3. ❌ **"Options can be exercised early"**
   - ✅ OKX options are European (exercise only at expiry)

4. ❌ **"Theta decay is linear"**
   - ✅ Accelerates near expiry (use OKX's theta)

5. ❌ **"Holding through expiry is fine in backtest"**
   - ✅ Complex settlement logic, recommend closing 1 day before

6. ❌ **"Don't need to verify API docs"**
   - ✅ **ALWAYS verify** critical specs (expiry time, settlement, Greeks formula)

---

## Agent Protocol: Options Specs Verification

**BEFORE using options specs in backtest:**

1. ✅ Read this KB file (quick reference)
2. ✅ Identify critical details needed:
   - Expiry time → Check official docs
   - Greeks → Confirm OKX provides historical Greeks
   - Settlement → Understand cash vs physical
3. ✅ Use WebFetch to verify:
   ```
   WebFetch(
       url='https://www.okx.com/docs-v5/en/#options-trading',
       prompt='What is the exact expiry time for OKX options?'
   )
   ```
4. ✅ If KB outdated → Update + notify user
5. ✅ Cite sources in response

**Example**:
```
User: "OKX 옵션 만기일 정확히 언제야?"

Agent:
  [1] Reads this KB file → "UTC 08:00 (assumed)"
  [2] Sees "⚠️ User must verify"
  [3] Uses WebFetch on https://www.okx.com/docs-v5/en/#options-trading
  [4] Confirms: UTC 08:00
  [5] Responds:

  "OKX 옵션 만기일은 **UTC 08:00** (KST 17:00)입니다.

   확인 출처:
   - https://www.okx.com/docs-v5/en/#options-trading
   - knowledge/exchanges/okx/options_specifications.md

   백테스트 시:
   - 만기 1일 전 청산 권장 (settlement 로직 복잡도 회피)
   - Greeks 만기 24시간 내 불안정 (gamma explosion)"
```

---

## References

- **OKX Options Trading Docs**: https://www.okx.com/docs-v5/en/#options-trading
- **OKX Trade Info**: https://www.okx.com/trade-info/options
- **API Endpoint (Greeks)**: `GET /api/v5/public/option-summary`
- **Related KB**:
  - [Fee Structure](fee_structure.md)
  - [Order Execution](order_execution.md)
- **User conversation**: 2025-12-22 (specs verification reminder)

---

**Version**: 1.0
**Next Action**: User should verify expiry time and update this KB with exact spec
