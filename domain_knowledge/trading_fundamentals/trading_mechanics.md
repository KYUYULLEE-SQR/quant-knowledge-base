# Trading Mechanics (거래 메커니즘)

**Purpose**: 일반 거래 개념 (주문 유형, 체결, 청산, 마진) - Exchange 무관 도메인 지식

**Last Updated**: 2025-12-23
**Owner**: sqr

---

## 📌 Quick Reference

| Concept | Definition | Example |
|---------|------------|---------|
| **Market Order** | 즉시 체결 (현재 가격) | Buy 10 BTC @ Market |
| **Limit Order** | 지정 가격 이하/이상 체결 | Buy 10 BTC @ $87,500 |
| **Stop Order** | 가격 도달 시 market order | Stop-loss @ $85,000 |
| **Maker** | 호가창에 주문 추가 | Limit order, 체결 대기 |
| **Taker** | 호가창에서 주문 소진 | Market order, 즉시 체결 |
| **FOK** | Fill-or-Kill (전량 즉시 or 취소) | Buy 100 @ $88k FOK |
| **IOC** | Immediate-or-Cancel (일부 가능) | Buy 100 @ $88k IOC |
| **Post-Only** | Maker만 (taker 금지) | Limit $87,500 post-only |

---

## 🎯 Part 1: Order Types

### 1.1 Market Order (시장가 주문)

**Definition**: **현재 최우선 호가**로 즉시 체결

**Characteristics**:
- **Price**: 불확정 (현재 ask/bid)
- **Execution**: Immediate (즉시)
- **Slippage**: High (spread + depth 소진)
- **Fee**: Taker fee (0.03% on OKX)

**Example**:
```
Order Book:
  Ask: $88,010 (50 BTC)
  Ask: $88,015 (30 BTC)
  Bid: $87,990 (40 BTC)

Market Buy 10 BTC:
  → Fill @ $88,010 (ask price)
  → Slippage = $88,010 - $88,000 (mid) = $10
  → Fee = $88,010 × 10 × 0.0003 = $26.40
```

**Use Case**:
- **Urgent execution** needed
- Small orders (slippage minimal)
- High liquidity markets

**Risk**:
- **Slippage**: Large orders walk through multiple price levels
- **Flash crash**: Extreme price during low liquidity

---

### 1.2 Limit Order (지정가 주문)

**Definition**: **지정 가격 이하(buy) / 이상(sell)** 로 체결

**Characteristics**:
- **Price**: Fixed (지정가)
- **Execution**: Conditional (호가 도달 시)
- **Slippage**: Zero (if filled at limit)
- **Fee**: Maker fee (-0.02% on OKX VIP9) if passive

**Example**:
```
BTC Mid: $88,000

Limit Buy @ $87,500:
  → Order sits on bid side
  → If market drops to $87,500 → Fill
  → If market stays > $87,500 → No fill

Limit Sell @ $88,500:
  → Order sits on ask side
  → If market rises to $88,500 → Fill
```

**Execution Scenarios**:
1. **Passive fill** (Maker):
   - Order sits on book → counterparty hits it
   - Fee: Maker rebate (-0.02%)

2. **Aggressive fill** (Taker):
   - Limit price crosses spread (buy @ ask or higher)
   - Immediate fill like market order
   - Fee: Taker fee (0.03%)

**Example**:
```
Ask: $88,010, Bid: $87,990

Limit Buy @ $88,010 (crosses spread):
  → Immediate fill @ $88,010 (taker)
  → Fee: 0.03% (not maker rebate)

Limit Buy @ $87,995:
  → Sits on book (maker)
  → Wait for fill
  → Fee: -0.02% (if filled)
```

---

### 1.3 Stop Order (조건부 시장가)

**Definition**: **지정 가격 도달 시** market order로 전환

**Types**:
- **Stop-Loss**: 손실 제한 (하방 보호)
- **Stop-Buy**: 상승 추종 (breakout)

**Example** (Stop-Loss):
```
Position: Long BTC @ $88,000

Stop-Loss @ $85,000:
  - Trigger: BTC ≤ $85,000
  - Action: Market sell
  - Purpose: Max loss = $3,000

Execution:
  BTC drops to $85,000 → Stop triggered → Market sell @ ~$84,950 (slippage)
```

**Example** (Stop-Buy):
```
Position: Flat

Stop-Buy @ $90,000:
  - Trigger: BTC ≥ $90,000
  - Action: Market buy
  - Purpose: Breakout 추종

Execution:
  BTC rises to $90,000 → Stop triggered → Market buy @ ~$90,050
```

**Risk**:
- **Slippage**: Stop triggered → market order → fill worse than stop price
- **Gap risk**: Price gaps through stop (flash crash)

**Stop-Limit** (hybrid):
```
Stop-Limit Sell @ Stop $85,000, Limit $84,500:
  - Trigger: BTC ≤ $85,000
  - Action: Limit sell @ $84,500
  - Risk: May not fill if price drops below $84,500
```

---

### 1.4 Advanced Order Types

#### FOK (Fill-or-Kill)

**Definition**: **전량 즉시 체결** or **전량 취소**

```
Order: Buy 100 BTC @ $88,000 FOK

Order Book:
  Ask $88,000: 80 BTC ← Not enough!
  Ask $88,010: 50 BTC

Result: Order cancelled (can't fill 100 @ $88,000)
```

**Use Case**: All-or-nothing execution

---

#### IOC (Immediate-or-Cancel)

**Definition**: **즉시 체결 가능한 만큼 fill**, 나머지 취소

```
Order: Buy 100 BTC @ $88,000 IOC

Order Book:
  Ask $88,000: 60 BTC

Result:
  Fill 60 BTC @ $88,000
  Cancel 40 BTC (no partial order on book)
```

**Use Case**: Partial fill 허용, but no waiting

---

#### Post-Only (Maker-Only)

**Definition**: **Maker로만 체결** (taker 금지)

```
Order: Buy BTC @ $88,010 Post-Only

Current Ask: $88,010

Result:
  Order rejected (would cross spread → taker)

Order: Buy BTC @ $87,995 Post-Only

Current Bid: $87,990

Result:
  Order posted on book @ $87,995 (maker)
  Wait for fill (guaranteed maker fee)
```

**Use Case**:
- **Maker rebate** 확보 (-0.02% on VIP9)
- No slippage (fill at limit or nothing)

**Related**: `../backtest_models/fill_probability.md` - 30% fill ratio for maker orders

---

### 1.5 Order Type Comparison

| Order Type | Execution | Price | Slippage | Fee | Use Case |
|------------|-----------|-------|----------|-----|----------|
| **Market** | Immediate | Variable | High | Taker | Urgent |
| **Limit** | Conditional | Fixed | Zero | Maker/Taker | Patient |
| **Stop** | Triggered → Market | Variable | High | Taker | Risk mgmt |
| **Stop-Limit** | Triggered → Limit | Fixed (limit) | Zero | Maker/Taker | Controlled |
| **FOK** | Immediate or Cancel | Fixed | Zero or reject | Taker | All-or-nothing |
| **IOC** | Immediate (partial OK) | Fixed | Zero | Taker | Fast partial |
| **Post-Only** | Conditional | Fixed | Zero | Maker only | Rebate farming |

---

## 📊 Part 2: Order Execution

### 2.1 Maker vs Taker

**Maker**: 호가창에 **유동성 제공** (liquidity provider)
**Taker**: 호가창에서 **유동성 소진** (liquidity taker)

**Example**:
```
Order Book Before:
  Ask: $88,010 (50 BTC)
  Bid: $87,990 (40 BTC)

Scenario 1: Maker
  → Place Limit Buy @ $87,995 (inside spread)
  → Order sits on book (adds liquidity)
  → Fee: Maker (-0.02% rebate)

Order Book After:
  Ask: $88,010 (50 BTC)
  Bid: $87,995 (new order, maker)
  Bid: $87,990 (40 BTC)

Scenario 2: Taker
  → Market Buy or Limit Buy @ $88,010+
  → Hits existing ask (removes liquidity)
  → Fee: Taker (0.03%)

Order Book After:
  Ask: $88,010 (40 BTC, reduced by 10)
  Bid: $87,990 (40 BTC)
```

**Fee Structure**:
| Role | OKX VIP9 (Options) | OKX VIP0 |
|------|-------------------|----------|
| **Maker** | -0.01% (rebate) | 0.02% |
| **Taker** | 0.03% | 0.05% |

**Maker Advantages**:
- ✅ Negative fee (rebate)
- ✅ No slippage (fill at limit)
- ❌ Partial fill risk (30% avg on options)
- ❌ Slow execution (wait for fill)

**Taker Advantages**:
- ✅ Immediate fill
- ✅ 100% fill (guaranteed)
- ❌ Positive fee (0.03%)
- ❌ Slippage (spread + depth)

---

### 2.2 Order Matching (Price-Time Priority)

**Matching Rule**: **Price first**, then **Time**

**Example**:
```
Bid Side:
  1. $88,000 (100 BTC, 10:00:00)  ← Best price
  2. $88,000 (50 BTC, 10:00:05)   ← Same price, later time
  3. $87,995 (200 BTC, 09:59:50)  ← Worse price

Incoming Market Sell 120 BTC:
  Step 1: Fill 100 BTC @ $88,000 (order #1, best price + earliest)
  Step 2: Fill 20 BTC @ $88,000 (order #2, same price)
  Result: Avg fill = $88,000 (120 BTC)
```

**Fair Queue**: Early orders get priority at same price level

---

### 2.3 Partial Fill

**Definition**: 주문이 **일부만 체결**

**Causes**:
1. **Insufficient depth**: 호가창에 물량 부족
2. **Maker order**: Passive fill (30% avg on options)
3. **IOC order**: Immediate fill limit

**Example**:
```
Order: Limit Buy 100 BTC @ $88,000 (Post-Only)

Fills:
  10:00: Fill 20 BTC (counterparty sells 20)
  10:05: Fill 10 BTC (counterparty sells 10)
  10:10: Timeout, cancel 70 BTC unfilled

Total: 30% fill (30 BTC out of 100)
```

**Handling Unfilled**:
1. **Cancel**: Give up
2. **Reorder**: New order at more aggressive price
3. **Wait**: Keep order on book (passive)

**Related**: `../backtest_models/fill_probability.md` - Fill ratio model

---

### 2.4 Slippage

**Definition**: **의사결정 가격** vs **실제 체결 가격** 차이

**Formula**:
```
Slippage = |Execution Price - Reference Price|

Reference Price:
  - Mid price: (bid + ask) / 2
  - Mark price: 거래소 공식 가격
  - Signal price: 전략 신호 시점 가격
```

**Example**:
```
Decision: Buy at mid $88,000

Market Order:
  Fill @ Ask $88,010
  Slippage = $88,010 - $88,000 = $10 per BTC

100 BTC order:
  Slippage cost = $10 × 100 = $1,000
```

**Slippage Types**:
1. **Spread slippage**: Bid-ask spread (taker orders)
2. **Depth slippage**: Walking through order book (large orders)
3. **Time slippage**: Price moves between decision and execution

**Mitigation**:
- Use **limit orders** (zero slippage if filled)
- Split large orders (**TWAP, VWAP**)
- Trade during **high liquidity** hours

**Related**: `../backtest_models/slippage_estimation.md` - Slippage models

---

## 💰 Part 3: Fees & Costs

### 3.1 Trading Fees

**Fee Structure**: Based on **VIP tier** (volume-based)

**OKX Tiers**:
| Tier | 30D Volume | Maker (Options) | Taker (Options) |
|------|------------|-----------------|-----------------|
| VIP0 | < $10M | 0.02% | 0.05% |
| VIP1 | $10M-$50M | 0.015% | 0.04% |
| VIP5 | $500M-$1B | 0% | 0.025% |
| VIP9 | $10B+ | **-0.01%** | 0.03% |

**Important**: Fee tier **≠ Fill probability** (시장 조건에만 의존)

---

### 3.2 Funding Rate (Perpetual Only)

**Definition**: Long/Short 간 주기적 정산 (8시간마다)

**Formula**:
```
Funding Payment = Position Value × Funding Rate

Positive Rate: Long pays Short
Negative Rate: Short pays Long
```

**Example**:
```
Position: Long 10 BTC perpetual @ $88,000
Funding Rate: 0.01% (positive)

Payment (8 hours later):
  = $88,000 × 10 × 0.0001
  = $88 paid to shorts
```

**Note**: **Options는 funding 없음** (만기 있음)

---

### 3.3 Transaction Cost Summary

**Total T-cost**:
```
T-cost = Fees + Slippage + Partial Fill Impact

Maker Order (Post-Only):
  Fees = -0.01% (rebate)
  Slippage = 0 (fill at limit)
  Partial Fill = Opportunity cost (70% unfilled)
  Net T-cost ≈ -0.01% + opportunity cost

Taker Order (Market):
  Fees = 0.03%
  Slippage = Spread / 2 ≈ 1% (options)
  Partial Fill = 0 (100% fill)
  Net T-cost ≈ 1.03%
```

**Related**: `../backtest_models/transaction_cost_model.md`

---

## 🏦 Part 4: Margin & Leverage

### 4.1 Margin Types

**Initial Margin**: 포지션 진입 시 필요 (담보)
**Maintenance Margin**: 포지션 유지 최소 요구 (청산 기준)

**Example** (Futures):
```
Position: Long 10 BTC futures @ $88,000
Leverage: 10x

Initial Margin Required:
  = Notional / Leverage
  = ($88,000 × 10) / 10
  = $88,000

Maintenance Margin (OKX):
  ≈ 0.5% of notional
  = $880,000 × 0.005 = $4,400
```

**Liquidation**: Equity < Maintenance Margin → 강제 청산

---

### 4.2 Options Margin (Seller Only)

**Buyer**: Premium 지불 → **No margin** (max loss = premium)
**Seller**: **Margin required** (unlimited risk)

**OKX Margin** (Seller):
```
Margin = max(
  0.15 × Spot - OTM Amount + Premium,
  0.10 × Spot + Premium
)

Where:
  OTM Amount = max(K - S, 0) for Calls
               max(S - K, 0) for Puts
```

**Example** (Short Call):
```
Short BTC-USD-250110-90000-C @ $2,500
BTC = $88,000

Margin = max(
  0.15 × 88000 - max(90000-88000, 0) + 2500,
  0.10 × 88000 + 2500
)
= max(
  13200 - 2000 + 2500 = $13,700,
  8800 + 2500 = $11,300
)
= $13,700
```

**Margin Call**: BTC 상승 → Call value 증가 → Margin 부족 → 추가 입금 or 청산

---

### 4.3 Portfolio Margin (Advanced)

**Definition**: 포트폴리오 전체의 **risk-based margin** (개별 포지션 합산 아님)

**Benefit**: **Hedged positions** → Lower margin

**Example**:
```
Position 1: Long 1 BTC @ $88,000
Position 2: Short 1 BTC Call $90k @ $2,500

Individual Margin:
  Long BTC: $88,000 (100%)
  Short Call: $13,700
  Total: $101,700

Portfolio Margin (hedged):
  Delta-hedged → Lower risk
  Margin: ~$15,000 (85% reduction)
```

**Use Case**: Complex multi-leg strategies (spreads, straddles)

---

## 📈 Part 5: Settlement

### 5.1 Options Settlement (Expiry)

**Settlement Time**: OKX options expire at **UTC 08:00** (KST 17:00)

**Settlement Process**:
1. **Determine ITM/OTM**:
   - Settlement price = **Index price** at expiry
   - ITM: Intrinsic value settlement
   - OTM: Expire worthless

2. **Cash Settlement** (OKX):
   - No physical delivery
   - ITM: Credit **intrinsic value** to account
   - OTM: No action

**Example**:
```
Long BTC-USD-250110-90000-C @ $2,500

Settlement Price: $95,000 (ITM)
  Intrinsic Value = 95000 - 90000 = $5,000
  Net PnL = $5,000 - $2,500 = $2,500 profit
  Account: +$5,000 cash credited

Settlement Price: $88,000 (OTM)
  Intrinsic Value = 0
  Net PnL = 0 - $2,500 = -$2,500 loss
  Account: No action (premium lost)
```

---

### 5.2 Futures Settlement

**Perpetual**: **No expiry** (funding rate로 수렴)
**Quarterly**: 매 분기 마지막 금요일 UTC 08:00

**Settlement**:
```
Position: Long 10 BTC futures @ $88,000

Settlement Price: $90,000
  PnL = (90000 - 88000) × 10 = $20,000
  Account: +$20,000 credited, position closed
```

---

## 📚 Related Documentation

- **OKX Order Execution**: `exchanges/okx/order_execution.md` - OKX 구체적 스펙
- **OKX Fee Structure**: `exchanges/okx/fee_structure.md` - VIP tier별 수수료
- **Fill Probability**: `../backtest_models/fill_probability.md` - Maker order 30% fill
- **Slippage Estimation**: `../backtest_models/slippage_estimation.md` - Slippage 모델
- **Transaction Costs**: `../backtest_models/transaction_cost_model.md` - T-cost 계산

---

**Last Updated**: 2025-12-23
**Version**: 1.0
**Maintainer**: sqr

**Note**: 이 문서는 도메인 지식 (exchange 무관). 거래소별 스펙은 `exchanges/` 참조.
