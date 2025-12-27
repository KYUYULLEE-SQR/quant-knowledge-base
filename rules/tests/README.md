# Prompt Test Cases (프롬프트 테스트)

**Purpose**: Agent 능동성 및 규칙 준수 검증
**Last Updated**: 2025-12-26
**Usage**: 새 세션 시작 시 또는 프롬프트 수정 후 검증용

---

## 🎯 테스트 목적

1. **능동성 유지 확인**: Agent가 수동적으로 변하지 않았는지
2. **규칙 준수 확인**: Self-verification, Phase 1, reconciliation 등
3. **회귀 방지**: 프롬프트 수정 후 기존 행동 유지 확인

---

## 📋 테스트 파일 목록

| 파일 | 테스트 대상 | 핵심 검증 |
|------|------------|----------|
| `test_proactivity.md` | 능동성 | 자동 실행, 확장, 다음 단계 |
| `test_metrics_output.md` | 출력 형식 | 테이블, 4+ metrics, 파일 경로 |
| `test_experiment_discipline.md` | 실험 규율 | Phase 1, reconciliation, baseline |
| `test_session_consistency.md` | 세션 일관성 | 100k tokens 후에도 동일 품질 |
| `test_kb_lookup.md` | KB 참조 | 도메인 질문 시 자동 검색 |

---

## 🔧 테스트 실행 방법

### Manual Testing (수동)

1. 새 세션 시작
2. 각 테스트 파일의 Input 입력
3. Expected와 비교
4. FAIL 시 프롬프트 수정

### Automated (자동화 예정)

```python
# 향후 구현
def test_proactivity():
    response = claude_code("이 전략 테스트해봐")
    assert "테스트할까요" not in response
    assert count_variants(response) >= 3
    assert "Next" in response
```

---

## 📊 Pass/Fail 기준

### PASS 조건
- [ ] Expected 출력과 일치
- [ ] Anti-pattern 없음
- [ ] 모든 필수 요소 포함

### FAIL 조건
- [ ] Anti-pattern 발견 ("테스트할까요?", 단독 숫자 등)
- [ ] 필수 요소 누락 (테이블, 파일 경로, Next Action)
- [ ] 수동적 응답 (질문하고 대기)

---

## 🚨 FAIL 시 조치

1. 어떤 테스트가 실패했는지 기록
2. 관련 rules 파일 확인
3. CLAUDE.md 또는 해당 rules 수정
4. 재테스트

---

**Version**: 1.0
