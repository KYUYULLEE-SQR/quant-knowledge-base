# Options Market Making - Key Insights

**Last Updated**: 2025-12-25
**Source**: Paper trading experiments (option_market_making project)

---

## 1. Quote Pricing

### DO NOT: Recalculate price with Black-Scholes

```python
# WRONG - BS price doesn't match market
fair_price = black_scholes(spot, strike, tte, iv, r)  # Too low
```

### DO: Use market mark price as base

```python
# CORRECT - Use exchange's mark price
fair_price = market_mark_price  # From OKX opt-summary API
bid_price = fair_price * (1 - spread/2)
ask_price = fair_price * (1 + spread/2)
```

**이유**: 거래소의 mark price는 forward price, vol smile 등 반영됨. BS 단순 재계산은 bias 발생.

---

## 2. Spread Configuration

### Delta-based spread (OKX options)

| Delta Bucket | Spread | Rationale |
|--------------|--------|-----------|
| ATM (0.4-0.6) | 1.5-2.0% | 유동성 좋음, 경쟁 치열 |
| Near ATM (0.25-0.4) | 1.0-1.5% | 적당한 유동성 |
| OTM (0.1-0.25) | 1.5-2.0% | 유동성 낮음 |
| Deep OTM (<0.1) | 2.5-3.0% | 매우 낮은 유동성 |

**주의**: 너무 좁은 spread = adverse selection 위험

---

## 3. Fill Model (Simulation)

### Maker fill 조건

```python
# 단순 price crossing은 비현실적
if price_now < quote.bid_price:  # WRONG - too easy
    fill = True

# 실제로는 mark가 quote를 "넘어서야" 체결
MIN_CROSS_PCT = 0.005  # 0.5%
if price_now < quote.bid_price * (1 - MIN_CROSS_PCT):  # CORRECT
    fill_prob = calculate_prob(cross_depth)
```

### Fill rate 제한

```python
MAX_FILLS_PER_TICK = 2  # 과다 fill 방지
```

**교훈**: Paper trading에서 fill을 너무 쉽게 주면 비현실적 수익 발생.

---

## 4. Delta Hedging

### Configuration

```python
HEDGE_THRESHOLD = 0.5  # BTC (~$50k exposure)
HEDGE_FEE_BPS = 2.0    # Perp futures fee
```

### 구현 주의사항

```python
# Hedge position 생성 시 mark price 초기화 필수!
def apply_trade(self, qty, price, ...):
    self.last_price = price  # CRITICAL
    ...
```

**버그 경험**: `last_price = 0`으로 초기화 안 하면 unrealized PnL 잘못 계산됨.

---

## 5. Fee Structure (OKX DMM/VIP9)

| Type | Fee |
|------|-----|
| Options Maker | -1 bps (rebate) |
| Options Taker | +3 bps |
| Perp Futures | +2 bps |

**중요**: Maker rebate는 passive fill만 적용. Aggressive order = taker fee.

---

## 6. Position Management

### Limits

```python
MAX_INVENTORY_PER_SYMBOL = 3   # Per option symbol
MAX_TOTAL_POSITIONS = 10-15    # Total portfolio
MAX_DELTA_EXPOSURE = 0.5       # BTC before hedge
```

### Inventory Skew (권장)

```python
# 포지션이 쌓이면 반대 방향 spread 축소
if inventory > 0:  # Long
    ask_spread *= 0.8  # More aggressive ask
    bid_spread *= 1.2  # Less aggressive bid
```

---

## 7. P&L Attribution

### Components

| Component | Source |
|-----------|--------|
| Spread PnL | Bid-ask capture (bid에 사고 ask에 팔기) |
| Inventory PnL | Position MTM (가격 변동에 따른 손익) |
| Theta PnL | Time decay (옵션 시간가치 수취) |
| Hedge PnL | Delta hedge 손익 |
| Fee PnL | Maker rebate - Taker fee |

### 기대 수익 구조

- **Short-term (1h)**: Spread + Inventory 변동 dominant
- **Long-term (24h+)**: Theta decay가 주요 수익원
- **이상적**: Delta-neutral → Spread + Theta 수취

---

## 8. Common Pitfalls

### 8.1 Quote Price Mismatch

```python
# Problem: BS price < market mark
# Symptom: Always buying (our bid too high)
# Solution: Use market mark as fair price
```

### 8.2 Excessive Fills

```python
# Problem: 40+ fills per tick
# Symptom: Unrealistic equity curve
# Solution: MAX_FILLS_PER_TICK + MIN_CROSS_PCT
```

### 8.3 Hedge Initialization

```python
# Problem: Hedge position created with last_price = 0
# Symptom: Equity drops 50% then recovers
# Solution: Set last_price = entry_price in apply_trade()
```

### 8.4 Short Bias in Rising Market

```python
# Problem: MM naturally accumulates short (sells more than buys)
# Symptom: Losses in trending market
# Solution: Inventory skew + faster delta hedge
```

---

## 9. Recommended Settings

### Conservative (검증 단계)

```python
spread_mult = 1.5      # 기본 spread의 1.5배
max_fills = 2          # Tick당 최대 fill
hedge_threshold = 0.3  # 빠른 hedge
max_inventory = 2      # 적은 포지션
```

### Aggressive (검증 완료 후)

```python
spread_mult = 1.0      # 기본 spread
max_fills = 5          # 더 많은 fill 허용
hedge_threshold = 0.5  # 표준 hedge
max_inventory = 5      # 더 많은 포지션
```

---

## 10. Next Steps (Research Agenda)

1. **Theta decay 측정**: 24시간+ 실행하여 theta 수익 확인
2. **Gamma hedging**: Delta만으로 부족, gamma exposure 관리 필요
3. **Regime detection**: 변동성 높을 때 spread 자동 확대
4. **Order book integration**: Mark price 외에 depth 데이터 활용

---

**References**:
- Project: `/home/sqr/option_market_making/`
- Detailed insights: `docs/paper_trading_insights.md`
- OKX API: `docs/okx_option_market_analysis.md`
