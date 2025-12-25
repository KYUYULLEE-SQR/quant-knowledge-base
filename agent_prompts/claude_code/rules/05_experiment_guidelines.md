# 🧪 Experiment & Research Guidelines

## 0) Purpose
**Not "plausible backtests" but reproducible decision-making (deploy/shelve/discard).**

Experiment = *(hypothesis → implementation → validation → falsification → decision)*

---

## 1) Hard Rules (절대 규칙)

### 1.1 No Look-Ahead Bias
* **Any t+1 information in t-time decision = failure**
* Common leaks: `center=True`, future ffill/bfill, label/feature timing mismatch, survivorship bias

### 1.2 Data Snooping Prevention
* **1 experiment = 1 hypothesis + 1 change**
* More tuning = overfitting, not discovery
* Changing rules after seeing results = new experiment

### 1.3 One Variable at a Time (실험 독립성)
**CRITICAL: 한 실험당 하나의 효과만 측정 가능하도록 설계**

**🎯 실험 순서 (MANDATORY):**
1. **Phase 1: Individual Effects (개별 효과)**
   - 각 변수를 **하나씩** 독립적으로 테스트
   - 다른 모든 조건 고정
   - 각 변수의 순수 효과 측정
   
2. **Phase 2: Joint Effects (결합 효과)**
   - Phase 1 완료 후에만 허용
   - 개별 효과가 확인된 변수들의 조합
   - 상호작용(interaction) 효과 분석

**순서 위반 = 실험 무효**

---

* ❌ **나쁜 예 (여러 변수 동시 변경)**:
  - "IV 필터 10% → 15% + TTE 필터 3d → 5d + 레짐 Bull → Bear 동시 변경"
  - "수수료 모델 변경 + 진입 로직 변경 + 청산 로직 변경"
  - → **무엇이 성과를 바꿨는지 알 수 없음**
  - → **Phase 1 없이 바로 Phase 2 시도 = 금지**

* ✅ **좋은 예 (Phase 1 → Phase 2 순서)**:
  
  **Phase 1 (개별 효과):**
  - **Exp A**: IV 필터 10% → 15% (다른 모든 것 고정)
  - **Exp B**: TTE 필터 3d → 5d (베이스라인에서, IV=10% 고정)
  - **Exp C**: 레짐 Bull → Bear (베이스라인에서, IV=10%, TTE=3d 고정)
  
  **Phase 1 결과:**
  - Exp A: Sharpe +0.3 ✅ (채택)
  - Exp B: Sharpe +0.1 ✅ (채택)
  - Exp C: Sharpe -0.2 ❌ (기각)
  
  **Phase 2 (결합 효과, Phase 1 완료 후):**
  - **Exp D**: IV=15% + TTE=5d (A, B 결합)
  - **분석**: Sharpe(D) vs [Sharpe(A) + Sharpe(B)]
    - 같으면: 독립 효과 (interaction 없음)
    - 다르면: 상호작용 효과 (synergy or interference)

* ✅ **Grid Search (Phase 1 대체 가능)**:
  - 모든 파라미터 조합 테스트 (N×M 실험)
  - **반드시 각 차원별 marginal effect 분석 포함**
  - **상호작용(interaction) 있으면 명시적으로 보고**
  - Grid Search 완료 = Phase 1 완료로 간주

**실험 설계 시 체크리스트:**
1. ⚠️ 이번 실험에서 **단 하나의 변수**만 바뀌었는가?
2. ⚠️ 다른 모든 조건은 **이전 실험과 동일**한가?
3. ⚠️ 베이스라인(비교 대상)이 **명확**한가?
4. ⚠️ 결과 차이를 **이 변수 하나로 설명** 가능한가?

**위반 시 조치:**
- 실험 결과 무효 처리
- 변수 분리하여 재설계
- 각 변수당 독립 실험 수행

### 1.4 Reproducibility Obligation
* Must include: code version, data version, config, seed, command, output paths
* "Somehow it will reproduce" is prohibited

---

## 2) Agent Behavior (Anti-Passive Mode)

### 🚀 AUTONOMOUS EXECUTION (절대 원칙)

**NEVER ask "Should I run this?" or "Shall I execute?"**

* **When user says "experiment", "test", "try", "analyze":**
  - ✅ Design experiment → Write code → **EXECUTE IMMEDIATELY** → Report results
  - ❌ Design experiment → Write code → Ask permission → Wait
  
* **Default behavior:**
  - Run baseline (2+ variants)
  - Run main experiment (3-5 parameter settings)
  - Run falsification tests (shift/placebo/permutation)
  - **ALL WITHOUT ASKING**

* **Only ask when:**
  - Destructive operation (delete data, overwrite important files)
  - Financial cost involved (API calls with billing)
  - Computation takes >30 minutes (then inform + run in background)

### 🔄 Iterative Experimentation

* **Don't stop at first result**
  - Run 3-5 parameter variations automatically
  - Test edge cases (min/max values)
  - Compare multiple baselines
  - Always run falsification tests

* **When stuck >10min**: Present "3 causes + 3 experiments" and **EXECUTE ALL 3**
* **When results good**: **AUTOMATICALLY** perform breaking experiments (stress/placebo/permutation)
* **Default**: (1) Run 2+ baselines → (2) Run main → (3) Run falsification → (4) Report all together

---

## 3) Experiment Workflow

### Step A. Experiment Card (Brief but Mandatory)

**반드시 명시:**
- **Hypothesis**: "X improves Y" (구체적으로)
- **Isolated Variable**: 이번 실험에서 **유일하게** 바뀌는 변수
- **Control Group (Baseline)**: 비교 대상 (이전 최적 설정 or 표준 설정)
- **Expected Signal**: 어떤 지표가 얼마나 개선될 것인가?
- **Failure Condition**: 어떤 결과가 나오면 기각하는가?

**예시:**
```
Hypothesis: IV 과대평가 필터를 15%로 올리면 거짓 신호 감소 → Sharpe 개선
Isolated Variable: IV filter threshold (10% → 15%)
Control Group: 현재 운영중인 10% 설정 (모든 다른 파라미터 동일)
Expected Signal: Sharpe +0.3 이상, 거래 빈도 -20% 이내
Failure Condition: Sharpe 변화 없거나, 거래 빈도 -50% 이상
```

**금지 사항:**
- ❌ "여러 가지 개선 사항 테스트"
- ❌ "전반적인 성능 향상"
- ❌ "파라미터 튜닝"
→ **변수가 2개 이상이면 실험을 분리하라**

### Step B. Fix Data/Universe
- Fix: period/costs/slippage/fill/leverage/rebalancing
- Prevent: survivorship, corporate actions, timezone issues

### Step C. Baseline (≥2) + Ablation (≥1)

**목적: 성과가 추가된 변수 때문인지 증명**

* **Baseline 필수 구성**:
  1. **Control (이전 최적 설정)**: 이번 실험의 유일한 변수만 이전 값으로
  2. **Simple Benchmark**: 단순 전략 (buy-and-hold, moving average crossover, random)
  3. **Do Nothing**: 아무것도 안 하는 경우 (거래 비용 zero baseline)

* **Ablation (제거 실험)**:
  - 새로 추가한 변수를 **완전히 제거**한 버전
  - "이 변수가 없으면 어떻게 되는가?"
  - 예: IV 필터 추가 실험 → IV 필터 완전 제거 버전도 테스트

**실험 구조 예시:**
```
Control:      IV filter = 10%, TTE = 3d, Regime = Bull  [기존 설정]
Experiment:   IV filter = 15%, TTE = 3d, Regime = Bull  [단 하나만 변경]
Ablation:     No IV filter,    TTE = 3d, Regime = Bull  [변수 완전 제거]
Simple:       Buy when price > SMA(20)                   [단순 벤치마크]
```

**보고 시 필수:**
- Control vs Experiment: 순수 변수 효과
- Experiment vs Ablation: 변수 존재 가치
- Experiment vs Simple: 복잡도 대비 개선

### Step D. Validation: Walk-forward + Purge/Embargo
- Fixed time split (train→test)
- Consider purged k-fold
- "Survives by sub-period" > "works full period"

### Step E. Robustness Battery
- Cost sensitivity: 0.5×, 1×, 2× fees/slippage
- Fill sensitivity: mid, bid/ask, adverse
- Parameter stability: nearby values
- Resampling: monthly/quarterly bootstrap
- Placebo: signal shift, label randomization

### Step F. Operational Checklist
- Max DD, DD duration
- Tail: worst 1% day/week, CVaR/ES
- Position sizing/margin risk
- Operational complexity vs profit

---

## 4) Complexity Management
**Complexity = cost. Deduct from performance.**

- Similar performance → choose simpler
- Slightly better + much complex → shelve/reject
- "Simple" = structure that hits core, not just fewer rules

---

## 5) Standard Deliverables (Always Leave)

**모든 실험 종료 시 반드시 포함:**

### 5.1 Experiment Summary Table
```
Variant         | Sharpe | Max DD | Total Trades | Win Rate | Variable Changed
----------------|--------|--------|--------------|----------|------------------
Control (10%)   |  1.85  | -12.3% |     127      |   58.3%  | [baseline]
Experiment(15%) |  2.12  | -10.1% |      98      |   61.2%  | IV filter: 10→15%
Ablation (none) |  1.42  | -18.7% |     203      |   52.1%  | IV filter removed
Simple (SMA)    |  0.87  | -25.3% |      45      |   51.1%  | [benchmark]
```

### 5.2 Isolated Effect Analysis
**"이 변수 하나가 미친 영향"을 명확히:**
```
Variable: IV filter threshold (10% → 15%)
Effect:
  - Sharpe: +0.27 (1.85 → 2.12, +14.6%)
  - MaxDD: +2.2% (개선)
  - Trades: -29 (-22.8%, 신호 품질 ↑)
  - Win Rate: +2.9%

Conclusion: IV 필터 강화가 거짓 신호 제거에 효과적
```

### 5.3 Decision
- **Deploy**: 즉시 운영 반영
- **Shelve**: 유보 (다른 조건에서 재검증 필요)
- **Discard**: 기각 (효과 없음 or 부작용 큼)

### 5.4 Evidence
- 3 key metrics + sub-period breakdown
- 최소 2개 이상 기간에서 일관성 확인

### 5.5 Risks
- Worst period/tail/failure modes
- 어떤 시장 조건에서 실패하는가

### 5.6 Leak/Bug Check
- Placebo/shift/random label 결과
- 통계적 유의성 검증 (p-value, permutation test)

### 5.7 Next Action
**단일 변수 실험 체인:**
```
Completed: IV filter optimization (10% → 15%) ✅
Next:
  1. TTE filter (3d → 5d, IV=15% 고정)
  2. Regime filter (Bull only → Bull+Sideways, IV=15%, TTE=최적값 고정)
  3. Position sizing (3% → 5% NAV, 모든 파라미터 최적값 고정)
```

**절대 금지:**
- ❌ "다음: 여러 파라미터 동시 최적화"
- ❌ "다음: 전반적인 성능 개선"
→ **항상 다음 실험도 단일 변수**

---

## 6) Proactive Experimentation

**When experimenting:**
- Don't stop after 1-2 trials
- Explore multiple parameter ranges
- Test edge cases systematically
- Report comprehensively with all findings
- Suggest next experiments based on results

