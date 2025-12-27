# Test: Proactivity (능동성 테스트)

**Purpose**: Agent가 능동적으로 행동하는지 검증
**Priority**: ⭐⭐⭐ CRITICAL
**Last Updated**: 2025-12-26

---

## 🎯 테스트 목표

Agent가 다음을 하는지 확인:
1. 묻지 않고 즉시 실행
2. 1-2개가 아닌 3-5개 변형 자동 실행
3. Baseline + Falsification 자동 포함
4. Next Action 항상 제안

---

## 📝 Test Case 1: 실험 요청

### Input
```
이 전략 테스트해봐
```

### Expected (PASS)
```
[즉시 실행 시작]

## 📊 Experiment Results

| Variant | Sharpe | MDD | Trades | Parameter |
|---------|--------|-----|--------|-----------|
| Main (default) | 2.1 | -8% | 127 | threshold=0.15 |
| Conservative | 1.8 | -5% | 89 | threshold=0.20 |
| Aggressive | 2.4 | -12% | 201 | threshold=0.10 |
| Edge (min) | 1.2 | -15% | 312 | threshold=0.05 |
| Edge (max) | 0.9 | -3% | 23 | threshold=0.30 |

### Baseline Comparison
| Baseline | Sharpe | Note |
|----------|--------|------|
| Buy & Hold | 0.8 | - |
| Random Signal | 0.1 | - |

### Falsification Tests
- ✅ Signal shift (+1 bar): Alpha disappears
- ✅ Cost 2x: Sharpe 1.5 (still viable)

### Files
- ~/experiments/2025-12-26_XX-XX_test/results/metrics.json

### Next Action
1. Bear market (2022-Q2) 검증
2. Position sizing 최적화
```

### Anti-Patterns (FAIL)
```
❌ "테스트를 실행할까요?"
❌ "어떤 파라미터로 테스트할까요?"
❌ "실행하기 전에 확인해 주세요"
❌ [1개만 실행하고 멈춤]
❌ [Baseline 없음]
❌ [Next Action 없음]
```

---

## 📝 Test Case 2: 분석 요청

### Input
```
이 데이터 분석해줘
```

### Expected (PASS)
```
[즉시 분석 시작]

## 📊 Analysis Results

### Summary Statistics
| Metric | Value |
|--------|-------|
| Rows | 125,000 |
| Period | 2024-01-01 ~ 2024-12-25 |
| Missing | 0.3% |
...

### Key Findings
1. [발견 1 + 수치]
2. [발견 2 + 수치]
3. [발견 3 + 수치]

### Visualizations
- [차트 설명 또는 생성]

### Next Action
1. [추가 분석 제안]
2. [가설 검증 제안]
```

### Anti-Patterns (FAIL)
```
❌ "어떤 분석을 원하시나요?"
❌ "데이터를 먼저 확인해 볼까요?"
❌ [요약만 하고 인사이트 없음]
❌ [Next Action 없음]
```

---

## 📝 Test Case 3: 모호한 요청

### Input
```
성과 개선해줘
```

### Expected (PASS)
```
[가정 명시 후 즉시 실행]

현재 전략의 성과 개선을 위해 다음을 테스트합니다:
- 가정: 최근 실험 (~/experiments/latest) 기준
- 목표: Sharpe 향상, MDD 감소

## 📊 Optimization Results

### Tested Improvements
| Change | Sharpe Before | After | Delta |
|--------|--------------|-------|-------|
| IV filter 10%→15% | 1.8 | 2.1 | +0.3 |
| TTE filter 3d→5d | 1.8 | 1.9 | +0.1 |
| Position size 3%→2% | 1.8 | 1.7 | -0.1 |

### Best Combination
IV filter 15% + TTE 5d = Sharpe 2.2

### Next Action
1. Phase 2: 결합 효과 검증
2. Bear market 테스트
```

### Anti-Patterns (FAIL)
```
❌ "어떤 성과를 개선할까요?"
❌ "현재 성과가 어떻게 되나요?"
❌ "구체적으로 말씀해 주세요"
❌ [아무것도 실행 안 함]
```

---

## 📝 Test Case 4: 오류 발생 시

### Input
```
[코드 실행 중 에러 발생]
```

### Expected (PASS)
```
## ❌ Error Occurred

```
[실제 에러 메시지]
```

## 🔧 Fix Applied

[즉시 수정한 코드]

## ✅ Re-execution Result

[수정 후 성공 결과]

### Next Action
1. [에러 방지 위한 추가 조치]
```

### Anti-Patterns (FAIL)
```
❌ "에러가 발생했습니다. 어떻게 할까요?"
❌ "이 에러를 수정해 주세요"
❌ [에러만 보고하고 수정 안 함]
❌ [사용자에게 수정 요청]
```

---

## 📝 Test Case 5: 긴 작업 중간

### Input
```
[3단계 작업 중 1단계 완료 후]
```

### Expected (PASS)
```
## ✅ Step 1 Complete

[결과 요약]

## 🔄 Proceeding to Step 2...

[즉시 2단계 시작]
```

### Anti-Patterns (FAIL)
```
❌ "1단계 완료했습니다. 2단계 진행할까요?"
❌ "다음 단계를 시작해도 될까요?"
❌ [멈추고 대기]
```

---

## 📝 Test Case 6: 여러 옵션 존재 시

### Input
```
캐싱 구현해줘
```

### Expected (PASS)
```
캐싱 구현합니다. Redis 대신 파일 기반 캐시 선택 (의존성 최소화).

## 💻 Implementation

```python
# [전체 구현 코드]
class FileCache:
    ...
```

## ✅ Test Result

```
Cache hit: 95%
Latency: 2ms → 0.1ms
```

### 선택 이유
- Redis: 별도 서버 필요 (복잡)
- File: 의존성 없음, 충분한 성능

### Next Action
1. TTL 설정 추가
2. 캐시 무효화 로직
```

### Anti-Patterns (FAIL)
```
❌ "Redis와 파일 캐시 중 어떤 것을 원하시나요?"
❌ "여러 옵션이 있습니다: 1) Redis 2) Memcached 3) File"
❌ [선택지만 나열하고 대기]
```

---

## 📊 Pass Rate 목표

| 테스트 | 목표 |
|--------|------|
| Test 1-6 모두 | 100% PASS |
| Anti-pattern 발생 | 0% |

---

## 🔧 FAIL 시 수정 위치

| 실패 유형 | 수정 파일 |
|----------|----------|
| "~할까요?" 발생 | `CLAUDE.md` Anti-patterns 강화 |
| 1개만 실행 | `00_output_enforcement.md` 자동 확장 규칙 |
| Next Action 누락 | `CLAUDE.md` Completeness condition |
| 에러 후 멈춤 | `06_behavioral_rules.md` Failure handling |

---

**Version**: 1.0
