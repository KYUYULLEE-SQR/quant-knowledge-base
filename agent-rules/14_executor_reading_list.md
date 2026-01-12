# Executor Agent Reading List (범용)

**Last Updated**: 2025-12-29
**Purpose**: 어느 프로젝트든 Executor가 시작할 때 읽을 것 (반복 최소화)
**Priority**: ⭐⭐⭐ MANDATORY for all executors

---

## 🎯 Problem: "뭐 읽어야 하나요?" 매번 물어봄

### 이전 (비효율)
```
User: "이 프로젝트 실험 좀 돌려줘"
Executor: "뭐 읽으면 되나요?"
User: "STATE.md, ROADMAP.md, 그리고..."  (반복)
```

### 이후 (표준화)
```
User: "이 프로젝트 실험 좀 돌려줘"
Executor: [자동으로 읽기 순서 따름]
  1. EXECUTOR_START.md (5분) ← 필수
  2. STATE.md (1분) ← 필수
  3. [프로젝트 폴더 체크]
  4. 시작
```

---

## 📚 Standard Reading Order (모든 프로젝트 공통)

### Level 0: Pre-Check (5초)

**확인 사항**:
```bash
# 1. 현재 위치 확인
pwd

# 2. 프로젝트 루트인가?
ls -la | grep -E "(STATE.md|README.md|EXECUTOR_START.md)"

# 3. Git repo인가?
git status 2>/dev/null && echo "✅ Git repo" || echo "⚠️ Not a git repo"
```

**Expected**: 프로젝트 루트에 있어야 함 (`/home/sqr/project_name/`)

---

### Level 1: Quick Start (5분) ⭐ MUST READ

**파일**: `EXECUTOR_START.md` (있으면) 또는 `README.md` (없으면)

**읽는 이유**:
- 즉시 실행 가능한 명령어 (1-5줄)
- 필수 3가지만 (핵심 개념)
- 금지 3가지 (흔한 실수)

**읽는 방법**:
```bash
# 1. 파일 존재 확인
if [ -f "EXECUTOR_START.md" ]; then
  cat EXECUTOR_START.md
elif [ -f "README.md" ]; then
  cat README.md
else
  echo "⚠️ No quick start guide. Read STATE.md instead."
  cat STATE.md
fi
```

**Expected output**:
- ⚡ 즉시 실행 (명령어)
- 📋 필수 3가지 (핵심)
- 🚫 금지 3가지 (함정)

---

### Level 2: Context (1-2분) ⭐ MUST READ

**파일**: `STATE.md`

**읽는 이유**:
- 현재 프로젝트 목표 (Objective)
- 완료된 것 (Done)
- 진행 중인 것 (In Progress) ← 충돌 방지
- 다음에 할 것 (Next)

**읽는 방법**:
```bash
cat STATE.md

# 주요 섹션만 빠르게
grep -A 5 "## Objective" STATE.md
grep -A 5 "## In Progress" STATE.md
grep -A 5 "## Next" STATE.md
```

**Expected output**:
- Objective: "Test grid trading on 608 symbols"
- In Progress: "timeframe_analysis (다른 에이전트 작업 중)" ← 건드리지 마
- Next: "550 symbol sweep (Phase 2)"

---

### Level 3: Conflict Check (30초) ⭐ MUST DO

**확인 사항**:
- 다른 에이전트가 실험 진행 중인가?
- 내가 할 실험이 이미 완료되었나?

**명령어**:
```bash
# 1. Active experiments (.LOCK 파일)
find experiments -name ".LOCK" -type f 2>/dev/null

# 2. 진행 중 실험 (REGISTRY.md)
if [ -f "experiments/REGISTRY.md" ]; then
  grep "🔄" experiments/REGISTRY.md
fi

# 3. STATE.md "In Progress" 섹션
grep -A 10 "## In Progress" STATE.md
```

**Expected**:
- `.LOCK` 파일 있으면: 다른 에이전트 작업 중 → **충돌 방지**
- `🔄 Running` 있으면: 같은 실험 진행 중 → **중복 방지**

---

### Level 4: Full Guide (Optional, 10-15분)

**파일**: `AGENT_GUIDE.md` (있으면)

**읽는 시기**:
- 처음 프로젝트 참여할 때
- EXECUTOR_START.md만으로 부족할 때
- 복잡한 프로젝트 (옵션 전략, ML 등)

**읽는 방법**:
```bash
# 존재 확인
if [ -f "AGENT_GUIDE.md" ]; then
  cat AGENT_GUIDE.md
else
  echo "⚠️ No full guide. Use docs/ folder"
  ls -la docs/
fi
```

**Expected output**:
- TL;DR (1-2 paragraphs)
- Project structure (폴더 설명)
- Quick start (6 steps)
- Data access (데이터 로딩)
- Validation checklist
- Common pitfalls
- Decision framework

---

## 🚫 What NOT to Read (시간 낭비)

### ❌ Don't Read (바로 시작 시)

**These are for Guide agents, not Executors**:
1. `ROADMAP.md` - 전략 방향 (Guide가 읽음)
2. `PROJECT_MANAGEMENT.md` - 워크플로우 상세 (Guide가 읽음)
3. `CHANGELOG.md` - 버전 히스토리 (Reference only)
4. `MIGRATION_LOG.md` - 데이터 마이그레이션 (Reference only)
5. `docs/*.md` - 상세 문서 (필요할 때만)

**Exception**: Guide agent가 "이거 읽어" 명시하면 읽기

---

## 📋 Reading Checklist (Copy-Paste)

**Before starting any work, check these**:

```bash
#!/bin/bash
# Executor Pre-Flight Check

echo "=== Executor Pre-Flight Check ==="

# 1. Location check
echo "📍 Location: $(pwd)"

# 2. Quick Start guide
if [ -f "EXECUTOR_START.md" ]; then
  echo "✅ EXECUTOR_START.md found (READ THIS FIRST)"
  # head -30 EXECUTOR_START.md
elif [ -f "README.md" ]; then
  echo "✅ README.md found (read this)"
else
  echo "⚠️ No quick start guide"
fi

# 3. STATE.md
if [ -f "STATE.md" ]; then
  echo "✅ STATE.md found (READ THIS SECOND)"
  echo "   Objective: $(grep -A 1 '## Objective' STATE.md | tail -1)"
else
  echo "⚠️ No STATE.md"
fi

# 4. Conflict check
locks=$(find experiments -name ".LOCK" 2>/dev/null | wc -l)
if [ $locks -gt 0 ]; then
  echo "⚠️  $locks active experiments (.LOCK files found)"
  find experiments -name ".LOCK" | xargs -I {} dirname {}
else
  echo "✅ No conflicts (no .LOCK files)"
fi

# 5. Ready
echo ""
echo "🚀 Ready to start"
echo "   Next: Read EXECUTOR_START.md (5 min)"
echo "   Then: Start work"
```

**Usage**:
```bash
bash ~/knowledge/scripts/executor_preflight.sh
```

---

## 🎯 Project-Specific Reading (프로젝트별)

### grid_backtester_v4 (Trading Strategy)

**Reading order**:
1. `EXECUTOR_START.md` (5 min) ⭐
2. `STATE.md` (1 min) ⭐
3. Check `.LOCK` files (30 sec) ⭐
4. `experiments/REGISTRY.md` (skim, 2 min)
5. Start work

**Don't read**:
- `ROADMAP.md` (Guide only)
- `PROJECT_MANAGEMENT.md` (Guide only)
- `docs/DATA_ACCESS_GUIDE.md` (Reference only, 464 lines too long)

### market_data_collector (Data Collection)

**Reading order**:
1. `EXECUTOR_START.md` (5 min) ⭐
2. `STATE.md` (1 min) ⭐
3. Check current collection status (30 sec)
4. Start work

**Don't read**:
- `docs/EXCHANGE_API_GUIDE.md` (Reference only)

### ML Training Project

**Reading order**:
1. `EXECUTOR_START.md` (5 min) ⭐
2. `STATE.md` (1 min) ⭐
3. Check `experiments/REGISTRY.md` (2 min)
4. Review last experiment results (2 min)
5. Start work

**Don't read**:
- `docs/MODEL_ARCHITECTURE.md` (Reference only)

---

## 🤝 Communication with Guide Agent

### When to Ask Guide

**Ask when**:
- EXECUTOR_START.md unclear or contradictory
- Conflict detected (another experiment running)
- Experiment failed unexpectedly
- Results don't make sense

**How to ask**:
```bash
# Create message file
cat > experiments/_messages/$(date +%Y-%m-%d_%H-%M)_executor_to_guide.md << EOF
---
from: executor
to: guide
priority: high
---

# Question: [Subject]

## Context
[What you're trying to do]

## Issue
[What's unclear/wrong]

## Attempted
[What you tried]

## Request
[What you need from Guide]
EOF
```

### When NOT to Ask

**Don't ask**:
- How to run basic Python (`python script.py`)
- How to load data (read EXECUTOR_START.md)
- Where files are (read STATE.md)
- Standard validation (read AGENT_GUIDE.md)

**Instead**: Read the docs first, then ask if still unclear

---

## 📊 Summary Table

| File | When | Time | Must Read? | Purpose |
|------|------|------|------------|---------|
| `EXECUTOR_START.md` | 시작 시 | 5 min | ⭐ YES | 즉시 실행 가능 |
| `STATE.md` | 시작 시 | 1 min | ⭐ YES | 현재 상태 |
| `.LOCK` files | 시작 시 | 30 sec | ⭐ YES | 충돌 방지 |
| `AGENT_GUIDE.md` | 필요 시 | 10-15 min | Optional | 전체 가이드 |
| `REGISTRY.md` | 필요 시 | 2 min | Optional | 과거 실험 |
| `ROADMAP.md` | Never | - | ❌ NO | Guide only |
| `docs/*.md` | 필요 시 | Varies | Optional | Reference |

---

## 🎓 Examples

### Example 1: Brand New Executor (처음 프로젝트 참여)

**Scenario**: 프로젝트를 처음 봄

**Reading**:
```bash
# 1. Quick start (5 min)
cat EXECUTOR_START.md

# 2. Current state (1 min)
cat STATE.md

# 3. Conflict check (30 sec)
find experiments -name ".LOCK"

# 4. Past experiments (skim, 2 min)
cat experiments/REGISTRY.md | head -50

# Total: 8-9 minutes
```

**Output**: "Ready to start. Objective: Test 608 symbols. No conflicts."

### Example 2: Returning Executor (같은 프로젝트 다시 참여)

**Scenario**: 며칠 전에도 작업했음

**Reading**:
```bash
# 1. What changed? (1 min)
cat STATE.md
git log --oneline -10  # Recent commits

# 2. Conflict check (30 sec)
find experiments -name ".LOCK"

# Total: 1-2 minutes
```

**Output**: "Phase 2 started. No conflicts. Resume work."

### Example 3: Urgent Fix (에러 수정)

**Scenario**: 실험 중 에러 발생, 빠른 수정 필요

**Reading**:
```bash
# 1. Error context (1 min)
tail -50 experiments/*/logs/errors.txt

# 2. No other reading needed
# Fix and restart

# Total: 1 minute
```

---

## 🚨 Red Flags (읽다가 이거 보이면 중단)

### 🚨 Red Flag 1: "This document is outdated"

**Action**: Ask Guide for updated version

### 🚨 Red Flag 2: EXECUTOR_START.md has "TODO: ..."

**Action**: This project not set up yet. Ask Guide to customize.

### 🚨 Red Flag 3: STATE.md says "🔴 ARCHIVED"

**Action**: This project is dead. Don't work on it.

### 🚨 Red Flag 4: Multiple .LOCK files (>2)

**Action**: Something wrong. Ask Guide.

---

**Last Updated**: 2025-12-29
**Version**: 1.0
**Based on**: grid_backtester_v4 (multi-agent success case)
