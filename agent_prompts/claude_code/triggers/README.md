# Triggers (자동 행동 트리거)

**Purpose**: 키워드 감지 → 자동 행동 정의
**Last Updated**: 2025-12-26

---

## 📂 파일 구조

```
triggers/
├── README.md                    # 이 파일
├── proactivity_triggers.md      # 능동성 트리거 (즉시 실행, 자동 확장)
└── anti_patterns.md             # 금지 패턴 (확인 요청, 불완전 출력)
```

---

## 🎯 핵심 원칙

**"묻지 말고 해라"**

1. 특정 키워드 감지 → 즉시 행동
2. 확인 요청 = 실패
3. 1개 실행 = 불완전 → 3-5개로 확장
4. 단독 숫자 = 금지 → 테이블로

---

## 🔥 트리거 요약

### 즉시 실행 트리거

| 키워드 | 행동 |
|-------|------|
| 테스트, 실험, 해봐 | 3-5개 변형 + baseline + falsification |
| 분석, 봐줘 | 통계 + 발견 + 시각화 |
| 만들어, 구현 | 전체 코드 + 실행 + 결과 |
| 고쳐, 개선 | 수정 + before/after |

### KB 참조 트리거

| 키워드 | 참조 파일 |
|-------|----------|
| 수수료, fee | okx/fee_structure.md |
| Greeks, delta | greeks_definitions.md |
| 만기, TTE | options_expiry_and_tte.md |
| 슬리피지 | transaction_cost_model.md |

### 규율 강제 트리거

| 감지 | 행동 |
|-----|------|
| 다중 변수 | Phase 1 분리 |
| 백테스트 완료 | Reconciliation 필수 |
| MDD > 100% | 무효화 + 재실행 |

---

## 🚫 Anti-Pattern 요약

### 절대 금지

| 패턴 | 대신 |
|-----|------|
| "~할까요?" | 즉시 실행 |
| 옵션 나열 + 대기 | 선택 + 실행 |
| 단독 숫자 | 4+ metrics 테이블 |
| 1개만 실행 | 3-5개 변형 |
| 경로 누락 | 경로 포함 |
| Expected: | 실제 실행 |

---

## 📚 연관 파일

- `tests/test_proactivity.md` - 능동성 테스트
- `rules/00_output_enforcement.md` - 출력 강제
- `rules/06_behavioral_rules.md` - 행동 규칙
- `CLAUDE.md` - 메인 프롬프트

---

**Version**: 1.0
