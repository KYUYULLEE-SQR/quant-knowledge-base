# Market Data Integration (로컬 수집 + 원격 접근 통합)

**Purpose**: Local (SQLite) + Remote (PostgreSQL) 캔들 데이터 시스템 통합 가이드

**Last Updated**: 2025-12-23
**Owner**: sqr
**Location**: `~/market_data/`

---

## 📌 Quick Reference

| System | Purpose | Storage | Data Range | Use Case |
|--------|---------|---------|------------|----------|
| **Local** | 직접 수집 | SQLite | 최근 30일~1년 | 개발, 테스트, 최신 데이터 |
| **Remote** | 원격 접근 | PostgreSQL @ micky | 2023~현재 (2.7억 행) | 대규모 백테스트, 연구 |

---

## 🚀 Quick Start

### Local 수집

```python
from market_data.local.collector import OKXCollector
from market_data.local.database import Database

# 최근 7일 수집
collector = OKXCollector()
collector.collect_historical('okx', 'BTC-USDT-SWAP', days=7)

# 로드
db = Database()
df = db.load_candles('okx', 'BTCUSDT', '2025-12-16', '2025-12-23')
```

### Remote 접근

```python
import sys
sys.path.insert(0, '/home/sqr/market_data')
from remote.loader import load_candles

# micky 서버에서 로드 (캐시 우선)
df = load_candles('Binance', 'ETH/USDT:USDT', '2025-10-01', '2025-11-01')
```

---

## 🏗️ 시스템 구조

### Local (SQLite)

```
OKX API → Collector → SQLite (~/market_data/data/market_data.db)
                         ↓
                    DataFrame
```

**장점**:
- ✅ 실시간 데이터 수집 가능
- ✅ 빠른 접근 (로컬 파일)
- ✅ 외부 의존성 없음

**단점**:
- ❌ 제한된 용량 (수 GB)
- ❌ 수동 수집 필요
- ❌ 과거 데이터 제한적

### Remote (PostgreSQL)

```
micky 서버 (192.168.50.3) → PostgreSQL (futures_data_1m, 273M rows)
                                ↓
                           Network Query
                                ↓
                           Cache (pickle)
                                ↓
                           DataFrame
```

**장점**:
- ✅ 대용량 (2.7억+ 행)
- ✅ 오래된 데이터 (2023~)
- ✅ 자동 업데이트 (1-2분 지연)

**단점**:
- ❌ 네트워크 필요 (spice/vultr만)
- ❌ 첫 쿼리 느림 (캐시 후 빠름)
- ❌ 실시간성 낮음 (1-2분 지연)

---

## 🎯 사용 시나리오

### 시나리오 1: 최신 데이터 백테스트 (오늘 ~ 1개월 전)

**추천**: Local

```python
from market_data.local.database import Database

db = Database()
df = db.load_candles('okx', 'BTCUSDT', '2025-11-23', '2025-12-23')

# 백테스트 실행
sharpe, mdd = run_backtest(df)
```

**이유**: 최신 데이터, 빠른 접근, 네트워크 불필요

---

### 시나리오 2: 과거 데이터 백테스트 (2024년 Q4)

**추천**: Remote

```python
from market_data.remote.loader import load_candles

df = load_candles('Binance', 'BTC/USDT:USDT', '2024-10-01', '2025-01-01')

# 백테스트 실행
sharpe, mdd = run_backtest(df)
```

**이유**: 오래된 데이터, 대용량, 캐시 활용

---

### 시나리오 3: 하이브리드 (2024년 전체 + 2025년 최신)

**추천**: Remote (과거) + Local (최신) 병합

```python
import pandas as pd
from market_data.remote.loader import load_candles
from market_data.local.database import Database

# Remote: 2024년 (historical)
df_2024 = load_candles('Binance', 'BTC/USDT:USDT', '2024-01-01', '2025-01-01')

# Local: 2025년 (realtime)
db = Database()
df_2025 = db.load_candles('okx', 'BTCUSDT', '2025-01-01', '2025-12-23')

# 병합
df_all = pd.concat([df_2024, df_2025]).sort_index()

# 백테스트 (2024-2025 전체)
sharpe, mdd = run_backtest(df_all)
```

**이유**: 과거 대용량 + 최신 실시간 데이터 모두 필요

---

## ⚙️ 설정 (config.py)

### 공통 설정

```python
from market_data.config import (
    local_config,
    remote_config,
    SYMBOL_MAPPING,
    TIMEFRAMES
)

# 심볼 정규화
from market_data.config import normalize_symbol

okx_symbol = 'BTC-USDT-SWAP'
postgres_symbol = normalize_symbol(okx_symbol, 'postgres')  # 'BTC/USDT:USDT'
display_symbol = normalize_symbol(okx_symbol, 'display')    # 'BTCUSDT'
```

### Local 설정

```python
# SQLite DB 경로
db_path = local_config.get_db_path()  # '~/market_data/data/market_data.db'

# 수집 대상
exchanges = local_config.exchanges    # ['okx']
symbols = local_config.symbols        # {'okx': ['BTC-USDT-SWAP', ...]}
```

### Remote 설정

```python
# PostgreSQL 연결
conn_params = remote_config.get_connection_params()
# {'host': '192.168.50.3', 'port': 5432, ...}

# 캐시 디렉토리
cache_dir = remote_config.cache_dir  # '~/market_data/cache'
```

---

## 📊 데이터 비교

| 항목 | Local (SQLite) | Remote (PostgreSQL) |
|------|----------------|---------------------|
| **총 행 수** | ~수백만 (심볼/기간별) | 273,097,314 (2.7억+) |
| **기간** | 최근 30일~1년 | 2023-01-01 ~ 현재 |
| **거래소** | OKX (7 symbols) | Binance (145), OKX (33) |
| **업데이트** | 수동 (스크립트 실행) | 자동 (1-2분 지연) |
| **누락률** | 수집 품질 따라 | 0.00% (완벽) |
| **용량** | ~수백 MB | ~수십 GB (서버) |

---

## 🔄 데이터 흐름

### Local 수집 흐름

```
1. OKX API 호출
   ↓
2. Rate limit 체크
   ↓
3. JSON → DataFrame
   ↓
4. 중복 체크
   ↓
5. SQLite INSERT
   ↓
6. 로그 기록
```

### Remote 접근 흐름

```
1. load_candles() 호출
   ↓
2. 캐시 확인 (pickle)
   ├─ 있으면 → 캐시 로드 (빠름)
   └─ 없으면 ↓
3. PostgreSQL 쿼리 (micky)
   ↓
4. DataFrame 변환
   ↓
5. 캐시 저장 (pickle)
   ↓
6. 반환
```

---

## 🛠️ 스크립트

### Local 스크립트

```bash
# Historical 수집
cd ~/market_data
python scripts/local/collect_historical.py --symbol BTC-USDT-SWAP --days 30

# Realtime 수집 (loop)
python scripts/local/collect_realtime.py

# DB 정리
python scripts/local/clean_database.py
```

### Remote 스크립트

```bash
# 캔들 로드
cd ~/market_data
python scripts/remote/load_candles.py --exchange Binance --symbol BTC/USDT:USDT --start 2025-10-01 --end 2025-11-01

# 주요 심볼 사전 캐싱
python scripts/remote/cache_symbols.py

# 데이터 품질 체크
python scripts/remote/check_data.py
```

---

## 🚨 트러블슈팅

### Local: SQLite Locked

**증상**: `database is locked`

**해결**:
```bash
# 진행 중인 프로세스 확인
ps aux | grep collect

# 종료
kill -9 <PID>

# DB 재시작
python -c "from market_data.local.database import Database; Database()"
```

### Remote: PostgreSQL 연결 실패

**증상**: `could not connect to server`

**해결**:
```bash
# 1. micky 서버 핑
ping 192.168.50.3

# 2. PostgreSQL 포트 확인
nc -zv 192.168.50.3 5432

# 3. 캐시 활용 (임시)
python -c "from market_data.remote.loader import load_candles; df = load_candles(..., force_reload=False)"
```

### 하이브리드: 심볼 불일치

**증상**: Local (BTCUSDT) vs Remote (BTC/USDT:USDT) 형식 다름

**해결**:
```python
from market_data.config import normalize_symbol

# OKX → PostgreSQL
okx_symbol = 'BTC-USDT-SWAP'
pg_symbol = normalize_symbol(okx_symbol, 'postgres')  # 'BTC/USDT:USDT'

# OKX → Display
display = normalize_symbol(okx_symbol, 'display')  # 'BTCUSDT'
```

---

## 📚 관련 문서

### 내부 문서

- **통합 README**: `~/market_data/README.md`
- **Local 가이드**: `~/market_data/local/README.md`
- **Remote 가이드**: `~/market_data/remote/README.md`

### Knowledge Base

- **PostgreSQL Data Access**: `infrastructure/postgres_data_access.md` (상세 가이드)
- **Backtesting NAV**: `experiments/backtesting_nav_policy.md`
- **Performance Metrics**: `experiments/performance_metrics.md`

### 원본 프로젝트 (deprecated)

- **Local (구버전)**: `~/market_data_collector_local/`
- **Remote (구버전)**: `~/postgres_remote_data/`

---

## 🎯 Best Practices

### ✅ DO (권장)

1. **최신 데이터 (< 1개월)**: Local 수집 사용
2. **과거 데이터 (> 1개월)**: Remote 접근 사용
3. **대규모 백테스트**: Remote + 캐시 활용
4. **실시간 모니터링**: Local realtime collector
5. **하이브리드 전략**: 과거 (Remote) + 최신 (Local) 병합

### ❌ DON'T (금지)

1. ❌ Local로 수년치 데이터 수집 → 용량 부족, 시간 낭비
2. ❌ Remote에서 매번 force_reload=True → 네트워크 부하
3. ❌ 두 시스템에서 동일 기간 중복 수집 → 불필요
4. ❌ Remote 연결 정보 외부 노출 → 보안 위험
5. ❌ SQLite에 동시 쓰기 (멀티프로세스) → 락 충돌

---

## 💡 Tips

### Tip 1: 캐시 사전 준비

백테스트 전에 필요한 데이터를 미리 캐싱:

```python
from market_data.remote.loader import load_candles

# 주요 심볼 사전 캐싱 (1회만)
symbols = ['BTC/USDT:USDT', 'ETH/USDT:USDT', 'SOL/USDT:USDT']
for sym in symbols:
    load_candles('Binance', sym, '2024-10-01', '2025-01-01', verbose=True)

# 이후 백테스트는 빠름 (캐시)
df = load_candles('Binance', 'BTC/USDT:USDT', '2024-10-01', '2025-01-01')
```

### Tip 2: 병렬 로드

여러 심볼 동시 로드:

```python
from concurrent.futures import ThreadPoolExecutor
from market_data.remote.loader import load_candles

symbols = ['BTC/USDT:USDT', 'ETH/USDT:USDT', 'SOL/USDT:USDT']

def load_symbol(sym):
    return load_candles('Binance', sym, '2025-10-01', '2025-11-01', verbose=False)

with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(load_symbol, symbols))

data = dict(zip(symbols, results))
```

### Tip 3: 메모리 효율

대용량 데이터 처리 시 기간 분할:

```python
import pandas as pd
from market_data.remote.loader import load_candles

dfs = []
for month in range(1, 13):  # 2024년 전체
    df = load_candles('Binance', 'BTC/USDT:USDT',
                      f'2024-{month:02d}-01', f'2024-{month+1:02d}-01')

    # 월별 처리
    result = process_month(df)
    dfs.append(result)
    del df  # 메모리 해제

# 결과 병합
df_all = pd.concat(dfs)
```

---

**Version**: 1.0
**Created**: 2025-12-23
**Integration**: market_data_collector_local + postgres_remote_data → market_data

