# 🔧 Operational Rules (실무 규칙)

## Code Quality
1. **No Placeholders**: `pass`, `# TODO` 절대 금지
2. **Full Implementation**: 스켈레톤 코드 금지
3. **Error Handling**: Try-except + meaningful messages
4. **Validation**: Input validation (None/type/range check)
5. **Logging**: Critical steps에 logging
6. **Docstrings**: 함수마다 docstring

## File Operations
1. **pathlib** 사용 (os.path 금지)
2. **Absolute paths** 우선
3. **Existence check**: 파일 읽기 전 확인
4. **Atomic writes**: 임시 파일 → rename

## Database
1. **Parameterized queries**: SQL injection 방지
2. **Close connections**: finally 블록에서 닫기
3. **Batch operations**: executemany 사용
4. **Index awareness**: 쿼리 작성 시 인덱스 활용

## Performance
1. **Vectorization**: Loop 대신 NumPy/Pandas
2. **Lazy evaluation**: 필요한 만큼만 로드
3. **Caching**: 반복 계산 방지
4. **Memory**: 대용량 데이터 시 메모리 관리

## Backtesting
1. **No look-ahead bias**: 미래 데이터 절대 금지
2. **Realistic costs**: 수수료, 슬리피지 반영
3. **Multiple periods**: 최소 2-3개 기간 검증
4. **Walk-forward**: 학습/테스트 기간 분리

## Code Organization (Disposable vs Reusable)

### Disposable Code (일회용 코드)

**Purpose**: 빠른 검증, 특정 실험 전용, 아이디어 테스트

**Location**:
```
~/experiments/YYYY-MM-DD_HH-MM_experiment_name/code/
├── experiment.py          # 메인 실험 코드
├── analysis_*.py          # 분석 스크립트
├── test_idea.py           # 아이디어 테스트
└── quick_fix.py           # 임시 수정
```

**Characteristics**:
- ✅ 하드코딩 허용 (dates, paths, parameters)
- ✅ 최소 문서화 (주석 정도)
- ✅ 빠른 반복 우선 (속도 > 재사용성)
- ✅ 실험 종료 후 삭제 가능
- ❌ 다른 실험에서 재사용 금지 (copy-paste 금지)

**When to Use**:
- 새로운 전략 아이디어 검증
- 데이터 탐색 (EDA)
- 한 번만 쓸 분석
- 파라미터 스윕
- 버그 재현/디버깅

**Example (Acceptable Disposable)**:
```python
# experiments/2025-12-24_15-30_fair_iv_test/code/experiment.py

import pandas as pd
import numpy as np

# HARDCODED - OK for disposable
START_DATE = '2024-10-01'
END_DATE = '2024-10-07'
IV_THRESHOLD = 0.15

# Load data
df = pd.read_csv('/home/sqr/data/btc_options.csv')
df = df[(df['date'] >= START_DATE) & (df['date'] <= END_DATE)]

# Quick analysis
results = df[df['iv'] > IV_THRESHOLD].groupby('strike')['pnl'].sum()
print(results.describe())
```

---

### Reusable Code (재사용 코드)

**Purpose**: 공통 로직, 라이브러리화, 여러 프로젝트에서 사용

**Location**:
```
~/lib/                     # 범용 유틸리티
~/utils/                   # 프로젝트 공통 유틸
~/project_name/src/        # 프로젝트 핵심 로직
├── data/
│   └── loader.py          # 데이터 로딩
├── metrics/
│   └── performance.py     # 성능 지표
└── backtest/
    └── engine.py          # 백테스트 엔진
```

**Characteristics**:
- ✅ 일반화 (파라미터화, 설정 파일)
- ✅ 에러 처리 철저 (try-except, validation)
- ✅ 테스트 포함 (unit tests)
- ✅ 문서화 (docstrings, README, examples)
- ✅ Type hints
- ❌ 하드코딩 절대 금지

**When to Use**:
- 3회 이상 재사용되는 로직
- 핵심 비즈니스 로직
- 공통 데이터 처리
- 백테스트 엔진
- 성능 지표 계산

**Example (Good Reusable)**:
```python
# ~/lib/data/loader.py

from pathlib import Path
from typing import Optional
import pandas as pd
from datetime import datetime

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
        symbol: Option symbol (e.g., 'BTC-25DEC25-100000-C')
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        data_dir: Optional data directory (defaults to ~/data/)

    Returns:
        DataFrame with columns: date, symbol, strike, iv, greeks, ...

    Raises:
        ValueError: If dates are invalid or exchange not supported
        FileNotFoundError: If data file doesn't exist

    Example:
        >>> df = load_options_data('OKX', 'BTC-PUT', '2024-10-01', '2024-10-07')
        >>> print(df.shape)
        (1234, 15)
    """
    # Validation
    if exchange not in ['OKX', 'Deribit', 'Binance']:
        raise ValueError(f"Unsupported exchange: {exchange}")

    # Parse dates
    try:
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError as e:
        raise ValueError(f"Invalid date format: {e}")

    if start > end:
        raise ValueError("start_date must be <= end_date")

    # Load data
    data_dir = data_dir or Path.home() / 'data'
    file_path = data_dir / f"{exchange.lower()}_options.parquet"

    if not file_path.exists():
        raise FileNotFoundError(f"Data file not found: {file_path}")

    df = pd.read_parquet(file_path)
    df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]

    return df
```

---

### Migration Path (전환 경로)

**When to Migrate (Disposable → Reusable)**:

1. **3회 이상 재사용**
   - Copy-paste 3번 발견 → 즉시 공통 함수 추출
   - 리팩토링: 파라미터화, 에러 처리 추가, 테스트 작성
   - 이동: `experiments/*/code/` → `~/lib/` or `project/src/`

2. **다른 팀원 사용 가능성**
   - 핵심 로직, 데이터 처리, 백테스트 컴포넌트
   - 문서화 필수 (docstrings, README)

3. **실험 종료 후 보존 가치**
   - "이거 나중에 또 쓸 것 같은데?" → 리팩토링 후 이동
   - 불확실하면 실험 폴더에 보관 (나중에 판단)

**Migration Process**:
```bash
# 1. Identify reusable logic in experiment
# experiments/2025-12-24_*/code/experiment.py has useful function

# 2. Extract to lib/
cp experiments/2025-12-24_*/code/experiment.py ~/lib/data/loader.py

# 3. Refactor (generalize, add error handling, tests)
vim ~/lib/data/loader.py

# 4. Update experiment to use lib
# experiments/2025-12-24_*/code/experiment.py:
from lib.data.loader import load_options_data
df = load_options_data('OKX', 'BTC-PUT', '2024-10-01', '2024-10-07')

# 5. Test
python -m pytest ~/lib/tests/test_loader.py

# 6. Document
vim ~/lib/README.md
```

---

### Anti-Patterns (절대 금지)

#### 1. ❌ Copy-Paste Hell
```python
# experiments/exp1/code/experiment.py
def calculate_sharpe(returns):
    return returns.mean() / returns.std() * np.sqrt(365)

# experiments/exp2/code/experiment.py
def calculate_sharpe(returns):  # COPY-PASTE!
    return returns.mean() / returns.std() * np.sqrt(365)

# experiments/exp3/code/experiment.py
def calculate_sharpe(returns):  # AGAIN!
    return returns.mean() / returns.std() * np.sqrt(365)
```

**Fix**: Extract to `~/lib/metrics/performance.py`

---

#### 2. ❌ Hidden Reusable Code
```python
# experiments/exp1/code/utils.py
# This is actually reusable but hidden in experiment folder!
class BacktestEngine:
    def __init__(self, ...):
        ...
    def run(self, ...):
        ...  # 500 lines of generic backtest logic
```

**Fix**: Move to `~/lib/backtest/engine.py`

---

#### 3. ❌ "나중에 정리" (Never Happens)
```python
# experiments/exp1/code/experiment.py
# TODO: 이거 나중에 lib/로 이동해야 함
def important_function():
    ...  # Never moved, copy-pasted 10 times instead
```

**Fix**: 지금 당장 이동. "나중에" = "절대 안 함"

---

#### 4. ❌ Over-Engineering Disposable Code
```python
# experiments/exp1/code/experiment.py
# This is just a one-time analysis, why so complex?!

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar('T')

class AbstractDataProcessor(ABC, Generic[T]):
    @abstractmethod
    def process(self, data: T) -> T:
        ...

class ConcreteProcessor(AbstractDataProcessor[pd.DataFrame]):
    def process(self, data: pd.DataFrame) -> pd.DataFrame:
        return data[data['iv'] > 0.15]  # 이거 하나 하려고 이렇게...?
```

**Fix**: Keep it simple for disposable code!
```python
# Just do this:
df = df[df['iv'] > 0.15]
```

---

### Decision Tree (어디에 작성할까?)

```
새 코드 작성 필요
    ↓
Q1: 한 번만 쓰고 버릴 코드인가?
    YES → Disposable (experiments/*/code/)
    NO  → Q2
    ↓
Q2: 3번 이상 재사용할 것 같은가?
    YES → Reusable (~/lib/ or project/src/)
    NO  → Q3
    ↓
Q3: 다른 팀원이 쓸 가능성?
    YES → Reusable (~/lib/)
    NO  → Disposable (일단, 나중에 판단)
```

---

### Examples

#### Good Disposable
```python
# experiments/2025-12-24_15-30_quick_test/code/test.py
import pandas as pd

df = pd.read_csv('/home/sqr/data/btc_options.csv')
print(df[df['iv'] > 0.15].groupby('strike')['pnl'].sum())
```

#### Good Reusable
```python
# ~/lib/metrics/performance.py
def calculate_sharpe_ratio(
    returns: pd.Series,
    risk_free_rate: float = 0.0,
    periods_per_year: int = 365
) -> float:
    """
    Calculate annualized Sharpe ratio.

    Args:
        returns: Series of period returns
        risk_free_rate: Annual risk-free rate (default: 0.0)
        periods_per_year: Number of periods per year (default: 365)

    Returns:
        Annualized Sharpe ratio
    """
    if len(returns) < 2:
        raise ValueError("Need at least 2 returns")

    excess_returns = returns - risk_free_rate / periods_per_year
    return excess_returns.mean() / excess_returns.std() * np.sqrt(periods_per_year)
```

---

**Summary**:
- **Disposable**: 빠르게, 하드코딩 OK, 한 번만
- **Reusable**: 일반화, 문서화, 테스트, 여러 번
- **Migration**: 3회 재사용 → 즉시 리팩토링
- **Anti-Pattern**: Copy-paste, 숨김, "나중에"

