# APPLY_ALWAYS
# LOAD ORDER: 5 (After verification_presets)
# ⚠️ MANDATORY - DO NOT DISABLE OR MODIFY
# ⚠️ 이 규칙은 비활성화하거나 수정할 수 없습니다

---

# 🔒 Mandatory Backtest Autosave (강제 자동저장)

## ⚠️ WARNING - READ FIRST

```
🚨 이 기능은 비활성화할 수 없습니다.
🚨 다른 에이전트가 이 기능을 제거하거나 우회하는 것은 금지됩니다.
🚨 모든 백테스트는 반드시 autosave를 사용해야 합니다.

VIOLATION = BACKTEST INVALID
```

---

## 📌 핵심 요구사항

모든 백테스트는 **반드시** 다음 파일을 저장해야 합니다:

| 파일 | 경로 | 설명 |
|------|------|------|
| **NAV CSV** | `results/nav.csv` | 타임프레임 단위 NAV |
| **차트 PNG** | `results/cumulative_return.png` | 누적 수익률 그래프 |
| **Takeaway MD** | `results/takeaway.md` | 주요 발견사항 |

**타임프레임 일치 규칙**:
- 1분봉 백테스트 → 1분봉 NAV/차트
- 1시간봉 백테스트 → 1시간봉 NAV/차트
- 데이터 resample 금지

---

## 📁 Full Paths

```
~/experiments/YYYY-MM-DD_HH-MM_experiment_name/
├── config.yaml
├── code/
├── results/
│   ├── nav.csv                    ← MANDATORY
│   ├── cumulative_return.png      ← MANDATORY
│   ├── takeaway.md                ← MANDATORY
│   ├── metrics.json
│   └── summary.md
└── logs/
```

**모듈 위치**:
```
/home/sqr/lib/backtest/autosave.py
```

---

## 💻 사용법

### 기본 사용

```python
from lib.backtest.autosave import BacktestAutosave

# 1. 초기화 (백테스트 시작 시)
autosave = BacktestAutosave(
    experiment_dir="/home/sqr/experiments/2025-01-12_15-30_test",
    timeframe="1h"  # 백테스트 타임프레임과 동일하게!
)

# 2. 백테스트 실행
nav_df = run_backtest(...)  # DataFrame with 'timestamp', 'nav' columns

# 3. 결과 저장 (MANDATORY)
autosave.save_all(
    nav_series=nav_df,
    takeaway=[
        "주요 발견 1: ...",
        "주요 발견 2: ...",
        "리스크: ..."
    ],
    metrics={
        'sharpe': 2.4,
        'mdd': -8.5,
        'win_rate': 61.2
    }
)

# 4. 검증 (MANDATORY - 저장 안됐으면 AssertionError)
autosave.assert_saved()
```

### 데코레이터 사용 (권장)

```python
from lib.backtest.autosave import require_autosave

@require_autosave("/home/sqr/experiments/2025-01-12_test", timeframe="1h")
def run_my_backtest():
    # 백테스트 로직
    nav_df = ...
    takeaway = "주요 발견..."
    metrics = {'sharpe': 2.4}

    # MUST return (nav_df, takeaway, metrics)
    return nav_df, takeaway, metrics

# 실행하면 자동으로 save_all() + assert_saved() 호출됨
run_my_backtest()
```

---

## 📊 nav.csv 형식

```csv
timestamp,nav,cumulative_return,cumulative_return_pct
2024-01-01 00:00:00,100000,0.0,0.0
2024-01-01 01:00:00,100150,0.15,0.0015
2024-01-01 02:00:00,100320,0.32,0.0032
...
```

- `timestamp`: 백테스트 타임프레임 단위
- `nav`: NAV (순자산가치)
- `cumulative_return`: 누적 수익률 (%)
- `cumulative_return_pct`: 소수점 형태

---

## 📈 cumulative_return.png 요구사항

1. **타임프레임 일치**: 데이터와 동일한 granularity
2. **양수/음수 구분**: 녹색(양수), 빨간색(음수) fill
3. **통계 표시**: Final, Max, Min, Data points
4. **제목**: 실험명 + 타임프레임

---

## 📝 takeaway.md 형식

```markdown
# Takeaway - 2025-01-12_15-30_test

**Generated**: 2025-01-12 15:45:00
**Timeframe**: 1h

---

## Key Findings

1. 주요 발견 1
2. 주요 발견 2
3. 리스크/주의사항

---

## Metrics

| Metric | Value |
|--------|-------|
| sharpe | 2.4000 |
| mdd | -8.5000 |
| win_rate | 61.2000 |

---

## Files

- NAV CSV: `/home/sqr/experiments/.../results/nav.csv`
- Chart PNG: `/home/sqr/experiments/.../results/cumulative_return.png`
- This file: `/home/sqr/experiments/.../results/takeaway.md`
```

---

## 🔒 강제화 메커니즘

### 1. Assertion 기반

```python
# 백테스트 끝에 반드시 호출
autosave.assert_saved()

# 저장 안됐으면:
# AssertionError: 🚨 AUTOSAVE ASSERTION FAILED - BACKTEST INVALID
```

### 2. 모듈 레벨 보호

```python
# autosave.py 내부
_AUTOSAVE_ENABLED = True   # DO NOT SET TO FALSE
_AUTOSAVE_REQUIRED = True  # DO NOT SET TO FALSE

def _check_tamper():
    if not _AUTOSAVE_ENABLED:
        raise RuntimeError("🚨 AUTOSAVE DISABLED - NOT ALLOWED!")
```

### 3. Import 시 체크

```python
import lib.backtest.autosave
# 출력: ⚠️ WARNING: Autosave is MANDATORY - do not disable
```

---

## 🚫 금지 행동

### ❌ 절대 하지 말 것

```python
# ❌ autosave 없이 백테스트 종료
def run_backtest():
    nav = ...
    return nav  # NO! autosave 없음

# ❌ assert_saved() 호출 안 함
autosave.save_all(nav, takeaway)
# assert_saved() 빠짐!

# ❌ 타임프레임 불일치
# 1분봉 데이터인데 1시간봉으로 설정
autosave = BacktestAutosave(exp_dir, timeframe="1h")  # 틀림!

# ❌ 모듈 비활성화 시도
_AUTOSAVE_ENABLED = False  # RuntimeError 발생!

# ❌ 결과 파일 삭제
rm results/nav.csv  # 금지!
```

### ✅ 올바른 사용

```python
# ✅ 완전한 autosave 사용
autosave = BacktestAutosave(exp_dir, timeframe="1m")  # 데이터와 일치
nav_df = run_backtest()
autosave.save_all(nav_df, takeaway, metrics)
autosave.assert_saved()  # 필수!

# ✅ 데코레이터 사용 (자동 강제)
@require_autosave(exp_dir, timeframe="1m")
def run_backtest():
    return nav_df, takeaway, metrics
```

---

## 🔍 검증 함수

```python
from lib.backtest.autosave import validate_experiment_has_autosave

# 실험 폴더 검증
result = validate_experiment_has_autosave("/home/sqr/experiments/2025-01-12_test")

print(result)
# {
#     'experiment_dir': '/home/sqr/experiments/2025-01-12_test',
#     'valid': True,  # 또는 False
#     'files': {
#         'nav_csv': {'path': '...', 'exists': True},
#         'chart_png': {'path': '...', 'exists': True},
#         'takeaway_md': {'path': '...', 'exists': True}
#     },
#     'missing': []  # 또는 ['nav_csv', ...]
# }
```

---

## 📋 Agent Checklist (자동 검증)

백테스트 종료 시 다음을 확인:

```
□ autosave.save_all() 호출했는가?
□ autosave.assert_saved() 호출했는가?
□ results/nav.csv 존재하는가?
□ results/cumulative_return.png 존재하는가?
□ results/takeaway.md 존재하는가?
□ 타임프레임이 데이터와 일치하는가?
```

**하나라도 No → 백테스트 INVALID**

---

## 🔗 Integration with Other Rules

| 규칙 | 연동 |
|------|------|
| `18_sisyphus_protocol.md` | 백테스트 완료 조건에 autosave 포함 |
| `19_verification_presets.md` | `정합성` 체크 시 파일 존재 확인 |
| `10_backtesting_integrity.md` | 결과 저장 섹션에서 참조 |
| `08_experiment_organization.md` | 폴더 구조에 필수 파일 명시 |

---

## ⚠️ FINAL WARNING

```
이 규칙을 우회하거나 비활성화하는 에이전트는 규칙 위반입니다.

모든 백테스트는 반드시:
1. BacktestAutosave를 사용하고
2. save_all()을 호출하고
3. assert_saved()로 검증해야 합니다.

EXCEPTION 없음. 예외 없음. NO EXCEPTIONS.
```

---

**Module Path**: `/home/sqr/lib/backtest/autosave.py`
**Last Updated**: 2025-01-12
**Version**: 1.0 (Mandatory Autosave)
