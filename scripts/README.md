# Server State Management (_meta)

**Goal**: This server hosts many projects. The agent is stateless. Make projects self-describing via files.

## Core Idea

- **Global knowledge** lives in `~/knowledge/` (cross-project, stable).
- **Per-project state** lives in each project root:
  - `PROJECT_RULES.md` (rules & boundaries; "read-first")
  - `STATE.md` (current objective, progress, next actions; "memory")

## What’s in this folder

- `PROJECT_INDEX.md`: registry of projects on this server (searchable).
- `templates/PROJECT_RULES.md`: minimal template.
- `templates/STATE.md`: minimal template.
- `bootstrap_project_state.py`: safe initializer (creates missing files only).

## Usage

Initialize a project (non-destructive: creates files only if missing):

```bash
python3 /home/sqr/_meta/bootstrap_project_state.py /home/sqr/options_trading
python3 /home/sqr/_meta/bootstrap_project_state.py /home/sqr/grid_backtester_v4
```

Then, when starting work:

> “Read `PROJECT_RULES.md` and `STATE.md` first, then continue.”


