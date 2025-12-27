# APPLY_ALWAYS
# This file defines response structure (reference guide).
# Follow when generating responses, but behavioral rules take priority.

---

# 📝 Response Structure (구조 가이드)

Every response MUST follow this **4-section format**.

**CRITICAL**: 추상적/짧은 보고 금지. 구체적 수치/코드/로그 포함 필수.

---

## 📏 Length Guidelines

**Minimum per response:**
- Section 1: 4-6 lines (수치 3개 이상)
- Section 2: 15-25 lines (표/코드/벤치마크)
- Section 3: 30-50 lines (실제 코드+출력+파일)
- Section 4: 20-30 lines (한계+인사이트+다음단계)
- **Total: 70-110 lines minimum**

---

## Section 1: 🎯 Executive Summary (핵심 요약)

**Format**:
```markdown
- **Status**: 🛠️/⚠️/🔍 [상태]
- **Key Actions**: [파일명, 함수명, 행 수, 구체적 작업]
- **Results**: [수치 결과 - Sharpe, MDD, 거래 수, 에러율 등]
- **Design Decision**: [왜 A vs B - 비교 수치 포함]
```

**❌ Bad**: "분석 완료", "좋은 결과"
**✅ Good**: "25,279건 분석, 21.3% 과대평가, RMSE 0.1357 ± 0.0024, Ridge vs Lasso (+5% RMSE 우수)"

---

## Section 2: ⚙️ Architecture & Logic (구조 & 논리)

**Required subsections**:
1. 전체 흐름 (단계별 input/output)
2. 핵심 구현 (주요 함수/클래스)
3. 알고리즘 선택 (벤치마크 테이블)
4. Trade-offs (장점 vs 단점)

**Must include**: 비교 테이블, 코드 스니펫, 복잡도 분석

**❌ Bad**: "Ridge regression 사용"
**✅ Good**: 
```
Ridge vs Lasso vs RF 비교:
| Method | RMSE | Time | Stability |
|--------|------|------|-----------|
| Ridge  | 0.135| 2.3s | ★★★★★    |
| Lasso  | 0.142| 3.1s | ★★★☆☆    |
| RF     | 0.130| 45s  | ★★★★☆    |
선택: Ridge (RMSE 4% 차이, 학습 20배 빠름, IV는 smooth해야 함)
```

---

## Section 3: 💻 Execution Results (실행 결과)

**Required components**:
1. 실행 환경 (서버, 시간, 코드 경로)
2. 실행 코드 (실제 실행한 코드 전체)
3. 실행 출력 (실제 출력 - 로그/메트릭/에러 모두)
4. 생성 파일 (경로 + 크기)
5. 메트릭 테이블

**CRITICAL**: 
- Placeholder 절대 금지 ("Expected output:" 금지)
- 실제 실행만 보고
- 코드 + 출력 모두 포함

**❌ Bad**: "모델 학습 완료. 결과: Sharpe 2.4"
**✅ Good**: [실제 코드 20-30줄] + [실제 출력 10-20줄] + [생성 파일 목록] + [메트릭 테이블]

---

## Section 4: 💡 Insights & Next Steps (인사이트 & 다음 단계)

**Required subsections**:

### Self-Critique (3가지)
- 한계 1: [문제 + 영향 + 개선 방안]
- 한계 2: [문제 + 영향 + 개선 방안]
- 한계 3: [문제 + 영향 + 개선 방안]

### Key Insights (3가지)
- 패턴 1: [발견 + 빈도 + 전략적 의미]
- 패턴 2: [발견 + 빈도 + 전략적 의미]
- 패턴 3: [발견 + 빈도 + 전략적 의미]

### Proactive Suggestions (3가지, 우선순위)
**우선순위 1 (High)**: [실험명]
- 목표: [예상 개선]
- 방법: [구체적 단계]
- 예상 결과: [수치]
- 예상 시간: [시간]

**우선순위 2**: ...
**우선순위 3**: ...

**권장 순서**: 1 → 2 → 3 (이유 명시)

---

## 🎯 Quick Examples

### ❌ Bad Response (20 lines, abstract)
```
Fair IV 모델 분석했습니다.
Ridge regression으로 학습했고 결과가 좋습니다.
다음에 더 테스트하면 좋겠습니다.
```

### ✅ Good Response (80+ lines, concrete)
```
🎯 Executive Summary
- Status: 🔍 Fair IV 분석 완료 (25,279건, 2024-Q4)
- Key Actions: Ridge(degree=2, alpha=1.0), 5-fold CV, RMSE 0.1357
- Results: Mispricing >10%: 21.3%, Deep OTM 집중 (+83%)
- Design Decision: Ridge vs Lasso (RMSE +5%, 안정성 +40%)

⚙️ Architecture & Logic
[15-25 lines with table, code, benchmark]

💻 Execution Results
[30-50 lines with actual code + output + files + metrics table]

💡 Insights & Next Steps
[20-30 lines with 3 critiques + 3 insights + 3 prioritized suggestions]
```

---

**Last Updated**: 2025-12-18  
**Version**: 4.0 (Condensed from 14KB → 5KB)
