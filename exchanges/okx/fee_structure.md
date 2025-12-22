# OKX Fee Structure

**Last Updated**: 2025-12-22
**Source**: User account info, OKX official docs (https://www.okx.com/fees)
**Account Tier**: DMM (Designated Market Maker) = VIP9 equivalent

---

## Overview

OKX uses a **tiered fee structure** based on:
1. 30-day trading volume (USD)
2. OKB holdings (OKX native token)
3. Special designations (DMM, Affiliate, etc.)

**CRITICAL**: Fee tier changes monthly based on rolling 30-day volume.

---

## User's Current Tier: DMM (VIP9)

### What is DMM?
**Designated Market Maker** = Special tier granted by OKX for providing liquidity.

**Benefits**:
- Equivalent to VIP9 fee rates
- Lower maker fees (rebates)
- Potentially higher API rate limits
- Priority support

**Requirements** (typical):
- Application required
- Minimum liquidity provision commitments
- Monthly volume requirements
- Uptime/availability SLAs

### Fee Rates (DMM/VIP9)

| Instrument | Maker | Taker | Notes |
|-----------|-------|-------|-------|
| **Futures** | **-0.5 bps** | +5.0 bps | Maker rebate |
| **Options** | **-1.0 bps** | +3.0 bps | Maker rebate |
| **Perpetual** | -0.5 bps | +5.0 bps | Same as futures |
| **Spot** | +2.0 bps | +5.0 bps | (if applicable) |

**Key Points**:
- ✅ Negative maker fee = **rebate** (you get paid for providing liquidity)
- ✅ Options have better maker rebate than futures (-1 bps vs -0.5 bps)
- ⚠️ Only applicable if order filled as **maker** (passive fill)
- ⚠️ Taker fees are positive (you pay)

---

## VIP Tier Comparison (for reference)

**Note**: User should verify current tier and rates at https://www.okx.com/fees

### Standard VIP Tiers

| Tier | 30d Volume (USD) | Futures Maker | Futures Taker | Options Maker | Options Taker |
|------|-----------------|---------------|---------------|---------------|---------------|
| VIP0 | < $50K | +2 bps | +5 bps | +3 bps | +8 bps |
| VIP1 | $50K - $500K | +1.5 bps | +4.5 bps | +2.5 bps | +7.5 bps |
| VIP2 | $500K - $2M | +1 bps | +4 bps | +2 bps | +7 bps |
| VIP3 | $2M - $10M | +0.5 bps | +3.5 bps | +1.5 bps | +6.5 bps |
| ... | ... | ... | ... | ... | ... |
| **VIP9** | **> $500M** | **-0.5 bps** | **+5 bps** | **-1 bps** | **+3 bps** |
| VIP10 | > $1B | -1 bps | +4.5 bps | -1.5 bps | +2.5 bps |
| VIP11 | > $5B | -1.5 bps | +4 bps | -2 bps | +2 bps |

**Source**: https://www.okx.com/fees (verify periodically, rates may change)

### How to Check Your Current Tier

1. **OKX Web/App**:
   - Account → Fee Tier
   - Shows current tier + next tier requirements

2. **API**:
   ```python
   # GET /api/v5/account/account-fee-tier
   import requests

   response = requests.get(
       'https://www.okx.com/api/v5/account/account-fee-tier',
       headers={'OK-ACCESS-KEY': API_KEY, ...}
   )

   # Response:
   # {
   #   "level": "9",
   #   "taker": "0.0005",  # 5 bps
   #   "maker": "-0.00005", # -0.5 bps (futures)
   #   ...
   # }
   ```

3. **Monthly Check**:
   ⚠️ Set reminder to check fee tier on 1st of each month (tier updates based on past 30 days)

---

## Maker vs Taker: How It's Determined

### Maker (Passive Fill)
**Order sits on the order book and gets filled by someone else's market order.**

```python
# Example: Maker order
Current bid: $50,000, ask: $50,010

# You place limit order INSIDE spread or AT best bid/ask
order = place_limit_order(
    side='buy',
    price=50000,  # At current best bid (or better)
    size=10
)

# Order goes on book → someone takes it → you are MAKER
# Fee: -0.5 bps (futures) or -1 bps (options) = rebate
```

**Conditions**:
- ✅ Limit order
- ✅ Posted price does NOT cross spread
- ✅ Filled passively (someone else's market/aggressive limit order)

### Taker (Aggressive Fill)
**Order immediately matches existing orders on the book.**

```python
# Example: Taker order
Current bid: $50,000, ask: $50,010

# You place market order OR limit order that crosses spread
order = place_limit_order(
    side='buy',
    price=50010,  # Crosses spread (takes liquidity)
    size=10
)

# Order immediately filled against existing ask → you are TAKER
# Fee: +5 bps (futures) or +3 bps (options) = you pay
```

**Conditions**:
- Market order (always taker)
- Limit order that crosses spread
- Immediate fill (takes existing liquidity)

### Post-Only Orders (Ensure Maker)
```python
# OKX API: Use "post_only" flag to guarantee maker or cancel
order = place_limit_order(
    side='buy',
    price=50000,
    size=10,
    post_only=True  # If would be taker, cancel instead
)

# If order would cross spread → rejected/cancelled
# Guarantees: only maker fills, never taker fees
```

---

## Backtest Implications

### Optimistic (Unrealistic)
```python
# Assume 100% maker fills
fee_rate = -0.01 / 100  # -1 bps (options)

# Every trade EARNS 1 bps
# Sharpe will be inflated
```

### Realistic (Conservative)
```python
# Assume 70% maker, 30% taker
MAKER_RATIO = 0.7

fee_maker = -0.01 / 100  # -1 bps
fee_taker = 0.03 / 100   # +3 bps

fee_avg = MAKER_RATIO * fee_maker + (1 - MAKER_RATIO) * fee_taker
# = 0.7 * (-0.0001) + 0.3 * (0.0003)
# = -0.00007 + 0.00009
# = 0.00002 = 0.2 bps

# Small positive fee (more realistic)
```

### Validation (Post-Live)
```python
# After live trading, calculate actual maker ratio
total_trades = 1000
maker_trades = 720
actual_maker_ratio = maker_trades / total_trades  # 0.72

# If backtest assumed 0.7, close enough ✅
# If backtest assumed 1.0, need to adjust ❌
```

---

## Fee Changes & Updates

### How to Stay Updated

1. **OKX Announcements**:
   - Check https://www.okx.com/support/announcements regularly
   - Fee structure changes announced 30 days in advance (usually)

2. **API Monitoring**:
   ```python
   # Periodically check fee tier
   # Alert if tier changes unexpectedly
   current_tier = get_account_fee_tier()

   if current_tier != expected_tier:
       send_alert(f"Fee tier changed: {expected_tier} → {current_tier}")
   ```

3. **Volume Monitoring**:
   ```python
   # Track 30-day rolling volume to predict tier changes
   volume_30d = get_30day_volume()

   # VIP9 requires > $500M/month
   if volume_30d < 500_000_000:
       send_warning("Volume below VIP9 threshold, tier may downgrade next month")
   ```

---

## Common Mistakes (Agents)

1. ❌ **"Fee is always -1 bps"**
   - ✅ Only for OPTIONS, MAKER fills
   - ✅ Futures: -0.5 bps
   - ✅ Taker: +3 bps (options), +5 bps (futures)

2. ❌ **"DMM = VIP10"**
   - ✅ DMM = VIP9 equivalent (check official docs for confirmation)

3. ❌ **"VIP tier is permanent"**
   - ✅ Tier recalculated MONTHLY based on trailing 30-day volume
   - ✅ Can be downgraded if volume drops

4. ❌ **"Maker rebate = free money"**
   - ✅ Only if order filled as maker (passive)
   - ✅ If strategy needs aggressive fills → taker fees apply

5. ❌ **"Don't need to check API docs"**
   - ✅ **ALWAYS verify** at https://www.okx.com/fees
   - ✅ Fee structure changes occasionally
   - ✅ This KB is summary, not authoritative source

---

## Agent Protocol: Fee Verification

**BEFORE using fee rates in backtest:**

1. ✅ Read this file (knowledge/exchanges/okx/fee_structure.md)
2. ✅ Check OKX official docs: https://www.okx.com/fees
3. ✅ If discrepancy found → Update this KB + notify user
4. ✅ Use conservative assumption (70% maker, not 100%)
5. ✅ Test sensitivity (0.5×, 1×, 2× fees)

**Example**:
```
User: "OKX 수수료 얼마야?"

Agent:
  [1] Reads this KB file
  [2] Sees: DMM/VIP9, Options maker -1 bps, taker +3 bps
  [3] Checks OKX docs (WebFetch if needed)
  [4] Responds: "OKX DMM (VIP9) 기준, 옵션 maker -1 bps, taker +3 bps.
                 출처: knowledge/exchanges/okx/fee_structure.md

                 ⚠️ 백테스트 시 maker 100% 가정하지 말 것 (비현실적).
                 권장: 70% maker, 30% taker 가정 → 평균 0.2 bps"
```

---

## References

- **Official OKX Fees**: https://www.okx.com/fees
- **API Endpoint**: `GET /api/v5/account/account-fee-tier`
- **Related KB**: [Transaction Cost Model](../../modeling/transaction_cost_model.md)
- **User conversation**: 2025-12-22 (fee specification)

---

**Version**: 1.0
**Next Update**: 2025-01-22 (monthly check)
