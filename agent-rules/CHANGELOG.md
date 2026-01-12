# CHANGELOG - CLAUDE.md 버전 히스토리

모든 주요 변경사항을 기록합니다.

---

## [10.1] - 2025-01-12

### Added
- `--dangerously-skip-permissions` 런타임 모드 명시
- `CLAUDE_SUMMARY.md` 생성 (~80줄 요약본)

### Fixed
- KB 파일 참조 검증 (6/6 확인)

---

## [10.0] - 2025-01-12

### Changed
- **대규모 통합**: 500줄 → 318줄 (36% 감소)
- 19개 섹션 → 14개 섹션으로 재구성
- 중복 규칙 제거:
  - "~할까요? 금지" (4곳 → 1곳)
  - "Look-ahead bias" (3곳 → 1곳)
  - "10+ metrics" (3곳 → 1곳)

### Removed
- 별도 Language 섹션 (자명하여 삭제)
- 별도 Negative Constraints 섹션 (Core Autonomy로 통합)
- 별도 Proactive Experimentation 섹션 (Sisyphus로 통합)

---

## [9.0] - 2025-01-11

### Added
- `19_verification_presets.md` - 검증 프리셋 시스템
- 키워드 트리거: 정합성, 엄밀하게, 객관적으로, 이상한거, 풀체크
- 옵션 백테스트 전용 체크리스트

---

## [8.0] - 2025-01-11

### Added
- `17_baksa_verification.md` - 적대적 검증 시스템 (My-Jogyo에서 이식)
  - Trust Score (0-100)
  - 4 Challenges
  - Dual Gate 시스템
  - 통계 마커: [STAT:ci], [STAT:effect_size], [STAT:sample_size]
- `18_sisyphus_protocol.md` - Never Give Up 프로토콜
  - 자동 재시도 (최대 3회)
  - 에러 → 수정 → 재실행
  - STATE.md 자동 저장

### Changed
- Self-Verification Loop에 Baksa 체크 항목 추가
- Load Order 업데이트 (9개 → 10개)

---

## [6.1] - 2025-12-30

### Added
- `15_quant_pitfalls.md` - 퀀트 함정 방지
  - Look-ahead bias 패턴
  - Chart timeframe 규칙
  - Pre-backtest checklist

### Changed
- Self-Verification Loop에 미래참조 체크 추가

---

## [6.0] - 2025-12-25

### Added
- `12_project_state_protocol.md` - 프로젝트 상태 관리
  - PROJECT_RULES.md / STATE.md 시스템
  - Phase 1 → Phase 2 실험 규율

### Changed
- 실험 가이드라인 강화 (One Variable at a Time)

---

## [5.0] - 2025-12-18

### Added
- `00_output_enforcement.md` - 출력 강제 규칙
- `08_experiment_organization.md` - 실험 폴더 구조
- `10_backtesting_integrity.md` - 백테스트 정합성

### Changed
- Mandatory Output 템플릿 추가
- Good vs Bad Examples 섹션 추가

---

## [4.0] - 2025-12-15

### Added
- `02_cognitive_protocol.md` - 사고 깊이 (L1-L4)
- `05_experiment_guidelines.md` - 실험 규율
- `06_behavioral_rules.md` - 행동 규칙

### Changed
- Core Autonomy 7대 원칙 정립

---

## [3.0] - 2025-12-10

### Added
- `01_identity_and_context.md` - 정체성 정의
- Knowledge Base 참조 시스템
- tests/ 폴더 구조

---

## [2.0] - 2025-12-05

### Added
- 기본 규칙 구조 설계
- Load Order 개념 도입

---

## [1.0] - 2025-12-01

### Added
- 초기 CLAUDE.md 생성
- 기본 퀀트 연구 규칙

---

## 파일 번호 변경 이력

| 날짜 | 변경 | 이유 |
|------|------|------|
| 2025-01-12 | `13_mandatory_backtest_autosave.md` → `20_` | 번호 충돌 해결 |

---

## 규칙 파일 목록 (현재)

```
00_output_enforcement.md      # 출력 강제
01_identity_and_context.md    # 정체성
02_cognitive_protocol.md      # 사고 깊이
03_response_structure.md      # 응답 구조
04_operational_rules.md       # 실무 규칙
05_experiment_guidelines.md   # 실험 규율
06_behavioral_rules.md        # 행동 규칙
08_experiment_organization.md # 실험 폴더
10_backtesting_integrity.md   # 백테스트 정합성
11_file_hygiene.md            # 파일 위생
12_project_state_protocol.md  # 프로젝트 상태
13_multi_agent_coordination.md# 멀티에이전트
14_executor_reading_list.md   # 실행자 가이드
15_quant_pitfalls.md          # 퀀트 함정
16_automated_research_loop.md # 자동 연구
17_baksa_verification.md      # 적대적 검증
18_sisyphus_protocol.md       # Never Give Up
19_verification_presets.md    # 검증 프리셋
20_mandatory_backtest_autosave.md # 백테스트 자동저장
```

---

**Maintained by**: Claude Code Agent
**Last Updated**: 2025-01-12
