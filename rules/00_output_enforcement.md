# APPLY_ALWAYS
# LOAD ORDER: 0 (FIRST - before all other rules)
# This file OVERRIDES default short-response behavior
# Every output MUST pass self-verification before delivery

---

# 🚨 OUTPUT ENFORCEMENT PROTOCOL (강제 출력 규칙)

## 🎯 Core Problem This Solves

**Claude Code가 대충 답변하는 문제**:
- ❌ "수익률 15%" (MDD, Sharpe, Win Rate 누락)
- ❌ "실험 완료" (결과 테이블 없음)
- ❌ 짧은 답변 후 추가 질문 대기

**해결**: 키워드 감지 → 자동 확장 → Self-verification

---

## 🔥 HARD TRIGGER RULES (강제 발동)

### Trigger 1: 실험/백테스트 결과

**키워드 감지**: 실험, 백테스트, 수익률, 성과, 결과, PnL, return, performance, backtest

**자동 출력 (MANDATORY)**:

```markdown
## 📊 Performance Summary

| Metric | Value | Note |
|--------|-------|------|
| Total Return | X% | 기간: YYYY-MM-DD ~ YYYY-MM-DD |
| Sharpe Ratio | X.XX | Annualized (365d) |
| Max Drawdown | -X.X% | Date: YYYY-MM-DD |
| Win Rate | X.X% | N wins / M total |
| Profit Factor | X.XX | Gross profit / Gross loss |
| Total Trades | N | Avg holding: X days |
| Avg Trade | $X (X%) | Per trade |
| Best Trade | $X (X%) | |
| Worst Trade | -$X (-X%) | |

## 📈 Equity Curve Characteristics
- Initial: $X → Final: $X
- Peak: $X (Date) → Trough: $X (Date)
- Recovery time: X days

## ⚠️ Risk Analysis
- Longest DD duration: X days
- Worst month: YYYY-MM (-X%)
- Tail risk (worst 5%): -X% avg
```

**누락 시**: 응답 불완전 → 자동 확장 필수

---

### Trigger 2: 단일 메트릭 질문

**키워드 감지**: Sharpe가, MDD가, 수익률이, win rate가

**자동 확장**:
- 질문된 메트릭 + 관련 3개 메트릭 함께 출력
- 단독 숫자 답변 금지

**Example**:
```
User: "Sharpe가 얼마야?"

❌ Bad: "Sharpe 2.4입니다"

✅ Good:
| Metric | Value |
|--------|-------|
| Sharpe Ratio | 2.4 |
| Max Drawdown | -8.5% |
| Win Rate | 61% |
| Total Return | 45% |

Full results: ~/experiments/2025-12-25_*/results/metrics.json
```

---

### Trigger 3: 실험 종료/완료

**키워드 감지**: 완료, 끝, 종료, done, finished, 결과 보여줘

**자동 출력 (MANDATORY)**:

```markdown
## 🎯 Experiment Conclusion

**Decision**: ✅ Deploy / 🟡 Shelve / 🔴 Discard

### Key Findings
1. [Finding 1 with number]
2. [Finding 2 with number]
3. [Finding 3 with number]

### Performance Table
[Full metrics table - see Trigger 1]

### Validation Status
- [ ] Position reconciliation: ✅/❌
- [ ] No look-ahead bias: ✅/❌
- [ ] Cost sensitivity (2x): ✅/❌
- [ ] Sub-period consistency: ✅/❌

### Files Saved
- Config: ~/experiments/YYYY-MM-DD_HH-MM_name/config.yaml
- Results: ~/experiments/YYYY-MM-DD_HH-MM_name/results/
- Summary: ~/experiments/YYYY-MM-DD_HH-MM_name/results/summary.md

### Next Action
1. [Specific next experiment]
2. [Alternative if #1 fails]
```

---

## 🔄 SELF-VERIFICATION LOOP (자기 검증)

**EVERY response MUST pass this check before delivery:**

### Pre-Delivery Checklist

```
□ 1. 실험/백테스트 언급? → Full metrics table 있는가?
□ 2. 단일 메트릭 질문? → 관련 메트릭 3개+ 포함했는가?
□ 3. 실험 완료? → Conclusion + Files + Next Action 있는가?
□ 4. 코드 실행? → 실제 출력 포함했는가? (Expected 금지)
□ 5. 수치 언급? → 단위, 기간, 비교 대상 명시했는가?
```

**하나라도 No → 응답 확장 후 재전송**

### Self-Check Enforcement

응답 작성 완료 후, 다음 질문에 답하기:

1. **"수익률 얼마야?"에 대한 답변인가?**
   - Yes → Sharpe, MDD, Win Rate 포함되었는가?
   - No 있으면 → 추가

2. **백테스트 결과 보고인가?**
   - Yes → 10개 이상 메트릭 테이블 있는가?
   - No 있으면 → 추가

3. **실험 완료 보고인가?**
   - Yes → Decision + Next Action + Files 있는가?
   - No 있으면 → 추가

---

## 📏 MINIMUM OUTPUT STANDARDS

### Experiment Results (실험 결과)

**Minimum 10 metrics**:
1. Total Return
2. Sharpe Ratio
3. Max Drawdown
4. Win Rate
5. Profit Factor
6. Total Trades
7. Avg Trade Return
8. Best/Worst Trade
9. Longest DD Duration
10. Sub-period Breakdown (2+ periods)

**Missing any → response INCOMPLETE**

### Single Metric Question (단일 메트릭 질문)

**Minimum 4 metrics** (질문 + 관련 3개)

Example:
- "MDD 얼마?" → MDD + Sharpe + Return + Recovery time

### Code Execution (코드 실행)

**Must include**:
1. Actual code executed
2. Actual output (not "Expected:")
3. Files created (paths)
4. Errors (if any) + fix

---

## 🚫 ANTI-PATTERNS (절대 금지)

### ❌ 단독 숫자 답변

```
User: "Sharpe 얼마야?"
❌: "2.4입니다"
✅: [4+ metrics table]
```

### ❌ "Expected:" 출력

```
❌: "Expected output: Sharpe 2.4"
✅: [Actual executed output]
```

### ❌ 요약만 (테이블 없음)

```
❌: "성과 좋습니다. Sharpe 2.4, MDD -8%"
✅: [Full 10+ metrics table]
```

### ❌ 파일 경로 누락

```
❌: "결과 저장했습니다"
✅: "결과 저장: ~/experiments/2025-12-25_15-30_test/results/metrics.json"
```

### ❌ Next Action 누락

```
❌: "실험 완료"
✅: "실험 완료. Next: Bear market (2022-Q2) 검증"
```

---

## 🎯 OUTPUT TEMPLATES (Copy-Paste Ready)

### Template A: Full Experiment Report

```markdown
## 🎯 Executive Summary

**Experiment**: [Name]
**Period**: YYYY-MM-DD ~ YYYY-MM-DD
**Decision**: ✅ Deploy / 🟡 Shelve / 🔴 Discard

## 📊 Performance Summary

| Metric | Value | Baseline | Delta |
|--------|-------|----------|-------|
| Total Return | X% | Y% | +Z% |
| Sharpe Ratio | X.XX | Y.YY | +Z.ZZ |
| Max Drawdown | -X.X% | -Y.Y% | +Z.Z% |
| Win Rate | X.X% | Y.Y% | +Z.Z% |
| Profit Factor | X.XX | Y.YY | +Z.ZZ |
| Total Trades | N | M | +K |
| Avg Trade | X% | Y% | +Z% |
| Longest DD | X days | Y days | -Z days |

## 📈 Sub-Period Analysis

| Period | Return | Sharpe | MDD | Trades |
|--------|--------|--------|-----|--------|
| Q1 2024 | X% | X.XX | -X% | N |
| Q2 2024 | X% | X.XX | -X% | N |
| Q3 2024 | X% | X.XX | -X% | N |
| Q4 2024 | X% | X.XX | -X% | N |

## ✅ Validation

- [x] Position reconciliation passed
- [x] No look-ahead bias (signal shift test)
- [x] Cost sensitivity: Sharpe X.X @ 2x fees
- [x] Parameter stability: CV < 20%

## 📁 Files

- Config: `~/experiments/YYYY-MM-DD_HH-MM_name/config.yaml`
- Metrics: `~/experiments/YYYY-MM-DD_HH-MM_name/results/metrics.json`
- Trades: `~/experiments/YYYY-MM-DD_HH-MM_name/results/trades.csv`
- Summary: `~/experiments/YYYY-MM-DD_HH-MM_name/results/summary.md`

## 💡 Next Actions

1. **Priority 1**: [Specific next experiment]
2. **Priority 2**: [Alternative]
```

### Template B: Quick Metrics Response

```markdown
| Metric | Value |
|--------|-------|
| [Asked Metric] | X |
| Sharpe Ratio | X.XX |
| Max Drawdown | -X.X% |
| Win Rate | X.X% |

Full results: `~/experiments/[latest]/results/metrics.json`
```

### Template C: Code Execution Report

```markdown
## 💻 Execution

**Code**:
```python
[actual code]
```

**Output**:
```
[actual output - NOT "Expected:"]
```

**Files Created**:
- `path/to/file1.csv` (N rows)
- `path/to/file2.json`

**Status**: ✅ Success / ❌ Error (see below)
```

---

## 🔄 ENFORCEMENT MECHANISM

### How This Works

1. **Before writing response**: Check triggers (keywords)
2. **If triggered**: Use corresponding template
3. **Before sending**: Run self-verification checklist
4. **If incomplete**: Expand until complete

### Priority Order

```
1. 00_output_enforcement.md (THIS FILE) ← HIGHEST
2. 01_identity_and_context.md
3. 06_behavioral_rules.md
4. ... other rules
```

**This file ALWAYS takes precedence.**

---

## 📋 Quick Reference Card

**Remember these 5 rules:**

1. **실험 결과 = 10+ metrics table** (no exceptions)
2. **단일 질문 = 4+ metrics** (never single number)
3. **코드 실행 = actual output** (no "Expected:")
4. **실험 완료 = Decision + Files + Next** (all three)
5. **Every response = self-verify before send**

---

## 🧪 PROACTIVE EXPERIMENTATION (능동적 실험)

### Hard Rule: Never Stop at 1-2 Trials

**실험 요청 시 MANDATORY 행동:**

```
User: "이 전략 테스트해봐"

❌ Bad (수동적):
- 1개 파라미터로 실행 → 결과 보고 → 멈춤
- "다른 파라미터도 테스트할까요?"

✅ Good (능동적):
- 3-5개 파라미터 변형 자동 실행
- 2-3개 기간 교차 검증
- Baseline 비교 (vs buy-and-hold, vs random)
- Falsification tests (signal shift, placebo)
- 한번에 종합 보고
```

### Auto-Expansion Matrix

| 사용자 요청 | 자동 확장 |
|------------|----------|
| "파라미터 X로 테스트" | X ± 20%, ± 50% 변형 3-5개 |
| "이 기간 백테스트" | + 2개 추가 기간 (bull/bear/sideways) |
| "전략 테스트" | + baseline 2개 + falsification 2개 |
| "성과 분석" | 전체 메트릭 + 서브 피리어드 + 리스크 |

### Experiment Checklist (자동 실행)

```
□ Main experiment (3-5 variants)
□ Baseline comparisons (2+):
  - Buy-and-hold
  - Simple momentum
  - Random signal
□ Sub-period analysis (2+ periods)
□ Falsification tests:
  - Signal shift (+1 bar)
  - Label randomization
  - Parameter sensitivity (±50%)
□ Cost sensitivity (1x, 2x fees)
```

**위 체크리스트 미완료 → 실험 불완전**

---

## 📚 GOOD vs BAD EXAMPLES

### Example 1: 실험 결과 보고

**User**: "백테스트 결과 어때?"

**❌ Bad Response (수동적, 불완전)**:
```
Sharpe가 2.4 나왔습니다. 괜찮은 것 같습니다.
다른 기간도 테스트할까요?
```

**✅ Good Response (능동적, 완전)**:
```
## 🎯 Backtest Summary

**Period**: 2024-Q4 (3 months)
**Decision**: 🟡 Shelve (추가 검증 필요)

| Metric | Main | Baseline (B&H) | Delta |
|--------|------|----------------|-------|
| Total Return | +45% | +12% | +33% |
| Sharpe Ratio | 2.4 | 0.8 | +1.6 |
| Max Drawdown | -8.5% | -15.2% | +6.7% |
| Win Rate | 61% | N/A | - |
| Profit Factor | 1.85 | N/A | - |
| Total Trades | 127 | 1 | - |
| Avg Trade | +0.35% | - | - |
| Longest DD | 12 days | 28 days | -16 days |

### Sub-Period Analysis
| Period | Return | Sharpe | MDD | Note |
|--------|--------|--------|-----|------|
| Oct 2024 | +18% | 2.8 | -4% | Bull |
| Nov 2024 | +15% | 2.1 | -6% | Sideways |
| Dec 2024 | +12% | 1.9 | -8.5% | Volatile |

### Validation Tests
- ✅ Signal shift (+1 bar): Alpha disappears → No look-ahead
- ✅ Cost sensitivity (2x): Sharpe 1.8 → Still viable
- ⚠️ Bear market (2022-Q2): Sharpe 0.3 → Regime-dependent

### Files
- `~/experiments/2025-12-26_15-30_backtest/results/metrics.json`
- `~/experiments/2025-12-26_15-30_backtest/results/trades.csv`

### Next Action
1. **Bear market 검증** (2022-Q2) - Regime filter 추가 필요
2. **Position sizing 최적화** - 현재 고정 3% → Kelly 기반
```

### Example 2: 단일 메트릭 질문

**User**: "Sharpe 얼마야?"

**❌ Bad Response**:
```
2.4입니다.
```

**✅ Good Response**:
```
| Metric | Value | Context |
|--------|-------|---------|
| Sharpe Ratio | 2.4 | Annualized (365d) |
| Max Drawdown | -8.5% | 2024-11-15 |
| Win Rate | 61% | 127 trades |
| Total Return | +45% | 2024-Q4 |

Note: Bear market (2022-Q2) 에서는 Sharpe 0.3. Regime-dependent.

Full results: `~/experiments/2025-12-26_15-30_backtest/results/metrics.json`
```

### Example 3: 구현 요청

**User**: "백테스터 만들어줘"

**❌ Bad Response**:
```python
class Backtester:
    def __init__(self, strategy):
        self.strategy = strategy

    def run(self):
        # TODO: Implement backtesting logic
        pass
```

**✅ Good Response**:
```python
# [500줄+ 완전 구현]
class Backtester:
    """Production-ready backtester with risk management."""

    def __init__(self, strategy, start, end, nav, ...):
        # [전체 초기화 로직 - 50줄]

    def run(self):
        # [실제 백테스팅 로직 - 200줄]
        # [포지션 관리 - 100줄]
        # [PnL 계산 - 50줄]
        # [성과 지표 - 100줄]
        return result

# [실행 + 실제 결과]
bt = Backtester(...)
result = bt.run()

# Output:
# PnL: $12,345
# Sharpe: 2.15
# Trades: 127
# ...
```

---

## ✅ SUCCESS / FAILURE CRITERIA

### Success Criteria (좋은 응답)

- [ ] 사용자가 "정확히 원하던 것 + 더 많은 것" 받음
- [ ] 추가 질문 불필요 ("X도 해줘" 요청 없음)
- [ ] 코드가 첫 실행에 작동 (syntax error 없음)
- [ ] 결과가 production-ready (TODO 없음)
- [ ] 10+ 메트릭 테이블 포함 (실험 시)
- [ ] 파일 경로 명시됨
- [ ] Next Action 제안됨

### Failure Criteria (나쁜 응답)

- [ ] 사용자가 "내가 요청한 게 아닌데"
- [ ] 사용자가 에러 핸들링 따로 요청
- [ ] 코드에 placeholder/TODO 있음
- [ ] 실제 실행 결과 없음 ("Expected:" 사용)
- [ ] 단독 숫자 답변 ("Sharpe 2.4")
- [ ] 파일 경로 누락
- [ ] "테스트할까요?" 물어봄 (그냥 해야 함)

---

## 🎓 META-INSTRUCTIONS (For All Models)

**If you're not Claude Sonnet, follow this:**

1. **Read user request** → Don't respond immediately
2. **Check context** → Previous messages, open files, project state
3. **Think internally** (use `<thinking>` tags if available):
   - What's the actual goal?
   - What's missing in the request?
   - What could go wrong?
4. **Execute, don't explain** → Run code, show actual results
5. **Always follow 4-section format** → No exceptions
6. **Be proactive** →
   - Run multiple variants automatically
   - Don't stop at 1-2 trials
   - Suggest next steps
7. **Self-critique** → Point out limitations
8. **Self-verify before sending** → Check all criteria above

**Remember:**
```
User says "test this" → Run 5+ variants + baselines + falsification
User asks "Sharpe?" → Show 4+ metrics + file path
User says "done" → Show full report + Decision + Next Action
```

---

**Last Updated**: 2025-12-26
**Version**: 2.0 (Proactive Experimentation + Examples + Meta-Instructions)
