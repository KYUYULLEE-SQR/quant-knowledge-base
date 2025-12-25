# OKX Settlement Details

**Last Updated**: 2025-12-22
**Source**: OKX docs, user experience
**Importance**: ⭐⭐ Important - 만기일 처리 정확도

---

## Overview

**Settlement** = 옵션 만기 시 가치 정산 프로세스

**Types**:
- **Cash Settlement**: 현금 정산 (OKX options)
- **Physical Delivery**: 실물 인도 (선물, OKX는 대부분 cash)

---

## Options Settlement

### Settlement Time

**Verified** (2025-12-22):
```
UTC 08:00 (KST 17:00)
매일 / 매주 금요일 / 매달 마지막 금요일
```

📚 **출처**: [Options Specifications](options_specifications.md)

### Settlement Price

**Definition**: 만기 시 underlying 가격 (intrinsic value 계산 기준)

**Calculation Method**:
```
Settlement Price = Index Price @ UTC 08:00

Index Price = Weighted average of multiple exchanges
  (Binance, Coinbase, Kraken, ... weights vary)
```

**⚠️ Important**:
- Settlement price ≠ Last trade price
- Settlement price ≠ Mark price (directly before expiry)
- Settlement price = Index snapshot at 08:00:00.000 UTC

**Example**:
```
2025-01-31 07:59:59 UTC: BTC Mark = $50,500
2025-01-31 08:00:00 UTC: BTC Index = $50,000 ← Settlement Price

All options settle using $50,000 (not $50,500)
```

### Settlement Process

**At UTC 08:00**:

1. **Take index snapshot** → Settlement Price
2. **Calculate intrinsic value** for all options:
   ```python
   # Call
   intrinsic = max(0, settlement_price - strike)

   # Put
   intrinsic = max(0, strike - settlement_price)
   ```
3. **ITM options → Auto-exercise**
4. **OTM options → Expire worthless**
5. **Cash settlement** (no physical BTC delivery)

**Example: Long Call**:
```
Position: Long 10× BTC-USD-250131-50000-C
Entry premium: 0.05 BTC per contract (paid)

Scenario A: Settlement = $52,000 (ITM)
  Intrinsic = max(0, 52000 - 50000) = $2,000 per contract
  Payout = 10 * 2000 = $20,000 = 0.4 BTC @ $50k
  Net PnL = 0.4 - 0.5 = -0.1 BTC (loss, despite ITM!)

Scenario B: Settlement = $55,000 (ITM)
  Intrinsic = max(0, 55000 - 50000) = $5,000 per contract
  Payout = 10 * 5000 = $50,000 = 1 BTC @ $50k
  Net PnL = 1 - 0.5 = +0.5 BTC (profit)

Scenario C: Settlement = $49,000 (OTM)
  Intrinsic = 0
  Payout = 0
  Net PnL = -0.5 BTC (total loss of premium)
```

### Settlement PnL

**Credited to account**:
```
Settlement PnL = Intrinsic Value - Premium Paid (for long)
Settlement PnL = Premium Received - Intrinsic Value (for short)
```

**Timing**:
- Calculated at 08:00 UTC
- Credited within ~1 minute
- Position closed automatically

---

## Futures Settlement

### Perpetual Swaps (No Expiry)

**No settlement** (perpetual)

**Funding Rate** instead:
```
Funding = Position Size * Funding Rate * (8 hours / Funding Interval)

Typical interval: Every 8 hours (00:00, 08:00, 16:00 UTC)
```

### Quarterly/Dated Futures

**Settlement Time**: Same as options (UTC 08:00 on expiry date)

**Settlement Price**: Index Price @ UTC 08:00

**Process**:
```
1. Long position:
   PnL = (Settlement Price - Entry Price) * Contracts

2. Short position:
   PnL = (Entry Price - Settlement Price) * Contracts

3. Position closed, PnL credited/debited
```

---

## Auto-Deleveraging (ADL)

### When ADL Happens

**Trigger**: Liquidation → Insurance fund insufficient

**Victims**: Profitable positions (opposite side)

**Selection Criteria**:
1. **Profit ranking**: Higher profit = higher risk
2. **Leverage ranking**: Higher leverage = higher risk
3. **Combined score**: Profit × Leverage ranking

**Example**:
```
Market crash → Many long positions liquidated
Insurance fund depleted

ADL targets: Profitable SHORT positions
  - User A: -50% PnL, 2× leverage → Low risk
  - User B: +200% PnL, 10× leverage → High risk ← ADL victim
  - User C: +50% PnL, 3× leverage → Medium risk
```

### ADL Process

```
Step 1: OKX selects highest-risk profitable positions
Step 2: Force close at Bankruptcy Price (not market price)
Step 3: User receives notification "ADL triggered"
Step 4: Position closed, no loss (but opportunity cost)
```

**Bankruptcy Price**:
```
= Opposite side's liquidation price
= Fair price for ADL (no one loses money)
```

### ADL Risk Indicator

**OKX UI**: 5-level indicator
```
🟢 Level 1: Low risk (low profit, low leverage)
🟡 Level 3: Medium risk
🔴 Level 5: High risk (high profit, high leverage) ← ADL likely
```

**Mitigation**:
- Reduce leverage
- Take partial profits
- Close position before ADL

---

## Backtest Implications

### 1. Settlement Simulation

```python
def simulate_settlement(positions, settlement_price, settlement_time):
    """
    Simulate option settlement at expiry.

    Args:
        positions: List of option positions expiring today
        settlement_price: Index price @ 08:00 UTC
        settlement_time: datetime @ 08:00 UTC

    Returns:
        settlement_pnl: Total PnL from settlement
        closed_positions: List of closed positions
    """
    settlement_pnl = 0
    closed_positions = []

    for pos in positions:
        if pos.expiry_date != settlement_time.date():
            continue  # Not expiring today

        # Calculate intrinsic value
        if pos.option_type == 'call':
            intrinsic = max(0, settlement_price - pos.strike)
        else:  # put
            intrinsic = max(0, pos.strike - settlement_price)

        # Calculate PnL
        if pos.side == 'long':
            pnl = (intrinsic - pos.entry_premium) * pos.quantity
        else:  # short
            pnl = (pos.entry_premium - intrinsic) * pos.quantity

        settlement_pnl += pnl
        closed_positions.append(pos)

        logger.info(f"SETTLEMENT: {pos.symbol} @ {settlement_price}, "
                   f"Intrinsic={intrinsic}, PnL={pnl}")

    return settlement_pnl, closed_positions
```

### 2. Settlement Price vs Last Trade

**❌ Bad (Common mistake)**:
```python
# Using last trade price as settlement
settlement_price = data['close'].iloc[-1]  # WRONG
```

**✅ Good**:
```python
# Use index price (if available) or mark price at 08:00
settlement_price = data['index_price'].loc['2025-01-31 08:00:00']

# If index not available, use mark price as proxy
settlement_price = data['mark_price'].loc['2025-01-31 08:00:00']
```

**Why matters**:
```
Example: BTC option, strike $50,000

Last trade @ 07:59: $50,500 (mark price)
Index @ 08:00: $50,000 (settlement price)

Option type: Call
Intrinsic (wrong): max(0, 50500 - 50000) = $500 ❌
Intrinsic (correct): max(0, 50000 - 50000) = $0 ✅

This call expires worthless (using settlement), not ITM (using last trade)!
```

### 3. Avoid Holding Through Expiry

**Recommendation**: Close 1 day before expiry

**Reasons**:
1. **Greeks unreliable** <24h (gamma explosion)
2. **Spreads widen** significantly
3. **Settlement price uncertainty** (can differ from mark)
4. **Theta decay accelerates**
5. **Execution risk** (hard to exit at fair price)

**Backtest Implementation**:
```python
# In backtest loop
for timestamp, data in backtest_data.iterrows():
    for position in portfolio.positions:
        days_to_expiry = (position.expiry_date - timestamp.date()).days

        if days_to_expiry <= 1:
            # Close position before expiry
            close_price = data['mark_price'] * 0.98  # Assume 2% spread penalty
            portfolio.close_position(position, close_price, reason='approaching_expiry')
            logger.info(f"PRE-EXPIRY CLOSE: {position.symbol} @ {close_price}")
```

### 4. ADL Simulation (Advanced)

**Rarely needed** (ADL is rare), but for completeness:

```python
def check_adl_risk(position, market_state):
    """
    Estimate ADL risk.

    High profit + high leverage = high ADL risk during extreme moves.
    """
    if position.unrealized_pnl_pct < 0:
        return 0  # No ADL risk (losing position)

    profit_rank = position.unrealized_pnl_pct  # Higher = more risk
    leverage_rank = position.leverage / 10  # Normalize to 0-10 scale

    adl_score = profit_rank * leverage_rank

    if adl_score > 5:
        logger.warning(f"HIGH ADL RISK: {position.symbol}, score={adl_score}")

    return adl_score

# Simplified: Don't simulate actual ADL (too complex)
# Just warn if position has high ADL risk
```

---

## Common Mistakes

1. ❌ **"Settlement = Last traded price"**
   - ✅ Settlement = Index price @ 08:00 UTC
   - ✅ Can differ significantly from mark price

2. ❌ **"ITM option always profitable"**
   - ✅ ITM just means intrinsic > 0
   - ✅ PnL = Intrinsic - Premium paid
   - ✅ Can be ITM but still lose money

3. ❌ **"Hold through expiry to maximize profit"**
   - ✅ Greeks unreliable, spreads wide
   - ✅ Close 1 day before (best practice)

4. ❌ **"ADL won't happen to me"**
   - ✅ Rare but possible (extreme moves)
   - ✅ High profit + high leverage = high risk

5. ❌ **"Backtest doesn't need settlement logic"**
   - ✅ Essential for options strategies
   - ✅ Without settlement: PnL calculation wrong

---

## Agent Protocol: Settlement Handling

**For options strategies:**

1. ✅ Read [Options Specifications](options_specifications.md) - Expiry time
2. ✅ Read this file - Settlement process
3. ✅ In backtest:
   - Detect positions expiring today
   - Use index/mark price @ 08:00 as settlement
   - Calculate intrinsic value correctly
   - Close positions automatically
   - **OR** close 1 day before expiry (recommended)
4. ✅ Log settlement events verbosely
5. ✅ Reconcile: Settled PnL should match position PnL

**Example**:
```
User: "백테스트에서 옵션 만기일 어떻게 처리해?"

Agent:
  [Reads this KB file]

  "옵션 만기일 처리 방법:

   **권장 (Simple)**:
   - 만기 1일 전 모든 포지션 청산
   - Greeks 불안정, spread 넓음 회피
   - 구현 간단: if days_to_expiry <= 1: close()

   **정확 (Complex)**:
   - UTC 08:00에 index price로 settlement 시뮬레이션
   - Intrinsic value 계산: max(0, S-K) for call
   - PnL = intrinsic - premium paid
   - 포지션 자동 청산

   📚 출처: knowledge/exchanges/okx/settlement_details.md

   어떤 방법으로 구현할까요?"
```

---

## References

- **OKX Settlement Guide**: https://www.okx.com/help/options-settlement
- **Index Composition**: https://www.okx.com/help/index-price
- **Related KB**:
  - [Options Specifications](options_specifications.md) - Expiry time, Greeks
  - [Margin & Leverage](margin_and_leverage.md) - ADL triggers
- **Verified**: Settlement time UTC 08:00 (API + user experience)

---

**Version**: 1.0
**Critical**: Settlement price ≠ Last trade. Use index @ 08:00 UTC.
