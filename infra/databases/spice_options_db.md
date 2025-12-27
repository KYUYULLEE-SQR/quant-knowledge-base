# Spice Server - Options Database

**Purpose**: Spice 서버 로컬 옵션 데이터베이스 접속 및 사용 가이드
**Last Updated**: 2025-12-23
**Owner**: sqr
**Server**: spice (localhost)

---

## 📌 Quick Reference

| Item | Value |
|------|-------|
| **Database** | PostgreSQL 12 |
| **Host** | 127.0.0.1:5432 |
| **Database Name** | `data_integration` |
| **User** | sqr |
| **Password** | sqr |
| **Main Table** | `btc_options_parsed` |
| **Total Rows** | 169,755,765 rows (169M) |
| **Data Period** | 2022-04-16 ~ 2025-12-05 |
| **Data Sources** | Deribit (138M rows), OKX (31M rows) |
| **Update Frequency** | Daily (OKX 데이터) |

---

## 🚀 Quick Start (30초)

### Connection String

```bash
# psql 직접 접속
PGPASSWORD=sqr psql -h 127.0.0.1 -U sqr -d data_integration
```

### Python Connection

```python
import psycopg2
import pandas as pd

# Connection config
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 5432,
    'user': 'sqr',
    'password': 'sqr',
    'database': 'data_integration'
}

# Connect
conn = psycopg2.connect(**DB_CONFIG)

# Query
query = """
SELECT *
FROM btc_options_parsed
WHERE date = '2024-10-05'
  AND exchange = 'OKEX'
LIMIT 100
"""

df = pd.read_sql(query, conn)
conn.close()
```

---

## 📊 Database Overview

### Available Tables

```
data_integration 데이터베이스 (8개 테이블):

1. btc_options_parsed         169M rows  ⭐ 메인 (일별 OHLCV + Greeks)
2. btc_options_hourly          ~15M rows  (시간별 normalized data)
3. eth_options_parsed          (ETH 옵션, unlogged table)
4. futures_data_1m             (선물 1분봉 OHLCV)
5. btc_options_normalized      (normalized data)
6. btc_options_parsed_staging  (staging area)
7. trading_tickers             (거래 가능 심볼 목록)
8. eth_options_ohlc_greek_deribit (Deribit ETH 옵션)
```

---

## 📋 Table Schemas

### 1. `btc_options_parsed` ⭐ (Main Table)

**Purpose**: BTC 옵션 일별 OHLCV + Greeks (Deribit + OKX)

**Schema**:
```sql
Column          | Type                        | Description
----------------+-----------------------------+----------------------------------
date            | timestamp without time zone | 데이터 시각 (UTC)
exchange        | text                        | 'deribit' or 'OKEX'
currency        | text                        | 'BTC' or 'ETH'
callput         | text                        | 'c' (Call) or 'p' (Put)
strike          | double precision            | 행사가 (USD)
tte             | double precision            | Time to Expiry (days)
expiry          | timestamp without time zone | 만기일 (UTC)
symbol          | text                        | OKX 형식: BTC-USD-251226-100000-C
iv              | double precision            | Implied Volatility (IV)
open            | double precision            | Open price
high            | double precision            | High price
low             | double precision            | Low price
close           | double precision            | Close price
spot_price_usd  | double precision            | BTC spot price (USD)
delta           | double precision            | Delta (Greek)
gamma           | double precision            | Gamma (Greek)
theta           | double precision            | Theta (Greek)
vega            | double precision            | Vega (Greek)
rho             | double precision            | Rho (Greek, mostly NULL)

Indexes:
    idx_btc_options_parsed_unique         UNIQUE (date, symbol, exchange)
    idx_btc_options_parsed_date_new       (date)
    idx_btc_options_parsed_date_symbol    (date, symbol)
    idx_btc_options_parsed_expiry         (expiry)
    idx_btc_options_parsed_expiry_symbol  (expiry, symbol)
    idx_btc_options_parsed_delta          (delta)
    idx_btc_options_parsed_symbol         (symbol)
```

**Data Statistics** (2025-12-23 기준):
```
Total Rows:       169,755,765
Date Range:       2022-04-16 ~ 2025-12-05
Exchanges:
  - Deribit:      138,276,701 rows (81.5%)
  - OKEX:          31,479,064 rows (18.5%)

OKX Data Only:
  - Rows:          31,479,064
  - Unique Symbols: 18,243
  - Date Range:     2025-02-05 ~ 2025-12-05
  - Trading Days:   295 days
```

**Top Symbols** (OKX, by row count):
```
BTC-USD-251226-180000-P    44,954 rows
BTC-USD-251226-260000-C    44,954 rows
BTC-USD-251226-110000-C    44,954 rows
BTC-USD-251226-150000-P    44,954 rows
BTC-USD-251226-130000-C    44,954 rows
...
```

---

### 2. `btc_options_hourly`

**Purpose**: BTC 옵션 시간별 normalized data

**Schema**:
```sql
Column   | Type      | Description
---------+-----------+----------------------------------
date     | TIMESTAMP | 데이터 시각 (UTC)
symbol   | VARCHAR   | BTC-USD-250131-50000-C
strike   | FLOAT     | 행사가 (USD)
callput  | VARCHAR   | 'c' or 'p'
expiry   | TIMESTAMP | 만기일 (UTC 08:00)
price    | FLOAT     | Normalized (price/spot)
spot     | FLOAT     | BTC spot price (USD)
iv       | FLOAT     | Implied Volatility
delta    | FLOAT     | Delta (BS Greeks)
gamma    | FLOAT     | Gamma (BS Greeks)
theta    | FLOAT     | Theta (BS Greeks, daily)
vega     | FLOAT     | Vega (BS Greeks, per 1% IV)

Indexes:
    idx_date            (date)
    idx_expiry          (expiry)
    idx_date_expiry     (date, expiry)
```

**Data Statistics**:
```
Total Rows:     ~15M rows
Date Range:     2022-04-16 ~ 2025-12-05
Sources:        Deribit (2022-2025.06), OKX (2025.06-)
```

**Important**:
- Prices are **normalized** (price/spot)
- Greeks are **BS Greeks** (OKX PA Greeks 자동 변환)

---

### 3. `eth_options_parsed`

**Purpose**: ETH 옵션 데이터 (btc_options_parsed와 동일 스키마)

**Schema**: Same as `btc_options_parsed`

**Note**: **Unlogged table** (faster but no crash recovery)

---

### 4. `futures_data_1m`

**Purpose**: 선물 1분봉 OHLCV 데이터

**Schema**:
```sql
Column    | Type                     | Description
----------+--------------------------+----------------------------------
timestamp | timestamp with time zone | 캔들 시각 (with timezone)
exchange  | text                     | 거래소 (e.g., 'Binance')
symbol    | text                     | 심볼 (e.g., 'BTC/USDT:USDT')
open      | numeric(18,8)            | Open price
high      | numeric(18,8)            | High price
low       | numeric(18,8)            | Low price
close     | numeric(18,8)            | Close price
volume    | numeric(28,8)            | Volume

Indexes:
    futures_data_1m_pkey                   PRIMARY KEY (exchange, symbol, timestamp)
    idx_futures_data_1m_symbol_timestamp   (symbol, timestamp DESC)
    idx_futures_data_1m_timestamp          (timestamp DESC)
```

---

## 🎯 Common Queries

### 1. OKX 데이터 로드 (특정 날짜)

```sql
-- 2025-12-05의 모든 OKX 옵션 데이터
SELECT *
FROM btc_options_parsed
WHERE date = '2025-12-05'
  AND exchange = 'OKEX'
ORDER BY symbol;
```

### 2. 특정 만기일 옵션들

```sql
-- 2025-12-26 만기 옵션들 (2025-12-05 기준)
SELECT
    symbol,
    strike,
    callput,
    iv,
    delta,
    close as option_price,
    spot_price_usd
FROM btc_options_parsed
WHERE date = '2025-12-05'
  AND expiry = '2025-12-26 08:00:00'
  AND exchange = 'OKEX'
ORDER BY strike;
```

### 3. ATM 옵션 찾기 (Delta 기준)

```sql
-- ATM 옵션: |delta| ≈ 0.50
SELECT
    symbol,
    strike,
    callput,
    delta,
    iv,
    close
FROM btc_options_parsed
WHERE date = '2025-12-05'
  AND expiry = '2025-12-26 08:00:00'
  AND exchange = 'OKEX'
  AND ABS(delta) BETWEEN 0.45 AND 0.55
ORDER BY callput, ABS(delta - 0.5);
```

### 4. OTM 옵션 찾기 (Delta 0.10)

```sql
-- Call OTM: delta ≈ 0.10
-- Put OTM: delta ≈ -0.10
SELECT
    symbol,
    strike,
    callput,
    delta,
    iv,
    close
FROM btc_options_parsed
WHERE date = '2025-12-05'
  AND expiry = '2025-12-26 08:00:00'
  AND exchange = 'OKEX'
  AND (
      (callput = 'c' AND delta BETWEEN 0.08 AND 0.12)
      OR (callput = 'p' AND delta BETWEEN -0.12 AND -0.08)
  )
ORDER BY callput, strike;
```

### 5. 시계열 데이터 (특정 심볼)

```sql
-- BTC-USD-251226-100000-C의 시계열
SELECT
    date,
    close,
    iv,
    delta,
    gamma,
    theta,
    vega,
    spot_price_usd
FROM btc_options_parsed
WHERE symbol = 'BTC-USD-251226-100000-C'
  AND exchange = 'OKEX'
  AND date >= '2025-11-01'
ORDER BY date;
```

### 6. IV Smile (특정 만기일)

```sql
-- IV smile curve
SELECT
    strike,
    callput,
    delta,
    iv,
    close as option_price,
    spot_price_usd
FROM btc_options_parsed
WHERE date = '2025-12-05'
  AND expiry = '2025-12-26 08:00:00'
  AND exchange = 'OKEX'
ORDER BY callput, strike;
```

### 7. 사용 가능한 만기일 목록

```sql
-- 2025-12-05에 거래 가능한 만기일들
SELECT DISTINCT expiry
FROM btc_options_parsed
WHERE date = '2025-12-05'
  AND exchange = 'OKEX'
ORDER BY expiry;
```

### 8. TTE (Time to Expiry) 필터링

```sql
-- TTE 7~30일 옵션들
SELECT
    symbol,
    strike,
    callput,
    tte,
    expiry,
    iv,
    delta
FROM btc_options_parsed
WHERE date = '2025-12-05'
  AND exchange = 'OKEX'
  AND tte BETWEEN 7 AND 30
ORDER BY expiry, strike;
```

---

## 🔧 Data Loading Scripts

### Location

```
/home/sqr/options_trading/data/
├── load_to_db.py          # Parquet → PostgreSQL 로딩
├── sync.py                # 데이터 동기화
├── status.py              # 데이터 상태 확인
└── reconstruct_missing.py # 누락 데이터 복구
```

### Usage: load_to_db.py

**Purpose**: Parquet 파일 → PostgreSQL 로딩

**Source**:
```
/home/sqr/data_archive/
├── options_market/{year}/{month}/{yyyymmdd}.parquet  # OHLCV
└── greeks/{year}/{month}/{yyyymmdd}.parquet          # Greeks
```

**Usage**:
```bash
# 특정 날짜부터 로딩
cd /home/sqr/options_trading/data
python load_to_db.py --start-date 2025-11-01

# 날짜 범위 지정
python load_to_db.py --start-date 2025-11-01 --end-date 2025-12-05

# Dry-run (실제 삽입 없이 테스트)
python load_to_db.py --start-date 2025-12-01 --dry-run
```

**How it works**:
1. Parquet 파일 읽기 (OHLCV + Greeks)
2. BTC 옵션만 필터 (`BTC-USD-*`)
3. 심볼 파싱 (strike, callput, expiry 추출)
4. Greeks와 OHLCV 병합
5. TTE 계산
6. 기존 데이터 삭제 후 INSERT

**Output**: `btc_options_parsed` 테이블에 삽입

---

## 🚨 Important Notes

### 1. Timezone = UTC

**CRITICAL**: 모든 timestamp는 UTC

```python
# ✅ GOOD
from datetime import datetime
current_time = datetime(2025, 12, 5, 12, 0)  # UTC

# ❌ BAD
import pytz
kst = pytz.timezone('Asia/Seoul')
current_time = datetime(2025, 12, 5, 21, 0, tzinfo=kst)
```

### 2. Expiry Time = UTC 08:00

**OKX options expire at UTC 08:00** (KST 17:00)

```python
expiry = datetime(2025, 12, 26, 8, 0)  # UTC 08:00 ✅
```

### 3. Greeks Differences

**Deribit vs OKX**:
- **Deribit**: Original BS Greeks (정상)
- **OKX**: PA Greeks (스케일 다름)
  - `load_to_db.py`가 자동으로 변환
  - `btc_options_hourly`는 BS Greeks로 재계산됨

**주의**: `btc_options_parsed`는 raw Greeks 포함 (OKX는 PA Greeks)

### 4. Symbol Format

**OKX format**:
```
BTC-USD-251226-100000-C
│   │   │      │       │
│   │   │      │       └─ C (Call) or P (Put)
│   │   │      └───────── Strike (100000 USD)
│   │   └──────────────── Expiry (YYMMDD: 2025-12-26)
│   └──────────────────── Quote currency (USD)
└──────────────────────── Base currency (BTC)
```

### 5. Price Units

**btc_options_parsed**:
- Prices are in **USD** (not normalized)
- `open`, `high`, `low`, `close` = USD

**btc_options_hourly**:
- Prices are **normalized** (price/spot)
- Need to multiply by spot to get USD

### 6. TTE Calculation

**TTE (Time to Expiry)** is in **days**:

```python
tte = (expiry - date).total_seconds() / (24 * 3600)
# e.g., tte = 21.5 (21.5 days to expiry)
```

---

## 🔍 Data Quality Checks

### Check Latest OKX Data

```sql
-- OKX 최신 데이터 날짜
SELECT MAX(date) as latest_date
FROM btc_options_parsed
WHERE exchange = 'OKEX';
```

### Check Data Completeness

```sql
-- 날짜별 옵션 개수 (gap 확인)
SELECT
    DATE(date) as day,
    COUNT(*) as total_options,
    COUNT(DISTINCT symbol) as unique_symbols
FROM btc_options_parsed
WHERE exchange = 'OKEX'
  AND date >= '2025-11-01'
GROUP BY DATE(date)
ORDER BY day DESC;
```

### Check Greeks Availability

```sql
-- Greeks NULL 비율
SELECT
    COUNT(*) as total_rows,
    COUNT(delta) as has_delta,
    COUNT(gamma) as has_gamma,
    COUNT(iv) as has_iv,
    ROUND(100.0 * COUNT(delta) / COUNT(*), 2) as pct_delta,
    ROUND(100.0 * COUNT(iv) / COUNT(*), 2) as pct_iv
FROM btc_options_parsed
WHERE exchange = 'OKEX'
  AND date = '2025-12-05';
```

---

## 🛠️ Troubleshooting

### Connection Failed

```
psycopg2.OperationalError: could not connect to server
```

**해결**:
```bash
# PostgreSQL 상태 확인
sudo systemctl status postgresql

# 실행 중인지 확인
ps aux | grep postgres

# 포트 확인
netstat -tuln | grep 5432
```

### Slow Queries

**증상**: 쿼리가 느림 (>5초)

**원인**: Index 활용 안 됨

**해결**:
1. **날짜 필터 필수**: `WHERE date = ...`
2. **Exchange 필터 추가**: `WHERE exchange = 'OKEX'`
3. **EXPLAIN 확인**:
   ```sql
   EXPLAIN ANALYZE
   SELECT * FROM btc_options_parsed
   WHERE date = '2025-12-05' AND exchange = 'OKEX';
   ```

### Missing Data

**증상**: 특정 날짜 데이터 없음

**확인**:
```bash
# Parquet 파일 확인
ls -lh /home/sqr/data_archive/options_market/2025/12/20251205.parquet

# 로그 확인
tail -100 /home/sqr/options_trading/logs/load_to_db.log
```

**복구**:
```bash
# 해당 날짜만 재로딩
cd /home/sqr/options_trading/data
python load_to_db.py --start-date 2025-12-05 --end-date 2025-12-05
```

---

## 📖 Related Documentation

- **OKX Options Specs**: `/home/sqr/knowledge/domain_knowledge/exchanges/okx/options_specifications.md`
- **OKX Fee Structure**: `/home/sqr/knowledge/domain_knowledge/exchanges/okx/fee_structure.md`
- **Data Loader (v2)**: `/home/sqr/options_trading/v2/data.py`
- **Options Backtester**: `/home/sqr/options_trading/v2/options_backtester.py`
- **Remote 1m Data (micky)**: `/home/sqr/knowledge/infrastructure/postgres_data_access.md`

---

**Last Updated**: 2025-12-23
**Verified By**: sqr
**Status**: Production-ready
**Data Coverage**: 2022-04-16 ~ 2025-12-05 (169M rows)
