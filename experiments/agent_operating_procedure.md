# Agent Operating Procedure (SOP) — Multi-Project Research Server

**Last Updated**: 2025-12-25  
**Importance**: ⭐⭐⭐ Critical — 반복 지시 제거, 품질/정합성 강제  

---

## 🎯 Problem (What hurts)

This server runs multiple concurrent tracks (options / futures HFT / shitcoin / etc).
The agent is **stateless**, but the user expects **stateful continuity**.

**Failure modes (repeated):**
- Files scattered in root, no experiment folders
- No separation of throwaway scripts vs reusable code
- Data integrity issues not detected early
- Backtest outputs inconsistent (trades/positions/nav mismatch)
- Metrics wrong because NAV is not Mark-to-Market (MDD=0, Sharpe inflated)
- Same “please organize / validate / reconcile / MTM / fix metrics” instructions every session

---

## ✅ Core Solution (State Architecture)

### Two-layer state (MANDATORY)

1. **Global Knowledge**: `~/knowledge/` (cross-project truth)
2. **Project-local Memory** (per project root):
   - `PROJECT_RULES.md` = rules, boundaries, autonomy policy
   - `STATE.md` = objective, done, in-progress, next, assumptions, references

**Rule**: Start-of-work = read `PROJECT_RULES.md` + `STATE.md`.  
If missing, create them (non-destructive) before doing anything else.

---

## 🧪 Experiment Discipline (MANDATORY Sequence)

### Phase 1: Single Effect (Individual Effects)

- 1 experiment = 1 hypothesis = 1 variable change
- Control group fixed (baseline clearly defined)
- Output must isolate effect (ΔSharpe, ΔMDD, ΔTrades, etc.)

### Phase 2: Joint Effect (Only after Phase 1)

- Allowed only after Phase 1 is complete
- Combine only variables with positive individual effect
- Must report interaction (synergy / interference)

---

## 🗂️ File & Code Hygiene (Project Standard)

### Project root: keep clean

Project root should not accumulate `test.py`, `final_final.py`, random notebooks.

### Standard folders (recommended)

```
project/
├─ PROJECT_RULES.md
├─ STATE.md
├─ src/            # reusable library code
├─ scratch/        # one-off scripts, prototypes (disposable)
├─ experiments/    # all experiments live here
│  ├─ _archive/
│  └─ YYYY-MM-DD_short_desc/
│     ├─ README.md
│     ├─ config.yaml
│     ├─ code/
│     ├─ results/
│     └─ logs/
└─ docs/
```

### Reusable vs Throwaway (hard rule)

- `src/`: modules you expect to reuse across experiments/projects  
- `scratch/`: fast iteration scripts; allowed to be messy; must not become dependencies  
- If `scratch/` code becomes valuable → **promote** into `src/` with minimal cleanup + docstring + tests if possible

---

## 📦 Standard Artifacts (Backtest Integrity)

Every backtest run must produce (in `results/`):

1. `trades.csv` — trade-by-trade with before/after state
2. `positions.csv` — position snapshot per timestep
3. `nav.csv` — Mark-to-Market NAV time series (not entry/exit only)
4. `metrics.json` — standard metrics (Sharpe, MDD, Vol, CAGR, turnover, etc.)
5. `reconciliation.csv` — integrity test results (pass/fail + diffs)

**No artifact → no result → no reporting.**

---

## 🔎 Preflight Checks (Run every time)

Before trusting results, run:

### A) Data sanity

- Missing/NaN rate per key columns
- Time ordering (monotonic timestamps)
- Duplicate timestamps
- Units sanity (PA vs BS, BTC vs USD)

### B) Integrity reconciliation

- Position continuity: position changes == trades exactly
- Cash conservation: cash flow matches trades + fees
- No orphan trades: every close has open
- PnL attribution sums to total PnL

### C) MTM sanity

- NAV has enough points (not only entry/exit)
- MDD not artificially 0 due to sparse NAV
- Drawdown curve exists

### D) Metric sanity

- Annualization convention consistent (365-day on crypto)
- Sharpe range sanity check (e.g., Sharpe > 10 ⇒ suspicious)
- Return/vol consistency (vol=0 with non-zero returns ⇒ bug)

---

## 🧰 Automation (Local, common across projects)

This server provides a common meta-layer:

- `/home/sqr/_meta/bootstrap_project_state.py`
  - Creates `PROJECT_RULES.md` and `STATE.md` if missing (non-destructive)
- `/home/sqr/_meta/project_guard.py`
  - Creates standard folders (`src/`, `scratch/`, `experiments/`, `_archive/`) if missing
- `/home/sqr/_meta/preflight_backtest.py`
  - Validates required artifacts + basic MTM/metrics sanity and writes a report file

---

## ✅ Session Routine (Zero-repeat workflow)

### Start-of-session

1. Read `PROJECT_RULES.md`
2. Read `STATE.md`
3. Pick **1 next item** (single-effect experiment or bugfix)
4. Create new experiment folder (never overwrite)

### End-of-session

1. Save artifacts to disk
2. Write `results/summary.md` (decision: deploy/shelve/discard)
3. Update `STATE.md`
4. Archive unused scratch outputs if needed

---

## 📚 References

- `~/knowledge/experiments/methodology.md`
- `~/knowledge/experiments/file_organization_policy.md`
- `~/knowledge/experiments/backtesting_nav_policy.md`
- `~/knowledge/claude_code_rules/rules/10_backtesting_integrity.md`


