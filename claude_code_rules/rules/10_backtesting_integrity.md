# 🔬 Backtesting Integrity (백테스트 정합성)

## 📌 CORE PRINCIPLES (10-line summary)

**"감으로 대충" 백테스트 절대 금지. Trade-by-trade reconciliation 필수.**

**MANDATORY FILES (every backtest):**
1. `results/trades.csv` - every trade with before/after state
2. `results/positions.csv` - position at every timestep
3. `results/pnl_attribution.csv` - PnL breakdown (realized/unrealized/fees)
4. `results/reconciliation.csv` - validation test results

**REQUIRED VALIDATION TESTS (5개):**
1. ✅ Position continuity: position changes = trades exactly
2. ✅ Cash conservation: cash flow = trade amounts + fees
3. ✅ PnL attribution: total PnL = components sum
4. ✅ No orphan trades: every close has open
5. ✅ Margin compliance: no violations

**NEVER:**
- ❌ Report results without reconciliation
- ❌ If reconciliation fails → must fix, don't report
- ❌ Look-ahead bias (t+1 data in t decision)

---

## 🎯 Purpose

**"감으로 대충" 백테스트 절대 금지.**

모든 백테스트는 **trade-by-trade reconciliation**으로 검증되어야 함.
회계 장부처럼 매 거래, 매 시점의 포지션/PnL/캐시가 정확히 맞아떨어져야 함.

---

## ⚠️ 문제: 대충 하는 백테스트

### 흔한 실수들:

1. **Position tracking 없음**
   - 거래만 기록하고 포지션 상태 추적 안 함
   - 청산 시점에 포지션이 실제로 있는지 확인 안 함

2. **PnL 계산 대충**
   - Realized vs Unrealized 구분 안 함
   - Mark-to-market 시점 불명확
   - Fee/slippage 일부만 적용하거나 누락

3. **Cash flow 추적 없음**
   - 현금 잔고 계산 안 함
   - 마진/담보 요구사항 무시
   - 레버리지 계산 틀림

4. **Greeks 추적 부실 (옵션)**
   - Delta/Gamma/Theta/Vega 시점별 추적 안 함
   - 옵션 만기 처리 누락
   - Early assignment 무시

5. **검증 없음**
   - 백테스트 끝나고 "이익 나왔네" 하고 끝
   - Trade count, position 변화, PnL attribution 체크 안 함

---

## ✅ 정합성 체크리스트 (MANDATORY)

### 1. Trade-by-Trade Accounting

**MUST track every single trade:**

```csv
# trades.csv (required columns)
timestamp, trade_id, symbol, side, quantity, price, fee, slippage, 
pnl_realized, position_before, position_after, cash_before, cash_after,
reason, signal_value
```

**Required validations:**
- ✅ Every trade ID unique
- ✅ Position_after = position_before ± quantity (with correct sign)
- ✅ Cash_after = cash_before - (price * quantity) - fee - slippage
- ✅ No orphan closes (closing non-existent position)
- ✅ No over-closes (closing more than held)

### 2. Position Reconciliation (Every Timestep)

**MUST maintain position ledger:**

```csv
# positions.csv (required columns)
timestamp, symbol, quantity, avg_entry_price, current_price, 
unrealized_pnl, margin_required, days_held
```

**Required validations:**
- ✅ Sum of all position changes = current position
- ✅ Position never goes negative (unless short allowed)
- ✅ Mark-to-market at every timestep
- ✅ Unrealized PnL = (current_price - avg_entry_price) * quantity

### 3. Cash & PnL Attribution

**MUST track cash and PnL components:**

```csv
# pnl_attribution.csv (required columns)
timestamp, realized_pnl, unrealized_pnl, fees_paid, slippage_cost,
funding_pnl, theta_decay, cash_balance, equity, leverage
```

**Required validations:**
- ✅ Equity = cash + unrealized_pnl
- ✅ Total PnL = realized + unrealized = sum(all trades pnl) + sum(position mtm)
- ✅ Cash flow reconciles: cash_t = cash_{t-1} + realized_pnl_t - fees_t
- ✅ Leverage = (sum(abs(position_value))) / equity

### 4. Strategy-Specific Reconciliation

#### For Options:
```csv
# options_positions.csv
timestamp, symbol, position, delta, gamma, theta, vega, rho,
mark_price, intrinsic_value, time_value, days_to_expiry
```

**Required validations:**
- ✅ Greeks recalculated every timestep
- ✅ Expiry handling: ITM → auto-exercise, OTM → expire worthless
- ✅ Early assignment probability considered (American options)
- ✅ Theta decay tracked daily
- ✅ Implied volatility changes tracked

#### For Market Making:
```csv
# mm_positions.csv
timestamp, symbol, inventory, mark_price, bid, ask, spread,
quote_qty, filled_bid, filled_ask, inventory_pnl, spread_pnl
```

**Required validations:**
- ✅ Inventory = cumsum(fills)
- ✅ PnL = spread_capture + inventory_mtm
- ✅ Quote updates tracked
- ✅ Adverse selection quantified

#### For Long-Short Portfolio:
```csv
# portfolio_positions.csv
timestamp, symbol, position, weight, sector, factor_exposure,
long_pnl, short_pnl, hedge_ratio, net_exposure
```

**Required validations:**
- ✅ Sum of weights = 100% (or target leverage)
- ✅ Long/short balance maintained (if dollar-neutral)
- ✅ Sector exposure within limits
- ✅ Factor exposures tracked

### 5. Margin & Risk Reconciliation

**MUST track margin requirements:**

```csv
# margin.csv
timestamp, initial_margin, maintenance_margin, margin_used, 
margin_available, margin_call_risk, liquidation_price
```

**Required validations:**
- ✅ Margin call detection: margin_used > maintenance_margin
- ✅ Liquidation price calculated correctly
- ✅ No trading when insufficient margin
- ✅ Overnight margin requirements (if applicable)

---

## 🔍 Reconciliation Tests (Run After Backtest)

### Test 1: Position Continuity
```python
def test_position_continuity(trades_df, positions_df):
    """Every position change must have corresponding trade."""
    for t in positions_df.index:
        pos_change = positions_df.loc[t, 'quantity'] - positions_df.shift(1).loc[t, 'quantity']
        trades_sum = trades_df[trades_df.timestamp == t]['quantity'].sum()
        assert abs(pos_change - trades_sum) < 1e-6, f"Position mismatch at {t}"
```

### Test 2: Cash Conservation
```python
def test_cash_conservation(trades_df, pnl_df):
    """Cash flow must reconcile with trades."""
    cash_from_trades = -trades_df['price'] * trades_df['quantity'] - trades_df['fee']
    cash_from_pnl = pnl_df['realized_pnl'] - pnl_df['fees_paid']
    assert abs(cash_from_trades.sum() - cash_from_pnl.sum()) < 1e-3
```

### Test 3: PnL Attribution
```python
def test_pnl_attribution(trades_df, pnl_df):
    """Total PnL must equal sum of components."""
    total_pnl_calc = pnl_df['realized_pnl'].iloc[-1] + pnl_df['unrealized_pnl'].iloc[-1]
    total_pnl_direct = (pnl_df['cash_balance'].iloc[-1] + pnl_df['unrealized_pnl'].iloc[-1]) - INITIAL_CAPITAL
    assert abs(total_pnl_calc - total_pnl_direct) < 1e-2
```

### Test 4: No Orphan Trades
```python
def test_no_orphan_closes(trades_df):
    """No closing trades without prior open."""
    positions = {}
    for _, trade in trades_df.iterrows():
        symbol = trade['symbol']
        if trade['side'] == 'close':
            assert symbol in positions and positions[symbol] > 0, f"Orphan close: {symbol} at {trade['timestamp']}"
            positions[symbol] -= trade['quantity']
        else:
            positions[symbol] = positions.get(symbol, 0) + trade['quantity']
```

### Test 5: Leverage Compliance
```python
def test_leverage_limits(pnl_df, max_leverage=3.0):
    """Leverage must stay within limits."""
    assert (pnl_df['leverage'] <= max_leverage).all(), f"Leverage exceeded {max_leverage}x"
```

---

## 📊 Reconciliation Report (Required in README)

Every experiment README MUST include:

```markdown
## Reconciliation Status

- ✅ Position continuity: All trades reconciled
- ✅ Cash conservation: Cash flow matches trades
- ✅ PnL attribution: Components sum correctly
- ✅ No orphan trades: All closes have opens
- ✅ Margin compliance: No violations
- ✅ Greeks tracking: (Options only) All Greeks tracked
- ✅ Trade count: [Expected vs Actual]
- ✅ Final position: [Should be flat/hedge remaining]

**Discrepancies**: None / [List any unresolved issues]
```

---

## 🚨 Agent Rules (Backtesting Integrity)

### MANDATORY Behaviors:

1. **ALWAYS generate reconciliation files:**
   - `results/trades.csv` (every single trade)
   - `results/positions.csv` (position at every timestep)
   - `results/pnl_attribution.csv` (PnL breakdown)
   - `results/reconciliation.csv` (validation checks)

2. **ALWAYS run reconciliation tests:**
   - After every backtest
   - Before reporting results
   - Include test results in logs

3. **NEVER report results without reconciliation:**
   - If reconciliation fails → FIX IT, don't report
   - If trades don't reconcile → BUG, not "good results"

4. **Log verbosely:**
   - Every trade with before/after state
   - Every position change with reason
   - Every PnL attribution with breakdown

5. **Sanity checks:**
   - Final position should be flat (unless hedge remaining)
   - Total PnL should match equity change
   - Trade count should match signal count (roughly)
   - No huge unexplained PnL jumps

### RED FLAGS (Stop and Debug):

- ❌ Position goes negative when shouldn't
- ❌ Cash goes negative without margin
- ❌ PnL components don't sum to total
- ❌ Trade without corresponding signal
- ❌ Greeks not tracked (options)
- ❌ Fees/slippage missing
- ❌ Leverage exceeds limits without detection

---

## 📈 Example: Good Reconciliation Output

```
=== BACKTEST RECONCILIATION ===

Period: 2024-10-01 to 2024-10-07
Strategy: Fair IV Short Put

POSITION TRACKING:
  Total trades: 287
  Open trades: 145
  Close trades: 142
  Final position: 3 contracts (expected: hedge remaining)
  ✅ Position continuity: PASS

CASH FLOW:
  Initial capital: $100,000
  Final cash: $98,234
  Total fees paid: $1,245
  Total slippage: $521
  ✅ Cash conservation: PASS (diff: $0.03)

PNL ATTRIBUTION:
  Realized PnL: $2,456
  Unrealized PnL: $1,234
  Theta decay: $3,890
  Delta PnL: -$200
  Total PnL: $3,690
  Equity: $103,690
  ✅ PnL attribution: PASS (diff: $0.02)

MARGIN:
  Max margin used: $45,678 (45.7%)
  Max leverage: 2.3x (limit: 3.0x)
  Margin calls: 0
  ✅ Margin compliance: PASS

GREEKS (Options):
  Delta tracking: 287 updates
  Gamma tracking: 287 updates
  Theta tracked: $3,890 total decay
  Expiry handling: 12 contracts expired (all correct)
  ✅ Greeks reconciliation: PASS

VALIDATION TESTS:
  ✅ test_position_continuity: PASS
  ✅ test_cash_conservation: PASS (err: 0.0003%)
  ✅ test_pnl_attribution: PASS (err: 0.0002%)
  ✅ test_no_orphan_closes: PASS
  ✅ test_leverage_limits: PASS

=== ALL RECONCILIATION CHECKS PASSED ===

Files saved:
  - results/trades.csv (287 rows)
  - results/positions.csv (168 hours × 45 symbols = 7,560 rows)
  - results/pnl_attribution.csv (168 rows)
  - results/reconciliation.csv (5 tests × details)
```

---

**Last Updated**: 2025-12-18  
**Version**: 1.0

