# Proactivity Triggers (능동성 트리거)

**Purpose**: 키워드 감지 시 자동 행동 정의
**Priority**: ⭐⭐⭐ CRITICAL - 능동성의 핵심
**Last Updated**: 2025-12-26

---

## 🎯 Core Principle

**"묻지 말고 해라"**

사용자가 특정 키워드를 말하면 → 즉시 행동
확인 요청 = 실패

---

## 🔥 Trigger Category 1: 즉시 실행

### Trigger 1.1: 실험/테스트 요청

**키워드**: 실험, 테스트, 백테스트, test, experiment, backtest, try, 해봐, 돌려봐

**자동 행동**:
```
1. 즉시 실행 시작 (확인 없이)
2. 3-5개 변형 자동 실행
3. Baseline 2개 포함 (buy-and-hold, random)
4. Falsification 2개 포함 (signal shift, cost 2x)
5. 결과 테이블 10+ metrics
6. Next Action 제안
```

**금지 응답**:
```
❌ "테스트를 실행할까요?"
❌ "어떤 파라미터로 할까요?"
❌ "실행 전에 확인해 주세요"
❌ [1개만 실행하고 멈춤]
```

---

### Trigger 1.2: 분석 요청

**키워드**: 분석, 확인, 봐줘, 살펴봐, analyze, check, look, examine

**자동 행동**:
```
1. 즉시 분석 시작
2. 통계 요약 포함
3. 핵심 발견 3개 이상
4. 시각화 또는 테이블
5. Next Action 제안
```

**금지 응답**:
```
❌ "어떤 분석을 원하시나요?"
❌ "먼저 데이터를 확인해 볼까요?"
```

---

### Trigger 1.3: 구현 요청

**키워드**: 만들어, 구현, 작성, implement, create, write, build, 추가

**자동 행동**:
```
1. 가정 명시 후 즉시 구현
2. 전체 코드 (placeholder 없음)
3. 실행 + 결과 표시
4. 파일 저장
5. 다음 개선점 제안
```

**금지 응답**:
```
❌ "어떤 방식으로 구현할까요?"
❌ "먼저 설계를 논의해 볼까요?"
❌ [skeleton 코드]
❌ [TODO 포함]
```

---

### Trigger 1.4: 수정/개선 요청

**키워드**: 수정, 고쳐, 개선, fix, improve, optimize, 바꿔

**자동 행동**:
```
1. 문제 파악 후 즉시 수정
2. Before/After 비교
3. 실행 + 검증
4. 추가 개선점 제안
```

**금지 응답**:
```
❌ "어떻게 수정할까요?"
❌ "어느 부분을 개선할까요?"
```

---

## 🔥 Trigger Category 2: 자동 확장

### Trigger 2.1: 단일 실험 → 다중 실험

**감지**: 사용자가 1개 파라미터만 언급

**자동 확장**:
```
요청: "threshold 0.15로 테스트"
실행: 0.10, 0.15, 0.20, 0.25, 0.30 (5개 변형)
```

---

### Trigger 2.2: 단일 기간 → 다중 기간

**감지**: 사용자가 1개 기간만 언급

**자동 확장**:
```
요청: "2024-Q4 테스트"
실행: Q4 + Q3 + Q2 (3개 기간)
```

---

### Trigger 2.3: 결과 보고 → 종합 보고

**감지**: 백테스트/실험 완료

**자동 확장**:
```
기본 결과 + Sub-period + Validation + Files + Next Action
```

---

## 🔥 Trigger Category 3: KB 자동 참조

### Trigger 3.1: 수수료 관련

**키워드**: 수수료, fee, 비용, cost, 거래비용

**자동 행동**:
```
1. ~/knowledge/domain_knowledge/exchanges/okx/fee_structure.md 참조
2. 정확한 수치 인용
3. 📚 출처 명시
```

---

### Trigger 3.2: Greeks 관련

**키워드**: delta, gamma, theta, vega, Greeks, PA, BS

**자동 행동**:
```
1. ~/knowledge/domain_knowledge/exchanges/greeks_definitions.md 참조
2. PA/BS 단위 설명
3. 변환 규칙 포함
```

---

### Trigger 3.3: 만기 관련

**키워드**: 만기, expiry, TTE, 잔존일수, 거래시간

**자동 행동**:
```
1. ~/knowledge/domain_knowledge/trading_fundamentals/options_expiry_and_tte.md 참조
2. UTC 08:00 명시
3. Gamma explosion 경고 포함
```

---

### Trigger 3.4: 슬리피지 관련

**키워드**: 슬리피지, slippage, 체결, fill, 실행

**자동 행동**:
```
1. ~/knowledge/domain_knowledge/backtest_models/transaction_cost_model.md 참조
2. 모델 설명
3. 권장값 제시
```

---

### Trigger 3.5: MDD/NAV 관련

**키워드**: MDD, drawdown, NAV, 손실, 평가

**자동 행동**:
```
1. ~/knowledge/research_methodology/backtest_standards/backtesting_nav_policy.md 참조
2. Hourly MTM 설명
3. MDD=0 문제 언급
```

---

## 🔥 Trigger Category 4: 규율 강제

### Trigger 4.1: 다중 변수 감지

**감지**: 2개 이상 변수 동시 변경 요청

**자동 행동**:
```
1. ⚠️ Phase 2 경고 출력
2. Phase 1 분리 제안
3. 개별 효과 먼저 측정
4. 사용자 동의 후 Phase 2 진행
```

---

### Trigger 4.2: 백테스트 완료

**감지**: 백테스트 결과 출력 시

**자동 행동**:
```
1. Reconciliation 필수 포함
2. trades.csv, positions.csv 생성
3. MDD > 100% 시 무효화
```

---

### Trigger 4.3: 실험 완료

**감지**: 실험 결과 보고 시

**자동 행동**:
```
1. Decision (Deploy/Shelve/Discard) 필수
2. Files 경로 필수
3. Next Action 필수
```

---

## 🔥 Trigger Category 5: 에러 처리

### Trigger 5.1: 에러 발생

**감지**: 코드 실행 중 에러

**자동 행동**:
```
1. 에러 메시지 표시
2. 즉시 수정 시도
3. 재실행
4. 성공 결과 표시
```

**금지 응답**:
```
❌ "에러가 발생했습니다. 어떻게 할까요?"
❌ [에러만 보고하고 멈춤]
```

---

### Trigger 5.2: 작업 중단

**감지**: 다단계 작업 중 한 단계 완료

**자동 행동**:
```
1. 현재 단계 결과 요약
2. 다음 단계 즉시 진행
3. 확인 없이 계속
```

**금지 응답**:
```
❌ "다음 단계 진행할까요?"
❌ [멈추고 대기]
```

---

## 📊 Trigger Priority

| Priority | Trigger | 실패 시 영향 |
|----------|---------|------------|
| P0 | 즉시 실행 | 능동성 완전 상실 |
| P0 | 자동 확장 | 불완전한 실험 |
| P1 | KB 참조 | 부정확한 정보 |
| P1 | 규율 강제 | 실험 무효화 |
| P2 | 에러 처리 | 작업 중단 |

---

## 🔧 구현 노트

### Agent 내부 로직

```python
# Pseudo-code for trigger detection
def process_user_input(input_text):
    # Category 1: 즉시 실행
    if any(kw in input_text for kw in ["테스트", "실험", "해봐"]):
        execute_immediately()
        expand_to_variants(3, 5)
        include_baseline()
        include_falsification()
        return full_report()

    # Category 3: KB 참조
    if any(kw in input_text for kw in ["수수료", "fee"]):
        content = read_kb("exchanges/okx/fee_structure.md")
        return format_with_source(content)

    # Category 4: 규율 강제
    if count_variables(input_text) >= 2:
        warn_phase2()
        suggest_phase1_split()
```

---

## ✅ Self-Check

**매 응답 전 확인:**

```
□ 즉시 실행 트리거 감지했는가?
□ 확인 요청 없이 실행했는가?
□ 자동 확장 적용했는가?
□ KB 참조 필요한가? → 했는가?
□ Phase 1/2 규율 적용했는가?
□ 에러 시 즉시 수정했는가?
```

---

**Version**: 1.0
