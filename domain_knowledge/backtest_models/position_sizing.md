# Position Sizing

**Purpose**: 포지션 사이징 방법론 (Notional vs Premium)
**Last Updated**: 2025-12-26
**Version**: 1.0

---

## 📌 Quick Reference

| Method | 계산 | 용도 | 특징 |
|--------|------|------|------|
| **Notional Sizing** | NAV × % / underlying_price | 옵션, 선물 | 기초자산 노출 기준 |
| **Premium Sizing** | NAV × % / option_premium | 옵션 매수 | 지불 금액 기준 |
| **Contract Sizing** | 고정 계약 수 | 단순 백테스트 | ❌ 비추천 |

---

## 🎯 Notional Sizing (핵심)

### 정의

**Notional = 기초자산 가치 기준 포지션 크기**

옵션/선물에서 "얼마나 큰 포지션인가"를 **기초자산 노출(underlying exposure)** 기준으로 측정.

### 공식

```python
# Notional Sizing
notional_usd = NAV * notional_pct
contracts = notional_usd / underlying_price

# Example:
# NAV = $1,000,000
# Notional % = 10%
# BTC price = $100,000
# → Notional = $100,000
# → Contracts = $100,000 / $100,000 = 1.0 BTC
```

### 코드 구현

```python
def calculate_notional_size(
    nav: float,
    notional_pct: float,
    underlying_price: float
) -> float:
    """
    Notional 기준 포지션 사이즈 계산.

    Args:
        nav: 순자산가치 (e.g., $1,000,000)
        notional_pct: Notional 비율 (e.g., 0.10 = 10%)
        underlying_price: 기초자산 가격 (e.g., BTC $100,000)

    Returns:
        contracts: 기초자산 단위 계약 수 (e.g., 1.0 BTC)

    Example:
        >>> calculate_notional_size(1_000_000, 0.10, 100_000)
        1.0  # 1 BTC worth of options
    """
    notional_usd = nav * notional_pct
    contracts = notional_usd / underlying_price
    return contracts
```

### 예시

| NAV | Notional % | BTC Price | Notional USD | Contracts |
|-----|------------|-----------|--------------|-----------|
| $1,000,000 | 10% | $100,000 | $100,000 | 1.0 BTC |
| $1,000,000 | 10% | $50,000 | $100,000 | 2.0 BTC |
| $1,000,000 | 5% | $100,000 | $50,000 | 0.5 BTC |
| $500,000 | 10% | $100,000 | $50,000 | 0.5 BTC |

**핵심**: BTC 가격이 변해도 **USD 노출은 동일** ($100,000)

---

## 🔄 Notional vs Premium Sizing

### Premium Sizing (비교용)

```python
def calculate_premium_size(
    nav: float,
    premium_pct: float,
    option_premium: float
) -> float:
    """
    Premium 기준 포지션 사이즈 계산.

    Args:
        nav: 순자산가치
        premium_pct: Premium 비율 (e.g., 0.01 = 1%)
        option_premium: 옵션 프리미엄 (USD per contract)

    Returns:
        contracts: 계약 수
    """
    premium_budget = nav * premium_pct
    contracts = premium_budget / option_premium
    return contracts
```

### 차이점

| 측면 | Notional Sizing | Premium Sizing |
|------|-----------------|----------------|
| **기준** | 기초자산 노출 | 지불 금액 |
| **용도** | 옵션 매도, 선물 | 옵션 매수 |
| **리스크 측정** | 기초자산 움직임 기준 | 최대 손실 기준 |
| **Greeks 해석** | Delta 1 = 1 BTC 노출 | 무관 |

### 예시: 같은 NAV, 다른 결과

```python
NAV = 1_000_000
BTC_price = 100_000

# Option: BTC-100000-P (ATM Put)
# Premium: $5,000 per 1 BTC

# Notional 10%
notional_contracts = 1_000_000 * 0.10 / 100_000  # = 1.0 BTC
premium_paid = 1.0 * 5_000  # = $5,000 (0.5% of NAV)

# Premium 1%
premium_contracts = 1_000_000 * 0.01 / 5_000  # = 2.0 BTC
notional_exposure = 2.0 * 100_000  # = $200,000 (20% of NAV)
```

**결론**:
- Notional 10% → Premium 0.5% 소비
- Premium 1% → Notional 20% 노출

---

## ⚠️ 언제 어떤 방식?

### Notional Sizing 사용 (권장)

- ✅ **옵션 매도 (Short Options)**: 노출 리스크 관리
- ✅ **선물 거래**: 레버리지 관리
- ✅ **델타 헷징**: 기초자산 노출 매칭
- ✅ **포트폴리오 리스크 관리**: 섹터/자산 노출 제한

### Premium Sizing 사용

- ✅ **옵션 매수 (Long Options)**: 최대 손실 = Premium
- ✅ **보험성 헷지**: 지불 비용 기준
- ✅ **복권형 베팅**: 소액 투입

---

## 💻 백테스트 통합

```python
class PositionSizer:
    """Position sizing for backtesting."""

    def __init__(
        self,
        method: str = 'notional',  # 'notional' or 'premium'
        size_pct: float = 0.10,
        max_leverage: float = 3.0
    ):
        self.method = method
        self.size_pct = size_pct
        self.max_leverage = max_leverage

    def calculate(
        self,
        nav: float,
        underlying_price: float,
        option_premium: float = None
    ) -> float:
        """
        Calculate position size in contracts (underlying units).

        Returns:
            contracts: Position size in underlying units (e.g., BTC)
        """
        if self.method == 'notional':
            contracts = (nav * self.size_pct) / underlying_price
        elif self.method == 'premium':
            if option_premium is None:
                raise ValueError("Premium required for premium sizing")
            contracts = (nav * self.size_pct) / option_premium
        else:
            raise ValueError(f"Unknown method: {self.method}")

        # Leverage check
        notional_exposure = contracts * underlying_price
        if notional_exposure / nav > self.max_leverage:
            contracts = (nav * self.max_leverage) / underlying_price

        return contracts


# Usage
sizer = PositionSizer(method='notional', size_pct=0.10)

nav = 1_000_000
btc_price = 100_000
option_premium = 5_000

contracts = sizer.calculate(nav, btc_price)
print(f"Notional 10%: {contracts:.2f} BTC")  # 1.00 BTC

# Premium sizing
sizer_premium = PositionSizer(method='premium', size_pct=0.01)
contracts_p = sizer_premium.calculate(nav, btc_price, option_premium)
print(f"Premium 1%: {contracts_p:.2f} BTC")  # 2.00 BTC
```

---

## ✅ Checklist

- [ ] Sizing method 선택: Notional vs Premium
- [ ] NAV 기준 명확히 (Mark-to-Market)
- [ ] Underlying price source 정의
- [ ] Max leverage 제한 설정
- [ ] 백테스트 config에 sizing method 기록

---

## 📚 Related

- Backtesting Integrity: `backtesting_integrity.md` (rules/10)
- Slippage: `slippage_estimation.md`
- Fill Probability: `fill_probability.md`
- Transaction Cost: `transaction_cost_model.md`

---

**Key Insight**:
- **Notional Sizing** = "BTC 가격이 얼마든, NAV의 10%에 해당하는 BTC 노출"
- **Premium Sizing** = "옵션 프리미엄으로 NAV의 1%를 지불"
- 옵션 매도 전략에서는 **Notional Sizing** 권장 (리스크 = 기초자산 움직임)
