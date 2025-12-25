# Claude Code Rules (통합 관리)

**Purpose**: Claude Code 프롬프트를 knowledge repo에서 통합 관리

**장점**:
- ✅ Knowledge repo 클론만 하면 모든 규칙 포함
- ✅ 규칙 수정 → git commit → 다른 서버에서 pull
- ✅ 버전 관리 (git history)
- ✅ 새 서버 설정 자동화 (install.sh 한 번 실행)

---

## 설치 방법

### 새 서버 (처음 설치)

```bash
# 1. knowledge repo 클론
git clone https://github.com/KYUYULLEE-SQR/quant-knowledge-base.git ~/knowledge

# 2. Claude Code rules 설치
cd ~/knowledge/agent_prompts/claude_code
./install.sh

# 완료! Claude Code가 이 프롬프트를 사용함
```

---

## 규칙 수정

### 로컬에서 수정

```bash
# 1. 파일 수정
vim ~/knowledge/agent_prompts/claude_code/CLAUDE.md
vim ~/knowledge/agent_prompts/claude_code/rules/06_behavioral_rules.md

# 2. Git commit & push
cd ~/knowledge
git add agent_prompts/claude_code/
git commit -m "Update Claude Code rules: ..."
git push

# 3. 다른 서버에서 동기화
cd ~/knowledge
git pull
# 심링크가 자동 반영됨 (재설치 불필요)
```

---

## 파일 구조

| 파일 | 위치 (knowledge) | 심링크 위치 (Claude Code) |
|------|-----------------|-------------------------|
| CLAUDE.md | `~/knowledge/agent_prompts/claude_code/` | `~/.claude/` |
| rules/*.md | `~/knowledge/agent_prompts/claude_code/rules/` | `~/.claude/rules/` |

---

## 주의사항

1. **심링크 방식**: 파일을 복사하지 않고 심링크로 연결
   - 장점: knowledge에서 수정 → Claude Code가 즉시 반영
   - 주의: knowledge 디렉토리 삭제 시 심링크 깨짐

2. **Git 관리**: 이 디렉토리는 knowledge repo의 일부
   - `.gitignore`에 포함되지 않음 (모든 파일 추적)

3. **다른 서버 동기화**:
   - git pull만 하면 됨 (재설치 불필요)
   - 심링크가 계속 유지됨

---

## 포함된 규칙

### CLAUDE.md
- Core identity & persona
- Autonomy principles
- Language & communication
- Cognitive protocol
- Response structure
- Experiment guidelines
- Server context
- Knowledge base protocol

### rules/*.md (10개)
1. `01_identity_and_context.md` - 정체성, 서버 문맥
2. `02_cognitive_protocol.md` - 사고 프로토콜
3. `03_response_structure.md` - 응답 구조
4. `04_operational_rules.md` - 실무 규칙
5. `05_experiment_guidelines.md` - 실험 가이드라인
6. `06_behavioral_rules.md` - 행동 규칙
7. `08_experiment_organization.md` - 실험 파일 관리
8. `10_backtesting_integrity.md` - 백테스트 정합성
9. `11_file_hygiene.md` - 파일 정리 규칙
10. `12_project_state_protocol.md` - 프로젝트 상태 관리

---

## 문제 해결

### 심링크가 깨진 경우

```bash
# 재설치
cd ~/knowledge/agent_prompts/claude_code
./install.sh
```

### 규칙이 적용 안 되는 경우

1. Claude Code 재시작
2. 심링크 확인:
   ```bash
   ls -la ~/.claude/CLAUDE.md
   ls -la ~/.claude/rules/
   ```
3. 파일 존재 확인:
   ```bash
   cat ~/.claude/CLAUDE.md
   ```

---

**Last Updated**: 2025-12-25
**Version**: 1.1 (Path fixes, added rules 11-12)
