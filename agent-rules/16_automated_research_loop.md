# 🔄 Automated Research Loop (자동화된 연구 파이프라인)

**Priority**: ⭐⭐⭐⭐⭐ CRITICAL
**Last Updated**: 2025-12-30

---

## 🎯 Purpose

**사용자가 "백테스트", "테스트", "전략" 요청 시 자동으로:**

1. 정합성 있는 백테스트 실행 (꼼수 금지)
2. 새로운 방법 탐색 (3-5 변형)
3. Quant 함정 검증 (Signal Shift, Placebo, OOS)
4. 결과 문서화 (성공 시)

**사용자가 매번 지시할 필요 없이 자동 완성!**

---

## 🚀 자동 실행 조건

### Trigger Keywords (이 단어 보이면 자동 실행)

| 키워드 | 자동 실행 파이프라인 |
|--------|---------------------|
| "백테스트", "backtest" | Full Research Loop |
| "전략 테스트", "strategy test" | Full Research Loop |
| "실험", "experiment" | Full Research Loop |
| "최적화", "optimize" | Grid Search + Validation |
| "검증", "validate" | Validation Only (Signal Shift, Placebo, OOS) |

---

## 📋 Full Research Loop Pipeline

### 자동 실행 순서

```
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 1: Integrity Backtest (정합성 백테스트)                   │
│  ├─ Look-ahead bias 자동 탐지                                   │
│  ├─ Signal delay 적용 (시그널 → 1봉 후 진입)                     │
│  ├─ Trade-by-trade reconciliation                               │
│  └─ Timeframe-consistent 차트 생성                              │
├─────────────────────────────────────────────────────────────────┤
│  PHASE 2: Grid Search (파라미터 탐색)                            │
│  ├─ 3-5개 파라미터 조합 자동 테스트                              │
│  ├─ 각 조합 정합성 검증                                          │
│  └─ Best candidate 선택 (Sharpe 기준)                            │
├─────────────────────────────────────────────────────────────────┤
│  PHASE 3: Quant Pitfall Validation (함정 검증)                   │
│  ├─ Signal Shift Test: 시그널 1봉 밀었을 때 alpha 사라지는지      │
│  ├─ Placebo Test: 랜덤 시그널에서 alpha 없는지                    │
│  ├─ OOS Test: Out-of-sample에서 성과 유지되는지                   │
│  └─ Param Stability: 인접 파라미터에서도 성과 유지되는지          │
├─────────────────────────────────────────────────────────────────┤
│  PHASE 4: Documentation (문서화)                                 │
│  ├─ 결과 요약 테이블                                             │
│  ├─ 검증 결과                                                   │
│  ├─ Decision: ✅ Deploy / 🟡 Shelve / 🔴 Discard                │
│  └─ 파일 저장 (experiments/YYYY-MM-DD_*/...)                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 💻 사용 방법

### 1. Framework Import

```python
from lib.backtest import IntegrityBacktest, run_research_loop, BacktestConfig
```

### 2. Strategy 정의

```python
class MyStrategy(IntegrityBacktest):
    def __init__(self, df, timeframe, fast=10, slow=30, **kwargs):
        super().__init__(df, timeframe, **kwargs)
        self.fast = fast
        self.slow = slow

    def generate_signals(self, df):
        """
        시그널 생성.

        CRITICAL: 현재 봉 데이터가 아닌 과거 데이터로만 시그널 생성!
        """
        fast_ma = df['close'].rolling(self.fast).mean()
        slow_ma = df['close'].rolling(self.slow).mean()

        signal = pd.Series(0, index=df.index)
        signal[fast_ma > slow_ma] = 1
        signal[fast_ma < slow_ma] = -1

        return signal
```

### 3. Full Pipeline 실행

```python
# 전체 파이프라인 자동 실행
results = run_research_loop(
    MyStrategy,
    df,
    timeframe='15m',
    param_grid={
        'fast': [5, 10, 20],
        'slow': [20, 30, 50]
    }
)

# 결과 확인
print(f"Decision: {results['decision']}")
print(f"Best Params: {results['best_candidate']['params']}")
```

### 4. 단일 백테스트 실행

```python
bt = MyStrategy(df, '15m', fast=10, slow=30)
results = bt.run()  # 자동으로 정합성 검증

# 결과 저장
bt.save_results()
```

---

## 🔍 Validation Details

### 1. Signal Shift Test

**목적**: 시그널을 1봉 미래로 밀었을 때 alpha가 사라지는지 확인

```
원본: 시그널 → 다음 봉 진입
Shift: 시그널 → 2봉 후 진입

✅ PASS: Sharpe가 30%+ 감소
❌ FAIL: Sharpe 유지 = 미래참조 의심
```

### 2. Placebo Test

**목적**: 랜덤 시그널에서 alpha가 없는지 확인

```
원본: 전략 시그널
Placebo: 랜덤 시그널 (-1, 0, 1)

✅ PASS: 랜덤 Sharpe ≈ 0
❌ FAIL: 랜덤에서도 높은 Sharpe = 데이터 누수
```

### 3. Out-of-Sample Test

**목적**: 마지막 30% 데이터에서 성과 유지되는지 확인

```
IS: 전체 데이터 70%
OOS: 전체 데이터 30%

✅ PASS: OOS Sharpe > IS Sharpe * 50%
❌ FAIL: OOS 성과 급감 = 과적합
```

### 4. Parameter Stability Test

**목적**: 인접 파라미터에서도 성과 유지되는지 확인

```
Best: fast=10, slow=30 (Sharpe 2.0)
Adjacent: fast=5,15, slow=20,50

✅ PASS: 인접 평균 Sharpe > Best * 50%
❌ FAIL: 특정 파라미터에서만 좋음 = 과적합
```

---

## 📁 Output Structure

```
~/experiments/YYYY-MM-DD_HH-MM_research_loop/
├── grid_001/                    # 첫 번째 파라미터 조합
│   └── results/
│       ├── metrics.json
│       ├── trades.csv
│       └── summary.md
├── grid_002/                    # 두 번째 조합
├── ...
├── validation_signal_shift/     # Signal shift 검증
├── validation_oos/              # OOS 검증
└── final_report/
    ├── report.json              # 구조화된 데이터
    └── REPORT.md                # 최종 보고서
```

---

## 🤖 Agent Rules

### MANDATORY Behaviors (필수)

1. **백테스트 요청 시 자동으로 Research Loop 실행**
   - 사용자가 "백테스트해봐", "전략 테스트해봐" 하면
   - `run_research_loop()` 자동 실행
   - 최소 3개 파라미터 조합 테스트
   - 4가지 검증 자동 실행

2. **정합성 실패 시 중단**
   - Look-ahead bias 감지 → 코드 수정 → 재실행
   - 승률 > 70% 또는 Sharpe > 5 → 경고 출력

3. **문서화 자동 생성**
   - 결과 테이블 + 검증 결과 + Decision
   - 파일 저장 경로 명시

4. **사용자에게 물어보지 않음**
   - ❌ "추가 검증 할까요?"
   - ✅ 자동으로 모든 검증 실행 후 종합 보고

### Decision Criteria (결정 기준)

| 조건 | Decision |
|------|----------|
| 모든 검증 통과 | ✅ DEPLOY |
| 일부 검증 실패 | 🟡 SHELVE (추가 조사 필요) |
| 정합성 실패 or 치명적 함정 | 🔴 DISCARD |

---

## 📊 Output Format (MANDATORY)

모든 연구 결과는 다음 형식으로 보고:

```markdown
## 🎯 Research Loop Results

**Experiment**: YYYY-MM-DD_HH-MM_strategy_name
**Decision**: ✅ DEPLOY / 🟡 SHELVE / 🔴 DISCARD

### Grid Search (N combinations)

| Params | Sharpe | Return | MDD | Integrity |
|--------|--------|--------|-----|-----------|
| {fast=10, slow=30} | 2.1 | +15% | -8% | ✅ |
| {fast=20, slow=50} | 1.8 | +12% | -6% | ✅ |
| ... | ... | ... | ... | ... |

### Best Candidate

| Metric | Value |
|--------|-------|
| Parameters | {fast=10, slow=30} |
| Sharpe | 2.1 |
| Return | +15% |
| MDD | -8% |
| Win Rate | 58% |
| Trades | 127 |

### Validations

- ✅ Signal Shift: Sharpe 2.1 → 0.5 (-76%)
- ✅ Placebo: Random Sharpe 0.1 avg
- ✅ OOS: Sharpe 1.8 (86% retained)
- ✅ Param Stability: Adjacent avg 1.7 (81%)

### Files

- `~/experiments/.../final_report/REPORT.md`
- `~/experiments/.../final_report/report.json`

### Next Action

[다음 실험 제안]
```

---

## 🚫 Anti-Patterns (절대 금지)

```python
# ❌ WRONG: 수동으로 개별 백테스트
bt = MyStrategy(df, '15m')
results = bt.run()
print(f"Sharpe: {results['sharpe_ratio']}")
# 검증 없이 끝

# ✅ CORRECT: Research Loop 사용
results = run_research_loop(
    MyStrategy, df, '15m',
    param_grid={'fast': [5, 10, 20], 'slow': [20, 30, 50]}
)
# 자동으로 3x3=9개 조합 + 4개 검증 + 문서화
```

```
# ❌ WRONG: 사용자에게 물어봄
"Signal shift 테스트 할까요?"
"OOS 검증도 진행할까요?"

# ✅ CORRECT: 자동 실행
[모든 검증 자동 실행 후]
"✅ 4/4 검증 통과. Decision: DEPLOY"
```

---

## 🔗 Related Files

- `~/lib/backtest/integrity_backtest.py` - 정합성 백테스트 프레임워크
- `~/lib/backtest/research_loop.py` - 연구 루프 자동화
- `~/knowledge/agent-rules/15_quant_pitfalls.md` - Quant 함정 방지

---

**Last Updated**: 2025-12-30
**Version**: 1.0
