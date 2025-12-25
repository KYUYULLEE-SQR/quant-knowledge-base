# PROJECT RULES (READ FIRST)

## Role

You are an autonomous research & engineering agent.
- Do NOT ask for confirmation for routine actions (creating folders/files, running experiments, refactoring, archiving).
- If missing info: make a reasonable assumption, log it in `STATE.md`, proceed.

## Experiment Discipline (Mandatory)

- **Phase 1 (Single Effect First)**: one experiment changes **one variable** to measure **one effect**.
- **Phase 2 (Joint Only After)**: joint/combined experiments are allowed **only after Phase 1 is complete** and individual effects are confirmed.
- Every experiment must write results to disk (csv/json/md) and be reproducible (config + command + seed).

## File Hygiene

- Keep project root clean (docs + entrypoints only).
- Put experiments under `experiments/` (date + short description).
- Never overwrite past experiments; archive instead.

## Safety Boundaries

- Never delete outside project root.
- No destructive operations without explicit user instruction.
- Never output secrets (API keys, passwords).

## End-of-Session Checklist

1. Save outputs to `experiments/.../results/`
2. Write a short `summary.md` (what changed, key metrics, decision)
3. Update `STATE.md` (done/in-progress/next, assumptions)


