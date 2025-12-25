# Knowledge Base (중앙 지식 저장소)

**Purpose**: Agent들이 공통으로 참조하는 도메인 지식, 거래소 스펙, 모델링 디테일, 실험 방법론

**Last Updated**: 2025-12-23 (Added: options_expiry_and_tte.md)
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
| "SM이 뭐야?" | `exchanges/options_expiry_conventions.md` | Second Month (2개월 후), NOT Saturday! |
| "Front Month 언제?" | `exchanges/options_expiry_conventions.md` | 다음 월간 마지막 금요일 |
| "만기 약자 D/W/M/Q?" | `exchanges/options_expiry_conventions.md` | Daily/Weekly/Monthly/Quarterly |
| "micky 서버 데이터 접근?" | `infrastructure/postgres_data_access.md` | load_candles() 캐시 우선 |
| "PostgreSQL 연결 안 돼" | `infrastructure/postgres_data_access.md` | 트러블슈팅 (ping/ssh) |
| "캔들 데이터 어디서?" | `infrastructure/postgres_data_access.md` | micky (192.168.50.3) |
| "spice 옵션 DB 접속?" | `infrastructure/spice_options_database.md` | localhost:5432 (data_integration) |
| "btc_options_parsed 스키마?" | `infrastructure/spice_options_database.md` | 19개 컬럼, 169M rows |
| "OKX 옵션 데이터 어디?" | `infrastructure/spice_options_database.md` | btc_options_parsed (31M rows) |
| "Inverse option이 뭐야?" | `domain/inverse_options.md` | BTC-settled, delta unbounded |
| "Delta가 1 넘을 수 있어?" | `domain/inverse_options.md` | Inverse delta: non-monotonic |
| "BTC 세틀먼트 PnL 계산?" | `domain/inverse_options.md` | Payoff (BTC) = Payoff (USD) / S |
| "Greeks가 왜 다르지?" | `domain/inverse_options.md` | Convex→Concave transition |
| "만기 전에 거래 가능?" | `domain/options_expiry_and_tte.md` | UTC 08:00 직전까지 ✅ |
| "TTE 1일 미만이면?" | `domain/options_expiry_and_tte.md` | 거래 가능 (1분 전도 OK) |
| "만기일 당일 거래?" | `domain/options_expiry_and_tte.md` | UTC 07:59까지 가능 ✅ |
| "Gamma explosion 언제?" | `domain/options_expiry_and_tte.md` | TTE < 1 day, ATM |

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

- **[Options Expiry Conventions](exchanges/options_expiry_conventions.md)** ⭐⭐⭐
  - 만기 약자: D, W, M, **SM (Second Month, NOT Saturday Monthly!)**, Q
  - Front/Second/Third Month (FM, SM, TM)
  - 계산법: 마지막 금요일, UTC 08:00
  - 트레이더 용어: Near-term, Mid-term, Far-term
  - DTE 구분: 0-7 (감마), 30-60 (밸런스), 90+ (방향성)

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

- **[Agent Operating Procedure (SOP)](experiments/agent_operating_procedure.md)** ⭐⭐⭐
  - multi-project 서버에서 반복 지시 제거 (PROJECT_RULES.md + STATE.md)
  - 실험 폴더/코드 위생 표준 (src vs scratch)
  - backtest artifacts + preflight checks (integrity, MTM, metrics sanity)

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

- **[Lessons Learned](experiments/lessons_learned.md)** ⭐⭐⭐
  - 실패 사례, 교훈 (22개)
  - Look-ahead bias, Fill probability, Data quality, Greeks, Backtesting

- **[Common Mistakes](experiments/common_mistakes.md)** ⭐⭐⭐
  - Agent 반복 실수 (28개)
  - Python/Pandas, API, Backtesting, Greeks, Code organization

### 🎓 Domain (도메인 지식)

- **[Options Expiry & TTE](domain/options_expiry_and_tte.md)** ⭐⭐⭐
  - Expiry: UTC 08:00 (OKX/Deribit)
  - Trading until: **만기 직전까지** (UTC 07:59도 가능 ✅)
  - TTE ≠ Trading cutoff: TTE 1분(0.001 day)도 거래 가능
  - Common mistake: "TTE < 1 day = 거래 불가" (WRONG!)
  - Gamma explosion: TTE < 1 day, ATM (Greeks unreliable)
  - Backtest: Close 1 day before expiry (권장)
  - Timeline examples: 7일 전 → 1분 전 (구체적 시간표)

- **[Inverse Options](domain/inverse_options.md)** ⭐⭐⭐
  - USD-denominated contract, BTC/ETH settlement (Deribit, OKX)
  - Delta: non-monotonic, unbounded (vs standard [0,1])
  - PnL: BTC units, not USD (Payoff BTC = Payoff USD / S)
  - Greeks: use exchange API (NOT Black-Scholes)
  - Convexity flip: convex → concave for deep ITM
  - Backtest: track BTC balance, not just USD P&L

- **[Options Basics](domain/options_basics.md)** ⭐⭐
  - Greeks (Delta, Gamma, Theta, Vega)
  - Strategies (Covered Call, Straddle, Iron Condor)
  - IV & Volatility

- **[Trading Mechanics](domain/trading_mechanics.md)** ⭐⭐
  - Order types (Market, Limit, Stop, Post-Only)
  - Execution (Maker vs Taker, Slippage)
  - Margin & Settlement

### 🖥️ Infrastructure (인프라)

- **[PostgreSQL Data Access - micky](infrastructure/postgres_data_access.md)** ⭐⭐⭐
  - micky 서버 (192.168.50.3) - 캔들 데이터 (선물 1분봉)
  - `load_candles()` - Binance/OKX 데이터 로드 (캐시 우선)
  - 273M+ 행, 2023-01-01 ~ 현재, 준실시간 업데이트
  - 네트워크: vultr/spice → micky (내부 네트워크)
  - 캐시 시스템 (178 symbols, 363.87 MB)
  - 트러블슈팅: 연결 에러, 타임아웃, 캐시 손상

- **[Spice Options Database](infrastructure/spice_options_database.md)** ⭐⭐⭐
  - spice 서버 localhost (127.0.0.1:5432) - 옵션 데이터
  - Database: `data_integration` (PostgreSQL 12)
  - 메인 테이블: `btc_options_parsed` (169M rows, 2022-04-16 ~ 2025-12-05)
  - 데이터 소스: Deribit (138M), OKX (31M)
  - 컬럼: date, exchange, symbol, strike, callput, expiry, tte, iv, ohlc, greeks
  - 로딩: `/home/sqr/options_trading/data/load_to_db.py` (Parquet → PostgreSQL)
  - 기타 테이블: btc_options_hourly (15M, normalized), futures_data_1m, eth_options_parsed

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
