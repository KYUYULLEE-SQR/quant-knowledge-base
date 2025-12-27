# Cost Models

백테스트용 거래비용 모델.

## Files

| File | Purpose |
|------|---------|
| `transaction_cost.md` | 거래비용 종합 모델 |
| `slippage_model.md` | 슬리피지 모델 |
| `fill_probability.md` | 체결확률 모델 |
| `position_sizing.md` | 포지션 사이징 |

## Key Principles

1. **Realistic Costs**: 수수료 + 슬리피지 + 마켓임팩트
2. **Conservative Estimate**: 실제보다 높게 추정
3. **Sensitivity Test**: 0.5x, 1x, 2x 비용으로 테스트
