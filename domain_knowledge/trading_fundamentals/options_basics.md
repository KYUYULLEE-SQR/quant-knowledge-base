# Options Basics (옵션 기초)

**Purpose**: 옵션 거래의 기본 개념 (Greeks, Payoff, Moneyness, 전략) - Exchange 무관 도메인 지식

**Last Updated**: 2025-12-23
**Owner**: sqr

---

## 📌 Quick Reference

| Concept | Definition | Example |
|---------|------------|---------|
| **Call Option** | 매수 권리 | BTC $90k Call → BTC > $90k면 행사 |
| **Put Option** | 매도 권리 | BTC $85k Put → BTC < $85k면 행사 |
| **Strike (K)** | 행사가 | $90,000 |
| **Premium** | 옵션 가격 | $2,500 |
| **Expiry** | 만기일 | 2025-01-10 UTC 08:00 |
| **ITM** | In-The-Money | Call: S > K, Put: S < K |
| **ATM** | At-The-Money | S ≈ K |
| **OTM** | Out-of-The-Money | Call: S < K, Put: S > K |

---

## 🎯 Part 1: Option Basics

### 1.1 Call Option (콜 옵션)

**Definition**: 기초자산을 **행사가(K)에 살 권리**

**Example**:
```
BTC-USD-250110-90000-C (BTC Call, Strike $90k, Expiry Jan 10)

Buyer (Long Call):
  - 권리: BTC를 $90k에 살 수 있음
  - 비용: Premium $2,500 지불
  - 행사: S > K일 때 (ITM)

Seller (Short Call):
  - 의무: BTC를 $90k에 팔아야 함
  - 수익: Premium $2,500 받음
  - 리스크: Unlimited (S가 무한대까지 상승 가능)
```

**Payoff** (만기 시):
```
Long Call Payoff = max(S - K, 0) - Premium
Short Call Payoff = Premium - max(S - K, 0)

Where:
  S = Spot price at expiry
  K = Strike price
  Premium = Option price paid
```

**Example Calculation**:
```
Long BTC-USD-250110-90000-C @ $2,500

Case 1: BTC = $95,000 at expiry (ITM)
  Payoff = max(95000 - 90000, 0) - 2500
         = 5000 - 2500
         = $2,500 profit

Case 2: BTC = $88,000 at expiry (OTM)
  Payoff = max(88000 - 90000, 0) - 2500
         = 0 - 2500
         = -$2,500 loss (premium lost)
```

**Breakeven**: `S = K + Premium = $90,000 + $2,500 = $92,500`

---

### 1.2 Put Option (풋 옵션)

**Definition**: 기초자산을 **행사가(K)에 팔 권리**

**Example**:
```
BTC-USD-250110-85000-P (BTC Put, Strike $85k, Expiry Jan 10)

Buyer (Long Put):
  - 권리: BTC를 $85k에 팔 수 있음
  - 비용: Premium $1,800 지불
  - 행사: S < K일 때 (ITM)

Seller (Short Put):
  - 의무: BTC를 $85k에 사야 함
  - 수익: Premium $1,800 받음
  - 리스크: K까지 (S=0일 때 최대)
```

**Payoff** (만기 시):
```
Long Put Payoff = max(K - S, 0) - Premium
Short Put Payoff = Premium - max(K - S, 0)
```

**Example Calculation**:
```
Long BTC-USD-250110-85000-P @ $1,800

Case 1: BTC = $80,000 at expiry (ITM)
  Payoff = max(85000 - 80000, 0) - 1800
         = 5000 - 1800
         = $3,200 profit

Case 2: BTC = $88,000 at expiry (OTM)
  Payoff = max(85000 - 88000, 0) - 1800
         = 0 - 1800
         = -$1,800 loss (premium lost)
```

**Breakeven**: `S = K - Premium = $85,000 - $1,800 = $83,200`

---

### 1.3 Moneyness (내가격성)

**Definition**: 옵션의 intrinsic value 상태

| Moneyness | Call (S vs K) | Put (S vs K) | Intrinsic Value |
|-----------|---------------|--------------|-----------------|
| **ITM** (In-The-Money) | S > K | S < K | Positive |
| **ATM** (At-The-Money) | S ≈ K | S ≈ K | ~Zero |
| **OTM** (Out-of-The-Money) | S < K | S > K | Zero |

**Example** (BTC = $88,000):
```
Call Options:
  Strike $85k Call: ITM (S > K, intrinsic = $3,000)
  Strike $88k Call: ATM (S ≈ K, intrinsic ≈ $0)
  Strike $90k Call: OTM (S < K, intrinsic = $0)

Put Options:
  Strike $85k Put: OTM (S > K, intrinsic = $0)
  Strike $88k Put: ATM (S ≈ K, intrinsic ≈ $0)
  Strike $90k Put: ITM (S < K, intrinsic = $2,000)
```

**Moneyness Ratio** (normalized):
```
Moneyness = S / K

Call:
  ITM: Moneyness > 1.0 (e.g., 88/85 = 1.035)
  ATM: Moneyness ≈ 1.0
  OTM: Moneyness < 1.0 (e.g., 88/90 = 0.978)

Put:
  ITM: Moneyness < 1.0
  ATM: Moneyness ≈ 1.0
  OTM: Moneyness > 1.0
```

**Importance**: Moneyness는 **옵션 가격, IV, Greeks에 큰 영향**

---

### 1.4 Intrinsic Value vs Time Value

**Option Price = Intrinsic Value + Time Value**

**Intrinsic Value**: 즉시 행사 시 이익
```
Call Intrinsic Value = max(S - K, 0)
Put Intrinsic Value = max(K - S, 0)
```

**Time Value**: 만기까지 남은 가치 (optionality)
```
Time Value = Option Price - Intrinsic Value
```

**Example** (BTC = $88,000):
```
BTC-USD-250110-85000-C (Call, Strike $85k, 7 DTE)
  Market Price: $4,500
  Intrinsic Value: max(88000 - 85000, 0) = $3,000
  Time Value: $4,500 - $3,000 = $1,500

BTC-USD-250110-90000-C (Call, Strike $90k, 7 DTE)
  Market Price: $2,200
  Intrinsic Value: max(88000 - 90000, 0) = $0
  Time Value: $2,200 - $0 = $2,200 (all time value)
```

**Time Decay**: Time value는 **만기에 가까워질수록 감소** (Theta decay)

---

## 📈 Part 2: Greeks

**Greeks**: 옵션 가격의 **민감도 (sensitivity)**

### 2.1 Delta (Δ): Price Sensitivity

**Definition**: Spot price $1 변화 시 옵션 가격 변화

```
Delta = ∂(Option Price) / ∂(Spot Price)
```

**Range**:
- **Call Delta**: 0 to 1 (or 0% to 100%)
- **Put Delta**: -1 to 0 (or -100% to 0%)

**Interpretation**:
```
Delta = 0.60 (Call)
→ BTC가 $1 상승하면 Call 가격 $0.60 상승
→ Hedge ratio: 0.60 BTC short으로 delta neutral

Delta = -0.40 (Put)
→ BTC가 $1 상승하면 Put 가격 $0.40 하락
```

**Moneyness별 Delta**:
| Moneyness | Call Delta | Put Delta | Probability of ITM |
|-----------|------------|-----------|---------------------|
| **Deep OTM** | ~0.10 | ~-0.10 | ~10% |
| **OTM** | ~0.30 | ~-0.30 | ~30% |
| **ATM** | ~0.50 | ~-0.50 | ~50% |
| **ITM** | ~0.70 | ~-0.70 | ~70% |
| **Deep ITM** | ~0.95 | ~-0.95 | ~95% |

**Note**: Delta ≈ **행사 확률** (ITM으로 만기할 확률)

**Example**:
```
BTC = $88,000
BTC-USD-250110-90000-C (OTM Call, Strike $90k)
  Delta = 0.35
  → 35% 확률로 ITM 만기
  → BTC $1 상승 → Call 가격 $0.35 상승
```

**트레이더 표현법** (Delta로 옵션 지칭):

트레이더들은 옵션을 **"몇 델타"**로 부른다:

| 표현 | Delta 값 | Moneyness | 예시 |
|------|----------|-----------|------|
| **10 delta call** | Δ ≈ 0.10 | Deep OTM | "10 델타 콜 매도" |
| **25 delta call** | Δ ≈ 0.25 | OTM | "25 델타 콜 매수" (리스크 리버설) |
| **50 delta call** | Δ ≈ 0.50 | ATM | "50 델타 스트래들" |
| **75 delta call** | Δ ≈ 0.75 | ITM | "75 델타 콜 롤" |
| **90 delta call** | Δ ≈ 0.90 | Deep ITM | "90 델타 합성 롱" |

**실제 대화 예시**:
```
Trader A: "Give me price on 25 delta call, 1 week out"
Trader B: "25d call, 1W tenor, trading at 0.15 BTC"

Trader A: "Sell 10 delta put for premium?"
Trader B: "10d put, FM expiry, 0.05 BTC bid"

Trader A: "50 delta straddle on front month?"
Trader B: "ATM straddle, FM, total premium 1.2 BTC"
```

**용도**:
- **25 delta**: Risk reversal (25d call long + 25d put short)
- **50 delta**: ATM straddle/strangle
- **10 delta**: Far OTM selling (premium collection)

**Why use Delta instead of Strike?**
- Delta는 **strike-independent** (BTC 가격 변해도 "25 delta"는 항상 비슷한 위치)
- Strike는 **price-dependent** (BTC $88k일 때 $90k call = OTM, $100k일 때는 ITM)
- Hedging 계산 편리 (25 delta call 100개 = 25 BTC delta exposure)

---

### 2.2 Gamma (Γ): Delta의 변화율

**Definition**: Spot price $1 변화 시 Delta 변화

```
Gamma = ∂(Delta) / ∂(Spot Price)
```

**Range**:
- **Call/Put Gamma**: Always positive (0 to ~0.05)
- **ATM Gamma > ITM/OTM Gamma**

**Interpretation**:
```
Gamma = 0.02
→ BTC가 $1 상승하면 Delta가 0.02 증가

Example:
  Initial: Delta = 0.50, Gamma = 0.02
  BTC +$100: Delta = 0.50 + (0.02 × 100) = 0.52
```

**Moneyness별 Gamma**:
| Moneyness | Gamma | Convexity |
|-----------|-------|-----------|
| **Deep OTM/ITM** | Low (~0.001) | Flat (linear) |
| **ATM** | High (~0.03) | Curved (convex) |

**Gamma Trading**: High gamma → **큰 가격 변동 시 이익**
- Long gamma: Volatility 상승 시 유리 (straddle)
- Short gamma: Volatility 하락 시 유리 (iron condor)

**Example**:
```
Long ATM Straddle (Long Call + Long Put, same strike)
  Gamma = 0.03 (high)

BTC moves $1,000 (up or down):
  Delta change = 0.03 × 1000 = 30
  → Profit from gamma (convexity benefit)

Short gamma: 반대 (큰 변동 시 손실)
```

---

### 2.3 Theta (Θ): Time Decay

**Definition**: 하루 경과 시 옵션 가격 변화

```
Theta = ∂(Option Price) / ∂(Time)
```

**Unit**:
- **OKX BS Theta**: USD/day
- **OKX PA Theta**: BTC/day

**Range**:
- **Long options (Call/Put)**: Theta < 0 (시간 지나면 가치 감소)
- **Short options**: Theta > 0 (시간 지나면 이익)

**Interpretation**:
```
Theta = -110 USD/day (Long Call)
→ 하루 지나면 옵션 가격 $110 감소 (다른 조건 동일)

Theta = +110 USD/day (Short Call)
→ 하루 지나면 $110 이익
```

**DTE별 Theta**:
| DTE (Days to Expiry) | Theta (ATM) | Decay Rate |
|----------------------|-------------|------------|
| **30+ days** | Low (~-50) | Slow |
| **7-30 days** | Medium (~-100) | Moderate |
| **< 7 days** | High (~-200+) | Fast (exponential) |
| **Last day** | Very high (~-500+) | Extreme |

**Theta Decay Curve**: **비선형** (만기 가까울수록 가속)

**Example**:
```
BTC-USD-250110-90000-C (7 DTE, ATM)
  Theta = -$120/day

Day 1: Price = $2,500
Day 2: Price ≈ $2,500 - $120 = $2,380 (다른 조건 동일)
Day 7: Price ≈ $0 (만기, OTM이면)

→ 7일간 $2,500 손실 (time decay)
```

**Strategy**:
- **Long options**: Theta 적 (손실) → 빠른 가격 변동 필요
- **Short options**: Theta 양 (이익) → 가격 안정 시 유리

---

### 2.4 Vega (ν): Volatility Sensitivity

**Definition**: IV 1% 변화 시 옵션 가격 변화

```
Vega = ∂(Option Price) / ∂(IV)
```

**Unit**:
- **OKX BS Vega**: USD per 1% IV
- **OKX PA Vega**: BTC per 1% IV

**Range**:
- **Call/Put Vega**: Always positive (0 to ~500 USD)
- **ATM Vega > ITM/OTM Vega**

**Interpretation**:
```
Vega = $180 per 1% IV (Long Call)
→ IV가 50% → 51% (1% 상승) → Call 가격 $180 상승

Vega = -$180 per 1% IV (Short Call)
→ IV가 50% → 49% (1% 하락) → $180 이익
```

**DTE별 Vega**:
| DTE | Vega (ATM) | IV Sensitivity |
|-----|------------|----------------|
| **30+ days** | High (~$200) | Very sensitive |
| **7-30 days** | Medium (~$150) | Moderate |
| **< 7 days** | Low (~$50) | Less sensitive |

**Example**:
```
BTC-USD-250110-90000-C (14 DTE, ATM)
  Current: IV = 55%, Price = $3,000, Vega = $170

IV increases to 60% (+5%):
  New Price ≈ $3,000 + ($170 × 5) = $3,850 (+$850)

IV decreases to 50% (-5%):
  New Price ≈ $3,000 - ($170 × 5) = $2,150 (-$850)
```

**Volatility Trading**:
- **Long Vega**: IV 상승 기대 (long straddle)
- **Short Vega**: IV 하락 기대 (short straddle)

---

### 2.5 Rho (ρ): Interest Rate Sensitivity

**Definition**: 무위험 이자율 1% 변화 시 옵션 가격 변화

```
Rho = ∂(Option Price) / ∂(Risk-Free Rate)
```

**Importance**: **Crypto 옵션에서는 거의 무시** (금리 변동 작음)

**Range**:
- **Call Rho**: Positive
- **Put Rho**: Negative

**Interpretation**:
```
Rho = $50 per 1% rate (Call)
→ 금리 0% → 1% → Call 가격 $50 상승

Crypto에서는:
  - 금리 변동 < 0.1%/year
  - Rho impact < $5 (매우 작음)
  → 무시 가능
```

---

### 2.6 Greeks Summary Table

| Greek | Measures | Call | Put | Long/Short | Importance |
|-------|----------|------|-----|------------|------------|
| **Delta** | Price sensitivity | 0~1 | -1~0 | Always | ⭐⭐⭐ |
| **Gamma** | Delta change rate | Positive | Positive | High ATM | ⭐⭐ |
| **Theta** | Time decay | Negative | Negative | Long lose | ⭐⭐⭐ |
| **Vega** | IV sensitivity | Positive | Positive | Long gain | ⭐⭐⭐ |
| **Rho** | Rate sensitivity | Positive | Negative | Crypto: ignore | ⭐ |

**Priority**: **Delta, Theta, Vega** (Gamma는 advanced)

---

## 🎲 Part 3: Option Strategies

### 3.1 Covered Call (커버드 콜)

**Structure**: Long BTC + Short Call

**Example**:
```
Position:
  - Long 1 BTC @ $88,000
  - Short BTC-USD-250110-92000-C @ $1,500

Greeks:
  Delta: 1.0 (BTC) - 0.30 (Call) = 0.70
  Theta: +$80/day (time decay profit)
```

**Payoff**:
```
BTC < $92,000 at expiry:
  BTC PnL = S - 88000
  Call PnL = +$1,500 (premium kept)
  Total = S - 88000 + 1500

BTC > $92,000:
  BTC PnL = 92000 - 88000 = $4,000 (capped)
  Call PnL = +$1,500
  Total = $5,500 (max profit)
```

**Use Case**:
- BTC 상승 제한적 예상
- Premium 수익 (월 1-3%)
- Downside protection: $1,500 (limited)

---

### 3.2 Protective Put (보호 풋)

**Structure**: Long BTC + Long Put

**Example**:
```
Position:
  - Long 1 BTC @ $88,000
  - Long BTC-USD-250110-85000-P @ $1,800

Greeks:
  Delta: 1.0 (BTC) - 0.30 (Put) = 0.70
  Theta: -$90/day (cost of protection)
```

**Payoff**:
```
BTC > $85,000 at expiry:
  BTC PnL = S - 88000
  Put PnL = -$1,800 (premium lost)
  Total = S - 88000 - 1800

BTC < $85,000:
  BTC PnL = S - 88000
  Put PnL = (85000 - S) - 1800
  Total = 85000 - 88000 - 1800 = -$4,800 (max loss)
```

**Use Case**:
- BTC 보유 중 하락 위험 hedge
- Downside protection (insurance)
- Cost: $1,800 (time decay)

---

### 3.3 Straddle (스트래들)

**Structure**: Long Call + Long Put (same strike, same expiry)

**Example**:
```
Position:
  - Long BTC-USD-250110-88000-C @ $2,300
  - Long BTC-USD-250110-88000-P @ $2,100
  Total Cost: $4,400

Greeks:
  Delta: 0.50 (Call) - 0.50 (Put) = 0 (delta neutral)
  Gamma: High (ATM)
  Vega: High (long vol)
  Theta: -$200/day (high time decay)
```

**Payoff**:
```
BTC = $88,000 at expiry (ATM):
  Call PnL = -$2,300
  Put PnL = -$2,100
  Total = -$4,400 (max loss)

BTC = $95,000 (up $7k):
  Call PnL = 7000 - 2300 = $4,700
  Put PnL = -$2,100
  Total = $2,600 profit

BTC = $81,000 (down $7k):
  Call PnL = -$2,300
  Put PnL = 7000 - 2100 = $4,900
  Total = $2,600 profit

Breakeven: $88,000 ± $4,400 = $83,600 or $92,400
```

**Use Case**:
- **High volatility 예상** (큰 가격 변동)
- 방향 무관 (up or down, just move)
- Risk: $4,400 (premium), Reward: Unlimited

---

### 3.4 Strangle (스트랭글)

**Structure**: Long OTM Call + Long OTM Put (different strikes)

**Example**:
```
Position:
  - Long BTC-USD-250110-92000-C @ $1,200 (OTM)
  - Long BTC-USD-250110-84000-P @ $1,000 (OTM)
  Total Cost: $2,200

Greeks:
  Delta: 0.25 (Call) - 0.25 (Put) ≈ 0
  Vega: High
  Theta: -$100/day
```

**Payoff**:
```
BTC between $84k-$92k at expiry:
  Both expire worthless
  Total = -$2,200 (max loss)

BTC > $92,000:
  Call PnL = (S - 92000) - 1200
  Breakeven: $94,200

BTC < $84,000:
  Put PnL = (84000 - S) - 1000
  Breakeven: $82,800
```

**Straddle vs Strangle**:
| Strategy | Cost | Breakeven | Volatility Required |
|----------|------|-----------|---------------------|
| **Straddle** | High ($4,400) | Wide (±5%) | Moderate |
| **Strangle** | Low ($2,200) | Wider (±7%) | High |

**Use Case**: Extreme volatility 예상 (cheaper than straddle)

---

### 3.5 Iron Condor (아이언 콘도르)

**Structure**: Short OTM Call + Short OTM Put + Long farther OTM Call + Long farther OTM Put

**Example**:
```
Position:
  - Short BTC-USD-250110-92000-C @ $1,200 (sell)
  - Short BTC-USD-250110-84000-P @ $1,000 (sell)
  - Long BTC-USD-250110-94000-C @ $600 (buy, protection)
  - Long BTC-USD-250110-82000-P @ $500 (buy, protection)

Net Credit: ($1,200 + $1,000) - ($600 + $500) = $1,100

Greeks:
  Delta: ≈ 0 (neutral)
  Theta: +$80/day (time decay profit)
  Vega: Negative (short vol)
```

**Payoff**:
```
BTC between $84k-$92k at expiry (inside range):
  All options expire worthless
  Profit = $1,100 (max profit, net credit)

BTC > $94k or < $82k:
  Max loss = Spread width - Net credit
          = $2,000 - $1,100 = $900

Breakeven: $83,900 or $93,100
```

**Use Case**:
- **Low volatility 예상** (range-bound)
- Time decay profit
- Risk: $900, Reward: $1,100 (limited)

---

## 📊 Part 4: IV & Volatility

### 4.1 Implied Volatility (IV)

**Definition**: 옵션 시장 가격에서 역산한 **예상 변동성**

**Formula** (Black-Scholes):
```
Option Price = BS(S, K, T, r, σ)

where:
  S = Spot price
  K = Strike
  T = Time to expiry
  r = Risk-free rate
  σ = Volatility (unknown)

IV = σ that makes BS(...) = Market Price
```

**Example**:
```
BTC-USD-250110-90000-C
  Market Price: $2,500
  S = $88,000, K = $90,000, T = 7 days, r = 0%

IV = solve BS(88000, 90000, 7/365, 0, σ) = 2500
   ≈ 0.55 (55% annualized volatility)
```

**Interpretation**:
- **IV = 55%**: 시장은 BTC가 연간 55% 변동 예상
- **High IV**: 큰 가격 변동 예상 (옵션 비쌈)
- **Low IV**: 작은 변동 예상 (옵션 저렴)

---

### 4.2 IV Smile (변동성 미소)

**Definition**: 같은 만기, 다른 strike의 IV 패턴

**Shape**:
```
    IV
     |
 60% |     *           *
 55% |       *       *      ← Smile (U-shape)
 50% |         * * *
     |_____________________
          OTM  ATM  OTM
         Put       Call
```

**Moneyness별 IV**:
| Moneyness | IV | Reason |
|-----------|-----|--------|
| **Deep OTM Put** | High (~60%) | Crash protection demand |
| **ATM** | Low (~50%) | Baseline |
| **Deep OTM Call** | High (~58%) | Upside speculation |

**Crypto IV Smile**: **비대칭** (Put IV > Call IV, downside risk 높음)

---

### 4.3 IV Term Structure (만기별 IV)

**Definition**: 같은 strike, 다른 만기의 IV 패턴

**Normal Market** (평온):
```
    IV
     |
 60% |                  *
 55% |             *
 50% |        *
 45% |   *
     |_____________________
        7D  14D 30D 60D
```

**Volatility Spike** (위기):
```
    IV
     |
 80% |   *
 70% |        *
 60% |             *
 55% |                  *
     |_____________________
        7D  14D 30D 60D
       ← Front-month premium
```

**Use Case**:
- **Normal**: Long-dated options cheaper (IV낮음)
- **Spike**: Short-dated options expensive (immediate risk)

---

## 📚 Related Documentation

- **OKX Options Specifications**: `exchanges/okx/options_specifications.md` - 거래소별 스펙
- **Greeks Definitions**: `exchanges/greeks_definitions.md` - OKX PA vs BS units
- **Greeks Converter**: `exchanges/greeks_converter.py` - Unit conversion utility
- **Common Pitfalls**: `~/knowledge/research_methodology/lessons_learned/common_pitfalls.md` - Options 관련 실수

---

**Last Updated**: 2025-12-23
**Version**: 1.0
**Maintainer**: sqr

**Note**: 이 문서는 도메인 지식 (exchange 무관). 거래소별 스펙은 `exchanges/` 참조.
