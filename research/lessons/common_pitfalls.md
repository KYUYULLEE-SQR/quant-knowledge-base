# Common Pitfalls in Quant Research (퀀트의 함정)

**Purpose**: 백테스트-실거래 갭 유발 함정 (빠른 참조용)
**Last Updated**: 2025-12-25
**Owner**: sqr

---

## 📌 Quick Reference

| Pitfall | 증상 | 탐지 | 예방 |
|---------|------|------|------|
| **Look-ahead Bias** | Sharpe 2-4× 과대 | Signal shift test | Strict time separation |
| **Selection Bias** | 생존자만 포함 | Universe check | Include delisted |
| **Data Snooping** | 우연히 좋은 결과 | Bonferroni correction | One hypothesis/experiment |
| **Low T-cost** | 비용 과소평가 | 2× cost test | 7-23 bps realistic |
| **Overfitting** | 미래에 작동 안 함 | Parameter stability | Simplicity bias |
| **Backtest Gap** | Paper ≠ Live | Paper trading 2주 | Slippage logging |
| **Regime Change** | 특정 구간만 작동 | Regime split test | All regimes test |

---

## 🔴 Pitfall 1: Look-Ahead Bias ⭐⭐⭐

**미래 정보를 현재 결정에 사용 = 치명적**

### Common Cases
```python
# ❌ shift(-1) = 미래 데이터
signals = df['close'].shift(-1) > df['close']

# ❌ center=True = 미래 포함
df['ma'] = df['close'].rolling(20, center=True).mean()

# ❌ bfill = 미래로 채움
df_hourly['filled'] = df_hourly['close'].fillna(method='bfill')
```

```python
# ✅ 과거 데이터만 사용
signals = df['close'].shift(1) > df['close'].shift(2)
df['ma'] = df['close'].rolling(20, center=False).mean()
df_hourly['filled'] = df_hourly['close'].fillna(method='ffill')
```

### Detection: Signal Shift Test
```python
# 신호 +1 bar shift → alpha 사라져야 정상
original_sharpe = backtest(data, shift=0)
shifted_sharpe = backtest(data, shift=1)
if abs(shifted_sharpe) > 0.5:
    print("⚠️ Look-ahead bias detected!")
```

---

## 🟠 Pitfall 2: Selection Bias ⭐⭐⭐

**살아남은 것만 선택 = Sharpe 인플레이션**

### Survivorship Bias
```python
# ❌ 현재 상장된 것만
tickers = get_current_sp500()  # 망한 회사 제외

# ✅ 과거 시점 모든 종목 (delisted 포함)
tickers = get_universe_at_date('2000-01-01', include_delisted=True)
```

### Cherry-Picking Prevention
```python
# ❌ 좋은 파라미터만 선택
best = max(results)  # Overfit

# ✅ Out-of-sample 검증
train_data = data['2015':'2022']
test_data = data['2023':'2024']
best = optimize(train_data)
final = backtest(test_data, best)  # 새 데이터에서 검증
```

---

## 🟡 Pitfall 3: Data Snooping ⭐⭐

**같은 데이터 100번 실험 = 5개 우연히 유의**

### Prevention
```python
# ❌ 여러 가설 동시 테스트
for feature in 100_features:
    for window in 95_windows:
        if sharpe > 2.0: found_alpha()  # False discovery

# ✅ One hypothesis per experiment + Bonferroni
adjusted_alpha = 0.05 / n_tests
critical_sharpe = stats.norm.ppf(1 - adjusted_alpha/2)
```

### Hold-Out Set (최종 방어)
```python
train = data['2015':'2022']    # 개발용 80%
holdout = data['2023':'2024']  # 검증용 20% (1회만 테스트)
```

---

## 🟢 Pitfall 4: Transaction Cost Underestimation ⭐⭐⭐

**백테스트 가정 vs 현실**

| 항목 | 백테스트 | 현실 |
|------|---------|------|
| Slippage | 0 | 2-10 bps |
| Fill | 100% | 30% |
| Fee | Maker only | Mixed |
| Delay | Instant | 50-500ms |

**Cost Sensitivity Test**:
```python
for cost_mult in [0.5, 1.0, 2.0]:
    sharpe = backtest(cost_model * cost_mult)
    print(f"{cost_mult}× cost: Sharpe {sharpe:.2f}")
# 2× cost에서 Sharpe < 0 → too cost-sensitive
```

📚 **상세**: `trading/cost-models/transaction_cost.md`

---

## 🔵 Pitfall 5: Overfitting ⭐⭐⭐

**과거에 과적합 = 미래 실패**

### Symptoms
- 파라미터 >10개
- Sharpe >5, MDD <5%
- ±10% 파라미터 변화 → Sharpe 50% 하락

### Prevention
```python
# Parameter stability test
for param in [0.8, 0.9, 1.0, 1.1, 1.2]:  # ±20%
    sharpe = backtest(param * optimal)
# 모든 값에서 Sharpe 비슷해야 robust

# Simplicity bias
# A: Sharpe 2.5, 20 params → 위험
# B: Sharpe 2.3, 3 params  → 선택 ✅
```

---

## 🟣 Pitfall 6: Backtest-Reality Gap ⭐⭐

### Paper Trading (필수)
```
Backtest → Paper Trading 2-4주 → Live 소액

Paper에서 확인:
- Fill rate: 100% → 70-90%
- Sharpe: 2.5 → 2.0-2.3 (acceptable)
- Slippage: 0 → 5-10 bps
```

### Slippage Logging
```python
slippage_bps = abs(actual - expected) / expected * 10000
if slippage_bps > 20:
    logger.warning(f"HIGH SLIPPAGE: {slippage_bps:.1f} bps")
```

---

## ⚫ Pitfall 7: Regime Change Ignorance ⭐⭐

**2021 Bull ≠ 2022 Bear ≠ 2023 Sideways**

```python
# Regime-split test
for regime in ['bull', 'bear', 'sideways']:
    regime_sharpe = backtest(data[data['regime'] == regime])
    print(f"{regime}: Sharpe {regime_sharpe:.2f}")

# 모든 레짐에서 Sharpe > 1.0 → robust
# 한 레짐만 작동 → regime-dependent (위험)
```

---

## ✅ Pitfall Check Checklist

**백테스트 완료 후 필수**:
- [ ] Signal shift test (+1 bar): alpha 사라지는가?
- [ ] Transaction cost 2× test: Sharpe > 0?
- [ ] Parameter stability (±20%): Sharpe 유지?
- [ ] Regime split: 모든 구간에서 작동?
- [ ] Survivorship: delisted 포함?
- [ ] Hold-out test: 새 데이터에서 검증?

**하나라도 실패 → 수정 후 재검증**

---

## 📚 Related

- `lessons_learned/lessons_learned.md` - 실패 사례 22개
- `lessons_learned/common_mistakes.md` - 코딩 실수 28개
- `trading/cost-models/transaction_cost.md` - T-cost
- `experiment_design/methodology.md` - Phase 1→2

---

**Version**: 2.0 (Condensed)
**Critical**: 모든 함정은 실제 손실 유발. 반드시 체크.
