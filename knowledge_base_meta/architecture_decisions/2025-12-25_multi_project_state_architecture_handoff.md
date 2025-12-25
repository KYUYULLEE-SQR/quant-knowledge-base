# Multi-Project State Management Architecture (Handoff)

**Date**: 2025-12-25  
**Participants**: User, Cursor Agent (GPT-5.2)  
**Context**: This server runs multiple concurrent projects (options / futures HFT / shitcoin / etc). The recurring pain is repetition: experiments become messy (files scattered), repeated reminders about experiment discipline, reusable vs scratch separation, data integrity, Mark-to-Market NAV, and metric sanity.

---

## Key Decisions

1. **Treat the agent as stateless. Persist state in files.**
   - Knowledge is global (Git-managed): `~/knowledge/`
   - Project memory is local: `PROJECT_RULES.md` + `STATE.md` in each project root

2. **Experiment discipline is enforced as a sequence:**
   - Phase 1: single-effect (one variable at a time)
   - Phase 2: joint-effect only after Phase 1 completes

3. **Stop teaching repeatedly; make the system “read-first”:**
   - Anchor rules require reading `PROJECT_RULES.md` and `STATE.md` before work starts
   - If missing, create them non-destructively

---

## What was implemented (Concrete Artifacts)

### A) Claude anchor rule strengthened

- Updated: `~/.claude/rules/06_behavioral_rules.md`
  - CORE LOOP now includes: *“Phase 1 single-effect first → Phase 2 joint only after Phase 1 is complete”*
  - Added “Project State Protocol”: read/create `PROJECT_RULES.md` and `STATE.md` per project

### B) Server-wide meta layer

Created under `/home/sqr/_meta/`:

- `README.md` — describes the architecture
- `PROJECT_INDEX.md` — registry template for projects
- `templates/PROJECT_RULES.md` — per-project rules template
- `templates/STATE.md` — per-project state template
- `bootstrap_project_state.py` — creates `PROJECT_RULES.md` and `STATE.md` if missing (atomic write, non-destructive)
- `project_guard.py` — creates standard folders + `.gitignore` patterns + `experiments/README.md` stub (non-destructive)
- `preflight_backtest.py` — checks required backtest artifacts + MTM/metrics sanity; writes `results/preflight_report.json`

### C) Knowledge (Git-managed) SOP

Added: `~/knowledge/experiments/agent_operating_procedure.md`
- Repeated workflow captured as SOP:
  - folder discipline (experiments under `experiments/`)
  - reusable vs throwaway (`src/` vs `scratch/`)
  - mandatory backtest artifacts (trades/positions/nav/metrics/reconciliation)
  - preflight checks (integrity/MTM/metrics sanity)

Also indexed in `~/knowledge/README.md`.

---

## Verified executions (What actually ran)

### 1) Bootstrap project state

- `python3 /home/sqr/_meta/bootstrap_project_state.py /home/sqr/options_trading`
  - Created: `/home/sqr/options_trading/PROJECT_RULES.md`
  - Created: `/home/sqr/options_trading/STATE.md`

- `python3 /home/sqr/_meta/bootstrap_project_state.py /home/sqr/grid_backtester_v4`
  - Created: `/home/sqr/grid_backtester_v4/PROJECT_RULES.md`
  - Created: `/home/sqr/grid_backtester_v4/STATE.md`

### 2) Project guard (structure hygiene)

- `python3 /home/sqr/_meta/project_guard.py /home/sqr/options_trading`
  - Created `src/`, `scratch/`, `experiments/_archive/`
  - Updated `.gitignore`
  - Created `experiments/README.md`

- `python3 /home/sqr/_meta/project_guard.py /home/sqr/high_frequency_trading`
  - Created `src/`, `scratch/`, `experiments/`, `experiments/_archive/`
  - Updated `.gitignore`
  - Created `experiments/README.md`

- `python3 /home/sqr/_meta/project_guard.py /home/sqr/shitcoin_trading`
  - Created `src/`, `scratch/`, `docs/`, `experiments/_archive/`
  - Updated `.gitignore`

---

## Current repo status (Important for handoff)

`/home/sqr/knowledge` is a Git repo and currently has **uncommitted changes**:

- Modified: `README.md`
- Modified: `claude_code_rules/rules/06_behavioral_rules.md`
- New: `experiments/agent_operating_procedure.md`
- New: this handoff doc (you are reading it)

---

## Recommended operating pattern (for next agent)

### Start-of-work (per project)

1. Read `<project>/PROJECT_RULES.md`
2. Read `<project>/STATE.md`
3. Create a new experiment folder under `<project>/experiments/YYYY-MM-DD_short_desc/`
4. Ensure artifacts are written to `<experiment>/results/`
5. Run preflight: `python3 /home/sqr/_meta/preflight_backtest.py <experiment_dir>`

### End-of-session

1. Write `results/summary.md` (decision: deploy/shelve/discard)
2. Update `<project>/STATE.md` (done/in-progress/next + assumptions)
3. Archive unused scratch outputs if needed

---

## Next Steps (High ROI)

1. **Commit & push knowledge changes** (so other machines/agents share SOP)
2. Add a simple server index updater (optional):
   - scan `/home/sqr/*` for `PROJECT_RULES.md`/`STATE.md`
   - update `/home/sqr/_meta/PROJECT_INDEX.md`
3. Extend `preflight_backtest.py` with optional project adapters:
   - project-specific reconciliation hooks (cash/position conservation)

---

## References

- `~/knowledge/experiments/methodology.md`
- `~/knowledge/experiments/file_organization_policy.md`
- `~/knowledge/experiments/backtesting_nav_policy.md`
- `~/knowledge/experiments/agent_operating_procedure.md`
- `/home/sqr/_meta/README.md`

