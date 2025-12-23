# Deribit Options Database (Archive)

**⚠️ ARCHIVED**: 이 문서는 2024-07-28까지 운영된 Deribit 옵션 DB의 아카이브입니다.
**Current DB**: [spice_options_database.md](spice_options_database.md) (OKX + Deribit, 2025-12-05까지)

**Last Updated**: 2025-11-15
**Data Period**: 2022-04-19 ~ 2024-07-28 (운영 중단)
**Status**: ⚠️ 참고용 아카이브

---

## 📊 Database Overview

### Basic Information

| Item | Value |
|------|-------|
| **Database** | PostgreSQL 12 |
| **Database Name** | `sqr` |
| **Host** | localhost:5432 |
| **Total Size** | 55 GB |
| **Exchange** | Deribit |
| **Period** | 2022-04-19 ~ 2024-07-28 |
| **Status** | ⚠️ 운영 중단 (2024-07-28 이후 업데이트 없음) |

### Data Assets

- **BTC Options**: 2022-04-19 ~ 2024-07-28
- **ETH Options**: 2022-05-02 ~ 2024-07-28
- **Unique Symbols**: 84,336
- **Backtest Strategies**: 141

---

## 📋 Main Tables

### 1. option_pnl (옵션 손익 데이터)

**Size**: 7.1 GB | **Records**: 27,499,744

```sql
CREATE TABLE option_pnl (
    date                    TIMESTAMP NOT NULL,
    symbol                  VARCHAR(256) NOT NULL,
    iv                      DOUBLE PRECISION,
    delta                   DOUBLE PRECISION,
    gamma                   DOUBLE PRECISION,
    vega                    DOUBLE PRECISION,
    theta                   DOUBLE PRECISION,
    maturity                TIMESTAMP,
    underlying_price        DOUBLE PRECISION,
    option_pnl              DOUBLE PRECISION,
    delta_pnl               DOUBLE PRECISION,
    delta_hedged_option_pnl DOUBLE PRECISION,
    currency                VARCHAR(256),
    PRIMARY KEY (date, symbol)
);
```

**Data Statistics**:
- Records: 27,499,744
- Period: 2022-04-19 ~ 2024-07-28
- Trading Days: 832
- Unique Symbols: 84,336
- BTC: 14,887,804 (54.1%)
- ETH: 12,611,940 (45.9%)

**Sample Data**:
```
       symbol        |        date         |   iv   | delta | underlying_price
---------------------+---------------------+--------+-------+------------------
 btc-28jun24-120000-p | 2024-07-28 05:00:00 | 0.6252 |   0.0 |         67890.12
 btc-28jun24-120000-c | 2024-07-28 05:00:00 | 0.6252 |   1.0 |         67890.12
```

---

### 2. iv_surface (IV Surface)

**Size**: 1.9 GB | **Records**: 11,462,976

```sql
CREATE TABLE iv_surface (
    date     TIMESTAMP NOT NULL,
    callput  VARCHAR(10),      -- 'call' or 'put'
    maturity VARCHAR(10),      -- 'FD', '1W', '1M', etc
    delta    INTEGER,          -- 0-100
    iv       DOUBLE PRECISION,
    tte      DOUBLE PRECISION, -- Time to expiry (days)
    currency VARCHAR(10)       -- 'btc' or 'eth'
);
```

**Maturity Types**:
- FD (Front Day): 당일 만기
- 1W, 2W, 3W: 1-3주
- 1M, 2M, 3M: 1-3개월

---

### 3. term_structure (기간 구조)

**Size**: 11 GB | **Records**: 73,962,462

```sql
CREATE TABLE term_structure (
    date     TIMESTAMP,
    callput  VARCHAR(10),
    tte_day  INTEGER,          -- Time to expiry (days)
    delta    INTEGER,
    iv       DOUBLE PRECISION,
    currency VARCHAR(10)
);
```

**Data Statistics**:
- Period: 2022-04-19 ~ 2024-05-23
- Records: 73,962,462

---

### 4. backtest_portfolio (백테스트 포트폴리오)

**Size**: 5.3 GB | **Records**: 14,002,981

**Asset Distribution**:
- Option: 12,933,971 (92.4%)
- Future: 827,709 (5.9%)
- Swap: 241,301 (1.7%)

**Top Strategies**:
1. vrp: 6,878,804
2. vrp_0: 459,851
3. vrp_20: 449,283
4. vrp_44: 444,280
5. FW: 337,599

---

## 📊 All Tables (28 total)

### Production Tables
- `option_pnl` - 옵션 손익
- `iv_surface` - IV 서피스
- `term_structure` - 기간 구조
- `backtest_portfolio` - 백테스트 포트폴리오
- `backtest_result` - 백테스트 결과
- `mp_by_strategy` - 전략별 시장 포지션
- `greeks_by_strategy` - 전략별 그릭스
- `pnl_by_strategy` - 전략별 손익
- `portfolios` - 포트폴리오
- `signals` - 시그널
- `daily_product_returns` - 일별 상품 수익률

### Development Tables (dev_*)
- `dev_option_pnl`
- `dev_iv_surface`
- `dev_mp_by_strategy`
- `dev_ap_by_strategy`
- `dev_greek_by_strategy`
- `dev_greek_pnl_by_strategy`
- `dev_risk_matrix_by_strategy`
- `dev_strategy_signal_by_strategy`
- `dev_live_portfolio_by_strategy`

### Live Tables (live_*)
- `live_option_pnl`
- `live_iv_surface`
- `live_mp_by_strategy`
- `live_ap_by_strategy`
- `live_greek_by_strategy`
- `live_backtest_portfolio`
- `live_backtest_result`
- `live_risk_matrix_by_strategy`

---

## 🔐 Connection

```bash
# psql connection
psql postgres://sqr:sqr@localhost:5432/sqr

# or
psql -h localhost -p 5432 -d sqr -U sqr
```

---

## 📈 Sample Queries

### Option Data
```sql
-- Latest option data
SELECT * FROM option_pnl
ORDER BY date DESC
LIMIT 100;

-- BTC options only
SELECT * FROM option_pnl
WHERE currency = 'btc'
ORDER BY date DESC
LIMIT 100;

-- Date range
SELECT * FROM option_pnl
WHERE date BETWEEN '2024-07-01' AND '2024-07-31'
ORDER BY date DESC;

-- Daily statistics
SELECT
    currency,
    COUNT(*) as records,
    MIN(date) as start_date,
    MAX(date) as end_date,
    COUNT(DISTINCT symbol) as unique_symbols
FROM option_pnl
GROUP BY currency;
```

### IV Surface
```sql
-- Latest IV Surface
SELECT * FROM iv_surface
WHERE currency = 'btc'
ORDER BY date DESC
LIMIT 100;

-- Specific maturity
SELECT date, delta, iv
FROM iv_surface
WHERE maturity = '1M'
  AND callput = 'c'
  AND currency = 'btc'
ORDER BY date DESC, delta;
```

### Backtest Results
```sql
-- Strategies by position count
SELECT strategy_name, COUNT(*) as positions
FROM backtest_portfolio
GROUP BY strategy_name
ORDER BY positions DESC;

-- Recent positions for a strategy
SELECT * FROM backtest_portfolio
WHERE strategy_name = 'vrp'
ORDER BY date DESC
LIMIT 100;
```

---

## ⚠️ Important Notes

### 1. Data Collection Stopped

**Last Data Date**: 2024-07-28
**Reason**: Unknown (no automation found)
**Status**: No active collection

**Evidence**:
- No crontab entries
- No PM2 processes
- No background Python scripts
- Last update: 5 months ago

### 2. Current Alternative

**Use Instead**: [spice_options_database.md](spice_options_database.md)
- Database: `data_integration` (same server)
- Main Table: `btc_options_parsed`
- Data Sources: Deribit (138M) + OKX (31M)
- Period: 2022-04-16 ~ 2025-12-05 (updated)
- Total: 169M rows

### 3. Migration Notes

If migrating from `sqr` DB to `data_integration`:
```sql
-- Check data overlap
SELECT MIN(date), MAX(date) FROM sqr.option_pnl;
-- 2022-04-19 ~ 2024-07-28

SELECT MIN(date), MAX(date) FROM data_integration.btc_options_parsed;
-- 2022-04-16 ~ 2025-12-05

-- Deribit data overlap: 2022-04-19 ~ 2024-07-28
-- OKX new data: 2025-02-05 ~ 2025-12-05
```

---

## 📝 Maintenance (Historical)

### Database Size Check
```bash
psql postgres://sqr:sqr@localhost:5432/sqr \
  -c "SELECT pg_size_pretty(pg_database_size('sqr'));"
# Output: 55 GB
```

### Table Sizes
```bash
psql postgres://sqr:sqr@localhost:5432/sqr \
  -c "SELECT table_name,
             pg_size_pretty(pg_total_relation_size(quote_ident(table_name)::text)) AS size
      FROM information_schema.tables
      WHERE table_schema = 'public'
      ORDER BY pg_total_relation_size(quote_ident(table_name)::text) DESC
      LIMIT 10;"
```

---

## 🗄️ Archive Purpose

이 문서는 다음 목적으로 보존됩니다:

1. **Historical Reference**: 과거 백테스트 재현 시 참조
2. **Schema Documentation**: 테이블 구조 참고
3. **Migration Guide**: data_integration DB와 비교
4. **Legacy Code**: 옛날 코드에서 이 DB 참조하는 경우

**⚠️ Production Use**: 운영용으로는 [spice_options_database.md](spice_options_database.md) 사용

---

**Original Documentation**: `/home/sqr/db_documentation/` (deleted)
**Archived**: 2025-12-23
**Archived By**: sqr
