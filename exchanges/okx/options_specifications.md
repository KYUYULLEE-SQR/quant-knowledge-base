# OKX Options Specifications (옵션 상세 스펙)

**Exchange**: OKX
**Last Updated**: 2025-12-24
**Status**: ✅ Verified via API docs + WebSearch

---

## Quick Summary (핵심 3줄)

- **Contract Size**: BTC = 0.01 BTC, ETH = 0.1 ETH per contract (inverse settlement)
- **Min Order**: 1 contract, Qty Step = 1 contract, Tick Size = 0.0001 BTC or 0.0005 ETH
- **Settlement**: European-style, auto-exercise at UTC 08:00, inverse (settled in underlying)

---

## 1. Contract Specifications (계약 스펙)

### Contract Value (`ctVal`) ⭐ CRITICAL

| Underlying | Contract Size (`ctVal`) | Physical Meaning |
|------------|------------------------|------------------|
| BTC        | 0.01 BTC               | 1 contract = 권리행사 시 0.01 BTC 인도/수령 |
| ETH        | 0.1 ETH                | 1 contract = 권리행사 시 0.1 ETH 인도/수령 |

**물리적 의미**:
- BTC 옵션 1 contract 매수 = BTC 0.01개에 대한 권리 보유
- Strike $100,000 BTC Call 1 contract = 만기 시 $100,000에 0.01 BTC 살 권리
- **Notional value** = `ctVal * strike * contracts`
  - Example: 100 contracts @ strike $100,000 = 0.01 * 100,000 * 100 = $100,000 notional

**⚠️ Common Mistake**:
- ❌ "1 contract = 1 BTC" (wrong!)
- ✅ "1 contract = 0.01 BTC" (correct)

### Symbol Format

```
{UNDERLYING}-{CURRENCY}-{EXPIRY}-{STRIKE}-{TYPE}

Examples:
  BTC-USD-250328-100000-C   # BTC Call, expires 2025-03-28, strike $100,000
  BTC-USD-250328-100000-P   # BTC Put, expires 2025-03-28, strike $100,000
  ETH-USD-250228-3000-C     # ETH Call, expires 2025-02-28, strike $3,000
```

---

## 2. Trading Parameters (거래 파라미터) ⭐ CRITICAL

### Price Units & Tick Size (`tickSz`)

**Tick Size (최소 호가 단위)**:

| Underlying | Tick Size (`tickSz`) | Meaning |
|------------|---------------------|---------|
| BTC        | 0.0001 BTC          | 가격은 0.0001 BTC 단위로만 입력 가능 |
| ETH        | 0.0005 ETH          | 가격은 0.0005 ETH 단위로만 입력 가능 |

**Price Unit**: Premium은 **underlying 단위**로 표시 (BTC/ETH, NOT USDT)

**Example**:
- BTC 옵션 premium: 0.0234 BTC ✅, 0.02341 BTC ❌ (invalid, not multiple of 0.0001)
- ETH 옵션 premium: 0.0125 ETH ✅, 0.0123 ETH ❌ (invalid, not multiple of 0.0005)

**Physical meaning**:
- Premium 0.02 BTC = 실제로 0.02 BTC를 지불 (USDT로 환산 X)
- 현재 BTC = $100,000이면 → 0.02 BTC = $2,000 상당

### Quantity Parameters

| Parameter | Value | API Field | Meaning |
|-----------|-------|-----------|---------|
| **Min Size** | 1 contract | `minSz` | 최소 주문 수량 |
| **Lot Size** | 1 contract | `lotSz` | 수량 증분 단위 (Qty Step) |

**Example**:
- Order 1 contract ✅
- Order 10 contracts ✅
- Order 0.5 contracts ❌ (invalid, must be integer)
- Order 1.5 contracts ❌ (invalid, must be multiple of `lotSz`)

**Physical meaning**:
- 100 contracts = 100 * 0.01 BTC = 1 BTC exposure
- Deep OTM 옵션 100 contracts 매수 = 최대 손실 = premium * 100

---

## 3. Settlement & Exercise (결제 및 행사)

### Settlement Type: Inverse Settlement (역마진)

**Inverse Settlement** (역마진 결제):
- Premium 지불/수령: **Underlying으로** (BTC/ETH)
- PnL 정산: **Underlying으로** (BTC/ETH)
- **NOT USDT-settled** (Bybit/Binance와 다름 ⚠️)

**Example**:
- BTC Call premium 0.02 BTC:
  - Buyer pays: 0.02 BTC (not USDT!)
  - Seller receives: 0.02 BTC
- Profit/Loss at expiry: settled in BTC

**Physical meaning**:
- 계좌에 BTC가 있어야 옵션 매수 가능
- PnL도 BTC로 정산되므로, BTC 가격 변동 위험 있음

### Expiry & Exercise

| Parameter | Value | Meaning |
|-----------|-------|---------|
| **Style** | European | 만기일에만 행사 가능 (조기 행사 불가) |
| **Expiry Time** | UTC 08:00 (KST 17:00) | 만기 시각 (✅ verified) |
| **Auto-Exercise** | ITM options | In-the-money 자동 행사 |
| **OTM Handling** | Expire worthless | Out-of-money 자동 소멸 |

**Exercise Threshold**:
- ITM > 0 (any amount in-the-money → auto-exercise)
- **No manual exercise** (자동 행사만 가능)

**Example**:
- BTC Call, Strike $100,000, Expiry price $101,000:
  - ITM = $1,000 → Auto-exercised
  - Long: Receives 0.01 BTC worth of settlement
- BTC Put, Strike $100,000, Expiry price $101,000:
  - OTM → Expires worthless, premium lost

### Expiry Structure (Tenor Terminology)

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

**⚠️ 중요**:
- 금요일 당일: **Front day = Front week** (같은 만기)
- 마지막 금요일 당일: **Front day = Front week = Front month** (모두 같음)
- ❌ **"Next week (NW)"** 같은 용어는 존재하지 않음

---

## 4. Greeks & Pricing (Greeks 및 가격)

### OKX Greeks vs Black-Scholes ⭐ CRITICAL

**CRITICAL**: OKX provides **PA (Probability Analysis) Greeks**, NOT Black-Scholes Greeks.

| Source | Method | Volatility Model |
|--------|--------|------------------|
| OKX API | PA (Probability Analysis) | Smile/Skew 반영 |
| Black-Scholes | 이론 모델 | Flat IV 가정 |

**절대 금지**:
- ❌ Black-Scholes로 Delta/Gamma 계산 후 백테스트
- ❌ Flat IV 가정으로 Greeks 추정

**반드시 사용**:
- ✅ OKX API에서 제공하는 Greeks 사용 (`GET /api/v5/public/option-summary`)
- ✅ Smile/Skew 반영된 실제 Greeks

### Available Greeks

| Greek | API Field | Meaning |
|-------|-----------|---------|
| Delta | `delta` | Underlying 가격 변화 대비 옵션 가격 변화 |
| Gamma | `gamma` | Delta 변화율 (2차 도함수) |
| Theta | `theta` | 시간 경과 대비 가격 변화 (하루당) |
| Vega  | `vega`  | IV 변화 대비 가격 변화 |

**Update Frequency**: Real-time (매 tick마다 업데이트)

---

## 5. API Fields Reference (API 필드 참조)

### Instrument Info (`GET /api/v5/public/instruments?instType=OPTION`)

```json
{
  "instId": "BTC-USD-250328-100000-C",
  "uly": "BTC-USD",
  "instType": "OPTION",
  "ctVal": "0.01",        // Contract value (0.01 BTC per contract) ⭐
  "ctMult": "1",          // Contract multiplier
  "ctType": "inverse",    // Inverse settlement ⭐
  "optType": "C",         // Call (C) or Put (P)
  "stk": "100000",        // Strike price
  "tickSz": "0.0001",     // Tick size (price increment) ⭐
  "lotSz": "1",           // Lot size (qty step) ⭐
  "minSz": "1",           // Min order size ⭐
  "settleCcy": "BTC",     // Settlement currency
  "expTime": "1711612800000"  // Expiry timestamp (UTC 08:00)
}
```

### Option Summary (`GET /api/v5/public/option-summary?uly=BTC-USD`)

```json
{
  "instId": "BTC-USD-250328-100000-C",
  "delta": "0.5432",
  "gamma": "0.0001",
  "theta": "-0.0012",
  "vega": "0.0234",
  "markVol": "0.6234",    // Mark IV
  "bidVol": "0.6180",     // Bid IV
  "askVol": "0.6288"      // Ask IV
}
```

---

## 6. Practical Examples (실전 예시)

### Example 1: Order Validation

**Scenario**: BTC Call, Strike $100,000, Premium 0.0234 BTC

```python
# Valid orders
order_qty = 10  # ✅ Multiple of lotSz (1)
order_price = 0.0234  # ✅ Multiple of tickSz (0.0001)

# Invalid orders
order_qty = 0.5  # ❌ Not integer (lotSz = 1)
order_price = 0.02341  # ❌ Not multiple of tickSz (0.0001)

# Validation function
def validate_order(qty, price, tick_size=0.0001, lot_size=1):
    if qty % lot_size != 0:
        raise ValueError(f"Qty {qty} not multiple of lotSz {lot_size}")
    if round(price / tick_size) * tick_size != price:
        raise ValueError(f"Price {price} not multiple of tickSz {tick_size}")
    return True
```

### Example 2: Position Size Calculation

**Position**: 100 BTC Calls @ Strike $100,000

```python
contract_size = 0.01  # BTC per contract (ctVal)
strike = 100000  # USD
qty = 100  # contracts

# Notional value
notional_btc = contract_size * qty  # 1 BTC
notional_usd = contract_size * strike * qty  # $100,000

# Premium paid (assume 0.02 BTC per contract)
premium_per_contract = 0.02  # BTC
total_premium_btc = premium_per_contract * qty  # 2 BTC
total_premium_usd = total_premium_btc * btc_price  # if BTC = $100,000 → $200,000

# Max loss (long call)
max_loss_btc = total_premium_btc  # 2 BTC
max_loss_usd = total_premium_usd  # $200,000
```

### Example 3: Settlement Calculation

**BTC Call, Strike $100,000, Expiry Price $101,000, Position: Long 100 contracts**

```python
contract_size = 0.01  # BTC (ctVal)
strike = 100000
expiry_price = 101000
qty = 100

# Intrinsic value per contract
intrinsic_usd = max(0, expiry_price - strike)  # $1,000
intrinsic_btc = intrinsic_usd / expiry_price  # 0.0099 BTC per contract

# Total settlement (in BTC)
settlement_btc = intrinsic_btc * qty  # 0.99 BTC

# Net PnL (assume premium paid 0.02 BTC per contract)
premium_paid_btc = 0.02 * qty  # 2 BTC
net_pnl_btc = settlement_btc - premium_paid_btc  # -1.01 BTC (loss)

# Convert to USD for reporting
net_pnl_usd = net_pnl_btc * expiry_price  # -$1,020 (loss)
```

---

## 7. Common Mistakes (흔한 실수) ⚠️

### ❌ Mistake 1: USDT Settlement 가정
```python
# WRONG (OKX는 inverse settlement, BTC로 지불)
premium_usd = 0.02 * btc_price  # ❌ Premium은 BTC로 지불, not USDT

# CORRECT
premium_btc = 0.02  # ✅ Premium in BTC
premium_usd_equivalent = premium_btc * btc_price  # For reporting only
```

### ❌ Mistake 2: Contract Size 착각
```python
# WRONG (1 contract ≠ 1 BTC)
notional = strike * qty  # ❌ 틀렸음

# CORRECT (1 contract = 0.01 BTC)
ct_val = 0.01  # BTC per contract
notional = strike * ct_val * qty  # ✅ 올바름
```

### ❌ Mistake 3: Black-Scholes Greeks 사용
```python
# WRONG
from scipy.stats import norm

def black_scholes_delta(S, K, T, r, sigma):
    d1 = (np.log(S/K) + (r + 0.5*sigma**2)*T) / (sigma*np.sqrt(T))
    return norm.cdf(d1)

delta = black_scholes_delta(S=100000, K=100000, T=7/365, r=0.05, sigma=0.6)
# ❌ This will NOT match OKX's delta (different model, skew ignored)

# CORRECT
delta = api.get_option_summary(instId)['delta']  # ✅ OKX PA Greeks
```

### ❌ Mistake 4: Tick Size 무시
```python
# WRONG
order_price = 0.02345  # ❌ Not multiple of 0.0001

# CORRECT
tick_size = 0.0001
order_price = round(0.02345 / tick_size) * tick_size  # 0.0235 (rounded)
```

### ❌ Mistake 5: 만기 시각 가정
```python
# WRONG
expiry_time = "23:59:59 UTC"  # ❌ Wrong time
expiry_time = "00:00:00 UTC"  # ❌ Wrong time

# CORRECT
expiry_time = "08:00:00 UTC"  # ✅ Correct (KST 17:00)
```

---

## 8. Backtesting Considerations (백테스트 주의사항)

### Greeks Tracking (MANDATORY)

**MANDATORY**:
- ✅ Greeks 매 timestep 추적 (delta/gamma/theta/vega)
- ✅ OKX API Greeks 사용 (Black-Scholes 금지)
- ✅ Smile/Skew 반영된 Mark IV 사용

```python
# ✅ GOOD: Use OKX historical Greeks
# Store Greeks at every timestamp in your database

# Example database schema
CREATE TABLE options_greeks (
    timestamp TIMESTAMP,
    symbol VARCHAR(50),
    delta FLOAT,
    gamma FLOAT,
    theta FLOAT,
    vega FLOAT,
    mark_price FLOAT,
    underlying_price FLOAT,
    mark_iv FLOAT
);

# In backtest: Fetch historical Greeks
greeks = fetch_greeks(symbol='BTC-USD-250328-100000-C', timestamp='2024-10-05 12:00:00')
delta = greeks['delta']  # Use OKX's delta, not calculated
```

### Settlement Handling

**MANDATORY**:
- ✅ Inverse settlement 정확히 구현 (BTC/ETH 기준)
- ✅ Expiry UTC 08:00 정확히 반영
- ✅ ITM auto-exercise, OTM expire 처리

**Recommended**: Close positions 1 day before expiry
- Greeks <24h to expiry: 불안정 (gamma explosion)
- Spreads widen significantly
- Avoids settlement logic complexity

### Position Sizing (MANDATORY)

**Position Sizing Rules**:
- ✅ 1% NAV per trade (옵션 백테스트)
- ✅ Notional = `ctVal * strike * qty`로 계산
- ✅ MDD > 100% = 청산 = 백테스트 무효

```python
# Position sizing example
nav = 100000  # USDT
risk_per_trade = nav * 0.01  # $1,000 (1% NAV)

# BTC Call @ strike $100,000, premium 0.02 BTC
premium_btc = 0.02
btc_price = 100000
premium_usd = premium_btc * btc_price  # $2,000

max_qty = risk_per_trade / premium_usd  # 0.5 contracts → round to 1 (minSz)
# If premium > 1% NAV, skip trade (too risky)
```

### Cost Model (Fees)

**Fees** (DMM VIP9):
- Maker: -0.02% (rebate)
- Taker: +0.03%

**Realistic assumption**:
- 70% maker, 30% taker → avg 0.005% (0.5 bps)

**Conservative assumption**:
- 50% maker, 50% taker → avg 0.005% (still 0.5 bps, asymmetric)

---

## 9. References (참고 자료)

- **OKX Options Trading Guide**: https://www.okx.com/help/options-trading-guide
- **API Docs - Public Data**: https://www.okx.com/docs-v5/en/#public-data-rest-api
- **API Docs - Option Summary**: https://www.okx.com/docs-v5/en/#public-data-rest-api-get-option-market-data
- **Fee Structure**: knowledge/exchanges/okx/fee_structure.md
- **WebSearch Results**: 2025-12-24 (verified ctVal, tickSz, lotSz, settlement type)

---

**Last Updated**: 2025-12-24
**Version**: 2.0 (Major update: ctVal, tickSz, lotSz, physical meanings, examples)
**Previous Version**: 1.0 (2025-12-22, basic specs)
