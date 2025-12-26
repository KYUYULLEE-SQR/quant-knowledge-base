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

**Last Updated**: 2025-12-26
**Version**: 1.0 (Initial - Output Enforcement)
