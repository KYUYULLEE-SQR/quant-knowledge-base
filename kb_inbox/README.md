# Knowledge Update Input

**Purpose**: 다른 프로젝트/에이전트에서 발견한 지식을 임시 보관 후 KB에 반영

---

## 사용 방법

### 1. 새로운 지식 발견 시

다른 프로젝트나 에이전트 작업 중 "이거 knowledge에 추가해야겠다" 싶으면:

```bash
# 이 디렉토리에 .md 파일로 작성
vim ~/knowledge/input/YYYY-MM-DD_topic.md
```

### 2. 파일 형식

```markdown
# [주제]

**Date**: YYYY-MM-DD
**Source**: [프로젝트명 or 실험명]
**Target KB File**: [어느 KB 파일에 반영할지]

---

## Summary

간단한 요약

## Details

상세 내용 (코드, 데이터, 인사이트)

## Action Required

- [ ] knowledge/[category]/[file].md 업데이트
- [ ] 관련 문서 cross-reference 추가
- [ ] README.md 인덱스 업데이트

## References

- 관련 파일/링크
```

### 3. 주기적 검토

주기적으로 (주 1회 or 월 1회):
1. input/ 폴더의 .md 파일들 검토
2. 해당 KB 파일에 반영
3. input/ 파일 삭제 or archive/ 이동

---

## 파일명 규칙

```
YYYY-MM-DD_topic_name.md
```

**예시**:
- `2025-12-24_okx_funding_rate_anomaly.md`
- `2025-12-25_partial_fill_실제_데이터.md`
- `2026-01-05_theta_decay_edge_case.md`

---

## 현재 상태

**파일 수**: 0 (pending updates 없음)

---

## 예시

### 좋은 예

```markdown
# OKX 부분 체결 실제 데이터

**Date**: 2025-12-24
**Source**: options_trading 프로젝트 (live trading)
**Target KB File**: modeling/fill_probability.md

---

## Summary

실제 거래 데이터 분석 결과, OKX 옵션 maker order 부분 체결률이
기존 가정(30%)보다 높음 (42% ± 8%).

## Details

- Period: 2025-12-01 ~ 2025-12-24
- Sample: 1,247 orders
- Full fill: 58.1%
- Partial fill: 42.3% (기존 가정 30% vs 실제 42%)
- No fill: 0.6%

Deep OTM (delta < 0.1): 62% partial fill
ATM (delta 0.4-0.6): 28% partial fill

## Action Required

- [ ] modeling/fill_probability.md 업데이트
  - 기존 30% → 42% (conservative)
  - Delta 구간별 차등 적용
- [ ] experiments/lessons_learned.md 추가
  - "가정 검증의 중요성" 섹션

## References

- ~/options_trading/analysis/fill_analysis_2025-12.ipynb
- ~/options_trading/logs/live_trading_2025-12.log
```

---

## 나쁜 예 (금지)

```markdown
# 메모

뭔가 이상한거 발견했는데 나중에 정리...
```

**문제점**:
- 날짜 없음
- 출처 불명
- 구체적 내용 없음
- 액션 아이템 없음

---

**Last Updated**: 2025-12-24
**Version**: 1.0
