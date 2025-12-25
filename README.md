# Knowledge Base (중앙 지식 저장소)

**Purpose**: Agent들이 공통으로 참조하는 도메인 지식, 거래소 스펙, 모델링 디테일, 실험 방법론

**Last Updated**: 2025-12-25 (Hierarchical structure reorganization v3.0)
**Owner**: sqr
**Environment**: micky (data), spice (backtest), vultr (trading)

---

## 📂 Hierarchical Structure (Agent Workflow Order)

```
~/knowledge/
├── agent_prompts/                    # 🤖 Tier 1: HOW to behave (행동 규칙)
│   └── claude_code/
│       ├── CLAUDE.md                 # 메인 프롬프트
│       ├── rules/                    # 모듈별 규칙 (10개)
│       │   ├── 01_identity_and_context.md
│       │   ├── 02_cognitive_protocol.md
│       │   ├── 03_response_structure.md
│       │   ├── 04_operational_rules.md
│       │   ├── 05_experiment_guidelines.md
│       │   ├── 06_behavioral_rules.md
│       │   ├── 08_experiment_organization.md
│       │   ├── 10_backtesting_integrity.md
│       │   ├── 11_file_hygiene.md
│       │   └── 12_project_state_protocol.md
│       ├── install.sh                # Symlink 자동 설치 (~/.claude/)
│       └── README.md                 # Claude Code rules 사용법
│
├── domain_knowledge/                 # 📚 Tier 2: WHAT to know (도메인 지식)
│   ├── exchanges/                    # 거래소별 스펙 (수수료, 옵션, API)
│   │   ├── greeks_definitions.md     # OKX PA vs BS, Deribit
│   │   ├── options_expiry_conventions.md  # D/W/M/SM/Q 약자
│   │   ├── okx/
│   │   │   ├── fee_structure.md
│   │   │   ├── options_specifications.md
│   │   │   └── order_execution.md
│   │   ├── bybit/
│   │   │   ├── fee_structure.md
│   │   │   └── options_specifications.md
│   │   └── binance/
│   │       ├── fee_structure.md
│   │       └── options_specifications.md
│   │
│   ├── backtest_models/              # 백테스트 모델 (t-cost, 슬리피지, 체결)
│   │   ├── transaction_cost_model.md ⭐⭐⭐
│   │   ├── slippage_estimation.md
│   │   └── fill_probability.md
│   │
│   ├── trading_fundamentals/         # 트레이딩 기본 개념 (옵션, Greeks)
│   │   ├── inverse_options.md        ⭐⭐⭐
│   │   ├── options_expiry_and_tte.md ⭐⭐⭐
│   │   ├── options_basics.md
│   │   └── trading_mechanics.md
│   │
│   └── trading_strategies/           # 전략별 지식 (비어있음)
│
├── research_methodology/             # 🧪 실험 방법론 (설계, 함정, 교훈)
│   ├── experiment_design/
│   │   ├── methodology.md            ⭐⭐⭐ (Phase 1→2)
│   │   └── file_organization_policy.md
│   │
│   ├── backtest_standards/
│   │   ├── backtesting_nav_policy.md ⭐⭐⭐ (Hourly MTM)
│   │   └── performance_metrics.md    ⭐⭐⭐ (365-day annualization)
│   │
│   └── lessons_learned/
│       ├── common_pitfalls.md        ⭐⭐⭐ (Look-ahead bias 등)
│       ├── common_mistakes.md        ⭐⭐⭐ (Agent 반복 실수 28개)
│       └── lessons_learned.md        ⭐⭐⭐ (실패 사례 22개)
│
├── technical_infrastructure/         # 🖥️ 인프라 (DB, 서버, 자동화)
│   ├── databases/
│   │   ├── micky_postgres.md         ⭐⭐⭐ (선물 1분봉, 273M rows)
│   │   ├── spice_options_db.md       ⭐⭐⭐ (옵션 데이터, 169M rows)
│   │   ├── market_data_integration.md
│   │   └── deribit_options_db_archive.md
│   │
│   └── automation/                   # 프로젝트 자동화 스크립트
│       ├── bootstrap_project_state.py  # PROJECT_RULES.md/STATE.md 생성
│       ├── project_guard.py            # 표준 폴더 구조 생성
│       └── preflight_backtest.py       # 백테스트 검증
│
└── knowledge_base_meta/              # 📋 KB 관리 (메타 정보)
    ├── architecture_decisions/       # 중요 설계 결정 아카이브
    │   └── 2025-12-25_multi_project_state_architecture_handoff.md
    │
    ├── document_templates/           # 문서 템플릿 (비어있음)
    │
    └── pending_updates/              # KB 업데이트 임시 보관 (비어있음)
```

**Design Principle**: Agent 작업 순서대로 계층 구성
1. **agent_prompts/** - 어떻게 행동할지 (자동 로드)
2. **domain_knowledge/** - 무엇을 알아야 하는지 (필요시 검색)
3. **research_methodology/** - 실험 어떻게 설계할지
4. **technical_infrastructure/** - 데이터/서버 어떻게 접근할지
5. **knowledge_base_meta/** - KB 자체 관리

---

## 🎯 Agent 읽기 가이드

### 3-Tier Architecture

**Tier 1: Prompt (자동 로드, 매 세션)**
- `agent_prompts/claude_code/` → **HOW to behave** (행동 규칙)
- Symlink: `~/.claude/` → `~/knowledge/agent_prompts/claude_code/`
- 예: "실험 시 Phase 1 먼저", "백테스트 시 reconciliation 필수"
- 읽기: Claude Code가 자동 로드 (every session start)

**Tier 2: Knowledge (필요할 때, on-demand)**
- `domain_knowledge/`, `research_methodology/`, `technical_infrastructure/` → **WHAT to know** (도메인 지식)
- 예: "OKX 수수료 얼마", "슬리피지 모델", "옵션 기본 개념"
- 읽기: Agent가 질문/실험 시작 시 관련 KB 검색

**Tier 3: Project (프로젝트별 오버라이드)**
- `<project>/PROJECT_RULES.md`, `<project>/STATE.md`
- 프로젝트별 특수 규칙, 상태 기록

### 실험/작업 시 읽는 순서:

1. **Session Start** → `agent_prompts/` 자동 로드 (Tier 1)
2. **User Question** → 해당 토픽의 KB 파일 읽기 (Tier 2, 아래 Quick Start 참조)
3. **Experiment** → `research_methodology/experiment_design/` 읽기
4. **Data Access** → `technical_infrastructure/databases/` 읽기
5. **Exchange Spec** → `domain_knowledge/exchanges/okx/` 읽기

---

## 🚀 Quick Start (Agent용)

### BEFORE answering questions, READ relevant KB:

| Question Type | Read This | Example |
|--------------|-----------|---------|
| **거래소 스펙** |
| "수수료 얼마야?" | `domain_knowledge/exchanges/okx/fee_structure.md` | VIP9 maker -0.01% |
| "옵션 만기일 언제?" | `domain_knowledge/exchanges/okx/options_specifications.md` | UTC 08:00 |
| "주문이 부분 체결되면?" | `domain_knowledge/exchanges/okx/order_execution.md` | 30% fill 가정 |
| **백테스트 모델** |
| "슬리피지 어떻게 계산?" | `domain_knowledge/backtest_models/transaction_cost_model.md` | Depth 기반 추정 |
| **실험 방법론** |
| "실험 설계 어떻게?" | `research_methodology/experiment_design/methodology.md` | 변인 통제 (Phase 1→2) |
| "Look-ahead bias 방지?" | `research_methodology/lessons_learned/common_pitfalls.md` | Signal shift test |
| "백테스트 NAV 계산?" | `research_methodology/backtest_standards/backtesting_nav_policy.md` | Hourly MTM → Daily resample |
| "MDD가 0이라고 나와" | `research_methodology/backtest_standards/backtesting_nav_policy.md` | Entry/Exit만 평가하는 문제 |
| **트레이딩 개념** |
| "Inverse option이 뭐야?" | `domain_knowledge/trading_fundamentals/inverse_options.md` | BTC-settled, delta unbounded |
| "Delta가 1 넘을 수 있어?" | `domain_knowledge/trading_fundamentals/inverse_options.md` | Inverse delta: non-monotonic |
| "만기 전에 거래 가능?" | `domain_knowledge/trading_fundamentals/options_expiry_and_tte.md` | UTC 08:00 직전까지 ✅ |
| "TTE 1일 미만이면?" | `domain_knowledge/trading_fundamentals/options_expiry_and_tte.md` | 거래 가능 (1분 전도 OK) |
| "Gamma explosion 언제?" | `domain_knowledge/trading_fundamentals/options_expiry_and_tte.md` | TTE < 1 day, ATM |
| **데이터 인프라** |
| "micky 서버 데이터 접근?" | `technical_infrastructure/databases/micky_postgres.md` | load_candles() 캐시 우선 |
| "PostgreSQL 연결 안 돼" | `technical_infrastructure/databases/micky_postgres.md` | 트러블슈팅 (ping/ssh) |
| "spice 옵션 DB 접속?" | `technical_infrastructure/databases/spice_options_db.md` | localhost:5432 (data_integration) |
| "btc_options_parsed 스키마?" | `technical_infrastructure/databases/spice_options_db.md` | 19개 컬럼, 169M rows |

### Response Format (필수)
```
[Answer]

📚 출처: knowledge/[category]/[subcategory]/[file].md
```

---

## 📖 Document Index by Category

### 🤖 Agent Prompts (Tier 1: HOW to behave)

**목적**: Agent 행동 규칙 (자동 로드)

**Location**: `agent_prompts/claude_code/`

**Core Files**:
- **[CLAUDE.md](agent_prompts/claude_code/CLAUDE.md)** ⭐⭐⭐
  - 메인 프롬프트 (identity, protocol, response structure)
- **[install.sh](agent_prompts/claude_code/install.sh)**
  - Symlink 자동 설치 스크립트 (`~/.claude/` ← `~/knowledge/agent_prompts/claude_code/`)

**Rules (10개)**:
1. **01_identity_and_context.md** - Identity & Server Context
2. **02_cognitive_protocol.md** - Cognitive Protocol (checklist)
3. **03_response_structure.md** - Response Structure (4-section format)
4. **04_operational_rules.md** - Code Quality, File Ops, DB, Performance
5. **05_experiment_guidelines.md** - Experiment Workflow (Phase 1→2)
6. **06_behavioral_rules.md** - Autonomy Principles (no asking)
7. **08_experiment_organization.md** ⭐ - Experiment File Management
8. **10_backtesting_integrity.md** - Trade-by-Trade Reconciliation
9. **11_file_hygiene.md** ⭐ - "정리해" Command Rules
10. **12_project_state_protocol.md** ⭐ - PROJECT_RULES.md/STATE.md Protocol

**읽기**: 자동 로드 (매 세션 시작 시, via ~/.claude/ symlink)

---

### 📚 Domain Knowledge (Tier 2: WHAT to know)

#### 🏦 Exchanges (거래소 스펙)

**Location**: `domain_knowledge/exchanges/`

**General**:
- **[Greeks Definitions](domain_knowledge/exchanges/greeks_definitions.md)** ⭐⭐⭐
  - OKX: PA (BTC units) vs BS (USD units)
  - Deribit: USD units (surprising for BTC-margined!)
  - Theta/Vega conversion: PA × BTC_price ≈ BS (1.00-1.05x)

- **[Options Expiry Conventions](domain_knowledge/exchanges/options_expiry_conventions.md)** ⭐⭐⭐
  - 만기 약자: D, W, M, **SM (Second Month, NOT Saturday Monthly!)**, Q
  - Front/Second/Third Month (FM, SM, TM)
  - 계산법: 마지막 금요일, UTC 08:00

**OKX**:
- **[Fee Structure](domain_knowledge/exchanges/okx/fee_structure.md)** ⭐
  - VIP tiers (0-11), DMM (VIP9), maker/taker fees
  - 선물: maker -0.5bps, 옵션: maker -1bps

- **[Options Specifications](domain_knowledge/exchanges/okx/options_specifications.md)** ⭐
  - Expiry time: UTC 08:00 (KST 17:00)
  - Settlement, Greeks source, tick size

- **[Order Execution](domain_knowledge/exchanges/okx/order_execution.md)** ⭐
  - Maker order matching, partial fill probability (~30%)
  - Slippage model (depth-based)

**Bybit**:
- **[Fee Structure](domain_knowledge/exchanges/bybit/fee_structure.md)** ⭐
  - Options: 3 bps maker/taker (no rebate)

- **[Options Specifications](domain_knowledge/exchanges/bybit/options_specifications.md)** ⭐
  - Contract size: 0.01 BTC, 0.1 ETH
  - USDT settlement

**Binance**:
- **[Fee Structure](domain_knowledge/exchanges/binance/fee_structure.md)** ⭐
  - Options: 3 bps maker/taker + 1.5 bps exercise fee

- **[Options Specifications](domain_knowledge/exchanges/binance/options_specifications.md)** ⭐
  - USDT settlement
  - Writing access: LP-only (retail cannot write)

---

#### 🧮 Backtest Models (백테스트 모델)

**Location**: `domain_knowledge/backtest_models/`

- **[Transaction Cost Model](domain_knowledge/backtest_models/transaction_cost_model.md)** ⭐⭐⭐
  - T-cost = fees + slippage + partial fill impact
  - Maker-only strategy (no slippage)
  - Partial fill model (30% fill, reorder next minute)

- **[Slippage Estimation](domain_knowledge/backtest_models/slippage_estimation.md)**
  - Depth-based, spread-based, impact models

- **[Fill Probability](domain_knowledge/backtest_models/fill_probability.md)**
  - Partial fill probability (size, volatility, depth)

---

#### 🎓 Trading Fundamentals (트레이딩 개념)

**Location**: `domain_knowledge/trading_fundamentals/`

- **[Inverse Options](domain_knowledge/trading_fundamentals/inverse_options.md)** ⭐⭐⭐
  - USD-denominated contract, BTC/ETH settlement (Deribit, OKX)
  - Delta: non-monotonic, unbounded (vs standard [0,1])
  - PnL: BTC units, not USD (Payoff BTC = Payoff USD / S)
  - Greeks: use exchange API (NOT Black-Scholes)
  - Convexity flip: convex → concave for deep ITM

- **[Options Expiry & TTE](domain_knowledge/trading_fundamentals/options_expiry_and_tte.md)** ⭐⭐⭐
  - Expiry: UTC 08:00 (OKX/Deribit)
  - Trading until: **만기 직전까지** (UTC 07:59도 가능 ✅)
  - TTE ≠ Trading cutoff: TTE 1분(0.001 day)도 거래 가능
  - Common mistake: "TTE < 1 day = 거래 불가" (WRONG!)
  - Gamma explosion: TTE < 1 day, ATM (Greeks unreliable)

- **[Options Basics](domain_knowledge/trading_fundamentals/options_basics.md)** ⭐⭐
  - Greeks (Delta, Gamma, Theta, Vega)
  - Strategies (Covered Call, Straddle, Iron Condor)
  - IV & Volatility

- **[Trading Mechanics](domain_knowledge/trading_fundamentals/trading_mechanics.md)** ⭐⭐
  - Order types (Market, Limit, Stop, Post-Only)
  - Execution (Maker vs Taker, Slippage)
  - Margin & Settlement

---

#### 🧬 Trading Strategies (전략별 지식)

**Location**: `domain_knowledge/trading_strategies/`

**Status**: 비어있음 (전략 성숙 시 문서화)

---

### 🧪 Research Methodology (실험 방법론)

#### 🎨 Experiment Design (실험 설계)

**Location**: `research_methodology/experiment_design/`

- **[Methodology](research_methodology/experiment_design/methodology.md)** ⭐⭐⭐
  - 변인 통제 (한 번에 하나의 효과만)
  - Phase 1 (개별 효과) → Phase 2 (결합 효과)
  - Common mistakes (여러 변수 동시 변경)

- **[File Organization Policy](research_methodology/experiment_design/file_organization_policy.md)** ⭐⭐⭐
  - 100+ 실험 관리 구조
  - Strategy/Phase/Date-based hierarchy
  - REGISTRY.md for searchability

---

#### 📊 Backtest Standards (백테스트 표준)

**Location**: `research_methodology/backtest_standards/`

- **[Backtesting NAV Policy](research_methodology/backtest_standards/backtesting_nav_policy.md)** ⭐⭐⭐
  - Hourly MTM evaluation (NOT entry/exit only)
  - Daily resample for metrics
  - Fixes MDD = 0 problem

- **[Performance Metrics](research_methodology/backtest_standards/performance_metrics.md)** ⭐⭐⭐
  - 365-day annualization (NOT 255)
  - Sharpe, Sortino, MDD, Volatility, Returns
  - Mark-to-Market NAV calculation

---

#### 📚 Lessons Learned (교훈)

**Location**: `research_methodology/lessons_learned/`

- **[Common Pitfalls](research_methodology/lessons_learned/common_pitfalls.md)** ⭐⭐⭐
  - Look-ahead bias, selection bias, data snooping
  - Overfitting, backtest-reality gap, regime change
  - Detection methods and prevention

- **[Common Mistakes](research_methodology/lessons_learned/common_mistakes.md)** ⭐⭐⭐
  - Agent 반복 실수 (28개)
  - Python/Pandas, API, Backtesting, Greeks, Code organization

- **[Lessons Learned](research_methodology/lessons_learned/lessons_learned.md)** ⭐⭐⭐
  - 실패 사례, 교훈 (22개)
  - Look-ahead bias, Fill probability, Data quality, Greeks, Backtesting

---

### 🖥️ Technical Infrastructure (인프라)

#### 💾 Databases (데이터베이스)

**Location**: `technical_infrastructure/databases/`

- **[Micky PostgreSQL](technical_infrastructure/databases/micky_postgres.md)** ⭐⭐⭐
  - micky 서버 (192.168.50.3) - 캔들 데이터 (선물 1분봉)
  - `load_candles()` - Binance/OKX 데이터 로드 (캐시 우선)
  - 273M+ 행, 2023-01-01 ~ 현재, 준실시간 업데이트
  - 네트워크: vultr/spice → micky (내부 네트워크)
  - 캐시 시스템 (178 symbols, 363.87 MB)
  - 트러블슈팅: 연결 에러, 타임아웃, 캐시 손상

- **[Spice Options DB](technical_infrastructure/databases/spice_options_db.md)** ⭐⭐⭐
  - spice 서버 localhost (127.0.0.1:5432) - 옵션 데이터
  - Database: `data_integration` (PostgreSQL 12)
  - 메인 테이블: `btc_options_parsed` (169M rows, 2022-04-16 ~ 2025-12-05)
  - 데이터 소스: Deribit (138M), OKX (31M)
  - 컬럼: date, exchange, symbol, strike, callput, expiry, tte, iv, ohlc, greeks
  - 로딩: `/home/sqr/options_trading/data/load_to_db.py` (Parquet → PostgreSQL)
  - 기타 테이블: btc_options_hourly (15M, normalized), futures_data_1m, eth_options_parsed

- **[Market Data Integration](technical_infrastructure/databases/market_data_integration.md)**
  - 데이터 소스 통합 (거래소 → DB → backtest)

- **[Deribit Options DB Archive](technical_infrastructure/databases/deribit_options_db_archive.md)**
  - Deribit 옵션 아카이브 (historical data)

---

#### 🛠️ Automation (자동화)

**Location**: `technical_infrastructure/automation/`

- **[bootstrap_project_state.py](technical_infrastructure/automation/bootstrap_project_state.py)**
  - PROJECT_RULES.md/STATE.md 생성 (non-destructive)

- **[project_guard.py](technical_infrastructure/automation/project_guard.py)**
  - 표준 폴더 구조 생성 (src/, scratch/, experiments/)

- **[preflight_backtest.py](technical_infrastructure/automation/preflight_backtest.py)**
  - 백테스트 검증 (artifacts + MTM/metrics sanity)

**Usage**:
```bash
# PROJECT_RULES.md/STATE.md 생성
python3 ~/knowledge/technical_infrastructure/automation/bootstrap_project_state.py ~/options_trading

# 표준 폴더 생성
python3 ~/knowledge/technical_infrastructure/automation/project_guard.py ~/options_trading

# 백테스트 검증
python3 ~/knowledge/technical_infrastructure/automation/preflight_backtest.py ~/experiments/2025-12-25_test/
```

---

### 📋 Knowledge Base Meta (KB 관리)

#### 🗂️ Architecture Decisions (설계 결정)

**Location**: `knowledge_base_meta/architecture_decisions/`

- **[2025-12-25 Multi-Project State Architecture](knowledge_base_meta/architecture_decisions/2025-12-25_multi_project_state_architecture_handoff.md)** ⭐⭐⭐
  - multi-project 서버에서 반복 지시 제거를 위한 state management architecture
  - `/home/sqr/_meta` 자동화 + `PROJECT_RULES.md`/`STATE.md` 표준
  - Phase 1(단일효과) → Phase 2(결합) 실험 순서 강제

**보관 기준**:
1. 중요한 아키텍처/구현 결정
2. 실패 사례, 성공 패턴
3. 반복되는 문제의 근본 원인
4. 새로운 실험 방법, 백테스트 기법

---

#### 📄 Document Templates (문서 템플릿)

**Location**: `knowledge_base_meta/document_templates/`

**Status**: 비어있음 (문서화 패턴 반복 시 템플릿화)

---

#### 📥 Pending Updates (업데이트 대기)

**Location**: `knowledge_base_meta/pending_updates/`

**목적**: 다른 프로젝트/에이전트에서 발견한 지식을 임시 보관 후 KB에 반영

**사용법**:
1. 새로운 지식 발견 시: `~/knowledge/knowledge_base_meta/pending_updates/YYYY-MM-DD_topic.md` 작성
2. 파일 형식: Summary, Details, Action Required, References
3. 주기적 검토 (주 1회): KB 파일에 반영 → pending_updates 파일 삭제

**Status**: 비어있음 (pending updates 없음)

---

## 🔄 Update Protocol

### When to Update

1. ✅ **User teaches new knowledge** → Update relevant .md
2. ✅ **Experiment reveals insight** → Update `research_methodology/lessons_learned/`
3. ✅ **Exchange changes fees/specs** → Update `domain_knowledge/exchanges/okx/`
4. ✅ **Model improved** → Update `domain_knowledge/backtest_models/`
5. ✅ **Important conversation** → Archive to `knowledge_base_meta/architecture_decisions/`

### How to Update

```python
# 1. Read existing file
from pathlib import Path
kb_file = Path('~/knowledge/domain_knowledge/exchanges/okx/fee_structure.md').expanduser()
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
ls ~/knowledge/domain_knowledge/exchanges/okx/

# View index
cat ~/knowledge/README.md
```

---

## 🚫 Anti-Repetition Protocol (같은 말 안하게)

**목적**: 사용자가 같은 지시를 반복하지 않아도 Agent가 자동 적용

### 자동 적용 규칙

| 반복되는 지시 | Agent 자동 트리거 | KB 참조 |
|--------------|------------------|---------|
| "Deep Reasoning Mode" | L3/L4 복잡도 작업 시 자동 활성화 | `rules/02_cognitive_protocol.md` |
| "Correctness over speed" | 백테스트/실험/아키텍처 작업 시 자동 적용 | `rules/06_behavioral_rules.md` |
| "Phase 1 먼저" | 실험 설계 시 단일 변수 우선 강제 | `rules/05_experiment_guidelines.md` |
| "KB 찾아봐" | 도메인 질문 시 자동 검색 | 이 README.md Quick Start |
| "생각해" / "깊이 생각해" | L3/L4 판단 시 Deep Reasoning 자동 | `rules/02_cognitive_protocol.md` |
| "검증해" / "확인해" | 백테스트 결과에 reconciliation 필수 | `rules/10_backtesting_integrity.md` |

### Red Flags: 사용자가 이 말을 하면 Agent가 잘못하고 있는 것

| 사용자 발언 | 의미 | Agent 수정 행동 |
|------------|------|----------------|
| ❌ "아까 말했잖아" | Context 추적 실패 | 이전 대화 참조, STATE.md 확인 |
| ❌ "KB에 있을텐데" | KB 검색 안 함 | Quick Start 테이블 참조 후 답변 |
| ❌ "Phase 1 먼저 해야지" | 실험 순서 위반 | 즉시 Phase 1로 재설계 |
| ❌ "생각 좀 해" | 성급한 실행 | 복잡도 L3/L4 재평가, Deep Reasoning |
| ❌ "왜 또 물어봐?" | 불필요한 확인 요청 | Assume → State → Proceed |
| ❌ "reconciliation은?" | 정합성 검증 누락 | trades.csv, positions.csv 생성 |

### Agent Self-Check (매 응답 전)

```
□ 이 작업의 복잡도? (L1-L4) → L3/L4면 Deep Reasoning 자동
□ 도메인 질문인가? → KB Quick Start 확인
□ 실험 설계인가? → Phase 1 단일변수 먼저
□ 백테스트인가? → reconciliation 파일 필수
□ 이전에 사용자가 관련 지시 했는가? → 자동 적용
```

### 예시

**❌ Bad (사용자가 반복해야 함)**:
```
User: "백테스트 해줘"
Agent: "백테스트 실행합니다"
User: "Phase 1 먼저 해야지"
Agent: "네, Phase 1으로 합니다"
User: "그리고 Deep Reasoning Mode로"
Agent: "네, 깊이 생각합니다"
```

**✅ Good (Agent가 자동 적용)**:
```
User: "백테스트 해줘"
Agent: [내부 판단]
  - 복잡도: L3 (백테스트) → Deep Reasoning 자동
  - 실험: Phase 1 단일변수 먼저 적용
  - 결과: reconciliation 파일 자동 생성

Agent: "백테스트 L3 복잡도로 판단.
  1. Phase 1 (단일 효과) 먼저 설계
  2. Experiment Card 작성
  3. 결과에 trades.csv, reconciliation.csv 포함
  [실행]"
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

4. **Hierarchical structure follows agent workflow**
   - `agent_prompts/` → HOW to behave (Tier 1)
   - `domain_knowledge/` → WHAT to know (Tier 2)
   - `research_methodology/` → HOW to experiment
   - `technical_infrastructure/` → HOW to access data
   - `knowledge_base_meta/` → KB management

5. **Folder names are self-documenting**
   - `research_methodology/` (NOT `experiments/`)
   - `technical_infrastructure/automation/` (NOT `scripts/`)
   - `domain_knowledge/trading_fundamentals/` (NOT `concepts/`)
   - `agent_prompts/claude_code/` (NOT `rules/`)
   - Purpose clear from hierarchy + name

---

## 📦 Installation (New Server)

```bash
# 1. Clone knowledge repo
git clone https://github.com/KYUYULLEE-SQR/quant-knowledge-base.git ~/knowledge

# 2. Install Claude Code rules (symlink to ~/.claude/)
cd ~/knowledge/agent_prompts/claude_code
./install.sh

# 3. Done! Claude Code will auto-load prompts from ~/.claude/
```

---

**Version**: 3.1 (Anti-Repetition Protocol 추가)
**Created**: 2025-12-22
**Last Updated**: 2025-12-25
