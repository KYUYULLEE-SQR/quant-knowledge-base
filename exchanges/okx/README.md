# OKX Exchange

OKX 거래소 관련 상세 스펙.

## Files

| File | Purpose |
|------|---------|
| `fee_structure.md` | 수수료 체계 (VIP 티어, DMM) |
| `options_specifications.md` | 옵션 스펙 (BTC/ETH, 만기, Greeks) |
| `api_specifications.md` | REST/WebSocket API |
| `api_examples.md` | API 사용 예시 |
| `order_types.md` | 주문 유형 |
| `position_limits.md` | 포지션 한도 |
| `margin_requirements.md` | 마진 요구사항 |
| `settlement_rules.md` | 정산 규칙 |

## Quick Reference

- **Options**: European-style, Cash-settled
- **Greeks**: PA-based (not Black-Scholes)
- **Fee Tier**: VIP9 DMM = maker -1bps, taker +3bps
