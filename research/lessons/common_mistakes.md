# Common Mistakes (자주 하는 실수)

**Purpose**: 코딩 오류 및 구현 실수 모음 (빠른 참조용)
**Last Updated**: 2025-12-25
**Owner**: sqr

---

## 📌 Quick Reference

| Category | Mistake | Fix |
|----------|---------|-----|
| **Pandas** | SettingWithCopyWarning | `.loc[row, col] = value` 또는 `.copy()` |
| **Pandas** | Timezone-naive | `.tz_localize('UTC')` |
| **Pandas** | `inplace=True` 남용 | Method chaining |
| **NumPy** | Integer division | `float()` 변환 또는 dtype=float |
| **Python** | Mutable default arg | `def f(x=None): x = x or []` |
| **API** | Rate limit 무시 | Rate limiter 구현 |
| **Git** | Credentials commit | 환경변수 + `.gitignore` |
| **Backtest** | `shift(-1)` 혼동 | -1 = 미래(Label), +1 = 과거(Feature) |

---

## 🐍 Category 1: Python/Pandas

### 1.1 SettingWithCopyWarning
```python
# ❌ df_filtered = df[df['price'] > 100]; df_filtered['signal'] = 1
# ✅ df_filtered = df[df['price'] > 100].copy(); df_filtered['signal'] = 1
# ✅ df.loc[df['price'] > 100, 'signal'] = 1
```

### 1.2 Timezone-Naive
```python
# ❌ df.index = pd.to_datetime(df.index)  # Naive
# ✅ df.index = pd.to_datetime(df.index).tz_localize('UTC')
```
**Rule**: 모든 internal datetime은 UTC

### 1.3 `inplace=True` 남용
```python
# ❌ df.dropna(inplace=True)
# ✅ df_clean = df.dropna().sort_values('ts').reset_index(drop=True)
```

### 1.4 Integer Division (NumPy)
```python
# ❌ arr = np.array([10, 3], dtype=int); arr[0]/arr[1]  # 3
# ✅ arr = np.array([10, 3], dtype=float); arr[0]/arr[1]  # 3.333
```

### 1.5 Mutable Default Argument
```python
# ❌ def add(trade, portfolio=[]): portfolio.append(trade)
# ✅ def add(trade, portfolio=None): portfolio = portfolio or []
```

---

## 📊 Category 2: Performance

### 2.1 Loop 대신 Vectorization
```python
# ❌ for i in range(len(df)): signals.append(df.loc[i, 'p'] > df.loc[i, 'ma'])
# ✅ df['signal'] = (df['p'] > df['ma']).astype(int)
```
**Impact**: 1000× faster

### 2.2 `apply()` 남용
```python
# ❌ df['log_ret'] = df['price'].apply(lambda x: np.log(x))
# ✅ df['log_ret'] = np.log(df['price'])
```

### 2.3 반복적 Row 추가
```python
# ❌ for t in trades: df = df.append(t)  # O(n²)
# ✅ trade_list = []; for t in trades: trade_list.append(t); df = pd.DataFrame(trade_list)
```
**Impact**: 300× faster

---

## 🌐 Category 3: API

### 3.1 Rate Limit 무시
**OKX limit**: 20 req/2s, 초과 시 ban
```python
# ✅ class RateLimiter: deque로 calls 추적, 초과 시 sleep
```

### 3.2 Error Handling 부재
```python
# ❌ data = requests.get(url).json()['data']
# ✅ try: response.raise_for_status(); if data['code'] != '0': retry
```
**Rule**: retry + timeout + exponential backoff

### 3.3 Credentials 하드코딩
```python
# ❌ API_KEY = "1a2b3c..."
# ✅ API_KEY = os.getenv('OKX_API_KEY'); .gitignore에 .env 추가
```

---

## 🧪 Category 4: Backtest

### 4.1 `shift()` 방향 혼동
```python
# ❌ df['signal'] = (df['return'].shift(-1) > 0)  # 미래 정보!
# ✅ df['signal'] = (df['ma'].shift(1) > df['price'])  # 과거 데이터
```
**Rule**: `shift(-1)` = 미래 → Label용, `shift(1)` = 과거 → Feature용

### 4.2 Off-by-One Error
```python
# ❌ entry_price = prices[i]; exit_price = prices[i]  # PnL = 0
# ✅ Entry at i → Exit at i+1 (최소 1 bar 간격)
```

### 4.3 Position Tracking 누락
```python
# ❌ if signal == 1: buy(10)  # 중복 진입 (10 → 20 → 30...)
# ✅ if signal == 1 and position == 0: buy(10); position = 10
```

### 4.4 Vectorized vs Event-Driven
- **Vectorized**: 단순 전략, daily rebalance
- **Event-driven**: 복잡 로직, intraday, order dependency

**📚 상세**: `lessons_learned.md` Category 5 참조

---

## 🔢 Category 5: Greeks

### 5.1 PA/BS 혼용
```python
# ❌ portfolio_theta = pos1.theta_pa + pos2.theta_bs  # 단위 다름!
# ✅ Portfolio 집계는 모두 BS (USD) 단위로 통일
```

### 5.2 옵션 만기 처리 누락
```python
# ✅ if timestamp >= pos.expiry_time:
#        if pos.is_itm(): settle(intrinsic_value) else: expire()
```
**OKX 만기**: UTC 08:00

### 5.3 IV를 Constant로 가정
```python
# ❌ iv = 0.50  # 고정
# ✅ iv = get_mark_iv(timestamp, symbol)  # Market IV
```

**📚 상세**: `exchanges/_common/greeks.md`

---

## 📝 Category 6: Code Quality

### 6.1 Magic Numbers
```python
# ❌ if vol > 0.8: ...
# ✅ HIGH_VOL_THRESHOLD = 0.8; if vol > HIGH_VOL_THRESHOLD: ...
```

### 6.2 함수 >100 lines
```python
# ❌ def run_backtest(): # 500 lines
# ✅ run_backtest() → preprocess() → calc_features() → generate_signals() → execute()
```
**Rule**: 함수 50 lines 이하

### 6.3 불명확한 변수명
```python
# ❌ df2 = df[df['x'] > 100]; temp = df2['y'].mean()
# ✅ filtered_options = data[data['volume'] > 100]; avg_iv = filtered['iv'].mean()
```

---

## 🐛 Category 7: Debugging

### 7.1 `print()` 대신 Logging
```python
# ❌ print(f"Sharpe: {sharpe}")
# ✅ logging.info(f"Sharpe: {sharpe:.2f}")
```

### 7.2 Bare `except:` 금지
```python
# ❌ try: ... except: pass  # 에러 숨김
# ✅ except ValueError as e: logger.error(e); raise
```

### 7.3 Assertion 미사용
```python
# ✅ assert nav >= 0, f"Negative NAV: {nav}"
# ✅ assert not np.isnan(nav), "NAV is NaN"
```

---

## ✅ Quick Checklist

### Before Code:
- [ ] Variable names: descriptive (not `df`, `temp`)
- [ ] Constants: named (not magic numbers)
- [ ] Function: < 50 lines
- [ ] Datetime: UTC
- [ ] Logging: not `print()`

### Before Backtest:
- [ ] `shift(1)` = past, `shift(-1)` = future
- [ ] Position: explicit state
- [ ] Greeks: BS (USD) 통일
- [ ] Rate limit: under limit
- [ ] Credentials: not in code

### After Backtest:
- [ ] Assertions: NAV >= 0, no NaN
- [ ] Reconciliation: Position/Cash/PnL 일치
- [ ] Git: no credentials

---

## 📚 Related

- `lessons_learned/lessons_learned.md` - 백테스트 실패 사례
- `lessons_learned/common_pitfalls.md` - Bias 종류
- `agent_prompts/claude_code/rules/10_backtesting_integrity.md` - Reconciliation

---

**Version**: 2.0 (Condensed)
**Contributing**: 새 실수 발견 시 추가
