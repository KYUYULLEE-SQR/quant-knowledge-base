# PostgreSQL Remote Data Access (micky 서버)

**Purpose**: micky 서버에서 캔들 데이터 접근 방법 (Binance, OKX)

**Last Updated**: 2025-12-23
**Owner**: sqr
**Server**: micky (192.168.50.3), accessed from spice/vultr

---

## 📌 Quick Reference

| Item | Value |
|------|-------|
| **서버 이름** | micky (데이터 서버) |
| **IP 주소** | 192.168.50.3:5432 |
| **데이터베이스** | PostgreSQL |
| **테이블** | `futures_data_1m` (273M+ rows) |
| **데이터 기간** | 2023-01-01 ~ 현재 (준실시간) |
| **접속 가능** | vultr, spice 서버만 (내부 네트워크) |
| **코드 위치** | `~/postgres_remote_data/` |
| **캐시** | 178개 심볼, 363.87 MB |

---

## 🚀 Quick Start (30초)

```python
import sys
sys.path.insert(0, '/home/sqr/postgres_remote_data')
from market_data_loader import load_candles

# ETH 10월 데이터 로드 (캐시 우선)
df = load_candles('Binance', 'ETH/USDT:USDT', '2025-10-01', '2025-11-01')
print(f"Loaded {len(df):,} candles")

# BTC 9월 데이터 (강제 DB 재로드)
df = load_candles('Binance', 'BTC/USDT:USDT', '2025-09-01', '2025-10-01', force_reload=True)
```

**Output**: pandas.DataFrame (index=timestamp, columns=open/high/low/close/volume)

---

## 🏗️ 시스템 구조

### 서버 역할

```
[거래소 API] → [micky 서버] → [PostgreSQL DB] → [spice/vultr] → [캐시 + 분석]
                (데이터 수집)    (273M+ rows)    (데이터 로드)    (로컬 캐시)
```

### 네트워크 구성

```
micky (192.168.50.3)
  └─ PostgreSQL 서버 (port 5432)
      └─ futures_data_1m (273M+ rows)

spice (현재 서버) ────┐
                      ├─ 내부 네트워크 ─→ micky
vultr (trading 서버) ─┘

외부 인터넷 ─✗─> micky (접속 불가)
```

### 데이터 흐름

1. **수집 (micky 서버)**:
   - Binance/OKX API → 1분봉 수집 → PostgreSQL 저장
   - 매 분마다 수집 (1-2분 지연)

2. **로드 (spice/vultr)**:
   - `load_candles()` 호출 → 캐시 확인 → 없으면 DB 쿼리 → 캐시 저장

3. **캐시 (로컬)**:
   - `~/postgres_remote_data/cache/*.pkl` (pickle 형식)
   - 178개 심볼, 363.87 MB
   - 기간별로 별도 파일 (빠른 재사용)

---

## 📖 주요 함수

### `load_candles()` - 데이터 로드 (캐시 우선)

```python
load_candles(
    exchange,           # 'Binance' or 'OKX'
    symbol,             # 'ETH/USDT:USDT', 'BTC/USDT:USDT'
    start_date,         # '2025-10-01'
    end_date,           # '2025-11-01'
    timeframe='1m',     # (옵션) '1m', '5m', '1h', '1d'
    force_reload=False, # (옵션) 캐시 무시하고 DB에서 재로드
    verbose=True        # (옵션) 로그 출력
)
```

**작동 방식**:
1. 캐시 확인 (`force_reload=False`일 때)
2. 캐시 없으면 PostgreSQL에서 로드
3. 로드한 데이터 캐시에 저장
4. DataFrame 반환

**예시**:
```python
# 1. 기본 사용 (캐시 우선)
df = load_candles('Binance', 'ETH/USDT:USDT', '2025-10-01', '2025-11-01')

# 2. 여러 심볼
symbols = ['BTC/USDT:USDT', 'ETH/USDT:USDT', 'SOL/USDT:USDT']
data = {sym: load_candles('Binance', sym, '2025-10-01', '2025-11-01', verbose=False)
        for sym in symbols}

# 3. 강제 재로드 (최신 데이터 반영)
df = load_candles('OKX', 'BTC/USDT:USDT', '2025-12-01', '2025-12-23', force_reload=True)

# 4. 다른 타임프레임
df_5m = load_candles('Binance', 'ETH/USDT:USDT', '2025-10-01', '2025-11-01', timeframe='5m')
```

### `get_cache_info()` - 캐시 정보 조회

```python
from market_data_loader import get_cache_info

info = get_cache_info()
print(f"캐시: {info['cache_count']}개, {info['total_size_mb']} MB")
# Output: 캐시: 178개, 363.87 MB
```

### `clear_cache()` - 캐시 삭제

```python
from market_data_loader import clear_cache

clear_cache()  # 전체 캐시 삭제 (.pkl 파일 모두 삭제)
```

---

## 🗄️ PostgreSQL 연결 정보

### DB Config (Hard-coded)

```python
# ~/postgres_remote_data/market_data_loader.py
DB_CONFIG = {
    'host': '192.168.50.3',      # micky 서버
    'port': 5432,
    'database': 'postgres',
    'user': 'postgres',
    'password': '123123'         # ⚠️ Production: 환경변수 사용 권장
}
```

### 직접 연결 (psycopg2)

```python
import psycopg2

# 연결 테스트
conn = psycopg2.connect(
    host='192.168.50.3',
    port=5432,
    database='postgres',
    user='postgres',
    password='123123'
)

# 쿼리 실행
cursor = conn.cursor()
cursor.execute("""
    SELECT timestamp, open, high, low, close, volume
    FROM futures_data_1m
    WHERE symbol = 'ETH/USDT:USDT'
    AND exchange = 'Binance'
    AND timestamp >= '2025-10-01 00:00:00'
    AND timestamp < '2025-10-02 00:00:00'
    ORDER BY timestamp ASC
""")

rows = cursor.fetchall()
conn.close()
```

### ⚠️ 보안 주의사항

1. **패스워드 하드코딩**:
   - 현재: 코드에 직접 `'123123'` 하드코딩
   - ✅ 개발/연구: 현재 설정 사용 OK
   - ⚠️ Production: 환경변수 권장
   ```python
   import os
   password = os.getenv('POSTGRES_PASSWORD', '123123')
   ```

2. **네트워크 제한**:
   - micky 서버는 외부 인터넷에서 직접 접속 불가
   - spice/vultr 서버를 경유해야만 접속 가능
   - 내부 네트워크 전용

3. **권한**:
   - 현재 `postgres` 사용자 (읽기/쓰기 모두 가능)
   - 데이터 삭제/수정 시 주의 (273M+ 행)
   - 가능하면 읽기 전용 사용자 생성 권장

---

## 📊 데이터 스키마

### `futures_data_1m` 테이블

| Column | Type | Description |
|--------|------|-------------|
| `timestamp` | TIMESTAMP | 캔들 시작 시각 (UTC) |
| `symbol` | VARCHAR | 심볼 (예: 'ETH/USDT:USDT') |
| `exchange` | VARCHAR | 거래소 ('Binance', 'OKX') |
| `open` | FLOAT | 시가 |
| `high` | FLOAT | 고가 |
| `low` | FLOAT | 저가 |
| `close` | FLOAT | 종가 |
| `volume` | FLOAT | 거래량 (계약 수) |

### 데이터 현황 (2024-12-23 기준)

- **총 행 수**: 273,097,314
- **기간**: 2023-01-01 ~ 현재
- **거래소**: Binance (145 symbols), OKX (33 symbols)
- **타임프레임**: 1m, 5m, 1h, 1d
- **누락률**: 0.00% (완벽)
- **업데이트**: 준실시간 (1-2분 지연)

---

## 🔍 Common Use Cases

### 백테스트 데이터 준비

```python
import sys
sys.path.insert(0, '/home/sqr/postgres_remote_data')
from market_data_loader import load_candles
import pandas as pd

# 2024 Q4 데이터 로드 (3개월)
df = load_candles('Binance', 'BTC/USDT:USDT', '2024-10-01', '2025-01-01')

# 리샘플링 (1m → 1h)
df_1h = df.resample('1h').agg({
    'open': 'first',
    'high': 'max',
    'low': 'min',
    'close': 'last',
    'volume': 'sum'
}).dropna()

print(f"1m candles: {len(df):,}")
print(f"1h candles: {len(df_1h):,}")
```

### 여러 거래소 비교

```python
# Binance vs OKX BTC 가격 비교
btc_binance = load_candles('Binance', 'BTC/USDT:USDT', '2025-10-01', '2025-11-01')
btc_okx = load_candles('OKX', 'BTC/USDT:USDT', '2025-10-01', '2025-11-01')

# 가격 차이 (arbitrage opportunity)
merged = pd.merge(
    btc_binance['close'],
    btc_okx['close'],
    left_index=True,
    right_index=True,
    suffixes=('_binance', '_okx')
)
merged['spread'] = merged['close_binance'] - merged['close_okx']
merged['spread_pct'] = (merged['spread'] / merged['close_binance']) * 100

print(f"평균 스프레드: {merged['spread_pct'].mean():.4f}%")
print(f"최대 스프레드: {merged['spread_pct'].max():.4f}%")
```

### 볼륨 분석

```python
# ETH 거래량 패턴 분석
df = load_candles('Binance', 'ETH/USDT:USDT', '2025-10-01', '2025-11-01')

# 시간대별 평균 거래량
df['hour'] = df.index.hour
volume_by_hour = df.groupby('hour')['volume'].mean()

print("시간대별 평균 거래량:")
print(volume_by_hour.sort_values(ascending=False).head(5))
```

---

## 🚨 트러블슈팅

### 1. 연결 에러 (psycopg2.OperationalError)

**증상**: `could not connect to server`

**원인**:
- micky 서버 다운
- 네트워크 장애
- PostgreSQL 서비스 중지

**해결**:
```bash
# 1. micky 서버 핑 테스트
ping 192.168.50.3

# 2. micky 서버 접속 확인
ssh micky
sudo systemctl status postgresql

# 3. PostgreSQL 재시작 (필요 시)
sudo systemctl restart postgresql

# 4. 캐시 활용 (임시 대안)
df = load_candles(..., force_reload=False)  # 캐시된 데이터 사용
```

### 2. 느린 쿼리 (타임아웃)

**증상**: 쿼리가 1분 이상 걸림

**원인**:
- 대용량 기간 쿼리 (6개월+)
- 네트워크 지연
- DB 부하

**해결**:
```python
# 1. 기간 분할 (1개월씩)
import pandas as pd
from datetime import datetime, timedelta

dfs = []
start = datetime(2025, 1, 1)
for i in range(6):  # 6개월
    end = start + timedelta(days=30)
    df = load_candles('Binance', 'BTC/USDT:USDT',
                      start.strftime('%Y-%m-%d'),
                      end.strftime('%Y-%m-%d'))
    dfs.append(df)
    start = end

df_all = pd.concat(dfs)

# 2. 캐시 재사용
df = load_candles(..., force_reload=False)  # 캐시 우선
```

### 3. 캐시 손상 (UnpicklingError)

**증상**: `pickle.UnpicklingError`

**해결**:
```python
from market_data_loader import clear_cache

# 전체 캐시 삭제 후 재로드
clear_cache()
df = load_candles(..., force_reload=True)
```

### 4. 데이터 누락 (빈 DataFrame)

**증상**: `df is None` or `df.empty`

**원인**:
- 잘못된 심볼명
- 데이터 없는 기간
- 거래소 오타

**해결**:
```python
# 1. 심볼명 확인 (정확한 형식)
# ✅ Correct: 'ETH/USDT:USDT'
# ❌ Wrong: 'ETHUSDT', 'ETH-USDT'

# 2. 기간 확인 (2023-01-01 이후만 가능)
df = load_candles('Binance', 'ETH/USDT:USDT', '2023-01-01', '2023-02-01')

# 3. 거래소 확인 (대소문자 구분)
# ✅ Correct: 'Binance', 'OKX'
# ❌ Wrong: 'binance', 'okx'
```

---

## 🔄 데이터 업데이트 정보

### 업데이트 주기
- **실시간성**: 준실시간 (Near real-time)
- **수집 주기**: 매 분마다 (1분봉 기준)
- **지연 시간**: 1-2분
- **데이터 소스**: Binance/OKX API

### 데이터 신선도 (Freshness)

```python
from market_data_loader import load_candles
from datetime import datetime, timedelta

# 최신 데이터 확인
today = datetime.now()
yesterday = today - timedelta(days=1)

df = load_candles('Binance', 'BTC/USDT:USDT',
                  yesterday.strftime('%Y-%m-%d'),
                  today.strftime('%Y-%m-%d'),
                  force_reload=True)  # 캐시 무시, DB에서 최신 데이터

print(f"최신 캔들: {df.index[-1]}")
print(f"지연 시간: {(datetime.now() - df.index[-1]).total_seconds() / 60:.1f}분")
```

### 백필 (Backfill) 정책
- **과거 데이터**: 2023-01-01부터 완벽 보존
- **누락 시**: 자동 재수집 (micky 서버에서)
- **검증**: 매일 자동 연속성 체크

---

## 📚 관련 문서

### 내부 문서
- **상세 README**: `~/postgres_remote_data/README.md`
- **예제 코드**: `~/postgres_remote_data/examples/example_usage.py`
- **스크립트**: `~/postgres_remote_data/scripts/*.py`

### Knowledge Base
- **Trading Mechanics**: `knowledge/domain/trading_mechanics.md` (거래 기초)
- **Backtesting NAV**: `knowledge/experiments/backtesting_nav_policy.md`
- **Performance Metrics**: `knowledge/experiments/performance_metrics.md`

### 외부 문서
- **PostgreSQL 공식 문서**: https://www.postgresql.org/docs/
- **psycopg2 문서**: https://www.psycopg.org/docs/

---

## ⚙️ 고급 설정

### 캐시 디렉토리 변경

```python
# market_data_loader.py 수정
CACHE_DIR = os.path.join(os.path.dirname(__file__), 'cache')

# 변경 예시 (SSD로 이동)
CACHE_DIR = '/mnt/ssd/cache'
```

### 타임아웃 설정 (추천)

```python
import psycopg2

# 타임아웃 설정 (30초)
conn = psycopg2.connect(
    host='192.168.50.3',
    port=5432,
    database='postgres',
    user='postgres',
    password='123123',
    connect_timeout=30  # 30초 타임아웃
)
```

### 연결 풀링 (대량 쿼리)

```python
from psycopg2 import pool

# 연결 풀 생성 (5개 연결)
connection_pool = pool.SimpleConnectionPool(
    1, 5,  # min, max connections
    host='192.168.50.3',
    port=5432,
    database='postgres',
    user='postgres',
    password='123123'
)

# 연결 가져오기
conn = connection_pool.getconn()

# 사용 후 반환
connection_pool.putconn(conn)
```

---

## 📈 성능 최적화

### 1. 캐시 우선 사용 (권장)

```python
# ✅ Good: 캐시 우선 (빠름)
df = load_candles('Binance', 'ETH/USDT:USDT', '2025-10-01', '2025-11-01')

# ⚠️ 필요시만: 강제 재로드 (느림)
df = load_candles('Binance', 'ETH/USDT:USDT', '2025-10-01', '2025-11-01', force_reload=True)
```

**속도 비교**:
- 캐시: 0.1~0.5초 (pickle 로드)
- DB 쿼리: 2~10초 (네트워크 + DB)

### 2. 병렬 로드 (여러 심볼)

```python
from concurrent.futures import ThreadPoolExecutor

symbols = ['BTC/USDT:USDT', 'ETH/USDT:USDT', 'SOL/USDT:USDT', 'BNB/USDT:USDT']

def load_symbol(sym):
    return load_candles('Binance', sym, '2025-10-01', '2025-11-01', verbose=False)

# 병렬 로드 (4개 심볼 동시)
with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(load_symbol, symbols))

data = dict(zip(symbols, results))
```

**속도 개선**: 4개 심볼 순차 로드 (40초) → 병렬 (12초)

### 3. 메모리 효율 (대용량)

```python
# ⚠️ 나쁜 예: 6개월 데이터 한번에 (메모리 1GB+)
df_6m = load_candles('Binance', 'BTC/USDT:USDT', '2025-01-01', '2025-07-01')

# ✅ 좋은 예: 1개월씩 분할 처리
for month in range(1, 7):
    df = load_candles('Binance', 'BTC/USDT:USDT',
                      f'2025-{month:02d}-01', f'2025-{month+1:02d}-01')
    # 처리
    result = process(df)
    save_result(result)
    del df  # 메모리 해제
```

---

## 🎯 Best Practices

### ✅ DO (권장)

1. **캐시 우선 사용**:
   ```python
   df = load_candles(..., force_reload=False)  # 기본값
   ```

2. **기간 분할 (대용량)**:
   ```python
   # 6개월 이상: 1개월씩 분할
   ```

3. **에러 처리**:
   ```python
   try:
       df = load_candles(...)
       if df is None or df.empty:
           print("⚠️ No data")
   except Exception as e:
       print(f"❌ Error: {e}")
   ```

4. **심볼명 정확히**:
   ```python
   # ✅ 'ETH/USDT:USDT' (slash + colon)
   ```

5. **타임아웃 설정 (psycopg2 직접 사용 시)**:
   ```python
   conn = psycopg2.connect(..., connect_timeout=30)
   ```

### ❌ DON'T (금지)

1. **캐시 무시 (불필요)**:
   ```python
   # ❌ 매번 force_reload=True (느림)
   df = load_candles(..., force_reload=True)
   ```

2. **대용량 기간 한번에**:
   ```python
   # ❌ 1년치 데이터 한번에 (메모리 폭발)
   df = load_candles(..., '2024-01-01', '2025-01-01')
   ```

3. **연결 미종료 (메모리 누수)**:
   ```python
   # ❌ conn.close() 없음
   conn = psycopg2.connect(...)
   # ... 작업 ...
   # conn.close() 누락!
   ```

4. **심볼명 오타**:
   ```python
   # ❌ 'ETHUSDT' (틀림)
   # ✅ 'ETH/USDT:USDT' (맞음)
   ```

5. **패스워드 하드코딩 (production)**:
   ```python
   # ❌ Production: 하드코딩
   password = '123123'

   # ✅ Production: 환경변수
   password = os.getenv('POSTGRES_PASSWORD')
   ```

---

**Version**: 1.0
**Created**: 2025-12-23
**Server**: spice (accessing micky)


---
---

# PostgreSQL Remote Data Access (corsair 서버) ⭐ NEW

**Purpose**: corsair 서버에서 캔들/옵션 데이터 접근 방법 (Binance, OKX, Bybit, Deribit)

**Last Updated**: 2025-12-26
**Owner**: sqr
**Server**: corsair (192.168.50.203)
**Status**: ✅ Production (Micky 데이터 + 옵션 Greeks 통합)

---

## 📌 Quick Reference

| Item | Value |
|------|-------|
| **서버 이름** | corsair (통합 데이터 서버) |
| **IP 주소** | 192.168.50.203:5432 |
| **데이터베이스** | PostgreSQL 14 (Docker TimescaleDB) |
| **주요 테이블** | `futures_data_1m` (53M+), `futures_data_1h` (26M+), 옵션 Greeks (175M+) |
| **데이터 기간** | 2023-01-01 ~ 현재 (실시간) |
| **접속 가능** | 내부 네트워크 (192.168.50.x) |
| **특징** | **Micky 선물 + 옵션 Greeks 통합** |

---

## 🚀 Quick Start

### Python에서 접속

```python
import psycopg2
import pandas as pd

# Corsair 서버 연결
conn = psycopg2.connect(
    host='192.168.50.203',
    port=5432,
    dbname='postgres',
    user='postgres',
    password='123123'
)

# 1분봉 데이터 로드
query = """
    SELECT timestamp, open, high, low, close, volume
    FROM futures_data_1m
    WHERE symbol = 'BTC/USDT:USDT'
      AND exchange = 'Binance'
      AND timestamp >= '2025-12-01'
      AND timestamp < '2025-12-02'
    ORDER BY timestamp ASC
"""

df = pd.read_sql(query, conn)
conn.close()

print(f"Loaded {len(df):,} candles")
```

### 옵션 Greeks 데이터 로드

```python
# OKX BTC 옵션 Greeks (Raw - 거래소 제공)
query = """
    SELECT timestamp, inst_id, delta, gamma, theta, vega, mark_vol
    FROM raw_okx_btc_options
    WHERE timestamp >= '2025-12-01'
      AND timestamp < '2025-12-02'
    ORDER BY timestamp ASC
"""

df_greeks = pd.read_sql(query, conn)

# Processed Greeks (Black-Scholes 재계산)
query = """
    SELECT timestamp, inst_id, delta, gamma, theta, vega, iv
    FROM processed_btc_options
    WHERE timestamp >= '2025-12-01'
    ORDER BY timestamp ASC
"""

df_processed = pd.read_sql(query, conn)
```

---

## 🗄️ 주요 테이블

### OHLCV (캔들 데이터) - Micky에서 이전

| 테이블 | Rows | 설명 |
|--------|------|------|
| `futures_data_1m` | 53M+ | 1분봉 (Binance, OKX, Bybit) |
| `futures_data_1h` | 26M+ | 1시간봉 (Binance, OKX, Bybit) |

### 옵션 Greeks (Raw) - 거래소 제공 원본 ⭐ NEW

| 테이블 | Rows | 크기 | 설명 |
|--------|------|------|------|
| `raw_okx_btc_options` | 57M | 18GB | OKX BTC 옵션 Greeks |
| `raw_okx_eth_options` | 53M | 16GB | OKX ETH 옵션 Greeks |
| `raw_deribit_btc_options` | 16M | 3.3GB | Deribit BTC 옵션 Greeks |
| `raw_deribit_eth_options` | 14M | 2.7GB | Deribit ETH 옵션 Greeks |

### 옵션 Greeks (Processed) - Black-Scholes 재계산 ⭐ NEW

| 테이블 | Rows | 크기 | 설명 |
|--------|------|------|------|
| `processed_btc_options` | 16M | 3.6GB | BTC Greeks (BS 재계산) |
| `processed_eth_options` | 19M | 4.0GB | ETH Greeks (BS 재계산) |

**차이점**:
- **Raw**: 거래소가 제공하는 Greeks (신뢰도 낮음)
- **Processed**: IV만 거래소에서 가져오고 모든 Greeks를 Black-Scholes로 재계산 (정확도 높음)

### 기타 테이블

| 테이블 | 설명 |
|--------|------|
| `funding_rates_v2` | 펀딩 레이트 |
| `futures_open_interest` | 미결제약정 |
| `okex_ticks` | 체결 데이터 (Multi-Exchange) |
| `okex_orderbook_snapshot` | 호가 스냅샷 |
| `symbol_metadata` | ATH/ATL 추적 (765 symbols) |
| `deribit_volatility_index` | Deribit DVOL |

---

## 📊 데이터 스키마

### `futures_data_1m` / `futures_data_1h`

| Column | Type | Description |
|--------|------|-------------|
| `timestamp` | TIMESTAMP | 캔들 시작 시각 (UTC) |
| `symbol` | TEXT | 심볼 (예: 'BTC/USDT:USDT') |
| `exchange` | TEXT | 거래소 ('Binance', 'OKX', 'Bybit') |
| `open` | NUMERIC | 시가 |
| `high` | NUMERIC | 고가 |
| `low` | NUMERIC | 저가 |
| `close` | NUMERIC | 종가 |
| `volume` | NUMERIC | 거래량 |

### `raw_okx_btc_options` (예시)

| Column | Type | Description |
|--------|------|-------------|
| `timestamp` | TIMESTAMP | 데이터 시각 (UTC) |
| `inst_id` | TEXT | 옵션 계약명 (예: 'BTC-25DEC25-100000-C') |
| `delta` | NUMERIC | Delta (거래소 제공) |
| `gamma` | NUMERIC | Gamma |
| `theta` | NUMERIC | Theta |
| `vega` | NUMERIC | Vega |
| `mark_vol` | NUMERIC | Mark IV (내재 변동성) |
| `mark_price` | NUMERIC | Mark Price |

### `processed_btc_options`

| Column | Type | Description |
|--------|------|-------------|
| `timestamp` | TIMESTAMP | 데이터 시각 |
| `inst_id` | TEXT | 옵션 계약명 |
| `delta` | NUMERIC | Delta (BS 재계산) ⭐ |
| `gamma` | NUMERIC | Gamma (BS 재계산) ⭐ |
| `theta` | NUMERIC | Theta (BS 재계산) ⭐ |
| `vega` | NUMERIC | Vega (BS 재계산) ⭐ |
| `iv` | NUMERIC | IV (거래소에서 가져옴) |
| `theoretical_price` | NUMERIC | BS 이론가 |

---

## 🔄 Micky vs Corsair 비교

| 항목 | Micky (192.168.50.3) | Corsair (192.168.50.203) |
|------|---------------------|----------------------|
| **용도** | 데이터 수집 원본 서버 | **통합 데이터 서버** ⭐ |
| **OHLCV** | ✅ 273M rows | ✅ 80M rows (동일 데이터) |
| **옵션 Greeks** | ✅ 175M rows | ✅ 175M rows (이전 완료) |
| **Processed Greeks** | ✅ 35M rows | ✅ 35M rows |
| **PM2 프로세스** | 15개 (수집 중) | 15개 (수집 중) |
| **재부팅 자동 시작** | ✅ | ✅ |
| **추천 용도** | 수집 전용 | **분석/백테스트 용도** ⭐ |

**권장 사용**:
- **백테스트/분석**: Corsair 사용 (통합 데이터)
- **모니터링**: Micky 또는 Corsair 둘 다 가능

---

## 🔍 Common Use Cases

### 1. 옵션 Greeks 분석

```python
import psycopg2
import pandas as pd

conn = psycopg2.connect(
    host='192.168.50.203', port=5432,
    dbname='postgres', user='postgres', password='123123'
)

# BTC 12월 만기 옵션 Delta 분석
query = """
    SELECT timestamp, inst_id, delta, mark_price
    FROM processed_btc_options
    WHERE inst_id LIKE '%25DEC25%'
      AND timestamp >= '2025-12-01'
    ORDER BY timestamp, inst_id
"""

df = pd.read_sql(query, conn)
conn.close()

# Delta hedging 계산
df['delta_hedge'] = df['delta'] * df['mark_price']
```

### 2. IV Surface 구축

```python
# 특정 시각의 IV Surface
query = """
    SELECT inst_id, iv, mark_price
    FROM processed_btc_options
    WHERE timestamp = '2025-12-26 12:00:00'
    ORDER BY inst_id
"""

df_iv = pd.read_sql(query, conn)

# Strike & Expiry 파싱
df_iv['strike'] = df_iv['inst_id'].str.extract(r'-(\\d+)-')[0].astype(float)
df_iv['expiry'] = pd.to_datetime(df_iv['inst_id'].str.extract(r'BTC-(\\d{2}[A-Z]{3}\\d{2})')[0], format='%d%b%y')
```

### 3. 여러 거래소 비교

```python
# Binance vs OKX vs Bybit 가격 비교
query = """
    SELECT timestamp, exchange, close
    FROM futures_data_1m
    WHERE symbol = 'BTC/USDT:USDT'
      AND timestamp >= '2025-12-26 00:00:00'
      AND timestamp < '2025-12-26 01:00:00'
    ORDER BY timestamp, exchange
"""

df = pd.read_sql(query, conn)
df_pivot = df.pivot(index='timestamp', columns='exchange', values='close')

# Arbitrage spread 계산
df_pivot['binance_okx_spread'] = df_pivot['Binance'] - df_pivot['OKX']
```

---

## 🚨 트러블슈팅

### 연결 실패

```bash
# 1. Corsair 서버 핑 테스트
ping 192.168.50.203

# 2. Docker 컨테이너 상태 확인
ssh sqr@192.168.50.203
sudo docker ps | grep candledb

# 3. PostgreSQL 로그 확인
sudo docker logs candledb --tail 50
```

### 데이터 없음

```python
# 테이블 존재 확인
query = """
    SELECT tablename FROM pg_tables
    WHERE schemaname = 'public'
    ORDER BY tablename
"""

df_tables = pd.read_sql(query, conn)
print(df_tables)
```

---

## 📚 추가 문서

- **Corsair 상세 설정**: `/home/sqr/CORSAIR_SETUP_SUMMARY.md`
- **Data Collector 접속 정보**: `/home/sqr/data_collector/docs/SERVER_ACCESS.md`
- **Micky 서버 정보**: 위의 micky 섹션 참조

---

**Version**: 1.0 (Corsair 통합)  
**Created**: 2025-12-26  
**Server**: Any server → Corsair (192.168.50.203)
