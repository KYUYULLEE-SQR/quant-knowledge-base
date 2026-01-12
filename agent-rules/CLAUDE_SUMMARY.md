# CLAUDE.md 요약 (Quick Reference)

**Full version**: `CLAUDE.md` (~320줄) | **This**: ~80줄
**Runtime**: `--dangerously-skip-permissions` (권한 확인 불필요)

---

## 🚨 매 응답 전 체크

```
□ 백테스트? → 10+ metrics + [STAT:ci]
□ 단일 질문? → 4+ metrics
□ 완료? → Decision + Files + Next
□ Sharpe>5/승률>70%? → 🚨 경고
```

---

## ⚡ 7대 원칙

1. 즉시 실행 (확인 금지)
2. 가정 → 명시 → 실행
3. 항상 Next Action
4. 세션 일관성
5. artifact + next
6. 1개 → 3-5개 자동
7. Baseline + Falsification 자동

---

## ❌/✅ Quick Reference

| ❌ | ✅ |
|---|---|
| "~할까요?" | 즉시 실행 |
| "선택해주세요" | 둘 다 실행 |
| 1개 후 멈춤 | 3-5개 변형 |
| 에러 후 대기 | 자동 수정 |

---

## 🔴 백테스트 전 체크

```
□ shift(-N), bfill, center=True 없음?
□ entry = signal.shift(1)?
□ Sharpe < 5, 승률 < 70%?
```

---

## 📊 출력 형식

**실험**: 10+ metrics table + Files + Next
**단일 질문**: 4+ metrics + 파일 경로
**완료**: Decision (Deploy/Shelve/Discard)

---

## 🎓 Baksa Trust Score

| 점수 | 조치 |
|------|------|
| 80+ | Deploy |
| 60-79 | Shelve |
| 40-59 | 재작업 |
| <40 | Discard |

**감점**: Sharpe>5 (-20), 승률>70% (-20), 통계없음 (-30)

---

## 🔄 Sisyphus

```
에러 → 수정 → 재실행 (3회)
1개 완료 → 다음 자동
중단 → STATE.md 저장
```

---

## 🔑 프리셋 키워드

| 말하면 | 실행 |
|--------|------|
| 정합성 | Entry/Position/PnL 체크 |
| 엄밀하게 | 통계/엣지케이스 |
| 이상한거 | Anomaly 스캔 |
| 풀체크 | 전체 5개 |

---

## 📁 폴더

```
~/experiments/YYYY-MM-DD_HH-MM_name/
├── config.yaml
├── code/
├── results/
└── logs/
```

---

## 🧠 사고 깊이

| L1 | 즉시 | typo |
| L2 | 표준 | 기능 |
| L3 | Deep | 백테스트 |
| L4 | 최대 | 실거래 |

---

**Version**: 10.0 | **Updated**: 2025-01-12
