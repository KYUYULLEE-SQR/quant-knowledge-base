# Test: Session Consistency (세션 일관성 테스트)

**Purpose**: 긴 세션에서도 Agent 품질이 유지되는지 검증
**Priority**: ⭐⭐⭐ CRITICAL
**Last Updated**: 2025-12-26

---

## 🎯 테스트 목표

Agent가 다음을 유지하는지 확인:
1. 100k tokens 후에도 동일한 능동성
2. 세션 초반과 동일한 상세함
3. Context 추적 (이전 결정 기억)
4. "멍청해지기" 방지

---

## 📝 Test Case 1: 긴 세션 후 실험 요청

### Context
```
[세션 50k+ tokens 진행 후]
[이전에 IV=15% 실험 완료, TTE 테스트 예정이었음]
```

### Input
```
다음 실험 해줘
```

### Expected (PASS)
```
## 📋 Next Experiment: TTE Filter

이전 실험 (IV=15%) 결과 기반으로 TTE 필터 테스트 진행합니다.

**Context from previous**:
- IV=15%: Sharpe 2.12 (✅ Adopted)
- 다음 예정: TTE 3d → 5d

### Experiment Card
**Hypothesis**: TTE 5d로 늘리면 gamma explosion 회피
**Isolated Variable**: TTE (3d → 5d)
**Fixed**: IV=15% (이전 실험 결과 적용)

[전체 실험 결과...]

### Next Action
1. Phase 2: IV=15% + TTE=5d 결합
```

### Anti-Patterns (FAIL)
```
❌ "어떤 실험을 할까요?"
❌ [이전 context 무시]
❌ [짧은 응답]
❌ [IV=15% 결과 잊어버림]
```

---

## 📝 Test Case 2: 세션 후반 상세함 유지

### Context
```
[세션 80k+ tokens]
```

### Input
```
백테스트 결과 보여줘
```

### Expected (PASS)
```
[세션 초반과 동일한 상세함]

## 📊 Backtest Results

**Period**: 2024-10-01 ~ 2024-12-25

| Metric | Value | Baseline | Delta |
|--------|-------|----------|-------|
| Total Return | +45% | +12% | +33% |
| Sharpe Ratio | 2.4 | 0.8 | +1.6 |
[... 10+ metrics ...]

### Sub-Period Analysis
[... 테이블 ...]

### Validation
[... 체크리스트 ...]

### Files
[... 경로 ...]

### Next Action
[... 제안 ...]
```

### Anti-Patterns (FAIL)
```
❌ "Sharpe 2.4, MDD -8.5%입니다" [짧은 응답]
❌ [테이블 생략]
❌ [Sub-period 생략]
❌ [Next Action 생략]
❌ [세션 초반보다 간략함]
```

---

## 📝 Test Case 3: Context 추적

### Context
```
[세션 중반]
User: "수수료 VIP9로 가정해줘"
[...50 messages later...]
```

### Input
```
비용 얼마나 나와?
```

### Expected (PASS)
```
## 💰 Transaction Costs

**Fee Tier**: VIP9 (DMM) - 세션 초반에 설정됨

| Cost Type | Rate | Total |
|-----------|------|-------|
| Maker Fee | -0.01% (rebate) | -$127 |
| Taker Fee | +0.03% | $0 (maker only) |
| Slippage | ~0.05% | $635 |
| **Net Cost** | - | **$508** |

Note: VIP9 maker rebate 적용됨 (세션 초반 설정 유지)
```

### Anti-Patterns (FAIL)
```
❌ "어떤 수수료 티어를 사용할까요?"
❌ [VIP9 설정 잊어버림]
❌ [기본 티어로 계산]
```

---

## 📝 Test Case 4: 이전 결정 기억

### Context
```
[세션 초반]
User: "Bear market은 나중에 테스트하자"
[...30 messages later...]
```

### Input
```
다음 뭐해?
```

### Expected (PASS)
```
## 📋 Next Steps

현재까지 완료:
1. ✅ IV filter 15% (Sharpe +0.27)
2. ✅ TTE filter 5d (Sharpe +0.10)
3. ✅ Phase 2 결합 (Sharpe 2.25)

남은 작업:
1. **Position sizing** - Kelly 기반 최적화
2. ~~Bear market (2022-Q2)~~ - 사용자 요청으로 보류

Position sizing 테스트 진행할까요?
```

### Anti-Patterns (FAIL)
```
❌ "Bear market 테스트 해볼까요?" [보류 요청 잊음]
❌ [완료된 작업 다시 제안]
❌ [세션 context 무시]
```

---

## 📝 Test Case 5: 에러 후 복구

### Context
```
[세션 중 에러 발생 후]
```

### Input
```
계속해
```

### Expected (PASS)
```
## 🔄 Resuming from Error

에러 수정 완료. 중단된 지점부터 재개합니다.

**이전 상태**:
- Step 1: ✅ 데이터 로드 (완료)
- Step 2: ❌ 백테스트 (에러 발생)
- Step 3: ⏳ 결과 분석 (대기)

**에러 수정**:
```python
# 문제: NaN 처리 누락
# 수정: df = df.dropna()
```

## 🔄 Step 2 재실행 중...

[결과...]

## ➡️ Step 3 진행 중...
```

### Anti-Patterns (FAIL)
```
❌ "어디서부터 계속할까요?"
❌ [처음부터 다시 시작]
❌ [에러 상태 모름]
```

---

## 📝 Test Case 6: 피로도 테스트

### Context
```
[세션 100k+ tokens]
[동일한 유형의 작업 10회 이상 반복]
```

### Input
```
하나 더 테스트해봐
```

### Expected (PASS)
```
[첫 번째 테스트와 동일한 품질]

## 📋 Experiment #11

[전체 Experiment Card]
[전체 결과 테이블]
[Baseline + Falsification]
[Reconciliation]
[Files]
[Next Action]
```

### Anti-Patterns (FAIL)
```
❌ [점점 짧아지는 응답]
❌ [테이블 생략 시작]
❌ [Falsification 생략]
❌ "이전과 비슷한 결과입니다"
```

---

## 📊 Self-Check (Agent 내부 체크)

**매 응답 전 확인:**

```
□ 세션 초반과 동일한 상세함인가?
□ 이전 결정/설정을 기억하고 있는가?
□ 사용자가 보류 요청한 것 기억하는가?
□ 완료된 작업 목록 정확한가?
□ 능동성이 유지되고 있는가?
□ "멍청해지기" 시작하지 않았는가?
```

---

## 📊 일관성 지표

| 지표 | 세션 초반 | 세션 후반 | 목표 |
|------|----------|----------|------|
| 응답 길이 | 100줄 | 100줄 | 동일 |
| 테이블 개수 | 3개 | 3개 | 동일 |
| Next Action | 있음 | 있음 | 항상 |
| Context 참조 | N/A | 있음 | 필수 |
| 능동성 | 높음 | 높음 | 유지 |

---

## 🔧 FAIL 시 수정

| 증상 | 원인 | 수정 |
|------|------|------|
| 응답 짧아짐 | Context 압박 | 핵심 규칙 상단 배치 |
| Context 잊음 | 참조 부재 | STATE.md 활용 강조 |
| 능동성 저하 | 규칙 희석 | Self-check 루프 강화 |
| 반복 질문 | 설정 망각 | 세션 설정 명시적 저장 |

---

**Version**: 1.0
