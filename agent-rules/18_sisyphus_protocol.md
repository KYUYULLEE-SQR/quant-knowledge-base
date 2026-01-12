# APPLY_ALWAYS
# LOAD ORDER: 3 (After baksa_verification)
# Sisyphus Protocol - Never Give Up, Auto-Retry, Complete Everything

---

# 🔄 Sisyphus Protocol (끊임없이 완료하기)

## 🎯 Core Philosophy

**"실패해도 포기하지 않는다. 완료될 때까지 계속한다."**

Sisyphus는 그리스 신화에서 영원히 바위를 굴리는 인물.
이 프로토콜은 **작업이 완료될 때까지 자동으로 재시도**하는 행동 규칙.

> "에러가 났다고 멈추지 마라. 수정하고 다시 해라."
> "1개 했다고 멈추지 마라. 전부 끝날 때까지 해라."

---

## 🔁 Auto-Retry Rules (자동 재시도)

### Rule 1: 에러 발생 시 자동 수정

```
에러 감지
    ↓
[1] 에러 메시지 분석
    ↓
[2] 원인 파악 (코드 버그? 환경? 데이터?)
    ↓
[3] 수정 적용
    ↓
[4] 재실행
    ↓
성공? → 다음 단계
실패? → 다른 접근법으로 재시도 (최대 3회)
3회 실패? → 원인 보고 + 대안 제시
```

**예시:**
```python
# 1차 시도: 에러 발생
# TypeError: 'NoneType' object is not subscriptable

# [자동 분석]: df가 None임 → 데이터 로드 실패
# [자동 수정]: 데이터 경로 확인 + 예외 처리 추가
# [재실행]: 성공
# [보고]: "데이터 경로 오류 수정 후 성공"
```

### Rule 2: 작업 미완료 시 자동 계속

```
백테스트 요청
    ↓
[1] Main experiment (3-5 variants)
    ↓ (1개 끝났다고 멈추지 않음)
[2] Baseline comparisons (2+)
    ↓ (자동 진행)
[3] Sub-period analysis (2+)
    ↓ (자동 진행)
[4] Falsification tests
    ↓ (자동 진행)
[5] Baksa verification
    ↓ (자동 진행)
[6] 종합 보고
    ↓
전체 완료!
```

### Rule 3: 세션 중단 시 상태 저장

```
작업 중 중단 (컨텍스트 한도, 사용자 종료 등)
    ↓
[자동] STATE.md 업데이트
    - Done: 완료된 항목
    - In Progress: 진행 중이던 항목
    - Next: 다음 할 것
    ↓
다음 세션에서 STATE.md 읽고 이어서
```

---

## 🚫 금지 행동 (Sisyphus Anti-Patterns)

### ❌ 절대 하지 마라

```
❌ "에러가 발생했습니다. 어떻게 할까요?"
   → 물어보지 말고 수정해서 다시 해

❌ "1개 테스트 완료했습니다. 더 할까요?"
   → 물어보지 말고 전부 다 해

❌ "ImportError 발생. 패키지를 설치할까요?"
   → 물어보지 말고 설치하고 다시 해

❌ "파일을 찾을 수 없습니다."
   → 경로 확인하고 수정해서 다시 해

❌ 에러 메시지만 보여주고 대기
   → 분석 + 수정 + 재실행까지
```

### ✅ 대신 이렇게 해라

```
✅ 에러 발생
   → "[자동 수정] ImportError → pip install 실행 → 재실행 → 성공"

✅ 1개 완료
   → "1/5 완료. 2번째 변형 실행 중..."
   → "5/5 완료. Baseline 비교 실행 중..."
   → "전체 완료. 결과 보고:"

✅ 파일 없음
   → "[자동 수정] 경로 오류 → 올바른 경로 탐색 → 재실행 → 성공"

✅ 중단됨
   → "STATE.md 업데이트 완료. 다음 세션에서 이어서 가능."
```

---

## 📊 Retry Limits (재시도 한도)

| 상황 | 최대 재시도 | 초과 시 |
|------|------------|--------|
| 같은 에러 반복 | 3회 | 다른 접근법 시도 |
| 다른 접근법 | 3가지 | 원인 분석 + 사용자 보고 |
| 환경 문제 (패키지, 권한) | 2회 | 환경 설정 가이드 제공 |
| 데이터 문제 | 2회 | 데이터 상태 보고 |

### 재시도 로그 형식

```markdown
## 🔄 Retry Log

| 시도 | 에러 | 수정 | 결과 |
|------|------|------|------|
| 1 | ImportError: pandas | pip install pandas | ✅ 해결 |
| 2 | FileNotFoundError | 경로 수정 | ✅ 해결 |
| 3 | ValueError: empty data | 데이터 확인 | ⚠️ 실제 데이터 없음 |

**최종 상태**: 데이터 파일 필요 (경로: ~/data/btc_options.csv)
```

---

## 🎯 Completion Criteria (완료 조건)

### 작업이 "완료"되려면:

**백테스트의 경우:**
- [ ] Main experiment 3-5개 변형 실행
- [ ] Baseline 2개 이상 비교
- [ ] Sub-period 2개 이상 분석
- [ ] Falsification tests 실행
- [ ] Baksa verification (Trust Score)
- [ ] 종합 보고서 생성
- [ ] 파일 저장 확인

**위 중 하나라도 미완료 → 계속 진행**

### 중단 조건 (예외)

- 사용자가 명시적으로 "중단" 요청
- 3가지 다른 접근법 모두 실패
- 환경 문제로 진행 불가 (권한, 하드웨어)

---

## 🔧 Implementation Patterns

### Pattern 1: Try-Retry-Report

```python
def sisyphus_execute(task, max_retries=3):
    for attempt in range(max_retries):
        try:
            result = execute(task)
            return result  # 성공
        except Exception as e:
            fix = analyze_and_fix(e)
            task = apply_fix(task, fix)
            # 자동으로 다음 시도

    # 3회 실패 시
    try_alternative_approaches(task)
```

### Pattern 2: Chain Execution

```python
def sisyphus_backtest(strategy):
    # 멈추지 않고 전부 실행
    results = []

    # Phase 1: Main experiments
    for variant in generate_variants(strategy, n=5):
        results.append(run_backtest(variant))

    # Phase 2: Baselines (자동 진행)
    for baseline in ['buy_hold', 'random', 'momentum']:
        results.append(run_backtest(baseline))

    # Phase 3: Sub-periods (자동 진행)
    for period in ['2024-Q3', '2024-Q4', '2022-Q2']:
        results.append(run_backtest(strategy, period))

    # Phase 4: Falsification (자동 진행)
    results.append(run_signal_shift_test(strategy))
    results.append(run_placebo_test(strategy))

    # Phase 5: Report (전체 완료 후)
    return generate_comprehensive_report(results)
```

### Pattern 3: State Persistence

```python
def sisyphus_with_state(task):
    state = load_state("STATE.md")

    if state.in_progress:
        task = resume_from(state.in_progress)

    try:
        result = sisyphus_execute(task)
        update_state(state, done=task)
    except Interrupted:
        update_state(state, in_progress=task)
        raise

    return result
```

---

## 📋 Self-Check: Sisyphus Compliance

**응답 보내기 전 체크:**

```
□ 에러 발생했는데 수정 안 하고 물어봤나? → 금지
□ 1개만 하고 "더 할까요?" 물어봤나? → 금지
□ 중단됐는데 STATE.md 안 썼나? → 금지
□ 재시도 안 하고 바로 포기했나? → 금지
```

**하나라도 Yes → 수정 후 재응답**

---

## 🎯 Good vs Bad Examples

### 에러 처리

**❌ Bad (포기):**
```
FileNotFoundError: ~/data/btc.csv not found
이 파일이 필요합니다. 확인해주세요.
```

**✅ Good (Sisyphus):**
```
FileNotFoundError 발생 → 자동 수정 중...

[탐색] ~/data/ 디렉토리 확인
[발견] btc_options.csv 존재 (btc.csv 아님)
[수정] 파일명 수정
[재실행] 성공

결과:
| Metric | Value |
...
```

### 작업 범위

**❌ Bad (멈춤):**
```
백테스트 1개 완료.
Sharpe: 2.4

다른 파라미터도 테스트할까요?
```

**✅ Good (Sisyphus):**
```
백테스트 진행 중... (1/12)

[완료] Main variant 1: Sharpe 2.4
[진행] Main variant 2: 실행 중...
[진행] Main variant 3: 대기
...
[완료] Falsification: Signal shift 통과

## 종합 결과 (12/12 완료)

| Variant | Sharpe | MDD | Note |
|---------|--------|-----|------|
| Main 1  | 2.4    | -8% | Best |
| Main 2  | 2.1    | -9% | |
...

Files: ~/experiments/2025-01-11_*/
```

---

## 🔗 Integration with Other Rules

| 규칙 | Sisyphus 연동 |
|------|--------------|
| `00_output_enforcement` | 완료될 때까지 출력 보류 가능 |
| `05_experiment_guidelines` | Phase 1→2 자동 진행 |
| `17_baksa_verification` | 백테스트 후 자동 검증 |
| `12_project_state_protocol` | STATE.md 자동 업데이트 |

---

**Last Updated**: 2025-01-11
**Version**: 1.0 (Sisyphus Protocol - Never Give Up)
**Inspiration**: oh-my-claude-sisyphus by Yeachan-Heo
