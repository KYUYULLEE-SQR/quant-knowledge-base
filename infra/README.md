# Infra

데이터베이스, 서버, 자동화 스크립트.

## Structure

```
infra/
├── databases/        # DB 접속 정보 (micky, corsair, spice)
└── scripts/          # 자동화 스크립트
```

## Quick Find

| Looking for... | File |
|----------------|------|
| Futures 데이터 (micky) | `databases/micky_postgres.md` |
| Options Greeks (corsair) | `databases/corsair_timescaledb.md` |
| Options raw (spice) | `databases/spice_options_db.md` |
| SSH 키 설정 | `scripts/setup_ssh_key.sh` |
| 프로젝트 초기화 | `scripts/bootstrap_project_state.py` |

## Server Map

| Server | IP | Data |
|--------|-----|------|
| micky | 192.168.50.3 | Futures 1m candles (273M rows) |
| corsair | 192.168.50.203 | Options Greeks (170M rows) |
| spice | localhost | Options raw (169M rows) |

## Related

- `~/knowledge/exchanges/` - 거래소 API 정보
