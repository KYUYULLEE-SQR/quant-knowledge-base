# 문서 템플릿

**Purpose**: 일관된 문서 작성을 위한 템플릿 모음

---

## 사용법

1. 템플릿 파일 복사
2. 내용 채우기
3. 적절한 디렉토리에 저장

---

## 템플릿 목록 (향후 추가)

### experiment_report.md
- 실험 결과 보고서 템플릿
- Hypothesis, Results, Validation, Conclusion 구조

### strategy_doc.md
- 전략 문서 템플릿
- Overview, Logic, Parameters, Risks 구조

### kb_article.md
- Knowledge Base 문서 템플릿
- Standard KB 포맷 (Last Updated, Quick Summary, etc.)

### pitfall_template.md
- 함정 문서 템플릿
- Problem, Example, Detection, Prevention 구조

---

## 현재 상태

**파일 수**: 0 (템플릿 없음)

문서화 패턴이 반복되면 템플릿화하세요.

---

## 작성 가이드라인

### 모든 KB 문서 공통

```markdown
# [Title]

**What**: 한 줄 정의
**Why Important**: 왜 중요한가
**Last Updated**: YYYY-MM-DD

---

## Quick Summary (핵심 3-5줄)

...

## [Main Content Sections]

...

## References

- Related KB docs
- External links
```

### 헤더 일관성

- `## ` (Level 2): 주요 섹션
- `### ` (Level 3): 서브섹션
- `#### ` (Level 4): 상세 항목

### 코드 블록

- 언어 명시: ```python, ```bash, ```sql
- 주석 포함 (설명 필수)
