# Altcoin Rebalancing Strategies (2024-2025 Bear Market)

**Purpose**: Shitcoin L/S rebalancing 전략 연구 결과
**Period**: 2024-04-09 ~ 2025-12-21 (263 symbols, bear market)
**Last Updated**: 2025-12-26
**Total Strategies Tested**: 79+
**Owner**: sqr

---

## Quick Reference

| Strategy | Return | Sharpe | MDD | Category | Status |
|----------|--------|--------|-----|----------|--------|
| **Range Position (20d)** | +432.53% | 1.95 | -36.54% | Price MR | Deploy |
| **Kurtosis (20d)** | +156.50% | 1.52 | -28.67% | Statistical | Deploy |
| **Dispersion (7d/30d)** | +138.94% | 1.39 | -40.77% | Adaptive | Deploy |
| **Bollinger Band (1.5std)** | +95.73% | 1.16 | -30.59% | Band MR | Deploy |
| **Z-Score (20d)** | +89.84% | 1.11 | -30.14% | Statistical MR | Deploy |
| Volatility Sorting | +47.10% | 0.69 | -39.08% | Volatility | Deploy |
| Mean Reversion (3d) | +32.84% | 0.59 | -47.27% | Mean Reversion | Deploy |
| Beta Neutral (20d) | +26.83% | 0.53 | -49.39% | Beta | Consider |

---

## Winner #1: Range Position (Support/Resistance)

**Logic**: 최근 가격 범위 내 위치 기반 mean reversion

```python
# Core algorithm
range_pos = (current - low) / (high - low)  # 0=bottom, 1=top

# Near bottom (< 20%) → Long
# Near top (> 80%) → Short
```

**Why it works**:
- 레인지 하단 = 지지선 (support) → 반등 확률 높음
- 레인지 상단 = 저항선 (resistance) → 하락 확률 높음
- Bear market에서 특히 유효 (상승 시도 실패)

**Parameters**:
- lookback: 20d (best), 30d (okay)
- lower_pct: 0.20, upper_pct: 0.80
- top_n: 10, long_weight/short_weight: 0.5

**Trades**: 13,531 (적당한 turnover)

---

## Winner #2: Kurtosis (Fat Tail Avoidance)

**Logic**: 수익률 분포의 첨도 (뾰족함) 기반

```python
kurtosis = returns.tail(lookback).kurtosis()

# Low kurtosis Long (정규분포 유사 = 예측 가능)
# High kurtosis Short (fat tails = 급등락 위험)
```

**Why it works**:
- 저첨도 코인: 분포가 정규분포에 가까움 → 안정적
- 고첨도 코인: 극단적 움직임 빈번 → crash 위험
- Bear market에서 급락 회피 효과

**Parameters**:
- lookback: 20d (best), 30d (okay)
- top_n/bottom_n: 10
- Best risk profile: MDD -28.67% (가장 낮음)

**Trades**: 12,725

---

## Winner #3: Dispersion (Adaptive Strategy)

**Logic**: Cross-sectional dispersion에 따라 MR/Momentum 전환

```python
current_dispersion = returns.std(axis=1).mean()  # 종목 간 분산
hist_dispersion = returns.tail(30d).std(axis=1).mean()

if current_dispersion > hist_dispersion:
    # High dispersion → Mean Reversion (losers Long, winners Short)
else:
    # Low dispersion → Momentum (winners Long, losers Short)
```

**Why it works**:
- 고분산 기간: 과잉 반응 → mean reversion 유리
- 저분산 기간: 추세 지속 → momentum 유리
- 시장 상태에 자동 적응

**Parameters**:
- lookback: 7d (signal), dispersion_lookback: 30d (baseline)
- top_n/bottom_n: 10

**Trades**: 16,295

---

## Winner #4: Bollinger Band (Round 3)

**Logic**: 볼린저 밴드 기반 mean reversion

```python
mean = prices.tail(lookback).mean()
std = prices.tail(lookback).std()
upper = mean + num_std * std
lower = mean - num_std * std

band_position = (current - lower) / (upper - lower)

# Near lower band (0) = Long (oversold)
# Near upper band (1) = Short (overbought)
```

**Why it works**:
- 하단 밴드 근처 = 과매도 → 반등 확률 높음
- 상단 밴드 근처 = 과매수 → 하락 확률 높음
- Range Position과 유사하지만 변동성 기반 밴드 사용

**Parameters**:
- lookback: 20d (20*24 hours)
- num_std: 1.5 (2.0보다 약간 좋음)
- top_n/bottom_n: 10

**Return**: +95.73%
**Sharpe**: 1.16
**MDD**: -30.59%
**Trades**: 17,266

---

## Winner #5: Z-Score (Round 3)

**Logic**: 표준화된 가격 편차 기반 mean reversion

```python
mean = prices.tail(lookback).mean()
std = prices.tail(lookback).std()
z_score = (current - mean) / std

# Low z-score = Long (undervalued)
# High z-score = Short (overvalued)
```

**Why it works**:
- Z-score 낮음 = 평균 대비 저평가 → 반등
- Z-score 높음 = 평균 대비 고평가 → 하락
- 통계적으로 정규화된 신호

**Parameters**:
- lookback: 20d (20*24 hours)
- top_n/bottom_n: 10

**Return**: +89.84%
**Sharpe**: 1.11
**MDD**: -30.14%
**Trades**: 17,286

---

## Winner #6: Volatility Sorting

**Logic**: 변동성 기반 Long/Short

```python
volatility = returns.tail(lookback).std()

# Low volatility Long (안정적)
# High volatility Short (meme coin, pump-and-dump)
```

**Why it works**:
- 저변동성 코인 = mature, 덜 하락
- 고변동성 코인 = hype, crash 빈번
- Betting against volatility = betting against hype

**Parameters**:
- lookback: 20d (20*24 hours)
- top_n/bottom_n: 10

**Trades**: 12,505

---

## Winner #7: Mean Reversion (3d)

**Logic**: 최근 3일 수익률 기반 역추세

```python
momentum_3d = (1 + returns.tail(72)).prod() - 1

# Losers Long (oversold)
# Winners Short (overbought)
```

**Why it works**:
- 단기 과매수/과매도 반전
- 3d = sweet spot (1d too noisy, 7d delayed)

**Parameters**:
- lookback: 3d (72 hours)
- top_n/bottom_n: 10

**Trades**: 19,081

---

## Failed Categories (중요: 이유 학습)

| Category | Best Result | Why Failed |
|----------|-------------|------------|
| **Drawdown Hunter** | -86% | 바닥 없는 하락, 추세 지속 |
| **Recovery Momentum** | -84% | 반등 = 더 큰 하락 전조 |
| **Skewness** | -50% | 왜도 신호 무효 (theory ≠ practice) |
| **Mean-Variance** | -85% | 추정 에러 커서 역효과 |
| **Win Rate** | -26% | 승률 높다고 수익 아님 |
| **HighLow Distance** | -58% | 고점 근접 ≠ 매도 신호 |
| **All Momentum** | -70~95% | Bear market + 추격 = 고점 매수 |
| **Equal Weight Long** | -75% | Long-only = 시장 방향 노출 |
| **Consecutive Move** | -34% | 패턴 기반 = noise 많음 |
| **Relative Strength** | -35% | 상대 강도 = momentum = 실패 |
| **Momentum Persistence** | -22% | 일관된 추세 = 고점 추격 |
| **Price Acceleration** | -41% | 가속도 = momentum 변형 = 실패 |
| **Trend Strength** | -26% | 추세 강도 = momentum = 실패 |
| **ATR/Donchian Breakout** | -10% | Breakout = 고점 추격 |
| **Volatility Breakout** | -44% | 변동성 돌파 = 추세 추종 = 실패 |

**Key Lesson**: Bear market에서 모든 momentum-following/breakout/trend 전략 실패

---

## Implementation

**Location**: `/home/sqr/alt_rebal_trading/src/strategy/rebalance.py`

**Usage**:
```python
from src.strategy import (
    RangePositionRebalancer,
    KurtosisRebalancer,
    DispersionRebalancer,
    BollingerBandRebalancer,
    ZScoreRebalancer,
    VolatilitySortingRebalancer,
    MeanReversionRebalancer,
)
from src.backtest.engine import BacktestEngine, BacktestConfig

config = RebalanceConfig(rebalance_freq='1D', fee_rate=0.0004)
bt_config = BacktestConfig(initial_capital=100000, fee_rate=0.0004)

strategy = RangePositionRebalancer(config, lookback=24*20, top_n=10)
signals = strategy.generate_signals(prices)

engine = BacktestEngine(bt_config)
result = engine.run(prices, signals, verbose=False)
```

---

## Caveats & Risks

1. **Period-specific**: 2024-2025 bear market only, bull market 미검증
2. **Shitcoin universe**: 263 altcoins, majors (BTC/ETH/BNB) excluded
3. **Fees**: 4 bps taker assumed
4. **Rebalance**: Daily, no intraday
5. **Slippage**: Not modeled (실거래 시 추가 비용)

---

## Validation Results (2025-12-26)

| Strategy | Signal Shift | Cost 2x | Param Stab | Verdict |
|----------|-------------|---------|------------|---------|
| **Range Position** | PASS (Sharpe -0.20) | PASS (1.75) | PASS (CV 27%) | **CLEAN** |
| **Dispersion** | PASS (Sharpe -1.24) | PASS (1.09) | OK (CV 50%) | **CLEAN** |
| Kurtosis | WARN (0.51) | PASS (1.47) | PASS (CV 8%) | Slow factor |
| Volatility Sorting | WARN (0.70) | PASS (0.65) | PASS (CV 19%) | Slow factor |
| Mean Reversion | PASS (-2.22) | OK (0.23) | FAIL (CV 103%) | Sensitive |

**Analysis**:
- **Range Position**: 가장 robust - 모든 테스트 통과
- **Kurtosis/VolSort**: Shift 후 alpha 유지 = slow-moving factor (첨도/변동성 하루에 안 바뀜, look-ahead 아님)
- **Mean Reversion**: 3d lookback에 민감 (2.4d~3.6d 범위에서만 작동)

**Conclusion**: Range Position, Dispersion = 함정 없음, 실전 투입 가능

---

## Related

- Experiment: `~/alt_rebal_trading/experiments/2025-12-26_batch_strategies/`
- Data: `futures_data_1h` on micky:5432
- Backtest engine: `~/alt_rebal_trading/src/backtest/engine.py`

---

**Version**: 1.0
