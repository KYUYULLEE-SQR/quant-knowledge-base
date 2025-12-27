# Common Exchange Definitions

거래소 공통 정의 및 유틸리티.

## Files

| File | Purpose |
|------|---------|
| `greeks.md` | Greeks 정의 (Delta, Gamma, Theta, Vega) |
| `expiry.md` | 만기 표기법 컨벤션 |
| `greeks_converter.py` | Greeks 단위 변환 유틸리티 |

## Greeks Unit Standards

**Deribit 표준** (USD units despite BTC-margined):

| Greek | Unit | Description |
|-------|------|-------------|
| Delta | Dimensionless | 0-1 for calls, -1 to 0 for puts |
| Gamma | per $1 move | Delta change per $1 BTC price move |
| Theta | **USD/day** | Daily decay in USD |
| Vega | **USD/1% IV** | Value change per 1% IV move |

**OKX 비교**:
- PA Greeks = BTC 단위 (Theta: BTC/day, Vega: BTC/1%IV)
- BS Greeks = USD 단위 (Deribit과 동일)
