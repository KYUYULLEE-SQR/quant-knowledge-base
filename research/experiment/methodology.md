# Experiment Methodology (실험 방법론)

**Last Updated**: 2025-12-22
**Source**: User rules (CLAUDE.md), scientific best practices
**Importance**: ⭐⭐⭐ Critical - 잘못된 실험 = 쓸모없는 결과

---

## 🎯 Core Principle: One Variable at a Time

**CRITICAL RULE**: 한 실험당 **하나의 효과만** 측정 가능하도록 설계

**Why**:
- 여러 변수 동시 변경 → 무엇이 성과를 바꿨는지 알 수 없음
- "IV 필터 + TTE 필터 + 레짐 필터 동시 변경" → 어느 것이 유효했나?
- 재현성 불가능, 학습 불가능

---

## 📋 Experiment Phases (MANDATORY Sequence)

### Phase 1: Individual Effects (개별 효과)

**목표**: 각 변수를 **하나씩** 독립적으로 테스트

**순서**:
1. Baseline 설정 (변경 전 상태)
2. 변수 A만 변경 → 효과 측정
3. 변수 B만 변경 (Baseline에서) → 효과 측정
4. 변수 C만 변경 (Baseline에서) → 효과 측정

**Example**:
```
Baseline:
  IV filter: 10%
  TTE filter: 3 days
  Regime: Bull only

Experiment A (IV filter):
  IV filter: 15%  ← ONLY THIS CHANGED
  TTE filter: 3 days
  Regime: Bull only
  Result: Sharpe +0.3 ✅

Experiment B (TTE filter):
  IV filter: 10%  ← BACK TO BASELINE
  TTE filter: 5 days  ← ONLY THIS CHANGED
  Regime: Bull only
  Result: Sharpe +0.1 ✅

Experiment C (Regime):
  IV filter: 10%
  TTE filter: 3 days
  Regime: Bull + Sideways  ← ONLY THIS CHANGED
  Result: Sharpe -0.2 ❌
```

**Outcome of Phase 1**:
- Know which variables work (A ✅, B ✅, C ❌)
- Know magnitude of each effect (A: +0.3, B: +0.1)
- Can make informed decisions (keep A and B, discard C)

### Phase 2: Joint Effects (결합 효과)

**Conditions**:
- ✅ **ONLY after Phase 1 is complete**
- ✅ Only combine variables that individually showed positive effects
- ✅ Test for interaction effects (synergy or interference)

**Example (continuing from Phase 1)**:
```
Experiment D (A + B combined):
  IV filter: 15%  ← From Exp A
  TTE filter: 5 days  ← From Exp B
  Regime: Bull only
  Result: Sharpe +0.5

Analysis:
  Expected (if independent): +0.3 + 0.1 = +0.4
  Actual: +0.5
  Interaction effect: +0.1 (synergy! 🎉)
```

**If interaction is negative**:
```
Experiment D' (hypothetical):
  IV filter: 15%
  TTE filter: 5 days
  Result: Sharpe +0.2

Analysis:
  Expected: +0.4
  Actual: +0.2
  Interaction: -0.2 (interference! Variables conflict)
  Decision: Don't combine, use only the better one (A)
```

---

## 🚫 Common Mistakes (Agent가 자주 하는 실수)

### Mistake 1: 여러 변수 동시 변경

❌ **Bad**:
```
User: "IV 필터랑 TTE 필터 효과 테스트해봐"

Agent: "좋습니다. 둘 다 바꿔서 실험하겠습니다."

Experiment:
  IV filter: 10% → 15%  ← Changed
  TTE filter: 3d → 5d   ← Changed
  Result: Sharpe +0.2

Agent: "성과가 개선되었습니다!"

User: "뭐 때문에? IV? TTE?"
Agent: "모르겠습니다..." ❌
```

✅ **Good**:
```
User: "IV 필터랑 TTE 필터 효과 테스트해봐"

Agent: "Phase 1 (개별 효과) 먼저 진행하겠습니다.

  실험 A: IV 필터만 변경 (10% → 15%)
  실험 B: TTE 필터만 변경 (3d → 5d, IV=10% 유지)

  Phase 1 완료 후, 유효한 변수들을 결합 테스트 (Phase 2)."

Results:
  Exp A: Sharpe +0.3 ✅
  Exp B: Sharpe +0.1 ✅

Agent: "Phase 1 완료. 둘 다 유효.
       Phase 2 진행할까요? (A+B 결합 효과 측정)"
```

### Mistake 2: Baseline 불명확

❌ **Bad**:
```
Experiment 1:
  IV filter: 15%
  TTE filter: 5d
  Sharpe: 2.4

Experiment 2 (다음날):
  IV filter: 20%
  TTE filter: 3d  ← Wait, this changed too?
  Sharpe: 2.1

Agent: "20% IV가 더 나쁩니다."
User: "TTE도 바뀌었는데? 뭐가 원인이야?" ❌
```

✅ **Good**:
```
Baseline (명시):
  IV filter: 15%
  TTE filter: 5d
  Sharpe: 2.4

Experiment (IV만 변경):
  IV filter: 20%  ← ONLY THIS
  TTE filter: 5d  ← SAME AS BASELINE
  Sharpe: 2.1

Agent: "IV 20%로 증가 시 Sharpe -0.3 (2.4 → 2.1).
       IV 15%가 최적. ✅"
```

### Mistake 3: Phase 2 without Phase 1

❌ **Bad**:
```
User: "전략 개선해봐"

Agent: "여러 개선사항을 한번에 적용하겠습니다."

Changes:
  IV filter: 10% → 15%
  TTE filter: 3d → 5d
  Position size: 3% → 5%
  Rebalance: Daily → Hourly

Result: Sharpe 1.8 → 2.5 (huge improvement!)

User: "뭐가 먹혔어?"
Agent: "모르겠습니다. 여러 개 바꿨습니다." ❌
User: "다시 해." 😡
```

✅ **Good**:
```
User: "전략 개선해봐"

Agent: "4가지 개선 후보가 있습니다.
       Phase 1: 각각 개별 테스트

  Exp A: IV filter (10% → 15%) → Sharpe +0.2
  Exp B: TTE filter (3d → 5d) → Sharpe +0.1
  Exp C: Position size (3% → 5%) → Sharpe +0.3
  Exp D: Rebalance (Daily → Hourly) → Sharpe -0.1 ❌

  Phase 1 결과: A, B, C 유효. D 기각.

  Phase 2: 결합 효과 테스트
  Exp E: A + B + C → Sharpe +0.7 (expected +0.6, synergy!)

  최종 권장: A + B + C 모두 적용."
```

---

## 📊 Experiment Design Template

### Experiment Card (필수 작성)

```yaml
experiment_name: "IV_filter_optimization"
date: 2025-12-22
phase: 1  # Phase 1 (individual) or 2 (joint)

hypothesis:
  what: "IV filter를 15%로 증가시키면"
  why: "거짓 신호 감소 (10%는 너무 낮음)"
  expected: "Sharpe +0.2~0.3, 거래 빈도 -20%"

isolated_variable:
  name: "IV_filter_threshold"
  baseline_value: 10%
  experiment_value: 15%

control_variables:  # 고정된 변수들 (MUST NOT CHANGE)
  TTE_filter: 3 days
  regime: Bull only
  position_size: 3% NAV
  rebalance: Daily
  cost_model: Realistic (7 bps)

baseline:
  sharpe: 1.85
  max_dd: -12.3%
  trades: 127
  period: 2024-Q4

success_criteria:
  sharpe_increase: ">= +0.2"
  trade_count_decrease: "<= -30%"

failure_criteria:
  sharpe_increase: "< +0.1"
  max_dd_increase: "> +5%"
```

### Experiment Execution Checklist

**Before running**:
- [ ] Experiment card written (hypothesis, isolated variable, controls)
- [ ] Baseline results recorded (Sharpe, MDD, trades)
- [ ] Only ONE variable changed (verified)
- [ ] Success/failure criteria defined

**During run**:
- [ ] Baseline run first (to confirm reproducibility)
- [ ] Experiment run with ONLY specified variable changed
- [ ] All other parameters match baseline exactly

**After run**:
- [ ] Results compared to baseline (Sharpe, MDD, trades)
- [ ] Success criteria evaluated
- [ ] Isolated effect calculated (Δ Sharpe = ?)
- [ ] Decision: Accept / Reject / Retest

---

## 🔬 Grid Search (Phase 1 Alternative)

**Grid search** = Test all combinations of parameter values

**Allowed as Phase 1 replacement IF**:
1. ✅ Each dimension (variable) is analyzed independently
2. ✅ Marginal effects reported (effect of each variable holding others constant)
3. ✅ Interaction effects identified and reported

**Example**:
```python
# Grid search: IV filter × TTE filter
IV_values = [10, 15, 20]
TTE_values = [3, 5, 7]

results = []
for iv in IV_values:
    for tte in TTE_values:
        sharpe = backtest(iv_filter=iv, tte_filter=tte)
        results.append({'iv': iv, 'tte': tte, 'sharpe': sharpe})

# Analysis (mandatory):
# 1. Marginal effect of IV (averaging over TTE)
for iv in IV_values:
    avg_sharpe = mean([r['sharpe'] for r in results if r['iv'] == iv])
    print(f"IV {iv}%: avg Sharpe {avg_sharpe}")

# 2. Marginal effect of TTE (averaging over IV)
for tte in TTE_values:
    avg_sharpe = mean([r['sharpe'] for r in results if r['tte'] == tte])
    print(f"TTE {tte}d: avg Sharpe {avg_sharpe}")

# 3. Interaction heatmap
#     TTE=3  TTE=5  TTE=7
# IV=10  1.8    1.9    1.7
# IV=15  2.1    2.4    2.0  ← Best: IV=15, TTE=5
# IV=20  1.9    2.0    1.8
```

**If grid search done** → Phase 1 considered complete, can proceed to Phase 2 (if needed)

---

## 🧪 Validation Tests (Every Experiment)

**MANDATORY checks** (automated):

1. ✅ **Baseline reproducibility**:
   - Re-run baseline → should get same Sharpe (±0.05)
   - If not → code bug or data issue

2. ✅ **Integrity checks** (from backtesting integrity rules):
   - Trade-by-trade reconciliation
   - Position continuity
   - PnL attribution

3. ✅ **Placebo test** (look-ahead bias check):
   - Shift signal +1 bar → alpha should disappear
   - If alpha remains → look-ahead bias ❌

4. ✅ **Cost sensitivity**:
   - Run at 0.5×, 1×, 2× transaction costs
   - If Sharpe < 0 at 2× → too cost-sensitive ❌

5. ✅ **Parameter stability**:
   - Test nearby parameter values (±10%, ±20%)
   - If Sharpe changes >50% → overfitting ❌

---

## 🚨 Red Flags (Stop Immediately)

1. ❌ **Multiple variables changed without Phase 1**
   - Agent must refuse and explain Phase 1 requirement

2. ❌ **Baseline not defined**
   - Agent must ask user to specify baseline

3. ❌ **"Let's try everything and see what works"**
   - This is data snooping, overfitting guaranteed
   - Agent must explain: one variable at a time

4. ❌ **Results don't match success criteria but agent says "looks good"**
   - Agent must objectively evaluate against pre-defined criteria

5. ❌ **No validation tests run**
   - Integrity, placebo, cost sensitivity are MANDATORY

---

## 📝 Agent Protocol: Experiment Execution

**When user requests experiment:**

1. ✅ **Parse request**: Identify variable(s) user wants to test
2. ✅ **Check phase**: Is this Phase 1 (individual) or Phase 2 (joint)?
3. ✅ **Enforce sequence**: If Phase 2 requested but Phase 1 not done → Refuse
4. ✅ **Design experiment**:
   - Write experiment card
   - Identify isolated variable
   - Define control variables (fixed)
   - State baseline
5. ✅ **Execute**:
   - Run baseline (confirm reproducibility)
   - Run experiment (ONLY isolated variable changed)
   - Run validation tests
6. ✅ **Report**:
   - Isolated effect (Δ Sharpe)
   - Success criteria met? (yes/no)
   - Decision: Accept / Reject / Retest
   - Next steps (if Phase 1 → suggest Phase 2)

**Example dialogue**:
```
User: "IV 필터랑 TTE 필터 둘 다 바꿔서 테스트해봐"

Agent:
  "요청하신 것: IV + TTE 동시 변경
   문제: 두 변수를 동시에 바꾸면 어느 것이 효과적인지 알 수 없습니다.

   권장 방법 (Phase 1 → Phase 2):

   **Phase 1 (개별 효과)**:
   1. Exp A: IV만 변경 (10% → 15%), TTE 고정
   2. Exp B: TTE만 변경 (3d → 5d), IV 고정

   **Phase 2 (결합 효과)**:
   3. Exp C: A + B 결합 (둘 다 변경)
   4. 상호작용 분석 (synergy or interference)

   진행할까요? (Phase 1부터 시작)"
```

---

## 📚 References

- **User Rules**: `~/knowledge/agent_prompts/claude_code/rules/05_experiment_guidelines.md` (detailed rules)
- **Related KB**:
  - [Transaction Cost Model](../../trading/cost-models/transaction_cost.md) - Cost sensitivity testing
  - [Lessons Learned](lessons_learned.md) - Past experiment failures
- **Scientific Method**: Control variables, isolate effects, reproducibility

---

**Version**: 1.0
**Critical**: This is THE MOST IMPORTANT rule. Wrong experiments = wasted time.
