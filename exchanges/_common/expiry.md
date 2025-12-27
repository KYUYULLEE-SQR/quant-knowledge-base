# Options Expiry Conventions (옵션 만기 약자 체계)

**Purpose**: 옵션 만기 약자 (D, W, M, SM, Q 등) 정확한 의미와 계산법

**Last Updated**: 2025-12-23
**Owner**: sqr
**Scope**: OKX, Deribit 암호화폐 옵션 거래소

---

## 🚨 Critical: SM ≠ Saturday Monthly

**❌ 절대 금지**:
- SM = "Saturday Monthly" ← **완전히 틀림**
- SM = "Some Month" ← 의미 없음

**✅ 정답**:
- SM = **Second Month** (2개월 후 만기)

---

## 📅 만기 약자 체계 (전체)

### 일간 (Daily)

| 약자 | 영문 | 만기 | 예시 (오늘: 2025-12-23) |
|------|------|------|-------------------------|
| **D** | Daily | 다음 영업일 | 2025-12-24 |
| **1D** | 1 Day | 1일 후 | 2025-12-24 |
| **2D** | 2 Days | 2일 후 | 2025-12-25 |

**만기 시각**: UTC 08:00 (KST 17:00)

---

### 주간 (Weekly)

| 약자 | 영문 | 만기 | 예시 (오늘: 2025-12-23 화요일) |
|------|------|------|-------------------------------|
| **W** | Weekly | 이번 주 금요일 | 2025-12-26 (금) |
| **1W** | 1 Week | 다음 주 금요일 | 2026-01-02 (금) |
| **2W** | 2 Weeks | 2주 후 금요일 | 2026-01-09 (금) |
| **3W** | 3 Weeks | 3주 후 금요일 | 2026-01-16 (금) |
| **4W** | 4 Weeks | 4주 후 금요일 | 2026-01-23 (금) |

**만기 시각**: UTC 08:00 (KST 17:00)
**요일**: 항상 금요일 (Friday)

**계산법**:
```python
from datetime import datetime, timedelta

def get_weekly_expiry(weeks_ahead: int = 0):
    """
    주간 옵션 만기일 계산

    weeks_ahead: 0 = 이번주, 1 = 다음주, 2 = 2주후...
    """
    today = datetime.now()
    days_until_friday = (4 - today.weekday()) % 7  # 4 = Friday
    if days_until_friday == 0 and today.hour >= 8:
        days_until_friday = 7  # 이미 금요일 08:00 지났으면 다음주

    expiry = today + timedelta(days=days_until_friday + weeks_ahead * 7)
    return expiry.replace(hour=8, minute=0, second=0, microsecond=0)

# 예시
W_expiry = get_weekly_expiry(0)   # 이번주 금요일
W1_expiry = get_weekly_expiry(1)  # 다음주 금요일
W2_expiry = get_weekly_expiry(2)  # 2주 후 금요일
```

---

### 월간 (Monthly)

| 약자 | 영문 | 만기 | 예시 (오늘: 2025-12-23) |
|------|------|------|------------------------|
| **M** | Monthly | 가장 가까운 월간 만기 | 2025-12-26 (12월 마지막 금) |
| **FM** | Front Month | 가장 가까운 월간 만기 (= M) | 2025-12-26 (12월 마지막 금) |
| **SM** | **Second Month** | **FM 다음 월간 만기** | **2026-01-30 (1월 마지막 금)** |
| **TM** | Third Month | SM 다음 월간 만기 | 2026-02-27 (2월 마지막 금) |
| **1M** | 1 Month | 가장 가까운 월간 (= FM) | 2025-12-26 |
| **2M** | 2 Months | FM 다음 (= SM) | 2026-01-30 |
| **3M** | 3 Months | SM 다음 (= TM) | 2026-02-27 |

**만기 시각**: UTC 08:00 (KST 17:00)
**요일**: 항상 해당 월의 **마지막 금요일** (Last Friday of Month)

**계산법**:
```python
from datetime import datetime, timedelta
from calendar import monthrange

def get_last_friday_of_month(year: int, month: int):
    """
    해당 월의 마지막 금요일 찾기
    """
    # 해당 월의 마지막 날
    last_day = monthrange(year, month)[1]
    last_date = datetime(year, month, last_day)

    # 마지막 날에서 거슬러 올라가며 금요일 찾기
    while last_date.weekday() != 4:  # 4 = Friday
        last_date -= timedelta(days=1)

    return last_date.replace(hour=8, minute=0, second=0, microsecond=0)

def get_monthly_expiry(months_ahead: int = 0):
    """
    월간 옵션 만기일 계산

    months_ahead: 0 = 이번달, 1 = 다음달, 2 = 2개월 후 (SM)
    """
    today = datetime.now()
    target_month = today.month + months_ahead
    target_year = today.year + (target_month - 1) // 12
    target_month = (target_month - 1) % 12 + 1

    expiry = get_last_friday_of_month(target_year, target_month)

    # 이미 만기 지났으면 다음달
    if expiry < today:
        return get_monthly_expiry(months_ahead + 1)

    return expiry

# 예시
M_expiry = get_monthly_expiry(0)   # Monthly (M) = 가장 가까운 월간
FM_expiry = get_monthly_expiry(0)  # Front Month (FM) = M과 동일
SM_expiry = get_monthly_expiry(1)  # Second Month (SM) = FM 다음 ← 여기!
TM_expiry = get_monthly_expiry(2)  # Third Month (TM) = SM 다음
```

---

### 분기 (Quarterly)

| 약자 | 영문 | 만기 | 예시 (오늘: 2025-12-23) |
|------|------|------|------------------------|
| **Q** | Quarterly | 이번 분기 마지막 금요일 | 2025-12-26 (Q4 끝) |
| **1Q** | 1 Quarter | 다음 분기 마지막 금요일 | 2026-03-27 (Q1 끝) |
| **2Q** | 2 Quarters | 2분기 후 마지막 금요일 | 2026-06-26 (Q2 끝) |
| **3Q** | 3 Quarters | 3분기 후 마지막 금요일 | 2026-09-25 (Q3 끝) |
| **4Q** | 4 Quarters | 4분기 후 마지막 금요일 | 2026-12-25 (Q4 끝) |

**분기 구분**:
- Q1: 1월, 2월, **3월** (마지막 금요일 = 3월 마지막 금)
- Q2: 4월, 5월, **6월** (마지막 금요일 = 6월 마지막 금)
- Q3: 7월, 8월, **9월** (마지막 금요일 = 9월 마지막 금)
- Q4: 10월, 11월, **12월** (마지막 금요일 = 12월 마지막 금)

**만기 시각**: UTC 08:00 (KST 17:00)

**계산법**:
```python
def get_quarter_end_month(month: int) -> int:
    """분기 마지막 월 반환"""
    return ((month - 1) // 3 + 1) * 3

def get_quarterly_expiry(quarters_ahead: int = 0):
    """
    분기 옵션 만기일 계산

    quarters_ahead: 0 = 이번분기, 1 = 다음분기, 2 = 2분기 후
    """
    today = datetime.now()
    current_quarter_end_month = get_quarter_end_month(today.month)

    target_month = current_quarter_end_month + quarters_ahead * 3
    target_year = today.year + (target_month - 1) // 12
    target_month = (target_month - 1) % 12 + 1

    expiry = get_last_friday_of_month(target_year, target_month)

    # 이미 만기 지났으면 다음 분기
    if expiry < today:
        return get_quarterly_expiry(quarters_ahead + 1)

    return expiry

# 예시
Q_expiry = get_quarterly_expiry(0)   # 이번 분기 (Q)
Q1_expiry = get_quarterly_expiry(1)  # 다음 분기 (1Q)
Q2_expiry = get_quarterly_expiry(2)  # 2분기 후 (2Q)
```

---

## 🎯 트레이더 관점 용어 (Trading Terminology)

### Front Month vs Back Month

| 용어 | 의미 | 약자 | 예시 (2025-12-23 기준) |
|------|------|------|----------------------|
| **Front Month** | 가장 가까운 월간 만기 | FM, M, 1M | 2025-12-26 |
| **Second Month** | FM 다음 월간 만기 | **SM**, 2M | 2026-01-30 |
| **Back Month** | 먼 만기 (SM 이후) | TM, 3M, 4M... | 2026-02-27+ |

**트레이더 대화 예시**:
```
Trader A: "What's the IV on front month ATM?"
Trader B: "FM 25000 call is trading at 80% IV"

Trader A: "Roll to second month?"
Trader B: "Yeah, SM premium is better, theta decay slower"
```

### Near-term vs Far-term

| 용어 | 기간 | 약자 | 전략 |
|------|------|------|------|
| **Near-term** | 0-30일 | D, W, M | 빠른 감마/세타, 단기 이벤트 |
| **Mid-term** | 1-3개월 | FM, SM, TM | 밸런스, 롤 전략 |
| **Far-term** | 3개월+ | Q, 1Q, 2Q | 느린 세타, 방향성 베팅 |
| **LEAPS** | 1년+ | (암호화폐 드뭄) | 장기 포지션 |

### Weeklies vs Monthlies vs Quarterlies

| 타입 | 만기 주기 | 약자 | 특징 |
|------|----------|------|------|
| **Weeklies** | 매주 금요일 | W, 1W, 2W | 높은 감마, 빠른 세타 decay |
| **Monthlies** | 매월 마지막 금 | M, FM, SM | 가장 유동적, 스탠다드 |
| **Quarterlies** | 분기 마지막 금 | Q, 1Q, 2Q | 큰 포지션, 기관 선호 |

---

## 🏦 거래소별 차이

### OKX

**만기 표기법**:
```
BTC-USD-250328        # 2025년 3월 28일 만기 (날짜 직접)
BTC-USD-250328-80000-C  # 2025-03-28, 80000 콜
```

**약자 사용**:
- API/거래소 UI: 날짜 직접 표기 (YYMMDD)
- 트레이더 구두: W, M, SM, Q 사용

**만기 시각**: UTC 08:00 (KST 17:00)

**주요 만기일**:
- Weekly: 매주 금요일 08:00 UTC
- Monthly: 매월 마지막 금요일 08:00 UTC
- Quarterly: 3월, 6월, 9월, 12월 마지막 금요일 08:00 UTC

### Deribit

**만기 표기법**:
```
BTC-27DEC24-80000-C   # 2024년 12월 27일, 80000 콜
BTC-28MAR25-70000-P   # 2025년 3월 28일, 70000 풋
```

**약자 사용**:
- API: 날짜 직접 (DDMMMYY)
- 트레이더: W, M, Q 구두 사용

**만기 시각**: UTC 08:00 (동일)

**주요 만기일**:
- Daily: 매일 08:00 UTC (유동성 낮음)
- Weekly: 매주 금요일 08:00 UTC
- Monthly: 매월 마지막 금요일 08:00 UTC
- Quarterly: 분기 마지막 금요일 08:00 UTC

---

## 📊 만기 구조 예시 (2025-12-23 기준)

### 전체 만기 타임라인

```
TODAY (2025-12-23 화요일)
│
├─ D   (2025-12-24)   Daily [1일]
├─ W   (2025-12-26)   Weekly 이번주 금요일 [3일]
├─ M   (2025-12-26)   Monthly 이번달 마지막 금 [3일]
├─ Q   (2025-12-26)   Quarterly Q4 끝 [3일]
│
├─ 1W  (2026-01-02)   다음주 금요일 [10일]
├─ 2W  (2026-01-09)   2주 후 금요일 [17일]
├─ 3W  (2026-01-16)   3주 후 금요일 [24일]
├─ 4W  (2026-01-23)   4주 후 금요일 [31일]
│
├─ FM  (2025-12-26)   Front Month = M (12월 마지막 금) [3일]
├─ SM  (2026-01-30)   Second Month (1월 마지막 금) [38일] ← 여기!
├─ TM  (2026-02-27)   Third Month (2월 마지막 금) [66일]
│
├─ 1Q  (2026-03-27)   다음 분기 Q1 끝 [94일]
├─ 2Q  (2026-06-26)   2분기 후 Q2 끝 [185일]
└─ 3Q  (2026-09-25)   3분기 후 Q3 끝 [276일]
```

### 월별 Front/Second/Third Month 추이

| 오늘 날짜 | FM (Front) | SM (Second) | TM (Third) |
|-----------|------------|-------------|------------|
| 2025-12-23 | 2025-12-26 | 2026-01-30 | 2026-02-27 |
| 2025-12-27 | 2026-01-30 | 2026-02-27 | 2026-03-27 |
| 2026-01-05 | 2026-01-30 | 2026-02-27 | 2026-03-27 |
| 2026-01-31 | 2026-02-27 | 2026-03-27 | 2026-04-24 |
| 2026-02-05 | 2026-02-27 | 2026-03-27 | 2026-04-24 |

**규칙**:
- FM = 가장 가까운 월간 만기 (아직 안 지난 마지막 금요일)
- SM = FM 다음 월간 만기
- TM = SM 다음 월간 만기

**Note**: 12월 26일 만기 후 (2025-12-27부터) FM은 1월 30일로 롤오버

---

## 🧮 DTE (Days to Expiry) 구분

| DTE | 약자 | 특징 | 전략 예시 |
|-----|------|------|----------|
| **0-7 DTE** | D, W | 극단적 감마/세타, 변동성 높음 | 0DTE 스캘핑, 이벤트 트레이딩 |
| **7-30 DTE** | W, 1W, 2W | 빠른 세타 decay, 감마 민감 | Weekly 철새 전략, Short vol |
| **30-60 DTE** | FM, M | 밸런스, 가장 유동적 | ATM straddle, Iron Condor |
| **60-90 DTE** | SM, 2M | 적당한 세타, 안정적 델타 | Diagonal spread, Calendar |
| **90+ DTE** | TM, Q, 1Q | 느린 세타, 방향성 중심 | LEAP 대체, Long vol |

**트레이더 선호도**:
- **Day trader**: 0-7 DTE (D, W)
- **Swing trader**: 7-30 DTE (1W, 2W)
- **Option seller**: 30-60 DTE (FM, M) ← 가장 많음
- **Hedger**: 60-90 DTE (SM)
- **Long-term investor**: 90+ DTE (Q)

---

## 💬 트레이더 대화 예시 (Real Trading Floor)

### 예시 1: Roll 전략

```
Trader A: "My FM short puts are ITM, roll to SM?"
Trader B: "Yeah, SM premium is 1.2 BTC, you'll collect extra credit"
Trader A: "But SM delta is lower, need more contracts"
Trader B: "Right, go 1.3x notional to keep delta neutral"
```

**해석**:
- FM short put = Front Month (1개월) 숏 풋이 ITM
- SM으로 롤 = Second Month (2개월)로 연장
- SM premium 1.2 BTC = 2개월 옵션이 더 비쌈 (시간가치)
- 1.3× notional = 계약 수 늘려서 델타 중립

### 예시 2: Weekly vs Monthly

```
Trader A: "Weeklies are crazy volatile today"
Trader B: "Yeah, 200% IV on W, but FM is still 80%"
Trader A: "Sell W straddle, hedge with FM long?"
Trader B: "Risky, gamma blowup if BTC moves 10%"
```

**해석**:
- W = Weekly (이번주) IV 200% (극단적)
- FM = Front Month IV 80% (정상)
- Sell W straddle = 주간 옵션 매도 (세타 수취)
- Hedge with FM long = 월간 옵션 매수로 헷지
- Gamma blowup = 감마 폭발 (가격 급변 시 손실)

### 예시 3: Quarterly 만기

```
Trader A: "1Q BTC 100k call, what do you think?"
Trader B: "Too far, 94 DTE, theta is negligible"
Trader A: "Yeah but vega is huge, good for IV expansion"
Trader B: "Fair, if you're betting on vol regime change"
```

**해석**:
- 1Q = Next Quarter (다음 분기, 94일)
- 100k call = 10만 달러 콜옵션
- Theta negligible = 세타 decay 미미 (시간 많음)
- Vega huge = 베가 크다 (IV 변화 민감)
- Vol regime change = 변동성 체제 변화 베팅

---

## 🎓 트레이더 사고방식 (How Traders Think)

### 1. 만기 선택 = 전략 선택

| 전략 | 선호 만기 | 이유 |
|------|----------|------|
| **Theta harvesting** | FM (30-60 DTE) | 최적 세타/감마 비율 |
| **Gamma scalping** | W (7 DTE) | 높은 감마, 빠른 리밸런싱 |
| **Vega trading** | SM, 1Q (60-90 DTE) | 큰 베가, IV 변화 민감 |
| **Directional bet** | M, FM (30-60 DTE) | 밸런스 (델타+세타) |
| **Event trading** | D, W (0-7 DTE) | 이벤트 직전, 저렴한 프리미엄 |

### 2. 만기 체인 (Expiry Chain) 보는 법

**Option Chain 예시** (2025-12-23 기준):
```
Expiry    | DTE | ATM Call IV | ATM Put IV | Volume | OI
----------|-----|-------------|------------|--------|------
26DEC (W) | 3   | 120%        | 125%       | 5,000  | 12,000  ← Weekly 높은 IV
30JAN (FM)| 38  | 75%         | 78%        | 15,000 | 45,000  ← Front Month 유동적
27FEB (SM)| 66  | 70%         | 72%        | 8,000  | 30,000  ← Second Month
27MAR (TM)| 94  | 68%         | 70%        | 4,000  | 20,000  ← Third Month
27MAR (1Q)| 94  | 68%         | 70%        | 6,000  | 35,000  ← Quarterly 큰 OI
```

**트레이더 분석**:
- W (Weekly): IV 스파이크 → 매도 기회?
- FM (Front Month): 가장 유동적 → 진입/청산 쉬움
- SM (Second Month): IV 낮음 → 매수 기회? 또는 캘린더 스프레드
- 1Q (Quarterly): OI 큼 → 기관 포지션, support/resistance

### 3. Roll 타이밍 (When to Roll)

**일반적인 룰**:
```
포지션: FM short put (30 DTE)

롤 타이밍:
- 21 DTE: 감마 증가 시작 → 롤 고려
- 14 DTE: 감마 급증 → 롤 권장
- 7 DTE: 극단적 감마 → 즉시 롤 or 청산
```

**롤 방향**:
- FM → SM (Second Month): 시간 연장 (most common)
- W → FM (Weekly → Monthly): 감마 리스크 줄임
- SM → FM (Roll down): 만기 당김 (aggressive, 크레딧 수취)

**롤 예시**:
```
Original position:
- Short FM 90000 put (30 DTE, premium 0.5 BTC)

Roll to:
- Buy to close FM 90000 put (현재 0.2 BTC)
- Sell to open SM 90000 put (premium 0.8 BTC)
- Net credit: 0.8 - 0.2 = 0.6 BTC (롤 수익)
- New DTE: 66 DTE
```

---

## 🔍 Common Mistakes (흔한 실수)

### ❌ 실수 1: 약자 혼동

```python
# ❌ 틀린 해석
SM = "Saturday Monthly"  # 완전히 틀림
FM = "Full Month"        # 틀림 (Front Month)
TM = "This Month"        # 틀림 (Third Month)

# ✅ 올바른 해석
SM = "Second Month"      # 2개월 후 만기
FM = "Front Month"       # 가장 가까운 월간 만기
TM = "Third Month"       # 3개월 후 만기
```

### ❌ 실수 2: DTE 계산 오류

```python
# ❌ 틀린 계산
# "오늘이 12월 23일이니까 SM은 2월 23일이겠지?"
SM = datetime(2026, 2, 23)  # 틀림!

# ✅ 올바른 계산
# "SM은 2개월 후 '마지막 금요일'"
SM = get_last_friday_of_month(2026, 2)  # 2026-02-27
```

### ❌ 실수 3: 만기 시각 무시

```python
# ❌ 만기일만 체크
expiry_date = datetime(2026, 1, 30)
if today > expiry_date:
    print("Expired")

# ✅ 만기 시각까지 체크 (UTC 08:00)
expiry_datetime = datetime(2026, 1, 30, 8, 0, 0)  # 08:00 UTC
if today_utc > expiry_datetime:
    print("Expired")
```

### ❌ 실수 4: Weekly vs Monthly 혼동

```python
# ❌ "4W는 한 달이니까 M이랑 같겠지?"
W4 = get_weekly_expiry(4)   # 4주 후 금요일 (28일)
M = get_monthly_expiry(0)   # 이번달 마지막 금요일

# 다를 수 있음!
# 예: 12월 23일 기준
#   4W = 2026-01-23 (4주 후)
#   M  = 2025-12-26 (이번달 마지막 금)
#   FM = 2026-01-30 (다음달 마지막 금)
```

---

## 📚 관련 문서

### Knowledge Base
- **[OKX Options Specifications](okx/options_specifications.md)** - OKX 옵션 스펙
- **[Options Basics](../domain/options_basics.md)** - Greeks, 전략 기초
- **[Greeks Definitions](greeks_definitions.md)** - PA/BS Greeks 차이

### 외부 문서
- **OKX Options**: https://www.okx.com/help/options-trading
- **Deribit Options**: https://www.deribit.com/kb/options

---

## 🎯 Quick Reference (Cheat Sheet)

```
Daily    | D, 1D, 2D             | 다음 영업일, 1-2일 후
Weekly   | W, 1W, 2W, 3W, 4W     | 이번주/다음주/2-4주 후 금요일
Monthly  | M, FM, SM, TM         | 이번달/1-3개월 후 마지막 금요일
         | 1M, 2M, 3M            | (동일)
Quarterly| Q, 1Q, 2Q, 3Q, 4Q     | 이번/다음 분기 마지막 금요일

만기 시각: UTC 08:00 (KST 17:00)
만기 요일: 금요일 (Friday) - 월간/주간/분기 모두

FM = Front Month   (가장 가까운 월간)
SM = Second Month  (2개월 후) ← NOT Saturday Monthly!
TM = Third Month   (3개월 후)

DTE 구분:
0-7   | Near-term  | 높은 감마/세타
30-60 | Mid-term   | 밸런스 (가장 유동적)
90+   | Far-term   | 느린 세타, 방향성
```

---

**Version**: 1.0
**Created**: 2025-12-23
**Critical Note**: SM = Second Month (2개월 후), NOT Saturday Monthly!

