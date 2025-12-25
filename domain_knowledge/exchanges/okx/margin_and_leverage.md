# OKX Margin & Leverage

**Last Updated**: 2025-12-22
**Source**: OKX docs, user trading experience
**Importance**: ⭐⭐⭐ Critical - Liquidation 방지 필수

---

## Overview

**Margin** = 포지션 유지를 위해 필요한 담보
**Leverage** = 자본 대비 포지션 크기 배율

**Critical**: Liquidation 발생 시 강제 청산 + 손실 확정

---

## Margin Types

### 1. Cross Margin (교차 마진)

**Definition**: 전체 계좌 잔고를 담보로 사용

**특징**:
- ✅ 높은 liquidation 저항성 (전체 잔고 활용)
- ✅ 한 포지션 손실을 다른 포지션 이익으로 상쇄
- ❌ 한 포지션 liquidation 시 전체 계좌 위험

**Liquidation 조건**:
```
Margin Ratio = (Maintenance Margin) / (Account Equity) > 100%

Account Equity = Balance + Unrealized PnL
```

**사용 케이스**:
- 여러 포지션 동시 운영 (portfolio)
- 헷지 포지션 (long + short)
- 충분한 자본 + 보수적 레버리지

### 2. Isolated Margin (격리 마진)

**Definition**: 포지션별 독립 담보

**특징**:
- ✅ 리스크 격리 (한 포지션 liquidation = 다른 포지션 무관)
- ✅ 손실 한정 가능 (최대 = 할당 margin)
- ❌ Liquidation 가능성 높음 (제한된 담보)

**Liquidation 조건**:
```
Position Margin Ratio = (Maintenance Margin) / (Position Margin + Unrealized PnL) > 100%
```

**사용 케이스**:
- 고위험 실험 포지션
- 명확한 손절매 (isolated margin = max loss)
- 독립 전략 (서로 영향 없음)

### 3. Portfolio Margin (포트폴리오 마진) - Options

**Definition**: 포트폴리오 전체 리스크 기반 margin 계산

**특징**:
- ✅ Options + Futures 통합 리스크 계산
- ✅ 헷지 효과 인정 (delta-neutral 시 margin 감소)
- ✅ Greeks 기반 시나리오 분석
- ❌ 복잡한 계산 (블랙박스)

**Margin 계산** (simplified):
```
Portfolio Margin = max(
    Scenario Loss(+3% BTC, +20% IV),
    Scenario Loss(-3% BTC, +20% IV),
    Scenario Loss(+3% BTC, -20% IV),
    Scenario Loss(-3% BTC, -20% IV),
    ...
) * 1.2  # Buffer
```

**사용 케이스**:
- Options market making
- Delta-hedged strategies
- Complex option structures (spreads, straddles)

---

## Margin Calculation

### Initial Margin (IM)

**Definition**: 포지션 오픈 시 필요한 최소 margin

```python
# Futures
Initial Margin = (Contract Value) / Leverage

# Example: 1 BTC contract @ $50,000, 10× leverage
IM = (1 * 50000) / 10 = $5,000

# Options
Initial Margin = Premium + max(
    Underlying * (Margin_Rate + |Delta|) - OTM_Amount,
    Underlying * Margin_Rate
)
```

**Leverage Tiers** (예시, OKX 공식 확인 필요):

| Position Size (BTC) | Max Leverage | Initial Margin Rate |
|---------------------|--------------|---------------------|
| 0 - 50 | 100× | 1% |
| 50 - 200 | 50× | 2% |
| 200 - 500 | 20× | 5% |
| 500+ | 10× | 10% |

⚠️ **Verify**: https://www.okx.com/fees → Leverage Tiers

### Maintenance Margin (MM)

**Definition**: 포지션 유지를 위한 최소 margin (IM보다 낮음)

```python
# Futures
Maintenance Margin = (Contract Value) * MM_Rate

# MM Rate typically 0.4% - 0.5% (depending on tier)

# Example: 1 BTC @ $50,000, MM rate 0.5%
MM = 1 * 50000 * 0.005 = $250
```

**Margin Ratio**:
```python
Margin Ratio = (Maintenance Margin) / (Account Equity)

# Liquidation trigger: Margin Ratio > 100%
```

---

## Liquidation

### Liquidation Price Calculation

**Long Position**:
```python
Liquidation Price = Entry Price * (1 - 1/Leverage + MM_Rate)

# Example: Long 1 BTC @ $50,000, 10× leverage, MM 0.5%
Liq Price = 50000 * (1 - 1/10 + 0.005)
          = 50000 * 0.905
          = $45,250
```

**Short Position**:
```python
Liquidation Price = Entry Price * (1 + 1/Leverage - MM_Rate)

# Example: Short 1 BTC @ $50,000, 10× leverage, MM 0.5%
Liq Price = 50000 * (1 + 1/10 - 0.005)
          = 50000 * 1.095
          = $54,750
```

### Liquidation Process

```
Step 1: Margin Ratio > 100% (Maintenance margin breach)
   ↓
Step 2: Warning notification (if enabled)
   ↓
Step 3: Forced liquidation triggered
   ↓
Step 4: Position closed at Bankruptcy Price (best effort)
   ↓
Step 5a: If closed above Bankruptcy → Remaining margin returned
Step 5b: If closed below Bankruptcy → Insurance fund covers loss
```

### Auto-Deleveraging (ADL)

**When**: Insurance fund 부족 시

**Process**:
1. 수익 포지션 중 leverage 높고 수익 큰 순서로 선정
2. 선정된 포지션 강제 청산 (손실 포지션 커버 위해)
3. Bankruptcy price에 청산 (손해 없지만 기회비용 발생)

**ADL Indicator** (OKX UI):
- 🟢🟢🟢🟢🟢: ADL 위험 낮음
- 🔴🔴🔴🔴🔴: ADL 위험 높음 (수익 크고 leverage 높음)

**대응**:
- Leverage 낮추기
- 일부 이익 실현
- 헷지 포지션 추가

---

## Backtest Considerations

### 1. Liquidation Simulation (필수)

```python
def check_liquidation(position, current_price, leverage, mm_rate=0.005):
    """
    Check if position would be liquidated.

    Returns:
        is_liquidated: bool
        liquidation_price: float
    """
    if position > 0:  # Long
        liq_price = position.entry_price * (1 - 1/leverage + mm_rate)
        is_liquidated = current_price <= liq_price
    else:  # Short
        liq_price = position.entry_price * (1 + 1/leverage - mm_rate)
        is_liquidated = current_price >= liq_price

    return is_liquidated, liq_price

# In backtest loop
for bar in backtest_data:
    for position in portfolio.positions:
        is_liq, liq_price = check_liquidation(position, bar.price, leverage)

        if is_liq:
            # Force close at liquidation price (or worse)
            close_price = liq_price * 0.995  # 0.5% slippage penalty
            portfolio.close_position(position, close_price, reason='liquidated')
            logger.warning(f"LIQUIDATION: {position.symbol} @ {close_price}")
```

### 2. Margin Requirements in Position Sizing

```python
def calculate_max_position_size(account_equity, leverage, margin_buffer=0.2):
    """
    Calculate max position size considering margin.

    Args:
        account_equity: Total account value
        leverage: Target leverage
        margin_buffer: Safety buffer (20% = keep 20% free margin)

    Returns:
        max_position_usd: Max position size in USD
    """
    available_margin = account_equity * (1 - margin_buffer)
    max_position_usd = available_margin * leverage

    return max_position_usd

# Example
account_equity = 100000  # $100k
leverage = 5
max_position = calculate_max_position_size(account_equity, leverage, margin_buffer=0.3)
# = 100000 * (1 - 0.3) * 5 = $350,000 max position
```

### 3. Portfolio Margin (Options)

**Backtest Challenge**: OKX portfolio margin 계산 = 블랙박스

**Solution A - Conservative**:
```python
# Use isolated margin logic (worst case)
margin_per_option = premium + underlying * 0.15  # 15% margin
```

**Solution B - Approximation**:
```python
# Estimate portfolio margin with scenario analysis
def estimate_portfolio_margin(positions, underlying_price):
    """Simplified portfolio margin estimation."""
    scenarios = [
        (1.03, 1.2),  # +3% BTC, +20% IV
        (0.97, 1.2),  # -3% BTC, +20% IV
        (1.03, 0.8),  # +3% BTC, -20% IV
        (0.97, 0.8),  # -3% BTC, -20% IV
    ]

    max_loss = 0
    for price_mult, iv_mult in scenarios:
        scenario_loss = calculate_portfolio_loss(
            positions,
            underlying_price * price_mult,
            iv_mult
        )
        max_loss = max(max_loss, scenario_loss)

    return max_loss * 1.2  # 20% buffer
```

---

## Common Mistakes

1. ❌ **"Liquidation은 내 문제 아님"**
   - ✅ 백테스트에서도 liquidation 시뮬레이션 필수
   - ✅ MDD만 보지 말고 intraday drawdown 체크

2. ❌ **"Cross margin이면 안전함"**
   - ✅ 여러 포지션 동시 손실 시 liquidation 가능
   - ✅ Correlation 고려 (BTC/ETH 함께 떨어짐)

3. ❌ **"높은 leverage = 높은 수익"**
   - ✅ 높은 leverage = 빠른 liquidation
   - ✅ 5-10× 추천, 100× 절대 금지

4. ❌ **"Portfolio margin = 무한 leverage"**
   - ✅ 헷지 포지션도 극단 시나리오에서 margin 필요
   - ✅ Gamma explosion 주의 (만기 임박 시)

5. ❌ **"Maintenance margin만 체크"**
   - ✅ Initial margin도 체크 (포지션 오픈 가능 여부)
   - ✅ Free margin 충분한지 (추가 포지션 가능?)

---

## Risk Management Guidelines

### 1. Leverage Limits

| Strategy Type | Recommended Leverage | Max Leverage |
|--------------|---------------------|--------------|
| Directional (Long/Short) | 2-3× | 5× |
| Delta-neutral (Options) | 5-10× | 20× |
| Market Making | 10-20× | 50× |
| Arbitrage | 3-5× | 10× |

### 2. Margin Buffer

**Minimum Free Margin**: 30-50% of account equity

```python
# Check before every trade
free_margin_ratio = (account_equity - used_margin) / account_equity

if free_margin_ratio < 0.3:
    logger.warning("Low free margin! Reduce position or add collateral")
    # Don't open new positions
```

### 3. Liquidation Distance

**Target**: Liquidation price > 20% from current price

```python
liquidation_distance = abs(current_price - liquidation_price) / current_price

if liquidation_distance < 0.15:
    logger.error("Liquidation too close! Reduce leverage immediately")
```

---

## References

- **OKX Margin Guide**: https://www.okx.com/help/margin-trading
- **Leverage Tiers**: https://www.okx.com/fees
- **Related KB**:
  - [Contract Specifications](contract_specifications.md) - Position limits
  - [Risk Parameters](risk_parameters.md) - Margin tiers
- **User Experience**: Verified DMM/VIP9 tier behavior

---

**Version**: 1.0
**Critical**: Always simulate liquidation in backtest. Ignoring this = guaranteed failure.
