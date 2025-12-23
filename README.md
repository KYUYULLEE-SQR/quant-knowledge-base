# Knowledge Base (중앙 지식 저장소)

**Purpose**: Agent들이 공통으로 참조하는 도메인 지식, 거래소 스펙, 모델링 디테일, 실험 방법론

**Last Updated**: 2025-12-23
**Owner**: sqr
**Environment**: micky (data), spice (backtest), vultr (trading)

---

## 📂 Structure

```
~/knowledge/
├── domain/              # 도메인 지식 (일반 개념, 거래소 무관)
├── exchanges/           # 거래소별 구체적 스펙 (OKX, Binance, ...)
├── modeling/            # 백테스트 모델링 디테일 (t-cost, slippage, fill)
├── infrastructure/      # 인프라 (서버, DB, 환경)
├── strategies/          # 전략별 지식
├── experiments/         # 실험 방법론, 교훈
└── conversations/       # 중요 대화 아카이브
```

---

## 🚀 Quick Start (Agent용)

### BEFORE answering questions, READ relevant KB:

| Question Type | Read This | Example |
|--------------|-----------|---------|
| "수수료 얼마야?" | `exchanges/okx/fee_structure.md` | VIP9 maker -0.02% |
| "슬리피지 어떻게 계산?" | `modeling/transaction_cost_model.md` | Depth 기반 추정 |
| "옵션 만기일 언제?" | `exchanges/okx/options_specifications.md` | UTC 08:00 |
| "주문이 부분 체결되면?" | `exchanges/okx/order_execution.md` | 30% fill 가정 |
| "실험 설계 어떻게?" | `experiments/methodology.md` | 변인 통제 (Phase 1→2) |
| "실험 파일 어디 저장?" | `experiments/file_organization_policy.md` | Strategy/Phase hierarchy |
| "Sharpe 어떻게 계산?" | `experiments/performance_metrics.md` | 365-day annualization |
| "Look-ahead bias 방지?" | `experiments/common_pitfalls.md` | Signal shift test |
| "백테스트 NAV 계산?" | `experiments/backtesting_nav_policy.md` | Hourly MTM → Daily resample |
| "MDD가 0이라고 나와" | `experiments/backtesting_nav_policy.md` | Entry/Exit만 평가하는 문제 |
| "Greeks PA vs BS 차이?" | `exchanges/greeks_definitions.md` | PA=BTC, BS=USD |
| "OKX Theta 어떻게 읽어?" | `exchanges/greeks_definitions.md` | PA: BTC/day, BS: USD/day |

### Response Format (필수)
```
[Answer]

📚 출처: knowledge/[category]/[file].md
```

---

## 📖 Document Index

### 🏦 Exchanges (거래소 스펙)

#### General (공통)
- **[Greeks Definitions](exchanges/greeks_definitions.md)** ⭐⭐⭐
  - OKX: PA (BTC units) vs BS (USD units)
  - Deribit: USD units (surprising for BTC-margined!)
  - Theta/Vega conversion: PA × BTC_price ≈ BS (1.00-1.05x)
  - Converter utility: `exchanges/greeks_converter.py`

#### OKX
- **[Fee Structure](exchanges/okx/fee_structure.md)** ⭐
  - VIP tiers (0-11), DMM (VIP9), maker/taker fees
  - 선물: maker -0.5bps, 옵션: maker -1bps

- **[Options Specifications](exchanges/okx/options_specifications.md)** ⭐
  - Expiry time: UTC 08:00 (KST 17:00)
  - Settlement, Greeks source, tick size

- **[Order Execution](exchanges/okx/order_execution.md)** ⭐
  - Maker order matching, partial fill probability (~30%)
  - Slippage model (depth-based)

- **[API Reference](exchanges/okx/api_reference.md)**
  - API docs links, key endpoints, rate limits

### 🧮 Modeling (백테스트 모델)

- **[Transaction Cost Model](modeling/transaction_cost_model.md)** ⭐⭐⭐
  - T-cost = fees + slippage + partial fill impact
  - Maker-only strategy (no slippage)
  - Partial fill model (30% fill, reorder next minute)

- **[Slippage Estimation](modeling/slippage_estimation.md)**
  - Depth-based, spread-based, impact models

- **[Fill Probability](modeling/fill_probability.md)**
  - Partial fill probability (size, volatility, depth)

### 🧪 Experiments (실험 방법론)

- **[Methodology](experiments/methodology.md)** ⭐⭐⭐
  - 변인 통제 (한 번에 하나의 효과만)
  - Phase 1 (개별 효과) → Phase 2 (결합 효과)
  - Common mistakes (여러 변수 동시 변경)

- **[Common Pitfalls](experiments/common_pitfalls.md)** ⭐⭐⭐
  - Look-ahead bias, selection bias, data snooping
  - Overfitting, backtest-reality gap, regime change
  - Detection methods and prevention

- **[File Organization Policy](experiments/file_organization_policy.md)** ⭐⭐⭐
  - 100+ 실험 관리 구조
  - Strategy/Phase/Date-based hierarchy
  - REGISTRY.md for searchability

- **[Performance Metrics](experiments/performance_metrics.md)** ⭐⭐⭐
  - 365-day annualization (NOT 255)
  - Sharpe, Sortino, MDD, Volatility, Returns
  - Mark-to-Market NAV calculation

- **[Backtesting NAV Policy](experiments/backtesting_nav_policy.md)** ⭐⭐⭐
  - Hourly MTM evaluation (NOT entry/exit only)
  - Daily resample for metrics
  - Fixes MDD = 0 problem

- **[Lessons Learned](experiments/lessons_learned.md)**
  - 실패 사례, 교훈

- **[Common Mistakes](experiments/common_mistakes.md)**
  - Agent들이 자주 하는 실수

### 🎓 Domain (도메인 지식)

- **[Options Basics](domain/options_basics.md)**
  - Greeks, payoff, moneyness

- **[Trading Mechanics](domain/trading_mechanics.md)**
  - Order types, execution, settlement

---

## 🔄 Update Protocol

### When to Update

1. ✅ **User teaches new knowledge** → Update relevant .md
2. ✅ **Experiment reveals insight** → Update `experiments/lessons_learned.md`
3. ✅ **Exchange changes fees/specs** → Update `exchanges/okx/*.md`
4. ✅ **Model improved** → Update `modeling/*.md`
5. ✅ **Important conversation** → Archive to `conversations/`

### How to Update

```python
# 1. Read existing file
from pathlib import Path
kb_file = Path('~/knowledge/exchanges/okx/fee_structure.md').expanduser()
content = kb_file.read_text()

# 2. Edit (add section or update)
updated_content = content + "\n## New Section\n..."

# 3. Write back
kb_file.write_text(updated_content)

# 4. Update "Last Updated" date

# 5. Notify user
print(f"✅ Updated {kb_file.name}")
```

---

## 🔍 Search KB

```bash
# Text search
grep -r "maker fee" ~/knowledge/

# Find by topic
ls ~/knowledge/exchanges/okx/

# View index
cat ~/knowledge/README.md
```

---

## ⚠️ Important Notes

1. **API docs are source of truth**
   - KB is summary/interpretation
   - When in doubt, check official docs (links in KB)

2. **KB ≠ Implementation**
   - KB describes "what/how"
   - Code implements "actual logic"

3. **Keep KB updated**
   - Outdated KB worse than no KB
   - Always update "Last Updated" date

---

**Version**: 1.0
**Created**: 2025-12-22
