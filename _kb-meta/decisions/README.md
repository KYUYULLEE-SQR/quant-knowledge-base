# 중요 대화 아카이브

**Purpose**: 중요한 설계 결정, 통찰, 교훈이 담긴 대화 보관

---

## 사용 규칙

### 보관 기준

다음 조건 중 하나 이상 충족 시 아카이브:

1. **설계 결정**: 중요한 아키텍처/구현 결정
2. **교훈**: 실패 사례, 성공 패턴
3. **통찰**: 반복되는 문제의 근본 원인
4. **방법론**: 새로운 실험 방법, 백테스트 기법

### 파일명 규칙

```
YYYY-MM-DD_topic_name.md
```

**예시**:
- `2025-12-23_inverse_options_discovery.md`
- `2025-12-20_backtesting_nav_policy_decision.md`

---

## 구조

각 대화 파일은 다음 형식 권장:

```markdown
# [주제]

**Date**: YYYY-MM-DD
**Participants**: User, Claude
**Context**: 간단한 배경 설명

---

## Key Decisions

1. 결정 1
2. 결정 2

## Key Insights

- 통찰 1
- 통찰 2

## Lessons Learned

- 교훈 1
- 교훈 2

## References

- Link to related KB docs
```

---

## 현재 상태

**파일 수**: 1

- `2025-12-25_multi_project_state_architecture_handoff.md`
  - multi-project 서버에서 반복 지시 제거를 위한 “state management architecture”
  - `/home/sqr/_meta` 자동화 + `PROJECT_RULES.md`/`STATE.md` 표준
  - Phase 1(단일효과) → Phase 2(결합) 실험 순서 강제

중요한 대화가 발생하면 이 디렉토리에 보관하세요.
