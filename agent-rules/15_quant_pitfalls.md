# 🚨 Quant Pitfalls Prevention (퀀트 함정 방지)

**Priority**: ⭐⭐⭐⭐⭐ CRITICAL - 매 백테스트 전 확인 필수
**Last Updated**: 2025-12-30

---

## 🔴 STOP! 백테스트 전 이 체크리스트 확인

```
┌─────────────────────────────────────────────────────────────┐
│  🚨 PRE-BACKTEST CHECKLIST (실행 전 반드시 확인)            │
├─────────────────────────────────────────────────────────────┤
│  □ 1. 미래 데이터 참조 없는가? (shift/lag 확인)              │
│  □ 2. 시그널 생성 시점 vs 진입 시점 분리되었는가?           │
│  □ 3. 차트 timeframe = 데이터 timeframe 일치하는가?         │
│  □ 4. Train/Test 기간 완전히 분리되었는가?                  │
│  □ 5. 파라미터 최적화 후 OOS 검증 있는가?                   │
└─────────────────────────────────────────────────────────────┘
```

**하나라도 No → 백테스트 중단, 코드 수정 후 재실행**

---

# 1️⃣ Look-Ahead Bias (미래 참조) 방지

## 🎯 핵심 원칙

**t 시점 결정에 t+1 이후 정보 사용 = 백테스트 무효**

### 흔한 미래 참조 패턴 (자주 범하는 실수)

#### ❌ Pattern 1: 당일 Close로 당일 진입 결정

```python
# ❌ WRONG: 15:59 close 가격을 15:00에 알 수 없음
df['signal'] = df['close'] > df['close'].rolling(20).mean()
df['entry'] = df['signal']  # 같은 봉에서 signal과 entry

# ✅ CORRECT: 시그널은 전 봉, 진입은 다음 봉
df['signal'] = df['close'] > df['close'].rolling(20).mean()
df['entry'] = df['signal'].shift(1)  # 전 봉 시그널로 현재 봉 진입
```

#### ❌ Pattern 2: 미래 데이터로 정규화

```python
# ❌ WRONG: 전체 기간 mean/std로 정규화 = 미래 참조
df['normalized'] = (df['price'] - df['price'].mean()) / df['price'].std()

# ✅ CORRECT: Rolling 또는 expanding으로 과거만 사용
df['normalized'] = (df['price'] - df['price'].expanding().mean()) / df['price'].expanding().std()
```

#### ❌ Pattern 3: 당일 High/Low 사용

```python
# ❌ WRONG: 당일 high/low는 장 마감 전까지 모름
df['signal'] = df['close'] > (df['high'] + df['low']) / 2

# ✅ CORRECT: 전일 high/low 사용
df['signal'] = df['close'] > (df['high'].shift(1) + df['low'].shift(1)) / 2
```

#### ❌ Pattern 4: 미래 레이블로 학습

```python
# ❌ WRONG: 미래 수익률을 feature에 포함
df['future_return'] = df['close'].pct_change(5).shift(-5)  # shift(-5) = 미래!
model.fit(df[['feature', 'future_return']], df['target'])

# ✅ CORRECT: 과거 데이터만 feature로
df['past_return'] = df['close'].pct_change(5)  # 과거 5봉 수익률
model.fit(df[['feature', 'past_return']], df['target'])
```

#### ❌ Pattern 5: ffill/bfill 미래 참조

```python
# ❌ WRONG: bfill = 미래 값으로 과거 채움
df['filled'] = df['value'].fillna(method='bfill')

# ✅ CORRECT: ffill = 과거 값으로 미래 채움
df['filled'] = df['value'].fillna(method='ffill')
```

#### ❌ Pattern 6: center=True 이동평균

```python
# ❌ WRONG: center=True는 양방향 참조 (미래 포함)
df['ma'] = df['close'].rolling(20, center=True).mean()

# ✅ CORRECT: center=False (기본값)
df['ma'] = df['close'].rolling(20, center=False).mean()
```

---

## 🔍 미래 참조 자동 탐지 코드

**모든 백테스트 전에 실행 필수:**

```python
def detect_lookahead_bias(df: pd.DataFrame, signal_col: str, price_col: str = 'close'):
    """
    Look-ahead bias 자동 탐지.

    Returns:
        dict: 탐지 결과 + 경고 메시지
    """
    warnings = []

    # 1. shift(-N) 사용 여부 (코드 분석 필요)
    # → 수동 확인 필요

    # 2. 시그널과 가격의 상관관계 체크
    # 미래 참조 시 비정상적으로 높은 상관관계
    future_corr = df[signal_col].corr(df[price_col].shift(-1))
    if abs(future_corr) > 0.5:
        warnings.append(f"⚠️ 시그널-미래가격 상관 {future_corr:.2f} (높음, 미래참조 의심)")

    # 3. 시그널 shift 체크
    # 시그널이 가격 변화보다 먼저 움직이면 의심
    signal_lead = df[signal_col].diff().corr(df[price_col].diff().shift(-1))
    if signal_lead > 0.3:
        warnings.append(f"⚠️ 시그널이 가격을 선행 {signal_lead:.2f} (미래참조 의심)")

    # 4. Perfect foresight 체크
    # 승률이 비현실적으로 높으면 의심
    if 'pnl' in df.columns:
        win_rate = (df['pnl'] > 0).mean()
        if win_rate > 0.7:
            warnings.append(f"⚠️ 승률 {win_rate:.1%} (비현실적, 미래참조 의심)")

    return {
        'warnings': warnings,
        'future_corr': future_corr,
        'signal_lead': signal_lead,
        'passed': len(warnings) == 0
    }

# 사용
result = detect_lookahead_bias(df, 'signal')
if not result['passed']:
    print("🚨 LOOK-AHEAD BIAS DETECTED!")
    for w in result['warnings']:
        print(f"  {w}")
    raise ValueError("백테스트 중단: 미래 참조 의심")
```

---

## ✅ Look-Ahead Bias 방지 체크리스트

**코드 작성 시:**
- [ ] `shift(-N)` 사용 금지 (미래 값 참조)
- [ ] `bfill()` 사용 금지 → `ffill()` 사용
- [ ] `center=True` 사용 금지 (rolling)
- [ ] 당일 high/low 사용 금지 → 전일 값 사용
- [ ] 전체 기간 통계 사용 금지 → expanding/rolling 사용

**시그널 생성 시:**
- [ ] 시그널 생성 시점 < 진입 시점 (최소 1봉 차이)
- [ ] `df['entry'] = df['signal'].shift(1)` 필수
- [ ] 슬리피지: 다음 봉 open 또는 close 사용

**학습/최적화 시:**
- [ ] Train/Test 완전 분리 (시간순)
- [ ] Walk-forward validation 사용
- [ ] 파라미터 최적화 결과를 다른 기간에서 검증

---

# 2️⃣ Chart Timeframe Consistency (차트 시간축 일관성)

## 🎯 핵심 원칙

**데이터 timeframe = 차트 timeframe**

15분봉 백테스트 → 15분봉 차트
1분봉 백테스트 → 1분봉 차트
**❌ 절대 1일봉으로 리샘플링 금지**

### 왜 중요한가?

1. **정합성 검증 불가**: 15분봉에서 진입/청산 타이밍을 1일봉에서 확인 불가
2. **시그널 타이밍 오류**: 일봉에서 "좋아보이는" 진입이 15분봉에서는 최악일 수 있음
3. **Drawdown 은폐**: 일중 DD가 일봉 차트에서 보이지 않음
4. **디버깅 불가**: 특정 거래가 왜 발생했는지 확인 불가

---

## 🔍 올바른 차트 생성 방법

### ❌ WRONG: 무조건 일봉으로 리샘플링

```python
# ❌ WRONG: 15분봉 백테스트인데 일봉으로 그림
def plot_results(df_15m, trades):
    df_daily = df_15m.resample('1D').agg({
        'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last'
    })
    plt.plot(df_daily['close'])  # 정합성 검증 불가!
```

### ✅ CORRECT: 데이터 timeframe 유지

```python
def plot_backtest_results(
    df: pd.DataFrame,
    trades: pd.DataFrame,
    timeframe: str,  # '15m', '1h', '1D' 등
    figsize: tuple = (16, 10)
):
    """
    백테스트 결과 시각화 - timeframe 일관성 유지.

    CRITICAL: 데이터 timeframe과 차트 timeframe 반드시 일치!
    """
    fig, axes = plt.subplots(3, 1, figsize=figsize, sharex=True)

    # 1. 가격 차트 (원본 timeframe 유지)
    ax1 = axes[0]
    ax1.plot(df.index, df['close'], label=f'Close ({timeframe})', alpha=0.7)

    # 거래 마커 (진입/청산)
    for _, trade in trades.iterrows():
        if trade['side'] == 'buy':
            ax1.scatter(trade['entry_time'], trade['entry_price'],
                       marker='^', color='green', s=100, zorder=5)
        else:
            ax1.scatter(trade['entry_time'], trade['entry_price'],
                       marker='v', color='red', s=100, zorder=5)

        # 청산 마커
        ax1.scatter(trade['exit_time'], trade['exit_price'],
                   marker='x', color='black', s=50, zorder=5)

    ax1.set_title(f'Price & Trades ({timeframe} timeframe)')
    ax1.legend()

    # 2. 포지션 차트 (원본 timeframe)
    ax2 = axes[1]
    ax2.fill_between(df.index, df['position'], 0,
                     where=df['position'] > 0, color='green', alpha=0.3, label='Long')
    ax2.fill_between(df.index, df['position'], 0,
                     where=df['position'] < 0, color='red', alpha=0.3, label='Short')
    ax2.set_title(f'Position ({timeframe})')
    ax2.legend()

    # 3. Equity Curve (원본 timeframe)
    ax3 = axes[2]
    ax3.plot(df.index, df['equity'], label='Equity', color='blue')
    ax3.fill_between(df.index, df['equity'], df['equity'].cummax(),
                     color='red', alpha=0.3, label='Drawdown')
    ax3.set_title(f'Equity & Drawdown ({timeframe})')
    ax3.legend()

    plt.tight_layout()
    return fig


def plot_trade_detail(
    df: pd.DataFrame,
    trade: pd.Series,
    timeframe: str,
    window_bars: int = 50  # 거래 전후 몇 봉 표시
):
    """
    개별 거래 상세 차트 - 진입/청산 타이밍 검증용.

    CRITICAL: 이 차트로 각 거래의 진입/청산 타이밍 정합성 확인!
    """
    # 거래 전후 window
    entry_idx = df.index.get_loc(trade['entry_time'])
    start_idx = max(0, entry_idx - window_bars)
    end_idx = min(len(df), entry_idx + window_bars)

    df_window = df.iloc[start_idx:end_idx]

    fig, ax = plt.subplots(figsize=(14, 6))

    # 캔들스틱 또는 라인
    ax.plot(df_window.index, df_window['close'], 'b-', alpha=0.7)
    ax.fill_between(df_window.index, df_window['low'], df_window['high'],
                    alpha=0.2, color='gray')

    # 진입 마커
    ax.axvline(trade['entry_time'], color='green', linestyle='--', label='Entry')
    ax.scatter([trade['entry_time']], [trade['entry_price']],
               marker='^', color='green', s=200, zorder=5)

    # 청산 마커
    ax.axvline(trade['exit_time'], color='red', linestyle='--', label='Exit')
    ax.scatter([trade['exit_time']], [trade['exit_price']],
               marker='v', color='red', s=200, zorder=5)

    # 시그널 봉 마커 (진입 1봉 전)
    signal_time = df.index[entry_idx - 1] if entry_idx > 0 else trade['entry_time']
    ax.axvline(signal_time, color='orange', linestyle=':', label='Signal')

    ax.set_title(f"Trade Detail ({timeframe}): {trade['symbol']} | "
                 f"PnL: {trade['pnl']:.2f} | Entry: {trade['entry_time']}")
    ax.legend()

    return fig
```

---

## 📊 Timeframe별 권장 시각화 설정

| 백테스트 Timeframe | 차트 Timeframe | 표시 기간 권장 | 거래 상세 Window |
|-------------------|----------------|---------------|-----------------|
| 1m | 1m | 1-7일 | 100봉 (전후) |
| 5m | 5m | 1-14일 | 60봉 |
| 15m | 15m | 1-30일 | 50봉 |
| 1h | 1h | 1-90일 | 40봉 |
| 4h | 4h | 3-180일 | 30봉 |
| 1D | 1D | 전체 기간 | 20봉 |

---

## ✅ Chart Timeframe 체크리스트

**차트 생성 전:**
- [ ] 데이터 timeframe 확인 (df의 index 간격)
- [ ] resample 사용 금지 (리샘플링 없이 원본 사용)
- [ ] 차트 title에 timeframe 명시

**차트 생성 시:**
- [ ] 가격 차트: 원본 timeframe
- [ ] 포지션 차트: 원본 timeframe
- [ ] Equity 차트: 원본 timeframe
- [ ] 거래 마커: 정확한 진입/청산 시점

**정합성 검증:**
- [ ] 무작위 10개 거래 상세 차트 확인
- [ ] 진입 타이밍이 시그널 봉 다음인지 확인
- [ ] 청산 타이밍이 청산 조건 시점과 일치하는지 확인

---

# 3️⃣ 기타 흔한 퀀트 함정

## Survivorship Bias (생존 편향)

```python
# ❌ WRONG: 현재 상장된 종목만으로 과거 백테스트
symbols = get_current_symbols()  # 2024년 현재 상장 종목
backtest(symbols, '2020-01-01', '2024-12-31')  # 2020년부터?

# ✅ CORRECT: 각 시점의 상장 종목 사용
def get_symbols_at_time(date):
    """해당 시점에 상장되어 있던 종목 반환 (상폐 포함)"""
    ...
```

## Data Snooping (데이터 스누핑)

```python
# ❌ WRONG: 여러 전략 테스트 후 최고 성과만 보고
for strategy in [s1, s2, s3, s4, s5]:  # 5개 테스트
    result = backtest(strategy)
best = max(results)  # 최고만 선택 → p-hacking

# ✅ CORRECT: 사전에 가설 설정, 1개만 테스트, 또는 다중 비교 보정
hypothesis = "MA crossover가 momentum보다 나을 것"
result = backtest(ma_crossover)
# Bonferroni correction if multiple tests
```

## Overfitting (과적합)

```python
# ❌ WRONG: 파라미터 최적화 결과를 같은 기간에서 평가
best_params = optimize(df_train)
sharpe = evaluate(df_train, best_params)  # 같은 데이터!

# ✅ CORRECT: 최적화와 평가 기간 분리
best_params = optimize(df_train)
sharpe = evaluate(df_test, best_params)  # 다른 기간
```

---

# 🚨 Agent Rules (Quant Pitfalls)

## MANDATORY Behaviors

1. **백테스트 전 체크리스트 확인 출력**
   - 매 백테스트 시작 시 체크리스트 출력
   - 하나라도 No → 백테스트 중단

2. **Look-ahead 탐지 코드 실행**
   - `detect_lookahead_bias()` 함수 자동 실행
   - 경고 발생 시 → 백테스트 중단, 코드 수정

3. **차트 생성 시 timeframe 명시**
   - 모든 차트 title에 timeframe 포함
   - resample 사용 금지 (명시적 요청 제외)

4. **거래 상세 차트 포함**
   - 백테스트 결과에 최소 3개 거래 상세 차트 포함
   - 진입/청산 타이밍 정합성 시각적 확인

## RED FLAGS (즉시 수정)

- ❌ `shift(-N)` 발견
- ❌ `bfill()` 발견
- ❌ `center=True` 발견
- ❌ 당일 high/low로 당일 시그널 생성
- ❌ 차트 timeframe ≠ 데이터 timeframe
- ❌ 승률 > 70% (미래 참조 의심)
- ❌ Sharpe > 5 (미래 참조 의심)

---

**Last Updated**: 2025-12-30
**Version**: 1.0
