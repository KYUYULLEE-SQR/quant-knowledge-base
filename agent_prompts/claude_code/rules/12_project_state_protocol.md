# Project State Protocol

**Purpose**: Multi-project state management (read-first approach)
**Last Updated**: 2025-12-25
**Priority**: ⭐⭐⭐ MANDATORY

---

## 🎯 Problem & Solution

### Problem

This server runs **multiple concurrent projects** (options / futures HFT / shitcoin / etc).
Agent is **stateless**, but user expects **stateful continuity**.

**Failure modes** (repeated):
- Same instructions every session ("organize files", "validate integrity", "fix metrics")
- No memory of what was done, what's next
- Experiments scattered, no discipline

### Solution

**Two-layer state architecture**:

1. **Global Knowledge** (`~/knowledge/`): Cross-project truth (Git-managed)
2. **Project-local Memory** (`PROJECT_RULES.md` + `STATE.md`): Per-project state

**Rule**: Start-of-work = read `PROJECT_RULES.md` + `STATE.md`.
If missing, create them (non-destructive) before doing anything else.

---

## 📂 Project Files (Per Project Root)

### PROJECT_RULES.md (Optional)

**Purpose**: Project-specific rules, overrides global rules

**Location**: `<project>/PROJECT_RULES.md`

**When to create**:
- Project has specific constraints (e.g., no destructive operations)
- Different autonomy level than default
- Special safety boundaries

**Template** (minimal):

```markdown
# PROJECT RULES (Override Global)

## Project-Specific Rules

(Leave empty if no overrides needed)

## Autonomy Level

- High / Medium / Low (default: Medium)
  - High: Full autonomy (create folders, run experiments, refactor)
  - Medium: Autonomy for routine tasks, ask for destructive ops
  - Low: Ask for confirmation on most actions

## Safety Boundaries

(Project-specific constraints only, e.g., "Never delete data/")

## End-of-Session Checklist

(If different from global, override here)
```

**If missing**: Use global rules only (from `~/.claude/rules/`)

### STATE.md (Recommended)

**Purpose**: Project memory (current objective, progress, next steps)

**Location**: `<project>/STATE.md`

**When to create**:
- Long-running projects (multiple sessions)
- Need to track progress

**Template**:

```markdown
# STATE (Project Memory)

## Objective

(Current main goal in one sentence)

## Done

- [x] 2025-12-24: Completed fair IV model (Ridge, Sharpe 2.4)
- [x] 2025-12-23: Data collection pipeline setup

## In Progress

- [ ] Mispricing filter validation (started 2025-12-25)

## Next (1-3 items, prioritized)

1. [ ] Backtest mispricing filter (Phase 1, single effect)
2. [ ] Validate on 2022-Q2 (bear market)
3. [ ] Compare with Lasso model

## Assumptions

- OKX data is clean (verified 2025-12-24)
- Greeks are PA-based (not Black-Scholes)
- NAV is Mark-to-Market (daily)

## References

- Knowledge: `~/knowledge/exchanges/okx/options_specifications.md`
- Data: `micky:/futures_data_1m`, `micky:/options_greeks`
- Key scripts: `src/backtest/engine.py`, `src/data/okx_loader.py`
```

**If missing**: Create with template on first session

---

## 🔄 Session Routine (MANDATORY)

### Start-of-Session (Automatic)

**EVERY session MUST start with this sequence**:

1. **Read PROJECT_RULES.md**
   ```python
   from pathlib import Path

   project_root = Path.cwd()  # Or specified project dir
   rules_file = project_root / "PROJECT_RULES.md"

   if rules_file.exists():
       rules = rules_file.read_text()
       # Parse autonomy level, safety boundaries, etc.
   else:
       # Use global rules only
       print("ℹ️ No PROJECT_RULES.md, using global rules")
   ```

2. **Read STATE.md**
   ```python
   state_file = project_root / "STATE.md"

   if state_file.exists():
       state = state_file.read_text()
       # Parse objective, done, in-progress, next
   else:
       # Create from template
       print("ℹ️ No STATE.md, creating from template")
       create_state_template(state_file)
   ```

3. **Pick 1 next item**
   - From STATE.md "Next" section
   - **Single-effect experiment** (Phase 1 rule)
   - User can override

4. **Create experiment folder** (if experiment)
   ```python
   from datetime import datetime

   exp_name = datetime.now().strftime("%Y-%m-%d_%H-%M") + "_short_desc"
   exp_dir = project_root / "experiments" / exp_name

   for subdir in ["code", "results", "logs"]:
       (exp_dir / subdir).mkdir(parents=True, exist_ok=True)
   ```

### End-of-Session (Mandatory)

**EVERY session MUST end with this sequence**:

1. **Save artifacts to disk**
   - `results/trades.csv`
   - `results/positions.csv`
   - `results/nav.csv`
   - `results/metrics.json`
   - `results/reconciliation.csv`

2. **Write summary.md**
   ```markdown
   # Experiment Summary

   **Date**: 2025-12-25
   **Experiment**: 2025-12-25_16-30_mispricing_filter

   ## Decision

   - Deploy / Shelve / Discard

   ## Key Metrics

   | Metric | Value |
   |--------|-------|
   | Sharpe | 2.1   |
   | MDD    | -8.5% |
   | Trades | 127   |

   ## Next Steps

   - Validate on bear market (2022-Q2)
   ```

3. **Update STATE.md**
   ```python
   # Move "In Progress" → "Done"
   # Add new "Next" items if discovered
   # Update assumptions if changed
   ```

4. **Archive if needed**
   ```bash
   # If experiment failed/discarded
   mv experiments/2025-12-25_16-30_failed experiments/_archive/
   ```

---

## 🧪 Experiment Discipline (Phase 1 → Phase 2)

### Phase 1: Single Effect (MANDATORY FIRST)

**Rule**: 1 experiment = 1 hypothesis = 1 variable change

**Example**:

```markdown
## Experiment Card

**Hypothesis**: IV 과대평가 필터를 15%로 올리면 거짓 신호 감소

**Isolated Variable**: IV filter threshold (10% → 15%)

**Control Group**: 현재 운영중인 10% 설정 (모든 다른 파라미터 동일)

**Expected Signal**: Sharpe +0.3 이상, 거래 빈도 -20% 이내

**Failure Condition**: Sharpe 변화 없거나, 거래 빈도 -50% 이상
```

**Output**:

```markdown
## Results

| Variant | Sharpe | MDD | Trades | Variable |
|---------|--------|-----|--------|----------|
| Control (10%) | 1.85 | -12.3% | 127 | baseline |
| Experiment (15%) | 2.12 | -10.1% | 98 | IV filter: 10→15% |

## Isolated Effect

- Sharpe: +0.27 (+14.6%)
- MDD: +2.2% (improved)
- Trades: -29 (-22.8%, signal quality ↑)

## Conclusion

✅ Phase 1 complete. IV filter 강화 효과 확인.
```

### Phase 2: Joint Effect (ONLY AFTER Phase 1)

**Rule**: Allowed ONLY after Phase 1 is complete and individual effects confirmed.

**Example**:

```markdown
## Phase 1 Results (Required before Phase 2)

- Exp A: IV filter 10% → 15% (Sharpe +0.3) ✅
- Exp B: TTE filter 3d → 5d (Sharpe +0.1) ✅
- Exp C: Regime Bull → Bear (Sharpe -0.2) ❌ (rejected)

## Phase 2: Joint Effect

**Hypothesis**: IV=15% + TTE=5d 결합 시 interaction 효과

**Variables**: IV filter + TTE filter (A, B 결합)

**Expected**: Sharpe(A+B) ≈ Sharpe(A) + Sharpe(B) if independent

**Results**:

| Variant | Sharpe | Expected | Interaction |
|---------|--------|----------|-------------|
| A only  | 2.15   | -        | -           |
| B only  | 1.95   | -        | -           |
| A+B     | 2.50   | 2.35     | +0.15 (synergy) ✅ |

## Conclusion

✅ Positive interaction detected. A+B > A + B (synergy).
```

### Enforcement

**Agent MUST**:
- ❌ Reject Phase 2 experiments if Phase 1 not complete
- ❌ Reject multi-variable changes without justification
- ✅ Ask user to break down into Phase 1 experiments first

**Example**:

```
User: "IV 필터 15%로 올리고 TTE 5d로 바꿔서 테스트해봐"

Agent: "⚠️ 이 요청은 2개 변수 동시 변경입니다 (Phase 2).
        Phase 1 (단일 효과 측정)을 먼저 진행해야 합니다.

        제안:
        1. Exp A: IV filter 10% → 15% (TTE 고정)
        2. Exp B: TTE 3d → 5d (IV 고정)
        3. Exp C: IV=15% + TTE=5d (Phase 2, A+B 결합)

        Exp A부터 시작할까요?"
```

---

## 🛠️ Automation Scripts (Optional)

**Location**: `~/knowledge/scripts/` (formerly `/home/sqr/_meta/`)

### bootstrap_project_state.py

**Usage**:
```bash
python3 ~/knowledge/scripts/bootstrap_project_state.py ~/options_trading
```

**Function**: Creates `PROJECT_RULES.md` and `STATE.md` if missing (non-destructive)

### project_guard.py

**Usage**:
```bash
python3 ~/knowledge/scripts/project_guard.py ~/options_trading
```

**Function**: Creates standard folders (`src/`, `scratch/`, `experiments/`, `_archive/`)

### preflight_backtest.py

**Usage**:
```bash
python3 ~/knowledge/scripts/preflight_backtest.py ~/experiments/2025-12-25_exp/
```

**Function**: Validates required artifacts + MTM/metrics sanity, writes `results/preflight_report.json`

**Note**: Scripts are optional. Agent can perform these tasks without scripts.

---

## 🔍 STATE.md Parsing Rules

**Agent MUST parse STATE.md and extract**:

1. **Current Objective**:
   - What is the main goal?
   - Use this to prioritize next actions

2. **Done**:
   - What has been completed?
   - Don't repeat completed tasks

3. **In Progress**:
   - What is currently being worked on?
   - Resume if interrupted

4. **Next** (1-3 items):
   - Pick the first item (highest priority)
   - Check if it's Phase 1 (single effect)
   - If user requests something else, update priorities

5. **Assumptions**:
   - What assumptions were made?
   - Validate if necessary

---

## 📋 Checklist: Proper State Management

- [ ] Read PROJECT_RULES.md (or use global rules if missing)
- [ ] Read STATE.md (or create from template if missing)
- [ ] Pick 1 next item (single-effect, Phase 1)
- [ ] Create experiment folder (YYYY-MM-DD_HH-MM_desc)
- [ ] Run experiment
- [ ] Save artifacts (trades/positions/nav/metrics/reconciliation)
- [ ] Write summary.md (decision: deploy/shelve/discard)
- [ ] Update STATE.md (done/in-progress/next)
- [ ] Archive if discarded

---

## 🚫 Anti-Patterns

### ❌ Don't Skip Reading STATE.md

**Bad**:
```
Agent: "어떤 작업을 할까요?"
(STATE.md에 "Next: Backtest mispricing filter" 명시되어 있는데 읽지 않음)
```

**Good**:
```
Agent: [Reads STATE.md]
      "STATE.md에 다음 작업이 명시되어 있습니다:
       1. Backtest mispricing filter (Phase 1)

       이 작업을 진행할까요? 아니면 다른 작업을 우선하시겠습니까?"
```

### ❌ Don't Forget to Update STATE.md

**Bad**:
```
Agent: [Completes experiment, writes summary.md]
       [Doesn't update STATE.md]
(Next session: Agent doesn't know what was done)
```

**Good**:
```
Agent: [Completes experiment]
       [Updates STATE.md:
        - Move "Backtest mispricing filter" to "Done"
        - Add "Validate on bear market" to "Next"
       ]
```

### ❌ Don't Violate Phase 1 → Phase 2

**Bad**:
```
User: "IV + TTE 동시에 바꿔서 테스트"
Agent: [Runs experiment with both changes]
(Result: 무엇이 효과를 냈는지 알 수 없음)
```

**Good**:
```
User: "IV + TTE 동시에 바꿔서 테스트"
Agent: "⚠️ Phase 2 실험입니다. Phase 1 먼저 진행해야 합니다.

        제안:
        1. Exp A: IV only
        2. Exp B: TTE only
        3. Exp C: IV + TTE (Phase 2)

        Exp A부터 시작할까요?"
```

---

**Last Updated**: 2025-12-25
**Version**: 1.0
