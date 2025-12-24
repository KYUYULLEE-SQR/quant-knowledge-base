# Bybit Fee Structure

**Last Updated**: 2025-12-24
**Source**: Bybit official docs (https://www.bybit.com/en/help-center/article/Trading-Fee-Structure)
**Account Tier**: Assumed VIP 0 (verify your actual tier)

---

## Overview

Bybit uses a **tiered fee structure** based on:
1. 30-day trading volume (USDT)
2. BIT holdings (Bybit native token, optional)

**CRITICAL**: Fee tier changes monthly based on rolling 30-day volume.

---

## VIP Tier Structure

### Standard VIP Tiers (Options)

| Tier | 30d Volume (USDT) | Options Maker | Options Taker |
|------|------------------|---------------|---------------|
| VIP 0 | < $100K | +0.03% | +0.03% |
| VIP 1 | $100K - $1M | +0.025% | +0.025% |
| VIP 2 | $1M - $5M | +0.02% | +0.02% |
| VIP 3 | $5M - $25M | +0.015% | +0.015% |
| VIP 4 | $25M - $100M | +0.01% | +0.01% |
| VIP 5+ | > $100M | Custom rates | Custom rates |

**Source**: https://www.bybit.com/en/help-center/article/Trading-Fee-Structure

**Key Points**:
- ⚠️ **No maker rebates** (unlike OKX DMM)
- ⚠️ Maker = Taker fee (same rate)
- ✅ Simpler structure (no maker/taker distinction for retail)
- ✅ Lower tiers more accessible than OKX VIP9 (100K vs 500M)

---

## Fee Comparison: Bybit vs OKX

| Feature | OKX (DMM VIP9) | Bybit (VIP 0) | Bybit (VIP 3) |
|---------|---------------|---------------|---------------|
| **Maker Fee** | -1 bps (rebate) | +3 bps | +1.5 bps |
| **Taker Fee** | +3 bps | +3 bps | +1.5 bps |
| **30d Volume** | $500M+ | < $100K | $5M - $25M |
| **Maker Rebate** | ✅ Yes | ❌ No | ❌ No |

**Key Difference**:
- OKX: Maker rebate → incentivizes passive liquidity provision
- Bybit: No rebate → simpler, but higher cost for makers

---

## Backtest Implications

### Bybit Cost Model

```python
# VIP 0 (most common for retail)
fee_rate = 0.03 / 100  # 3 bps (both maker/taker)

# VIP 3 (achievable for active traders)
fee_rate = 0.015 / 100  # 1.5 bps

# No need to distinguish maker/taker
# Both have same fee
```

### Realistic vs Conservative

**Realistic** (VIP 0):
```python
fee_rate = 0.0003  # 3 bps
# Apply to both entry and exit
total_roundtrip_fee = 2 * fee_rate  # 6 bps
```

**Conservative** (account for slippage):
```python
fee_rate = 0.0003  # 3 bps
slippage = 0.0005  # 5 bps (conservative for options)
total_cost = fee_rate + slippage  # 8 bps per trade
total_roundtrip = 2 * total_cost  # 16 bps
```

### Comparison with OKX

**Bybit VIP 0 vs OKX DMM**:
```python
# OKX (70% maker, 30% taker)
okx_avg_fee = 0.7 * (-0.0001) + 0.3 * (0.0003)  # 0.2 bps

# Bybit VIP 0
bybit_fee = 0.0003  # 3 bps

# Difference: 2.8 bps per trade
# Over 100 trades: 280 bps = 2.8% performance difference
```

**Implication**: OKX DMM has significant fee advantage for high-frequency strategies.

---

## How to Check Your Tier

### Web/App
1. Go to Account → API Management → Trading Fees
2. Shows current tier + requirements for next tier

### API
```python
# GET /v5/account/fee-rate?category=option
import requests

response = requests.get(
    'https://api.bybit.com/v5/account/fee-rate',
    headers={'X-BAPI-API-KEY': API_KEY, ...},
    params={'category': 'option'}
)

# Response:
# {
#   "retCode": 0,
#   "result": {
#     "list": [{
#       "symbol": "BTC-28MAR25-100000-C",
#       "takerFeeRate": "0.0003",  # 3 bps
#       "makerFeeRate": "0.0003"   # 3 bps (same)
#     }]
#   }
# }
```

---

## Fee Discounts (BIT Token)

**Bybit offers fee discounts for holding BIT tokens**:

| BIT Balance | Fee Discount |
|-------------|--------------|
| 0 - 999 | 0% |
| 1,000 - 9,999 | 5% |
| 10,000 - 49,999 | 10% |
| 50,000+ | 15% |

**Example** (VIP 0 + 10,000 BIT):
- Base fee: 3 bps
- Discount: 10%
- Effective fee: 3 * 0.9 = 2.7 bps

**Note**: Verify current BIT discount structure at https://www.bybit.com/en/help-center

---

## Common Mistakes

1. ❌ **"Bybit has maker rebates like OKX"**
   - ✅ Bybit has NO maker rebates (both maker/taker pay same fee)

2. ❌ **"VIP 0 = lowest fees"**
   - ✅ VIP 0 = highest fees (3 bps), VIP levels reduce fees

3. ❌ **"Don't need to check tier monthly"**
   - ✅ Tier recalculates monthly based on 30-day volume (can be downgraded)

4. ❌ **"Maker/taker distinction doesn't matter"**
   - ✅ For fee calculation: correct (same rate)
   - ✅ For fill probability: still matters (maker waits, taker fills immediately)

---

## Agent Protocol: Fee Verification

**BEFORE using Bybit fees in backtest:**

1. ✅ Read this file (knowledge/exchanges/bybit/fee_structure.md)
2. ✅ Check Bybit official docs: https://www.bybit.com/en/help-center/article/Trading-Fee-Structure
3. ✅ If user has VIP tier → use that tier's fees
4. ✅ If unknown → assume VIP 0 (conservative)
5. ✅ Include slippage (5-10 bps for options)

---

## References

- **Official Bybit Fees**: https://www.bybit.com/en/help-center/article/Trading-Fee-Structure
- **API Endpoint**: `GET /v5/account/fee-rate?category=option`
- **Related KB**: knowledge/exchanges/bybit/options_specifications.md
- **Comparison**: knowledge/exchanges/okx/fee_structure.md

---

**Version**: 1.0
**Next Update**: 2025-01-24 (monthly check recommended)
