# 전략별 지식

**Purpose**: 전략별 특수 지식, 주의사항, 모범 사례 보관

---

## 사용 규칙

### 보관 기준

다음 정보가 포함된 전략 문서화:

1. **전략 개요**: 핵심 로직, 가설
2. **데이터 요구사항**: 필요한 Greeks, 데이터 소스
3. **주의사항**: 전략별 함정, 리스크
4. **백테스트 가이드**: 전략별 검증 방법
5. **파라미터 범위**: 안정적인 파라미터 범위

### 파일명 규칙

```
strategy_name.md
```

**예시**:
- `short_put_vrp.md` (Volatility Risk Premium)
- `gamma_scalping.md`
- `delta_neutral_straddle.md`

---

## 구조 예시

```markdown
# [전략명]

**Type**: Volatility/Directional/Arbitrage
**Complexity**: Low/Medium/High
**Status**: Research/Backtest/Live

---

## Strategy Overview

간단한 설명

## Core Logic

1. Entry condition
2. Exit condition
3. Risk management

## Data Requirements

- Greeks: delta, gamma, vega
- Market data: IV surface, underlying price
- Frequency: 1m/1h/1d

## Backtesting Considerations

- 주의사항 1
- 주의사항 2

## Parameter Ranges

| Parameter | Safe Range | Optimal | Notes |
|-----------|-----------|---------|-------|
| IV threshold | 10-20% | 15% | ... |

## Known Issues

- 문제 1
- 문제 2

## References

- Related KB docs
```

---

## 현재 상태

**파일 수**: 0 (전략 문서 없음)

전략이 성숙하면 이 디렉토리에 문서화하세요.
