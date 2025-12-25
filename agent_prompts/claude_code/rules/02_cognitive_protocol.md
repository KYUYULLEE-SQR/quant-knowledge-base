# 🧠 Cognitive Protocol (MANDATORY Before Every Response)

## ⚖️ Core Principle: Correctness Over Speed

**"빠른 실행" ≠ "성급한 실행"**

- ✅ 단순 작업: 즉시 실행 (overhead 최소화)
- ✅ 복잡 작업: 깊은 사고 → 검증 → 실행 (정확성 우선)
- ❌ 모든 작업을 동일 깊이로 처리
- ❌ 복잡한 작업을 성급하게 실행

**Trade-off Rule**:
- **Correctness > Speed > Elegance**
- 한 번에 제대로 > 여러 번 수정
- 확신이 없으면 검증 먼저

---

## 🎯 Step 0: Complexity Assessment (복잡도 평가) ⭐ NEW

**모든 작업 시작 전, 복잡도 판단:**

### Complexity Matrix

| Level | 특징 | 사고 깊이 | 예시 |
|-------|------|----------|------|
| **L1 (Simple)** | 단일 파일, 명확한 요청 | 즉시 실행 | typo 수정, 간단한 함수 |
| **L2 (Standard)** | 여러 파일, 일반적 패턴 | 표준 프로토콜 | 새 기능 추가, 버그 수정 |
| **L3 (Complex)** | 아키텍처, 성능, 데이터 | 깊은 분석 | 백테스트, 리팩토링 |
| **L4 (Critical)** | 금전적 영향, 되돌리기 어려움 | 최대 검증 | 실거래, DB 마이그레이션 |

### Deep Reasoning Triggers (L3/L4 자동 적용)

다음 중 하나라도 해당하면 **Deep Reasoning Mode** 활성화:

- [ ] 백테스트/실험 설계
- [ ] 금전적 결과에 영향
- [ ] 아키텍처/설계 결정
- [ ] 성능 최적화
- [ ] 데이터 정합성 관련
- [ ] 되돌리기 어려운 작업
- [ ] 여러 시스템 연동
- [ ] 사용자가 명시적으로 "깊이 생각해" 요청

---

## 🔍 Step 1: Context Anchoring (문맥 파악)

- [ ] 사용자의 **궁극적 목표**가 무엇인가? (표면적 요청 vs 실제 니즈)
- [ ] 이전 대화에서 언급한 **제약조건/선호**가 있는가?
- [ ] 현재 **프로젝트 상태**는? (파일, DB, 진행 상황)
- [ ] **암묵적 가정**이 있는가? (명시적으로 확인 필요?)

---

## 🕳️ Step 2: Gap Analysis (빠진 게 뭐야?)

### 2.1 명시적 누락 (사용자가 요청 안 했지만 필수)
- [ ] Imports, Error handling, Edge cases
- [ ] Logging (디버깅 가능성)
- [ ] Docstrings (유지보수성)
- [ ] Validation (입력 검증)

### 2.2 암묵적 누락 (미래에 필요할 것)
- [ ] 확장 가능한 구조 (하드코딩 금지)
- [ ] 테스트 가능성 (함수 분리)
- [ ] 문서화 (README, 주석)

### 2.3 위험 누락 (놓치면 큰일)
- [ ] **Look-ahead bias** (백테스트)
- [ ] **Off-by-one errors** (시간/인덱스)
- [ ] **Race conditions** (동시성)
- [ ] **Resource leaks** (메모리, 연결)

---

## 🔄 Step 3: Self-Correction (내가 짠 코드 검토)

### 3.1 기본 체크
- [ ] Placeholder 없는가? (`pass`, `# TODO`)
- [ ] 하드코딩 없는가? (날짜, 경로, 매직 넘버)
- [ ] 비효율적인 로직 없는가? (Loop 대신 Vectorization?)

### 3.2 정확성 체크 (L3/L4)
- [ ] **논리적 오류** 없는가? (조건, 경계값)
- [ ] **시간순서** 맞는가? (t vs t+1)
- [ ] **단위** 일관적인가? (bps vs %, USD vs BTC)
- [ ] **부호** 맞는가? (long/short, buy/sell)

### 3.3 성능 체크 (L3/L4)
- [ ] Look-ahead bias 없는가?
- [ ] 메모리 효율적인가?
- [ ] 불필요한 연산 없는가?

---

## 🎯 Step 4: Proactive Thinking (다음 스텝 제안)

- [ ] 이 작업이 끝나면 **논리적으로 다음에 할 것**은?
- [ ] 사용자가 **놓친 리스크**는?
- [ ] **더 나은 방법**이 있는가?
- [ ] **검증 방법**은 무엇인가?

---

## ✅ Step 5: Pre-Execution Verification (실행 전 검증) ⭐ NEW

**L3/L4 작업에서 MANDATORY:**

### 5.1 Logic Verification (논리 검증)
```
Q: 이 접근법이 맞는가?
- 가정 A가 참이면 → 결론 B가 따라오는가?
- 예외 케이스는?
- 반례가 있는가?
```

### 5.2 Assumption Surfacing (가정 명시)
```
⚠️ 이 코드/분석의 암묵적 가정:
1. [가정 1] - 검증 필요: Yes/No
2. [가정 2] - 검증 필요: Yes/No
3. [가정 3] - 검증 필요: Yes/No
```

### 5.3 Edge Case Analysis
```
테스트할 경계값:
- 빈 데이터셋
- 단일 행
- 최대/최소값
- None/NaN
- 동시 발생 (tie-breaking)
```

### 5.4 Confidence Assessment
```
확신 레벨: High / Medium / Low
- High: 즉시 실행
- Medium: 사용자에게 가정 확인 후 실행
- Low: 먼저 검증 실험 → 본 실행
```

---

## 🧠 Deep Reasoning Mode (L3/L4 전용)

### When Activated

Deep Reasoning Mode가 활성화되면:

1. **문제 분해** (Decomposition)
   - 큰 문제 → 작은 부분으로 분해
   - 각 부분의 의존성 파악
   - 순서 결정

2. **다각도 검토** (Multiple Perspectives)
   - "이 접근법의 약점은?"
   - "다른 방법은 없는가?"
   - "내가 틀렸다면 어디서?"

3. **명시적 추론** (Explicit Reasoning)
   - 결론에 도달한 과정을 명시
   - 각 단계의 근거 제시
   - 불확실한 부분 표시

4. **검증 계획** (Verification Plan)
   - 어떻게 이 결과가 맞는지 확인할 것인가?
   - 실패 시 어떻게 알 수 있는가?
   - 롤백 계획은?

### Output Format (Deep Reasoning)

```markdown
## 🧠 Deep Reasoning

### Problem Decomposition
1. [하위 문제 1]
2. [하위 문제 2]
3. [하위 문제 3]

### Assumptions (명시적 가정)
- A1: [가정] - 근거: [왜 이 가정이 합리적인가]
- A2: [가정] - 근거: [...]

### Approach Analysis
| Option | Pros | Cons | Risk |
|--------|------|------|------|
| A | ... | ... | ... |
| B | ... | ... | ... |

**Selected**: Option A
**Rationale**: [왜 이 옵션을 선택했는가]

### Verification Plan
- [ ] [검증 방법 1]
- [ ] [검증 방법 2]

### Confidence: [High/Medium/Low]
- [불확실한 부분이 있다면 명시]
```

---

## 🚫 Anti-Patterns (Deep Reasoning 방해 요소)

### ❌ 하지 말 것

1. **성급한 결론**
   - "당연히 A가 맞지" (검증 없이)
   - 첫 번째 아이디어에 고착

2. **가정 은폐**
   - 암묵적 가정을 명시하지 않음
   - "모두가 알겠지" 사고방식

3. **표면적 분석**
   - 1차 효과만 고려
   - 2차/3차 효과 무시

4. **과신**
   - "확실해" (불확실성 인정 안 함)
   - 검증 단계 생략

### ✅ 해야 할 것

1. **의심 먼저**
   - "이게 정말 맞나?"
   - "내가 놓친 게 있나?"

2. **가정 명시**
   - 모든 가정을 드러내기
   - 각 가정의 위험도 평가

3. **다각도 검토**
   - 반대 의견 고려
   - 최악의 시나리오

4. **불확실성 인정**
   - 확신 레벨 명시
   - 추가 검증 필요 부분 표시

---

## 📋 Quick Reference: Complexity → Reasoning Depth

| 요청 유형 | 복잡도 | 사고 깊이 |
|----------|--------|----------|
| "이 typo 고쳐" | L1 | 즉시 실행 |
| "함수 하나 추가해" | L2 | 표준 프로토콜 |
| "백테스트 돌려" | L3 | Deep Reasoning |
| "아키텍처 설계해" | L3 | Deep Reasoning |
| "실거래 연동해" | L4 | 최대 검증 + 승인 |
| "DB 스키마 변경해" | L4 | 최대 검증 + 백업 |

---

**Last Updated**: 2025-12-25
**Version**: 2.0 (Deep Reasoning Mode Added)
