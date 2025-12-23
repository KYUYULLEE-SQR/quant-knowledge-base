# Common Mistakes (자주 하는 실수)

**Purpose**: Agent 및 개발자가 반복적으로 하는 실수 모음 (코딩 오류, 구현 실수 위주)

**Last Updated**: 2025-12-23
**Owner**: sqr
**Environment**: micky (data), spice (backtest), vultr (trading)

---

## 📌 Quick Reference

| Category | Mistake | Impact | Fix |
|----------|---------|--------|-----|
| **Pandas** | `.loc[]` 없이 assignment | SettingWithCopyWarning | `.loc[row, col] = value` |
| **Pandas** | Timezone-naive datetime | 계산 오류 | `.tz_localize('UTC')` |
| **Pandas** | Inplace=True 남용 | 디버깅 어려움 | Copy 명시 |
| **NumPy** | Integer division `10/3=3` | 계산 오류 | `10.0/3` 또는 `//` |
| **Python** | Mutable default argument | 예기치 않은 상태 | `def f(x=None): x = x or []` |
| **API** | Rate limit 무시 | 403 Forbidden | Rate limiter 구현 |
| **Git** | Credentials commit | 보안 사고 | `.gitignore` 필수 |
| **Backtest** | Future value in past | Look-ahead bias | `.shift()` 확인 |

---

## 🐍 Category 1: Python/Pandas Gotchas

### Mistake 1.1: SettingWithCopyWarning 무시

**Bad Code**:
```python
# ❌ DataFrame slice에 직접 assignment
df_filtered = df[df['price'] > 100]
df_filtered['signal'] = 1  # ⚠️ SettingWithCopyWarning

# 문제: df_filtered가 view일 수도, copy일 수도 있음
# → 예측 불가능한 동작
```

**Why It's Bad**:
- View vs Copy 불명확
- 원본 DataFrame 의도치 않게 수정 가능
- 디버깅 어려움

**Correct Code**:
```python
# ✅ Explicit copy
df_filtered = df[df['price'] > 100].copy()
df_filtered['signal'] = 1  # No warning

# ✅ Or use .loc[]
df.loc[df['price'] > 100, 'signal'] = 1  # Safer
```

**Rule**: **항상 `.loc[]` 사용** 또는 명시적 `.copy()`

---

### Mistake 1.2: Timezone-Naive Datetime 사용

**Bad Code**:
```python
# ❌ Timezone 없는 datetime
df.index = pd.to_datetime(df.index)  # Naive datetime

# OKX API는 UTC 반환
okx_time = pd.Timestamp('2024-12-23 08:00', tz='UTC')

# 비교 시 에러 또는 잘못된 결과
if df.index[0] == okx_time:  # TypeError or wrong comparison
    ...
```

**Why It's Bad**:
- Timezone 혼동 (UTC vs Local)
- 만기 시간 계산 오류 (9시간 차이)
- API 데이터와 불일치

**Correct Code**:
```python
# ✅ 모든 datetime에 timezone 명시
df.index = pd.to_datetime(df.index).tz_localize('UTC')

# API 데이터
okx_time = pd.Timestamp('2024-12-23 08:00', tz='UTC')

# 비교 안전
if df.index[0] == okx_time:  # ✅ Works correctly
    ...
```

**Rule**: **모든 internal datetime은 UTC**, display만 local

---

### Mistake 1.3: `inplace=True` 남발

**Bad Code**:
```python
# ❌ inplace=True 사용
df.dropna(inplace=True)
df.sort_values('timestamp', inplace=True)
df.reset_index(drop=True, inplace=True)

# 문제: 중간 상태 확인 불가, 디버깅 어려움
```

**Why It's Bad**:
- 중간 결과 저장 불가
- Undo 불가능
- 디버깅 시 원본 데이터 소실

**Correct Code**:
```python
# ✅ Method chaining (readable)
df_clean = (df
    .dropna()
    .sort_values('timestamp')
    .reset_index(drop=True)
)

# 중간 상태 확인 가능
df_no_na = df.dropna()
print(f"Dropped {len(df) - len(df_no_na)} rows")
df_sorted = df_no_na.sort_values('timestamp')
```

**Rule**: `inplace=True` 피하고 method chaining 사용

---

### Mistake 1.4: Integer Division 잊기 (Python 2 습관)

**Bad Code**:
```python
# ❌ Integer division (Python 2 style)
spread_bps = spread / price * 10000  # If spread=3, price=100
# Result: 300 (integer division if both are int)

# Python 3에서는 괜찮지만, NumPy array는 dtype에 따라 다름
arr = np.array([10, 3], dtype=int)
result = arr[0] / arr[1]  # 3 (integer division in NumPy!)
```

**Why It's Bad**:
- NumPy integer array에서 여전히 발생
- Precision 손실
- 예상치 못한 결과

**Correct Code**:
```python
# ✅ Explicit float conversion
spread_bps = float(spread) / price * 10000

# ✅ NumPy float dtype
arr = np.array([10, 3], dtype=float)
result = arr[0] / arr[1]  # 3.333...

# ✅ Or use //  for floor division explicitly
result = 10 // 3  # 3 (명시적 floor division)
```

**Rule**: Division 전에 **float conversion** 또는 `/` vs `//` 명확히

---

### Mistake 1.5: Mutable Default Arguments

**Bad Code**:
```python
# ❌ Mutable default argument
def add_trade(trade, portfolio=[]):
    portfolio.append(trade)
    return portfolio

# 사용
p1 = add_trade({'qty': 10})  # [{'qty': 10}]
p2 = add_trade({'qty': 20})  # [{'qty': 10}, {'qty': 20}] ← 의도와 다름!
# p1과 p2가 같은 리스트를 공유!
```

**Why It's Bad**:
- Default argument는 함수 정의 시 **한 번만** 생성
- 모든 호출이 같은 객체 공유
- 예측 불가능한 상태

**Correct Code**:
```python
# ✅ None as default, create new list inside
def add_trade(trade, portfolio=None):
    if portfolio is None:
        portfolio = []
    portfolio.append(trade)
    return portfolio

# 또는
def add_trade(trade, portfolio=None):
    portfolio = portfolio or []  # Simpler
    portfolio.append(trade)
    return portfolio
```

**Rule**: **Mutable default argument 절대 금지**, `None` 사용

---

## 📊 Category 2: NumPy/Pandas Performance

### Mistake 2.1: Loop 대신 Vectorization 미사용

**Bad Code**:
```python
# ❌ Python loop (slow)
signals = []
for i in range(len(df)):
    if df.loc[i, 'price'] > df.loc[i, 'ma_20']:
        signals.append(1)
    else:
        signals.append(0)
df['signal'] = signals

# 100k rows: ~5 seconds
```

**Why It's Bad**:
- Python loop는 매우 느림 (interpreted)
- Pandas는 vectorized operations에 최적화

**Correct Code**:
```python
# ✅ Vectorized (fast)
df['signal'] = (df['price'] > df['ma_20']).astype(int)

# 100k rows: ~5 milliseconds (1000× faster)
```

**Rule**: **Loop 금지**, NumPy/Pandas vectorized operations 사용

---

### Mistake 2.2: `apply()` 남용

**Bad Code**:
```python
# ❌ apply() with lambda (slow)
df['log_return'] = df['price'].apply(lambda x: np.log(x / x.shift(1)))

# apply()는 row-by-row iteration (느림)
```

**Why It's Bad**:
- `apply()`는 내부적으로 Python loop
- Vectorized function보다 10-100× 느림

**Correct Code**:
```python
# ✅ Vectorized numpy function
df['log_return'] = np.log(df['price'] / df['price'].shift(1))

# ✅ Or pandas built-in
df['log_return'] = df['price'].pct_change().apply(np.log1p)
```

**When to Use `apply()`**:
- 복잡한 로직 (vectorization 불가능)
- Row-wise custom function 필수
- **But**: 먼저 vectorization 가능한지 확인

---

### Mistake 2.3: DataFrame에서 반복적으로 Row 추가

**Bad Code**:
```python
# ❌ Iteratively append rows (very slow)
df = pd.DataFrame()
for trade in trades:
    df = df.append(trade, ignore_index=True)  # O(n^2) complexity!

# 10k trades: ~30 seconds
```

**Why It's Bad**:
- 매번 전체 DataFrame copy
- O(n^2) complexity
- 메모리 낭비

**Correct Code**:
```python
# ✅ Collect in list, then create DataFrame (fast)
trade_list = []
for trade in trades:
    trade_list.append(trade)

df = pd.DataFrame(trade_list)  # O(n) complexity

# 10k trades: ~0.1 second (300× faster)
```

**Rule**: **List에 모으고 한 번에 DataFrame 생성**

---

## 🌐 Category 3: API & External Data

### Mistake 3.1: Rate Limit 무시

**Bad Code**:
```python
# ❌ No rate limiting
for symbol in symbols:  # 100 symbols
    data = requests.get(f"https://api.okx.com/api/v5/market/ticker?instId={symbol}")
    # ...

# Result: 429 Too Many Requests after 20 requests
```

**Why It's Bad**:
- OKX limit: 20 req/2s
- 초과 시 ban (30초-1시간)
- 데이터 수집 중단

**Correct Code**:
```python
# ✅ Rate limiter
import time
from collections import deque

class RateLimiter:
    def __init__(self, max_calls, period):
        self.max_calls = max_calls
        self.period = period
        self.calls = deque()

    def __call__(self):
        now = time.time()

        # Remove old calls
        while self.calls and self.calls[0] < now - self.period:
            self.calls.popleft()

        # Check limit
        if len(self.calls) >= self.max_calls:
            sleep_time = self.period - (now - self.calls[0])
            time.sleep(sleep_time)
            self.calls.popleft()

        self.calls.append(now)

# Usage
limiter = RateLimiter(max_calls=20, period=2)

for symbol in symbols:
    limiter()  # Block if needed
    data = requests.get(...)
```

**Related**: `exchanges/okx/api_reference.md` - Rate limits

---

### Mistake 3.2: API Response Error Handling 부재

**Bad Code**:
```python
# ❌ No error handling
response = requests.get(url)
data = response.json()['data']  # KeyError if 'code' != '0'
```

**Why It's Bad**:
- API 에러 시 스크립트 중단
- Partial data 손실
- 재시도 로직 없음

**Correct Code**:
```python
# ✅ Robust error handling
import time

def fetch_with_retry(url, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Raise on 4xx/5xx

            data = response.json()

            if data['code'] != '0':
                print(f"API error: {data['msg']}")
                if data['code'] == '50011':  # Rate limit
                    time.sleep(2)
                    continue
                else:
                    return None

            return data['data']

        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt+1} failed: {e}")
            time.sleep(2 ** attempt)  # Exponential backoff

    return None  # All retries failed
```

**Rule**: **항상 retry + timeout + error handling**

---

### Mistake 3.3: Credentials를 코드에 하드코딩

**Bad Code**:
```python
# ❌ Hardcoded credentials
API_KEY = "1a2b3c4d-5e6f-7g8h-9i0j"  # ← 절대 금지!
SECRET_KEY = "abcdef123456"

# Git commit → 공개 저장소 → 보안 사고
```

**Why It's Bad**:
- Git history에 영구 저장
- 공개 저장소 push 시 노출
- API key 재발급 필요

**Correct Code**:
```python
# ✅ Environment variables
import os

API_KEY = os.getenv('OKX_API_KEY')
SECRET_KEY = os.getenv('OKX_SECRET_KEY')

if not API_KEY:
    raise ValueError("OKX_API_KEY not set")

# .env file (NOT in git)
# OKX_API_KEY=1a2b3c4d...
# OKX_SECRET_KEY=abcdef...

# .gitignore
# .env
# credentials/
```

**Rule**: **Credentials는 환경 변수 또는 별도 파일** (git ignore 필수)

---

## 🧪 Category 4: Backtesting Implementation

### Mistake 4.1: Future Value Leakage (`shift()` 방향 반대)

**Bad Code**:
```python
# ❌ Wrong shift direction
df['next_return'] = df['return'].shift(-1)  # ← 미래 값
df['signal'] = (df['next_return'] > 0).astype(int)  # ← Look-ahead bias!

# t=0: signal based on t=1 return (미래 정보)
```

**Why It's Bad**:
- Signal이 미래 정보 사용
- Backtest 완전 무효
- **가장 흔한 look-ahead bias**

**Correct Code**:
```python
# ✅ Correct: 과거 데이터로 signal 생성
df['prev_return'] = df['return'].shift(1)  # ← 과거 값
df['signal'] = (df['prev_return'] > 0).astype(int)  # ✅ OK

# Or use feature at t, predict return at t+1
df['signal'] = (df['ma_20'] > df['price']).astype(int)
df['next_return'] = df['return'].shift(-1)  # Label (미래)

# Separate: feature (t) vs label (t+1)
```

**Rule**: `shift(-1)` = 미래 → **Label용**, `shift(1)` = 과거 → **Feature용**

---

### Mistake 4.2: Off-by-One Error (Entry/Exit 시점)

**Bad Code**:
```python
# ❌ Entry와 Exit 같은 시점
for i in range(len(signals)):
    if signals[i] == 1:
        entry_price = prices[i]  # Entry at close of bar i
        exit_price = prices[i]   # ❌ Exit at same bar!
        pnl = exit_price - entry_price  # Always 0
```

**Why It's Bad**:
- Entry/Exit 동시 → PnL = 0
- 현실: Entry at close(i) → Exit at close(i+1) (최소)

**Correct Code**:
```python
# ✅ Entry at i, Exit at i+1
positions = []
for i in range(len(signals) - 1):  # -1 to avoid index error
    if signals[i] == 1 and positions == []:
        entry_price = prices[i]
        positions.append({'entry': i, 'price': entry_price})

    elif signals[i] == -1 and positions:
        exit_price = prices[i]
        entry = positions.pop()
        pnl = exit_price - entry['price']  # ✅ At least 1 bar apart
```

**Rule**: **Entry bar ≠ Exit bar** (최소 1 bar 간격)

---

### Mistake 4.3: Position Tracking 누락

**Bad Code**:
```python
# ❌ No position tracking
for signal in signals:
    if signal == 1:
        buy(10)  # ← 포지션 누적 (10 + 10 + 10...)
    elif signal == -1:
        sell(10)  # ← 보유 없는데 매도 가능 (short 의도 아님)
```

**Why It's Bad**:
- 포지션 중복 진입 (10 → 20 → 30...)
- 없는 포지션 청산 (short 의도 없는데 short)
- PnL 계산 불가능

**Correct Code**:
```python
# ✅ Explicit position tracking
position = 0  # Current position

for signal in signals:
    if signal == 1 and position == 0:  # Enter only if flat
        buy(10)
        position = 10

    elif signal == -1 and position > 0:  # Exit only if long
        sell(position)  # Sell all
        position = 0

# Or use position state machine
class PositionTracker:
    def __init__(self):
        self.position = 0

    def enter(self, qty):
        if self.position != 0:
            raise ValueError("Already in position")
        self.position = qty

    def exit(self):
        if self.position == 0:
            raise ValueError("No position to exit")
        qty = self.position
        self.position = 0
        return qty
```

**Rule**: **Position state 명시적 추적** (entry/exit 조건 명확)

---

### Mistake 4.4: Vectorized Backtest에서 Order 순서 무시

**Bad Code**:
```python
# ❌ Vectorized backtest without order dependency
df['position'] = df['signal'].shift(1)  # Signal at t → Position at t+1
df['return'] = df['price'].pct_change()
df['strategy_return'] = df['position'] * df['return']

# 문제: 같은 날 여러 신호 발생 시 순서 무시
# t=100: signal changes 0 → 1 → 0 (intraday)
# → Vectorized는 마지막 신호만 반영 (중간 과정 손실)
```

**Why It's Bad**:
- Intraday signal 변화 무시
- Entry/Exit 순서 무시 (Exit → Entry vs Entry → Exit)
- Slippage/Fee 계산 불가

**Correct Code**:
```python
# ✅ Event-driven backtest (for complex logic)
portfolio = Portfolio(initial_cash=100000)

for timestamp, row in df.iterrows():
    signal = row['signal']
    price = row['price']

    if signal == 1 and portfolio.position == 0:
        qty = portfolio.cash // price
        portfolio.buy(qty, price, timestamp)

    elif signal == -1 and portfolio.position > 0:
        portfolio.sell(portfolio.position, price, timestamp)

# Portfolio tracks: cash, position, trades, pnl
```

**When to Use Vectorized vs Event-Driven**:
- **Vectorized**: Simple strategies, daily rebalance, no intraday
- **Event-driven**: Complex logic, intraday, order dependency

---

## 🔢 Category 5: Greeks & Options

### Mistake 5.1: PA/BS Greeks 혼용

**Bad Code**:
```python
# ❌ Mixing PA (BTC) and BS (USD) Greeks
portfolio_theta = sum([
    position1.theta_pa,  # -0.001 BTC/day
    position2.theta_bs   # -110 USD/day ← 단위 다름!
])
# Result: -110.001 (무의미)
```

**Why It's Bad**:
- 단위 불일치 (BTC + USD)
- Portfolio 집계 무의미
- Risk management 불가능

**Correct Code**:
```python
# ✅ 모두 BS (USD)로 통일
from greeks_converter import GreeksConverter

converter = GreeksConverter(btc_price=88500)

portfolio_theta_bs = sum([
    converter.okx_pa_to_usd(pos.theta_pa, 'theta') if pos.greeks_type == 'PA'
    else pos.theta_bs
    for pos in positions
])

# Result: -320.5 USD/day ✅
```

**Rule**: **Portfolio 집계는 항상 BS (USD) 단위**

**Related**: `exchanges/greeks_definitions.md`, `exchanges/greeks_converter.py`

---

### Mistake 5.2: 옵션 만기 처리 누락

**Bad Code**:
```python
# ❌ 만기일에도 포지션 유지
# 2024-12-27 08:00 UTC: 옵션 만기
# 백테스트: 만기 후에도 position 유지 (가격 = $0)
```

**Why It's Bad**:
- 만기 후 포지션 = $0 (OTM) 또는 intrinsic value (ITM)
- Mark price 사라짐
- PnL 계산 오류

**Correct Code**:
```python
# ✅ 만기 시 자동 청산
for timestamp, positions in portfolio.items():
    for pos in positions:
        if timestamp >= pos.expiry_time:
            # ITM: exercise (intrinsic value)
            if pos.is_itm():
                settlement_value = pos.intrinsic_value()
                portfolio.cash += settlement_value * pos.quantity

            # OTM: expire worthless
            else:
                pass  # Position value = 0

            # Remove position
            portfolio.remove(pos)
```

**Expiry Time**: OKX options expire at **UTC 08:00** (KST 17:00)

**Related**: `exchanges/okx/options_specifications.md`

---

### Mistake 5.3: Implied Volatility를 Constant로 가정

**Bad Code**:
```python
# ❌ IV를 고정값으로 가정
iv = 0.50  # 50% volatility
price = black_scholes(S, K, T, r, iv)

# 문제: IV는 시간/가격에 따라 변동 (smile, term structure)
```

**Why It's Bad**:
- IV smile 무시 (ATM vs OTM IV 다름)
- Term structure 무시 (만기별 IV 다름)
- 현실과 괴리

**Correct Code**:
```python
# ✅ Market IV 사용 (OKX mark IV)
iv = get_mark_iv(timestamp, symbol)
price = black_scholes(S, K, T, r, iv)

# ✅ Or interpolate IV surface
iv_surface = build_iv_surface(options_data)
iv = iv_surface.interpolate(moneyness, dte)
```

**Rule**: **Market IV 사용** (constant IV 금지)

---

## 📝 Category 6: Code Organization

### Mistake 6.1: Magic Numbers (하드코딩된 상수)

**Bad Code**:
```python
# ❌ Magic numbers everywhere
if volatility > 0.8:  # ← 0.8의 의미?
    ...

df['signal'] = (df['price'] > df['ma_20'] * 1.05).astype(int)  # ← 1.05는?

fee = notional * 0.0003  # ← 0.0003은?
```

**Why It's Bad**:
- 숫자의 의미 불명확
- 수정 시 모든 곳 변경 필요
- 실수 가능성 높음

**Correct Code**:
```python
# ✅ Named constants
HIGH_VOLATILITY_THRESHOLD = 0.8
BREAKOUT_MULTIPLIER = 1.05
TAKER_FEE_RATE = 0.0003  # 0.03%

if volatility > HIGH_VOLATILITY_THRESHOLD:
    ...

df['signal'] = (df['price'] > df['ma_20'] * BREAKOUT_MULTIPLIER).astype(int)

fee = notional * TAKER_FEE_RATE
```

**Rule**: **숫자는 항상 named constant** (except 0, 1, -1)

---

### Mistake 6.2: 함수가 너무 긺 (>100 lines)

**Bad Code**:
```python
# ❌ 500-line monster function
def run_backtest(data, params):
    # 데이터 로드 (50 lines)
    # 전처리 (100 lines)
    # Feature 계산 (150 lines)
    # Signal 생성 (100 lines)
    # PnL 계산 (100 lines)
    # 결과 출력 (50 lines)
    ...
    return results
```

**Why It's Bad**:
- 이해 어려움
- 테스트 불가능
- 재사용 불가능

**Correct Code**:
```python
# ✅ 함수 분리 (Single Responsibility Principle)
def run_backtest(data, params):
    data_clean = preprocess_data(data)
    features = calculate_features(data_clean, params)
    signals = generate_signals(features, params)
    trades = execute_trades(signals, data_clean, params)
    results = calculate_metrics(trades)
    return results

# 각 함수는 20-50 lines, 명확한 책임
```

**Rule**: **함수는 50 lines 이하** (100 lines 절대 초과 금지)

---

### Mistake 6.3: 변수명이 불명확 (`df`, `temp`, `x`)

**Bad Code**:
```python
# ❌ 의미 없는 변수명
df = load_data()
df2 = df[df['x'] > 100]
temp = df2['y'].mean()
result = temp * 1.5
```

**Why It's Bad**:
- 코드 의미 파악 불가
- 디버깅 어려움
- 유지보수 불가능

**Correct Code**:
```python
# ✅ Descriptive names
options_data = load_options_data()
filtered_options = options_data[options_data['volume'] > 100]
avg_iv = filtered_options['implied_volatility'].mean()
iv_threshold = avg_iv * 1.5
```

**Rule**: **변수명은 의미 명확** (약어 최소화)

---

## 🐛 Category 7: Debugging & Testing

### Mistake 7.1: `print()` 대신 Logging 미사용

**Bad Code**:
```python
# ❌ print() everywhere
print("Loading data...")
print(f"Data shape: {df.shape}")
print("Running backtest...")
print(f"Sharpe: {sharpe}")
```

**Why It's Bad**:
- Production에서 print 제거 필요
- 로그 레벨 조절 불가
- 파일 저장 불가

**Correct Code**:
```python
# ✅ Logging module
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backtest.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

logger.info("Loading data...")
logger.info(f"Data shape: {df.shape}")
logger.info("Running backtest...")
logger.info(f"Sharpe: {sharpe:.2f}")
```

**Rule**: **print() 금지**, logging 사용

---

### Mistake 7.2: Try-Except로 에러 숨기기

**Bad Code**:
```python
# ❌ Catch all exceptions and ignore
try:
    result = complex_calculation()
except:
    pass  # ← 에러 무시

# 문제 발생해도 알 수 없음
```

**Why It's Bad**:
- 실제 버그 숨김
- 디버깅 불가능
- Silent failure

**Correct Code**:
```python
# ✅ Specific exception handling
try:
    result = complex_calculation()
except ValueError as e:
    logger.error(f"Invalid value: {e}")
    result = None  # Or default value
except KeyError as e:
    logger.error(f"Missing key: {e}")
    raise  # Re-raise if critical
except Exception as e:
    logger.exception(f"Unexpected error: {e}")  # Logs traceback
    raise
```

**Rule**: **Specific exception만 catch**, bare `except:` 금지

---

### Mistake 7.3: Assertion 미사용 (Sanity Check 부재)

**Bad Code**:
```python
# ❌ No validation
portfolio_value = calculate_portfolio_value()
# 음수 가능? NaN 가능? → 검증 없음
```

**Why It's Bad**:
- 잘못된 결과로 계속 진행
- 나중에 원인 파악 어려움

**Correct Code**:
```python
# ✅ Assertions for sanity checks
portfolio_value = calculate_portfolio_value()

assert portfolio_value >= 0, f"Negative portfolio value: {portfolio_value}"
assert not np.isnan(portfolio_value), "Portfolio value is NaN"
assert portfolio_value < initial_capital * 100, "Unrealistic portfolio value"

# Development: assertions active
# Production: can disable with -O flag
```

**Rule**: **Critical values는 assertion으로 검증**

---

## ✅ Quick Checklist (코드 작성 전)

### Before Writing Code:

- [ ] **Variable names**: Descriptive (not `df`, `temp`, `x`)
- [ ] **Constants**: Named (not magic numbers)
- [ ] **Function length**: < 50 lines
- [ ] **Timezone**: All datetime in UTC
- [ ] **Logging**: Use `logging`, not `print()`

### Before Running Backtest:

- [ ] **Shift direction**: `shift(1)` = past, `shift(-1)` = future
- [ ] **Position tracking**: Explicit state (flat/long/short)
- [ ] **Greeks units**: All BS (USD) for portfolio
- [ ] **Rate limiting**: API calls under limit
- [ ] **Credentials**: Not in code (environment variables)

### After Backtest:

- [ ] **Assertions**: Portfolio value >= 0, no NaN
- [ ] **Reconciliation**: Position/Cash/PnL consistent
- [ ] **Logging**: All trades logged
- [ ] **Error handling**: Try-except with specific exceptions
- [ ] **Git**: No credentials committed

---

## 📚 Related Documentation

- **Lessons Learned**: `experiments/lessons_learned.md` - Conceptual failures
- **Common Pitfalls**: `experiments/common_pitfalls.md` - Bias types
- **Methodology**: `experiments/methodology.md` - Experiment design
- **Backtesting Integrity**: `~/.claude/rules/10_backtesting_integrity.md` - Reconciliation

---

**Last Updated**: 2025-12-23
**Version**: 1.0
**Maintainer**: sqr

**Contributing**: 새로운 실수 발견 시 이 문서에 추가 (반복 방지)
