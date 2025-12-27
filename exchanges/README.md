# Exchanges

거래소별 스펙, 수수료, API 정보.

## Structure

```
exchanges/
├── _common/          # Cross-exchange (Greeks, expiry conventions)
├── okx/              # OKX specifics
├── bybit/            # Bybit specifics
└── binance/          # Binance specifics
```

## Quick Find

| Looking for... | File |
|----------------|------|
| OKX 수수료 | `okx/fee_structure.md` |
| Bybit 수수료 | `bybit/fee_structure.md` |
| Greeks 정의 (PA vs BS) | `_common/greeks.md` |
| 만기 표기법 (D/W/M/Q) | `_common/expiry.md` |
| 옵션 스펙 | `<exchange>/options_specifications.md` |

## Related

- `~/knowledge/trading/cost-models/` - 슬리피지, 체결 모델
- `~/knowledge/infra/databases/` - 시세 데이터 접속
