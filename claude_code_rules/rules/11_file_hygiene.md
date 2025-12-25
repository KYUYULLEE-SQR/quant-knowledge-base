# File Hygiene & Organization Rules

**Purpose**: "정리해" 같은 명령어의 명확한 규칙 정의
**Last Updated**: 2025-12-25
**Priority**: ⭐⭐⭐ MANDATORY

---

## 🎯 Core Principle

**Keep project root clean. Organize by purpose, not by time.**

---

## 📂 Standard Folder Structure (MANDATORY)

Every project MUST have this structure:

```
project/
├── PROJECT_RULES.md       # (Optional) Project-specific overrides
├── STATE.md               # (Optional) Current state/objective/next
├── README.md              # Project overview
├── src/                   # Reusable library code
├── scratch/               # Throwaway scripts (disposable)
├── experiments/           # All experiments live here
│   ├── _archive/          # Completed/discarded experiments
│   └── YYYY-MM-DD_desc/   # Active experiments
│       ├── README.md
│       ├── config.yaml
│       ├── code/
│       ├── results/
│       └── logs/
├── docs/                  # Documentation
├── tests/                 # Unit tests (if applicable)
└── .gitignore
```

---

## 🗂️ src/ vs scratch/ (Critical Distinction)

### src/ (Reusable)

**Purpose**: Library code, reusable across experiments/projects

**Characteristics**:
- ✅ Generalized (parameters, config files)
- ✅ Error handling (try-except, validation)
- ✅ Docstrings (Args, Returns, Examples)
- ✅ Type hints
- ✅ Tests (if possible)
- ❌ No hardcoding (dates, paths, magic numbers)

**When to use**:
- Functions used 3+ times
- Core business logic
- Data loaders, metrics, utilities

**Example**:
```python
# src/data/loader.py
from pathlib import Path
from typing import Optional
import pandas as pd

def load_options_data(
    exchange: str,
    symbol: str,
    start_date: str,
    end_date: str,
    data_dir: Optional[Path] = None
) -> pd.DataFrame:
    """
    Load options data from local cache or database.

    Args:
        exchange: Exchange name (e.g., 'OKX', 'Deribit')
        symbol: Option symbol
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        data_dir: Optional data directory

    Returns:
        DataFrame with options data

    Raises:
        ValueError: If dates invalid or exchange not supported
        FileNotFoundError: If data file doesn't exist
    """
    # Implementation with full error handling
    ...
```

### scratch/ (Throwaway)

**Purpose**: Fast iteration, one-off scripts, prototypes

**Characteristics**:
- ✅ Hardcoding allowed (dates, paths, parameters)
- ✅ Minimal documentation (comments OK)
- ✅ Speed > reusability
- ✅ Can be messy
- ❌ Never become dependencies (don't import from scratch/)

**When to use**:
- Quick analysis (EDA)
- Testing ideas
- One-time data munging
- Debugging

**Example**:
```python
# scratch/quick_test.py
import pandas as pd

# HARDCODED - OK for scratch
START = '2024-10-01'
END = '2024-10-07'

df = pd.read_csv('/home/sqr/data/btc_options.csv')
df = df[(df['date'] >= START) & (df['date'] <= END)]

print(df[df['iv'] > 0.15].groupby('strike')['pnl'].sum())
```

### Migration Rule (scratch/ → src/)

**When to migrate** (3회 재사용 = 즉시 리팩토링):
1. Copy-paste 3번 발견 → 공통 함수 추출
2. Generalize (파라미터화, 에러 처리)
3. Add docstrings + tests
4. Move to `src/`
5. Update scratch/ scripts to import from src/

**Example**:
```bash
# Before: 3 scratch scripts with same logic
scratch/test1.py, scratch/test2.py, scratch/test3.py

# After: Extract to src/
src/metrics/sharpe.py (generalized function)
scratch/test1.py (imports from src/)
```

---

## 🧪 experiments/ Folder Rules

### Naming Convention

**Format**: `YYYY-MM-DD_HH-MM_short_description`

**Examples**:
- ✅ `2025-12-24_15-30_fair_iv_ridge`
- ✅ `2025-12-24_16-45_mispricing_filter`
- ❌ `test`, `final`, `new_version`

### Experiment Lifecycle

1. **Create** (before running):
   ```bash
   mkdir -p experiments/2025-12-24_15-30_fair_iv_ridge/{code,results,logs}
   ```

2. **Active**: Work in experiment folder
   - All code in `code/`
   - All outputs in `results/`
   - All logs in `logs/`

3. **Complete**: Write `results/summary.md`
   - Decision: deploy/shelve/discard
   - Key metrics
   - Next steps

4. **Archive** (if discarded):
   ```bash
   mv experiments/2025-12-24_15-30_failed_idea experiments/_archive/
   ```

### Never Overwrite

- ❌ Don't reuse experiment folders
- ❌ Don't delete old experiments
- ✅ Create new folder for new experiment
- ✅ Archive completed/failed experiments

---

## 🚫 Anti-Patterns (절대 금지)

### 1. ❌ Root Clutter

**Bad**:
```
project/
├── test.py
├── test2.py
├── final.py
├── final_final.py
├── experiment_old.py
├── temp.ipynb
└── backup/
```

**Good**:
```
project/
├── README.md
├── src/
├── scratch/
└── experiments/
```

### 2. ❌ Copy-Paste Hell

**Bad**:
```python
# experiments/exp1/code/experiment.py
def calculate_sharpe(returns):
    return returns.mean() / returns.std() * np.sqrt(365)

# experiments/exp2/code/experiment.py
def calculate_sharpe(returns):  # COPY-PASTE!
    return returns.mean() / returns.std() * np.sqrt(365)
```

**Good**:
```python
# src/metrics/performance.py
def calculate_sharpe_ratio(...):
    """Documented, generalized function"""
    ...

# experiments/exp1/code/experiment.py
from src.metrics.performance import calculate_sharpe_ratio
```

### 3. ❌ Hardcoded Paths in src/

**Bad**:
```python
# src/data/loader.py
def load_data():
    return pd.read_csv('/home/sqr/data/file.csv')  # ❌ Hardcoded
```

**Good**:
```python
# src/data/loader.py
def load_data(data_path: Path) -> pd.DataFrame:
    """Load data from specified path."""
    if not data_path.exists():
        raise FileNotFoundError(f"Data file not found: {data_path}")
    return pd.read_csv(data_path)
```

### 4. ❌ Importing from scratch/

**Bad**:
```python
# experiments/exp1/code/experiment.py
from scratch.quick_test import some_function  # ❌ Never import from scratch
```

**Good**:
```python
# If needed 3+ times → move to src/ first
# src/utils/helpers.py
def some_function(...):
    ...

# experiments/exp1/code/experiment.py
from src.utils.helpers import some_function  # ✅ Import from src/
```

---

## 📋 .gitignore Rules

**Standard .gitignore** (add to every project):

```gitignore
# Python
**/__pycache__/
*.py[cod]
*.pyc
.pytest_cache/
.coverage

# Data (large files)
*.csv
*.parquet
*.h5
*.hdf5
data/

# Logs
logs/
*.log

# Secrets
.env
*.pem
*.key
credentials.json

# OS
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
*.swp

# Experiments (large outputs)
experiments/*/results/*.png
experiments/*/results/*.csv
experiments/*/logs/

# But keep README
!experiments/*/README.md
!experiments/*/results/summary.md
```

---

## 🧹 "정리해" Command Rules

**When user says "정리해", follow these steps**:

### 1. Scan Project Root

```python
# Check for clutter
root_files = [f for f in Path('.').glob('*') if f.is_file()]
clutter = [f for f in root_files if f.suffix in ['.py', '.ipynb'] and f.name != 'README.md']

if clutter:
    print(f"⚠️ Found {len(clutter)} files in root: {clutter}")
    # Suggest moving to scratch/ or experiments/
```

### 2. Create Standard Folders (if missing)

```bash
mkdir -p src scratch experiments experiments/_archive docs tests
```

### 3. Move Files to Correct Locations

**Logic**:
- **Reusable code** → `src/`
- **One-off scripts** → `scratch/`
- **Experiment-related** → `experiments/YYYY-MM-DD_desc/`
- **Documentation** → `docs/`

**Ask user for confirmation** before moving files.

### 4. Update .gitignore

Add standard patterns if missing.

### 5. Archive Old Experiments

Move completed/failed experiments to `experiments/_archive/`.

### 6. Report

```
✅ 정리 완료:
- 3 files moved to scratch/
- 2 files moved to experiments/
- Standard folders created
- .gitignore updated
```

---

## 🔍 File Naming Rules

### Python Scripts

- ✅ `load_data.py`, `calculate_metrics.py` (descriptive)
- ❌ `test.py`, `final.py`, `temp.py` (vague)

### Notebooks

- ✅ `2025-12-24_eda_btc_options.ipynb` (date + description)
- ❌ `Untitled1.ipynb`, `Copy of notebook.ipynb`

### Experiments

- ✅ `2025-12-24_15-30_fair_iv_ridge` (date + time + description)
- ❌ `experiment1`, `new_test`, `final_version`

### Data Files (in data/)

- ✅ `btc_options_2024Q4.parquet` (symbol + period)
- ❌ `data.csv`, `output.parquet`

---

## ✅ Checklist: Clean Project

- [ ] Root has only README.md, PROJECT_RULES.md, STATE.md
- [ ] src/ contains only reusable modules (generalized, documented)
- [ ] scratch/ contains only throwaway scripts (no imports from here)
- [ ] experiments/ organized by date (YYYY-MM-DD_desc)
- [ ] No test.py, final.py, temp.py in root
- [ ] .gitignore present with standard patterns
- [ ] No hardcoded paths in src/
- [ ] No copy-paste code (extracted to src/ if used 3+ times)

---

**Last Updated**: 2025-12-25
**Version**: 1.0
