# Inverse Options (Crypto Options)

**What**: 계약 크기는 USD로 표시되지만, 마진/세틀먼트는 BTC/ETH 등 코인으로 처리되는 옵션
**Why Important**: PnL 계산, Greeks, 헤징 전략이 전통 옵션과 근본적으로 다름
**Where**: Deribit (전통적으로 inverse only), OKX (crypto-settled)

**Last Updated**: 2025-12-23

---

## 🎯 Quick Summary (30초)

| Aspect | Standard Options | Inverse Options |
|--------|------------------|-----------------|
| **Contract Size** | USD 표시 | USD 표시 |
| **Margin** | USD/Stablecoin | BTC/ETH (코인) |
| **Settlement** | USD/Stablecoin | BTC/ETH (코인) |
| **PnL Currency** | USD | BTC/ETH |
| **Delta Range** | [0, 1] for calls | **NOT bounded by 1** ⚠️ |
| **Delta Behavior** | Monotonic increasing | **Non-monotonic** (peak at S > K) ⚠️ |
| **Convexity** | Positive (convex) | **Switches**: convex → concave ⚠️ |
| **Use Case** | USD-based traders | BTC holders, miners, treasury |

---

## 📚 What is an Inverse Option?

### Definition

**Inverse Option** = Option where:
1. **Contract size denominated in USD** (e.g., 1 BTC option = $50,000 notional)
2. **Margined in cryptocurrency** (BTC/ETH, not USD)
3. **Settled in cryptocurrency** (BTC/ETH, not USD)

**Why "Inverse"?**
Because it's the **opposite** of standard options:
- Standard: USD contract → USD margin → USD settlement
- Inverse: USD contract → **Crypto margin** → **Crypto settlement**

### Why Do Inverse Options Exist?

**Deribit**:
- Does NOT accept fiat currency
- Only lists inverse products
- Forces traders to keep funds in BTC/ETH
- **>90% of crypto options market** trades on Deribit

**OKX**:
- Offers crypto-settled options (effectively inverse)
- Underlying = BTC/USD index
- Settlement in BTC/ETH

**User Benefits**:
- ✅ No fiat transfer needed (avoid KYC/bank friction)
- ✅ Stay in crypto (for HODLers, miners, treasuries)
- ✅ Natural hedge for BTC exposure
- ✅ Capital efficiency (margin in same asset)

---

## 💰 PnL Calculation (핵심 차이)

### Standard Call Option (USD-settled)

**Payoff at expiry**:
```
Payoff (USD) = max(S - K, 0)
```

**Example**:
- Buy BTC call, K = $50,000
- At expiry: S = $60,000
- Payoff = $60,000 - $50,000 = **$10,000 USD**

---

### Inverse Call Option (BTC-settled)

**Payoff at expiry**:
```
Payoff (USD) = max(S - K, 0)
Payoff (BTC) = max(S - K, 0) / S
```

**Example**:
- Buy BTC inverse call, K = $50,000
- At expiry: S = $60,000
- Payoff (USD) = $60,000 - $50,000 = $10,000
- Payoff (BTC) = $10,000 / $60,000 = **0.1667 BTC**

**Key Insight**:
- USD payoff 같음 ($10,000)
- 하지만 **BTC로 세틀**되므로 BTC 단위 payoff는 S에 반비례
- S ↑ → Payoff (BTC) ↓ (같은 USD 가치)

---

### PnL During Life (Mark-to-Market)

**Standard Option**:
```python
pnl_usd = (price_now - price_entry) * quantity
```

**Inverse Option**:
```python
pnl_usd = (price_now - price_entry) * quantity
pnl_btc = pnl_usd / S_now   # ⚠️ BTC로 환산 시 S_now로 나눔
```

**Backtest 주의**:
- PnL을 USD로 계산했다면, **포트폴리오 NAV는 BTC 기준**이어야 함
- BTC 가격 변동이 NAV에 영향 (S ↑ → NAV (BTC) ↓ even if PnL same)
- USD PnL만 보면 **실제 BTC 수익률과 다를 수 있음**

---

## 📊 Greeks Differences (매우 중요!)

### Delta (Δ)

**Standard Call Delta**:
- Range: [0, 1]
- Monotonically increasing in S
- S → ∞: Δ → 1

**Inverse Call Delta**:
- **NOT bounded by 1** ⚠️
- **Non-monotonic**: reaches maximum when S just exceeds K, then **declines**
- Inflection point: where pricing function shifts from convex → concave

**Formula (simplified)**:
```
Standard Delta:  Δ_std = N(d1)
Inverse Delta:   Δ_inv = [N(d1) - C/S] / (1 + C/S)

where C = option price (USD)
```

**Visual Behavior**:
```
Standard Delta (Call):
  Δ
  1 |                    ........
    |              ......
  0.5|        ......
    |   .....
  0 |___________________________
      K                        S

Inverse Delta (Call):
  Δ
    |         /\
    |        /  \
    |       /    \___
    |      /         \___
  0 |_____________________\____
      K    S*             S

S* = point where Δ peaks (typically S slightly > K)
```

**Backtest Impact**:
- Delta hedging with **standard formula** will FAIL for inverse options
- Need to use **inverse-specific Greeks** (from exchange API or custom model)
- **NEVER use Black-Scholes delta directly**

---

### Gamma (Γ)

**Standard Gamma**:
- Always positive
- Peaks at ATM (S ≈ K)

**Inverse Gamma**:
- **Can be negative** for deep ITM options ⚠️
- Different shape (not symmetric around K)

**Backtest Impact**:
- Gamma scalping strategies need adjustment
- Sign of gamma may flip (convex → concave transition)

---

### Vega (ν)

**Standard Vega**:
- Always positive (long option = long vol)

**Inverse Vega**:
- **Can differ** due to settlement currency
- Volatility of S affects BTC payoff differently

---

### Theta (Θ)

**Standard Theta**:
- Always negative for long options (time decay)

**Inverse Theta**:
- **Generally negative**, but magnitude differs
- Theta decay in BTC terms ≠ Theta in USD terms

**Backtest Impact**:
- Daily theta decay calculation must use **inverse formula**
- **Don't assume linear time decay**

---

## 🔬 Mathematical Details (Advanced)

### Boundary Conditions

**Standard Call**:
```
C(0, t) = 0
C(S, t) → S as S → ∞
```

**Inverse Call**:
```
C_inv(0, t) = 0
C_inv(S, t) → 1 as S → ∞   # ⚠️ Converges to 1 BTC, not S
```

### Convexity Transition

**Standard Call**: Always convex (∂²C/∂S² > 0)

**Inverse Call**:
- Convex when S < S_critical
- **Concave when S > S_critical** ⚠️
- S_critical depends on K, σ, T

**Implication**:
- Deep ITM inverse calls behave like **linear instruments** (not options)
- Hedging ratios non-intuitive

---

## 🧪 Backtesting Implications (CRITICAL)

### 1. Greeks Source ⚠️⚠️⚠️

**WRONG**:
```python
# ❌ DON'T DO THIS
delta = black_scholes_delta(S, K, r, σ, T)  # Standard formula
```

**RIGHT**:
```python
# ✅ DO THIS
delta = exchange_api.get_greeks(symbol)['delta']  # Deribit/OKX Greeks
# or
delta = inverse_option_delta(S, K, r, σ, T)  # Custom inverse formula
```

**Why**:
- Deribit/OKX already compute **inverse Greeks** in their APIs
- Using standard BS Greeks will give **wrong delta** (off by 10-50% for ITM)

---

### 2. PnL Attribution

**WRONG**:
```python
# ❌ USD-only tracking
pnl_usd = (mark_price - entry_price) * contracts
portfolio_value_usd += pnl_usd
```

**RIGHT**:
```python
# ✅ BTC-based tracking
pnl_usd = (mark_price - entry_price) * contracts
pnl_btc = pnl_usd / btc_price_now

portfolio_btc += pnl_btc
portfolio_value_usd = portfolio_btc * btc_price_now  # NAV in USD
```

**Why**:
- Your actual wallet balance is in **BTC**, not USD
- BTC price volatility affects NAV even if option PnL unchanged

---

### 3. Delta Hedging

**WRONG**:
```python
# ❌ Standard hedge
hedge_qty = -delta_std * option_qty
```

**RIGHT**:
```python
# ✅ Inverse hedge (use exchange delta)
delta_inv = get_inverse_delta(S, K, σ, T)  # or from API
hedge_qty = -delta_inv * option_qty

# ⚠️ Hedge in BTC perpetual, not USD futures
```

**Why**:
- Inverse delta ≠ standard delta
- Hedge instrument must also be **BTC-margined** (e.g., BTC perpetual)
- USD futures won't hedge properly (currency mismatch)

---

### 4. Settlement Handling

**At Expiry**:
```python
# Standard option
if S > K:
    cash_received_usd = (S - K) * contracts

# Inverse option
if S > K:
    cash_received_btc = (S - K) / S * contracts
    cash_received_usd = cash_received_btc * S  # same USD value
```

**Backtest Must Track**:
- BTC balance changes (not just USD P&L)
- Final portfolio value in BTC, then convert to USD for reporting

---

### 5. Margin Requirements

**Deribit Inverse Options**:
- Margin calculated in **BTC**
- Formula uses inverse option value
- Different from standard options margin

**OKX**:
- Similar: margin in BTC/ETH
- Portfolio margin considers all BTC-denominated positions

**Backtest Must**:
- Calculate margin in BTC (not USD)
- Check margin calls based on **BTC balance**, not USD

---

### 6. Theta Decay Tracking

**Standard Theta**:
```python
daily_theta_decay_usd = theta * contracts
pnl_theta_usd -= daily_theta_decay_usd
```

**Inverse Theta**:
```python
# ⚠️ Theta from exchange is in BTC terms
daily_theta_decay_btc = theta_inv * contracts  # in BTC
daily_theta_decay_usd = daily_theta_decay_btc * btc_price

pnl_theta_btc -= daily_theta_decay_btc
pnl_theta_usd -= daily_theta_decay_usd
```

---

## 🏦 Exchange-Specific Details

### Deribit

**Products**:
- **Inverse Options** (traditional, BTC/ETH settled)
- **USDC Options** (launched Aug 2025, linear settled)

**Inverse Option Specs**:
- Settlement: BTC Index (30-min TWAP before expiry, UTC 08:00)
- Contract Size: 1 BTC (USD-denominated)
- Margin Currency: BTC
- Settlement Formula: `(max(S - K, 0)) / S` for calls

**API Greeks**:
- Deribit provides **inverse Greeks** via API
- Fields: `delta`, `gamma`, `vega`, `theta`, `rho`
- Already adjusted for inverse structure

**Margin**:
- Portfolio margin (cross positions offset)
- Inverse options + USDC options offset each other
- Calculated in BTC

**Reference**:
- [Deribit USDC Options Launch](https://insights.deribit.com/education/usdc-settled-btc-eth-options-launch/)
- [Inverse Options Research Paper](https://arxiv.org/pdf/2107.12041)

---

### OKX

**Products**:
- Crypto-settled options (BTC/ETH)
- **Not explicitly called "inverse"**, but functionally same

**Settlement**:
- BTC/ETH settlement
- Underlying: BTC/USD index

**API Greeks**:
- OKX provides Greeks (assumed inverse-adjusted, verify!)
- Fields: `delta`, `gamma`, `vega`, `theta`

**Difference from Deribit**:
- OKX doesn't use term "inverse", just "crypto-settled"
- Functionally identical to inverse options

**Reference**:
- [OKX Options Introduction](https://www.okx.com/help/i-okx-options-introduction)

---

## 🚨 Common Mistakes (DON'T DO THIS)

### Mistake 1: Using Standard BS Greeks

**Wrong**:
```python
from scipy.stats import norm

def black_scholes_delta(S, K, r, sigma, T):
    d1 = (np.log(S/K) + (r + 0.5*sigma**2)*T) / (sigma*np.sqrt(T))
    return norm.cdf(d1)  # ❌ This is WRONG for inverse options

delta = black_scholes_delta(60000, 50000, 0.05, 0.8, 30/365)
# Result: 0.85 (standard delta)
# Actual inverse delta: ~0.65 (very different!)
```

**Right**:
```python
# Use exchange API
greeks = deribit_api.get_instrument(symbol)['greeks']
delta = greeks['delta']  # ✅ Correct inverse delta
```

---

### Mistake 2: USD-Only PnL Tracking

**Wrong**:
```python
# Track only USD P&L
portfolio_usd = 100000  # Start with $100k
pnl_usd = option_pnl_in_usd()
portfolio_usd += pnl_usd

# ❌ Ignores that your actual balance is in BTC
```

**Right**:
```python
# Track BTC balance
portfolio_btc = 100000 / 50000  # Start: 2 BTC ($100k at $50k/BTC)
pnl_btc = option_pnl_in_btc()
portfolio_btc += pnl_btc

# NAV in USD changes with BTC price
portfolio_usd = portfolio_btc * current_btc_price
```

---

### Mistake 3: Hedging with USD Futures

**Wrong**:
```python
# Buy BTC inverse call (delta = 0.6)
# Hedge with USD futures
hedge_contracts = -0.6 * inverse_call_qty  # ❌ Currency mismatch
```

**Right**:
```python
# Hedge with BTC perpetual (also BTC-margined)
btc_perp_delta = 1.0  # BTC perp has delta = 1 in BTC terms
hedge_qty = -(inverse_delta * inverse_call_qty) / btc_perp_delta
# Short BTC perpetual to hedge
```

---

### Mistake 4: Ignoring Convexity Flip

**Wrong**:
```python
# Assume gamma always positive
gamma_pnl = 0.5 * gamma * (dS**2)  # ❌ Can be negative for inverse!
```

**Right**:
```python
# Check gamma sign from exchange
gamma = exchange_greeks['gamma']  # Can be negative for deep ITM
gamma_pnl = 0.5 * gamma * (dS**2)  # Use actual gamma (with sign)
```

---

## 📐 Example Calculation (Full Walkthrough)

### Setup

- **Product**: Deribit BTC inverse call option
- **Strike**: K = $50,000
- **Current Price**: S = $60,000
- **Option Mark Price**: C = $11,000 (in USD terms)
- **Position**: Long 10 contracts

---

### Standard Option (Hypothetical USD-settled)

**Delta**: 0.85 (from Black-Scholes)

**If BTC moves $60k → $61k**:
```
Delta PnL = delta * dS * contracts
          = 0.85 * $1,000 * 10
          = $8,500 USD gain
```

---

### Inverse Option (Actual BTC-settled)

**Delta**: 0.65 (from Deribit API, inverse-adjusted)

**If BTC moves $60k → $61k**:
```
Delta PnL (USD) = delta_inv * dS * contracts
                = 0.65 * $1,000 * 10
                = $6,500 USD

Delta PnL (BTC) = $6,500 / $61,000
                = 0.1066 BTC
```

**Portfolio Impact**:
```
Before move:
  BTC balance: 2.0 BTC
  USD value: 2.0 * $60,000 = $120,000

After move (option PnL only):
  BTC balance: 2.0 + 0.1066 = 2.1066 BTC
  USD value: 2.1066 * $61,000 = $128,502

Total USD gain: $128,502 - $120,000 = $8,502
  = $6,500 (option PnL) + $2,002 (BTC appreciation on 2 BTC)
```

**Key Insight**:
- Option PnL: $6,500 (vs $8,500 for standard)
- But you also gain from BTC price increase on existing balance
- Net effect similar, but **attribution different**

---

### At Expiry (S = $65,000)

**Standard Option Payoff**:
```
Payoff = max($65,000 - $50,000, 0) * 10
       = $15,000 * 10
       = $150,000 USD
```

**Inverse Option Payoff**:
```
Payoff (USD) = $150,000 (same)
Payoff (BTC) = $150,000 / $65,000
             = 2.3077 BTC  # ⚠️ This is what you receive
```

**Portfolio After Settlement**:
```
BTC balance: 2.0 - 0.5 (premium paid) + 2.3077 (settlement)
           = 3.8077 BTC

USD value: 3.8077 * $65,000 = $247,500
```

---

## 🧠 When to Use Inverse vs Standard Options

### Use Inverse Options If:

1. ✅ You hold BTC/ETH long-term (HODLer)
2. ✅ You're a miner (receive BTC revenue)
3. ✅ You run a BTC treasury
4. ✅ You want to avoid fiat conversion friction
5. ✅ You trade on Deribit (no choice, inverse only)

### Use Standard (USDC) Options If:

1. ✅ You think in USD terms
2. ✅ You want simpler PnL tracking
3. ✅ You use standard Greek hedging strategies
4. ✅ You're arbitraging vs TradFi options
5. ✅ Available on Deribit (since Aug 2025) or other exchanges

---

## 🔍 Verification Checklist (Backtest)

Before trusting your inverse options backtest:

- [ ] **Greeks**: Used exchange API Greeks, NOT Black-Scholes
- [ ] **PnL**: Tracked both USD and BTC P&L
- [ ] **NAV**: Portfolio value in BTC, then convert to USD
- [ ] **Delta**: Verified delta non-monotonic for ITM calls
- [ ] **Hedging**: Used BTC-margined instruments (BTC perp, not USD futures)
- [ ] **Settlement**: Simulated BTC settlement (not USD)
- [ ] **Margin**: Calculated in BTC, not USD
- [ ] **Theta**: Used exchange theta (in BTC terms), not standard
- [ ] **Reconciliation**: BTC balance matches trade-by-trade
- [ ] **Comparison**: Ran same strategy on USDC options to verify difference

---

## 📚 Further Reading

### Research Papers

1. **"Inverse and Quanto Inverse Options in a Black-Scholes World"**
   - [arXiv:2107.12041](https://arxiv.org/pdf/2107.12041)
   - Comprehensive mathematical treatment
   - Greeks derivations, boundary conditions

2. **"Inverse Options in a Black-Scholes World"**
   - [ResearchGate](https://www.researchgate.net/publication/353478878_Inverse_Options_in_a_Black-Scholes_World)
   - Focuses on hedge ratios and convexity

### Exchange Documentation

1. **Deribit**:
   - [USDC Options Launch](https://insights.deribit.com/education/usdc-settled-btc-eth-options-launch/)
   - [Contract Specs (PDF)](https://statics.deribit.com/files/USDCContractSpecsandmargins.pdf)

2. **OKX**:
   - [Options Introduction](https://www.okx.com/help/i-okx-options-introduction)
   - [Get Started with Options](https://www.okx.com/help/get-started-with-okx-options)

### Related Knowledge Base

- `domain/options_basics.md` - Options fundamentals
- `exchanges/okx/options_specifications.md` - OKX option specs
- `../backtest_models/transaction_cost_model.md` - Cost modeling

---

## ⚠️ Critical Warnings

1. **NEVER use standard Black-Scholes Greeks** for inverse options
   → Error can be 10-50% for delta

2. **NEVER hedge with USD futures**
   → Currency mismatch, hedge will fail

3. **NEVER track only USD P&L**
   → Your real balance is BTC, BTC volatility affects NAV

4. **NEVER assume delta bounded by 1**
   → Inverse delta can exceed 1 or be negative

5. **NEVER assume positive gamma**
   → Can flip negative for deep ITM

6. **NEVER ignore settlement currency in backtest**
   → Final reconciliation must be in BTC, not USD

---

**Last Updated**: 2025-12-23
**Version**: 1.0
**Author**: sqr
**Status**: ✅ Production

**Sources**:
- [Deribit USDC Options Launch](https://insights.deribit.com/education/usdc-settled-btc-eth-options-launch/)
- [Inverse Options Research Paper (arXiv)](https://arxiv.org/pdf/2107.12041)
- [OKX Options Documentation](https://www.okx.com/help/i-okx-options-introduction)
- [Options Greeks and P&L Decomposition](https://quant-next.com/option-greeks-and-pl-decomposition-part-1/)
