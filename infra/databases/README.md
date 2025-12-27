# Database Documentation

데이터베이스 접속 및 스키마 문서.

## Servers

| Server | IP | Database | Docs |
|--------|-----|----------|------|
| micky | 192.168.50.3 | PostgreSQL (Futures 1m) | `micky_postgres.md` |
| corsair | 192.168.50.203 | TimescaleDB (Options Greeks) | `corsair_timescaledb.md` |
| spice | localhost | PostgreSQL (Options raw) | `spice_options_db.md` |

## Other Docs

| File | Purpose |
|------|---------|
| `deribit_options_db_archive.md` | Deribit 데이터 (archived) |
| `market_data_sources.md` | 데이터 소스 목록 |

## Quick Connect

```bash
# micky (futures)
psql -h 192.168.50.3 -U sqr -d futures_data

# corsair (greeks)
psql -h 192.168.50.203 -U sqr -d options_greeks

# spice (local)
psql -U sqr -d options_raw
```
