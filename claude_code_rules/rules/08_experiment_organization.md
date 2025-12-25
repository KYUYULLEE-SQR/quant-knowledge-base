# 📁 Experiment Organization (실험 파일 관리)

## 🎯 Purpose
**실험마다 독립된 폴더 + 표준화된 구조 = 재현성 + 추적성 + 휘발 방지**

---

## 📂 Minimal Directory Structure

### 실험 루트 디렉토리
```
~/experiments/
├── 2025-12-18_15-30_experiment_name/
├── 2025-12-18_16-45_another_experiment/
└── REGISTRY.md                        # 실험 추적 (MANDATORY)
```

### 개별 실험 폴더 (최소 구조)
```
experiments/YYYY-MM-DD_HH-MM_experiment_name/
├── README.md                          # 실험 카드 (가설, 결론, 메타데이터)
├── config.yaml                        # 설정 (고정값 기록)
├── code/                              # 실험 코드
├── results/                           # 결과물
│   ├── summary.md                     # ⭐ 한 줄 요약 (나중에 빠르게 찾기용)
│   ├── metrics.json                   # 핵심 지표
│   ├── trades.csv                     # 거래 내역 (trade-by-trade)
│   └── reconciliation.csv             # 포지션/PnL 정합성 체크
└── logs/                              # 실행 로그
```

**Note**: 전략 타입(옵션/MM/롱숏/arbitrage)에 따라 추가 구조는 자유롭게 추가

---

## 🚨 Experiment Completion Protocol (MANDATORY)

**실험이 종료되면 MUST 실행 (자동):**

### 1️⃣ Before Experiment Ends (종료 직전)

```python
# Agent MUST do this BEFORE ending conversation

from pathlib import Path
from datetime import datetime
import json

exp_dir = Path("~/experiments/YYYY-MM-DD_HH-MM_name").expanduser()

# 1. Write results/summary.md (한 줄 요약 + 핵심 지표)
summary = f"""# Experiment Summary

**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Decision**: Deploy / Shelve / Discard

## One-Line Summary
[실험 한 줄 요약 - 가설, 결과, 결론]

## Key Metrics
| Metric | Value |
|--------|-------|
| Sharpe | {sharpe} |
| Max DD | {mdd}% |
| Trades | {trades} |
| Win Rate | {win_rate}% |

## Decision Rationale
[Deploy/Shelve/Discard 이유 1-2문장]

## Next Action
[다음에 할 실험 1개]
"""

(exp_dir / "results" / "summary.md").write_text(summary)

# 2. Write results/metrics.json (구조화된 데이터)
metrics = {
    "sharpe": sharpe,
    "max_dd": mdd,
    "total_trades": trades,
    "win_rate": win_rate,
    "decision": "deploy/shelve/discard",
    "timestamp": datetime.now().isoformat()
}

with open(exp_dir / "results" / "metrics.json", 'w') as f:
    json.dump(metrics, f, indent=2)

# 3. Write README.md (상세 보고서)
readme = """
[See README.md Required Sections below]
"""
(exp_dir / "README.md").write_text(readme)

# 4. Update ~/experiments/REGISTRY.md (자동 인덱싱)
update_registry(exp_dir.name, metrics)
```

### 2️⃣ Update REGISTRY.md (자동)

```python
def update_registry(exp_name: str, metrics: dict):
    """
    REGISTRY.md 자동 업데이트 (실험 종료 시마다)
    """
    registry_file = Path("~/experiments/REGISTRY.md").expanduser()

    # REGISTRY.md 없으면 생성
    if not registry_file.exists():
        header = """# Experiment Registry

| Date | Name | Status | Sharpe | Decision | Notes |
|------|------|--------|--------|----------|-------|
"""
        registry_file.write_text(header)

    # 새 실험 추가
    date = exp_name.split('_')[0]  # YYYY-MM-DD
    short_name = '_'.join(exp_name.split('_')[2:])

    # Status emoji
    status = "✅" if metrics["decision"] == "deploy" else \
             "🟡" if metrics["decision"] == "shelve" else "🔴"

    new_row = f"| {date} | {short_name} | {status} | {metrics['sharpe']:.2f} | {metrics['decision'].title()} | [자동 생성] |\n"

    # 파일 끝에 추가 (atomic write)
    content = registry_file.read_text()
    registry_file.write_text(content + new_row)
```

### 3️⃣ Completion Checklist (자동 실행)

**Agent MUST check before ending experiment:**

- [ ] `results/summary.md` exists and non-empty
- [ ] `results/metrics.json` exists with all required keys
- [ ] `README.md` exists with all 8 required sections
- [ ] `config.yaml` saved at start
- [ ] All artifacts saved (trades.csv, positions.csv, etc.)
- [ ] REGISTRY.md updated
- [ ] No loose files in project root

**If ANY checkbox fails → Agent MUST fix before ending.**

---

## 📝 README.md Required Sections

Every experiment MUST have a README with:

1. **Hypothesis** (What/Why/Change)
2. **Configuration** (Period/Universe/Costs/Parameters)
3. **Results Summary** (Table with key metrics)
4. **Validation Results** (Checkboxes with actual results)
5. **Key Findings** (3-5 bullet points)
6. **Risks & Limitations** (2-3 bullet points)
7. **Reconciliation Status** (✅/❌ - trade-by-trade integrity)
8. **Next Steps** (1-2 next experiments)

**Template**:

```markdown
# [Experiment Name]

**Date**: YYYY-MM-DD HH:MM
**Decision**: ✅ Deploy / 🟡 Shelve / 🔴 Discard

---

## Hypothesis

[가설: X를 하면 Y가 개선될 것]

## Configuration

**Period**: 2024-10-01 ~ 2024-10-07
**Universe**: BTC-PUT options
**Costs**: OKX DMM VIP9 (maker -1 bps, taker +3 bps)
**Parameters**:
- Model: Ridge (alpha=1.0, degree=2)
- IV filter: 15%
- TTE filter: 3-30 days

## Results Summary

| Metric | Value | Baseline | Change |
|--------|-------|----------|--------|
| Sharpe | 2.4   | 1.8      | +33%   |
| Max DD | -8.5% | -12.3%   | +3.8%  |
| Trades | 127   | 203      | -37%   |
| Win Rate | 61.2% | 52.1%  | +9.1%  |

## Validation Results

- ✅ Placebo test: Signal shift → alpha disappears
- ✅ Parameter stability: CV 12% (acceptable)
- ✅ Cost sensitivity: Sharpe 1.8 @ 2× fees (still viable)
- ✅ Sub-period: Q4 positive, Q3 flat (regime-dependent)

## Key Findings

1. IV 필터 15% → 거짓 신호 37% 감소 (trades 127 vs 203)
2. Deep OTM 집중 (83%) → 승률 개선 (+9.1%)
3. Bear market (2022-Q2) 검증 필요 (bull-only 데이터)

## Risks & Limitations

1. **Bull market bias**: Q4 2024만 테스트, bear market 미검증
2. **Sample size**: 127 trades (통계적 유의성 경계)
3. **Greeks dependency**: OKX Greeks 사용, 다른 거래소 적용 불가

## Reconciliation Status

- ✅ Position continuity: All trades reconciled
- ✅ Cash conservation: Cash flow matches (err: 0.0003%)
- ✅ PnL attribution: Components sum correctly (err: 0.0002%)
- ✅ No orphan trades
- ✅ Greeks tracking: Delta/Gamma/Theta tracked

## Next Steps

1. **Phase 1**: TTE 필터 3d → 5d (IV=15% 고정, 단일 변수)
2. **Validation**: Bear market (2022-Q2) 백테스트
```

---

## 🧹 "실험 정리해" Command (User-Triggered Cleanup)

**When user says "실험 정리해":**

### Step 1: Scan Experiments Folder

```python
from pathlib import Path

exp_root = Path("~/experiments").expanduser()

# Find incomplete experiments (no summary.md or README.md)
incomplete = []
for exp_dir in sorted(exp_root.glob("*/")):
    if not exp_dir.is_dir():
        continue

    has_summary = (exp_dir / "results" / "summary.md").exists()
    has_readme = (exp_dir / "README.md").exists()

    if not has_summary or not has_readme:
        incomplete.append(exp_dir)

print(f"⚠️ Found {len(incomplete)} incomplete experiments:")
for exp in incomplete:
    print(f"  - {exp.name}")
```

### Step 2: Offer Actions

```
⚠️ 발견된 문제:

1. **Incomplete experiments (3개)**:
   - 2025-12-20_14-30_test_idea (summary.md 없음)
   - 2025-12-21_09-15_quick_test (README.md 없음)
   - 2025-12-22_16-00_experiment_v2 (둘 다 없음)

2. **Loose files in root (2개)**:
   - test.py
   - quick_analysis.ipynb

🔧 제안 조치:

A. **Incomplete experiments** →
   - Option 1: 자동으로 summary.md + README.md 생성 (실험 로그 기반)
   - Option 2: 수동 작성 안내
   - Option 3: _archive/incomplete/로 이동

B. **Loose files** →
   - test.py → scratch/ 이동
   - quick_analysis.ipynb → experiments/[가장 최근]/code/ 이동 or 삭제

진행할까요? (A-1 + B 자동 실행)
```

### Step 3: Auto-Fix (User Approval)

```python
# A-1: Auto-generate summary.md from logs
def generate_summary_from_logs(exp_dir: Path):
    """
    실험 로그/결과 파일에서 summary.md 자동 생성
    """
    metrics_file = exp_dir / "results" / "metrics.json"

    if metrics_file.exists():
        # metrics.json 있으면 그대로 사용
        with open(metrics_file) as f:
            metrics = json.load(f)
    else:
        # 없으면 placeholder
        metrics = {
            "sharpe": "N/A",
            "max_dd": "N/A",
            "decision": "incomplete"
        }

    summary = f"""# Experiment Summary (Auto-Generated)

**Date**: {exp_dir.name.split('_')[0]}
**Decision**: ⚠️ Incomplete (no decision recorded)

## One-Line Summary
[Auto-generated placeholder - please update]

## Key Metrics
| Metric | Value |
|--------|-------|
| Sharpe | {metrics.get('sharpe', 'N/A')} |
| Max DD | {metrics.get('max_dd', 'N/A')} |

## Decision Rationale
⚠️ Experiment incomplete - no summary recorded.

## Next Action
Review and complete this experiment or archive it.
"""

    (exp_dir / "results" / "summary.md").write_text(summary)
    print(f"✅ Generated summary.md for {exp_dir.name}")

# B: Move loose files
def move_loose_files():
    """
    프로젝트 루트의 loose files를 적절한 위치로 이동
    """
    # See 11_file_hygiene.md for full logic
    pass
```

---

## 🤖 Agent Rules for File Organization

### MANDATORY behaviors:

1. **Create experiment folder BEFORE running**
   ```python
   from datetime import datetime
   exp_name = datetime.now().strftime("%Y-%m-%d_%H-%M") + "_fair_iv_ridge"
   exp_dir = Path(f"~/experiments/{exp_name}").expanduser()
   exp_dir.mkdir(parents=True, exist_ok=True)
   (exp_dir / "code").mkdir(exist_ok=True)
   (exp_dir / "results").mkdir(exist_ok=True)
   (exp_dir / "logs").mkdir(exist_ok=True)
   (exp_dir / "validation").mkdir(exist_ok=True)
   ```

2. **Save ALL outputs to experiment folder**
   - Metrics: `results/metrics.json`
   - Summary: `results/summary.md` ⭐ NEW (MANDATORY)
   - Logs: `logs/experiment.log`
   - Plots: `results/figures/*.png`
   - Code: `code/*.py` (copy or save)

3. **Generate summary.md + README.md at the END (MANDATORY)**
   - ❌ OLD: "After all experiments complete" (vague)
   - ✅ NEW: **BEFORE ending conversation with user**
   - Include actual results (not placeholders)
   - Mark validation checkboxes based on actual tests
   - Update REGISTRY.md automatically

4. **Save config.yaml at the START**
   ```yaml
   experiment:
     name: fair_iv_ridge
     date: 2025-12-18 15:30
     hypothesis: "Ridge regression can predict fair IV better than naive model"

   data:
     period_start: 2024-10-01
     period_end: 2024-10-07
     symbols: ["BTC-PUT"]
     source: "postgresql://sqr:sqr@localhost/data_integration"

   parameters:
     model: Ridge
     alpha: 1.0
     degree: 2
     cv_folds: 5

   costs:
     exchange: OKX DMM VIP9
     maker_fee: -0.01%  # Fixed: was -0.02%
     taker_fee: 0.03%
   ```

5. **Never scatter files in random locations**
   - ❌ `test.py`, `test2.py`, `final.py`, `final_final.py` in root
   - ✅ All in `experiments/YYYY-MM-DD_HH-MM_name/code/`

6. **Never leave incomplete experiments**
   - ❌ Experiment done → no summary → user can't find results later
   - ✅ Experiment done → summary.md + README.md + REGISTRY.md updated

---

## 🔍 Searchability & Traceability

### Git Integration
```bash
cd ~/experiments
git init  # if not already
git add YYYY-MM-DD_HH-MM_name/
git commit -m "Experiment: Fair IV Ridge - Sharpe 2.4, Deploy"
git tag exp-fair-iv-ridge-v1
```

### Quick Search (Fast Finding)

```bash
# Find experiments by decision
grep -l "Decision.*Deploy" ~/experiments/*/results/summary.md

# Find experiments by metric threshold
grep -r "Sharpe.*2\.[4-9]" ~/experiments/*/results/summary.md

# Find experiments by date range
ls ~/experiments/ | grep "2025-12"

# Find incomplete experiments
find ~/experiments -type d -mindepth 1 -maxdepth 1 \
  ! -exec test -e "{}/results/summary.md" \; -print

# Check REGISTRY.md (all experiments at a glance)
cat ~/experiments/REGISTRY.md
```

---

## 📊 Experiment Registry (MANDATORY)

**Location**: `~/experiments/REGISTRY.md`

**Purpose**: 모든 실험을 한눈에 보기 + 빠른 검색

**Format**:

```markdown
# Experiment Registry

| Date | Name | Status | Sharpe | Decision | Notes |
|------|------|--------|--------|----------|-------|
| 2025-12-18 | fair_iv_ridge | ✅ | 2.4 | Deploy | Q4 only, needs bear market validation |
| 2025-12-18 | mispricing_filter | 🟡 | 1.8 | Shelve | Low sample size (127 trades) |
| 2025-12-19 | regime_backtest | 🔴 | 0.3 | Discard | No edge detected |
| 2025-12-20 | tte_filter_5d | ✅ | 2.1 | Deploy | Phase 1 complete, combine with IV=15% |
```

**Agent MUST update this file after EVERY experiment (automatic).**

**Emoji guide**:
- ✅ Deploy: Ready for production
- 🟡 Shelve: Promising but needs more work
- 🔴 Discard: Failed / no edge

---

## 🚫 Anti-Volatility Rules (강제)

### ❌ NEVER Do This:

1. ❌ End conversation without writing summary.md
2. ❌ Report results verbally but not save to disk
3. ❌ "유용한 결과" 일부만 보고 → 나머지 휘발
4. ❌ Incomplete experiments left in ~/experiments/
5. ❌ Forget to update REGISTRY.md

### ✅ ALWAYS Do This:

1. ✅ **Before ending conversation**:
   - Write `results/summary.md`
   - Write `README.md`
   - Update `REGISTRY.md`
   - Save all artifacts (trades.csv, metrics.json, etc.)

2. ✅ **When user says "실험 정리해"**:
   - Scan for incomplete experiments
   - Auto-generate missing summary.md
   - Offer to move loose files
   - Update REGISTRY.md

3. ✅ **When reporting results**:
   - Show metrics verbally AND save to disk
   - Give file paths where results are saved
   - "결과는 ~/experiments/2025-12-25_16-30_test/results/summary.md 에 저장했습니다"

---

## 📋 Completion Checklist (Agent Self-Check)

**Before ending ANY experiment conversation, Agent MUST verify:**

- [ ] Experiment folder exists (~/experiments/YYYY-MM-DD_HH-MM_name/)
- [ ] config.yaml saved at start
- [ ] All code saved to code/
- [ ] All results saved to results/
  - [ ] summary.md (1-page quick reference)
  - [ ] metrics.json (structured data)
  - [ ] trades.csv (if backtest)
  - [ ] reconciliation.csv (if backtest)
- [ ] README.md written (8 required sections)
- [ ] REGISTRY.md updated (new row added)
- [ ] No loose files in project root
- [ ] User informed of file paths

**If ANY item fails → Agent MUST fix immediately before ending.**

---

**Last Updated**: 2025-12-25
**Version**: 2.0 (Anti-Volatility Enforcement Added)
