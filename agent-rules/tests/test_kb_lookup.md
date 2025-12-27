# Test: KB Lookup (지식 베이스 참조 테스트)

**Purpose**: Agent가 도메인 질문 시 KB를 자동 참조하는지 검증
**Priority**: ⭐⭐ HIGH
**Last Updated**: 2025-12-26

---

## 🎯 테스트 목표

Agent가 다음을 하는지 확인:
1. 도메인 질문 시 KB 자동 검색
2. 출처 명시 (📚 참조)
3. KB 내용 정확히 인용
4. 없는 내용은 없다고 명시

---

## 📝 Test Case 1: 수수료 질문

### Input
```
OKX 수수료 얼마야?
```

### Expected (PASS)
```
## 💰 OKX Fee Structure

### Options (VIP9 DMM 기준)
| Type | Rate |
|------|------|
| Maker | -0.01% (rebate) |
| Taker | +0.03% |
| Exercise | +0.02% |

### Futures (VIP9 DMM 기준)
| Type | Rate |
|------|------|
| Maker | -0.005% (rebate) |
| Taker | +0.015% |

📚 출처: `~/knowledge/exchanges/okx/fee_structure.md`
```

### Anti-Patterns (FAIL)
```
❌ "대략 0.03% 정도입니다" [불정확]
❌ [출처 없음]
❌ [KB 참조 안 함]
```

---

## 📝 Test Case 2: Greeks 질문

### Input
```
OKX Greeks 단위가 뭐야? PA랑 BS 차이는?
```

### Expected (PASS)
```
## 📊 OKX Greeks Units

### PA (Per Asset) vs BS (Black-Scholes)

| Greek | PA Unit | BS Unit | Conversion |
|-------|---------|---------|------------|
| Delta | BTC | USD | PA × BTC_price |
| Gamma | BTC/USD | USD/USD² | 복잡 (사용 금지) |
| Theta | BTC/day | USD/day | PA × BTC_price |
| Vega | BTC/1% | USD/1% | PA × BTC_price |

### 핵심 규칙
- **Portfolio 집계**: 반드시 BS (USD) 단위로 통일
- **PA Gamma**: 변환 공식 불명확, 사용 금지
- **API 필드**: `deltaBS`, `thetaBS`, `vegaBS` 사용 권장

📚 출처: `~/knowledge/exchanges/_common/greeks.md`
```

### Anti-Patterns (FAIL)
```
❌ "PA는 BTC 단위, BS는 USD 단위입니다" [불완전]
❌ [변환 규칙 없음]
❌ [Portfolio 집계 규칙 없음]
```

---

## 📝 Test Case 3: 옵션 만기 질문

### Input
```
OKX 옵션 만기 시간이 언제야?
```

### Expected (PASS)
```
## ⏰ OKX Options Expiry

**만기 시간**: UTC 08:00 (KST 17:00)

### 거래 가능 시간
- 만기 **직전까지** 거래 가능 (UTC 07:59도 OK)
- TTE 1분(0.001 day)도 거래 가능
- ❌ "TTE < 1 day = 거래 불가" (WRONG!)

### 만기 약자
| 약자 | 의미 | 예시 |
|------|------|------|
| D | Daily | 매일 |
| W | Weekly | 매주 금요일 |
| M | Monthly | 매월 마지막 금요일 |
| SM | Second Month | 다음 달 (NOT Saturday!) |
| Q | Quarterly | 3/6/9/12월 마지막 금요일 |

### Gamma Explosion 주의
- TTE < 1 day, ATM 근처
- Greeks 급변, 신뢰도 낮음

📚 출처:
- `~/knowledge/exchanges/okx/options_specifications.md`
- `~/knowledge/trading/fundamentals/options_expiry_and_tte.md`
```

### Anti-Patterns (FAIL)
```
❌ "UTC 08:00입니다" [불완전]
❌ [거래 가능 시간 누락]
❌ [Gamma explosion 경고 없음]
```

---

## 📝 Test Case 4: 슬리피지 질문

### Input
```
슬리피지 어떻게 계산해?
```

### Expected (PASS)
```
## 📉 Slippage Model

### OKX Options 슬리피지

**기본 모델**:
```
slippage = spread / 2 + market_impact
```

### 구성 요소
| Component | Estimation |
|-----------|------------|
| Spread | bid-ask spread의 절반 |
| Market Impact | size / depth × volatility_factor |

### 백테스트 권장값
| 시장 상황 | 슬리피지 |
|----------|----------|
| 유동성 좋음 | 0.03-0.05% |
| 보통 | 0.05-0.10% |
| 유동성 나쁨 | 0.10-0.30% |

### Maker vs Taker
- **Maker**: 슬리피지 0 (spread 안 넘으면)
- **Taker**: 전체 spread + impact

📚 출처: `~/knowledge/trading/cost-models/transaction_cost.md`
```

### Anti-Patterns (FAIL)
```
❌ "대략 0.1% 가정하면 됩니다" [근거 없음]
❌ [모델 설명 없음]
❌ [출처 없음]
```

---

## 📝 Test Case 5: MDD 계산 질문

### Input
```
MDD가 0으로 나오는데 왜 그래?
```

### Expected (PASS)
```
## 🔍 MDD = 0 Problem

### 원인
Entry/Exit 시점에만 NAV 평가 → 중간 손실 미반영

### 증상
```
Backtest MDD: 0%
Live MDD: -18%
```

### 해결책: Hourly MTM

```python
# ❌ Bad: Entry/Exit만 평가
nav_history = [entry_nav, exit_nav]

# ✅ Good: 매 시간 평가
for ts in hourly_timestamps:
    nav = cash + sum(pos.qty * get_mark_price(ts))
    nav_history.append(nav)
```

### NAV Policy
- **평가 주기**: 시간별 (hourly)
- **리샘플링**: 일별 (daily) for metrics
- **Mark price**: 매 시점 market price

📚 출처: `~/knowledge/research_methodology/backtest_standards/backtesting_nav_policy.md`
```

### Anti-Patterns (FAIL)
```
❌ "코드에 버그가 있는 것 같습니다"
❌ [근본 원인 설명 없음]
❌ [해결책 없음]
```

---

## 📝 Test Case 6: DB 접속 질문

### Input
```
옵션 데이터 어디서 가져와?
```

### Expected (PASS)
```
## 💾 Options Data Source

### Primary: spice PostgreSQL

```python
# 연결 정보
host = "localhost"  # spice 서버에서
port = 5432
database = "data_integration"
user = "sqr"
```

### 메인 테이블: btc_options_parsed
| Column | Type | Description |
|--------|------|-------------|
| date | timestamp | 날짜/시간 |
| exchange | varchar | OKX, Deribit |
| symbol | varchar | BTC-25DEC25-100000-C |
| strike | float | 행사가 |
| callput | varchar | C/P |
| expiry | timestamp | 만기일 |
| tte | float | 잔존일수 |
| iv | float | 내재변동성 |
| greeks | jsonb | delta, gamma, theta, vega |

### 데이터 규모
- 총 169M rows
- 기간: 2022-04-16 ~ 2025-12-05
- OKX: 31M, Deribit: 138M

📚 출처: `~/knowledge/technical_infrastructure/databases/spice_options_db.md`
```

### Anti-Patterns (FAIL)
```
❌ "PostgreSQL에서 가져옵니다" [불완전]
❌ [연결 정보 없음]
❌ [테이블 스키마 없음]
```

---

## 📝 Test Case 7: KB에 없는 질문

### Input
```
Binance 선물 청산 메커니즘이 어떻게 돼?
```

### Expected (PASS)
```
## ⚠️ KB에 해당 정보 없음

`~/knowledge/exchanges/binance/` 에는 다음만 있습니다:
- `fee_structure.md` (수수료)
- `options_specifications.md` (옵션 스펙)

**선물 청산 메커니즘**은 문서화되어 있지 않습니다.

### 권장 조치
1. Binance 공식 문서 확인: https://www.binance.com/en/support/faq
2. KB에 추가 필요 시: `~/knowledge/exchanges/binance/futures_liquidation.md` 생성

### 일반적인 정보 (확인 필요)
- Maintenance margin 미달 시 청산
- Insurance fund 우선 사용
- ADL (Auto-Deleveraging) 후순위
```

### Anti-Patterns (FAIL)
```
❌ [없는 정보 추측해서 답변]
❌ "잘 모르겠습니다"
❌ [KB 확인 없이 일반 지식으로 답변]
```

---

## 📊 KB 참조 체크리스트

### 질문 유형별 참조 파일

| 키워드 | 참조 파일 |
|-------|----------|
| 수수료, fee | `exchanges/okx/fee_structure.md` |
| Greeks, delta, gamma | `exchanges/greeks_definitions.md` |
| 만기, expiry, TTE | `trading_fundamentals/options_expiry_and_tte.md` |
| 슬리피지, slippage | `backtest_models/transaction_cost_model.md` |
| MDD, drawdown, NAV | `backtest_standards/backtesting_nav_policy.md` |
| 데이터, DB, 테이블 | `databases/spice_options_db.md` |
| Look-ahead, bias | `lessons_learned/common_pitfalls.md` |

### 응답 필수 요소

- [ ] 관련 KB 파일 확인
- [ ] 정확한 수치/규칙 인용
- [ ] 📚 출처 명시
- [ ] 없으면 없다고 명시

---

**Version**: 1.0
