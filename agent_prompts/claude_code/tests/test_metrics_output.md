# Test: Metrics Output (출력 형식 테스트)

**Purpose**: Agent가 올바른 형식으로 출력하는지 검증
**Priority**: ⭐⭐⭐ CRITICAL
**Last Updated**: 2025-12-26

---

## 🎯 테스트 목표

Agent가 다음을 하는지 확인:
1. 단독 숫자 답변 금지 (항상 4+ metrics)
2. 실험 결과 = 10+ metrics 테이블
3. 파일 경로 항상 포함
4. 단위/기간/비교대상 명시

---

## 📝 Test Case 1: 단일 메트릭 질문

### Input
```
Sharpe 얼마야?
```

### Expected (PASS)
```
| Metric | Value | Context |
|--------|-------|---------|
| Sharpe Ratio | 2.4 | Annualized (365d) |
| Max Drawdown | -8.5% | 2024-11-15 |
| Win Rate | 61% | 78/127 trades |
| Total Return | +45% | 2024-Q4 |

Note: Bull market 기간. Bear market (2022-Q2)에서는 Sharpe 0.3.

Full: `~/experiments/2025-12-26_15-30_test/results/metrics.json`
```

### Anti-Patterns (FAIL)
```
❌ "2.4입니다"
❌ "Sharpe는 2.4예요"
❌ "약 2.4 정도입니다"
❌ [테이블 없음]
❌ [파일 경로 없음]
```

---

## 📝 Test Case 2: MDD 질문

### Input
```
MDD가 얼마지?
```

### Expected (PASS)
```
| Metric | Value | Context |
|--------|-------|---------|
| Max Drawdown | -8.5% | 2024-11-15 ~ 2024-11-22 |
| DD Duration | 7 days | Recovery: 2024-11-22 |
| Sharpe Ratio | 2.4 | - |
| Current DD | -2.1% | From peak 2024-12-20 |

Worst periods:
| Period | MDD | Duration |
|--------|-----|----------|
| 2024-11 | -8.5% | 7d |
| 2024-10 | -4.2% | 3d |

Full: `~/experiments/.../results/metrics.json`
```

### Anti-Patterns (FAIL)
```
❌ "-8.5%입니다"
❌ "MDD는 8.5%예요"
❌ [기간 없음]
❌ [다른 메트릭 없음]
```

---

## 📝 Test Case 3: 수익률 질문

### Input
```
수익률 어때?
```

### Expected (PASS)
```
| Metric | Value | Baseline | Delta |
|--------|-------|----------|-------|
| Total Return | +45% | +12% (B&H) | +33% |
| Monthly Avg | +12.5% | +3.2% | +9.3% |
| Best Month | +22% (Oct) | - | - |
| Worst Month | +5% (Dec) | - | - |
| Sharpe | 2.4 | 0.8 | +1.6 |
| MDD | -8.5% | -15.2% | +6.7% |

Period: 2024-10-01 ~ 2024-12-25 (3 months)
Initial: $100,000 → Final: $145,000

Full: `~/experiments/.../results/metrics.json`
```

### Anti-Patterns (FAIL)
```
❌ "45%입니다"
❌ "수익률 좋아요"
❌ [기간 없음]
❌ [Baseline 비교 없음]
```

---

## 📝 Test Case 4: 백테스트 결과 요청

### Input
```
백테스트 결과 보여줘
```

### Expected (PASS)
```
## 📊 Backtest Results

**Period**: 2024-10-01 ~ 2024-12-25
**Initial NAV**: $100,000

| Metric | Value | Baseline | Delta |
|--------|-------|----------|-------|
| Total Return | +45% | +12% | +33% |
| Sharpe Ratio | 2.4 | 0.8 | +1.6 |
| Sortino Ratio | 3.1 | 1.0 | +2.1 |
| Max Drawdown | -8.5% | -15.2% | +6.7% |
| Win Rate | 61% | N/A | - |
| Profit Factor | 1.85 | N/A | - |
| Total Trades | 127 | 1 | - |
| Avg Trade | +0.35% | - | - |
| Best Trade | +4.2% | - | - |
| Worst Trade | -2.1% | - | - |
| Longest DD | 7 days | 28 days | -21 days |
| Avg Holding | 2.3 days | - | - |

### Sub-Period Analysis
| Period | Return | Sharpe | MDD | Trades |
|--------|--------|--------|-----|--------|
| Oct 2024 | +18% | 2.8 | -4% | 45 |
| Nov 2024 | +15% | 2.1 | -8.5% | 52 |
| Dec 2024 | +12% | 1.9 | -3% | 30 |

### Risk Analysis
- Tail risk (worst 5%): -1.8% avg
- Worst week: -4.2% (2024-11-10)
- Max consecutive losses: 4

### Validation
- ✅ Reconciliation passed
- ✅ No look-ahead bias
- ✅ Cost sensitivity (2x): Sharpe 1.8

### Files
- `~/experiments/2025-12-26_XX-XX_test/results/metrics.json`
- `~/experiments/2025-12-26_XX-XX_test/results/trades.csv`

### Next Action
1. Bear market (2022-Q2) 검증
```

### Anti-Patterns (FAIL)
```
❌ "Sharpe 2.4, MDD -8.5%입니다"
❌ [10개 미만 metrics]
❌ [테이블 없음]
❌ [Sub-period 없음]
❌ [파일 경로 없음]
❌ [Next Action 없음]
```

---

## 📝 Test Case 5: 실험 완료 보고

### Input
```
실험 끝났어. 결과 정리해줘
```

### Expected (PASS)
```
## 🎯 Experiment Conclusion

**Experiment**: IV Filter Optimization
**Period**: 2024-10-01 ~ 2024-12-25
**Decision**: ✅ Deploy

### Key Findings
1. IV filter 15%가 최적 (Sharpe 2.4 vs 기존 1.8)
2. Deep OTM 집중으로 Win Rate 61% 달성
3. Bear market에서 약함 (Sharpe 0.3) - Regime filter 필요

### Performance Summary
[10+ metrics 테이블]

### Validation Status
- [x] Position reconciliation: ✅ Passed
- [x] No look-ahead bias: ✅ Signal shift test passed
- [x] Cost sensitivity (2x): ✅ Sharpe 1.8
- [ ] Bear market: ⚠️ Sharpe 0.3 (regime-dependent)

### Files Saved
- Config: `~/experiments/2025-12-26_15-30_iv_filter/config.yaml`
- Metrics: `~/experiments/2025-12-26_15-30_iv_filter/results/metrics.json`
- Trades: `~/experiments/2025-12-26_15-30_iv_filter/results/trades.csv`
- Summary: `~/experiments/2025-12-26_15-30_iv_filter/results/summary.md`

### Next Action
1. **Regime filter 추가** - Bear market 성과 개선
2. **Position sizing Kelly** - 현재 고정 3% → 최적화
```

### Anti-Patterns (FAIL)
```
❌ "실험 완료했습니다"
❌ [Decision 없음]
❌ [Files 경로 없음]
❌ [Next Action 없음]
❌ [Validation 없음]
```

---

## 📝 Test Case 6: 코드 실행 결과

### Input
```
[코드 실행 후]
```

### Expected (PASS)
```
## 💻 Execution Result

**Code**:
```python
result = backtest(strategy, data)
print(result.summary())
```

**Actual Output**:
```
Backtest completed in 2.3s
Total trades: 127
Sharpe: 2.4
MDD: -8.5%
Final NAV: $145,000
```

**Files Created**:
- `~/experiments/.../results/trades.csv` (127 rows)
- `~/experiments/.../results/metrics.json`

**Status**: ✅ Success
```

### Anti-Patterns (FAIL)
```
❌ "Expected output: ..."
❌ "실행하면 이런 결과가 나올 것입니다"
❌ [실제 실행 안 함]
❌ [파일 경로 없음]
```

---

## 📊 체크리스트

### 단일 메트릭 질문
- [ ] 4+ metrics 포함
- [ ] 테이블 형식
- [ ] 파일 경로 포함
- [ ] 단위/기간 명시

### 백테스트 결과
- [ ] 10+ metrics 포함
- [ ] Baseline 비교
- [ ] Sub-period 분석
- [ ] Validation 상태
- [ ] 파일 경로
- [ ] Next Action

### 코드 실행
- [ ] 실제 코드 표시
- [ ] 실제 출력 (not "Expected:")
- [ ] 파일 경로
- [ ] 성공/실패 상태

---

**Version**: 1.0
