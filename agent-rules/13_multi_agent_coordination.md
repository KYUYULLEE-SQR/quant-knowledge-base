# Multi-Agent Coordination Protocol

**Last Updated**: 2025-12-29
**Purpose**: Enable multiple agents to work on same project without conflicts
**Priority**: ⭐⭐⭐ MANDATORY when multiple agents active

---

## 🎯 Problem Statement

**Scenario**:
- Agent A: Running 608 symbol backtests (5+ hours)
- Agent B: Analyzing results, writing documentation, planning next steps

**Challenges**:
1. File conflicts (both writing to same file)
2. Resource contention (CPU/memory/database)
3. Result inconsistency (A generates data while B analyzes)
4. Confusion (who did what?)

**Goal**: Enable pair programming - one executes, one guides.

---

## 🤝 Coordination Patterns

### Pattern 1: Executor + Guide (Recommended for Experiments)

**Roles**:
- **Executor Agent**: Runs experiments, generates data, tests hypotheses
- **Guide Agent**: Plans, validates, documents, reviews results

**Protocol**:

#### Executor Responsibilities
1. **Before starting**:
   - Create experiment folder with unique timestamp
   - Create `.LOCK` file (mark as in-progress)
   - Update REGISTRY.md: status = "🔄 Running"
   - Update STATE.md: "In Progress" section

2. **During execution**:
   - Write to experiment folder only (isolated)
   - Log progress to `logs/progress.txt`
   - Save intermediate results every N iterations
   - Don't modify shared files (README, STATE, ROADMAP)

3. **After completion**:
   - Write results/summary.md
   - Write results/metrics.json
   - Remove `.LOCK`, create `.DONE`
   - Update REGISTRY.md: status = "✅ Complete"
   - Update STATE.md: move to "Done" section

4. **If interrupted**:
   - Keep `.LOCK` file (marks incomplete)
   - Write `logs/interrupted.txt` with last state
   - Another agent can resume or clean up

#### Guide Responsibilities
1. **Before Executor starts**:
   - Read STATE.md, REGISTRY.md
   - Create experiment plan (README template)
   - Write experiment prompt (guide for Executor)
   - Set up validation checklists

2. **While Executor runs**:
   - Monitor progress (read `logs/progress.txt`)
   - Check for errors (read `logs/errors.txt`)
   - Prepare analysis scripts
   - Update documentation (not in experiment folder)
   - Plan next experiments

3. **After Executor completes**:
   - Validate results (run validation_report.py)
   - Aggregate findings (if multiple experiments)
   - Update strategic docs (ROADMAP, PROJECT_MANAGEMENT)
   - Propose next experiments

4. **If Executor fails**:
   - Check `.LOCK` file timestamp (hung?)
   - Read `logs/` for errors
   - Create issue report
   - Suggest fixes

### Pattern 2: Parallel Executors (Avoid if Possible)

**Use case**: Multiple independent experiments

**Protocol**:
- Each agent creates separate experiment folder
- Different symbols/parameters (no overlap)
- Coordinate via REGISTRY.md
- Update STATE.md one at a time (atomic writes)

**Rules**:
- ❌ Don't run same experiment twice
- ❌ Don't modify each other's folders
- ✅ Use unique folder names (timestamp + agent_id)
- ✅ Check REGISTRY.md before starting

---

## 🔐 File Locking Protocol

### Experiment-Level Locking

**Structure**:
```
experiments/YYYY-MM-DD_HH-MM_name/
├── .LOCK           # Marks in-progress (created at start)
├── .DONE           # Marks completed (created at end)
├── .ERROR          # Marks failed (created on error)
└── .AGENT_ID       # Which agent owns this
```

**Lock File Format**:
```bash
# .LOCK file content
AGENT_ID=executor_01
START_TIME=2025-12-29T15:30:00
PID=12345
STATUS=running
PROGRESS=127/608 symbols
```

**Checking Lock Status**:
```python
from pathlib import Path
from datetime import datetime, timedelta

def check_experiment_status(exp_dir):
    """Check if experiment is locked, done, or stale."""
    lock_file = exp_dir / '.LOCK'
    done_file = exp_dir / '.DONE'
    error_file = exp_dir / '.ERROR'

    if done_file.exists():
        return 'completed'
    elif error_file.exists():
        return 'failed'
    elif lock_file.exists():
        # Check if stale (>24 hours old)
        lock_time = datetime.fromtimestamp(lock_file.stat().st_mtime)
        if datetime.now() - lock_time > timedelta(hours=24):
            return 'stale'
        return 'running'
    else:
        return 'not_started'

# Usage
status = check_experiment_status(Path('experiments/2025-12-29_15-30_sweep'))
if status == 'running':
    print("⚠️ Experiment in progress. Don't interfere.")
elif status == 'stale':
    print("⚠️ Experiment stale (>24h). May be hung. Check logs.")
```

### Registry-Level Coordination

**Single source of truth**: `experiments/REGISTRY.md`

**Update Protocol** (Atomic):
```python
import fcntl
import time

def update_registry(exp_name, status, metrics):
    """Thread-safe registry update."""
    registry_file = Path('experiments/REGISTRY.md')

    # Acquire lock
    with open(registry_file, 'a') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)  # Exclusive lock

        # Read current content
        content = registry_file.read_text()

        # Check if already exists
        if exp_name in content:
            # Update existing row (replace)
            # ... (update logic)
        else:
            # Append new row
            new_row = f"| {date} | {exp_name} | {status} | {metrics} |\n"
            f.write(new_row)

        # Release lock (automatic on close)

    time.sleep(0.1)  # Small delay to avoid race conditions
```

---

## 📊 Progress Monitoring

### Real-Time Progress (Executor → Guide)

**Executor writes**:
```python
# experiments/2025-12-29_15-30_sweep/logs/progress.txt
# Updated every 10 symbols

import json
from datetime import datetime

def update_progress(symbol_idx, total_symbols, current_symbol, sharpe):
    """Write progress for Guide to monitor."""
    progress = {
        'timestamp': datetime.now().isoformat(),
        'progress': f"{symbol_idx}/{total_symbols}",
        'percent': f"{symbol_idx/total_symbols*100:.1f}%",
        'current_symbol': current_symbol,
        'sharpe': sharpe,
        'eta_minutes': (total_symbols - symbol_idx) * 0.5  # Rough estimate
    }

    with open('logs/progress.txt', 'a') as f:
        f.write(json.dumps(progress) + '\n')

# Usage in sweep loop
for i, symbol in enumerate(symbols, 1):
    result = backtest(symbol)
    update_progress(i, len(symbols), symbol, result.sharpe)
```

**Guide reads**:
```python
# Check progress without blocking
def check_sweep_progress(exp_dir):
    """Monitor ongoing sweep."""
    progress_file = exp_dir / 'logs' / 'progress.txt'

    if not progress_file.exists():
        return "Not started or no progress logged"

    # Read last line (most recent update)
    with open(progress_file) as f:
        lines = f.readlines()
        if not lines:
            return "No progress yet"

        last_update = json.loads(lines[-1])
        return f"{last_update['progress']} ({last_update['percent']}), ETA: {last_update['eta_minutes']:.0f} min"

# Usage
status = check_sweep_progress(Path('experiments/2025-12-29_15-30_sweep'))
print(f"Sweep progress: {status}")
```

---

## 🚨 Conflict Resolution

### Scenario 1: Both Agents Modify Same File

**Problem**:
```
Agent A: Updates STATE.md (adds new "In Progress" item)
Agent B: Updates STATE.md (marks item "Done") at same time
→ One update lost
```

**Solution**: Use Git-like conflict markers

```python
def safe_update_state(section, item, new_status):
    """Update STATE.md with conflict detection."""
    state_file = Path('STATE.md')

    # Read current content
    original = state_file.read_text()

    # Make changes
    modified = update_section(original, section, item, new_status)

    # Check if file changed since we read it
    current = state_file.read_text()
    if current != original:
        # Conflict detected
        # Create backup with agent ID
        backup_file = state_file.parent / f'STATE.md.{AGENT_ID}.backup'
        backup_file.write_text(modified)

        raise ConflictError(
            f"STATE.md modified by another agent.\n"
            f"Your changes saved to: {backup_file}\n"
            f"Manually merge conflicts."
        )

    # Write if no conflict
    state_file.write_text(modified)
```

### Scenario 2: Executor Hangs (No Progress)

**Detection**:
```python
def detect_hung_experiment(exp_dir, max_idle_minutes=60):
    """Detect if experiment is hung (no progress)."""
    progress_file = exp_dir / 'logs' / 'progress.txt'

    if not progress_file.exists():
        return False

    # Check last update time
    last_update = datetime.fromtimestamp(progress_file.stat().st_mtime)
    idle_time = datetime.now() - last_update

    if idle_time > timedelta(minutes=max_idle_minutes):
        return True, f"No progress for {idle_time.total_seconds()/60:.0f} minutes"

    return False, "Active"

# Usage
is_hung, msg = detect_hung_experiment(Path('experiments/2025-12-29_15-30_sweep'))
if is_hung:
    print(f"⚠️ Experiment may be hung: {msg}")
    print(f"   Check logs: {exp_dir}/logs/")
    print(f"   Consider: killing process, resuming, or restarting")
```

**Recovery**:
```python
def recover_experiment(exp_dir):
    """Attempt to recover hung experiment."""
    # 1. Check if process still alive
    lock_file = exp_dir / '.LOCK'
    if lock_file.exists():
        agent_id = lock_file.read_text().split('\n')[0].split('=')[1]
        pid = int(lock_file.read_text().split('\n')[2].split('=')[1])

        # Check if PID exists
        import psutil
        if not psutil.pid_exists(pid):
            print(f"Process {pid} dead. Marking as failed.")
            lock_file.rename(exp_dir / '.ERROR')
            (exp_dir / '.ERROR').write_text(f"Process died. Last PID: {pid}")
            return 'failed'

    # 2. Check if resumable
    progress_file = exp_dir / 'logs' / 'progress.txt'
    if progress_file.exists():
        # Count how many symbols completed
        with open(progress_file) as f:
            lines = f.readlines()
            if lines:
                last = json.loads(lines[-1])
                completed = int(last['progress'].split('/')[0])
                print(f"Completed: {completed} symbols")
                print(f"Can resume from symbol {completed+1}")
                return 'resumable'

    return 'unknown'
```

### Scenario 3: Duplicate Experiments

**Prevention**:
```python
def ensure_unique_experiment(exp_name):
    """Ensure no duplicate experiment names."""
    exp_dir = Path(f'experiments/{exp_name}')

    if exp_dir.exists():
        # Check status
        status = check_experiment_status(exp_dir)

        if status == 'running':
            raise ValueError(
                f"Experiment {exp_name} already running.\n"
                f"Choose different name or wait for completion."
            )
        elif status == 'completed':
            # Suggest new name
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M')
            new_name = f"{timestamp}_{exp_name}_v2"
            raise ValueError(
                f"Experiment {exp_name} already completed.\n"
                f"Suggested name: {new_name}"
            )
        elif status == 'stale':
            print(f"⚠️ Found stale experiment {exp_name}. Cleaning up...")
            # Move to failed
            (exp_dir / '.LOCK').rename(exp_dir / '.ERROR')

    # Create experiment folder
    exp_dir.mkdir(parents=True, exist_ok=True)
    for subdir in ['code', 'results', 'logs']:
        (exp_dir / subdir).mkdir(exist_ok=True)

    return exp_dir
```

---

## 📋 Agent Communication Protocol

### Message Format (via files)

**Location**: `experiments/_messages/{timestamp}_{from}_{to}.md`

**Structure**:
```markdown
---
from: guide_agent
to: executor_agent
timestamp: 2025-12-29T15:45:00
priority: high
status: unread
---

# Message: Experiment Parameter Adjustment

## Context
Current experiment: 2025-12-29_15-30_sweep
Progress: 127/608 symbols (20.9%)

## Issue
Top 20 symbols show Sharpe < 1.0 (below threshold).
Possible issue: Grid size too wide for current volatility.

## Suggestion
Consider adjusting grid_size from 30bps to 20bps for remaining symbols.

## Action Requested
- [ ] Acknowledge this message
- [ ] Review first 127 results
- [ ] Decide: continue or adjust parameters
- [ ] Reply with decision

## Response Deadline
Within 1 hour (experiment continuing in meantime)
```

**Reading Messages**:
```python
def check_messages(agent_id):
    """Check for unread messages."""
    msg_dir = Path('experiments/_messages')
    msg_dir.mkdir(exist_ok=True)

    unread = []
    for msg_file in msg_dir.glob(f'*_to_{agent_id}.md'):
        content = msg_file.read_text()
        if 'status: unread' in content:
            unread.append(msg_file)

    return unread

# Usage
messages = check_messages('executor_agent')
if messages:
    print(f"📬 You have {len(messages)} unread messages:")
    for msg in messages:
        print(f"   - {msg.name}")
```

**Replying**:
```python
def send_message(from_agent, to_agent, subject, content, priority='normal'):
    """Send message to another agent."""
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = f"{timestamp}_{from_agent}_to_{to_agent}.md"

    msg_dir = Path('experiments/_messages')
    msg_file = msg_dir / filename

    message = f"""---
from: {from_agent}
to: {to_agent}
timestamp: {datetime.now().isoformat()}
priority: {priority}
status: unread
---

# Message: {subject}

{content}
"""

    msg_file.write_text(message)
    print(f"📤 Message sent: {filename}")

# Usage
send_message(
    from_agent='guide_agent',
    to_agent='executor_agent',
    subject='Parameter Adjustment Suggestion',
    content='Consider reducing grid_size to 20bps...',
    priority='high'
)
```

---

## 🎯 Best Practices

### DO's ✅

1. **Use unique experiment names** (timestamp + description)
2. **Create .LOCK file immediately** when starting
3. **Log progress frequently** (every 10 iterations)
4. **Update REGISTRY.md** at start and end
5. **Write summary.md** before removing .LOCK
6. **Check for active experiments** before starting new one
7. **Monitor other agent's progress** (read logs/progress.txt)
8. **Communicate via messages** for coordination

### DON'Ts ❌

1. ❌ **Don't modify experiment folders with .LOCK**
2. ❌ **Don't skip .LOCK creation** (others won't know you're running)
3. ❌ **Don't update STATE.md simultaneously** (conflicts!)
4. ❌ **Don't assume you're the only agent** (always check)
5. ❌ **Don't delete other agent's work** (even if looks wrong)
6. ❌ **Don't re-run completed experiments** (check .DONE first)
7. ❌ **Don't ignore hung experiments** (check and report)
8. ❌ **Don't batch update REGISTRY.md** (update per experiment)

---

## 🔍 Debugging Multi-Agent Issues

### Issue: "Results don't match between agents"

**Cause**: Using different data or parameters

**Debug**:
```bash
# Compare config files
diff experiments/exp_A/config.yaml experiments/exp_B/config.yaml

# Compare data sources
grep "data_source" experiments/exp_A/logs/*.log
grep "data_source" experiments/exp_B/logs/*.log

# Compare timestamps
ls -lt experiments/exp_A/results/
ls -lt experiments/exp_B/results/
```

### Issue: "REGISTRY.md corrupted"

**Cause**: Both agents wrote simultaneously

**Fix**:
```bash
# Check git history
cd /home/sqr/grid_backtester_v4
git log experiments/REGISTRY.md

# Restore from backup
git checkout HEAD~1 experiments/REGISTRY.md

# Manually merge changes from both agents
```

### Issue: "Experiment hung, no progress"

**Cause**: Process died, infinite loop, or waiting for input

**Debug**:
```bash
# Check lock file age
stat experiments/2025-12-29_15-30_sweep/.LOCK

# Check process
cat experiments/2025-12-29_15-30_sweep/.LOCK | grep PID
ps aux | grep <PID>

# Check last progress
tail -f experiments/2025-12-29_15-30_sweep/logs/progress.txt

# Check for errors
tail -100 experiments/2025-12-29_15-30_sweep/logs/errors.txt
```

---

**Last Updated**: 2025-12-29
**Version**: 1.0
