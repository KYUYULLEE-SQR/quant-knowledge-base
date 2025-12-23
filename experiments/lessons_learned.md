# Lessons Learned (실패 사례 & 교훈)

**Purpose**: 실제 실험/백테스트에서 발생한 실패 사례 및 교훈 정리 (재발 방지)

**Last Updated**: 2025-12-23
**Owner**: sqr
**Environment**: micky (data), spice (backtest), vultr (trading)

---

## 📌 Quick Reference

| Category | Lesson | Impact | Prevention |
|----------|--------|--------|------------|
| **Look-ahead Bias** | 미래 데이터 사용 (t+1 정보) | Sharpe 과대평가 2-3배 | Signal shift test |
| **100% Fill 가정** | Maker order 전량 체결 가정 | Sharpe 과대평가 35% | 30% fill ratio 적용 |
| **MDD = 0 문제** | Entry/Exit만 NAV 평가 | MDD 과소평가 (0%) | Hourly MTM evaluation |
| **Greeks 단위 혼동** | PA (BTC) vs BS (USD) 혼동 | PnL 계산 오류 10-100배 | greeks_definitions.md 참조 |
| **Data Snooping** | 동일 데이터로 반복 튜닝 | Overfitting, live 실패 | Walk-forward validation |
| **Survivorship Bias** | 상장 유지 종목만 포함 | 성과 과대평가 30-50% | 상장폐지 종목 포함 |
| **거래 비용 누락** | 수수료/슬리피지 미반영 | Sharpe 과대평가 50%+ | T-cost model 필수 |

---

## 🔴 Category 1: Look-Ahead Bias (미래 정보 누출)

### Lesson 1.1: Rolling Window의 `center=True` 함정

**배경**:
- 이동평균 계산 시 pandas `rolling(..., center=True)` 사용
- 의도: "현재 시점 기준 양방향 윈도우"
- 실제: **미래 데이터 포함** (t+N/2 까지)

**실패 사례**:
```python
# ❌ Wrong: center=True는 미래 데이터 포함
df['ma_20'] = df['price'].rolling(20, center=True).mean()

# 예시 데이터:
# t=10: ma_20 = mean(price[0:20])  ← t=11~19의 미래 데이터 포함!
```

**결과**:
- Backtest Sharpe: **3.2** (과대평가)
- Live Sharpe: **0.8** (실제)
- **Gap: 4배**

**교훈**:
```python
# ✅ Correct: center=False (default)
df['ma_20'] = df['price'].rolling(20, center=False).mean()

# 또는 명시적으로
df['ma_20'] = df['price'].rolling(20).mean()  # 과거 20개만 사용
```

**Detection**:
```python
# Signal shift test
signal_shifted = signal.shift(1)  # 1 bar 미래로 shift
backtest_result_shifted = run_backtest(signal_shifted)

# If Sharpe drops significantly → look-ahead bias 가능성
if sharpe_original > sharpe_shifted * 1.5:
    print("⚠️ Possible look-ahead bias detected")
```

**Related**: `experiments/common_pitfalls.md` - Look-ahead bias section

---

### Lesson 1.2: Resampling 후 Forward Fill 함정

**배경**:
- 1분 데이터 → 1시간 resample
- 결측치 처리: `ffill()` 사용
- 의도: "마지막 값으로 채우기"
- 실제: **미래 값이 과거로 전파**

**실패 사례**:
```python
# ❌ Wrong: resample 후 ffill → 미래 데이터 누출
df_hourly = df_1min.resample('1H').last()
df_hourly = df_hourly.ffill()  # ← 위험!

# 예시:
# 08:00 missing → ffill → 09:00 값이 08:00에 채워짐 (미래 정보)
```

**결과**:
- 결측치 있는 기간: **성과 과대평가**
- Sharpe 2.1 → **Live에서 0.3** (재현 불가)

**교훈**:
```python
# ✅ Correct: 과거 값으로만 채우기
df_hourly = df_1min.resample('1H').last()
df_hourly = df_hourly.bfill(limit=0)  # Backward fill 금지

# 또는 결측치 skip
df_hourly = df_hourly.dropna()
```

**Rule**: Resample 후에는 **bfill 절대 금지**, ffill도 신중히

---

### Lesson 1.3: 라벨 생성과 피처 계산 시점 불일치

**배경**:
- Label: t+1 시점의 수익률 (미래)
- Feature: t 시점의 지표
- **실수**: Feature 계산에 t+1 데이터 사용

**실패 사례**:
```python
# ❌ Wrong: 라벨과 피처를 같은 루프에서 계산
for t in range(len(df)):
    # Label (미래 수익률)
    df.loc[t, 'label'] = df.loc[t+1, 'ret']  # OK

    # Feature (현재 지표)
    df.loc[t, 'volatility'] = df.loc[t-20:t+20, 'ret'].std()  # ❌ t+1~t+20 포함!
```

**결과**:
- Training accuracy: **85%**
- Live accuracy: **52%** (random guess)

**교훈**:
```python
# ✅ Correct: 라벨과 피처를 분리하여 계산
# Step 1: Feature 계산 (과거 데이터만)
df['volatility'] = df['ret'].rolling(20).std()  # t-19 ~ t

# Step 2: Label 생성 (미래 데이터)
df['label'] = df['ret'].shift(-1)  # t+1

# Step 3: 타이밍 검증
assert df.loc[100, 'volatility'] == df.loc[80:100, 'ret'].std()
assert df.loc[100, 'label'] == df.loc[101, 'ret']
```

**Checklist**:
- [ ] Feature는 t 시점 이전 데이터만 사용
- [ ] Label은 t+1 이후 데이터 사용
- [ ] 계산 순서 명확히 분리

---

## 🟡 Category 2: Fill Probability & Execution (체결 가정)

### Lesson 2.1: Maker Order 100% Fill 가정

**배경**:
- Fair IV 전략: 과대평가 옵션 short (maker order)
- 백테스트 가정: **100% fill** at limit price
- 현실: **30% fill** (OKX BTC options 실측)

**실패 사례**:
```python
# ❌ Wrong: 모든 주문이 체결된다고 가정
for signal in signals:
    if signal['iv_spread'] > 0.10:
        trades.append({
            'quantity': 10,  # ❌ 전량 체결 가정
            'price': signal['mark_price'] - 5
        })
```

**결과**:
- Backtest Sharpe: **3.2**
- Live Sharpe: **2.1** (30% fill)
- **Gap: 35% 과대평가**

**교훈**:
```python
# ✅ Correct: 30% fill ratio 적용
for signal in signals:
    if signal['iv_spread'] > 0.10:
        intended_qty = 10
        filled_qty = intended_qty * 0.3  # 30% fill

        trades.append({
            'quantity': filled_qty,  # ✅ 3 contracts
            'price': signal['mark_price'] - 5,
            'unfilled': intended_qty - filled_qty  # 7 contracts
        })

        # Repost unfilled portion
        if unfilled > 0:
            repost_queue.append(unfilled)
```

**Related**: `modeling/fill_probability.md` - Empirical data (30% fill)

---

### Lesson 2.2: Slippage 미반영 (Taker Order)

**배경**:
- Taker order (market order) 사용
- 백테스트: Mid price로 체결 가정
- 현실: **Ask (매수) / Bid (매도)** 로 체결

**실패 사례**:
```python
# ❌ Wrong: Mid price로 체결
execution_price = mid_price  # ❌ 슬리피지 무시
```

**결과**:
- Spread 2% 시: **거래당 1% 손실** (25 bps × 2)
- 100 거래/월: **손실 100%**
- Sharpe 2.5 → **Live에서 -0.3**

**교훈**:
```python
# ✅ Correct: Spread slippage 반영
spread = ask - bid
slippage = spread / 2

if side == 'buy':
    execution_price = ask  # 또는 mid + slippage
else:
    execution_price = bid  # 또는 mid - slippage

# Cost calculation
notional = execution_price * quantity
slippage_cost = slippage * quantity
fee = notional * fee_rate
total_cost = slippage_cost + fee
```

**Related**: `modeling/slippage_estimation.md` - Spread-based model

---

### Lesson 2.3: Partial Fill 후 Reorder 비용 누락

**배경**:
- Maker order 30% fill → 70% unfilled
- Unfilled portion repost → 추가 비용 발생
- 백테스트: **Reorder 비용 미반영**

**실패 사례**:
```python
# ❌ Wrong: Unfilled portion을 무시
filled_qty = order_qty * 0.3
# Unfilled 70%는 그냥 사라짐... (opportunity cost 무시)
```

**결과**:
- 실제 거래: 70% unfilled → **alpha 손실**
- Reorder 시: 더 aggressive price 필요 → **spread 손실**
- **Net alpha 50% 감소**

**교훈**:
```python
# ✅ Correct: Reorder cost 반영
filled_qty = order_qty * 0.3
unfilled_qty = order_qty * 0.7

# Reorder with more aggressive price
reorder_price = mid_price - 10  # ← 5 tick 손실
reorder_cost = unfilled_qty * 5  # Opportunity cost

# Total cost
total_cost = fees + slippage + reorder_cost
```

**Related**: `modeling/fill_probability.md` - Reorder logic

---

## 🟠 Category 3: Data Quality & Integrity (데이터 품질)

### Lesson 3.1: Survivorship Bias (상장폐지 종목 누락)

**배경**:
- 백테스트 universe: 현재 상장된 종목만
- 과거 상장폐지 종목 누락
- **편향**: 살아남은 종목 = 성과 좋은 종목

**실패 사례**:
```python
# ❌ Wrong: 현재 상장 종목만 백테스트
universe = get_current_listed_tickers()  # 2025년 현재 상장 종목
backtest(universe, start='2020-01-01', end='2024-12-31')

# 문제: 2020-2024 사이 상장폐지된 종목 누락
# → 실패한 종목들이 제외됨
```

**결과**:
- Backtest Sharpe: **2.8**
- Live Sharpe: **1.2** (신규 상장 종목 포함)
- **Gap: 130% 과대평가** (살아남은 종목만 선택)

**교훈**:
```python
# ✅ Correct: 각 시점의 실제 상장 종목 사용
def get_universe_at_time(timestamp):
    """시점별 실제 상장 종목 조회 (상장폐지 포함)."""
    return db.query("""
        SELECT ticker FROM listings
        WHERE list_date <= :timestamp
          AND (delist_date IS NULL OR delist_date > :timestamp)
    """, timestamp=timestamp)

# 백테스트 시 매 시점마다 universe 갱신
for timestamp in timestamps:
    universe = get_universe_at_time(timestamp)
    positions = rebalance(universe, timestamp)
```

**Data Requirement**:
- `list_date`: 상장일
- `delist_date`: 상장폐지일 (NULL = 현재 상장중)

**Related**: `experiments/common_pitfalls.md` - Survivorship bias

---

### Lesson 3.2: Corporate Actions (액면분할, 배당) 미반영

**배경**:
- 주식 2:1 액면분할
- 백테스트: Raw price 사용 → **가격 급락**처럼 보임
- 현실: 2주로 분할, 가격은 1/2

**실패 사례**:
```python
# ❌ Wrong: Raw price 사용
# 2024-06-15: $100 → 2024-06-16: $50 (2:1 분할)
# → 백테스트는 -50% 손실로 인식!
```

**결과**:
- Stop-loss 발동 (-50% 손실)
- 실제: 0% 손실 (2배 주식 보유)
- **백테스트 무의미**

**교훈**:
```python
# ✅ Correct: Adjusted price 사용
df['price_adjusted'] = df['price_raw'] * df['adjustment_factor']

# Adjustment factor:
# - 액면분할 2:1 → factor = 2.0
# - 배당 $5 → factor = (price - 5) / price
```

**Data Source**:
- Bloomberg: Adjusted prices (default)
- Yahoo Finance: `Adj Close` 컬럼
- OKX: No corporate actions (crypto)

---

### Lesson 3.3: Timezone Mismatch (UTC vs Local)

**배경**:
- OKX 옵션 만기: **UTC 08:00**
- 백테스트 타임존: **KST (UTC+9)**
- **문제**: 만기 시간 9시간 차이

**실패 사례**:
```python
# ❌ Wrong: KST 기준으로 만기 처리
expiry_time = pd.Timestamp('2024-12-27 08:00', tz='Asia/Seoul')
# → 실제 만기: UTC 08:00 = KST 17:00
# → 9시간 차이!
```

**결과**:
- 옵션 만기 **9시간 전에** 청산
- Theta decay 손실 누락
- **PnL -5% 차이**

**교훈**:
```python
# ✅ Correct: 모든 시간은 UTC 기준
expiry_time = pd.Timestamp('2024-12-27 08:00', tz='UTC')

# 또는
df.index = df.index.tz_localize('UTC')

# Conversion to local (display only)
expiry_kst = expiry_time.tz_convert('Asia/Seoul')  # 17:00 KST
```

**Rule**: Internal data는 **항상 UTC**, display만 local timezone

---

## 🔵 Category 4: Greeks & Options (Greeks 관련)

### Lesson 4.1: OKX PA Gamma 단위 불명

**배경**:
- OKX Greeks: PA (BTC units) vs BS (USD units)
- PA Theta/Vega: `PA × BTC_price ≈ BS` (검증됨, 1-6% error)
- PA Gamma: **단위 불명**, 변환 공식 실패

**실패 사례**:
```python
# ❌ Wrong: PA Gamma를 Theta/Vega와 동일하게 변환
gamma_pa = 11.99
gamma_usd = gamma_pa * btc_price  # ← 검증 실패 (75% error)
```

**검증 결과**:
- Hypothesis: `PA_Gamma = BS_Gamma × BTC_price`
- Test: 287 options, ATM 위주
- Result: **75% average error** (일부는 5-10%, 대부분 실패)

**교훈**:
```python
# ✅ Correct: PA Gamma 사용 금지, BS Gamma만 사용
gamma_bs = opt['gammaBS']  # ✅ 신뢰 가능
gamma_pa = opt['gammaPA']  # ❌ 사용 금지 (단위 불명)

# Portfolio gamma tracking
portfolio_gamma = sum(position.quantity * position.gamma_bs for position in positions)
```

**Status**: OKX support 문의 필요 (PA Gamma 단위 확인)

**Related**: `exchanges/greeks_definitions.md` - PA Gamma 섹션

---

### Lesson 4.2: Greeks 단위 혼동 (PA vs BS)

**배경**:
- Portfolio Greeks 계산 시 PA/BS 혼용
- PA (BTC units) + BS (USD units) = **의미 없는 값**

**실패 사례**:
```python
# ❌ Wrong: PA와 BS를 섞어서 합산
portfolio_theta = sum([
    position1.theta_pa,  # -0.001 BTC/day
    position2.theta_bs,  # -110 USD/day ← 단위 다름!
])
# Result: -110.001 (???) 무의미한 값
```

**결과**:
- Theta decay tracking 실패
- Risk management 불가능
- **Live 운영 중단**

**교훈**:
```python
# ✅ Correct: 모두 BS (USD units)로 통일
from greeks_converter import GreeksConverter

converter = GreeksConverter(btc_price=88500)

portfolio_theta_bs = sum([
    converter.okx_pa_to_usd(pos.theta_pa, 'theta') if pos.source == 'PA'
    else pos.theta_bs
    for pos in positions
])

# Result: -320.5 USD/day ✅ 의미 있는 값
```

**Rule**: Portfolio 집계는 **항상 BS (USD units)** 사용

**Related**: `exchanges/greeks_converter.py` - Conversion utility

---

### Lesson 4.3: Implied Volatility Stale Data

**배경**:
- OKX mark IV 업데이트 빈도: **1분**
- 백테스트: **1초** 단위 거래
- **문제**: IV가 1분간 고정 → 오래된 데이터로 거래

**실패 사례**:
```python
# ❌ Wrong: 1초 단위로 IV 사용
for timestamp in timestamps_1s:
    iv = get_mark_iv(timestamp)  # ← 1분간 동일한 값
    if iv > fair_iv + 0.10:
        trade()  # 같은 IV로 60번 거래!
```

**결과**:
- 동일 조건에서 **60개 거래** 발생
- 실제: IV 업데이트 후 1개만 가능
- **거래 빈도 60배 과대평가**

**교훈**:
```python
# ✅ Correct: IV 업데이트 시점에만 거래
iv_series = get_mark_iv_1min()  # 1분 단위
iv_changes = iv_series.diff()  # IV 변화 감지

for timestamp in iv_changes[iv_changes != 0].index:
    iv = iv_series[timestamp]
    if iv > fair_iv + 0.10:
        trade()  # IV 변화 시점에만 거래
```

**Rule**: 신호 빈도 ≤ 데이터 업데이트 빈도

---

## 🟣 Category 5: Backtesting Mechanics (백테스트 구조)

### Lesson 5.1: MDD = 0 문제 (Entry/Exit만 NAV 평가)

**배경**:
- NAV 계산: Entry/Exit 시점만 평가
- 포지션 보유 중: **MTM 평가 없음**
- **문제**: 중간 손실 미반영 → MDD = 0

**실패 사례**:
```python
# ❌ Wrong: Entry/Exit만 NAV 계산
t=0:  Entry position, NAV = $100,000
t=1-167: (no evaluation) ← 중간 손실 -$20,000 무시
t=168: Close position, NAV = $105,000

# Result: MDD = 0% (wrong!)
# Reality: MDD = -20% (t=50에서 발생)
```

**결과**:
- Backtest MDD: **0%**
- Live MDD: **-18%**
- **Risk 완전 오판**

**교훈**:
```python
# ✅ Correct: 매 시간 Mark-to-Market NAV 계산
for timestamp in hourly_timestamps:
    nav = portfolio.cash

    for position in portfolio.positions:
        mark_price = get_mark_price(timestamp, position.symbol)
        mtm_value = position.quantity * mark_price
        unrealized_pnl = mtm_value - position.entry_value
        nav += unrealized_pnl

    nav_series[timestamp] = nav

# 일별 resample 후 MDD 계산
nav_daily = nav_series.resample('D').last()
mdd = calculate_mdd(nav_daily)  # ✅ 정확한 MDD
```

**Related**: `experiments/backtesting_nav_policy.md` - Hourly MTM

---

### Lesson 5.2: Trade-by-Trade Reconciliation 누락

**배경**:
- 백테스트 결과: Sharpe 2.8, Total PnL $50,000
- **검증 없음**: Position/Cash/PnL 정합성
- **문제 발견**: Live 운영 시 PnL 불일치

**실패 사례**:
```python
# ❌ Wrong: PnL만 보고, 정합성 검증 없음
total_pnl = sum(trade.pnl for trade in trades)
print(f"Total PnL: ${total_pnl}")  # ← 믿을 수 없는 값
```

**발견된 버그**:
- Position 누적 오류 (close 누락)
- Cash 불일치 (fee 누락)
- **실제 PnL: $5,000** (90% 오차)

**교훈**:
```python
# ✅ Correct: Trade-by-trade reconciliation
def validate_backtest(trades, positions, pnl):
    # 1. Position continuity
    for i, trade in enumerate(trades):
        expected_pos = positions[i-1] + trade.quantity * trade.side
        assert positions[i] == expected_pos, f"Position mismatch at {i}"

    # 2. Cash conservation
    cash_flow = sum(trade.quantity * trade.price + trade.fee for trade in trades)
    assert abs(final_cash - initial_cash - cash_flow) < 1e-6

    # 3. PnL attribution
    realized_pnl = sum(trade.realized_pnl for trade in trades)
    unrealized_pnl = sum(pos.mtm_pnl for pos in final_positions)
    total_pnl_calc = realized_pnl + unrealized_pnl

    assert abs(total_pnl - total_pnl_calc) < 1e-2, "PnL mismatch"

    print("✅ All reconciliation checks passed")
```

**Related**: `~/.claude/rules/10_backtesting_integrity.md` - Full checklist

---

### Lesson 5.3: Parameter Overfitting (파라미터 과최적화)

**배경**:
- 백테스트 기간: 2024-Q4 (3개월)
- 파라미터 튜닝: 100개 조합 테스트
- **문제**: 같은 데이터로 반복 최적화 → Overfitting

**실패 사례**:
```python
# ❌ Wrong: 전체 기간에서 최적 파라미터 찾기
best_sharpe = 0
for threshold in np.arange(0.05, 0.20, 0.01):  # 15개
    for lookback in range(10, 50, 5):  # 8개
        sharpe = backtest(threshold, lookback, data_full)
        if sharpe > best_sharpe:
            best_sharpe = sharpe
            best_params = (threshold, lookback)

# Result: Sharpe 3.8 (overfitted)
```

**결과**:
- Backtest Sharpe: **3.8** (최적 파라미터)
- Live Sharpe: **0.5** (overfitting)
- **Gap: 7.6배**

**교훈**:
```python
# ✅ Correct: Walk-forward optimization
train_period = data['2024-10':'2024-11']  # 2개월
test_period = data['2024-12']  # 1개월

# Train에서 최적 파라미터 찾기
best_params = grid_search(train_period)

# Test에서 검증 (단 1회, 파라미터 변경 금지)
test_sharpe = backtest(best_params, test_period)

# 또는 Cross-validation
for fold in kfold(data, n_splits=5):
    train, test = fold
    params = grid_search(train)
    sharpe = backtest(params, test)
    results.append(sharpe)

avg_sharpe = np.mean(results)  # ✅ 현실적인 추정
```

**Rule**:
- Train/Test 명확히 분리
- Test 기간 데이터는 **절대** 파라미터 튜닝에 사용 금지
- 최소 2-3개 기간에서 검증

**Related**: `experiments/methodology.md` - Walk-forward validation

---

## 🟢 Category 6: Data Snooping & P-hacking (데이터 스누핑)

### Lesson 6.1: 같은 데이터로 100번 실험

**배경**:
- 동일 데이터셋 (2024-Q4)에서 100개 전략 테스트
- **문제**: 우연히 잘 맞는 전략 발견 (p-hacking)
- False discovery rate 증가

**실패 사례**:
```python
# ❌ Wrong: 같은 데이터로 반복 실험
for strategy_id in range(100):
    sharpe = backtest(strategy_id, data_2024q4)
    if sharpe > 2.0:
        print(f"✅ Strategy {strategy_id} works! Sharpe {sharpe}")

# Result: 5개 전략이 Sharpe > 2.0
# → 100번 시도하면 5% (우연히) 성공 가능
```

**통계적 문제**:
- p-value 0.05 기준 → **100번 중 5번은 우연히 유의**
- Multiple testing correction 없음
- **False positive rate: 95%+**

**교훈**:
```python
# ✅ Correct: Bonferroni correction
n_strategies = 100
adjusted_pvalue = 0.05 / n_strategies  # 0.0005

# 또는 새로운 데이터로 검증
train_data = data_2024q4
test_data = data_2025q1  # ← 새 데이터

for strategy_id in range(100):
    sharpe_train = backtest(strategy_id, train_data)

    if sharpe_train > 2.0:
        # 새 데이터로 검증 (단 1회)
        sharpe_test = backtest(strategy_id, test_data)

        if sharpe_test > 1.5:  # Out-of-sample 검증
            print(f"✅ Strategy {strategy_id} validated")
```

**Rule**:
- 실험 횟수 N → significance level = 0.05 / N
- 또는 hold-out test set 사용 (단 1회 검증)

**Related**: `experiments/common_pitfalls.md` - Data snooping

---

### Lesson 6.2: Cherry-Picking Periods (기간 선택 편향)

**배경**:
- 여러 기간 백테스트: 2020-2024 (5년)
- **문제**: 가장 좋은 기간만 보고 (2024-Q4)
- 나쁜 기간 무시 (2022 Bear market)

**실패 사례**:
```python
# ❌ Wrong: 여러 기간 중 가장 좋은 것만 보고
results = {
    '2020': backtest(data_2020),  # Sharpe 0.8
    '2021': backtest(data_2021),  # Sharpe 1.2
    '2022': backtest(data_2022),  # Sharpe -0.5 ← 무시
    '2023': backtest(data_2023),  # Sharpe 1.5
    '2024': backtest(data_2024),  # Sharpe 3.2 ← 이것만 보고
}

print("Strategy works! Sharpe 3.2 in 2024")  # ← Cherry-picking
```

**결과**:
- 보고: Sharpe 3.2
- 전체 기간 평균: **Sharpe 1.2**
- 2022 Bear market: **-0.5** (실패)

**교훈**:
```python
# ✅ Correct: 모든 기간 보고 + 최악 케이스 명시
results = {}
for year in range(2020, 2025):
    sharpe = backtest(data[year])
    results[year] = sharpe

# 보고서
print(f"Average Sharpe: {np.mean(list(results.values())):.2f}")
print(f"Best period: {max(results, key=results.get)} (Sharpe {max(results.values()):.2f})")
print(f"Worst period: {min(results, key=results.get)} (Sharpe {min(results.values()):.2f})")
print(f"Std dev: {np.std(list(results.values())):.2f}")

# ✅ 투명한 보고
# Average: 1.2, Best: 3.2 (2024), Worst: -0.5 (2022), Std: 1.1
```

**Rule**:
- 모든 기간 결과 보고
- 최악 케이스 명시
- Regime별 분석 (Bull/Bear/Sideways)

---

## 💰 Category 7: Transaction Costs (거래 비용)

### Lesson 7.1: 수수료 누락 (Fee Omission)

**배경**:
- 고빈도 전략: 하루 100 거래
- 백테스트: **수수료 미반영**
- 현실: Taker fee 0.03%

**실패 사례**:
```python
# ❌ Wrong: 수수료 없이 백테스트
pnl = (exit_price - entry_price) * quantity
# Fee 누락!
```

**결과**:
- Backtest Sharpe: **2.5**
- Gross PnL: $100,000
- Fees: **$50,000** (100 trades/day × $500 avg notional × 0.03% × 365 days)
- Net PnL: **$50,000** (50% 손실)
- Live Sharpe: **1.2** (수수료 반영)

**교훈**:
```python
# ✅ Correct: 수수료 반영
entry_notional = entry_price * quantity
exit_notional = exit_price * quantity

entry_fee = entry_notional * fee_rate_taker  # 0.03%
exit_fee = exit_notional * fee_rate_taker

gross_pnl = exit_notional - entry_notional
net_pnl = gross_pnl - entry_fee - exit_fee  # ✅ 수수료 차감
```

**Impact by Strategy Type**:
- Low frequency (1 trade/week): **수수료 < 5% of PnL**
- Medium frequency (1 trade/day): **수수료 ~20% of PnL**
- High frequency (100 trades/day): **수수료 > 50% of PnL** ← Critical

**Related**: `modeling/transaction_cost_model.md`

---

### Lesson 7.2: Maker Fee Rebate 과신

**배경**:
- VIP9 Maker fee: **-0.02%** (rebate)
- "수수료로 돈 번다!" 착각
- **문제**: Fill ratio 30% → 실제 rebate 1/3

**실패 사례**:
```python
# ❌ Wrong: 100% fill 가정으로 maker rebate 계산
orders_per_day = 100
avg_notional = 10000  # $10k per order
maker_rebate_per_order = avg_notional * 0.0002  # $2
total_rebate_per_day = orders_per_day * maker_rebate_per_order  # $200/day

# Expected: $200/day rebate = $73k/year
```

**결과**:
- Expected rebate: **$73k/year**
- Actual fill: 30% → **$22k/year** (70% 감소)
- Unfilled 70%: Opportunity cost → **-$30k/year**
- **Net: -$8k/year** (손실)

**교훈**:
```python
# ✅ Correct: Fill ratio 반영 + opportunity cost
fill_ratio = 0.3
filled_orders = orders_per_day * fill_ratio  # 30 orders
actual_rebate = filled_orders * maker_rebate_per_order  # $60/day

unfilled_orders = orders_per_day * (1 - fill_ratio)  # 70 orders
opportunity_cost = unfilled_orders * expected_alpha_per_trade  # -$100/day

net_benefit = actual_rebate - opportunity_cost  # -$40/day (손실)
```

**Rule**: Maker rebate는 **alpha > opportunity cost** 일 때만 유리

---

## 📊 Quantitative Summary (정량적 요약)

### Impact Matrix: Backtest vs Live Gap

| Mistake Type | Sharpe Gap | PnL Gap | Detection | Fix Cost |
|--------------|------------|---------|-----------|----------|
| **Look-ahead bias** | 2-4× | 100-400% | Signal shift test | High |
| **100% fill assumption** | 1.35× | 35% | Fill ratio data | Medium |
| **Survivorship bias** | 1.5-2× | 50-100% | Universe check | High |
| **Slippage omission** | 1.3-2× | 30-100% | Spread data | Low |
| **Fee omission** | 1.2-1.5× | 20-50% | Fee calculation | Low |
| **MDD = 0 problem** | N/A (risk) | -20% MDD | Hourly MTM | Medium |
| **Parameter overfitting** | 3-7× | 200-600% | OOS validation | Medium |
| **Greeks unit mix** | N/A (critical) | 10-100× | Unit check | Low |

**High Priority Fixes** (Impact > 50%):
1. Look-ahead bias detection (Signal shift test)
2. Survivorship bias prevention (Full universe)
3. Parameter overfitting (Walk-forward)
4. Fill ratio calibration (30% → reality)

---

## 🔧 Prevention Checklist (실패 방지 체크리스트)

### Pre-Backtest (백테스트 전)

- [ ] **Data integrity**:
  - [ ] Timezone: 모두 UTC
  - [ ] Corporate actions: Adjusted prices
  - [ ] Survivorship: 상장폐지 종목 포함
  - [ ] Missing data: 결측치 처리 방법 명확

- [ ] **Look-ahead prevention**:
  - [ ] Rolling window: `center=False`
  - [ ] Resample: `bfill()` 사용 금지
  - [ ] Feature/Label: 계산 시점 분리

- [ ] **Transaction costs**:
  - [ ] Fees: Maker/Taker 구분
  - [ ] Slippage: Model 선택 (spread/depth/impact)
  - [ ] Fill ratio: 30% (maker) / 100% (taker)

### Post-Backtest (백테스트 후)

- [ ] **Validation**:
  - [ ] Signal shift test: Sharpe 변화 < 50%
  - [ ] Parameter stability: ±20% 파라미터 변화 시 Sharpe 유지
  - [ ] Walk-forward: OOS Sharpe > 0.5 × IS Sharpe
  - [ ] Multiple periods: 최소 2-3개 regime 검증

- [ ] **Reconciliation**:
  - [ ] Position continuity: All trades reconciled
  - [ ] Cash conservation: Cash flow = trades + fees
  - [ ] PnL attribution: Components sum to total
  - [ ] Greeks tracking: Portfolio greeks = sum(position greeks)

- [ ] **Integrity**:
  - [ ] MDD ≠ 0: Hourly MTM 확인
  - [ ] Trades count: 합리적 범위 (과다 거래 방지)
  - [ ] Sharpe < 3: 3 초과 시 의심
  - [ ] Greeks units: 모두 BS (USD) 통일

---

## 📚 Related Documentation

- **Common Pitfalls**: `experiments/common_pitfalls.md` - Bias 종류 및 탐지
- **Methodology**: `experiments/methodology.md` - 변인 통제, Walk-forward
- **Backtesting NAV**: `experiments/backtesting_nav_policy.md` - Hourly MTM
- **Fill Probability**: `modeling/fill_probability.md` - 30% fill ratio
- **Transaction Costs**: `modeling/transaction_cost_model.md` - T-cost 모델
- **Backtesting Integrity**: `~/.claude/rules/10_backtesting_integrity.md` - Full checklist

---

**Last Updated**: 2025-12-23
**Version**: 1.0
**Maintainer**: sqr

**Contributing**: 새로운 실패 사례 발견 시 이 문서에 추가 (재발 방지)
