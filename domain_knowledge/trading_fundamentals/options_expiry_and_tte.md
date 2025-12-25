# Options Expiry & Time to Expiry (TTE)

**What**: 옵션 만기 시각, 거래 가능 시점, TTE 계산의 명확한 정리
**Why Important**: 에이전트들이 "TTE 1일 = 거래 불가"로 착각하는 혼란 방지
**Critical**: 만기일 당일, 1분 전까지도 거래 가능 ✅

**Last Updated**: 2025-12-23

---

## 🎯 Quick Summary (핵심 3줄)

1. **Expiry Time**: OKX/Deribit = UTC 08:00 (만기 시각)
2. **Trading Until**: 만기 시각 **직전까지** 거래 가능 (UTC 07:59도 가능 ✅)
3. **TTE ≠ Trading Cutoff**: TTE 0.01 day (14분)도 거래 가능 ✅

**에이전트 착각**:
- ❌ "TTE 최소 1일이니까 만기 전날까지만 거래 가능"
- ✅ 만기일 UTC 07:59까지도 거래 가능 (TTE = 1분)

---

## ⏰ Expiry Time (만기 시각)

### OKX & Deribit

**공통 만기 시각**: **UTC 08:00** ✅

```
UTC: 08:00 (8:00 AM)
KST: 17:00 (5:00 PM, UTC+9)
EST: 03:00 (3:00 AM, UTC-5)
PST: 00:00 (midnight, UTC-8)
```

**Verification**:
- OKX API: `/api/v5/public/instruments` → `expTime` field
- Deribit: 30-min TWAP before UTC 08:00
- 646 BTC-USD options 모두 동일 (daily/weekly/monthly)

---

### Settlement Index

**OKX**:
- Index price snapshot at **UTC 08:00**
- Single point (not TWAP)

**Deribit**:
- **30-minute TWAP** (07:30 ~ 08:00 UTC)
- More stable, less manipulation

---

## 🕐 Trading Hours (언제까지 거래 가능?)

### Critical Rule

**거래 가능**: 만기 시각 **직전까지** ✅

```
Expiry: 2025-12-27 (금) UTC 08:00

✅ 2025-12-27 UTC 07:59:59  (1초 전)   - 거래 가능
✅ 2025-12-27 UTC 07:59:00  (1분 전)   - 거래 가능
✅ 2025-12-27 UTC 07:50:00  (10분 전)  - 거래 가능
✅ 2025-12-27 UTC 00:00:00  (8시간 전) - 거래 가능
✅ 2025-12-26 UTC 08:01:00  (24시간 전)- 거래 가능
✅ 2025-12-26 UTC 08:00:00  (정확히 1일 전) - 거래 가능

❌ 2025-12-27 UTC 08:00:00  (만기 시각) - 거래 중단
❌ 2025-12-27 UTC 08:01:00  (만기 후)   - 거래 불가
```

---

### 24/7 Trading

**OKX/Deribit**: 24시간 거래 (주말 포함)

**예외**:
- 만기 시각 (UTC 08:00) 도달 → 해당 옵션 거래 중단
- 시스템 점검 (사전 공지, 연 1-2회)

---

## 📏 TTE (Time to Expiry) Calculation

### Definition

**TTE** = 현재 시각부터 만기 시각까지 남은 시간

**단위**:
- **일(day)**: 연속적 (e.g., 0.5 day = 12 hours)
- **시간(hour)**: 정수 or 연속적
- **분(minute)**: 정수

---

### Calculation Formula

```python
from datetime import datetime

def calculate_tte(current_time, expiry_time):
    """
    Calculate Time to Expiry in days.

    Args:
        current_time: datetime (UTC)
        expiry_time: datetime (UTC 08:00)

    Returns:
        float: TTE in days (365-day year)
    """
    time_diff = expiry_time - current_time
    tte_days = time_diff.total_seconds() / 86400  # 86400 = seconds per day
    return max(0, tte_days)  # Can't be negative

# Example
expiry = datetime(2025, 12, 27, 8, 0, 0)  # UTC 08:00
current = datetime(2025, 12, 27, 7, 59, 0)  # 1 min before

tte = calculate_tte(current, expiry)
# tte = 1 / (24*60) = 0.000694 days = 1 minute
```

---

### TTE Examples (Timeline)

**Expiry**: 2025-12-27 (금) UTC 08:00

| Current Time (UTC) | TTE (days) | TTE (hours) | TTE (min) | 거래 가능? |
|-------------------|-----------|-------------|-----------|----------|
| 2025-12-20 08:00 | 7.000 | 168.0 | 10080 | ✅ |
| 2025-12-26 08:00 | 1.000 | 24.0 | 1440 | ✅ |
| 2025-12-26 20:00 | 0.500 | 12.0 | 720 | ✅ |
| 2025-12-27 00:00 | 0.333 | 8.0 | 480 | ✅ |
| 2025-12-27 07:00 | 0.042 | 1.0 | 60 | ✅ |
| 2025-12-27 07:50 | 0.007 | 0.17 | 10 | ✅ |
| 2025-12-27 07:59 | 0.001 | 0.017 | 1 | ✅ |
| 2025-12-27 07:59:30 | 0.0003 | 0.008 | 0.5 | ✅ |
| 2025-12-27 08:00 | 0.000 | 0.0 | 0 | ❌ 만기 |

**Key Insight**:
- TTE = 0.001 day (1분)도 **거래 가능** ✅
- TTE = 0 (만기 시각) → 거래 중단 ❌

---

### "Minimum TTE 1 Day" Misconception

**에이전트 착각**:
> "최소 TTE가 1일이니까, TTE < 1 day면 거래 못 한다"

**실제**:
- **"최소 TTE 1일"**은 **새 옵션 상장 규칙** (listing policy)
- 거래 중인 옵션은 **만기 직전까지** 거래 가능 ✅

**예시**:
```
OKX: 새 weekly 옵션 상장
  → 만기일 최소 1일 전에 상장 (listing)
  → 하지만 상장 후에는 만기 1분 전까지도 거래 가능 (trading)

2025-12-27 08:00 만기 옵션:
  → 2025-12-26 08:00 이전에 상장됨 (listing)
  → 2025-12-27 07:59까지 거래 가능 (trading) ✅
```

**결론**:
- Listing policy (상장) ≠ Trading cutoff (거래 중단)
- TTE < 1 day여도 **거래 가능** ✅

---

## 📊 Greeks Near Expiry

### Behavior as TTE → 0

**Delta**:
- ITM: Δ → ±1 (call/put)
- OTM: Δ → 0
- ATM: Δ ≈ 0.5 (jumpy)

**Gamma**:
- ATM: **Gamma explosion** 🔥
- Γ → ∞ as TTE → 0 (ATM)
- Risk: Small S move → Huge Δ change

**Theta**:
- θ accelerates (non-linear decay)
- Last 24h: Massive time decay
- Last 1h: Extreme decay

**Vega**:
- ν → 0 as TTE → 0
- IV changes matter less (no time value left)

---

### Gamma Explosion (ATM, TTE < 1 day)

**Definition**: Gamma → ∞ for ATM options as expiry approaches

**Example**:
```
BTC-USD-250127-50000-C (Call)
Strike: $50,000
Spot: $50,000 (exactly ATM)

TTE = 7 days:   Gamma = 0.00005
TTE = 1 day:    Gamma = 0.00035 (7× increase)
TTE = 1 hour:   Gamma = 0.01000 (200× increase)
TTE = 10 min:   Gamma = 0.10000 (2000× increase)

→ 10분 만기 옵션: BTC $100 움직이면 Delta 10 변화 (엄청난 리스크)
```

**Backtest Implication**:
- TTE < 24h: Greeks unreliable
- TTE < 1h: 극도로 불안정
- **권장**: 만기 1일 전 청산 (avoid gamma explosion)

---

## 🧪 Backtesting Implications

### 1. Trading Until Expiry (구현)

**Option 1: Trade Until Last Minute (현실적)**

```python
def can_trade_option(current_time, expiry_time):
    """
    Check if option is tradeable.

    Reality: Can trade until expiry time.
    """
    return current_time < expiry_time  # ✅ Correct

# Example
expiry = datetime(2025, 12, 27, 8, 0, 0)
current = datetime(2025, 12, 27, 7, 59, 0)

can_trade = can_trade_option(current, expiry)
# True ✅
```

**Option 2: Close 1 Day Before (백테스트 권장)**

```python
EXPIRY_CLOSE_THRESHOLD_DAYS = 1.0

def should_close_before_expiry(tte_days):
    """
    Conservative backtest: close 1 day before expiry.

    Reason: Avoid gamma explosion, wide spreads, settlement complexity.
    """
    return tte_days <= EXPIRY_CLOSE_THRESHOLD_DAYS

# Example
tte = 0.5  # 12 hours to expiry

should_close = should_close_before_expiry(tte)
# True → Close position (conservative)
```

**Trade-off**:
| Approach | Pros | Cons |
|----------|------|------|
| **Trade until last min** | Realistic, max alpha | Complex (gamma explosion, spreads) |
| **Close 1 day before** | Simple, stable | Miss some theta decay |

**Recommendation**:
- **First backtest**: Close 1 day before (simple, stable)
- **Advanced**: Model last-day behavior (gamma, spreads, settlement)

---

### 2. TTE Calculation (실시간)

**WRONG**:
```python
# ❌ Discrete TTE (only integer days)
tte_days = (expiry_date - current_date).days  # Ignores time
```

**RIGHT**:
```python
# ✅ Continuous TTE (includes hours/minutes)
tte_seconds = (expiry_time - current_time).total_seconds()
tte_days = tte_seconds / 86400

# More precise
tte_hours = tte_seconds / 3600
tte_minutes = tte_seconds / 60
```

**Why**:
- Greeks depend on **continuous TTE**, not discrete days
- TTE = 0.5 day ≠ TTE = 1 day (huge Greek difference)

---

### 3. Settlement Simulation

**At Expiry (UTC 08:00)**:

```python
def settle_option(position, settlement_price, strike, option_type):
    """
    Simulate option settlement at expiry.

    Args:
        position: Number of contracts (+ long, - short)
        settlement_price: Index price at UTC 08:00
        strike: Strike price
        option_type: 'call' or 'put'

    Returns:
        intrinsic_value: Cash received (USD)
    """
    if option_type == 'call':
        intrinsic = max(0, settlement_price - strike)
    else:  # put
        intrinsic = max(0, strike - settlement_price)

    # Long: receive intrinsic value
    # Short: pay intrinsic value
    cash_flow = position * intrinsic

    return cash_flow

# Example: Long 10 calls, K=$50k, S=$52k at expiry
cash = settle_option(
    position=10,
    settlement_price=52000,
    strike=50000,
    option_type='call'
)
# cash = 10 * max(0, 52000-50000) = 10 * 2000 = $20,000
```

**Backtest Must Track**:
1. Settlement cash flow
2. PnL = Settlement value - Premium paid
3. Portfolio reconciliation (cash in/out matches)

---

### 4. Greeks Discontinuity at Expiry

**At T = 0 (expiry)**:

```python
# Just before expiry (TTE = 1 second)
greeks = {
    'delta': 0.5,
    'gamma': 100.0,  # Massive gamma
    'theta': -500.0,  # Huge decay
    'vega': 0.01
}

# At expiry (TTE = 0)
greeks = {
    'delta': 0 or 1,  # Binary (ITM or OTM)
    'gamma': 0,       # No gamma
    'theta': 0,       # No time value
    'vega': 0         # No vol sensitivity
}
```

**Backtest Handling**:
- **Don't extrapolate** Greeks at TTE = 0
- **Close or settle** before Greeks blow up

---

## 🚨 Common Agent Mistakes (에이전트 착각 26개)

### Category 1: Trading Cutoff Confusion

#### Mistake 1: "TTE < 1 day = Can't Trade"
**Wrong**:
> "TTE가 0.5일이니까 거래 못 합니다"

**Right**:
> "TTE 0.5일(12시간)도 거래 가능. 만기 시각(UTC 08:00) 직전까지 거래 가능합니다."

---

#### Mistake 2: "Minimum TTE 1 Day = Trading Cutoff"
**Wrong**:
> "최소 TTE 1일 규칙이 있으니까 1일 전에 거래가 중단됩니다"

**Right**:
> "최소 TTE 1일은 **상장 규칙**(listing policy)이지, 거래 중단(trading cutoff)이 아닙니다. 상장 후에는 만기 직전까지 거래 가능합니다."

**Clarification**:
```
Listing policy: 새 옵션은 만기 최소 1일 전에 상장
Trading policy: 상장된 옵션은 만기 직전까지 거래 가능
```

---

#### Mistake 3: "만기일 당일은 거래 불가"
**Wrong**:
> "만기일이 2025-12-27이니까 그날은 거래 안 됩니다"

**Right**:
> "만기일 2025-12-27 UTC 08:00까지 거래 가능합니다. 그날 00:00, 07:00, 07:59 모두 가능합니다."

**Timeline**:
```
2025-12-27 (만기일)
  00:00 UTC: TTE = 8h   ✅ 거래 가능
  07:00 UTC: TTE = 1h   ✅ 거래 가능
  07:59 UTC: TTE = 1min ✅ 거래 가능
  08:00 UTC: TTE = 0    ❌ 만기 (거래 중단)
```

---

#### Mistake 4: "TTE는 정수(Integer)만 가능"
**Wrong**:
```python
tte_days = (expiry_date - current_date).days  # Only integer days
```

**Right**:
```python
tte_days = (expiry_time - current_time).total_seconds() / 86400  # Continuous
# tte_days can be 0.5, 0.1, 0.001, etc.
```

---

#### Mistake 5: "만기 시각 = UTC 00:00 (Midnight)"
**Wrong**:
> "옵션은 자정(midnight)에 만기됩니다"

**Right**:
> "OKX/Deribit 옵션은 **UTC 08:00**에 만기됩니다 (KST 17:00)."

**Verification**: OKX API, Deribit docs

---

### Category 2: Greeks Calculation Errors

#### Mistake 6: "TTE = 0일 때도 Greeks 계산 가능"
**Wrong**:
```python
# At expiry
delta = black_scholes_delta(S, K, T=0, r, sigma)
# Division by zero error!
```

**Right**:
```python
# At expiry, Greeks are undefined (or binary)
if tte <= 0:
    delta = 1 if (S > K and option_type == 'call') else 0
    gamma = 0
    theta = 0
    vega = 0
```

---

#### Mistake 7: "Theta는 선형 감소 (Linear Decay)"
**Wrong**:
```python
theta_per_day = -100
daily_decay = theta_per_day  # Constant every day
```

**Right**:
```python
# Theta accelerates near expiry
# Use OKX historical theta (non-linear)
theta = fetch_greeks(timestamp)['theta']  # Changes daily
```

**Visual**:
```
Theta Decay (Option Price):

Price
  |
  |\
  | \___
  |     \____
  |          \______
  |________________\___
  30d   20d   10d  1d  Expiry

→ 마지막 1일에 대부분 감소 (non-linear)
```

---

#### Mistake 8: "Gamma는 항상 양수"
**Wrong**:
> "Gamma는 long option이면 항상 양수입니다"

**Right**:
> "Standard options: Long → Gamma > 0
> **Inverse options**: Deep ITM → Gamma can be **negative** ⚠️"

**See**: `domain/inverse_options.md`

---

#### Mistake 9: "Greeks는 하루에 한 번만 업데이트"
**Wrong**:
```python
# Update Greeks once per day
greeks = fetch_greeks(date='2025-12-27')
```

**Right**:
```python
# Greeks update continuously (every tick)
# For backtest: hourly or more frequent
greeks = fetch_greeks(timestamp='2025-12-27 07:00:00')
```

---

#### Mistake 10: "ATM은 Strike = Spot"
**Wrong**:
> "ATM은 정확히 S = K일 때만입니다"

**Right**:
> "ATM은 보통 |S - K| / S < 2-5% 범위를 포함합니다. Traders say 'near ATM' or '~ATM'."

**Example**:
```
BTC Spot: $50,000

Strikes:
  $48,000: OTM (4% OTM)
  $49,000: Near ATM (2% OTM)
  $50,000: ATM (0% moneyness)
  $51,000: Near ATM (2% ITM)
  $52,000: ITM (4% ITM)
```

---

### Category 3: Settlement & PnL

#### Mistake 11: "Settlement = Mark Price at Expiry"
**Wrong**:
> "만기 시각의 mark price로 세틀됩니다"

**Right**:
> "**Index price** (spot 지수)로 세틀됩니다. Mark price ≠ Index price."

**OKX**: Index snapshot at UTC 08:00
**Deribit**: 30-min TWAP of index (07:30-08:00)

---

#### Mistake 12: "옵션을 hold하면 자동으로 settle PnL 계산됨"
**Wrong**:
```python
# Backtest: Just hold option until expiry, no code needed
```

**Right**:
```python
# Must explicitly simulate settlement
if current_time == expiry_time:
    intrinsic = max(0, settlement_price - strike)  # Call
    pnl = intrinsic - premium_paid
    portfolio_cash += pnl
```

---

#### Mistake 13: "Premium은 USD로 계산"
**Wrong** (for inverse options):
```python
premium_usd = premium_in_btc  # ❌ Wrong units
```

**Right**:
```python
# Inverse options: Premium in BTC
premium_btc = 0.05  # 0.05 BTC
premium_usd = premium_btc * btc_price  # Convert to USD
```

**See**: `domain/inverse_options.md`

---

#### Mistake 14: "Early Exercise 가능"
**Wrong**:
> "OKX 옵션은 언제든 exercise 가능합니다"

**Right**:
> "OKX/Deribit options are **European-style** → Exercise only at expiry."

---

### Category 4: Backtest Logic

#### Mistake 15: "만기 1분 전 Greeks 사용 가능"
**Wrong**:
```python
# TTE = 1 minute
greeks = fetch_greeks(symbol, timestamp)
delta = greeks['delta']  # Use for hedging
# ⚠️ Delta is unreliable (gamma explosion)
```

**Right**:
```python
# Avoid trading when TTE < threshold
TTE_THRESHOLD_DAYS = 1.0  # or 0.5

if tte < TTE_THRESHOLD_DAYS:
    # Close position, don't enter new trades
    close_position(reason='approaching_expiry')
```

---

#### Mistake 16: "Expiry 후에도 position 유지 가능"
**Wrong**:
```python
# Backtest continues holding after expiry
# Position still open at T > Expiry
```

**Right**:
```python
# At expiry: Force settlement
if current_time >= expiry_time:
    settle_and_close_position()
    position = 0  # No longer exists
```

---

#### Mistake 17: "Greeks interpolation 가능"
**Wrong**:
```python
# No Greeks data at 07:30, interpolate from 07:00 and 08:00
greeks_730 = (greeks_700 + greeks_800) / 2  # ❌ Wrong!
```

**Right**:
```python
# Greeks are non-linear near expiry, don't interpolate
# Use closest available data or model explicitly
greeks = fetch_greeks(timestamp='07:00')  # Use 07:00 data
```

---

#### Mistake 18: "Settlement price = Last trade price"
**Wrong**:
> "Settlement price는 마지막 거래 가격입니다"

**Right**:
> "Settlement price = **Index price** (spot 가중평균), NOT last trade price."

---

### Category 5: Time Zone & Timing

#### Mistake 19: "만기일 = 달력상 날짜"
**Wrong**:
> "2025-12-27 만기면 그날 자정까지입니다"

**Right**:
> "2025-12-27 만기 = 2025-12-27 **UTC 08:00** (정확한 시각 필요)"

---

#### Mistake 20: "KST 기준으로 계산"
**Wrong**:
```python
# Use local time (KST)
expiry_kst = datetime(2025, 12, 27, 17, 0, 0)  # KST 17:00
```

**Right**:
```python
# Always use UTC
expiry_utc = datetime(2025, 12, 27, 8, 0, 0)  # UTC 08:00

# Convert to KST if needed for display
import pytz
kst = pytz.timezone('Asia/Seoul')
expiry_kst = expiry_utc.replace(tzinfo=pytz.UTC).astimezone(kst)
```

---

#### Mistake 21: "Daylight Saving Time 고려 안 함"
**Wrong**:
```python
# EST = UTC-5 always
est_time = utc_time - timedelta(hours=5)
```

**Right**:
```python
# EST vs EDT (daylight saving)
# Use pytz to handle DST automatically
import pytz
est = pytz.timezone('US/Eastern')
est_time = utc_time.replace(tzinfo=pytz.UTC).astimezone(est)
```

---

### Category 6: Data & API

#### Mistake 22: "Greeks는 계산 가능 (No data needed)"
**Wrong**:
> "Greeks는 Black-Scholes로 계산하면 됩니다"

**Right**:
> "Historical backtest requires **historical Greeks from exchange API**. Black-Scholes ≠ OKX Greeks."

**See**: `exchanges/okx/options_specifications.md`

---

#### Mistake 23: "TTE는 metadata에서 읽기"
**Wrong**:
```python
# TTE stored in database
tte = row['tte']  # ❌ Static, doesn't update
```

**Right**:
```python
# Calculate TTE dynamically at each timestamp
tte = (expiry_time - current_time).total_seconds() / 86400
```

---

#### Mistake 24: "Option이 expired면 data 없음"
**Wrong**:
> "만기 후에는 데이터가 없으니 backtest 불가"

**Right**:
> "만기 후 settlement price는 index data에서 가져옴 (futures index, spot index)."

---

### Category 7: Risk Management

#### Mistake 25: "Gamma risk는 작음 (무시 가능)"
**Wrong**:
> "Gamma는 작은 Greek이니까 무시합니다"

**Right**:
> "TTE < 1 day, ATM 옵션의 gamma는 **massive risk**입니다. Small S move → Huge Δ change."

**Example**:
```
TTE = 1 hour, ATM call
Gamma = 0.01

BTC moves $100:
  ΔDelta = Gamma * ΔS = 0.01 * 100 = 1.0
  → Delta changes from 0.5 to 1.5 (or -0.5)
  → Extreme hedging required
```

---

#### Mistake 26: "Expiry 1일 전부터 spread 동일"
**Wrong**:
> "Spread는 항상 일정합니다"

**Right**:
> "TTE < 1 day: Spread widens significantly (2-5× wider).
> Liquidity decreases, market makers pull quotes."

---

## 📐 Full Timeline Example

### Scenario: BTC-USD-250127-50000-C

**Symbol**: BTC-USD-250127-50000-C (Call)
**Strike**: $50,000
**Expiry**: 2025-01-27 (월) UTC 08:00

---

### Timeline (7 Days Before → Expiry)

| Date & Time (UTC) | TTE (days) | TTE (hours) | 거래 가능? | Greeks Status | Notes |
|------------------|-----------|-------------|----------|--------------|-------|
| **2025-01-20 08:00** | 7.000 | 168.0 | ✅ | Normal | 1 week to expiry |
| **2025-01-23 08:00** | 4.000 | 96.0 | ✅ | Normal | 4 days to expiry |
| **2025-01-26 08:00** | 1.000 | 24.0 | ✅ | Accelerating theta | **1 day to expiry** (권장 청산 시점) |
| **2025-01-26 20:00** | 0.500 | 12.0 | ✅ | Theta ↑↑ | 12 hours to expiry |
| **2025-01-27 00:00** | 0.333 | 8.0 | ✅ | Gamma ↑ | **만기일 당일** (8시간 전) |
| **2025-01-27 04:00** | 0.167 | 4.0 | ✅ | Gamma ↑↑ | 4 hours to expiry |
| **2025-01-27 07:00** | 0.042 | 1.0 | ✅ | **Gamma explosion** 🔥 | 1 hour to expiry |
| **2025-01-27 07:30** | 0.021 | 0.5 | ✅ | Extreme gamma | 30 min to expiry |
| **2025-01-27 07:50** | 0.007 | 0.167 | ✅ | Greeks unreliable | 10 min to expiry |
| **2025-01-27 07:59** | 0.001 | 0.017 | ✅ | Delta → 0 or 1 | **1 min to expiry** |
| **2025-01-27 07:59:30** | 0.0003 | 0.008 | ✅ | Greeks blow up | 30 sec to expiry |
| **2025-01-27 08:00:00** | 0.000 | 0.0 | ❌ **Expiry** | Settlement | **거래 중단** |

---

### Greeks Evolution (Same Timeline)

**Assume**: BTC = $50,000 (exactly ATM), IV = 80%

| TTE (hours) | Delta | Gamma | Theta ($/day) | Vega | Price |
|------------|-------|-------|---------------|------|-------|
| 168 (7d) | 0.50 | 0.00005 | -$150 | $500 | $2,500 |
| 24 (1d) | 0.50 | 0.00035 | -$800 | $200 | $800 |
| 12 (0.5d) | 0.50 | 0.00070 | -$1,200 | $100 | $500 |
| 4 (4h) | 0.50 | 0.00210 | -$2,500 | $30 | $200 |
| 1 (1h) | 0.50 | 0.01000 | -$5,000 | $5 | $50 |
| 0.167 (10m) | 0.50 | 0.10000 | -$20,000 | $1 | $10 |
| 0.017 (1m) | 0.50 | 1.00000 | -$100,000 | $0 | $2 |

**Observations**:
- **Gamma**: 168h → 1h: 200× increase 🔥
- **Theta**: 168h → 1h: 33× increase 🔥
- **Price**: $2,500 → $2 (99.9% decay in last hour)

---

### Trading Activity

| Time | Action | Reason |
|------|--------|--------|
| **168h** | ✅ Can open/close | Normal trading |
| **24h** | ⚠️ **Close recommended** | Avoid gamma risk |
| **12h** | ⚠️ Spreads widen | Liquidity ↓ |
| **4h** | 🚨 High risk | Gamma explosion starting |
| **1h** | 🔴 Extreme risk | Greeks unreliable |
| **10m** | 💀 Don't trade | Chaos |
| **Expiry** | ❌ Trading stops | Settlement only |

---

## ✅ Backtest Checklist (Expiry Handling)

### Before Running Backtest

- [ ] **TTE Calculation**: Continuous (not discrete days)
- [ ] **Trading Cutoff**: Set policy (1 day before expiry? Or until last min?)
- [ ] **Greeks Source**: Historical Greeks from exchange (not calculated)
- [ ] **Settlement Logic**: Implemented (intrinsic value calculation)
- [ ] **Time Zone**: All times in UTC (not local time)
- [ ] **Expiry Time**: UTC 08:00 (verified for OKX/Deribit)
- [ ] **Gamma Risk**: Monitor TTE < 1 day (consider closing)
- [ ] **Theta Decay**: Non-linear (use exchange theta)
- [ ] **Spread Model**: Wider spreads near expiry
- [ ] **Position Close**: Force close/settle at expiry

---

### During Backtest

- [ ] **TTE Tracking**: Recalculate at every timestamp
- [ ] **Greeks Update**: Hourly or more frequent (not daily)
- [ ] **Settlement Trigger**: At expiry time, settle all open options
- [ ] **Cash Flow**: Track settlement cash in/out
- [ ] **Reconciliation**: Portfolio NAV = cash + positions MTM

---

### After Backtest

- [ ] **No Open Positions** at or after expiry time
- [ ] **Settlement PnL** matches intrinsic value
- [ ] **Greeks** not used when TTE = 0
- [ ] **NAV Continuity**: No unexplained jumps

---

## 🔗 Related Documentation

- **OKX Options Specs**: `exchanges/okx/options_specifications.md`
- **Inverse Options**: `domain/inverse_options.md` (BTC settlement)
- **Greeks Definitions**: `exchanges/greeks_definitions.md`
- **Transaction Costs**: `modeling/transaction_cost_model.md`
- **Backtesting NAV**: `experiments/backtesting_nav_policy.md`

---

## 📚 Further Reading

### Official Docs

- [OKX Options Trading](https://www.okx.com/docs-v5/en/#options-trading)
- [Deribit Options Specs](https://www.deribit.com/kb/options)

### Papers

- "Options Near Expiry" - Hull (Options, Futures, and Other Derivatives)
- Gamma risk management in option portfolios

---

**Last Updated**: 2025-12-23
**Version**: 1.0
**Author**: sqr
**Status**: ✅ Production

**Key Message**:
- ✅ 만기일 UTC 07:59까지도 거래 가능
- ✅ TTE 0.001 day (1분)도 거래 가능
- ❌ "TTE < 1 day = 거래 불가" 는 **착각**
