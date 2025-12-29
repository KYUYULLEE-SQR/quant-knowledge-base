# Spice Server - Options Database

**Purpose**: Spice 서버 로컬 옵션 데이터베이스 접속 및 사용 가이드
**Last Updated**: 2025-12-29
**Owner**: sqr
**Server**: spice (localhost)

---

## 📌 Quick Reference

| Item | Value |
|------|-------|
| **Database** | PostgreSQL 15 + TimescaleDB 2.24.0 |
| **Host** | 127.0.0.1:5432 (Docker) |
| **Database Name** | `data_integration` |
| **User** | sqr |
| **Password** | sqr |
| **Main Table** | `btc_options_parsed` |
| **Processed Table** | `processed_btc_options_hourly_v2` ⭐ NEW |
| **Total Rows** | 169M (raw) + 41M (processed) |
| **Data Period** | 2022-04-16 ~ 2025-12-27 |
| **Data Sources** | Deribit (138M rows), OKX (31M rows) |
| **Update Frequency** | Daily (OKX 데이터) |

---

## 🚀 TimescaleDB Hypertables (2025-12-27 Migration)

**All major time-series tables are now hypertables with compression:**

| Table | Rows | Before | After | Compression | Chunks |
|-------|------|--------|-------|-------------|--------|
| eth_options_ohlc_greek_deribit | 168M | 29 GB | 2.0 GB | 93% | 148 |
| trading_tickers | 36M | 10 GB | 5.0 GB | 50% | 149 |
| processed_eth_options_hourly | 22M | 5.2 GB | 1.3 GB | 75% | 193 |
| processed_btc_options_hourly | 16M | 4.0 GB | 1.0 GB | 75% | 192 |
| futures_data_1m | 11M | 2.3 GB | 0.2 GB | 91% | 184 |
| **Total** | **253M** | **~50.5 GB** | **~9.5 GB** | **81%** | **866** |

**Chunk Interval**: 7 days
**Compression Enabled**: Yes (all chunks compressed)
**Auto-Delete Policy**: No (disabled per user request)

---

## ⭐ Vol Surface Builder (2025-12-29) - 모범 사례

### 프로젝트 개요

| Item | Value |
|------|-------|
| **Project Location** | `/home/sqr/vol_surface_builder/` |
| **Server** | spice (localhost) |
| **Output Table** | `processed_btc_options_hourly_v2` |
| **Total Records** | 41,255,002 |
| **Data Period** | 2022-04-16 ~ 2025-12-27 (45개월) |
| **Processing Time** | ~45 min (8 parallel workers) |

### 목적

Raw 옵션 데이터(btc_options_hourly)를 **SVI(Stochastic Volatility Inspired) 모델**로 처리하여:
1. **Smooth Vol Surface** 생성 (arbitrage-free)
2. **Hourly Mark IV/Price** 계산
3. **Greeks 계산** (Delta, Gamma, Theta, Vega)
4. **Gap 보간** (거래 없는 시간대도 SVI로 interpolation)

### 결과 테이블: `processed_btc_options_hourly_v2`

```sql
CREATE TABLE processed_btc_options_hourly_v2 (
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    inst_id VARCHAR(100) NOT NULL,           -- e.g., BTC-USD-241025-60000-P
    strike NUMERIC NOT NULL,
    expiry TIMESTAMP WITH TIME ZONE NOT NULL,
    option_type CHAR(1) NOT NULL,            -- 'C' or 'P'
    spot_price NUMERIC NOT NULL,
    mark_price NUMERIC,                      -- SVI-derived price (USD)
    mark_iv NUMERIC,                         -- SVI-smoothed IV
    delta NUMERIC,
    gamma NUMERIC,
    theta NUMERIC,
    vega NUMERIC,
    raw_iv NUMERIC,                          -- Original exchange IV
    raw_price NUMERIC,                       -- Original exchange price
    PRIMARY KEY (timestamp, inst_id)
);

-- Indexes
CREATE INDEX idx_processed_v2_timestamp ON processed_btc_options_hourly_v2 (timestamp);
CREATE INDEX idx_processed_v2_expiry ON processed_btc_options_hourly_v2 (expiry);
```

### 데이터 품질 검증 결과 (2025-12-29)

| Check | Result | Notes |
|-------|--------|-------|
| Total Records | 41,255,002 | 45개월 처리 완료 |
| NULL Values | 0 | 모든 필수 컬럼 non-null |
| IV Range | 1.62% ~ 4561% | 극단 OTM 정상 |
| Delta Range | -1.0 ~ 1.0 | 유효 범위 내 |
| Gamma < 0 | 0건 | ✅ |
| Raw Data Match | 99.7% | 원본 데이터 매칭률 |
| Symbol Continuity | 99.3% (2024년) | First→Last 연속성 |

### SVI 모델 상세

**SVI (Stochastic Volatility Inspired)** 5-parameter model:

```
w(k) = a + b * (ρ * (k - m) + sqrt((k - m)² + σ²))

where:
- w = total variance = σ²(T) * T
- k = log-moneyness = ln(K/F)
- a, b, ρ, m, σ = SVI parameters
```

**Butterfly Arbitrage Constraint**: `b * (1 + |ρ|) < 4`

**Calendar Arbitrage Prevention**: Total variance space interpolation

### 파이프라인 코드

**Location**: `/home/sqr/vol_surface_builder/run_parallel_pipeline.py`

```python
#!/usr/bin/env python3
"""
Parallel Vol Surface Builder Pipeline

Usage:
    python run_parallel_pipeline.py
    python run_parallel_pipeline.py --workers 8 --start-month 2025-12
"""
import argparse
from multiprocessing import Pool
from datetime import datetime
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text

# Database connection
DB_URI = 'postgresql://sqr:sqr@127.0.0.1:5432/data_integration'
TARGET_TABLE = 'processed_btc_options_hourly_v2'

# Key parameters
WINDOW_HOURS = 4          # Rolling window for trade aggregation
MIN_TRADES_PER_EXPIRY = 5 # Minimum trades for SVI fitting
REG_STRENGTH = 0.15       # Temporal regularization strength
IV_MIN = 0.001            # Trust exchange data (no aggressive filtering)
IV_MAX = 5.0              # Allow high IV for deep OTM

class HourlySurfaceBuilder:
    """Build hourly vol surface snapshots using SVI"""

    def build_surfaces(self, trades_df, target_hours):
        """Build SVI surfaces for each target hour"""
        surfaces = {}
        window = pd.Timedelta(hours=self.window_hours)

        for hour in target_hours:
            # Get trades in window
            mask = (trades_df['timestamp'] >= hour - window) & \
                   (trades_df['timestamp'] < hour + window)
            window_trades = trades_df[mask]

            if len(window_trades) >= self.min_trades:
                surface = self._fit_hour_surface(window_trades, hour)
                if surface is not None:
                    surfaces[hour] = surface

        return surfaces

    def _fit_hour_surface(self, trades, hour):
        """Fit SVI parameters for each expiry"""
        params_by_expiry = {}

        for expiry, group in trades.groupby('expiry'):
            if len(group) < self.min_trades:
                continue

            T = (pd.to_datetime(expiry) - pd.to_datetime(hour)).total_seconds() \
                / (365.25 * 24 * 3600)

            if T <= 1/365:  # Skip < 1 day
                continue

            # Fit SVI with volume weighting
            weights = np.sqrt(group['vol'].values + 1)
            params = self.svi_fitter.fit_expiry(
                k=group['log_moneyness'].values,
                iv=group['iv'].values,
                T=T,
                weights=weights
            )

            if params is not None:
                params_by_expiry[expiry] = params

        return VolSurface(params_by_expiry, hour) if params_by_expiry else None

    def generate_hourly_snapshots(self, surfaces, all_options, spot_df):
        """Generate hourly snapshots with Greeks for all options"""
        results = []

        for hour, surface in surfaces.items():
            # Get spot price
            spot = self._get_spot(spot_df, hour)

            # Price all non-expired options
            valid_options = all_options[
                pd.to_datetime(all_options['expiry']) > hour
            ].copy()

            # Calculate IV from SVI surface
            ivs = [surface.get_iv(opt['strike'], opt['expiry'], spot)
                   for _, opt in valid_options.iterrows()]
            valid_options['mark_iv'] = ivs
            valid_options = valid_options.dropna(subset=['mark_iv'])

            # Calculate Greeks
            greeks = calc_greeks_vectorized(
                spot=np.full(len(valid_options), spot),
                strike=valid_options['strike'].values,
                tte=valid_options['tte'].values,
                iv=valid_options['mark_iv'].values,
                opt_type=valid_options['option_type'].values
            )

            # Build result records
            for i, (_, opt) in enumerate(valid_options.iterrows()):
                results.append({
                    'timestamp': hour,
                    'inst_id': opt['instrument_name'],
                    'strike': opt['strike'],
                    'expiry': opt['expiry'],
                    'option_type': opt['option_type'],
                    'spot_price': spot,
                    'mark_price': greeks['price'][i],
                    'mark_iv': valid_options.iloc[i]['mark_iv'],
                    'delta': greeks['delta'][i],
                    'gamma': greeks['gamma'][i],
                    'theta': greeks['theta'][i],
                    'vega': greeks['vega'][i],
                })

        return pd.DataFrame(results)

def process_month(month_tuple):
    """Process a single month (worker function)"""
    year, month = month_tuple

    # Load raw data
    trades_df, all_options, spot_df = load_month_data(year, month)

    # Filter outliers (minimal - trust exchange data)
    trades_clean = filter_iv_outliers(trades_df, iv_min=0.001, iv_max=5.0)

    # Build surfaces
    builder = HourlySurfaceBuilder(
        window_hours=4,
        min_trades_per_expiry=5,
        reg_strength=0.15
    )
    surfaces = builder.build_surfaces(trades_clean, target_hours)

    # Generate snapshots
    hourly_data = builder.generate_hourly_snapshots(surfaces, all_options, spot_df)

    # Remove duplicates
    hourly_data = hourly_data.drop_duplicates(
        subset=['timestamp', 'inst_id'],
        keep='first'
    )

    # Save to database
    save_to_db(hourly_data, year, month)

    return {'month': f'{year}-{month:02d}', 'records': len(hourly_data)}

def main():
    # Create table
    create_target_table()

    # Get all months
    months = get_available_months()  # [(2025, 12), (2025, 11), ...]

    # Process in parallel
    with Pool(processes=8) as pool:
        results = list(pool.imap(process_month, months))

    print(f"Total records: {sum(r['records'] for r in results):,}")

if __name__ == "__main__":
    main()
```

### 프로젝트 파일 구조

```
/home/sqr/vol_surface_builder/
├── run_parallel_pipeline.py    # ⭐ Main pipeline (8-worker parallel)
├── src/
│   ├── __init__.py
│   ├── iv_calculator.py        # IV calculation & outlier filtering
│   ├── svi_fitter.py           # SVI model fitting
│   ├── greeks.py               # Greeks calculation (vectorized)
│   └── surface_builder.py      # Vol surface construction
├── output/                      # Intermediate parquet files
└── pipeline_full.log           # Execution log
```

### 핵심 모듈 설명

**1. `src/svi_fitter.py`** - SVI 모델 피팅

```python
class SVIFitter:
    """
    SVI (Stochastic Volatility Inspired) model fitter

    Parameters:
    - reg_strength: Temporal regularization (0.15 default)
    - min_points: Minimum points per expiry for fitting

    Constraints enforced:
    - Butterfly: b * (1 + |ρ|) < 4
    - Calendar: Total variance monotonic in T
    """

    def fit_expiry(self, k, iv, T, weights=None):
        """
        Fit SVI parameters for a single expiry

        Args:
            k: log-moneyness array
            iv: implied volatility array
            T: time to expiry (years)
            weights: optional volume weights

        Returns:
            dict with {a, b, rho, m, sigma} or None if fit fails
        """
```

**2. `src/greeks.py`** - Greeks 계산

```python
def calc_greeks_vectorized(spot, strike, tte, iv, opt_type, r=0.0):
    """
    Vectorized Black-Scholes Greeks calculation

    Args:
        spot: spot prices array
        strike: strike prices array
        tte: time to expiry (years) array
        iv: implied volatility array
        opt_type: 'C' or 'P' array
        r: risk-free rate (default 0.0)

    Returns:
        dict with {price, delta, gamma, theta, vega}
    """
```

**3. `src/iv_calculator.py`** - IV 필터링

```python
def filter_iv_outliers(trades_df, iv_min=0.001, iv_max=5.0):
    """
    Filter IV outliers (minimal filtering - trust exchange data)

    Changed from aggressive filtering (15%-300%) to permissive (0.1%-500%)
    because real trades exist at various IV levels.
    """
```

### 사용법

```bash
# 전체 데이터 처리 (45개월, ~45분)
cd /home/sqr/vol_surface_builder
python run_parallel_pipeline.py --workers 8

# 특정 월만 처리
python run_parallel_pipeline.py --start-month 2024-10 --end-month 2024-10

# 로그 확인
tail -f pipeline_full.log
```

### Raw vs Processed 비교

| Metric | Raw (btc_options_hourly) | Processed (v2) |
|--------|-------------------------|----------------|
| Records | 15,962,922 | 41,255,002 |
| Coverage | 거래 있을 때만 | 매 시간 (SVI interpolation) |
| IV | Raw exchange IV | SVI-smoothed mark IV |
| Greeks | Raw exchange Greeks | BS Greeks (재계산) |
| Continuity | Gaps 있음 | 99.3% 연속성 (2024년) |

### SVI Smoothing 효과

| Metric | Raw OKX | SVI Processed |
|--------|---------|---------------|
| IV Jump (consecutive hour) | Mean 2.35%, Max 32.3% | Mean 1.26%, Max 12.1% |
| Smoothness | Bumpy | **47% smoother** |
| Delta Correlation | - | 0.99 (vs raw) |
| Price Correlation | - | 0.998 (vs raw) |

### 백테스트 사용 시 주의사항

1. **Backtest vs Real Trading Error**: ~80 bps median slippage
2. **Conservative Adjustment**: 10-20% PnL 감소 예상
3. **December 2025 Gap**: 12/06 ~ 12/21 raw 데이터 없음 (거래소 문제)
4. **2024년 데이터**: 99.3% symbol continuity, gap 없음

### Python 사용 예시

```python
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine('postgresql://sqr:sqr@127.0.0.1:5432/data_integration')

# 특정 시점의 모든 옵션 데이터 로드
query = """
SELECT
    timestamp, inst_id, strike, expiry, option_type,
    spot_price, mark_price, mark_iv, delta, gamma, theta, vega,
    raw_iv, raw_price
FROM processed_btc_options_hourly_v2
WHERE timestamp = '2024-10-15 12:00:00+00'
ORDER BY expiry, strike
"""
df = pd.read_sql(query, engine)

# 특정 심볼의 시계열 (백테스트용)
query = """
SELECT timestamp, mark_iv, mark_price, delta, gamma
FROM processed_btc_options_hourly_v2
WHERE inst_id = 'BTC-USD-241025-60000-P'
ORDER BY timestamp
"""
ts = pd.read_sql(query, engine)
# → 2792 records, 100% hourly continuity
```

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

- **OKX Options Specs**: `/home/sqr/knowledge/exchanges/okx/options_specifications.md`
- **OKX Fee Structure**: `/home/sqr/knowledge/exchanges/okx/fee_structure.md`
- **Data Loader (v2)**: `/home/sqr/options_trading/v2/data.py`
- **Options Backtester**: `/home/sqr/options_trading/v2/options_backtester.py`
- **Remote 1m Data (micky)**: `/home/sqr/knowledge/infrastructure/postgres_data_access.md`

---

**Last Updated**: 2025-12-29
**Verified By**: sqr
**Status**: Production-ready
**Data Coverage**:
- Raw: 2022-04-16 ~ 2025-12-27 (169M rows)
- Processed v2: 2022-04-16 ~ 2025-12-27 (41M rows, SVI-smoothed)
