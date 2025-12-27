#!/bin/bash

# Claude Code Rules 자동 설치 스크립트
# 실행: cd ~/knowledge/rules && ./install.sh

set -e  # 에러 시 중단

echo "🚀 Installing Claude Code rules..."

# 1. ~/.claude 디렉토리 생성
echo "📁 Creating ~/.claude directory..."
mkdir -p ~/.claude/rules

# 2. CLAUDE.md 심링크 생성
echo "🔗 Linking CLAUDE.md..."
ln -sf ~/knowledge/rules/CLAUDE.md ~/.claude/CLAUDE.md

# 3. rules/*.md 심링크 생성 (numbered rules)
echo "🔗 Linking rules..."
for rule in ~/knowledge/rules/*.md; do
    # Skip CLAUDE.md and README.md (only link numbered rules)
    basename=$(basename "$rule")
    if [[ "$basename" =~ ^[0-9] ]]; then
        ln -sf "$rule" ~/.claude/rules/"$basename"
    fi
done

echo ""
echo "✅ Claude Code rules installed successfully!"
echo ""
echo "📋 Installed files:"
echo "  - ~/.claude/CLAUDE.md → ~/knowledge/rules/CLAUDE.md"
echo "  - ~/.claude/rules/*.md → ~/knowledge/rules/*.md"
echo ""
echo "💡 To update rules:"
echo "  1. Edit files in ~/knowledge/rules/"
echo "  2. git commit & push"
echo "  3. On other servers: git pull (심링크가 자동 반영됨)"
