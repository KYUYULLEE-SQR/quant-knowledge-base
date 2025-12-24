# Bybit Options Specifications (옵션 상세 스펙)

**Exchange**: Bybit
**Last Updated**: 2025-12-24
**Status**: ✅ Verified via WebSearch + official docs

---

## Quick Summary (핵심 3줄)

- **Contract Size**: 0.01 BTC or 0.1 ETH per contract (same as OKX, but **USDT-settled**)
- **Min Order**: 0.01 BTC/0.1 ETH, Qty Step = 0.01 BTC/0.1 ETH, Tick Size = 5 USDT
- **Settlement**: European-style, auto-exercise at UTC 08:00, USDT-settled (NOT inverse)

---

## 1. Contract Specifications (계약 스펙)

### Contract Size

| Underlying | Contract Size | Settlement Currency | Physical Meaning |
|------------|--------------|---------------------|------------------|
| BTC        | 0.01 BTC     | USDT                | 1 contract = 0.01 BTC에 대한 권리, premium/PnL은 USDT |
| ETH        | 0.1 ETH      | USDT                | 1 contract = 0.1 ETH에 대한 권리, premium/PnL은 USDT |

**물리적 의미**:
- BTC 옵션 1 contract 매수 = BTC 0.01개에 대한 권리 보유
- Strike $100,000 BTC Call 1 contract = 만기 시 $100,000에 0.01 BTC 살 권리
- **Settlement in USDT** (OKX와 다름 ⚠️)
- **Notional value** = `contract_size * strike`
  - Example: 1 contract @ strike $100,000 = 0.01 * 100,000 = $1,000 notional

**Key Difference from OKX**:
- OKX: Inverse settlement (premium/PnL in BTC/ETH)
- Bybit: USDT settlement (premium/PnL in USDT) ✅ easier for USDT accounts

### Symbol Format

```
{UNDERLYING}-{EXPIRY}-{STRIKE}-{TYPE}

Examples:
  BTC-28MAR25-100000-C   # BTC Call, expires 2025-03-28, strike $100,000
  BTC-28MAR25-100000-P   # BTC Put, expires 2025-03-28, strike $100,000
  ETH-28FEB25-3000-C     # ETH Call, expires 2025-02-28, strike $3,000
```

---

## 2. Trading Parameters (거래 파라미터) ⭐ CRITICAL

### Price Units & Tick Size

**Tick Size (최소 호가 단위)**:

| Underlying | Tick Size | Meaning |
|------------|----------|---------|
| BTC        | 5 USDT   | 가격은 5 USDT 단위로만 입력 가능 |
| ETH        | 5 USDT   | 가격은 5 USDT 단위로만 입력 가능 |

**Price Unit**: Premium은 **USDT**로 표시 (BTC/ETH 아님, OKX와 다름)

**Example**:
- BTC 옵션 premium: 100 USDT ✅, 102 USDT ❌ (invalid, not multiple of 5)
- BTC 옵션 premium: 105 USDT ✅ (valid, multiple of 5)
- ETH 옵션 premium: 50 USDT ✅, 52 USDT ❌ (invalid)

**Physical meaning**:
- Premium 100 USDT = 실제로 100 USDT를 지불 (BTC로 환산 X)
- PnL도 USDT로 정산

### Quantity Parameters

| Parameter | Value | Meaning |
|-----------|-------|---------|
| **Min Size** | 0.01 BTC / 0.1 ETH | 최소 주문 수량 |
| **Qty Step** | 0.01 BTC / 0.1 ETH | 수량 증분 단위 |

**Example**:
- Order 0.01 BTC ✅ (1 contract)
- Order 0.1 BTC ✅ (10 contracts)
- Order 0.015 BTC ❌ (invalid, not multiple of 0.01)
- Order 0.5 BTC ✅ (50 contracts)

**Physical meaning**:
- 1 BTC exposure = 100 contracts (1 / 0.01)
- 10 ETH exposure = 100 contracts (10 / 0.1)

**Conversion**:
```python
# BTC
contracts = qty_btc / 0.01  # qty_btc = 0.1 BTC → 10 contracts
qty_btc = contracts * 0.01  # 50 contracts → 0.5 BTC

# ETH
contracts = qty_eth / 0.1   # qty_eth = 1 ETH → 10 contracts
qty_eth = contracts * 0.1   # 20 contracts → 2 ETH
```

---

## 3. Settlement & Exercise (결제 및 행사)

### Settlement Type: USDT-Settled ⭐

**USDT Settlement**:
- Premium 지불/수령: **USDT**
- PnL 정산: **USDT**
- **NOT inverse** (OKX와 다름 ⚠️)

**Example**:
- BTC Call premium 100 USDT:
  - Buyer pays: 100 USDT (not BTC!)
  - Seller receives: 100 USDT
- Profit/Loss at expiry: settled in USDT

**Physical meaning**:
- 계좌에 USDT만 있으면 옵션 매수 가능 (BTC 불필요)
- PnL도 USDT로 정산되므로, BTC 가격 변동 위험 없음 (헤지 제외)

### Expiry & Exercise

| Parameter | Value | Meaning |
|-----------|-------|---------|
| **Style** | European | 만기일에만 행사 가능 (조기 행사 불가) |
| **Expiry Time** | UTC 08:00 (KST 17:00) | 만기 시각 (same as OKX) |
| **Auto-Exercise** | ITM options | In-the-money 자동 행사 |
| **OTM Handling** | Expire worthless | Out-of-money 자동 소멸 |

**Exercise Threshold**:
- ITM > 0 (any amount in-the-money → auto-exercise)
- **No manual exercise** (자동 행사만 가능)

**Example**:
- BTC Call, Strike $100,000, Expiry price $101,000:
  - ITM = $1,000
  - Settlement = 0.01 BTC * $1,000 = $10 USDT per contract
  - Long 10 contracts → receives $100 USDT
- BTC Put, Strike $100,000, Expiry price $101,000:
  - OTM → Expires worthless, premium lost

### Expiry Structure

Bybit options have multiple expiry types, all at **UTC 08:00**:

1. **Daily Expiry**: 매일 08:00 UTC
2. **Weekly Expiry**: 매주 금요일 08:00 UTC
3. **Monthly Expiry**: 매달 마지막 금요일 08:00 UTC
4. **Quarterly Expiry**: 분기 마지막 금요일 08:00 UTC

**Same as OKX** (tenor terminology also similar)

---

## 4. Greeks & Pricing (Greeks 및 가격)

### Bybit Greeks

**Bybit provides Greeks via API**:
```
GET /v5/market/tickers?category=option
```

**Available Greeks**:
- Delta, Gamma, Theta, Vega

**⚠️ Important**: Use Bybit's Greeks, NOT Black-Scholes
- Bybit uses proprietary model (likely adjusted for skew/smile)
- Greeks update in real-time
- **Do NOT calculate Greeks yourself** in backtest

### Mark Price

**Mark Price** = Fair value price used for liquidation and unrealized PnL

**Bybit Mark Price**:
- Derived from order book + index price
- Used for margin calculation

---

## 5. API Fields Reference (API 필드 참조)

### Instrument Info

```json
{
  "symbol": "BTC-28MAR25-100000-C",
  "baseCoin": "BTC",
  "quoteCoin": "USDT",
  "settleCoin": "USDT",
  "optionsType": "Call",
  "launchTime": "1234567890000",
  "deliveryTime": "1234567890000",
  "deliveryFeeRate": "0.00015"
}
```

### Tickers (Greeks)

```json
{
  "symbol": "BTC-28MAR25-100000-C",
  "bidPrice": "95",
  "askPrice": "105",
  "lastPrice": "100",
  "markPrice": "100",
  "indexPrice": "100000",
  "delta": "0.5432",
  "gamma": "0.0001",
  "vega": "0.0234",
  "theta": "-0.0012",
  "totalVolume": "12.5",
  "totalTurnover": "125000",
  "openInterest": "45.3",
  "underlyingPrice": "100000"
}
```

---

## 6. Practical Examples (실전 예시)

### Example 1: Order Validation

**Scenario**: BTC Call, Strike $100,000, Premium 105 USDT

```python
# Valid orders
order_qty_btc = 0.1  # ✅ Multiple of 0.01 BTC
order_price_usdt = 105  # ✅ Multiple of 5 USDT

# Invalid orders
order_qty_btc = 0.015  # ❌ Not multiple of 0.01
order_price_usdt = 102  # ❌ Not multiple of 5

# Validation function
def validate_order_bybit(qty_btc, price_usdt):
    min_qty = 0.01
    qty_step = 0.01
    tick_size = 5

    if qty_btc < min_qty:
        raise ValueError(f"Qty {qty_btc} < min {min_qty}")
    if (qty_btc % qty_step) > 1e-6:  # Floating point tolerance
        raise ValueError(f"Qty {qty_btc} not multiple of {qty_step}")
    if price_usdt % tick_size != 0:
        raise ValueError(f"Price {price_usdt} not multiple of {tick_size}")
    return True
```

### Example 2: Position Size Calculation

**Position**: 1 BTC worth of BTC Calls @ Strike $100,000

```python
contract_size = 0.01  # BTC per contract
strike = 100000  # USD
qty_btc = 1.0  # BTC exposure desired

# Number of contracts
num_contracts = qty_btc / contract_size  # 100 contracts

# Notional value per contract
notional_per_contract = contract_size * strike  # $1,000

# Total notional
total_notional = notional_per_contract * num_contracts  # $100,000

# Premium paid (assume 100 USDT per contract)
premium_per_contract = 100  # USDT
total_premium_usdt = premium_per_contract * num_contracts  # 10,000 USDT

# Max loss (long call)
max_loss_usdt = total_premium_usdt  # 10,000 USDT
```

### Example 3: Settlement Calculation

**BTC Call, Strike $100,000, Expiry Price $101,000, Position: Long 1 BTC (100 contracts)**

```python
contract_size = 0.01  # BTC per contract
strike = 100000
expiry_price = 101000
qty_btc = 1.0
num_contracts = qty_btc / contract_size  # 100

# Intrinsic value per contract (in USDT)
intrinsic_per_contract = contract_size * max(0, expiry_price - strike)
# = 0.01 * $1,000 = $10 USDT

# Total settlement
settlement_usdt = intrinsic_per_contract * num_contracts  # $1,000 USDT

# Net PnL (assume premium paid 100 USDT per contract)
premium_paid_usdt = 100 * num_contracts  # 10,000 USDT
net_pnl_usdt = settlement_usdt - premium_paid_usdt  # -9,000 USDT (loss)
```

---

## 7. Common Mistakes (흔한 실수) ⚠️

### ❌ Mistake 1: Inverse Settlement 가정 (OKX와 혼동)
```python
# WRONG (Bybit는 USDT settlement)
premium_btc = 0.02  # ❌ Bybit premium은 USDT, not BTC

# CORRECT
premium_usdt = 100  # ✅ Premium in USDT
```

### ❌ Mistake 2: Tick Size 착각
```python
# WRONG (OKX tick size와 다름)
tick_size = 0.0001  # ❌ This is OKX BTC tick size

# CORRECT (Bybit는 USDT 기준)
tick_size = 5  # ✅ Bybit tick size = 5 USDT
```

### ❌ Mistake 3: Quantity 단위 혼동
```python
# WRONG (contracts vs BTC)
order_qty = 100  # ❌ 100 contracts? or 100 BTC? Ambiguous!

# CORRECT (명시적으로 BTC 단위 사용, Bybit API 기준)
order_qty_btc = 1.0  # 1 BTC = 100 contracts
order_qty_contracts = order_qty_btc / 0.01  # 100 contracts
```

### ❌ Mistake 4: Settlement 계산 오류
```python
# WRONG (intrinsic value 계산)
settlement = max(0, expiry_price - strike)  # ❌ Missing contract_size

# CORRECT
settlement_per_contract = contract_size * max(0, expiry_price - strike)
# BTC Call: 0.01 * (101000 - 100000) = $10 USDT
```

---

## 8. Backtesting Considerations (백테스트 주의사항)

### Greeks Tracking (MANDATORY)

**MANDATORY**:
- ✅ Greeks 매 timestep 추적 (delta/gamma/theta/vega)
- ✅ Bybit API Greeks 사용 (Black-Scholes 금지)
- ✅ Smile/Skew 반영된 Greeks

```python
# Store Bybit Greeks in database
CREATE TABLE bybit_options_greeks (
    timestamp TIMESTAMP,
    symbol VARCHAR(50),
    delta FLOAT,
    gamma FLOAT,
    theta FLOAT,
    vega FLOAT,
    mark_price FLOAT,
    underlying_price FLOAT,
    bid_price FLOAT,
    ask_price FLOAT
);
```

### Settlement Handling

**MANDATORY**:
- ✅ USDT settlement 정확히 구현
- ✅ Expiry UTC 08:00 정확히 반영
- ✅ ITM auto-exercise, OTM expire 처리

**Recommended**: Close positions 1 day before expiry
- Same reasons as OKX (Greeks unstable, spreads widen)

### Position Sizing (MANDATORY)

**Position Sizing Rules**:
- ✅ 1% NAV per trade (옵션 백테스트)
- ✅ Notional = `contract_size * strike * num_contracts`
- ✅ MDD > 100% = 청산 = 백테스트 무효

```python
# Position sizing example
nav_usdt = 100000  # USDT
risk_per_trade = nav_usdt * 0.01  # $1,000 (1% NAV)

# BTC Call @ strike $100,000, premium 100 USDT per contract
premium_usdt_per_contract = 100
max_contracts = risk_per_trade / premium_usdt_per_contract  # 10 contracts
max_qty_btc = max_contracts * 0.01  # 0.1 BTC
```

### Cost Model (Fees)

**Bybit Options Fees** (VIP 0):
- Maker: 0.03%
- Taker: 0.03%

**Realistic assumption**:
- Both maker/taker: 0.03% (no rebate, unlike OKX)

**Fee calculation**:
```python
# Fee on premium (not notional)
fee_usdt = premium_usdt * 0.0003  # 0.03%
total_cost = premium_usdt + fee_usdt
```

---

## 9. Comparison with OKX

| Feature | OKX | Bybit |
|---------|-----|-------|
| **Contract Size** | 0.01 BTC / 0.1 ETH | 0.01 BTC / 0.1 ETH (same) |
| **Settlement** | Inverse (BTC/ETH) | USDT |
| **Price Unit** | BTC/ETH | USDT |
| **Tick Size** | 0.0001 BTC / 0.0005 ETH | 5 USDT |
| **Qty Step** | 1 contract | 0.01 BTC / 0.1 ETH |
| **Expiry Time** | UTC 08:00 | UTC 08:00 (same) |
| **Maker Fee** | -0.02% (rebate) | 0.03% |
| **Taker Fee** | 0.03% | 0.03% |

**Key Takeaway**:
- OKX: BTC 계좌 필요, inverse settlement (복잡)
- Bybit: USDT 계좌만 필요, simpler settlement ✅ (USDT trader 선호)

---

## 10. References (참고 자료)

- **Bybit Options Trading Guide**: https://learn.bybit.com/trading/what-are-options/
- **Bybit API Docs**: https://bybit-exchange.github.io/docs/v5/market/tickers
- **WebSearch Results**: 2025-12-24 (verified tick size, qty step, settlement type)

---

**Last Updated**: 2025-12-24
**Version**: 1.0
