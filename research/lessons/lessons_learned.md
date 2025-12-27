# Lessons Learned (실패 사례 & 교훈)

**Purpose**: 실제 백테스트 실패 사례 및 교훈 (재발 방지)
**Last Updated**: 2025-12-25
**Owner**: sqr

---

## 📌 Quick Reference

| Category | Lesson | Impact | Prevention |
|----------|--------|--------|------------|
| **Look-ahead Bias** | 미래 데이터 사용 (t+1 정보) | Sharpe 2-4× 과대 | Signal shift test |
| **100% Fill 가정** | Maker order 전량 체결 가정 | Sharpe 35% 과대 | 30% fill ratio |
| **MDD = 0 문제** | Entry/Exit만 NAV 평가 | MDD 과소평가 | Hourly MTM |
| **Greeks 단위 혼동** | PA (BTC) vs BS (USD) 혼동 | PnL 10-100× 오류 | BS 통일 |
| **Data Snooping** | 동일 데이터로 반복 튜닝 | Overfitting | Walk-forward |
| **Survivorship Bias** | 상장 유지 종목만 포함 | 성과 30-50% 과대 | Full universe |
| **거래 비용 누락** | 수수료/슬리피지 미반영 | Sharpe 50%+ 과대 | T-cost model |

---

## 🔴 Category 1: Look-Ahead Bias

### Lesson 1.1: Rolling `center=True` 함정
**문제**: `rolling(20, center=True)` → 미래 10개 데이터 포함
**결과**: Backtest Sharpe 3.2 → Live 0.8 (4× gap)
```python
# ❌ df['ma'] = df['price'].rolling(20, center=True).mean()
# ✅ df['ma'] = df['price'].rolling(20).mean()  # center=False default
```

### Lesson 1.2: Resample 후 Forward Fill
**문제**: `resample().last().ffill()` → 09:00 값이 08:00에 채워짐
**결과**: Sharpe 2.1 → Live 0.3
```python
# ❌ df_hourly = df_1min.resample('1H').last().ffill()
# ✅ df_hourly = df_1min.resample('1H').last().dropna()
```

### Lesson 1.3: Feature/Label 시점 불일치
**문제**: Feature 계산에 t+1 데이터 사용
**결과**: Train accuracy 85% → Live 52%
```python
# ✅ Feature: df['vol'] = df['ret'].rolling(20).std()  # t-19 ~ t
# ✅ Label:   df['label'] = df['ret'].shift(-1)        # t+1
```

**Detection**: Signal shift test (+1 bar) → Sharpe 50%+ 하락 시 bias 의심

---

## 🟡 Category 2: Fill & Execution

### Lesson 2.1: Maker 100% Fill 가정
**문제**: OKX 옵션 실측 fill ratio = 30%
**결과**: Sharpe 3.2 → 2.1 (35% gap)
```python
# ❌ filled_qty = order_qty
# ✅ filled_qty = order_qty * 0.3
```

### Lesson 2.2: Slippage 미반영
**문제**: Mid price 체결 가정, spread 무시
**결과**: Spread 2% → 거래당 1% 손실, Sharpe 2.5 → -0.3
```python
# ✅ execution_price = ask if side == 'buy' else bid
```

### Lesson 2.3: Reorder 비용 누락
**문제**: 70% unfilled → repost 시 aggressive price 필요
**결과**: Net alpha 50% 감소

**📚 참조**: `trading/cost-models/fill_probability.md`

---

## 🟠 Category 3: Data Quality

### Lesson 3.1: Survivorship Bias
**문제**: 현재 상장 종목만 → 과거 상폐 종목 누락
**결과**: Sharpe 2.8 → 1.2 (130% gap)
```python
# ✅ WHERE list_date <= :ts AND (delist_date IS NULL OR delist_date > :ts)
```

### Lesson 3.2: Corporate Actions 미반영
**문제**: 2:1 분할 → 가격 -50% 손실로 인식
**해결**: Adjusted price 사용 (Bloomberg, Yahoo `Adj Close`)

### Lesson 3.3: Timezone Mismatch
**문제**: OKX 만기 UTC 08:00, 백테스트 KST → 9시간 차이
```python
# ✅ expiry = pd.Timestamp('2024-12-27 08:00', tz='UTC')
```

---

## 🔵 Category 4: Greeks & Options

### Lesson 4.1: OKX PA Gamma 단위 불명
**문제**: PA → BS 변환 공식 실패 (75% error)
```python
# ✅ gamma = opt['gammaBS']  # PA Gamma 사용 금지
```

### Lesson 4.2: PA/BS 혼용
**문제**: Portfolio Greeks 계산 시 PA + BS 합산 → 무의미
```python
# ✅ Portfolio Greeks는 모두 BS (USD units)로 통일
```

### Lesson 4.3: IV Stale Data
**문제**: OKX IV 업데이트 1분, 백테스트 1초 → 60× 거래 과대
```python
# ✅ for ts in iv_changes[iv_changes != 0].index: trade()
```

**📚 참조**: `exchanges/_common/greeks.md`

---

## 🟣 Category 5: Backtesting Mechanics

### Lesson 5.1: MDD = 0 문제
**문제**: Entry/Exit만 NAV 평가 → 중간 손실 미반영
**결과**: Backtest MDD 0% → Live MDD -18%
```python
# ✅ for ts in hourly_timestamps:
#        nav = cash + sum(pos.qty * get_mark_price(ts))
```

### Lesson 5.2: Reconciliation 누락
**문제**: 정합성 검증 없이 PnL 보고 → 90% 오차 발견
```python
# ✅ assert positions[i] == positions[i-1] + trade.qty * trade.side
# ✅ assert abs(final_cash - initial_cash - cash_flow) < 1e-6
```

### Lesson 5.3: Parameter Overfitting
**문제**: 전체 기간에서 100개 파라미터 조합 테스트
**결과**: Backtest Sharpe 3.8 → Live 0.5 (7.6× gap)
```python
# ✅ Walk-forward: train 2개월 → test 1개월, 파라미터 고정
```

**📚 참조**: `agent_prompts/claude_code/rules/10_backtesting_integrity.md`

---

## 🟢 Category 6: Data Snooping

### Lesson 6.1: 같은 데이터 100번 실험
**문제**: p-value 0.05 × 100번 = 5개 우연히 유의
**해결**: Bonferroni correction (0.05 / N) 또는 hold-out set

### Lesson 6.2: Cherry-Picking Periods
**문제**: 2024-Q4 (Sharpe 3.2)만 보고, 2022 (Sharpe -0.5) 무시
```python
# ✅ print(f"Avg: {np.mean(results)}, Worst: {min(results)}")
```

---

## 💰 Category 7: Transaction Costs

### Lesson 7.1: 수수료 누락
**문제**: HFT 100 trades/day, taker 0.03% → Fees = 50% of PnL
```python
# ✅ net_pnl = gross_pnl - entry_notional * fee_rate - exit_notional * fee_rate
```

### Lesson 7.2: Maker Rebate 과신
**문제**: Rebate -0.02%, 하지만 fill 30% → 실제 rebate 1/3
**결과**: Expected $73k → Actual $22k, opportunity cost -$30k = Net -$8k

**📚 참조**: `trading/cost-models/transaction_cost.md`

---

## 📊 Impact Matrix

| Mistake | Sharpe Gap | PnL Gap | Detection | Fix Cost |
|---------|------------|---------|-----------|----------|
| Look-ahead bias | 2-4× | 100-400% | Signal shift | High |
| 100% fill | 1.35× | 35% | Fill ratio data | Medium |
| Survivorship bias | 1.5-2× | 50-100% | Universe check | High |
| Slippage omission | 1.3-2× | 30-100% | Spread data | Low |
| Fee omission | 1.2-1.5× | 20-50% | Fee calc | Low |
| MDD = 0 | N/A | -20% MDD | Hourly MTM | Medium |
| Overfitting | 3-7× | 200-600% | OOS validation | Medium |
| Greeks mix | N/A | 10-100× | Unit check | Low |

**High Priority**: Look-ahead, Survivorship, Overfitting, Fill ratio

---

## 🔧 Prevention Checklist

### Pre-Backtest
- [ ] Timezone: 모두 UTC
- [ ] Survivorship: 상장폐지 종목 포함
- [ ] Rolling: `center=False`
- [ ] Resample: `bfill()` 금지
- [ ] Fees: Maker/Taker 구분
- [ ] Fill ratio: 30% maker / 100% taker

### Post-Backtest
- [ ] Signal shift test: Sharpe 변화 < 50%
- [ ] Parameter stability: ±20% 변화 시 Sharpe 유지
- [ ] Walk-forward: OOS Sharpe > 0.5 × IS Sharpe
- [ ] Position continuity: trades = position changes
- [ ] Cash conservation: trades + fees = cash flow
- [ ] MDD ≠ 0: Hourly MTM 확인
- [ ] Sharpe < 3: 초과 시 의심

---

## 📚 Related

- `lessons_learned/common_pitfalls.md` - Bias 종류 및 탐지
- `experiment_design/methodology.md` - Walk-forward, 변인 통제
- `backtest_standards/backtesting_nav_policy.md` - Hourly MTM
- `trading/cost-models/` - Fill, Slippage, T-cost

---

**Version**: 2.0 (Condensed)
**Contributing**: 새 실패 사례 발견 시 추가
