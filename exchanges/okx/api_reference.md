# OKX API Reference

**Purpose**: OKX API 주요 endpoint 및 rate limit 정리
**Last Updated**: 2025-12-25
**Version**: 2.0 (Condensed)

---

## 📌 Quick Reference

| Category | Endpoint | Rate Limit | Auth | Use Case |
|----------|----------|------------|------|----------|
| **Tickers** | `/api/v5/market/tickers` | 20/2s | ❌ | 전체 심볼 조회 |
| **Order Book** | `/api/v5/market/books` | 20/2s | ❌ | Depth (max 400) |
| **Candles** | `/api/v5/market/candles` | 40/2s | ❌ | OHLCV (max 100) |
| **Greeks/IV** | `/api/v5/public/opt-summary` | 20/2s | ❌ | 옵션 Greeks, Mark IV |
| **Instruments** | `/api/v5/public/instruments` | 20/2s | ❌ | 옵션 스펙 (만기, strike) |
| **Order** | `/api/v5/trade/order` | 60/2s | ✅ | 주문 생성 |
| **Cancel** | `/api/v5/trade/cancel-order` | 60/2s | ✅ | 주문 취소 |
| **Balance** | `/api/v5/account/balance` | 10/2s | ✅ | 계좌 잔고 |
| **Positions** | `/api/v5/account/positions` | 10/2s | ✅ | 포지션 조회 |

**Base URL**: `https://www.okx.com`
**Docs**: https://www.okx.com/docs-v5/en/

---

## 🔑 Authentication

```python
import hmac, base64, json
from datetime import datetime

def sign_request(timestamp, method, request_path, body, secret_key):
    prehash = timestamp + method + request_path + (json.dumps(body) if body else '')
    signature = base64.b64encode(
        hmac.new(secret_key.encode(), prehash.encode(), 'sha256').digest()
    ).decode()
    return signature

timestamp = datetime.utcnow().isoformat(timespec='milliseconds') + 'Z'
headers = {
    'OK-ACCESS-KEY': API_KEY,
    'OK-ACCESS-SIGN': sign_request(timestamp, 'GET', '/api/v5/account/balance', '', SECRET),
    'OK-ACCESS-TIMESTAMP': timestamp,
    'OK-ACCESS-PASSPHRASE': PASSPHRASE
}
```

**⚠️ Important**: Timestamp = ISO 8601 UTC (`2025-12-25T12:34:56.789Z`), 30초 후 만료

---

## 📊 Key Endpoints

### `/api/v5/public/opt-summary` (Options Greeks)

```python
response = requests.get("https://www.okx.com/api/v5/public/opt-summary",
                       params={'uly': 'BTC-USD'})
# Key fields:
# delta/deltaBS (BS), deltaPA (BTC units)
# markVol (Mark IV), bidVol, askVol
# fwdPx (Forward price for pricing)
```

**Greeks Units**: BS = USD, PA = BTC (See `greeks_definitions.md`)

### `/api/v5/trade/order` (Place Order)

```python
payload = {
    "instId": "BTC-USD-250110-90000-C",
    "tdMode": "cash",
    "side": "buy",
    "ordType": "post_only",  # Maker-only
    "px": "2850",
    "sz": "1"
}
response = requests.post(url, headers=headers, json=payload)
```

---

## ⚙️ Rate Limits

| Type | Limit | Window |
|------|-------|--------|
| Market Data | 20 req | 2 sec |
| Candles | 40 req | 2 sec |
| Trading | 60 req | 2 sec |
| Account | 10 req | 2 sec |

**Rate Limit Error**: `{"code": "50011", "msg": "Rate limit exceeded"}`

```python
from collections import deque
import time

class RateLimiter:
    def __init__(self, max_requests=20, window=2):
        self.max_requests = max_requests
        self.window = window
        self.requests = deque()

    def acquire(self):
        now = time.time()
        while self.requests and self.requests[0] < now - self.window:
            self.requests.popleft()
        if len(self.requests) >= self.max_requests:
            time.sleep(self.window - (now - self.requests[0]))
        self.requests.append(time.time())
```

---

## ⚠️ Common Errors

| Code | Message | Fix |
|------|---------|-----|
| `50113` | Invalid sign | Timestamp = ISO 8601 UTC (not unix ms) |
| `51008` | Insufficient balance | Check `availBal` before order |
| `50011` | Rate limit | Implement rate limiter |
| `51000` | Parameter error | Check `instId` format exactly |

---

## 🎯 Checklist

- [ ] Credentials in `~/.credentials/` (NOT git)
- [ ] Rate limiter implemented
- [ ] Timestamp = ISO 8601 UTC
- [ ] Greeks: PA vs BS units
- [ ] Maker order: `ordType: "post_only"`

---

## 📚 Related

- Greeks: `../greeks_definitions.md`
- Fees: `fee_structure.md`
- Execution: `order_execution.md`

---

**Source**: OKX API v5 (https://www.okx.com/docs-v5/en/)
