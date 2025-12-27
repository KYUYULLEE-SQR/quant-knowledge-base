# Research

연구 방법론, 백테스트 표준, 실패 교훈.

## Structure

```
research/
├── experiment/       # 실험 설계 (Phase 1→2, 단일 변수)
├── standards/        # NAV 정책, 성능 지표
└── lessons/          # 실패 사례, 흔한 실수
```

## Quick Find

| Looking for... | File |
|----------------|------|
| 실험 설계 원칙 | `experiment/methodology.md` |
| NAV/MDD 계산 | `standards/nav_policy.md` |
| Sharpe 계산 | `standards/metrics.md` |
| Look-ahead bias | `lessons/pitfalls.md` |
| 흔한 실수 28개 | `lessons/mistakes.md` |

## Key Principles

1. **Phase 1 먼저**: 한 번에 하나의 변수만 변경
2. **Hourly MTM**: MDD=0 버그 방지
3. **Reconciliation**: Trade-by-trade 정합성 필수

## Related

- `~/knowledge/rules/05_experiment_guidelines.md` - 실험 규칙
- `~/knowledge/rules/10_backtesting_integrity.md` - 백테스트 정합성
