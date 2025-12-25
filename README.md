# Knowledge Base (중앙 지식 저장소)

**Purpose**: Agent들이 공통으로 참조하는 도메인 지식, 거래소 스펙, 모델링 디테일, 실험 방법론

**Last Updated**: 2025-12-25 (Folder structure reorganization)
**Owner**: sqr
**Environment**: micky (data), spice (backtest), vultr (trading)

---

## 📂 Structure (Self-Contained Names)

```
~/knowledge/
├── claude_code_rules/          # Claude Code 프롬프트 규칙 (행동 규칙)
│   ├── CLAUDE.md               # 메인 프롬프트
│   └── rules/                  # 모듈별 규칙 (10개)
│
├── exchanges/                  # 거래소별 스펙 (수수료, 옵션 스펙, API)
│   ├── okx/                    # OKX 거래소
│   ├── bybit/                  # Bybit 거래소
│   └── binance/                # Binance 거래소
│
├── modeling/                   # 백테스트 모델 (t-cost, 슬리피지, 체결 확률)
│
├── trading_concepts/           # 금융/트레이딩 기본 개념 (옵션, Greeks, 메커니즘)
│
├── experiment_methodology/     # 실험 설계 방법론 (Phase 1→2, 함정, 교훈)
│
├── data_infrastructure/        # DB/데이터 통합 인프라 (PostgreSQL, micky/spice)
│
├── strategies/                 # 전략별 지식 (전략 설명, 주의사항, 파라미터)
│
├── project_automation/         # 프로젝트 자동화 스크립트
│   ├── bootstrap_project_state.py   # PROJECT_RULES.md/STATE.md 생성
│   ├── project_guard.py             # 표준 폴더 구조 생성
│   └── preflight_backtest.py        # 백테스트 검증
│
├── design_decisions/           # 중요 설계 결정 아카이브 (대화 기록)
│
├── document_templates/         # 문서 작성 템플릿 (실험 보고서, KB 문서)
│
└── kb_inbox/                   # KB 업데이트 임시 보관 (pending updates)
```

**Design Principle**: 폴더 이름만 봐도 내용 파악 가능 (Self-Contained)

---

## 🎯 Agent 읽기 가이드

### Tier 1: Prompt (자동 로드, 매 세션)
- `claude_code_rules/` → HOW to behave (행동 규칙)
- 예: "실험 시 Phase 1 먼저", "백테스트 시 reconciliation 필수"

### Tier 2: Knowledge (필요할 때, on-demand)
- `exchanges/`, `modeling/`, `trading_concepts/` 등 → WHAT to know (도메인 지식)
- 예: "OKX 수수료 얼마", "슬리피지 모델", "옵션 기본 개념"

### 실험/작업 시 읽는 순서:
1. **Session Start** → `claude_code_rules/` 자동 로드
2. **User Question** → 해당 토픽의 KB 파일 읽기 (아래 Quick Start 참조)
3. **Experiment** → `experiment_methodology/` 읽기
4. **Data Access** → `data_infrastructure/` 읽기
5. **Exchange Spec** → `exchanges/okx/` 읽기

---

## 🚀 Quick Start (Agent용)

### BEFORE answering questions, READ relevant KB:

| Question Type | Read This | Example |
|--------------|-----------|---------|
| **거래소 스펙** |
| "수수료 얼마야?" | `exchanges/okx/fee_structure.md` | VIP9 maker -0.01% |
| "옵션 만기일 언제?" | `exchanges/okx/options_specifications.md` | UTC 08:00 |
| "주문이 부분 체결되면?" | `exchanges/okx/order_execution.md` | 30% fill 가정 |
| **백테스트 모델** |
| "슬리피지 어떻게 계산?" | `modeling/transaction_cost_model.md` | Depth 기반 추정 |
| **실험 방법론** |
| "실험 설계 어떻게?" | `experiment_methodology/methodology.md` | 변인 통제 (Phase 1→2) |
| "Look-ahead bias 방지?" | `experiment_methodology/common_pitfalls.md` | Signal shift test |
| "백테스트 NAV 계산?" | `experiment_methodology/backtesting_nav_policy.md` | Hourly MTM → Daily resample |
| "MDD가 0이라고 나와" | `experiment_methodology/backtesting_nav_policy.md` | Entry/Exit만 평가하는 문제 |
| **트레이딩 개념** |
| "Inverse option이 뭐야?" | `trading_concepts/inverse_options.md` | BTC-settled, delta unbounded |
| "Delta가 1 넘을 수 있어?" | `trading_concepts/inverse_options.md` | Inverse delta: non-monotonic |
| "만기 전에 거래 가능?" | `trading_concepts/options_expiry_and_tte.md` | UTC 08:00 직전까지 ✅ |
| "TTE 1일 미만이면?" | `trading_concepts/options_expiry_and_tte.md` | 거래 가능 (1분 전도 OK) |
| "Gamma explosion 언제?" | `trading_concepts/options_expiry_and_tte.md` | TTE < 1 day, ATM |
| **데이터 인프라** |
| "micky 서버 데이터 접근?" | `data_infrastructure/postgres_data_access.md` | load_candles() 캐시 우선 |
| "PostgreSQL 연결 안 돼" | `data_infrastructure/postgres_data_access.md` | 트러블슈팅 (ping/ssh) |
| "spice 옵션 DB 접속?" | `data_infrastructure/spice_options_database.md` | localhost:5432 (data_integration) |
| "btc_options_parsed 스키마?" | `data_infrastructure/spice_options_database.md` | 19개 컬럼, 169M rows |

### Response Format (필수)
```
[Answer]

📚 출처: knowledge/[category]/[file].md
```

---

## 📖 Document Index

### 🎨 Claude Code Rules (Prompt Engineering - Tier 1)

**목적**: Agent가 **어떻게 행동**해야 하는지 (HOW to behave)

- **[CLAUDE.md](claude_code_rules/CLAUDE.md)** ⭐⭐⭐
  - 메인 프롬프트 (identity, protocol, response structure)
- **[rules/](claude_code_rules/rules/)** (10개 파일)
  - 01: Identity & Context
  - 02: Cognitive Protocol
  - 03: Response Structure
  - 04: Operational Rules
  - 05: Experiment Guidelines
  - 06: Behavioral Rules
  - 08: Experiment Organization ⭐ (실험 파일 관리)
  - 10: Backtesting Integrity
  - 11: File Hygiene ⭐ ("정리해" 규칙)
  - 12: Project State Protocol ⭐ (PROJECT_RULES.md/STATE.md)

**읽기**: 자동 로드 (매 세션 시작 시)

---

### 🏦 Exchanges (거래소 스펙)

**목적**: 거래소별 구체적 스펙 (수수료, 옵션 스펙, API)

#### General (공통)
- **[Greeks Definitions](exchanges/greeks_definitions.md)** ⭐⭐⭐
  - OKX: PA (BTC units) vs BS (USD units)
  - Deribit: USD units (surprising for BTC-margined!)
  - Theta/Vega conversion: PA × BTC_price ≈ BS (1.00-1.05x)

- **[Options Expiry Conventions](exchanges/options_expiry_conventions.md)** ⭐⭐⭐
  - 만기 약자: D, W, M, **SM (Second Month, NOT Saturday Monthly!)**, Q
  - Front/Second/Third Month (FM, SM, TM)
  - 계산법: 마지막 금요일, UTC 08:00

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

#### Bybit
- **[Fee Structure](exchanges/bybit/fee_structure.md)** ⭐
  - Options: 3 bps maker/taker (no rebate)

- **[Options Specifications](exchanges/bybit/options_specifications.md)** ⭐
  - Contract size: 0.01 BTC, 0.1 ETH
  - USDT settlement

#### Binance
- **[Fee Structure](exchanges/binance/fee_structure.md)** ⭐
  - Options: 3 bps maker/taker + 1.5 bps exercise fee

- **[Options Specifications](exchanges/binance/options_specifications.md)** ⭐
  - USDT settlement
  - Writing access: LP-only (retail cannot write)

---

### 🧮 Modeling (백테스트 모델)

**목적**: 백테스트 시 사용하는 모델 (t-cost, 슬리피지, 체결 확률)

- **[Transaction Cost Model](modeling/transaction_cost_model.md)** ⭐⭐⭐
  - T-cost = fees + slippage + partial fill impact
  - Maker-only strategy (no slippage)
  - Partial fill model (30% fill, reorder next minute)

- **[Slippage Estimation](modeling/slippage_estimation.md)**
  - Depth-based, spread-based, impact models

- **[Fill Probability](modeling/fill_probability.md)**
  - Partial fill probability (size, volatility, depth)

---

### 🎓 Trading Concepts (트레이딩 개념)

**목적**: 금융/트레이딩 기본 개념 (거래소 무관)

- **[Inverse Options](trading_concepts/inverse_options.md)** ⭐⭐⭐
  - USD-denominated contract, BTC/ETH settlement (Deribit, OKX)
  - Delta: non-monotonic, unbounded (vs standard [0,1])
  - PnL: BTC units, not USD (Payoff BTC = Payoff USD / S)
  - Greeks: use exchange API (NOT Black-Scholes)
  - Convexity flip: convex → concave for deep ITM

- **[Options Expiry & TTE](trading_concepts/options_expiry_and_tte.md)** ⭐⭐⭐
  - Expiry: UTC 08:00 (OKX/Deribit)
  - Trading until: **만기 직전까지** (UTC 07:59도 가능 ✅)
  - TTE ≠ Trading cutoff: TTE 1분(0.001 day)도 거래 가능
  - Common mistake: "TTE < 1 day = 거래 불가" (WRONG!)
  - Gamma explosion: TTE < 1 day, ATM (Greeks unreliable)

- **[Options Basics](trading_concepts/options_basics.md)** ⭐⭐
  - Greeks (Delta, Gamma, Theta, Vega)
  - Strategies (Covered Call, Straddle, Iron Condor)
  - IV & Volatility

- **[Trading Mechanics](trading_concepts/trading_mechanics.md)** ⭐⭐
  - Order types (Market, Limit, Stop, Post-Only)
  - Execution (Maker vs Taker, Slippage)
  - Margin & Settlement

---

### 🧪 Experiment Methodology (실험 방법론)

**목적**: 실험 설계 방법론, 함정, 교훈

- **[Methodology](experiment_methodology/methodology.md)** ⭐⭐⭐
  - 변인 통제 (한 번에 하나의 효과만)
  - Phase 1 (개별 효과) → Phase 2 (결합 효과)
  - Common mistakes (여러 변수 동시 변경)

- **[Common Pitfalls](experiment_methodology/common_pitfalls.md)** ⭐⭐⭐
  - Look-ahead bias, selection bias, data snooping
  - Overfitting, backtest-reality gap, regime change
  - Detection methods and prevention

- **[File Organization Policy](experiment_methodology/file_organization_policy.md)** ⭐⭐⭐
  - 100+ 실험 관리 구조
  - Strategy/Phase/Date-based hierarchy
  - REGISTRY.md for searchability

- **[Performance Metrics](experiment_methodology/performance_metrics.md)** ⭐⭐⭐
  - 365-day annualization (NOT 255)
  - Sharpe, Sortino, MDD, Volatility, Returns
  - Mark-to-Market NAV calculation

- **[Backtesting NAV Policy](experiment_methodology/backtesting_nav_policy.md)** ⭐⭐⭐
  - Hourly MTM evaluation (NOT entry/exit only)
  - Daily resample for metrics
  - Fixes MDD = 0 problem

- **[Lessons Learned](experiment_methodology/lessons_learned.md)** ⭐⭐⭐
  - 실패 사례, 교훈 (22개)
  - Look-ahead bias, Fill probability, Data quality, Greeks, Backtesting

- **[Common Mistakes](experiment_methodology/common_mistakes.md)** ⭐⭐⭐
  - Agent 반복 실수 (28개)
  - Python/Pandas, API, Backtesting, Greeks, Code organization

---

### 🖥️ Data Infrastructure (데이터 인프라)

**목적**: DB/데이터 통합 인프라 (PostgreSQL, micky/spice 서버)

- **[PostgreSQL Data Access - micky](data_infrastructure/postgres_data_access.md)** ⭐⭐⭐
  - micky 서버 (192.168.50.3) - 캔들 데이터 (선물 1분봉)
  - `load_candles()` - Binance/OKX 데이터 로드 (캐시 우선)
  - 273M+ 행, 2023-01-01 ~ 현재, 준실시간 업데이트
  - 네트워크: vultr/spice → micky (내부 네트워크)
  - 캐시 시스템 (178 symbols, 363.87 MB)
  - 트러블슈팅: 연결 에러, 타임아웃, 캐시 손상

- **[Spice Options Database](data_infrastructure/spice_options_database.md)** ⭐⭐⭐
  - spice 서버 localhost (127.0.0.1:5432) - 옵션 데이터
  - Database: `data_integration` (PostgreSQL 12)
  - 메인 테이블: `btc_options_parsed` (169M rows, 2022-04-16 ~ 2025-12-05)
  - 데이터 소스: Deribit (138M), OKX (31M)
  - 컬럼: date, exchange, symbol, strike, callput, expiry, tte, iv, ohlc, greeks
  - 로딩: `/home/sqr/options_trading/data/load_to_db.py` (Parquet → PostgreSQL)
  - 기타 테이블: btc_options_hourly (15M, normalized), futures_data_1m, eth_options_parsed

- **[Market Data Integration](data_infrastructure/market_data_integration.md)**
  - 데이터 소스 통합 (거래소 → DB → backtest)

- **[Deribit Options DB Archive](data_infrastructure/deribit_options_db_archive.md)**
  - Deribit 옵션 아카이브 (historical data)

---

### 🧬 Strategies (전략별 지식)

**목적**: 전략별 특수 지식, 주의사항, 파라미터 범위

(현재 비어있음 - 전략 성숙 시 문서화)

---

### 🛠️ Project Automation (프로젝트 자동화)

**목적**: 프로젝트 설정/검증 자동화 스크립트

- **[bootstrap_project_state.py](project_automation/bootstrap_project_state.py)**
  - PROJECT_RULES.md/STATE.md 생성 (non-destructive)

- **[project_guard.py](project_automation/project_guard.py)**
  - 표준 폴더 구조 생성 (src/, scratch/, experiments/)

- **[preflight_backtest.py](project_automation/preflight_backtest.py)**
  - 백테스트 검증 (artifacts + MTM/metrics sanity)

**Usage**:
```bash
# PROJECT_RULES.md/STATE.md 생성
python3 ~/knowledge/project_automation/bootstrap_project_state.py ~/options_trading

# 표준 폴더 생성
python3 ~/knowledge/project_automation/project_guard.py ~/options_trading

# 백테스트 검증
python3 ~/knowledge/project_automation/preflight_backtest.py ~/experiments/2025-12-25_test/
```

---

### 🗂️ Design Decisions (설계 결정)

**목적**: 중요한 설계 결정, 통찰, 교훈이 담긴 대화 보관

- **[2025-12-25 Multi-Project State Architecture](design_decisions/2025-12-25_multi_project_state_architecture_handoff.md)** ⭐⭐⭐
  - multi-project 서버에서 반복 지시 제거를 위한 state management architecture
  - `/home/sqr/_meta` 자동화 + `PROJECT_RULES.md`/`STATE.md` 표준
  - Phase 1(단일효과) → Phase 2(결합) 실험 순서 강제

**보관 기준**:
1. 중요한 아키텍처/구현 결정
2. 실패 사례, 성공 패턴
3. 반복되는 문제의 근본 원인
4. 새로운 실험 방법, 백테스트 기법

---

### 📄 Document Templates (문서 템플릿)

**목적**: 일관된 문서 작성을 위한 템플릿

(현재 비어있음 - 문서화 패턴 반복 시 템플릿화)

---

### 📥 KB Inbox (KB 업데이트 임시 보관)

**목적**: 다른 프로젝트/에이전트에서 발견한 지식을 임시 보관 후 KB에 반영

**사용법**:
1. 새로운 지식 발견 시: `~/knowledge/kb_inbox/YYYY-MM-DD_topic.md` 작성
2. 파일 형식: Summary, Details, Action Required, References
3. 주기적 검토 (주 1회): KB 파일에 반영 → kb_inbox 파일 삭제

**현재 상태**: 0 files (pending updates 없음)

---

## 🔄 Update Protocol

### When to Update

1. ✅ **User teaches new knowledge** → Update relevant .md
2. ✅ **Experiment reveals insight** → Update `experiment_methodology/lessons_learned.md`
3. ✅ **Exchange changes fees/specs** → Update `exchanges/okx/*.md`
4. ✅ **Model improved** → Update `modeling/*.md`
5. ✅ **Important conversation** → Archive to `design_decisions/`

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

4. **Folder names are self-documenting**
   - `experiment_methodology/` (NOT `experiments/`)
   - `project_automation/` (NOT `scripts/`)
   - `trading_concepts/` (NOT `domain/`)
   - Purpose clear from name alone

---

**Version**: 2.0 (Folder structure reorganization)
**Created**: 2025-12-22
**Last Updated**: 2025-12-25
