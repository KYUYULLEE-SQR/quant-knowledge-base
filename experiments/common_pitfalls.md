# Common Pitfalls in Quant Research (퀀트의 함정)

**Last Updated**: 2025-12-22
**Source**: User experience, industry best practices, academic research
**Importance**: ⭐⭐⭐ Critical - 한 번 빠지면 몇 주/몇 달 낭비

---

## Overview

**Quant pitfall** = 백테스트에서 좋아 보이지만 실거래에서 실패하는 원인

**Why Critical**:
- 백테스트 Sharpe 3.0 → 실거래 -0.5 (자주 발생)
- 원인 대부분: 이 문서에 나열된 함정들
- **예방 가능**: 제대로 알면 피할 수 있음

---

## 1. Look-Ahead Bias (미래참조) ⭐⭐⭐

### Definition

**미래 정보를 현재 시점 결정에 사용**하는 오류

**Why Fatal**:
- 백테스트에서 불가능한 수익 창출
- 실거래에서 절대 재현 불가능
- 가장 흔하고 가장 치명적인 함정

### Common Cases

#### Case 1: 데이터 shift 실수

**❌ Bad (Look-ahead bias)**:
```python
# 오늘 가격으로 내일 신호 생성
signals = df['close'].shift(-1) > df['close']  # 내일 가격 사용! ❌

# 신호와 수익 타이밍 불일치
df['signal'] = (df['close'] > df['close'].shift(1))  # 오늘 종가로 판단
df['returns'] = df['close'].pct_change()  # 오늘 종가 기준 수익 ❌
# → 신호 생성 시점(종가)과 진입 시점(종가) 같음 = 불가능
```

**✅ Good (Correct)**:
```python
# 어제 종가로 오늘 신호 생성
signals = df['close'].shift(1) > df['close'].shift(2)  # 과거 정보만

# 신호는 t-1, 수익은 t
df['signal'] = (df['close'].shift(1) > df['close'].shift(2))
df['returns'] = df['close'].pct_change()  # 오늘 수익
# → t-1 종가 보고 판단 → t 종가에 진입/청산 ✅
```

#### Case 2: Rolling window 중앙 정렬

**❌ Bad (Look-ahead bias)**:
```python
# center=True → 미래 데이터 포함
df['ma_20'] = df['close'].rolling(20, center=True).mean()  # ❌
df['signal'] = df['close'] > df['ma_20']
# → 중앙 정렬 = 미래 10일 데이터 사용
```

**✅ Good**:
```python
# center=False (default) → 과거 데이터만
df['ma_20'] = df['close'].rolling(20, center=False).mean()  # ✅
df['signal'] = df['close'] > df['ma_20']
```

#### Case 3: Feature에 미래 데이터

**❌ Bad (Options strategy)**:
```python
# Settlement price는 만기일에만 알 수 있음!
df['fair_iv'] = calculate_iv(
    settlement_price=df['settlement_price'],  # 미래 정보! ❌
    strike=df['strike'],
    dte=df['dte']
)
```

**✅ Good**:
```python
# 현재 mark price만 사용
df['fair_iv'] = calculate_iv(
    current_price=df['mark_price'],  # 현재 정보 ✅
    strike=df['strike'],
    dte=df['dte']
)
```

#### Case 4: Resampling 후 ffill/bfill

**❌ Bad**:
```python
# 1분 → 1시간 리샘플링
df_hourly = df_minute.resample('1H').last()
df_hourly['filled'] = df_hourly['close'].fillna(method='bfill')  # 미래 채움! ❌
```

**✅ Good**:
```python
# Forward fill only (과거로 채움)
df_hourly = df_minute.resample('1H').last()
df_hourly['filled'] = df_hourly['close'].fillna(method='ffill')  # ✅
```

### Detection Methods

#### 1. Signal Shift Test (Placebo Test)

**원리**: 신호를 +1 bar shift → alpha 사라져야 정상

```python
def test_look_ahead_bias(backtest_func, data):
    """
    Test for look-ahead bias by shifting signal.

    If alpha remains after shift → look-ahead bias detected.
    """
    # Original backtest
    original_sharpe = backtest_func(data, shift=0)

    # Shifted backtest (+1 bar)
    shifted_sharpe = backtest_func(data, shift=1)

    print(f"Original Sharpe: {original_sharpe:.2f}")
    print(f"Shifted (+1) Sharpe: {shifted_sharpe:.2f}")

    if abs(shifted_sharpe) > 0.5:  # Alpha should disappear
        print("⚠️ WARNING: Possible look-ahead bias detected!")
        print("   Alpha remains after signal shift.")
        return False
    else:
        print("✅ No look-ahead bias detected.")
        return True

# Usage
is_clean = test_look_ahead_bias(my_backtest, data)
```

#### 2. Manual Code Review

**Checklist**:
- [ ] 모든 `.shift()` 확인: negative shift 없는가?
- [ ] Rolling window: `center=False` 인가?
- [ ] Feature 생성: 미래 데이터 안 쓰는가?
- [ ] Label 생성: 타이밍 명확한가? (t 정보로 t+1 예측?)

#### 3. Walk-Forward Validation

**원리**: 학습 데이터와 테스트 데이터 엄격히 분리

```python
# Train on 2023, test on 2024
train_data = data['2023-01-01':'2023-12-31']
test_data = data['2024-01-01':'2024-12-31']

# Model trained ONLY on train_data
model.fit(train_data)

# Test on unseen data
test_sharpe = backtest(model, test_data)
```

---

## 2. Selection Bias (선택 편향) ⭐⭐⭐

### Definition

**살아남은 것만** 선택해서 분석하는 오류

### Common Cases

#### Case 1: Survivorship Bias (생존 편향)

**❌ Bad**:
```python
# 현재 상장된 주식만 분석
tickers = ['AAPL', 'MSFT', 'GOOGL', ...]  # 현재 S&P 500
# → 망한 회사 제외됨 (Enron, Lehman, ...)
# → Sharpe 인플레이션

data = download_data(tickers, start='2000-01-01')
backtest_result = backtest(data)  # 과대평가된 성과 ❌
```

**✅ Good**:
```python
# 과거 시점에 상장된 모든 주식 (delisted 포함)
tickers = get_universe_at_date('2000-01-01', include_delisted=True)
# → 망한 회사도 포함

data = download_data(tickers, start='2000-01-01')
backtest_result = backtest(data)  # 현실적 성과 ✅
```

**Options equivalent**:
```python
# ❌ Bad: 만기까지 살아남은 옵션만
options = query("SELECT * FROM options WHERE expired=True AND pnl IS NOT NULL")

# ✅ Good: 도중에 delisted/청산된 것도 포함
options = query("SELECT * FROM options WHERE listed_date < backtest_end")
```

#### Case 2: Cherry-Picking (체리피킹)

**❌ Bad**:
```python
# 여러 파라미터 테스트 → 좋은 것만 선택
results = []
for ma_period in range(5, 50):
    sharpe = backtest(ma_period=ma_period)
    results.append((ma_period, sharpe))

# 최고 성과만 선택
best_period = max(results, key=lambda x: x[1])[0]  # ❌
print(f"Best MA period: {best_period}")
# → 이 파라미터는 과거 데이터에 overfitting됨
```

**✅ Good**:
```python
# Out-of-sample 테스트
train_data = data['2020':'2022']
test_data = data['2023':'2024']

# Train period에서 최적 파라미터 찾기
best_period = optimize_parameter(train_data)

# Test period에서 검증 (새로운 데이터)
test_sharpe = backtest(test_data, ma_period=best_period)

if test_sharpe > threshold:
    print(f"✅ Robust: {best_period}")
else:
    print(f"❌ Overfit: {best_period}")
```

#### Case 3: Specific Period Selection

**❌ Bad**:
```python
# "좋은 기간"만 선택
backtest_data = data['2020-03-01':'2021-12-31']  # Bull market only ❌
sharpe = backtest(backtest_data)
# → 특정 시장 국면에서만 작동
```

**✅ Good**:
```python
# 전체 기간 테스트 (Bull + Bear + Sideways)
backtest_data = data['2015-01-01':'2024-12-31']  # 10 years ✅
sharpe = backtest(backtest_data)

# 구간별 성과 분석
for period, label in [('2015-2017', 'Bull'), ('2018', 'Bear'), ('2019-2021', 'Bull'), ('2022', 'Bear')]:
    period_sharpe = backtest(data[period])
    print(f"{label}: Sharpe {period_sharpe:.2f}")

# 모든 구간에서 작동해야 robust
```

### Detection Methods

#### 1. Universe Consistency Check

```python
def check_survivorship_bias(data, start_date):
    """
    Check if universe includes delisted instruments.
    """
    # Get current universe
    current_tickers = set(data.columns)

    # Get historical universe (should be larger)
    historical_tickers = get_universe_at_date(start_date, include_delisted=True)

    missing = historical_tickers - current_tickers
    missing_count = len(missing)

    if missing_count > 0:
        print(f"⚠️ WARNING: {missing_count} delisted tickers missing")
        print(f"   Examples: {list(missing)[:10]}")
        return False
    else:
        print(f"✅ Universe complete ({len(current_tickers)} tickers)")
        return True
```

#### 2. Parameter Stability Test

```python
def test_parameter_stability(backtest_func, param_range):
    """
    Test if performance is stable around optimal parameter.

    If only one parameter value works → overfitting.
    """
    results = []
    for param in param_range:
        sharpe = backtest_func(param)
        results.append((param, sharpe))

    # Check stability
    sorted_results = sorted(results, key=lambda x: x[1], reverse=True)
    best_sharpe = sorted_results[0][1]
    second_sharpe = sorted_results[1][1]

    stability = (best_sharpe - second_sharpe) / best_sharpe

    if stability > 0.3:  # >30% drop
        print(f"⚠️ WARNING: Unstable parameter")
        print(f"   Best: {sorted_results[0]}")
        print(f"   2nd: {sorted_results[1]}")
        return False
    else:
        print(f"✅ Stable parameter (±10-20% performance)")
        return True
```

---

## 3. Data Snooping (데이터 스누핑) ⭐⭐

### Definition

**같은 데이터로 여러 번 실험** → 우연히 좋은 결과 선택

**The Problem**:
- 100개 전략 테스트 → 5개 Sharpe > 2.0 발견
- 이 중 진짜 alpha? 0-1개 (나머지는 운)
- Multiple testing problem

### Prevention

#### 1. One Hypothesis Per Experiment

```python
# ❌ Bad: 여러 가설 동시 테스트
for feature in ['ma', 'rsi', 'macd', 'bbands', ...]:  # 100 features
    for window in range(5, 100):  # 95 windows
        sharpe = backtest(feature, window)
        if sharpe > 2.0:
            print(f"Found alpha: {feature}, {window}")  # ❌ False discovery
```

```python
# ✅ Good: 하나의 가설 테스트
# Experiment: "MA crossover works?"
feature = 'ma_crossover'
window = 20  # Pre-specified (not optimized)
sharpe = backtest(feature, window)

# Result: Accept or reject hypothesis
# → 다음 실험: 다른 가설 (새로운 데이터 or out-of-sample)
```

#### 2. Bonferroni Correction

**원리**: Multiple tests → 유의수준 조정

```python
def bonferroni_test(sharpes, alpha=0.05):
    """
    Adjust significance level for multiple tests.

    Args:
        sharpes: List of Sharpe ratios from N experiments
        alpha: Desired significance level (e.g., 0.05)

    Returns:
        significant: List of truly significant strategies
    """
    n_tests = len(sharpes)
    adjusted_alpha = alpha / n_tests  # Bonferroni correction

    # Critical Sharpe for adjusted alpha
    # (Simplified: assume Sharpe ~ N(0, 1))
    from scipy import stats
    critical_sharpe = stats.norm.ppf(1 - adjusted_alpha/2)

    significant = [s for s in sharpes if abs(s) > critical_sharpe]

    print(f"Total tests: {n_tests}")
    print(f"Adjusted alpha: {adjusted_alpha:.4f}")
    print(f"Critical Sharpe: {critical_sharpe:.2f}")
    print(f"Significant strategies: {len(significant)}/{n_tests}")

    return significant
```

#### 3. Hold-Out Set (완전 분리)

```python
# ❌ Bad: 모든 데이터로 최적화
full_data = data['2015':'2024']
best_strategy = optimize(full_data)  # Overfit ❌

# ✅ Good: Hold-out set으로 최종 검증
train_data = data['2015':'2022']  # 80%
holdout_data = data['2023':'2024']  # 20% (완전히 별도)

# Train에서 개발
best_strategy = optimize(train_data)

# Hold-out에서 1회만 테스트 (no 재최적화)
final_sharpe = backtest(holdout_data, best_strategy)

if final_sharpe > threshold:
    print("✅ Strategy validated")
else:
    print("❌ Strategy failed (overfit)")
```

---

## 4. Transaction Cost Underestimation ⭐⭐⭐

### Why Common

**Backtest assumptions**:
- Zero slippage
- Instant fill
- Maker fee only
- No partial fills

**Reality**:
- 2-10 bps slippage
- Partial fills (30%)
- Mixed maker/taker
- Reorder delays

### Solution

📚 **출처**: [Transaction Cost Model](../modeling/transaction_cost_model.md)

**Key Points**:
- T-cost = fees + slippage + partial fill impact
- Test at 0.5×, 1×, 2× costs
- If Sharpe < 0 at 2× → too cost-sensitive

---

## 5. Overfitting (과최적화) ⭐⭐⭐

### Definition

**과거 데이터에 과도하게 맞춤** → 미래에 작동 안 함

### Symptoms

1. **Too many parameters** (>5-10)
2. **Perfect backtest** (Sharpe > 5, MDD < 5%)
3. **Parameter sensitivity** (±10% change → Sharpe 50% drop)
4. **Complex rules** (if-then-else 10+ levels)

### Prevention

#### 1. Regularization (Model)

```python
# ❌ Bad: Complex model, no regularization
model = RandomForestRegressor(
    n_estimators=500,
    max_depth=50,  # Very deep
    min_samples_split=2  # No pruning
)

# ✅ Good: Regularized
model = RandomForestRegressor(
    n_estimators=100,
    max_depth=5,  # Shallow (prevent overfit)
    min_samples_split=20,  # More pruning
    max_features='sqrt'  # Feature sampling
)
```

#### 2. Cross-Validation (Time-Series)

```python
# ❌ Bad: Random CV (look-ahead bias)
from sklearn.model_selection import cross_val_score
scores = cross_val_score(model, X, y, cv=5)  # Random split ❌

# ✅ Good: Time-series CV (no look-ahead)
from sklearn.model_selection import TimeSeriesSplit
tscv = TimeSeriesSplit(n_splits=5)
scores = cross_val_score(model, X, y, cv=tscv)  # ✅
```

#### 3. Simplicity Bias

**Rule**: Simpler = Better (if similar performance)

```
Strategy A: Sharpe 2.5, 20 parameters, 500 lines code
Strategy B: Sharpe 2.3, 3 parameters, 50 lines code

→ Choose B (more robust, less overfit)
```

---

## 6. Backtest-Reality Gap ⭐⭐

### Common Gaps

1. **Data quality**: Backtest (clean) vs Live (missing, outliers)
2. **Execution**: Backtest (perfect) vs Live (delays, rejects)
3. **Market impact**: Backtest (price taker) vs Live (you move market)
4. **Regime change**: Backtest (past) vs Live (future = different)

### Mitigation

#### Paper Trading (필수)

```
Backtest → Paper Trading (2-4 weeks) → Live Trading

Paper trading:
  - Real market data
  - Real execution (simulated)
  - Real delays
  - No real money

Metrics to check:
  - Fill rate: Backtest 100% → Paper 70-90%
  - Sharpe: Backtest 2.5 → Paper 2.0-2.3 (acceptable)
  - Trade count: Backtest 100 → Paper 80-95
```

#### Slippage Logging

```python
# In live trading
def execute_order(order):
    expected_price = order.price
    actual_price = exchange.fill_order(order)

    slippage_bps = abs(actual_price - expected_price) / expected_price * 10000

    logger.info(f"Order filled: Expected {expected_price}, "
                f"Actual {actual_price}, Slippage {slippage_bps:.1f} bps")

    # Alert if slippage too high
    if slippage_bps > 20:
        logger.warning(f"HIGH SLIPPAGE: {slippage_bps:.1f} bps")
```

---

## 7. Regime Change Ignorance ⭐⭐

### Definition

**시장 구조 변화** 무시 → 과거 전략 미래에 작동 안 함

### Examples

- **2020-2021**: Low vol, bull → Momentum works
- **2022**: High vol, bear → Reversion works
- **2023-2024**: Choppy → Range-bound strategies

### Solution

#### Regime-Aware Backtest

```python
def backtest_by_regime(data, strategy):
    """
    Test strategy performance by market regime.

    Regime classification (simple):
      - Bull: +20% trailing 6M
      - Bear: -20% trailing 6M
      - Sideways: else
    """
    data['regime'] = classify_regime(data)

    results = {}
    for regime in ['bull', 'bear', 'sideways']:
        regime_data = data[data['regime'] == regime]
        sharpe = backtest(regime_data, strategy)
        results[regime] = sharpe

    print("Performance by Regime:")
    for regime, sharpe in results.items():
        print(f"  {regime.capitalize()}: Sharpe {sharpe:.2f}")

    # Strategy is robust if works in all regimes
    if min(results.values()) > 1.0:
        print("✅ Regime-robust strategy")
    else:
        print("⚠️ Regime-dependent strategy")

    return results
```

---

## Summary Table

| Pitfall | Detection | Prevention |
|---------|-----------|-----------|
| **Look-ahead bias** | Signal shift test, Code review | Strict time separation, Placebo test |
| **Selection bias** | Universe check, Period analysis | Include delisted, Full period test |
| **Data snooping** | Multiple testing correction | One hypothesis per experiment, Hold-out set |
| **Low t-cost** | Cost sensitivity test | Realistic costs (7-23 bps), 2× test |
| **Overfitting** | Parameter stability, CV | Regularization, Simplicity bias |
| **Backtest gap** | Paper trading | Paper 2-4 weeks, Slippage logging |
| **Regime change** | Regime-split analysis | Test all regimes, Adaptive strategies |

---

## Agent Protocol: Pitfall Check

**BEFORE finalizing strategy:**

1. ✅ Read this file (common_pitfalls.md)
2. ✅ Run **all** detection tests:
   - Signal shift (look-ahead)
   - Cost sensitivity (2×)
   - Parameter stability (±20%)
   - Regime split
3. ✅ Document which pitfalls checked (in README)
4. ✅ If any test fails → FIX, don't ignore
5. ✅ Recommend paper trading before live

**Example**:
```
User: "이 전략 백테스트 완료했어"

Agent:
  [Reads common_pitfalls.md]

  "백테스트 검증 체크리스트:

   ⚠️ 필수 확인 항목:
   1. Look-ahead bias test (signal shift +1)
   2. Transaction cost 2× test
   3. Parameter stability (±20%)
   4. Regime 구간별 성과

   현재 상태:
   - Sharpe: 2.5 (좋음)
   - 하지만 검증 안 됨 → 실거래 위험

   진행 방법:
   1. 위 4가지 테스트 자동 실행
   2. 모두 통과 → Paper trading 2주
   3. Paper 성과 OK → Live 소액 배포

   📚 출처: knowledge/experiments/common_pitfalls.md

   지금 검증 테스트 시작할까요?"
```

---

## References

- **Advances in Financial Machine Learning** (Marcos López de Prado) - Data snooping, overfitting
- **Related KB**:
  - [Experiment Methodology](methodology.md) - One variable at a time
  - [Transaction Cost Model](../modeling/transaction_cost_model.md) - Realistic costs
  - [Lessons Learned](lessons_learned.md) - Actual failure cases
- **Academic**: Bailey et al. (2014) "The Probability of Backtest Overfitting"

---

**Version**: 1.0
**Critical**: Every pitfall in this list has caused real money loss. Take seriously.
