# Binance Fee Structure

**Last Updated**: 2025-12-24
**Source**: Binance official docs (https://www.binance.com/en/fee/schedule)
**Account Tier**: Assumed VIP 0 (verify your actual tier)

---

## Overview

Binance uses a **tiered fee structure** based on:
1. 30-day trading volume (USDT)
2. BNB holdings (Binance native token)
3. VIP application (for high-volume traders)

**CRITICAL**: Fee tier changes monthly based on rolling 30-day volume.

---

## VIP Tier Structure

### Standard VIP Tiers (Options)

| Tier | 30d Volume (USDT) | BNB Balance | Options Maker | Options Taker | Exercise Fee |
|------|------------------|-------------|---------------|---------------|--------------|
| VIP 0 | < $250K | Any | +0.03% | +0.03% | 0.015% |
| VIP 1 | $250K - $2.5M | ≥ 25 BNB | +0.027% | +0.027% | 0.015% |
| VIP 2 | $2.5M - $7.5M | ≥ 200 BNB | +0.024% | +0.024% | 0.015% |
| VIP 3 | $7.5M - $22.5M | ≥ 600 BNB | +0.022% | +0.022% | 0.015% |
| VIP 4+ | > $22.5M | Custom | Custom | Custom | 0.015% |

**Source**: https://www.binance.com/en/fee/schedule

**Key Points**:
- ⚠️ **No maker rebates** (same as Bybit)
- ⚠️ Maker = Taker fee (same rate)
- ⚠️ **Exercise fee**: 0.015% (additional cost at expiry) ⭐
- ✅ BNB holdings requirement for higher tiers

---

## Exercise Fee (Options-Specific) ⚠️

**CRITICAL**: Binance charges an **exercise fee** on options settlement.

| Event | Fee |
|-------|-----|
| **Trading** (buy/sell) | 0.03% (VIP 0) |
| **Exercise** (settlement) | 0.015% |

**Example**:
```python
# BTC Call, Strike $100,000, Expiry Price $101,000
# Position: Long 100 contracts (1 BTC)

# Trading fees (entry)
premium_paid = 100 * 100  # 10,000 USDT
trading_fee_entry = premium_paid * 0.0003  # 30 USDT

# Settlement (ITM, auto-exercise)
intrinsic_value = 0.01 * (101000 - 100000) * 100  # 1,000 USDT
exercise_fee = intrinsic_value * 0.00015  # 1.5 USDT

# Total fees
total_fees = trading_fee_entry + exercise_fee  # 31.5 USDT

# If also exit (sell before expiry)
trading_fee_exit = premium_received * 0.0003
total_fees_with_exit = trading_fee_entry + trading_fee_exit  # No exercise fee
```

**Implication**: Holding to expiry costs more (exercise fee) vs exiting early (no exercise fee).

---

## Fee Comparison: Binance vs OKX vs Bybit

| Feature | OKX (DMM VIP9) | Bybit (VIP 0) | Binance (VIP 0) |
|---------|---------------|---------------|-----------------|
| **Maker Fee** | -1 bps | +3 bps | +3 bps |
| **Taker Fee** | +3 bps | +3 bps | +3 bps |
| **Exercise Fee** | None | None | +1.5 bps ⚠️ |
| **Total (Roundtrip)** | 0.4 bps (70% maker) | 6 bps | 6 bps + 1.5 bps (if exercise) |
| **30d Volume** | $500M+ | < $100K | < $250K |

**Key Differences**:
- OKX: Maker rebate → lowest cost
- Bybit: No exercise fee → simpler
- Binance: Exercise fee → highest cost for hold-to-expiry strategies

---

## Backtest Implications

### Binance Cost Model

```python
# VIP 0 (most common)
trading_fee_rate = 0.03 / 100  # 3 bps
exercise_fee_rate = 0.015 / 100  # 1.5 bps

# Scenario 1: Buy → Sell (before expiry, no exercise)
cost_no_exercise = 2 * trading_fee_rate  # 6 bps

# Scenario 2: Buy → Hold to expiry (ITM, auto-exercise)
cost_with_exercise = trading_fee_rate + exercise_fee_rate  # 4.5 bps (entry + exercise)

# Scenario 3: Full roundtrip (buy → sell → rebuy → exercise)
cost_full_roundtrip = 2 * trading_fee_rate + exercise_fee_rate  # 7.5 bps
```

### Realistic Cost Assumption

**For strategies holding to expiry**:
```python
# Entry + Exercise
total_cost_bps = 3 + 1.5  # 4.5 bps per trade

# Add slippage (conservative)
slippage_bps = 5  # 5 bps
total_cost = (3 + 1.5 + 5) / 10000  # 9.5 bps = 0.095%
```

**For strategies exiting before expiry**:
```python
# Entry + Exit (no exercise fee)
total_cost_bps = 3 + 3  # 6 bps

# Add slippage
slippage_bps = 5
total_cost = (6 + 5) / 10000  # 11 bps = 0.11%
```

---

## BNB Fee Discount

**Binance offers fee discounts for paying fees in BNB**:

| BNB Discount | Effective Fee (VIP 0) |
|--------------|----------------------|
| No BNB | 3 bps |
| With BNB (25% discount) | 2.25 bps |

**How it works**:
1. Enable "Use BNB to pay fees" in account settings
2. Hold sufficient BNB balance
3. Fees automatically deducted from BNB (at 25% discount)

**Example**:
```python
# Without BNB discount
fee_usdt = 100 * 0.0003  # 0.03 USDT

# With BNB discount (25% off)
fee_usdt_equivalent = 100 * 0.0003 * 0.75  # 0.0225 USDT (paid in BNB)
```

**Note**: Verify current BNB discount rate at https://www.binance.com/en/fee/schedule

---

## Common Mistakes

1. ❌ **"Binance fees = Bybit fees (both 3 bps)"**
   - ✅ Binance has **exercise fee** (1.5 bps), Bybit doesn't
   - ⚠️ This adds significant cost for hold-to-expiry strategies

2. ❌ **"Exercise fee only for manual exercise"**
   - ✅ Exercise fee applies to **auto-exercise** (ITM options at expiry)
   - ✅ No way to avoid if holding to expiry

3. ❌ **"VIP 0 is permanent"**
   - ✅ Tier recalculates monthly (can be downgraded if volume drops)

4. ❌ **"BNB discount always 25%"**
   - ✅ Discount rate changes periodically (verify at official docs)

5. ❌ **"Writing options is allowed for retail"**
   - ✅ **Writing is LP-only** on Binance (retail can only buy)
   - ⚠️ This limits strategy options significantly

---

## Writing Access Restriction ⚠️

**CRITICAL**: Binance Options **writing (selling)** is reserved for **Liquidity Providers (LPs)**.

**Implication**:
- ❌ Cannot backtest short volatility strategies (selling options)
- ❌ Cannot backtest market making strategies
- ✅ Can only backtest long options strategies (buying calls/puts)

**Fee Impact**:
- Lower liquidity → wider spreads
- More slippage expected (5-10 bps conservative)

---

## Agent Protocol: Fee Verification

**BEFORE using Binance fees in backtest:**

1. ✅ Read this file (knowledge/exchanges/binance/fee_structure.md)
2. ✅ Check Binance official docs: https://www.binance.com/en/fee/schedule
3. ✅ **CRITICAL**: Include exercise fee (1.5 bps) if holding to expiry
4. ✅ If user has VIP tier → use that tier's fees
5. ✅ If unknown → assume VIP 0 (conservative)
6. ✅ Add slippage (5-10 bps for options, higher than OKX/Bybit)

**Example**:
```
User: "Binance 옵션 수수료 얼마야?"

Agent:
  [1] Reads this KB file
  [2] Sees: VIP 0, 3 bps trading + 1.5 bps exercise
  [3] Responds:

  "Binance VIP 0 기준:
   - Trading fee: 3 bps (entry/exit)
   - Exercise fee: 1.5 bps (auto-exercise at expiry)

   📚 출처: knowledge/exchanges/binance/fee_structure.md

   ⚠️ 백테스트 시 주의:
   - Hold to expiry: 3 + 1.5 = 4.5 bps (entry + exercise)
   - Exit before expiry: 3 + 3 = 6 bps (entry + exit, no exercise fee)
   - Exercise fee는 피할 수 없음 (ITM auto-exercise)

   💡 Bybit와 비교:
   - Bybit: 3 bps (exercise fee 없음)
   - Binance: 3 + 1.5 = 4.5 bps (hold to expiry 시)
   - Binance가 1.5 bps 더 비쌈"
```

---

## References

- **Official Binance Fees**: https://www.binance.com/en/fee/schedule
- **Options Fees Guide**: https://www.binance.com/en/support/faq/options
- **API Endpoint**: `GET /eapi/v1/account` (account info)
- **Related KB**:
  - knowledge/exchanges/binance/options_specifications.md
  - knowledge/exchanges/bybit/fee_structure.md (comparison)
  - knowledge/exchanges/okx/fee_structure.md (comparison)

---

**Version**: 1.0
**Next Update**: 2025-01-24 (monthly check recommended)
