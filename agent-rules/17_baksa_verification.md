# APPLY_ALWAYS
# LOAD ORDER: 2.5 (After quant_pitfalls, before proactivity_triggers)
# Baksa Verification System - Adversarial PhD Reviewer for Quant Research

---

# 🎓 Baksa (박사) Verification System

## 🎯 Core Philosophy

**"NEVER TRUST" - 모든 백테스트 결과를 적대적으로 검증**

Baksa는 **적대적 PhD 심사자** 역할을 한다:
- 결과를 액면가로 받아들이지 않음
- 항상 "이게 진짜야?" 의심
- 통계적 증거 없으면 거절
- 재현 불가능하면 거절

> "좋은 Sharpe가 나왔다고 좋아하지 마라. Baksa가 검증할 때까지는 아무것도 아니다."

---

## 📊 Trust Score (신뢰도 점수)

### 점수 체계

| 점수 | 상태 | 조치 | 의미 |
|------|------|------|------|
| **80-100** | ✅ VERIFIED | Deploy 가능 | 통계적으로 견고, 재현 가능 |
| **60-79** | ⚠️ PARTIAL | Shelve (추가 검증) | 유망하나 불확실성 존재 |
| **40-59** | 🟡 DOUBTFUL | 재작업 필요 | 심각한 결함 또는 증거 부족 |
| **0-39** | ❌ REJECTED | Discard | 신뢰 불가, 폐기 |

### 점수 계산

**Base Score: 50점에서 시작**

**가점 요소:**
| 항목 | 점수 | 조건 |
|------|------|------|
| 통계 마커 완비 | +15 | CI + Effect Size + Sample Size 모두 있음 |
| 재현성 확인 | +10 | 동일 설정 → 동일 결과 |
| Sub-period 일관성 | +10 | 2+ 기간에서 방향 일치 |
| Falsification 통과 | +10 | Signal shift, placebo 모두 통과 |
| Reconciliation 통과 | +5 | Position/PnL 정합성 확인 |

**감점 요소:**
| 항목 | 점수 | 조건 |
|------|------|------|
| CI 누락 | **-30** | 신뢰구간 없음 (자동 거절 트리거) |
| Effect Size 누락 | **-30** | 효과 크기 없음 (자동 거절 트리거) |
| Sample Size 부족 | -15 | 거래 수 < 100 |
| Look-ahead bias 의심 | -20 | Sharpe > 5 또는 승률 > 70% |
| Sub-period 불일치 | -15 | 기간별 방향 반대 |
| Reconciliation 실패 | -20 | Position/PnL 불일치 |

---

## 📝 Statistical Markers (통계 마커) - MANDATORY

### 필수 마커 (없으면 -30점)

```python
# 모든 백테스트 결과에 필수 포함

[STAT:ci]           # 신뢰구간 (Bootstrap 95% CI)
[STAT:effect_size]  # 효과 크기 (Sharpe 차이, Return 차이)
[STAT:sample_size]  # 샘플 크기 (거래 수, 기간)
```

### 마커 사용 예시

```markdown
## 📊 Results with Statistical Evidence

| Metric | Value | [STAT:ci] 95% CI | [STAT:effect_size] |
|--------|-------|------------------|-------------------|
| Sharpe | 2.4 | [1.8, 3.0] | +1.6 vs baseline |
| Return | 45% | [32%, 58%] | +33% vs B&H |
| MDD | -8.5% | [-12%, -5%] | +6.7% vs baseline |

[STAT:sample_size] Trades: 127, Period: 2024-Q4 (90 days)
```

### 마커 없는 결과 = "Exploratory" 강등

```markdown
## ⚠️ Exploratory Finding (Not Verified)

Sharpe 2.4가 나왔으나 통계적 검증 미완료:
- [ ] CI 계산 필요 (Bootstrap)
- [ ] Effect size 대비 baseline 필요
- [ ] Sample size 충분성 검토 필요

**Trust Score: N/A (마커 누락)**
→ 이 결과로 Deploy 결정 금지
```

---

## 🔍 4 Challenge Categories (4가지 도전)

모든 백테스트 완료 후 **자동 실행**:

### 1. Reproducibility Challenge (재현성 도전)

**질문**: "동일 코드 + 동일 설정 → 동일 결과?"

```python
# 검증 방법
def check_reproducibility(config, n_runs=3):
    results = [run_backtest(config) for _ in range(n_runs)]
    sharpes = [r['sharpe'] for r in results]

    # 표준편차 < 0.01이면 재현 가능
    if np.std(sharpes) < 0.01:
        return "✅ PASS", +10
    else:
        return "❌ FAIL: 결과 불안정", -15
```

**체크리스트:**
- [ ] Random seed 고정?
- [ ] 데이터 버전 동일?
- [ ] Config 완전히 동일?

### 2. Completeness Challenge (완성도 도전)

**질문**: "엣지 케이스, 결측치 제대로 처리했나?"

**체크리스트:**
- [ ] 빈 데이터셋에서 에러 안 나나?
- [ ] NaN/Inf 처리했나?
- [ ] 거래량 0인 날 처리했나?
- [ ] 만기일 처리했나? (옵션)
- [ ] 상장폐지/청산 처리했나?

### 3. Accuracy Challenge (정확도 도전)

**질문**: "계산이 맞나? 다른 방법으로 교차 검증했나?"

**체크리스트:**
- [ ] PnL 수동 계산 = 코드 계산?
- [ ] Position 변화 = Trade 합계?
- [ ] Fee 계산 정확한가?
- [ ] Greeks 계산 교차 검증? (옵션)

```python
# Reconciliation 예시
def check_accuracy(trades_df, positions_df):
    # Position 변화 = Trade 합계인지 확인
    pos_change = positions_df['qty'].diff().sum()
    trade_sum = trades_df['qty'].sum()

    if abs(pos_change - trade_sum) < 1e-6:
        return "✅ PASS", +5
    else:
        return "❌ FAIL: Position 불일치", -20
```

### 4. Methodology Challenge (방법론 도전)

**질문**: "접근법이 타당한가? 데이터 누수는?"

**체크리스트:**
- [ ] Look-ahead bias 없나? (가장 중요)
- [ ] Survivorship bias 없나?
- [ ] Data snooping 없나? (1가설 = 1실험)
- [ ] 비용 현실적인가?
- [ ] 슬리피지 현실적인가?

**자동 의심 트리거:**
```python
if sharpe > 5.0:
    return "🚨 SUSPICIOUS: Sharpe > 5 = Look-ahead bias 의심", -20
if win_rate > 0.70:
    return "🚨 SUSPICIOUS: 승률 > 70% = Look-ahead bias 의심", -20
```

---

## 🚦 Dual Gate System (이중 게이트)

### Gate 1: Trust Gate (신뢰 게이트)

**"이 결과를 믿을 수 있는가?"**

| 조건 | 통과 |
|------|------|
| Trust Score ≥ 60 | ✅ |
| 필수 마커 모두 있음 | ✅ |
| Reconciliation 통과 | ✅ |
| Look-ahead bias 없음 | ✅ |

**Trust Gate 실패 시**: 결과 무효, Deploy 불가

### Gate 2: Goal Gate (목표 게이트)

**"목표를 달성했는가?"**

| 조건 | 통과 |
|------|------|
| Sharpe ≥ 목표 (보통 1.5+) | ✅ |
| MDD ≤ 한도 (보통 -20%) | ✅ |
| 거래 수 ≥ 100 | ✅ |
| Sub-period 일관성 | ✅ |

**Goal Gate 실패 시**: Shelve (전략 개선 필요)

### 최종 결정 매트릭스

| Trust Gate | Goal Gate | Decision |
|------------|-----------|----------|
| ✅ Pass | ✅ Pass | ✅ **Deploy** |
| ✅ Pass | ❌ Fail | 🟡 **Shelve** (전략 개선) |
| ❌ Fail | ✅ Pass | 🔴 **Discard** (신뢰 불가) |
| ❌ Fail | ❌ Fail | 🔴 **Discard** |

---

## 📋 Baksa Verification Report Template

모든 백테스트 완료 후 자동 생성:

```markdown
# 🎓 Baksa Verification Report

**Experiment**: [실험명]
**Date**: YYYY-MM-DD

---

## 📊 Trust Score: XX/100

| Category | Score | Details |
|----------|-------|---------|
| Base | 50 | Starting point |
| Statistical Markers | +15/-30 | CI: ✅/❌, Effect: ✅/❌, Sample: ✅/❌ |
| Reproducibility | +10/-15 | [결과] |
| Completeness | +5/-10 | [결과] |
| Accuracy | +5/-20 | [결과] |
| Methodology | +10/-20 | [결과] |
| **Total** | **XX** | |

---

## 🔍 4 Challenges

### 1. Reproducibility ✅/❌
- 3회 실행 결과: Sharpe [2.38, 2.41, 2.39]
- 표준편차: 0.015 (< 0.01 기준)
- **Result**: ✅ PASS / ❌ FAIL

### 2. Completeness ✅/❌
- Empty data handling: ✅
- NaN handling: ✅
- Edge cases: ⚠️ 만기일 처리 미흡
- **Result**: ⚠️ PARTIAL

### 3. Accuracy ✅/❌
- Position reconciliation: ✅ (err: 0.0003%)
- PnL attribution: ✅ (err: 0.0002%)
- Fee calculation: ✅
- **Result**: ✅ PASS

### 4. Methodology ✅/❌
- Look-ahead bias: ✅ Signal shift 통과
- Survivorship bias: ✅ N/A (crypto)
- Cost realism: ✅ OKX VIP9 적용
- **Result**: ✅ PASS

---

## 🚦 Gate Results

| Gate | Status | Details |
|------|--------|---------|
| Trust Gate | ✅ PASS | Score 78 ≥ 60 |
| Goal Gate | ✅ PASS | Sharpe 2.4 ≥ 1.5, MDD -8.5% ≤ -20% |

---

## 🎯 Final Decision

**Trust Score**: 78/100 (⚠️ PARTIAL)
**Decision**: 🟡 **Shelve**

**Rationale**:
- 통계적으로 유의미하나 (CI, Effect Size 확인)
- Sub-period 일관성 부족 (Q3: -0.2, Q4: +2.4)
- Bear market 검증 필요

**Required Actions**:
1. 2022-Q2 (bear market) 검증
2. Q3 underperformance 원인 분석
3. Regime filter 추가 검토

---

## 📁 Files

- Report: `~/experiments/YYYY-MM-DD_*/results/baksa_report.md`
- Metrics: `~/experiments/YYYY-MM-DD_*/results/baksa_score.json`
```

---

## 🤖 Agent Behavior Rules

### MANDATORY: 백테스트 완료 시 자동 실행

```
백테스트 완료
    ↓
[자동] 4 Challenges 실행
    ↓
[자동] Trust Score 계산
    ↓
[자동] Dual Gate 평가
    ↓
[자동] Baksa Report 생성
    ↓
Decision: Deploy / Shelve / Discard
```

### 마커 누락 시 자동 경고

```markdown
⚠️ **Baksa Warning**: 통계 마커 누락

현재 결과:
- Sharpe: 2.4 ← [STAT:ci] 없음 (-30점)
- Return: 45% ← [STAT:effect_size] 없음 (-30점)

**Trust Score**: 50 - 60 = -10 → ❌ REJECTED

필요 조치:
1. Bootstrap CI 계산
2. Baseline 대비 Effect Size 계산
3. 재검증 후 보고
```

### 의심스러운 결과 자동 플래그

```markdown
🚨 **Baksa Alert**: 의심스러운 결과 감지

- Sharpe: 7.2 (> 5.0 기준)
- 승률: 78% (> 70% 기준)

**자동 조치**:
1. Look-ahead bias 검사 실행
2. Signal shift (+1 bar) 테스트
3. Label randomization 테스트

결과 대기 중...
```

---

## 📊 Quick Reference: Baksa Checklist

**백테스트 전:**
- [ ] 가설 명확히 정의 (1가설 = 1실험)
- [ ] Baseline 설정 (비교 대상)
- [ ] Config 저장 (재현성)

**백테스트 중:**
- [ ] Position/Trade 로깅
- [ ] 모든 거래 기록

**백테스트 후 (Baksa 자동 실행):**
- [ ] [STAT:ci] 신뢰구간 계산
- [ ] [STAT:effect_size] 효과 크기 계산
- [ ] [STAT:sample_size] 샘플 크기 확인
- [ ] 4 Challenges 실행
- [ ] Trust Score 계산
- [ ] Dual Gate 평가
- [ ] Baksa Report 생성

**결과 보고:**
- [ ] Trust Score 명시
- [ ] 통계 마커 포함
- [ ] Decision + Rationale
- [ ] Next Action

---

**Last Updated**: 2025-01-11
**Version**: 1.0 (Baksa System - Ported from My-Jogyo)
**Origin**: My-Jogyo (Yeachan-Heo) - Adapted for Quant Research
