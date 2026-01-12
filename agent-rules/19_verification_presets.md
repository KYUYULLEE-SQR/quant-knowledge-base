# APPLY_ALWAYS
# LOAD ORDER: 4 (After sisyphus_protocol)
# Verification Presets - 자주 쓰는 검증 커맨드 프리셋

---

# 🎯 Verification Presets (검증 프리셋)

## 📌 Purpose

**자주 쓰는 "잔소리"를 키워드로 자동 발동**

사용자가 특정 키워드 말하면 → 해당 검증 모드 자동 활성화

---

## 🔑 Preset Keywords (트리거 키워드)

### Preset 1: `정합성` / `integrity` / `정합하게`

**발동 조건**: 사용자가 "정합성", "정합하게", "integrity" 언급

**자동 실행 체크리스트**:

```markdown
## 🔬 Integrity Verification Mode 활성화

### 옵션 백테스트 정합성 (Options Backtest Integrity)

□ **진입 타이밍 (Entry Timing)**
  - 시그널 시점 < 진입 시점? (signal.shift(1))
  - 장 마감 후 시그널 → 다음 날 진입?
  - 체결 가격 = 의도한 가격? (mid/bid/ask)

□ **포지션 정합성 (Position Integrity)**
  - 의도한 수량 = 실제 수량?
  - Long/Short 방향 맞는가?
  - 복수 레그 → 모든 레그 동시 체결?

□ **추가 진입 (Scaling In/Out)**
  - 기존 포지션 + 신규 = 합계 맞는가?
  - 평균 단가 재계산 정확한가?
  - 포지션 사이즈 한도 준수?

□ **만기 정산 (Expiry Settlement)**
  - Settlement price = Index price at expiry?
  - ITM → auto-exercise 처리?
  - OTM → expire worthless 처리?
  - Settlement time = 08:00 UTC (OKX)?

□ **PnL 정합성 (PnL Reconciliation)**
  - Realized PnL = 청산가 - 진입가 (×수량) - 수수료?
  - Unrealized PnL = Mark price - 진입가?
  - Total PnL = Realized + Unrealized?
  - Cash flow = trade amounts + fees?

□ **포지션 연속성 (Position Continuity)**
  - position[t] = position[t-1] + trades[t]?
  - 고아 청산 없는가? (없는 포지션 청산 시도)
  - 과다 청산 없는가? (보유량 초과 청산)
```

**출력 형식**:
```
🔬 Integrity Check Results

| 항목 | 상태 | 세부사항 |
|------|------|----------|
| Entry Timing | ✅/❌ | [상세] |
| Position | ✅/❌ | [상세] |
| Scaling | ✅/❌ | [상세] |
| Settlement | ✅/❌ | [상세] |
| PnL | ✅/❌ | [상세] |
| Continuity | ✅/❌ | [상세] |

Overall: ✅ PASS / ❌ FAIL (N/6 passed)
```

---

### Preset 2: `엄밀하게` / `rigorous` / `깐깐하게`

**발동 조건**: 사용자가 "엄밀하게", "rigorous", "깐깐하게", "꼼꼼하게" 언급

**자동 실행**:

```markdown
## 🔍 Rigorous Mode 활성화

**추가 검증 항목**:

□ **통계적 유의성**
  - Bootstrap 95% CI 계산
  - Effect size vs baseline
  - p-value (if applicable)
  - Sample size 충분? (n > 30 trades)

□ **엣지 케이스**
  - 빈 데이터셋 처리?
  - 단일 거래 케이스?
  - 동시 시그널 (tie-breaking)?
  - 최대/최소값 경계?

□ **가정 명시**
  - 암묵적 가정 모두 나열
  - 각 가정의 위험도 평가
  - 가정 위반 시 영향

□ **대안 검토**
  - 다른 접근법 비교했는가?
  - 왜 이 방법 선택했는가?
  - Trade-off 명시

□ **재현성**
  - Random seed 고정?
  - 환경 의존성 없는가?
  - 동일 입력 → 동일 출력?
```

---

### Preset 3: `객관적으로` / `objective` / `편향없이`

**발동 조건**: 사용자가 "객관적으로", "objective", "편향없이" 언급

**자동 실행**:

```markdown
## ⚖️ Objective Mode 활성화

**편향 제거 체크**:

□ **Confirmation Bias 방지**
  - 가설 지지 데이터만 선별하지 않았는가?
  - 반대 증거도 동등하게 보고
  - "좋은 결과" 과장 금지

□ **Look-ahead Bias**
  - 미래 정보 사용 없음 확인
  - Train/Test 완전 분리
  - Parameter tuning on test set 금지

□ **Survivorship Bias**
  - 상장폐지/실패 케이스 포함?
  - 현재 존재하는 것만 분석하지 않았는가?

□ **Selection Bias**
  - 기간 선택 편향?
  - 좋은 기간만 보여주지 않았는가?
  - Multiple sub-periods 검증

□ **양면 보고**
  - 장점만 아니라 단점도
  - Best case + Worst case
  - 리스크 정량화
```

---

### Preset 4: `이상한거` / `anomaly` / `버그찾아` / `뭔가이상`

**발동 조건**: 사용자가 "이상한거", "anomaly", "버그", "뭔가이상" 언급

**자동 실행**:

```markdown
## 🐛 Anomaly Detection Mode 활성화

**이상 징후 스캔**:

□ **결과 이상**
  - Sharpe > 5 → 🚨 Look-ahead bias?
  - 승률 > 70% → 🚨 미래 참조?
  - MDD = 0% → 🚨 뭔가 잘못됨
  - PnL 급등/급락 → 🚨 버그?

□ **데이터 이상**
  - NaN/Inf 값 존재?
  - 중복 timestamp?
  - 가격 음수/0?
  - Volume 이상치?

□ **로직 이상**
  - 같은 봉 진입+청산?
  - 포지션 부호 뒤집힘?
  - 수수료가 PnL보다 큼?
  - 레버리지 한도 초과?

□ **시간 이상**
  - 주말/휴일 거래?
  - 미래 날짜 데이터?
  - 시간순 아님?
  - 갭 존재?

□ **Greeks 이상 (옵션)**
  - Delta > 1 or < -1?
  - IV 음수?
  - Theta 양수? (long option)
  - Gamma 음수?
```

---

### Preset 5: `데이터체크` / `data check` / `데이터확인`

**발동 조건**: 사용자가 "데이터체크", "data check", "데이터확인", "데이터 이상" 언급

**자동 실행**:

```markdown
## 📊 Data Validation Mode 활성화

**데이터 품질 검증**:

□ **기본 검증**
  - Shape: (rows, cols)
  - Date range: start ~ end
  - Missing values: count per column
  - Duplicates: count

□ **가격 검증**
  - OHLC 관계: O/H/L/C within H-L range?
  - 음수 가격 없음?
  - 이상치 (3σ 이상)?
  - 갭 > 10% ?

□ **시간 검증**
  - Timezone 일관성?
  - 시간 간격 일정?
  - 누락 구간?
  - 미래 데이터 없음?

□ **옵션 특화**
  - Strike 유효 범위?
  - Expiry 날짜 유효?
  - IV 범위 (0.01 ~ 5.0)?
  - Greeks 부호 정상?

□ **정합성**
  - 데이터 소스 일치?
  - 기초자산 가격 일치?
  - 분봉 합계 = 일봉?
```

---

## 🔧 복합 프리셋 (Combo)

### `풀체크` / `full check` / `전체검증`

**모든 프리셋 동시 실행**:
1. 정합성 체크
2. 엄밀하게 체크
3. 객관적으로 체크
4. 이상한거 찾기
5. 데이터 체크

**출력**: 종합 보고서 (5개 섹션)

---

### `백테스트검증` / `backtest verify`

**백테스트 특화 검증**:
1. 정합성 (Integrity)
2. Look-ahead bias
3. Reconciliation
4. Cost sensitivity
5. Sub-period

---

## 📋 Quick Reference Card

| 키워드 | 모드 | 핵심 체크 |
|--------|------|----------|
| 정합성 | Integrity | 진입/포지션/만기/PnL |
| 엄밀하게 | Rigorous | 통계/엣지케이스/가정 |
| 객관적으로 | Objective | 편향 제거/양면보고 |
| 이상한거 | Anomaly | 결과/데이터/로직 이상 |
| 데이터체크 | Data | 품질/시간/가격 검증 |
| 풀체크 | All | 전체 (5개 모드) |

---

## 🎯 Options Backtest Specific (옵션 전용)

**옵션 백테스트에서 특히 중요한 체크**:

### 1. Entry Timing (진입 시점)
```python
# ❌ 잘못된 예
signal_time = "2024-01-01 09:00"
entry_time = "2024-01-01 09:00"  # 같은 시간 = 불가능

# ✅ 올바른 예
signal_time = "2024-01-01 09:00"
entry_time = "2024-01-01 09:15"  # 시그널 후 다음 봉 진입
```

### 2. Position Intent (포지션 의도)
```python
# 체크: 의도한 수량 = 실제 수량
intended_qty = 10
actual_qty = len(positions[positions['symbol'] == option])

assert intended_qty == actual_qty, f"Mismatch: {intended_qty} vs {actual_qty}"
```

### 3. Scaling (추가 진입)
```python
# 체크: 누적 포지션 정확
initial = 5
added = 3
expected_total = 8
actual_total = positions['quantity'].sum()

assert expected_total == actual_total, f"Scale mismatch"
```

### 4. Settlement (만기 정산)
```python
# OKX Options: 08:00 UTC settlement
settlement_time = "08:00 UTC"
settlement_price = index_price_at_expiry  # NOT last trade price

# ITM: auto-exercise
if option_type == 'call' and index_price > strike:
    pnl = (index_price - strike) * qty
elif option_type == 'put' and index_price < strike:
    pnl = (strike - index_price) * qty
else:
    pnl = -premium_paid  # OTM: expire worthless
```

### 5. Greeks Tracking
```python
# 매 시점 Greeks 기록
greeks_log = {
    'timestamp': [],
    'delta': [],
    'gamma': [],
    'theta': [],
    'vega': [],
    'iv': []
}

# Theta decay 누적
total_theta_decay = sum(greeks_log['theta'])
```

---

## 🚨 자동 경고 트리거

**결과에서 자동 감지 → 경고**:

```python
# Anomaly auto-detection
if sharpe > 5.0:
    print("🚨 Sharpe > 5 → Look-ahead bias 의심")

if win_rate > 0.70:
    print("🚨 승률 > 70% → 미래 참조 의심")

if max_dd == 0:
    print("🚨 MDD = 0% → 코드 버그 의심")

if any(position < 0) and not allow_short:
    print("🚨 음수 포지션 → 로직 버그")
```

---

## 📝 Usage Examples

### Example 1: 정합성 체크 요청
```
User: "이 백테스트 정합성 확인해줘"

Agent: [Integrity Mode 활성화]

       🔬 Integrity Check Results

       | 항목 | 상태 | 세부사항 |
       |------|------|----------|
       | Entry Timing | ✅ | signal.shift(1) 적용됨 |
       | Position | ✅ | 의도 수량 = 실제 수량 |
       | Scaling | ✅ | 누적 포지션 정확 |
       | Settlement | ❌ | ITM 만기 처리 누락! |
       | PnL | ✅ | Realized + Unrealized = Total |
       | Continuity | ✅ | 고아 거래 없음 |

       Overall: ❌ FAIL (5/6 passed)

       Issue: ITM 옵션 만기 시 auto-exercise 로직 누락
       Fix: [수정 코드 제시]
```

### Example 2: 풀체크 요청
```
User: "풀체크 해줘"

Agent: [All Modes 활성화]

       ## 1. 🔬 Integrity: 6/6 ✅
       ## 2. 🔍 Rigorous: 4/5 ⚠️ (CI 미계산)
       ## 3. ⚖️ Objective: 5/5 ✅
       ## 4. 🐛 Anomaly: 0 issues ✅
       ## 5. 📊 Data: 4/5 ⚠️ (3개 NaN)

       Overall: 19/26 checks passed

       Action Items:
       1. Bootstrap CI 계산 추가
       2. NaN 3건 처리 (fillna or dropna)
```

---

**Last Updated**: 2025-01-11
**Version**: 1.0 (Verification Presets)
