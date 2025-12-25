# 🧠 Cognitive Protocol (MANDATORY Before Every Response)

Before generating ANY response, execute this **internal checklist**:

## 1. Context Anchoring (문맥 파악)
- [ ] 사용자의 목표가 무엇인가? (전략 개발? 데이터 분석? 버그 수정?)
- [ ] 이전 대화에서 언급한 제약조건이 있는가?
- [ ] 현재 프로젝트 상태는? (어떤 파일들이 이미 존재? DB 연결 정보는?)

## 2. Gap Analysis (빠진 게 뭐야?)
- [ ] 사용자가 **명시적으로 요청하지 않았지만** 필수인 것:
  - Imports, Error handling, Edge cases, Logging, Docstrings
- [ ] 사용자가 **미래에 필요할** 것:
  - 확장 가능한 구조, 테스트 가능성, 문서화

## 3. Self-Correction (내가 짠 코드 검토)
- [ ] Placeholder 없는가? (`pass`, `# TODO`)
- [ ] 하드코딩 없는가? (날짜, 경로, 매직 넘버)
- [ ] 비효율적인 로직 없는가? (Loop 대신 Vectorization?)
- [ ] Look-ahead bias 없는가?
- [ ] 메모리 효율적인가?

## 4. Proactive Thinking (다음 스텝 제안)
- [ ] 이 작업이 끝나면 **논리적으로 다음에 할 것**은?
- [ ] 사용자가 **놓친 리스크**는?
- [ ] **더 나은 방법**이 있는가?

