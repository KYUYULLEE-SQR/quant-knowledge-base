# Quant Knowledge Base

Quantitative trading research knowledge, organized for intuitive navigation.

## Quick Find

| I want to know... | Look here |
|-------------------|-----------|
| Claude 행동 규칙 | `rules/` |
| OKX 수수료 | `exchanges/okx/fee_structure.md` |
| 백테스트 방법 | `research/experiment/methodology.md` |
| 데이터베이스 접속 | `infra/databases/` |
| 과거 실수/교훈 | `research/lessons/` |
| 옵션 기초 | `trading/fundamentals/` |
| 슬리피지/비용 모델 | `trading/cost-models/` |

---

## Structure (6 folders)

```
knowledge/
├── rules/            # Claude 행동 규칙 (→ ~/.claude/ symlink)
├── exchanges/        # 거래소별 스펙 (OKX, Bybit, Binance)
├── trading/          # 트레이딩 (fundamentals, strategies, cost-models)
├── research/         # 연구 방법론 (experiment, standards, lessons)
├── infra/            # 인프라 (databases, scripts)
└── _admin/           # KB 관리 (decisions, templates)
```

---

## Folder Details

### `rules/` - Claude 행동 규칙
Agent behavior rules (auto-loaded via `~/.claude/` symlink)

| File | Purpose |
|------|---------|
| `CLAUDE.md` | 메인 프롬프트 (identity, autonomy, output rules) |
| `00_output_enforcement.md` | 출력 강제 (HIGHEST PRIORITY) |
| `01_identity.md` ~ `12_*.md` | 세부 규칙 (11개) |
| `triggers/` | 능동성 트리거 |
| `tests/` | 규칙 테스트 케이스 (30개) |

### `exchanges/` - 거래소 정보
Exchange-specific specifications

| Folder | Contents |
|--------|----------|
| `_common/` | Greeks 정의, 만기 표기법 |
| `okx/` | 수수료, 옵션 스펙, API (8 files) |
| `bybit/` | 수수료, 옵션 스펙 |
| `binance/` | 수수료, 옵션 스펙 |

### `trading/` - 트레이딩
Trading concepts and models

| Folder | Contents |
|--------|----------|
| `fundamentals/` | 옵션 기초, inverse options, TTE |
| `strategies/` | MM, 리밸런싱 전략 |
| `cost-models/` | 거래비용, 슬리피지, 체결확률 |

### `research/` - 연구 방법론
Research methodology and lessons

| Folder | Contents |
|--------|----------|
| `experiment/` | 실험 설계 (Phase 1→2, 단일 변수) |
| `standards/` | NAV 정책, 성능 지표 |
| `lessons/` | 실패 사례, 흔한 실수 (50+ cases) |

### `infra/` - 인프라
Infrastructure and automation

| Folder | Contents |
|--------|----------|
| `databases/` | micky, corsair, spice 접속 정보 |
| `scripts/` | SSH 설정, 프로젝트 초기화 |

### `_admin/` - KB 관리
Knowledge base management

| Folder | Contents |
|--------|----------|
| `decisions/` | 아키텍처 결정 기록 |
| `templates/` | 문서 템플릿 |
| `pending/` | 반영 대기 업데이트 |

---

## Server Map

| Server | IP | Data | Docs |
|--------|-----|------|------|
| micky | 192.168.50.3 | Futures 1m (273M rows) | `infra/databases/micky_postgres.md` |
| corsair | 192.168.50.203 | Options Greeks (170M rows) | `infra/databases/corsair_timescaledb.md` |
| spice | localhost | Options raw (169M rows) | `infra/databases/spice_options_db.md` |

---

## Key Docs (Must Read)

| Priority | Document | Why |
|----------|----------|-----|
| ⭐⭐⭐ | `rules/00_output_enforcement.md` | 출력 품질 강제 |
| ⭐⭐⭐ | `trading/fundamentals/inverse_options.md` | Inverse 옵션 이해 |
| ⭐⭐⭐ | `research/standards/nav_policy.md` | MDD 계산 정책 |
| ⭐⭐ | `research/lessons/pitfalls.md` | Look-ahead bias 방지 |
| ⭐⭐ | `trading/cost-models/transaction_cost.md` | 거래비용 모델 |

---

## Setup (New Server)

```bash
# 1. Clone
git clone https://github.com/KYUYULLEE-SQR/quant-knowledge-base.git ~/knowledge

# 2. Install Claude rules (symlink to ~/.claude/)
cd ~/knowledge/rules && ./install.sh

# Done! Claude Code now uses these rules.
```

---

## Sync (Existing Server)

```bash
cd ~/knowledge && git pull
# Symlinks auto-update (no reinstall needed)
```

---

## Update Protocol

### When to Update
- User teaches new knowledge → Update relevant `.md`
- Experiment reveals insight → Update `research/lessons/`
- Exchange changes specs → Update `exchanges/<exchange>/`
- Important decision → Archive to `_admin/decisions/`

### How to Update
```bash
# Edit file
vim ~/knowledge/exchanges/okx/fee_structure.md

# Commit
cd ~/knowledge
git add -A && git commit -m "Update OKX fees"
git push
```

---

**Last Updated**: 2025-12-27
**Version**: 4.0 (Restructured for intuitive navigation)
