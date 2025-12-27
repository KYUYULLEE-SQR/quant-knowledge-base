# Altcoin Rebalancing Strategies

**Period**: 2024-04-09 ~ 2025-12-21 (263 shitcoins)
**Last Updated**: 2025-12-26
**Strategies Tested**: 79+

---

## Quick Reference

| Strategy | Full Period | 2024 | 2025 | Consistency | Status |
|----------|-------------|------|------|-------------|--------|
| **Range Position (20d)** | Sharpe 1.95 | 2.40 | 1.38 | ✅ S-Tier | Deploy |
| **Kurtosis (20d)** | Sharpe 1.52 | 0.36 | 2.16 | ✅ A-Tier | Deploy |
| **Dispersion (7d/30d)** | Sharpe 1.39 | 0.17 | 2.51 | ✅ A-Tier | Deploy |
| **Bollinger Band (1.5std)** | Sharpe 1.16 | 1.60 | 0.56 | ✅ B-Tier | Deploy |
| **Z-Score (20d)** | Sharpe 1.11 | 1.42 | 0.61 | ✅ B-Tier | Deploy |
| Volatility Sorting | Sharpe 0.69 | -0.09 | 0.99 | ❌ | Shelve |
| Mean Reversion (3d) | Sharpe 0.59 | 1.64 | -0.14 | ❌ | Shelve |

**Consistency**: 양 년도 모두 Sharpe > 0

---

## Yearly Comparison (2024 vs 2025)

| Strategy | 2024 Return | 2024 Sharpe | 2025 Return | 2025 Sharpe |
|----------|-------------|-------------|-------------|-------------|
| Range Position | +106.10% | 2.40 | +96.75% | 1.38 |
| Kurtosis | +4.92% | 0.36 | +128.09% | 2.16 |
| Dispersion | -0.55% | 0.17 | +181.85% | 2.51 |
| Bollinger Band | +45.77% | 1.60 | +15.77% | 0.56 |
| Z-Score | +39.08% | 1.42 | +18.06% | 0.61 |
| Volatility Sorting | -11.05% | -0.09 | +47.91% | 0.99 |
| Mean Reversion (3d) | +55.96% | 1.64 | -17.37% | -0.14 |

**Key Insight**:
- **Range Position** = 유일하게 양 년도 Sharpe > 1.0
- **Mean Reversion (3d)** = 2024 강세, 2025 손실 → 레짐 의존적

---

## S-Tier: Range Position

**Logic**: 가격 범위 내 위치 기반 mean reversion

```python
range_pos = (current - low) / (high - low)  # 0=bottom, 1=top
# Near bottom (< 20%) → Long
# Near top (> 80%) → Short
```

**Why it works**: 지지선/저항선에서 반전 확률 높음

**Parameters**: lookback=20d, lower_pct=0.20, upper_pct=0.80, top_n=10

---

## A-Tier: Kurtosis, Dispersion

### Kurtosis
```python
kurtosis = returns.tail(lookback).kurtosis()
# Low kurtosis → Long (정규분포 유사)
# High kurtosis → Short (fat tails)
```

### Dispersion
```python
if current_dispersion > hist_dispersion:
    # High dispersion → Mean Reversion
else:
    # Low dispersion → Momentum
```

---

## B-Tier: Bollinger Band, Z-Score

### Bollinger Band
```python
band_position = (current - lower) / (upper - lower)
# Near lower band → Long
# Near upper band → Short
```

### Z-Score
```python
z_score = (current - mean) / std
# Low z-score → Long
# High z-score → Short
```

---

## Failed Categories

| Category | Result | Reason |
|----------|--------|--------|
| All Momentum | -70~95% | Bear market + 추격 = 고점 매수 |
| Breakout (ATR/Donchian) | -10~44% | 돌파 = 추세 추종 = 실패 |
| Drawdown Hunter | -86~92% | 바닥 없는 하락 |
| Skewness/Mean-Variance | -50~88% | 이론 ≠ 실제 |

---

## Implementation

**Location**: `~/alt_rebal_trading/src/strategy/rebalance.py`

```python
from src.strategy import RangePositionRebalancer, KurtosisRebalancer
from src.backtest.engine import BacktestEngine, BacktestConfig

config = RebalanceConfig(rebalance_freq='1D', fee_rate=0.0004)
strategy = RangePositionRebalancer(config, lookback=24*20, top_n=10)
```

---

## Caveats

1. **Bear market only** (2024-2025), bull market 미검증
2. **Shitcoins only** (263), majors excluded
3. **Daily rebalance**, slippage 미반영
4. **Mean Reversion (3d)** = 레짐 의존적 (2025 손실)

---

## Related

- Experiment: `~/alt_rebal_trading/experiments/2025-12-26_batch_strategies/`
- Data: `futures_data_1h` on micky:5432

---

**Version**: 2.0 (Yearly comparison added)
