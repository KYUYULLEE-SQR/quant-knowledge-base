# KB Meta (Knowledge Base 관리)

Knowledge Base 자체를 관리하기 위한 내부 폴더.

## Structure

```
_kb-meta/
├── decisions/        # 중요 아키텍처 결정 기록
├── templates/        # 문서 템플릿
└── pending/          # 반영 대기 업데이트
```

## Purpose

- **decisions/**: 중요한 설계 결정을 기록 (왜 이렇게 했는지)
- **templates/**: 새 문서 작성용 템플릿
- **pending/**: KB 업데이트 staging 영역

## Why `_kb-meta`?

- `_` prefix: 내부/관리용임을 표시 (top에 정렬 안 됨)
- `kb-meta`: Knowledge Base에 관한 메타 정보

이전 이름 `_admin`은 "무엇의 admin인지" 불명확해서 변경.

## Related

- `~/knowledge/agent-rules/` - Claude/Agent 행동 규칙
