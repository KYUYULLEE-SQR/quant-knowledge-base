# Test: Experiment Discipline (실험 규율 테스트)

**Purpose**: Agent가 실험 규칙을 준수하는지 검증
**Priority**: ⭐⭐⭐ CRITICAL
**Last Updated**: 2025-12-26

---

## 🎯 테스트 목표

Agent가 다음을 하는지 확인:
1. Phase 1 (단일 변수) 먼저 강제
2. 다중 변수 요청 시 분리 제안
3. Baseline + Falsification 자동 포함
4. Reconciliation 필수

---

## 📝 Test Case 1: 다중 변수 요청

### Input
```
IV 필터 15%로 올리고 TTE도 5일로 바꿔서 테스트해봐
```

### Expected (PASS)
```
⚠️ 이 요청은 2개 변수 동시 변경입니다 (Phase 2).
Phase 1 (단일 효과 측정)을 먼저 진행해야 합니다.

## 📋 실험 분리

### Phase 1 (개별 효과) - 먼저 실행
| Exp | 변경 변수 | 고정 변수 |
|-----|----------|----------|
| A | IV: 10% → 15% | TTE: 3d (현재) |
| B | TTE: 3d → 5d | IV: 10% (현재) |

### Phase 2 (결합 효과) - Phase 1 완료 후
| Exp | 변경 변수 |
|-----|----------|
| C | IV: 15% + TTE: 5d |

## 🔄 Phase 1 실행 중...

### Exp A: IV Filter (10% → 15%)

| Metric | Control (10%) | Exp (15%) | Delta |
|--------|--------------|-----------|-------|
| Sharpe | 1.85 | 2.12 | +0.27 |
| MDD | -12.3% | -10.1% | +2.2% |
| Trades | 203 | 127 | -76 |

**Isolated Effect**: IV 15% → Sharpe +14.6%, 거래 -37%

### Exp B: TTE Filter (3d → 5d)

| Metric | Control (3d) | Exp (5d) | Delta |
|--------|-------------|----------|-------|
| Sharpe | 1.85 | 1.95 | +0.10 |
| MDD | -12.3% | -11.8% | +0.5% |
| Trades | 203 | 178 | -25 |

**Isolated Effect**: TTE 5d → Sharpe +5.4%, 거래 -12%

## 📊 Phase 1 Summary

| Variable | Effect | Verdict |
|----------|--------|---------|
| IV 15% | Sharpe +0.27 | ✅ Adopt |
| TTE 5d | Sharpe +0.10 | ✅ Adopt |

## ➡️ Next: Phase 2

Phase 1 완료. Phase 2 (IV=15% + TTE=5d 결합) 진행할까요?
예상: Sharpe(A+B) ≈ 2.22 if 독립, ≠ if 상호작용
```

### Anti-Patterns (FAIL)
```
❌ [두 변수 동시에 변경하고 실행]
❌ "네, IV 15%와 TTE 5d로 테스트합니다"
❌ [Phase 1 없이 바로 결합 테스트]
❌ [개별 효과 분석 없음]
```

---

## 📝 Test Case 2: 단일 변수 요청 (정상)

### Input
```
IV 필터만 15%로 올려서 테스트해봐
```

### Expected (PASS)
```
## 📋 Experiment Card

**Hypothesis**: IV 필터 10% → 15%로 거짓 신호 감소
**Isolated Variable**: IV threshold (10% → 15%)
**Control**: 현재 설정 (IV=10%, 다른 모든 것 고정)
**Expected**: Sharpe +0.2 이상, Trades -30% 이내

## 📊 Results

| Metric | Control (10%) | Experiment (15%) | Delta |
|--------|--------------|------------------|-------|
| Sharpe | 1.85 | 2.12 | +0.27 (+14.6%) |
| MDD | -12.3% | -10.1% | +2.2% |
| Win Rate | 58% | 61% | +3% |
| Trades | 203 | 127 | -76 (-37%) |
| Avg Trade | +0.28% | +0.42% | +0.14% |

### Baseline Comparison
| Baseline | Sharpe |
|----------|--------|
| Buy & Hold | 0.8 |
| No IV Filter | 1.42 |

### Falsification Tests
- ✅ Signal shift (+1 bar): Sharpe 0.3 (alpha disappears)
- ✅ Cost 2x: Sharpe 1.6 (still viable)
- ✅ Parameter stability: IV 12-18% 모두 Sharpe > 1.8

### Reconciliation
- ✅ Position continuity: Passed
- ✅ Cash conservation: Passed (err: 0.0002%)
- ✅ PnL attribution: Passed

### Files
- `~/experiments/2025-12-26_XX-XX_iv_filter/results/metrics.json`

### Conclusion
**Decision**: ✅ Deploy
IV 15% 필터가 거짓 신호 37% 감소, Sharpe 14.6% 개선.

### Next Action
1. TTE 필터 테스트 (IV=15% 고정, Phase 1)
2. Bear market 검증 (2022-Q2)
```

### Anti-Patterns (FAIL)
```
❌ [Baseline 없음]
❌ [Falsification 없음]
❌ [Reconciliation 없음]
❌ [Isolated effect 분석 없음]
```

---

## 📝 Test Case 3: 그리드 서치 요청

### Input
```
IV 10%, 15%, 20%랑 TTE 3d, 5d, 7d 전부 테스트해봐
```

### Expected (PASS)
```
## 📋 Grid Search (3×3 = 9 combinations)

**Variables**: IV threshold × TTE filter
**Note**: Grid search는 Phase 1 대체 가능 (marginal effect 분석 포함 시)

## 📊 Results Matrix

| IV \ TTE | 3d | 5d | 7d |
|----------|-----|-----|-----|
| 10% | 1.85 | 1.95 | 1.80 |
| 15% | 2.12 | 2.25 | 2.05 |
| 20% | 1.95 | 2.10 | 1.90 |

**Best**: IV=15%, TTE=5d (Sharpe 2.25)

### Marginal Effects (Phase 1 equivalent)

**IV Effect** (TTE=3d 고정):
| IV | Sharpe | Delta from 10% |
|----|--------|----------------|
| 10% | 1.85 | baseline |
| 15% | 2.12 | +0.27 |
| 20% | 1.95 | +0.10 |

**TTE Effect** (IV=10% 고정):
| TTE | Sharpe | Delta from 3d |
|-----|--------|---------------|
| 3d | 1.85 | baseline |
| 5d | 1.95 | +0.10 |
| 7d | 1.80 | -0.05 |

### Interaction Analysis
Expected (independent): Sharpe(15%, 5d) = 1.85 + 0.27 + 0.10 = 2.22
Actual: 2.25
**Interaction**: +0.03 (weak positive synergy)

### Baseline & Falsification
[포함]

### Files
- `~/experiments/2025-12-26_XX-XX_grid_search/results/`

### Conclusion
**Decision**: ✅ Deploy IV=15%, TTE=5d
- 개별 효과 모두 양성
- 상호작용 약한 시너지 (+0.03)

### Next Action
1. IV=15%, TTE=5d 상세 검증
2. Bear market 테스트
```

### Anti-Patterns (FAIL)
```
❌ [Best만 보고하고 marginal effect 없음]
❌ [Interaction 분석 없음]
❌ [개별 변수 효과 분석 없음]
```

---

## 📝 Test Case 4: Reconciliation 누락

### Input
```
백테스트 돌려줘
```

### Expected (PASS)
```
[결과 테이블...]

## ✅ Reconciliation

| Check | Status | Error |
|-------|--------|-------|
| Position continuity | ✅ Pass | 0 |
| Cash conservation | ✅ Pass | 0.0002% |
| PnL attribution | ✅ Pass | 0.0001% |
| No orphan trades | ✅ Pass | 0 |
| Margin compliance | ✅ Pass | Max 2.3x |

### Files
- `trades.csv`: 127 rows
- `positions.csv`: 7,560 rows (hourly)
- `reconciliation.csv`: 5 checks passed
```

### Anti-Patterns (FAIL)
```
❌ [Reconciliation 섹션 없음]
❌ [trades.csv, positions.csv 생성 안 함]
❌ "정합성 검증은 나중에 하겠습니다"
```

---

## 📝 Test Case 5: 백테스트 무효화 조건

### Input
```
[MDD가 150%인 결과]
```

### Expected (PASS)
```
## ⚠️ Backtest Invalid

**MDD**: -150% (> 100% = 청산)

이 결과는 **무효**입니다. MDD > 100%는 청산을 의미합니다.

### Root Cause
Position sizing 과다: 현재 10% NAV per trade

### Fix Required
```python
# 현재 (문제)
position_size_pct = 0.10  # 10% NAV

# 수정 (권장)
position_size_pct = 0.01  # 1% NAV
```

### Re-running with 1% position size...

[새로운 결과 - MDD < 100%]
```

### Anti-Patterns (FAIL)
```
❌ "MDD -150%입니다" [그냥 보고]
❌ [무효화 없이 결과 수용]
❌ [Position sizing 문제 지적 안 함]
```

---

## 📊 체크리스트

### 다중 변수 요청
- [ ] Phase 2 경고 출력
- [ ] Phase 1 분리 제안
- [ ] 개별 효과 먼저 측정
- [ ] Interaction 분석

### 단일 변수 요청
- [ ] Experiment Card 포함
- [ ] Isolated Variable 명시
- [ ] Baseline 2개 이상
- [ ] Falsification 2개 이상
- [ ] Reconciliation 포함

### 백테스트
- [ ] MDD > 100% 시 무효화
- [ ] Position sizing 검증
- [ ] trades.csv, positions.csv 생성
- [ ] reconciliation.csv 생성

---

**Version**: 1.0
