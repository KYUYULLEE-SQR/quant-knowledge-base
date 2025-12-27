# Corsair TimescaleDB (Options & Futures Data)

**Server**: corsair (192.168.50.203)
**Last Updated**: 2025-12-27
**Total Size**: ~55 GB
**Total Rows**: ~170M+

---

## Quick Start (접속 방법)

### SSH 접속
```bash
# SSH key 기반 접속 (권장)
ssh sqr@192.168.50.203

# SSH key 설정 스크립트 (최초 1회)
~/knowledge/technical_infrastructure/automation/setup_ssh_key.sh 192.168.50.203 sqr
```

### PostgreSQL 접속

**Docker 컨테이너 경유**:
```bash
# 직접 쿼리 실행
ssh sqr@192.168.50.203 "sudo docker exec candledb psql -U postgres -c 'SELECT count(*) FROM processed_btc_options'"

# 대화형 psql
ssh sqr@192.168.50.203 "sudo docker exec -it candledb psql -U postgres"
```

**Python 접속** (로컬에서):
```python
import pandas as pd
from sqlalchemy import create_engine

# SSH 터널 필요 (또는 직접 연결)
engine = create_engine('postgresql://postgres:postgres@192.168.50.203:5432/postgres')
df = pd.read_sql("SELECT * FROM processed_btc_options LIMIT 100", engine)
```

**SSH 터널 + Python** (권장):
```bash
# 터미널 1: SSH 터널
ssh -L 5433:localhost:5432 sqr@192.168.50.203
```
```python
# 터미널 2: Python
engine = create_engine('postgresql://postgres:postgres@localhost:5433/postgres')
```

---

## Server Specs

| Item | Value |
|------|-------|
| Hostname | corsair |
| IP | 192.168.50.203 |
| OS | Ubuntu (Linux 5.4.0) |
| RAM | 64 GB |
| User | sqr |
| Docker Container | candledb |
| Database | TimescaleDB (PostgreSQL 14) |
| Port | 5432 |
| Credentials | postgres / postgres |

---

## Database Tables Overview

| Table | Rows | Size | Description |
|-------|------|------|-------------|
| raw_okx_btc_options | 57.2M | 18 GB | OKX BTC 옵션 raw Greeks |
| raw_okx_eth_options | 53.1M | 16 GB | OKX ETH 옵션 raw Greeks |
| processed_eth_options | 17.9M | 5.0 GB | ETH 옵션 정제 데이터 |
| processed_btc_options | 16.9M | 4.6 GB | BTC 옵션 정제 데이터 |
| raw_deribit_btc_options | 8.2M | 3.3 GB | Deribit BTC 옵션 |
| raw_deribit_eth_options | 7.1M | 2.7 GB | Deribit ETH 옵션 |
| okx_btc_options_candles_1h | 6.1M | 2.4 GB | BTC 옵션 1시간 캔들 |
| okx_eth_options_candles_1h | 5.3M | 2.1 GB | ETH 옵션 1시간 캔들 |
| funding_rates_v2 | 2.8M | 488 MB | Binance/OKX 펀딩비 |
| futures_open_interest | - | 24 MB | 선물 미결제약정 |
| okex_option_symbols | - | 1.8 MB | 옵션 심볼 메타데이터 |
| symbol_metadata | - | 1.0 MB | 심볼 메타데이터 |

---

## Key Tables Schema

### processed_btc_options (주요 사용 테이블)

**Data Range**: 2022-04-16 ~ 2025-12-26 (16.9M rows)

```sql
Column          | Type              | Description
----------------|-------------------|-------------
ts              | timestamptz       | 타임스탬프 (PK)
inst_id         | text              | 옵션 심볼 (예: BTC-20250103-98000-C)
mark_px         | double precision  | 마크 가격
delta           | double precision  | 델타
gamma           | double precision  | 감마
theta           | double precision  | 세타
vega            | double precision  | 베가
mark_vol        | double precision  | 내재변동성 (IV)
underlying_px   | double precision  | 기초자산 가격
forward_px      | double precision  | 선도 가격
bid_px          | double precision  | 매수 호가
ask_px          | double precision  | 매도 호가
bid_sz          | double precision  | 매수 잔량
ask_sz          | double precision  | 매도 잔량
vol_bid         | double precision  | Bid IV
vol_ask         | double precision  | Ask IV
```

**Index**: `idx_processed_btc_options_ts` on (ts)

**Sample Query**:
```sql
SELECT ts, inst_id, mark_px, delta, mark_vol, underlying_px
FROM processed_btc_options
WHERE ts >= '2024-10-01' AND ts < '2024-10-08'
  AND inst_id LIKE 'BTC-%-P'  -- PUT options only
ORDER BY ts;
```

### raw_okx_btc_options (OKX Raw Data)

**Data Range**: 2022-04-15 ~ 2025-12-26 (57.2M rows)

```sql
Column          | Type              | Description
----------------|-------------------|-------------
ts              | timestamptz       | 타임스탬프
inst_id         | text              | 옵션 심볼
uly             | text              | 기초자산 (BTC-USD)
mark_px         | double precision  | 마크 가격
delta           | double precision  | 델타
gamma           | double precision  | 감마
theta           | double precision  | 세타 (daily decay)
vega            | double precision  | 베가
delta_bs        | double precision  | Black-Scholes 델타
gamma_bs        | double precision  | Black-Scholes 감마
theta_bs        | double precision  | Black-Scholes 세타
vega_bs         | double precision  | Black-Scholes 베가
lever           | double precision  | 레버리지
mark_vol        | double precision  | 마크 IV
bid_vol         | double precision  | Bid IV
ask_vol         | double precision  | Ask IV
real_vol        | double precision  | 실현 변동성
fwd_px          | double precision  | 선도 가격
vol_lv          | double precision  | 변동성 레벨
```

**Note**: OKX provides both PA (Price Agreement) and BS (Black-Scholes) Greeks.

### funding_rates_v2 (펀딩비)

**Data Range**: 2020-10-18 ~ 2025-12-26 (2.8M rows)

```sql
Column          | Type              | Description
----------------|-------------------|-------------
timestamp       | timestamptz       | 펀딩 시점 (PK)
symbol          | text              | 심볼 (예: BTCUSDT)
exchange        | text              | 거래소 (binance, okx)
funding_rate    | double precision  | 펀딩비 (8시간 기준)
mark_price      | double precision  | 마크 가격
index_price     | double precision  | 인덱스 가격
next_funding_time | timestamptz     | 다음 펀딩 시간
```

**Sample Query**:
```sql
SELECT timestamp, symbol, exchange, funding_rate
FROM funding_rates_v2
WHERE symbol = 'BTCUSDT'
  AND timestamp >= '2024-01-01'
ORDER BY timestamp;
```

---

## Data Quality Notes

### OKX Greeks (PA vs BS)

OKX provides two types of Greeks:
- **PA (Price Agreement)**: OKX's proprietary model, considers funding/forward
- **BS (Black-Scholes)**: Standard Black-Scholes model

**Recommendation**: Use PA Greeks for OKX-specific trading, BS for cross-exchange comparison.

### Time Zones

- All timestamps are in UTC (`timestamptz`)
- OKX funding: 00:00, 08:00, 16:00 UTC
- Binance funding: 00:00, 08:00, 16:00 UTC

### Missing Data Periods

Known gaps:
- 2023-06-05 ~ 2023-06-07: OKX API outage
- Check `ts` continuity before analysis

---

## Common Queries

### 1. Get Latest BTC Options Data
```sql
SELECT inst_id, mark_px, delta, mark_vol, underlying_px
FROM processed_btc_options
WHERE ts = (SELECT MAX(ts) FROM processed_btc_options)
ORDER BY inst_id;
```

### 2. Daily IV Surface (ATM)
```sql
SELECT
    DATE(ts) as date,
    AVG(mark_vol) FILTER (WHERE ABS(delta) BETWEEN 0.45 AND 0.55) as atm_iv
FROM processed_btc_options
WHERE ts >= '2024-01-01'
GROUP BY DATE(ts)
ORDER BY date;
```

### 3. Funding Rate History
```sql
SELECT
    DATE(timestamp) as date,
    AVG(funding_rate) * 3 * 365 as annualized_funding  -- 8h to annual
FROM funding_rates_v2
WHERE symbol = 'BTCUSDT' AND exchange = 'binance'
GROUP BY DATE(timestamp)
ORDER BY date;
```

### 4. Options Volume by Strike
```sql
SELECT
    SPLIT_PART(inst_id, '-', 3)::int as strike,
    COUNT(*) as samples,
    AVG(mark_vol) as avg_iv
FROM processed_btc_options
WHERE ts >= '2024-12-01'
  AND inst_id LIKE '%-C'  -- CALL
GROUP BY strike
ORDER BY strike;
```

---

## Maintenance

### Backup
```bash
# Docker volume backup
ssh sqr@192.168.50.203 "sudo docker exec candledb pg_dump -U postgres > /tmp/candledb_backup.sql"
```

### Check Table Sizes
```sql
SELECT
    table_name,
    pg_size_pretty(pg_total_relation_size(quote_ident(table_name))) as size
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY pg_total_relation_size(quote_ident(table_name)) DESC;
```

### Check Data Freshness
```sql
SELECT
    'processed_btc_options' as table_name,
    MAX(ts) as latest_data
FROM processed_btc_options
UNION ALL
SELECT
    'funding_rates_v2',
    MAX(timestamp)
FROM funding_rates_v2;
```

---

## Related Files

- SSH 자동화: `~/knowledge/technical_infrastructure/automation/setup_ssh_key.sh`
- OKX 수수료: `~/knowledge/domain_knowledge/exchanges/okx/fee_structure.md`
- Greeks 설명: `~/knowledge/domain_knowledge/exchanges/okx/options_specifications.md`

---

**Migration Note**: 이전 spice 서버에서 corsair로 이전됨 (2025-12).
