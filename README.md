# Quant Knowledge Base

Quantitative trading research knowledge, organized for intuitive navigation.

**Repo**: `quant-knowledge-base` → Clone to `~/knowledge`

---

## Quick Find

| I want to know... | Look here |
|-------------------|-----------|
| Claude/Agent 행동 규칙 | `agent-rules/` |
| OKX 수수료 | `exchanges/okx/fee_structure.md` |
| 백테스트 방법 | `research/experiment/methodology.md` |
| 데이터베이스 접속 | `infra/databases/` |
| 과거 실수/교훈 | `research/lessons/` |
| 옵션 기초 | `trading/fundamentals/` |
| 슬리피지/비용 모델 | `trading/cost-models/` |
| KB 관리/메타 | `_kb-meta/` |

---

## Structure (6 folders)

```
knowledge/
├── agent-rules/      # Claude/Agent 행동 규칙 (→ ~/.claude/ symlink)
├── exchanges/        # 거래소별 스펙 (OKX, Bybit, Binance)
├── trading/          # 트레이딩 (fundamentals, strategies, cost-models)
├── research/         # 연구 방법론 (experiment, standards, lessons)
├── infra/            # 인프라 (databases, scripts)
└── _kb-meta/         # KB 관리 (decisions, templates, pending)
```

---

## Folder Naming Convention

**원칙**: 폴더명만 보고 내용을 알 수 있어야 함

| 폴더명 | 의미 | 왜 이 이름? |
|--------|------|------------|
| `agent-rules/` | Agent 행동 규칙 | "rules"만 쓰면 뭔지 모름 (거래 규칙? 거래소 규칙?) |
| `exchanges/` | 거래소 정보 | 명확함 |
| `trading/` | 트레이딩 개념 | 명확함 |
| `research/` | 연구 방법론 | 명확함 |
| `infra/` | 인프라 | 명확함 |
| `_kb-meta/` | KB 관리 | underscore = internal, "meta" = about KB itself |

**"정리해" 명령 시 적용되는 규칙**:
- 폴더명은 **내용을 설명**해야 함 (추상적 금지)
- 2단어 이상이면 hyphen 연결 (`agent-rules`, `cost-models`)
- 내부용/관리용은 underscore prefix (`_kb-meta`)

---

## Folder Details

### `agent-rules/` - Agent 행동 규칙
Claude Code behavior rules (auto-loaded via `~/.claude/` symlink)

| File | Purpose |
|------|---------|
| `CLAUDE.md` | 메인 프롬프트 (identity, autonomy, output) |
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

### `_kb-meta/` - KB 관리
Knowledge base management (internal)

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
| ⭐⭐⭐ | `agent-rules/00_output_enforcement.md` | 출력 품질 강제 |
| ⭐⭐⭐ | `trading/fundamentals/inverse_options.md` | Inverse 옵션 이해 |
| ⭐⭐⭐ | `research/standards/nav_policy.md` | MDD 계산 정책 |
| ⭐⭐ | `research/lessons/pitfalls.md` | Look-ahead bias 방지 |
| ⭐⭐ | `trading/cost-models/transaction_cost.md` | 거래비용 모델 |

---

## Setup (New Server)

```bash
# 1. Clone (폴더명 ~/knowledge로 지정)
git clone https://github.com/KYUYULLEE-SQR/quant-knowledge-base.git ~/knowledge

# 2. Install agent rules (symlink to ~/.claude/)
cd ~/knowledge/agent-rules && ./install.sh

# Done! Claude Code now uses these rules.
```

---

## Sync (Existing Server)

```bash
cd ~/knowledge && git pull
# Symlinks auto-update (no reinstall needed)
```

---

## "정리해" 명령 프로토콜

사용자가 "정리해"라고 하면:

1. **폴더명 검토**: 내용을 명확히 설명하는가?
   - ❌ `rules/` → 뭔지 모름
   - ✅ `agent-rules/` → Agent 규칙임을 알 수 있음

2. **Naming Convention 적용**:
   - 내용 설명 필수
   - 2단어 이상은 hyphen 연결
   - 내부용은 underscore prefix

3. **중복/혼란 제거**:
   - 비슷한 내용 → 하나로 통합
   - 관련 없는 내용 → 분리

4. **README 업데이트**: 구조 변경 반영

---

**Last Updated**: 2025-12-27
**Version**: 5.0 (Explicit naming convention + 정리해 protocol)
