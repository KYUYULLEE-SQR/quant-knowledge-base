# OKX API Reference

**Purpose**: OKX API 주요 endpoint 및 rate limit 정리 (Options, Futures, Market Data)

**Last Updated**: 2025-12-23
**Owner**: sqr
**Environment**: micky (data), spice (backtest), vultr (trading)

---

## 📌 Quick Reference

| Category | Endpoint | Rate Limit | Auth | Use Case |
|----------|----------|------------|------|----------|
| **Market Data** | `/api/v5/market/tickers` | 20 req/2s | ❌ Public | 전체 심볼 ticker 조회 |
| **Market Data** | `/api/v5/market/ticker` | 20 req/2s | ❌ Public | 특정 심볼 ticker 조회 |
| **Market Data** | `/api/v5/market/books` | 20 req/2s | ❌ Public | Order book (depth) |
| **Market Data** | `/api/v5/market/candles` | 40 req/2s | ❌ Public | OHLCV 캔들 |
| **Options** | `/api/v5/public/opt-summary` | 20 req/2s | ❌ Public | 옵션 Greeks, IV, mark price |
| **Options** | `/api/v5/public/instruments` | 20 req/2s | ❌ Public | 옵션 계약 스펙 (만기, strike) |
| **Trading** | `/api/v5/trade/order` | 60 req/2s | ✅ Private | 주문 생성 |
| **Trading** | `/api/v5/trade/cancel-order` | 60 req/2s | ✅ Private | 주문 취소 |
| **Trading** | `/api/v5/trade/orders-pending` | 20 req/2s | ✅ Private | 미체결 주문 조회 |
| **Account** | `/api/v5/account/balance` | 10 req/2s | ✅ Private | 계좌 잔고 |
| **Account** | `/api/v5/account/positions` | 10 req/2s | ✅ Private | 포지션 조회 |
| **Account** | `/api/v5/account/account-position-risk` | 10 req/2s | ✅ Private | Greeks 포트폴리오 합계 |

---

## 🔗 Official Documentation

**Base URL**: `https://www.okx.com`

**Official Docs**:
- Main API Docs: https://www.okx.com/docs-v5/en/
- Options Trading: https://www.okx.com/docs-v5/en/#trading-account-rest-api
- Market Data: https://www.okx.com/docs-v5/en/#market-data-rest-api
- WebSocket: https://www.okx.com/docs-v5/en/#websocket-api

**API Version**: v5 (current as of 2025-12-23)

---

## 🔑 Authentication

### API Key Requirements

**3-key system**:
- `API Key` (Public identifier)
- `Secret Key` (Signing key)
- `Passphrase` (User-defined password)

**Credentials location**:
- **DO NOT hardcode** in scripts
- Store in: `~/.credentials/okx_api_key.md` (NOT in git)
- Load via environment variables or config

### Authentication Headers

**Required headers for private endpoints**:

```python
import hmac
import base64
from datetime import datetime

def sign_request(timestamp, method, request_path, body, secret_key):
    """Generate OKX API signature."""
    if body:
        body_str = json.dumps(body)
    else:
        body_str = ''

    # Prehash string: timestamp + method + requestPath + body
    prehash = timestamp + method + request_path + body_str

    # HMAC-SHA256 signature
    signature = base64.b64encode(
        hmac.new(
            secret_key.encode('utf-8'),
            prehash.encode('utf-8'),
            digestmod='sha256'
        ).digest()
    ).decode('utf-8')

    return signature

# Example headers
timestamp = datetime.utcnow().isoformat(timespec='milliseconds') + 'Z'
signature = sign_request(timestamp, 'GET', '/api/v5/account/balance', '', SECRET_KEY)

headers = {
    'OK-ACCESS-KEY': API_KEY,
    'OK-ACCESS-SIGN': signature,
    'OK-ACCESS-TIMESTAMP': timestamp,
    'OK-ACCESS-PASSPHRASE': PASSPHRASE,
    'Content-Type': 'application/json'
}
```

**Important**:
- Timestamp must be ISO 8601 UTC format with milliseconds: `2025-12-23T12:34:56.789Z`
- Signature expires in 30 seconds
- Wrong timestamp = `400 Bad Request` error

---

## 📊 Market Data Endpoints (Public)

### 1. `/api/v5/market/tickers` - All Tickers

**Request**:
```python
import requests

url = "https://www.okx.com/api/v5/market/tickers"
params = {
    'instType': 'OPTION',      # SPOT, FUTURES, SWAP, OPTION
    'uly': 'BTC-USD'           # Underlying (optional)
}
response = requests.get(url, params=params)
data = response.json()
```

**Response** (example):
```json
{
  "code": "0",
  "msg": "",
  "data": [
    {
      "instType": "OPTION",
      "instId": "BTC-USD-250110-90000-C",
      "last": "2850",
      "lastSz": "1",
      "askPx": "2875",
      "askSz": "50",
      "bidPx": "2825",
      "bidSz": "40",
      "open24h": "2900",
      "high24h": "3100",
      "low24h": "2750",
      "volCcy24h": "125.3",
      "vol24h": "42",
      "ts": "1703318400000"
    }
  ]
}
```

**Rate Limit**: 20 req/2s
**Use Case**: 전체 옵션 체인 스캔 (IV surface, mispricing 탐지)

---

### 2. `/api/v5/public/opt-summary` - Options Greeks & IV

**Request**:
```python
url = "https://www.okx.com/api/v5/public/opt-summary"
params = {
    'uly': 'BTC-USD',          # Required
    'instFamily': 'BTC-USD',   # Optional (same as uly)
    'expTime': ''              # Optional: filter by expiry (unix timestamp ms)
}
response = requests.get(url, params=params)
data = response.json()
```

**Response** (example):
```json
{
  "code": "0",
  "msg": "",
  "data": [
    {
      "instId": "BTC-USD-250110-90000-C",
      "instType": "OPTION",
      "uly": "BTC-USD",
      "delta": "0.4523",        # BS Delta (dimensionless)
      "gamma": "0.000124",      # BS Gamma (delta/$1)
      "vega": "18.45",          # BS Vega (USD per 1% IV)
      "theta": "-110.39",       # BS Theta (USD/day)
      "deltaBS": "0.4523",      # Same as delta
      "gammaBS": "0.000124",    # Same as gamma
      "vegaBS": "18.45",        # Same as vega
      "thetaBS": "-110.39",     # Same as theta
      "deltaPA": "0.0051",      # PA Delta (BTC)
      "gammaPA": "11.99",       # PA Gamma (⚠️ unit unclear)
      "vegaPA": "0.00021",      # PA Vega (BTC per 1% IV)
      "thetaPA": "-0.001172",   # PA Theta (BTC/day)
      "markVol": "0.5234",      # Mark IV (52.34%)
      "bidVol": "0.5187",       # Bid IV
      "askVol": "0.5281",       # Ask IV
      "realVol": "0.4890",      # Realized volatility (historical)
      "volLv": "0.5234",        # Volatility level (same as markVol)
      "lever": "12.35",         # Leverage
      "fwdPx": "88526.5",       # Forward price (BTC price for pricing)
      "markPx": "2845.3",       # Mark price (USD)
      "ts": "1703318400000"     # Timestamp (unix ms)
    }
  ]
}
```

**Key Fields**:
- **Greeks**: PA (BTC units) vs BS (USD units) - see `exchanges/greeks_definitions.md`
- **Mark IV** (`markVol`): OKX의 fair IV (백테스트 시 이 값과 비교)
- **Bid/Ask IV**: 실제 호가 기준 IV
- **Forward Price** (`fwdPx`): Greeks 계산에 사용된 BTC 가격

**Rate Limit**: 20 req/2s
**Use Case**: Greeks tracking, IV surface 분석, Fair IV 모델 검증

---

### 3. `/api/v5/public/instruments` - Instrument Specifications

**Request**:
```python
url = "https://www.okx.com/api/v5/public/instruments"
params = {
    'instType': 'OPTION',
    'uly': 'BTC-USD',
    'instFamily': 'BTC-USD'
}
response = requests.get(url, params=params)
```

**Response** (example):
```json
{
  "code": "0",
  "data": [
    {
      "instId": "BTC-USD-250110-90000-C",
      "instType": "OPTION",
      "uly": "BTC-USD",
      "instFamily": "BTC-USD",
      "category": "1",           # 1=Normal, 2=Quarterly
      "optType": "C",            # C=Call, P=Put
      "stk": "90000",            # Strike price
      "expTime": "1736496000000", # Expiry time (unix ms, UTC 08:00)
      "listTime": "1703318400000",
      "tickSz": "5",             # Tick size (min price increment)
      "lotSz": "0.1",            # Lot size (min quantity)
      "minSz": "0.1",            # Min order size
      "ctType": "linear",        # Contract type (linear/inverse)
      "ctVal": "0.01",           # Contract value (BTC)
      "ctMult": "1",             # Contract multiplier
      "settleCcy": "BTC",        # Settlement currency
      "quoteCcy": "USD",         # Quote currency
      "state": "live",           # live, suspend, preopen, expired
      "lever": "10",             # Max leverage
      "alias": "this-week",      # Alias (this-week, next-week, quarter)
      "ts": "1703318400000"
    }
  ]
}
```

**Rate Limit**: 20 req/2s
**Use Case**: 옵션 체인 구조 파악 (만기, strike 리스트)

---

### 4. `/api/v5/market/books` - Order Book (Depth)

**Request**:
```python
url = "https://www.okx.com/api/v5/market/books"
params = {
    'instId': 'BTC-USD-250110-90000-C',
    'sz': '400'  # Depth level (max 400)
}
response = requests.get(url, params=params)
```

**Response** (example):
```json
{
  "code": "0",
  "data": [
    {
      "asks": [
        ["2875", "50", "0", "3"],   # [price, quantity, deprecated, num_orders]
        ["2880", "30", "0", "2"],
        ["2885", "20", "0", "1"]
      ],
      "bids": [
        ["2825", "40", "0", "2"],
        ["2820", "25", "0", "1"],
        ["2815", "15", "0", "1"]
      ],
      "ts": "1703318400123"
    }
  ]
}
```

**Rate Limit**: 20 req/2s
**Use Case**: Slippage 추정, Market making depth 분석

---

### 5. `/api/v5/market/candles` - OHLCV Candles

**Request**:
```python
url = "https://www.okx.com/api/v5/market/candles"
params = {
    'instId': 'BTC-USD-250110-90000-C',
    'bar': '1H',              # 1m, 5m, 15m, 1H, 4H, 1D
    'limit': '100',           # Max 100 (default: 100)
    'after': '',              # Pagination (unix ms timestamp)
    'before': ''
}
response = requests.get(url, params=params)
```

**Response** (example):
```json
{
  "code": "0",
  "data": [
    [
      "1703318400000",  # Timestamp (open time, unix ms)
      "2900",           # Open
      "3100",           # High
      "2850",           # Low
      "2875",           # Close
      "42",             # Volume (contracts)
      "125.3",          # Volume (quote currency, USD)
      "125.3",          # Volume (quote currency, USD) - duplicate
      "1"               # Confirm (0=latest candle, 1=historical)
    ]
  ]
}
```

**Rate Limit**: 40 req/2s
**Use Case**: Volatility 계산, Backtesting price history

---

## 🔐 Trading Endpoints (Private)

### 1. `/api/v5/trade/order` - Place Order

**Request**:
```python
import requests
import json

url = "https://www.okx.com/api/v5/trade/order"
payload = {
    "instId": "BTC-USD-250110-90000-C",
    "tdMode": "cash",         # cash, cross, isolated
    "side": "buy",            # buy, sell
    "ordType": "limit",       # limit, market, post_only
    "px": "2850",             # Limit price (omit for market)
    "sz": "1",                # Quantity (contracts)
    "clOrdId": "user_order_123"  # Client order ID (optional)
}

# Add authentication headers
headers = {
    'OK-ACCESS-KEY': API_KEY,
    'OK-ACCESS-SIGN': signature,
    'OK-ACCESS-TIMESTAMP': timestamp,
    'OK-ACCESS-PASSPHRASE': PASSPHRASE,
    'Content-Type': 'application/json'
}

response = requests.post(url, headers=headers, data=json.dumps(payload))
```

**Response** (success):
```json
{
  "code": "0",
  "msg": "",
  "data": [
    {
      "ordId": "584735902597726208",
      "clOrdId": "user_order_123",
      "tag": "",
      "sCode": "0",
      "sMsg": ""
    }
  ]
}
```

**Response** (error):
```json
{
  "code": "51008",
  "msg": "Order placement failed due to insufficient balance",
  "data": []
}
```

**Rate Limit**: 60 req/2s
**Important**:
- `ordType: "post_only"` → Maker-only (거래소 maker fee 적용)
- Market order 사용 시 slippage 주의
- `clOrdId` 권장 (거래 추적용)

---

### 2. `/api/v5/trade/cancel-order` - Cancel Order

**Request**:
```python
url = "https://www.okx.com/api/v5/trade/cancel-order"
payload = {
    "instId": "BTC-USD-250110-90000-C",
    "ordId": "584735902597726208"  # or "clOrdId": "user_order_123"
}
response = requests.post(url, headers=headers, data=json.dumps(payload))
```

**Response**:
```json
{
  "code": "0",
  "msg": "",
  "data": [
    {
      "ordId": "584735902597726208",
      "clOrdId": "user_order_123",
      "sCode": "0",
      "sMsg": ""
    }
  ]
}
```

**Rate Limit**: 60 req/2s

---

### 3. `/api/v5/trade/orders-pending` - Pending Orders

**Request**:
```python
url = "https://www.okx.com/api/v5/trade/orders-pending"
params = {
    'instType': 'OPTION',
    'uly': 'BTC-USD',
    'instId': 'BTC-USD-250110-90000-C'  # Optional (specific instrument)
}
response = requests.get(url, params=params, headers=headers)
```

**Response**:
```json
{
  "code": "0",
  "data": [
    {
      "instType": "OPTION",
      "instId": "BTC-USD-250110-90000-C",
      "ordId": "584735902597726208",
      "clOrdId": "user_order_123",
      "px": "2850",
      "sz": "1",
      "fillPx": "0",
      "fillSz": "0",
      "avgPx": "0",
      "state": "live",          # live, partially_filled
      "side": "buy",
      "ordType": "post_only",
      "uTime": "1703318400123",
      "cTime": "1703318400000"
    }
  ]
}
```

**Rate Limit**: 20 req/2s
**Use Case**: 미체결 주문 모니터링, Maker order 체결 확인

---

## 💰 Account Endpoints (Private)

### 1. `/api/v5/account/balance` - Account Balance

**Request**:
```python
url = "https://www.okx.com/api/v5/account/balance"
params = {
    'ccy': 'BTC'  # Optional (specific currency)
}
response = requests.get(url, params=params, headers=headers)
```

**Response**:
```json
{
  "code": "0",
  "data": [
    {
      "uTime": "1703318400000",
      "totalEq": "10.5234",     # Total equity (BTC)
      "isoEq": "0",             # Isolated margin equity
      "adjEq": "10.2345",       # Adjusted equity (with unrealized)
      "ordFroz": "0.1234",      # Frozen for orders
      "imr": "0.5678",          # Initial margin requirement
      "mmr": "0.2839",          # Maintenance margin requirement
      "mgnRatio": "35.42",      # Margin ratio (%)
      "notionalUsd": "945231.45", # Total notional (USD)
      "details": [
        {
          "ccy": "BTC",
          "eq": "10.5234",      # Equity
          "cashBal": "10.0000", # Cash balance
          "availBal": "9.3996", # Available balance
          "frozenBal": "0.1234", # Frozen
          "ordFrozen": "0.1234", # Frozen for orders
          "upl": "0.5234",      # Unrealized PnL
          "uplLiab": "0"
        }
      ]
    }
  ]
}
```

**Rate Limit**: 10 req/2s
**Use Case**: NAV 계산, 마진 관리

---

### 2. `/api/v5/account/positions` - Current Positions

**Request**:
```python
url = "https://www.okx.com/api/v5/account/positions"
params = {
    'instType': 'OPTION',
    'instId': 'BTC-USD-250110-90000-C'  # Optional
}
response = requests.get(url, params=params, headers=headers)
```

**Response**:
```json
{
  "code": "0",
  "data": [
    {
      "instType": "OPTION",
      "instId": "BTC-USD-250110-90000-C",
      "pos": "-5",              # Position (negative = short)
      "availPos": "-5",         # Available to close
      "avgPx": "2850",          # Average entry price
      "upl": "-125.5",          # Unrealized PnL (USD)
      "uplRatio": "-0.0088",    # Unrealized PnL ratio
      "markPx": "2875.1",       # Current mark price
      "notionalUsd": "14375.5", # Notional (USD)
      "lever": "10",            # Leverage
      "margin": "1437.55",      # Margin used
      "mgnRatio": "12.34",      # Margin ratio
      "uTime": "1703318400123",
      "cTime": "1703318400000"
    }
  ]
}
```

**Rate Limit**: 10 req/2s
**Use Case**: 포지션 추적, Mark-to-market NAV 계산

---

### 3. `/api/v5/account/account-position-risk` - Portfolio Greeks

**Request**:
```python
url = "https://www.okx.com/api/v5/account/account-position-risk"
params = {
    'instType': 'OPTION'
}
response = requests.get(url, params=params, headers=headers)
```

**Response**:
```json
{
  "code": "0",
  "data": [
    {
      "adjEq": "10.2345",
      "balData": [
        {
          "ccy": "BTC",
          "eq": "10.5234",
          "disEq": "934521.45"  # Equity in USD
        }
      ],
      "posData": [
        {
          "instType": "OPTION",
          "instId": "BTC-USD-250110-90000-C",
          "pos": "-5",
          "notionalCcy": "71877.5",
          "notionalUsd": "71877.5",
          "deltaBS": "-2.2615",        # Portfolio Delta (BS)
          "deltaPA": "-0.0255",        # Portfolio Delta (PA, BTC)
          "gammaBS": "0.000620",       # Portfolio Gamma (BS)
          "gammaPA": "59.95",          # Portfolio Gamma (PA)
          "vegaBS": "92.25",           # Portfolio Vega (BS, USD)
          "vegaPA": "0.00105",         # Portfolio Vega (PA, BTC)
          "thetaBS": "-551.95",        # Portfolio Theta (BS, USD/day)
          "thetaPA": "-0.005860"       # Portfolio Theta (PA, BTC/day)
        }
      ],
      "ts": "1703318400123"
    }
  ]
}
```

**Rate Limit**: 10 req/2s
**Use Case**:
- Portfolio Greeks 모니터링
- Delta hedging
- Theta decay tracking
- Risk management

**Important**:
- Greeks are **aggregated across all positions** in the same instrument
- PA vs BS units - see `exchanges/greeks_definitions.md`
- Use for portfolio-level risk, not individual position Greeks

---

## ⚙️ Rate Limits

### Per-Endpoint Limits

| Endpoint Type | Limit | Window | Notes |
|---------------|-------|--------|-------|
| Market Data (Public) | 20 req | 2 seconds | Per IP |
| Candles | 40 req | 2 seconds | Higher limit |
| Trading (Private) | 60 req | 2 seconds | Per UID (user) |
| Account (Private) | 10 req | 2 seconds | Per UID |

### Rate Limit Response

**When rate limit exceeded**:
```json
{
  "code": "50011",
  "msg": "Rate limit exceeded",
  "data": []
}
```

**Retry-After**: Check `X-RateLimit-Reset` header (unix timestamp)

### Best Practices

1. **Batch requests** when possible (e.g., `/api/v5/market/tickers` instead of per-symbol)
2. **Cache data** (e.g., instrument specs change rarely)
3. **Exponential backoff** on rate limit errors
4. **WebSocket for real-time** (lower rate limit impact)

**Example rate limiter**:
```python
import time
from collections import deque

class RateLimiter:
    def __init__(self, max_requests, window_seconds):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = deque()

    def acquire(self):
        now = time.time()

        # Remove requests outside window
        while self.requests and self.requests[0] < now - self.window_seconds:
            self.requests.popleft()

        # Check if limit exceeded
        if len(self.requests) >= self.max_requests:
            sleep_time = self.window_seconds - (now - self.requests[0])
            if sleep_time > 0:
                time.sleep(sleep_time)
                self.acquire()  # Retry
                return

        # Record request
        self.requests.append(now)

# Usage
market_data_limiter = RateLimiter(max_requests=20, window_seconds=2)
trading_limiter = RateLimiter(max_requests=60, window_seconds=2)

market_data_limiter.acquire()
response = requests.get("https://www.okx.com/api/v5/market/tickers", params=...)
```

---

## 🔍 Common API Patterns

### 1. Get All Option Strikes for Expiry

```python
def get_option_chain(expiry_date: str, uly: str = 'BTC-USD'):
    """
    Get all strikes for a specific expiry.

    Args:
        expiry_date: 'YYMMDD' format (e.g., '250110')
        uly: Underlying

    Returns:
        List of option contracts
    """
    url = "https://www.okx.com/api/v5/public/instruments"
    params = {
        'instType': 'OPTION',
        'uly': uly,
        'instFamily': uly
    }

    response = requests.get(url, params=params)
    data = response.json()

    if data['code'] != '0':
        raise Exception(f"API Error: {data['msg']}")

    # Filter by expiry
    chain = [
        inst for inst in data['data']
        if expiry_date in inst['instId']
    ]

    return chain

# Example
chain = get_option_chain('250110')  # BTC-USD-250110-*
# Result: All strikes for Jan 10, 2025 expiry
```

### 2. Calculate Fair IV vs Mark IV Spread

```python
def get_iv_mispricing(fair_iv_model, uly: str = 'BTC-USD'):
    """
    Compare model fair IV with OKX mark IV.

    Returns:
        List of (instId, fair_iv, mark_iv, spread)
    """
    url = "https://www.okx.com/api/v5/public/opt-summary"
    params = {'uly': uly, 'instFamily': uly}

    response = requests.get(url, params=params)
    data = response.json()['data']

    results = []
    for opt in data:
        inst_id = opt['instId']
        mark_iv = float(opt['markVol'])

        # Calculate fair IV from model
        fair_iv = fair_iv_model.predict(opt)  # Your model

        spread = (mark_iv - fair_iv) / fair_iv  # Relative spread

        results.append({
            'instId': inst_id,
            'fair_iv': fair_iv,
            'mark_iv': mark_iv,
            'spread_pct': spread * 100,
            'delta': float(opt['deltaBS']),
            'dte': calculate_dte(opt['instId'])  # Days to expiry
        })

    return results

# Example
mispricing = get_iv_mispricing(my_fair_iv_model)
overpriced = [x for x in mispricing if x['spread_pct'] > 10]  # >10% overpriced
```

### 3. Monitor Maker Order Fill Rate

```python
import time

def monitor_fill_rate(order_id: str, timeout: int = 60):
    """
    Monitor maker order fill rate over time.

    Returns:
        Fill ratio (0.0 to 1.0)
    """
    url = "https://www.okx.com/api/v5/trade/order"
    params = {'ordId': order_id}

    start_time = time.time()

    while time.time() - start_time < timeout:
        response = requests.get(url, params=params, headers=auth_headers)
        data = response.json()['data'][0]

        state = data['state']
        fill_sz = float(data['fillSz'])
        total_sz = float(data['sz'])

        fill_ratio = fill_sz / total_sz

        print(f"Fill: {fill_ratio:.1%} ({fill_sz}/{total_sz}), State: {state}")

        if state == 'filled':
            return 1.0
        elif state == 'canceled':
            return fill_ratio

        time.sleep(5)  # Check every 5s

    return fill_ratio

# Example
fill_ratio = monitor_fill_rate('584735902597726208', timeout=60)
# Typical result: 0.3 (30% fill) for maker orders
```

---

## ⚠️ Common Errors

### 1. Authentication Errors

**Error Code**: `50113`
**Message**: "Invalid sign"

**Cause**:
- Wrong timestamp format (must be ISO 8601 UTC with milliseconds)
- Incorrect prehash string order (timestamp + method + path + body)
- Wrong secret key

**Fix**:
```python
# ✅ Correct timestamp
timestamp = datetime.utcnow().isoformat(timespec='milliseconds') + 'Z'
# Example: "2025-12-23T12:34:56.789Z"

# ❌ Wrong
timestamp = str(int(time.time() * 1000))  # Unix ms (OKX doesn't accept this)
```

### 2. Insufficient Balance

**Error Code**: `51008`
**Message**: "Order placement failed due to insufficient balance"

**Cause**:
- Not enough margin
- Frozen balance (pending orders)

**Fix**:
```python
# Check available balance before order
balance_resp = requests.get(
    "https://www.okx.com/api/v5/account/balance",
    params={'ccy': 'BTC'},
    headers=auth_headers
)
avail_bal = float(balance_resp.json()['data'][0]['details'][0]['availBal'])

# Only order if sufficient
if avail_bal > required_margin:
    place_order(...)
```

### 3. Rate Limit Exceeded

**Error Code**: `50011`
**Message**: "Rate limit exceeded"

**Fix**: Implement rate limiter (see above)

### 4. Invalid Parameter

**Error Code**: `51000`
**Message**: "Parameter {param} error"

**Common causes**:
- Wrong `instId` format (must be exact: `BTC-USD-250110-90000-C`)
- Invalid `ordType` value (must be: `limit`, `market`, `post_only`)
- Missing required field

---

## 🎯 Integration Checklist

### Before Production Trading:

- [ ] **Credentials stored securely** (NOT in git)
- [ ] **Rate limiter implemented** (per-endpoint limits)
- [ ] **Error handling** (retry on 50011, abort on 51008)
- [ ] **Logging** (all API calls + responses)
- [ ] **Testnet verification** (use `https://www.okx.com/api/v5/...` with testnet keys first)
- [ ] **Timestamp validation** (UTC ISO 8601 format)
- [ ] **Greeks unit awareness** (PA vs BS - see `exchanges/greeks_definitions.md`)
- [ ] **Mark IV vs Bid/Ask IV** (use correct field for strategy)
- [ ] **Maker order monitoring** (30% fill assumption verified)

---

## 📚 Related Documentation

- **Greeks Units**: `exchanges/greeks_definitions.md`
- **Fee Structure**: `exchanges/okx/fee_structure.md`
- **Options Specs**: `exchanges/okx/options_specifications.md`
- **Order Execution**: `exchanges/okx/order_execution.md`
- **Transaction Costs**: `modeling/transaction_cost_model.md`

---

**Last Updated**: 2025-12-23
**Version**: 1.0
**Maintainer**: sqr

**Source**: OKX API v5 Documentation (https://www.okx.com/docs-v5/en/)
