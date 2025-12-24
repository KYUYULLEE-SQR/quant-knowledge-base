# Binance Options Specifications (옵션 상세 스펙)

**Exchange**: Binance
**Last Updated**: 2025-12-24
**Status**: ⚠️ Partial verification (limited access, some specs inferred from public info)

---

## Quick Summary (핵심 3줄)

- **Contract Size**: Underlying 기준 (BTC/ETH), USDT-settled (similar to Bybit)
- **Trading Access**: ⚠️ **Limited** - Writing/market making reserved for LPs (읽기 전용 시장)
- **Settlement**: European-style, USDT-settled, expiry time **UTC 08:00** (inferred)

---

## ⚠️ Important Notice: Limited Access

**Binance Options Trading Restrictions**:
- **Writing (selling) options**: Reserved for **Liquidity Providers (LPs)** only
- **Retail traders**: Can only **buy** options (long calls/puts)
- **Market making**: Not available for retail

**Implication for strategies**:
- ❌ Short volatility strategies (selling options) 불가능
- ❌ Delta-neutral market making 불가능
- ✅ Directional strategies (buying calls/puts) 가능
- ✅ Spreads (if both legs are buys) 가능 (but likely wider spreads)

**Why this matters**:
- Binance options 유동성이 OKX/Bybit보다 낮을 가능성
- Spreads 넓을 가능성 (LP만 quote 제공)
- Backtesting 시 realistic fill assumption 필요

---

## 1. Contract Specifications (계약 스펙)

### Contract Size (Inferred)

| Underlying | Contract Size (Estimated) | Settlement Currency | Physical Meaning |
|------------|--------------------------|---------------------|------------------|
| BTC        | 1 BTC or 0.01 BTC        | USDT                | 1 contract = BTC에 대한 권리, USDT 정산 |
| ETH        | 1 ETH or 0.1 ETH         | USDT                | 1 contract = ETH에 대한 권리, USDT 정산 |

**⚠️ Verification Needed**:
- Exact contract size not confirmed (WebSearch 제한)
- Likely similar to Bybit (0.01 BTC / 0.1 ETH)
- **Verify via Binance API** before using

**물리적 의미** (assuming 0.01 BTC):
- BTC 옵션 1 contract 매수 = BTC 0.01개에 대한 권리 보유
- Strike $100,000 BTC Call 1 contract = 만기 시 $100,000에 0.01 BTC 살 권리
- **Settlement in USDT** (same as Bybit)

### Symbol Format (Estimated)

```
{UNDERLYING}{EXPIRY}{STRIKE}{TYPE}

Examples (inferred):
  BTCUSDT250328100000C   # BTC Call, expires 2025-03-28, strike $100,000
  BTCUSDT250328100000P   # BTC Put, expires 2025-03-28, strike $100,000

Note: Verify actual symbol format via Binance API
```

---

## 2. Trading Parameters (거래 파라미터)

### Price Units & Tick Size

**Tick Size** (⚠️ Verification Needed):
- Likely: **USDT 기준** (similar to Bybit)
- Estimated: 1 USDT or 5 USDT tick size
- **Verify via Binance API** before trading

**Price Unit**: Premium은 **USDT**로 표시 (확인 필요)

### Quantity Parameters

**⚠️ Verification Needed**:
- Min order size, qty step 정보 부족
- **Verify via Binance API**: `GET /eapi/v1/exchangeInfo`

---

## 3. Settlement & Exercise (결제 및 행사)

### Settlement Type: USDT-Settled (Confirmed)

**USDT Settlement**:
- Premium 지불/수령: **USDT**
- PnL 정산: **USDT**
- **NOT inverse** (same as Bybit)

**Physical meaning**:
- 계좌에 USDT만 있으면 옵션 매수 가능
- PnL도 USDT로 정산

### Expiry & Exercise

| Parameter | Value | Confidence |
|-----------|-------|------------|
| **Style** | European | ✅ Confirmed |
| **Expiry Time** | UTC 08:00 (inferred) | ⚠️ Needs verification |
| **Auto-Exercise** | ITM options | ✅ Likely (standard) |
| **OTM Handling** | Expire worthless | ✅ Likely (standard) |

**⚠️ Verification Needed**:
- Exact expiry time (likely UTC 08:00 like OKX/Bybit, but not confirmed)
- **Verify via Binance API**: `GET /eapi/v1/exerciseHistory`

---

## 4. Greeks & Pricing (Greeks 및 가격)

### Binance Greeks

**Binance provides Greeks via API** (likely):
```
GET /eapi/v1/mark
```

**Expected Greeks**:
- Delta, Gamma, Theta, Vega (standard)

**⚠️ Important**: Use Binance's Greeks, NOT Black-Scholes
- Verify Greeks availability via API
- If no Greeks provided → **큰 문제** (백테스트 어려움)

---

## 5. API Endpoints (참고)

### Exchange Info
```
GET /eapi/v1/exchangeInfo
```
- Returns: tick size, lot size, min order size, contract specs

### Mark Price & Greeks
```
GET /eapi/v1/mark
```
- Returns: mark price, potentially Greeks

### Historical Data
```
GET /eapi/v1/klines
```
- Returns: OHLCV data for options

**⚠️ API Access**:
- Binance Options API는 별도 endpoint (`/eapi/v1/`)
- Futures API와 다름 주의

---

## 6. Fees (확인됨)

### Binance Options Fees

| Fee Type | Rate |
|----------|------|
| **Maker** | 0.03% |
| **Taker** | 0.03% |
| **Exercise Fee** | 0.015% |

**No rebates** (unlike OKX)

**Fee calculation**:
```python
# Trading fee (on premium)
trading_fee = premium_usdt * 0.0003  # 0.03%

# Exercise fee (on settlement value)
exercise_fee = settlement_usdt * 0.00015  # 0.015%

# Total cost
total_fee = trading_fee + exercise_fee
```

---

## 7. Practical Examples (실전 예시)

### Example 1: Position Size Calculation (Assuming 0.01 BTC contract)

**Position**: 1 BTC worth of BTC Calls @ Strike $100,000

```python
contract_size = 0.01  # BTC per contract (assumed)
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

# Trading fee
trading_fee = total_premium_usdt * 0.0003  # 30 USDT

# Total cost
total_cost = total_premium_usdt + trading_fee  # 10,030 USDT
```

### Example 2: Settlement Calculation (with Exercise Fee)

**BTC Call, Strike $100,000, Expiry Price $101,000, Position: Long 1 BTC (100 contracts)**

```python
contract_size = 0.01  # BTC per contract (assumed)
strike = 100000
expiry_price = 101000
qty_btc = 1.0
num_contracts = qty_btc / contract_size  # 100

# Intrinsic value per contract (in USDT)
intrinsic_per_contract = contract_size * max(0, expiry_price - strike)
# = 0.01 * $1,000 = $10 USDT

# Total settlement (before fee)
settlement_usdt = intrinsic_per_contract * num_contracts  # $1,000 USDT

# Exercise fee
exercise_fee = settlement_usdt * 0.00015  # $0.15 USDT

# Net settlement
net_settlement = settlement_usdt - exercise_fee  # $999.85 USDT

# Net PnL (assume premium paid 100 USDT per contract + trading fee)
premium_paid = 100 * num_contracts  # 10,000 USDT
trading_fee_paid = premium_paid * 0.0003  # 30 USDT
total_cost = premium_paid + trading_fee_paid  # 10,030 USDT

net_pnl = net_settlement - total_cost  # -9,030.15 USDT (loss)
```

---

## 8. Common Mistakes (흔한 실수) ⚠️

### ❌ Mistake 1: Writing Options 시도
```python
# WRONG (retail traders cannot write options on Binance)
order_side = "SELL"  # ❌ Will be rejected (LP only)

# CORRECT (retail can only buy)
order_side = "BUY"  # ✅ Long calls/puts only
```

### ❌ Mistake 2: Contract Size 가정
```python
# WRONG (contract size not verified)
contract_size = 1.0  # ❌ Assumed 1 BTC, but might be 0.01

# CORRECT (verify first)
# Check /eapi/v1/exchangeInfo for actual contract size
contract_size = api.get_contract_size(symbol)  # ✅ Fetch from API
```

### ❌ Mistake 3: Exercise Fee 누락
```python
# WRONG (forgot exercise fee)
net_pnl = settlement - premium  # ❌ Missing 0.015% exercise fee

# CORRECT
exercise_fee = settlement * 0.00015
net_pnl = settlement - exercise_fee - premium - trading_fee  # ✅ All fees included
```

---

## 9. Backtesting Considerations (백테스트 주의사항)

### ⚠️ Critical Issues for Backtesting

1. **Liquidity Concerns**:
   - LP-only writing → likely wider spreads
   - Lower volume than OKX/Bybit
   - **Use conservative slippage assumptions** (5-10% of premium)

2. **Strategy Limitations**:
   - ❌ Cannot backtest short volatility strategies (selling options)
   - ❌ Cannot backtest market making strategies
   - ✅ Can backtest directional strategies (buying options)

3. **Data Availability**:
   - Historical Greeks may not be available
   - **Verify data availability** before backtesting

4. **Fee Model**:
   - Include both trading fee (0.03%) and exercise fee (0.015%)
   - No maker rebates (unlike OKX)

### Position Sizing (MANDATORY)

**Position Sizing Rules** (same as OKX/Bybit):
- ✅ 1% NAV per trade (옵션 백테스트)
- ✅ MDD > 100% = 청산 = 백테스트 무효

### Cost Model (Conservative)

**Fees**:
- Trading: 0.03% (both maker/taker)
- Exercise: 0.015%
- **Total**: ~0.045% (higher than OKX/Bybit)

**Slippage** (conservative):
- ATM: 5-10% of premium (wider than OKX)
- 10% OTM: 10-20% of premium
- Deep OTM: 20%+ of premium

**Why conservative**:
- Lower liquidity (LP-only writing)
- Wider spreads expected
- Retail-focused (not HFT-friendly)

---

## 10. Comparison with OKX & Bybit

| Feature | OKX | Bybit | Binance |
|---------|-----|-------|---------|
| **Contract Size** | 0.01 BTC / 0.1 ETH | 0.01 BTC / 0.1 ETH | ⚠️ Verify (likely same) |
| **Settlement** | Inverse (BTC/ETH) | USDT | USDT |
| **Price Unit** | BTC/ETH | USDT | USDT |
| **Writing Access** | ✅ All traders | ✅ All traders | ❌ LPs only |
| **Maker Fee** | -0.02% (rebate) | 0.03% | 0.03% |
| **Taker Fee** | 0.03% | 0.03% | 0.03% |
| **Exercise Fee** | None | None | 0.015% |
| **Liquidity** | ★★★★★ | ★★★★☆ | ★★★☆☆ (inferred) |

**Recommendation**:
- **OKX**: Best for HFT, market making, inverse settlement strategies
- **Bybit**: Good for USDT traders, directional strategies
- **Binance**: Limited use (retail long-only), lower priority for backtesting

---

## 11. Verification Checklist

**Before using Binance options for backtesting, MUST verify**:

- [ ] **Contract size**: Fetch from `/eapi/v1/exchangeInfo`
- [ ] **Tick size**: Check API response
- [ ] **Qty step**: Check API response
- [ ] **Expiry time**: Verify exact UTC time (likely 08:00)
- [ ] **Greeks availability**: Check `/eapi/v1/mark` for delta/gamma/theta/vega
- [ ] **Historical data**: Confirm Greeks/OHLCV data availability
- [ ] **Writing restrictions**: Confirm retail cannot write (LP-only)
- [ ] **Fee structure**: Verify 0.03% trading + 0.015% exercise

**Verification Method**:
```python
import requests

# Get exchange info
response = requests.get('https://eapi.binance.com/eapi/v1/exchangeInfo')
data = response.json()

# Check contract specs
for symbol in data['optionSymbols']:
    print(f"Symbol: {symbol['symbol']}")
    print(f"Contract Size: {symbol.get('contractSize', 'N/A')}")
    print(f"Tick Size: {symbol.get('filters', [{}])[0].get('tickSize', 'N/A')}")
    print(f"Min Qty: {symbol.get('filters', [{}])[1].get('minQty', 'N/A')}")
    print(f"Qty Step: {symbol.get('filters', [{}])[1].get('stepSize', 'N/A')}")
```

---

## 12. References (참고 자료)

- **Binance Options API Docs**: https://binance-docs.github.io/apidocs/voptions/en/
- **Binance Options Trading Guide**: https://www.binance.com/en/support/faq/options
- **Fee Schedule**: https://www.binance.com/en/fee/schedule (confirmed 0.03% + 0.015%)
- **WebSearch Results**: 2025-12-24 (confirmed European-style, USDT-settled, LP-only writing)

---

**Last Updated**: 2025-12-24
**Version**: 1.0 (⚠️ Partial - needs verification via API)
**Confidence**: Medium (fees confirmed, specs inferred)
**Next Action**: Verify contract specs via `/eapi/v1/exchangeInfo` before backtesting
