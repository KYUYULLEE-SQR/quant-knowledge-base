#!/bin/bash

# Claude Code Rules 자동 설치 스크립트
# 실행: cd ~/knowledge/claude_code_rules && ./install.sh

set -e  # 에러 시 중단

echo "🚀 Installing Claude Code rules..."

# 1. ~/.claude 디렉토리 생성
echo "📁 Creating ~/.claude directory..."
mkdir -p ~/.claude/rules

# 2. CLAUDE.md 심링크 생성
echo "🔗 Linking CLAUDE.md..."
ln -sf ~/knowledge/claude_code_rules/CLAUDE.md ~/.claude/CLAUDE.md

# 3. rules/*.md 심링크 생성
echo "🔗 Linking rules..."
for rule in ~/knowledge/claude_code_rules/rules/*.md; do
    ln -sf "$rule" ~/.claude/rules/$(basename "$rule")
done

echo ""
echo "✅ Claude Code rules installed successfully!"
echo ""
echo "📋 Installed files:"
echo "  - ~/.claude/CLAUDE.md → ~/knowledge/claude_code_rules/CLAUDE.md"
echo "  - ~/.claude/rules/*.md → ~/knowledge/claude_code_rules/rules/*.md"
echo ""
echo "💡 To update rules:"
echo "  1. Edit files in ~/knowledge/claude_code_rules/"
echo "  2. git commit & push"
echo "  3. On other servers: git pull (심링크가 자동 반영됨)"
