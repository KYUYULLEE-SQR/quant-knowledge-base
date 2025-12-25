# Options Expiry & Time to Expiry (TTE)

**Purpose**: 옵션 만기 시각, TTE 계산, Greeks near expiry
**Last Updated**: 2025-12-25
**Version**: 2.0 (Condensed)

---

## 📌 Quick Reference

| Item | Value | Note |
|------|-------|------|
| **Expiry Time** | UTC 08:00 | OKX/Deribit 동일 |
| **Trading Until** | 만기 직전까지 | UTC 07:59도 거래 가능 ✅ |
| **Settlement** | Index price | OKX: snapshot, Deribit: 30min TWAP |
| **Exercise Style** | European | 만기일에만 exercise |

**핵심 3줄**:
1. Expiry = UTC 08:00 (KST 17:00)
2. TTE 1분도 거래 가능 ✅ (만기 시각까지)
3. "최소 TTE 1일" = 상장(listing) 규칙, 거래(trading) 규칙 아님

---

## ⏰ TTE Calculation

```python
from datetime import datetime

def calculate_tte(current_time, expiry_time):
    """TTE in days (continuous)."""
    diff = (expiry_time - current_time).total_seconds()
    return max(0, diff / 86400)

# ❌ Wrong (integer days only)
tte = (expiry_date - current_date).days

# ✅ Correct (continuous)
tte = (expiry_time - current_time).total_seconds() / 86400
```

| Current (UTC) | TTE (days) | 거래 가능? |
|---------------|-----------|----------|
| Expiry - 24h | 1.000 | ✅ |
| Expiry - 1h | 0.042 | ✅ |
| Expiry - 1m | 0.001 | ✅ |
| Expiry | 0.000 | ❌ 만기 |

---

## 📊 Greeks Near Expiry

| TTE | Gamma | Theta | Risk Level |
|-----|-------|-------|------------|
| 7 days | Normal | Normal | ✅ Safe |
| 1 day | 7× | 5× | ⚠️ 권장 청산 |
| 1 hour | 200× | 33× | 🔥 Explosion |
| 10 min | 2000× | Extreme | 💀 Don't trade |

**ATM Gamma Explosion**:
- TTE 10분, BTC $100 움직임 → Delta 10 변화
- 극도로 불안정, 헷징 어려움

**백테스트 권장**: TTE < 1 day → 포지션 청산

---

## 🧪 Backtest Implementation

```python
# Option 1: Close 1 day before (권장, 단순)
CLOSE_THRESHOLD_DAYS = 1.0
if tte <= CLOSE_THRESHOLD_DAYS:
    close_position()

# Option 2: Trade until last minute (현실적, 복잡)
def can_trade(current, expiry):
    return current < expiry

# Settlement at expiry
def settle(position, settlement_price, strike, opt_type):
    if opt_type == 'call':
        intrinsic = max(0, settlement_price - strike)
    else:
        intrinsic = max(0, strike - settlement_price)
    return position * intrinsic
```

---

## 🚨 Common Mistakes

| ❌ Wrong | ✅ Right |
|---------|---------|
| TTE < 1 day = 거래 불가 | 만기 직전까지 거래 가능 |
| 만기 = UTC 00:00 | 만기 = **UTC 08:00** |
| TTE = 정수만 | TTE = 연속값 (0.5, 0.001, etc.) |
| Greeks 보간 가능 | Greeks는 만기 근처 비선형, 보간 금지 |
| Settlement = mark price | Settlement = **index price** |
| Theta = 선형 감소 | Theta = 가속 감소 (비선형) |

---

## ✅ Checklist

**Before backtest**:
- [ ] TTE = continuous (not integer days)
- [ ] Trading cutoff policy 정의
- [ ] Expiry time = UTC 08:00
- [ ] Settlement logic 구현

**During backtest**:
- [ ] TTE 매 timestamp 재계산
- [ ] Greeks hourly 업데이트
- [ ] 만기 시 settlement trigger

**After backtest**:
- [ ] 만기 후 포지션 없음
- [ ] Settlement PnL = intrinsic value

---

## 📚 Related

- OKX Options: `../exchanges/okx/options_specifications.md`
- Inverse Options: `inverse_options.md`
- Greeks: `../exchanges/greeks_definitions.md`

---

**Key Message**:
✅ 만기일 UTC 07:59까지 거래 가능
❌ "TTE < 1 day = 거래 불가" 는 착각
