# Options Database Access (로컬)

**Purpose**: 로컬 옵션 데이터베이스 접속 및 사용 가이드
**Last Updated**: 2025-12-23
**Owner**: sqr
**Server**: localhost (127.0.0.1)

---

## 📌 Quick Reference

| Item | Value |
|------|-------|
| **Database** | PostgreSQL |
| **Host** | 127.0.0.1:5432 |
| **Database Name** | `data_integration` |
| **User** | sqr |
| **Password** | sqr |
| **Main Table** | `btc_options_hourly` |
| **Data Period** | 2022-04-16 ~ 2025-12-05 |
| **Total Rows** | ~15M rows |
| **Data Source** | Deribit (2022-2025.06), OKX (2025.06-) |

---

## 🚀 Quick Start (30초)

### Python (Recommended)

```python
from v2.data import DataLoader
from datetime import datetime

# DataLoader 초기화 (config/settings.yaml 자동 로드)
loader = DataLoader()

# 특정 시각의 옵션 데이터
current_time = datetime(2024, 10, 5, 12, 0)
expiry = datetime(2024, 12, 27, 8, 0)  # UTC 08:00

options = loader.get_options(date=current_time, expiry=expiry)
spot = loader.get_spot(date=current_time)

print(f"Loaded {len(options)} options at spot ${spot:,.2f}")
```

### SQL (Direct)

```bash
psql -h 127.0.0.1 -U sqr -d data_integration
```

```sql
-- 2024-10-05 12:00 시점의 ATM 옵션들
SELECT
    symbol, strike, callput, price, delta, gamma, theta, vega
FROM btc_options_hourly
WHERE date = '2024-10-05 12:00:00'
    AND expiry = '2024-12-27 08:00:00'
    AND ABS(delta) BETWEEN 0.45 AND 0.55  -- ATM
ORDER BY strike;
```

---

## 📊 Database Schema

### Table: `btc_options_hourly`

```sql
CREATE TABLE btc_options_hourly (
    date TIMESTAMP NOT NULL,        -- 데이터 시각 (UTC)
    symbol VARCHAR(50),             -- BTC-USD-250131-50000-C
    strike FLOAT,                   -- 행사가 (USD)
    callput VARCHAR(10),            -- 'c' or 'p'
    expiry TIMESTAMP,               -- 만기일 (UTC 08:00)
    price FLOAT,                    -- Normalized price (price/spot)
    spot FLOAT,                     -- BTC spot price (USD)
    iv FLOAT,                       -- Implied Volatility
    delta FLOAT,                    -- Delta (BS Greeks)
    gamma FLOAT,                    -- Gamma (BS Greeks)
    theta FLOAT,                    -- Theta (BS Greeks, daily)
    vega FLOAT,                     -- Vega (BS Greeks, per 1% IV)
    PRIMARY KEY (date, symbol)
);

CREATE INDEX idx_date ON btc_options_hourly(date);
CREATE INDEX idx_expiry ON btc_options_hourly(expiry);
CREATE INDEX idx_date_expiry ON btc_options_hourly(date, expiry);
```

### Column Details

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `date` | TIMESTAMP | 데이터 시각 (UTC) | 2024-10-05 12:00:00 |
| `symbol` | VARCHAR | OKX symbol 형식 | BTC-USD-241227-65000-C |
| `strike` | FLOAT | 행사가 (USD) | 65000.0 |
| `callput` | VARCHAR | Call='c', Put='p' | c |
| `expiry` | TIMESTAMP | 만기일 (UTC 08:00) | 2024-12-27 08:00:00 |
| `price` | FLOAT | Normalized (price/spot) | 0.05 |
| `spot` | FLOAT | BTC spot price (USD) | 65000.0 |
| `iv` | FLOAT | Implied volatility | 0.50 |
| `delta` | FLOAT | Delta (BS) | 0.50 |
| `gamma` | FLOAT | Gamma (BS) | 0.00015 |
| `theta` | FLOAT | Theta (BS, daily) | -0.002 |
| `vega` | FLOAT | Vega (BS, per 1% IV) | 0.15 |

---

## 🔧 Config 설정

### File: `config/settings.yaml`

**Location**: `/home/sqr/options_trading/config/settings.yaml`

```yaml
database:
  # 로컬 옵션 데이터
  options:
    host: "127.0.0.1"
    port: 5432
    database: "data_integration"
    user: "sqr"
    password: "sqr"
```

**환경변수 오버라이드**:
```bash
export DB_OPTIONS_HOST="192.168.1.100"
export DB_OPTIONS_PASSWORD="new_password"
```

---

## 📚 DataLoader API

### Class: `v2.data.DataLoader`

#### `get_options(date, expiry, callput=None)`

**특정 시각의 옵션 데이터 로드**

```python
from v2.data import DataLoader
from datetime import datetime

loader = DataLoader()

# 모든 옵션 (Call + Put)
options = loader.get_options(
    date=datetime(2024, 10, 5, 12, 0),
    expiry=datetime(2024, 12, 27, 8, 0)
)

# Call만
calls = loader.get_options(
    date=datetime(2024, 10, 5, 12, 0),
    expiry=datetime(2024, 12, 27, 8, 0),
    callput='c'
)

# Returns: pd.DataFrame or None
```

**Returns**:
- `pd.DataFrame`: Columns = [symbol, strike, callput, expiry, price, spot, iv, delta, gamma, theta, vega]
- `None`: 데이터 없음

#### `get_spot(date)`

**특정 시각의 spot price**

```python
spot = loader.get_spot(date=datetime(2024, 10, 5, 12, 0))
# Returns: float (USD) or None
```

#### `get_closest_expiry(date, tenor)`

**Tenor로 만기일 찾기**

```python
expiry = loader.get_closest_expiry(
    date=datetime(2024, 10, 5, 12, 0),
    tenor='SM'  # Second Month
)
# Returns: datetime (UTC 08:00) or None
```

---

## 🎯 Common Queries

### 1. ATM 옵션 찾기

```sql
-- ATM: |delta| ≈ 0.50
SELECT
    symbol, strike, callput, price, delta
FROM btc_options_hourly
WHERE date = '2024-10-05 12:00:00'
    AND expiry = '2024-12-27 08:00:00'
    AND ABS(delta) BETWEEN 0.45 AND 0.55
ORDER BY callput, ABS(delta - 0.5);
```

### 2. OTM 옵션 찾기 (Delta 0.10)

```sql
-- Call OTM: delta ≈ 0.10
-- Put OTM: delta ≈ -0.10
SELECT
    symbol, strike, callput, price, delta
FROM btc_options_hourly
WHERE date = '2024-10-05 12:00:00'
    AND expiry = '2024-12-27 08:00:00'
    AND (
        (callput = 'c' AND delta BETWEEN 0.08 AND 0.12)
        OR (callput = 'p' AND delta BETWEEN -0.12 AND -0.08)
    )
ORDER BY callput, strike;
```

### 3. 특정 Strike 시계열

```sql
-- Strike 65000 Call의 시계열 데이터
SELECT
    date, price, iv, delta, gamma, theta
FROM btc_options_hourly
WHERE strike = 65000
    AND callput = 'c'
    AND expiry = '2024-12-27 08:00:00'
    AND date BETWEEN '2024-10-01' AND '2024-10-07'
ORDER BY date;
```

### 4. 만기일 목록

```sql
-- 2024-10-05에 사용 가능한 만기일들
SELECT DISTINCT expiry
FROM btc_options_hourly
WHERE date = '2024-10-05 12:00:00'
ORDER BY expiry;
```

### 5. IV Smile

```sql
-- IV smile curve (2024-10-05 12:00, expiry 2024-12-27)
SELECT
    strike,
    callput,
    delta,
    iv,
    price
FROM btc_options_hourly
WHERE date = '2024-10-05 12:00:00'
    AND expiry = '2024-12-27 08:00:00'
ORDER BY callput, strike;
```

---

## 🔍 Data Quality

### Greeks Consistency (중요!)

**Deribit 기간** (2022-04-16 ~ 2025-06-01):
- Original BS Greeks (정상)
- 직접 사용 가능

**OKX 기간** (2025-06-01 ~):
- Original: PA Greeks (스케일 다름, Gamma ≈ BS × Spot)
- **자동 변환**: `v2.data.recalculate_bs_greeks()` 함수로 IV → BS Greeks 재계산
- DataLoader가 자동으로 처리

**확인**:
```python
from v2.data import DataLoader, OKX_START_DATE
from datetime import datetime

loader = DataLoader()

# Deribit 기간
options_deribit = loader.get_options(
    date=datetime(2024, 5, 1, 12, 0),
    expiry=datetime(2024, 6, 28, 8, 0)
)
print("Deribit gamma:", options_deribit.iloc[0]['gamma'])

# OKX 기간 (재계산됨)
options_okx = loader.get_options(
    date=datetime(2025, 7, 1, 12, 0),
    expiry=datetime(2025, 8, 29, 8, 0)
)
print("OKX gamma (recalculated):", options_okx.iloc[0]['gamma'])
```

### Data Coverage

```sql
-- 데이터 커버리지 확인
SELECT
    DATE(date) as day,
    COUNT(DISTINCT DATE_TRUNC('hour', date)) as hours_covered,
    COUNT(*) as total_options
FROM btc_options_hourly
WHERE date >= '2024-10-01' AND date < '2024-11-01'
GROUP BY DATE(date)
ORDER BY day;
```

**Expected**: 24 hours/day (24/7 market)

---

## 🚨 Important Notes

### 1. Timezone = UTC

**CRITICAL**: 모든 timestamp는 UTC

```python
# ✅ GOOD
from datetime import datetime
current_time = datetime(2024, 10, 5, 12, 0)  # UTC

# ❌ BAD
import pytz
kst = pytz.timezone('Asia/Seoul')
current_time = datetime(2024, 10, 5, 21, 0, tzinfo=kst)
```

### 2. Expiry Time = UTC 08:00

**OKX/Deribit options expire at UTC 08:00** (KST 17:00)

```python
expiry = datetime(2024, 12, 27, 8, 0)  # UTC 08:00 ✅
```

### 3. Price = Normalized

**Price is normalized** (price / spot)

```python
# DB에서 로드한 가격
normalized_price = 0.05  # BTC 단위

# USD 가격 계산
spot = 65000  # USD
option_price_usd = normalized_price * spot  # $3,250
```

### 4. Greeks = BS (Black-Scholes)

**모든 Greeks는 BS Greeks** (일관성 확보)

- Delta: -1 to 1
- Gamma: Small (~0.0001 for ATM)
- Theta: Daily decay (BTC/day)
- Vega: Per 1% IV change

---

## 🛠️ Troubleshooting

### Connection Failed

```
psycopg2.OperationalError: could not connect to server
```

**해결**:
1. PostgreSQL 실행 확인:
   ```bash
   sudo systemctl status postgresql
   sudo systemctl start postgresql
   ```

2. 접속 테스트:
   ```bash
   psql -h 127.0.0.1 -U sqr -d data_integration
   ```

### No Data

```python
options = loader.get_options(...)
# Returns None or empty DataFrame
```

**원인**:
- 해당 시각에 데이터 없음
- 만기일이 이미 지남
- Timezone 잘못됨 (KST vs UTC)

**디버깅**:
```python
# 사용 가능한 날짜 확인
query = "SELECT DISTINCT date FROM btc_options_hourly ORDER BY date DESC LIMIT 10"

# 사용 가능한 만기일 확인
query = """
SELECT DISTINCT expiry
FROM btc_options_hourly
WHERE date = '2024-10-05 12:00:00'
ORDER BY expiry
"""
```

### Gamma 값 이상

**Gamma 값이 너무 큼** (e.g., 10.0)

**원인**: OKX PA Greeks (raw, 재계산 안 됨)

**해결**: DataLoader는 자동으로 BS Greeks 재계산. 직접 SQL 쿼리 시:
```python
from v2.data import recalculate_bs_greeks
df_corrected = recalculate_bs_greeks(df_raw)
```

---

## 📖 Related Documentation

- **Backtester**: `/home/sqr/options_trading/v2/options_backtester.py`
- **Data Loader**: `/home/sqr/options_trading/v2/data.py`
- **Config**: `/home/sqr/options_trading/config/settings.yaml`
- **OKX Specs**: `/home/sqr/knowledge/exchanges/okx/options_specifications.md`
- **Remote 1m Data**: `/home/sqr/knowledge/infrastructure/postgres_data_access.md`

---

**Last Updated**: 2025-12-23
**Status**: Production-ready, Greeks consistency verified
**Maintainer**: sqr
