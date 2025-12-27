# File Organization Policy (파일 정리 정책)

**Last Updated**: 2025-12-22
**Source**: User requirement (100+ experiments management)
**Importance**: ⭐⭐⭐ Critical - 못 찾으면 = 없는 것

---

## Problem Statement

**현재 문제**:
- 실험 100개 → 같은 폴더에 날짜 prefix로 쌓임
- 찾기 어려움: "3개월 전 fair IV 실험 어디 있지?"
- Agent 헷갈림: 비슷한 이름들 혼동
- 파일명 규칙 없음: `test.py`, `final_final.py`, `backup_v3.py`

**목표**:
- **3초 내 찾기**: 전략/단계/날짜로 빠른 탐색
- **Agent 명확성**: 폴더 구조만 봐도 이해 가능
- **확장성**: 1000개 실험도 문제없는 구조

---

## Directory Structure (계층 설계)

### Top-Level Structure

```
~/experiments/
├── strategies/                 # 전략별 분류 (Main)
│   ├── fair_iv/
│   ├── mispricing/
│   ├── theta_harvesting/
│   ├── delta_neutral/
│   └── market_making/
│
├── _archive/                   # 6개월+ 오래된 실험
│   └── 2024-Q2/
│
├── _failed/                    # 명확히 실패한 실험 (보존용)
│   └── 2025-12-15_bad_idea/
│
├── _templates/                 # 실험 템플릿
│   ├── experiment_template/
│   └── backtest_template/
│
├── REGISTRY.md                 # 전체 실험 인덱스 (검색용)
└── README.md                   # 폴더 구조 설명
```

### Strategy-Level Structure

```
~/experiments/strategies/fair_iv/
├── phase1_baseline/            # Phase별 하위 폴더
│   ├── 2025-12-18_ridge/
│   ├── 2025-12-19_lasso/
│   └── 2025-12-20_ridge_optimized/
│
├── phase2_features/
│   ├── 2025-12-22_add_tte_filter/
│   └── 2025-12-23_add_moneyness/
│
├── phase3_validation/
│   ├── 2025-12-25_walk_forward/
│   └── 2025-12-26_regime_test/
│
├── deployed/                   # 실제 배포된 버전
│   └── 2025-12-30_final_v1.0/
│
└── README.md                   # Fair IV 전략 전체 요약
```

### Individual Experiment Structure

```
~/experiments/strategies/fair_iv/phase1_baseline/2025-12-18_ridge/
├── README.md                   # 실험 카드 (가설, 결론)
├── config.yaml                 # 파라미터 (고정값)
├── code/                       # 코드
│   ├── backtest.py             # 메인 백테스트
│   ├── baseline_simple.py      # 베이스라인
│   └── utils.py
├── results/                    # 결과
│   ├── metrics.json            # 표준 지표 (Sharpe, MDD, ...)
│   ├── trades.csv              # 거래 내역
│   ├── nav.csv                 # NAV (Mark-to-Market)
│   ├── reconciliation.csv      # 정합성 체크
│   └── figures/
│       ├── equity_curve.png
│       └── drawdown.png
├── logs/                       # 로그
│   └── backtest.log
└── validation/                 # 검증 테스트 결과
    ├── placebo_test.json
    ├── cost_sensitivity.json
    └── parameter_stability.json
```

---

## Naming Conventions

### 1. Strategy Folder Names

**Format**: `{strategy_name}` (lowercase, underscores)

**Examples**:
- ✅ `fair_iv`
- ✅ `theta_harvesting`
- ✅ `delta_neutral_options`
- ❌ `FairIV` (no camelCase)
- ❌ `strategy-1` (no hyphens)

### 2. Phase Folder Names

**Format**: `phase{N}_{description}`

**Examples**:
- ✅ `phase1_baseline`
- ✅ `phase2_optimization`
- ✅ `phase3_validation`
- ✅ `phase4_robustness`

**Purpose**: Experiment methodology의 Phase 1→2 순서 반영

### 3. Experiment Folder Names

**Format**: `{YYYY-MM-DD}_{short_description}`

**Rules**:
- Date: ISO format (YYYY-MM-DD)
- Description: 2-4 words, lowercase, underscores
- Max length: 50 characters

**Examples**:
- ✅ `2025-12-18_ridge_baseline`
- ✅ `2025-12-22_iv_filter_15pct`
- ✅ `2025-12-25_cost_2x_test`
- ❌ `experiment_final_v3` (no date)
- ❌ `2025-12-18-Ridge-Baseline` (wrong format)

### 4. File Names (Inside Experiment)

**Config/Docs**:
- `README.md` (mandatory)
- `config.yaml` (mandatory)

**Code**:
- `backtest.py` (main backtest)
- `baseline_{name}.py` (baselines)
- `utils.py`, `models.py`, `features.py`

**Results**:
- `metrics.json` (standard metrics, mandatory)
- `nav.csv` (NAV time series, mandatory)
- `trades.csv` (trade-by-trade)
- `positions.csv` (position snapshots)
- `reconciliation.csv` (integrity checks)

**Figures**:
- `equity_curve.png`
- `drawdown.png`
- `returns_distribution.png`

**❌ Forbidden Names**:
- `test.py`, `test2.py`, `test_final.py`
- `backup.py`, `old.py`, `new.py`
- `untitled.py`, `script.py`
- `final_final_v3_REALLY_FINAL.py` 😡

---

## REGISTRY.md (Experiment Index)

**Purpose**: 전체 실험을 빠르게 검색/필터링

**Location**: `~/experiments/REGISTRY.md`

**Format**:
```markdown
# Experiment Registry

**Last Updated**: 2025-12-22

---

## Quick Search

### By Status
- [Deployed](#deployed)
- [In Progress](#in-progress)
- [Shelved](#shelved)
- [Failed](#failed)

### By Strategy
- [Fair IV](#fair-iv)
- [Mispricing](#mispricing)
- [Theta Harvesting](#theta-harvesting)

---

## Deployed

| Date | Strategy | Name | Sharpe | MDD | Status | Notes |
|------|----------|------|--------|-----|--------|-------|
| 2025-12-30 | Fair IV | Ridge v1.0 | 2.4 | -12% | ✅ Live | DMM VIP9, 3% NAV |

## In Progress

| Date | Strategy | Phase | Name | Expected | Notes |
|------|----------|-------|------|----------|-------|
| 2025-12-22 | Fair IV | Phase 2 | IV Filter 15% | 2025-12-25 | Testing |
| 2025-12-23 | Mispricing | Phase 1 | Baseline | 2025-12-26 | Just started |

## Shelved

| Date | Strategy | Name | Sharpe | Reason | Notes |
|------|----------|------|--------|--------|-------|
| 2025-12-20 | Fair IV | Lasso | 1.2 | Low Sharpe | Ridge better |

## Failed

| Date | Strategy | Name | Reason | Lesson Learned |
|------|----------|------|--------|----------------|
| 2025-12-15 | Random | Bad Idea | Look-ahead bias | Always placebo test |

---

## Fair IV

### Summary
Strategy: Predict fair IV, trade mispriced options

### Experiments
1. **2025-12-18 - Ridge Baseline** (Phase 1)
   - Path: `strategies/fair_iv/phase1_baseline/2025-12-18_ridge/`
   - Result: Sharpe 2.1, MDD -15%
   - Status: ✅ Baseline established

2. **2025-12-22 - IV Filter 15%** (Phase 2)
   - Path: `strategies/fair_iv/phase2_features/2025-12-22_iv_filter_15pct/`
   - Result: Sharpe 2.4 (+0.3 vs baseline)
   - Status: ✅ Improvement validated

3. **2025-12-30 - Final v1.0** (Deployed)
   - Path: `strategies/fair_iv/deployed/2025-12-30_final_v1.0/`
   - Result: Sharpe 2.4, MDD -12%
   - Status: ✅ Live (3% NAV, DMM VIP9)

[... more strategies ...]
```

---

## Workflow

### Creating New Experiment

**Step 1: Determine hierarchy**
```bash
# Which strategy?
STRATEGY="fair_iv"

# Which phase?
PHASE="phase2_optimization"

# Experiment name?
EXP_NAME="2025-12-22_iv_filter_15pct"
```

**Step 2: Create structure**
```bash
# Create experiment folder
EXP_DIR=~/experiments/strategies/${STRATEGY}/${PHASE}/${EXP_NAME}
mkdir -p ${EXP_DIR}/{code,results/figures,logs,validation}

# Copy templates
cp ~/experiments/_templates/experiment_template/README.md ${EXP_DIR}/
cp ~/experiments/_templates/experiment_template/config.yaml ${EXP_DIR}/

# Update README with actual experiment details
vim ${EXP_DIR}/README.md
```

**Step 3: Run experiment**
```bash
cd ${EXP_DIR}
python code/backtest.py --config config.yaml
```

**Step 4: Update registry**
```bash
# Add entry to REGISTRY.md
vim ~/experiments/REGISTRY.md
```

### Moving to Archive

**When**: Experiment > 6 months old AND not referenced

```bash
# Archive entire phase or strategy
mv ~/experiments/strategies/old_strategy ~/experiments/_archive/2024-Q2/
```

### Marking as Failed

**When**: Experiment clearly failed (integrity fail, look-ahead bias, etc.)

```bash
# Move to _failed (preserve for learning)
mv ~/experiments/strategies/fair_iv/phase1_baseline/2025-12-15_bad_idea \
   ~/experiments/_failed/
```

---

## Agent Protocol: File Organization

### BEFORE creating files

1. ✅ Read this policy (file_organization_policy.md)
2. ✅ Determine hierarchy:
   - Strategy name?
   - Phase number?
   - Experiment short description?
3. ✅ Check naming conventions (lowercase, underscores, date prefix)
4. ✅ Create full directory structure (code/, results/, logs/, validation/)
5. ✅ Copy templates (README, config.yaml)

### DURING experiment

6. ✅ Save ALL outputs to experiment folder (never ~/experiments/ root)
7. ✅ Use standard file names (metrics.json, nav.csv, trades.csv)
8. ✅ Generate figures in results/figures/

### AFTER experiment

9. ✅ Write README.md with actual results (not placeholders)
10. ✅ Update REGISTRY.md (add entry)
11. ✅ If failed → Move to _failed/ (preserve lesson)
12. ✅ If succeeded → Keep in phase folder or move to deployed/

### NEVER

❌ Create files in ~/experiments/ root (except REGISTRY.md)
❌ Use `test.py`, `final.py`, `backup.py` names
❌ Create folders without date prefix
❌ Scatter files randomly
❌ Forget to update REGISTRY.md

### Example Dialogue

```
User: "Fair IV 실험 시작해"

Agent:
  [1] Reads file_organization_policy.md
  [2] Determines hierarchy:
      Strategy: fair_iv
      Phase: phase1_baseline (첫 실험)
      Name: 2025-12-22_ridge_baseline
  [3] Creates structure:

  Creating experiment:
    Path: ~/experiments/strategies/fair_iv/phase1_baseline/2025-12-22_ridge_baseline/
    Structure:
      ├── README.md (template copied)
      ├── config.yaml (template copied)
      ├── code/
      ├── results/
      ├── logs/
      └── validation/

  [4] Starts coding in code/backtest.py
  [5] Saves all results to results/
  [6] Updates REGISTRY.md when done

  📚 출처: knowledge/experiments/file_organization_policy.md
```

---

## Common Violations (and Fixes)

### ❌ Violation 1: Root-level clutter
```bash
# Bad
~/experiments/test.py
~/experiments/backtest_v2.py
~/experiments/results.csv
```

**Fix**:
```bash
# Good
~/experiments/strategies/fair_iv/phase1_baseline/2025-12-22_ridge/code/backtest.py
~/experiments/strategies/fair_iv/phase1_baseline/2025-12-22_ridge/results/metrics.json
```

### ❌ Violation 2: No date prefix
```bash
# Bad
~/experiments/strategies/fair_iv/ridge_experiment/
```

**Fix**:
```bash
# Good
~/experiments/strategies/fair_iv/phase1_baseline/2025-12-22_ridge/
```

### ❌ Violation 3: Terrible file names
```bash
# Bad
code/test.py
code/final_final.py
code/backup_v3.py
```

**Fix**:
```bash
# Good
code/backtest.py
code/baseline_simple.py
code/utils.py
```

### ❌ Violation 4: No REGISTRY update
```bash
# Bad: Experiment done, REGISTRY.md not updated
# → 3 months later: "어디 있더라?"
```

**Fix**:
```bash
# Good: Immediately update REGISTRY.md
vim ~/experiments/REGISTRY.md
# Add: | 2025-12-22 | Fair IV | Ridge | 2.4 | -12% | ✅ Done | ... |
```

---

## Benefits

### Before (Chaos)
```
~/experiments/
├── test.py
├── test2.py
├── backtest_final.py
├── 2025-12-18_some_experiment/
├── 2025-12-19_another_thing/
├── 2025-12-20_idk_what_this_is/
└── ... (100 more)

User: "3개월 전 Fair IV Ridge 실험 어디 있지?"
Agent: "찾을 수 없습니다..." 😵
```

### After (Order)
```
~/experiments/
├── strategies/
│   └── fair_iv/
│       └── phase1_baseline/
│           └── 2025-12-18_ridge/  ← Found in 3 seconds
├── REGISTRY.md  ← Or search here
└── ...

User: "Fair IV Ridge 실험 결과 보여줘"
Agent: [Reads REGISTRY.md] "strategies/fair_iv/phase1_baseline/2025-12-18_ridge/
       Sharpe 2.1, MDD -15%. README: ..." ✅
```

---

## References

- **Related KB**:
  - [Experiment Methodology](methodology.md) - Phase 1→2 순서
  - [Performance Metrics](performance_metrics.md) - metrics.json 표준
- **User Requirement**: "실험 100개 할건데 정리 안 되면 못 찾음"

---

**Version**: 1.0
**Critical**: Follow this STRICTLY. Chaos = waste of weeks/months.
