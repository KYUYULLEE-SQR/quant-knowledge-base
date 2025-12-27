#!/bin/bash
# SSH Key Setup Script
# 새 서버에 SSH 키를 등록하는 스크립트
# Usage: ./setup_ssh_key.sh [hostname] [user]

set -e

HOST=${1:-"192.168.50.203"}
USER=${2:-"sqr"}
KEY_FILE="$HOME/.ssh/id_rsa"

echo "=== SSH Key Setup for $USER@$HOST ==="

# 1. SSH 키가 없으면 생성
if [ ! -f "$KEY_FILE" ]; then
    echo "SSH 키가 없습니다. 생성 중..."
    ssh-keygen -t rsa -b 4096 -f "$KEY_FILE" -N "" -C "$USER@$(hostname)"
    echo "✅ SSH 키 생성 완료: $KEY_FILE"
fi

# 2. known_hosts에서 기존 호스트 키 제거 (새 서버인 경우)
echo "기존 호스트 키 제거 중..."
ssh-keygen -f "$HOME/.ssh/known_hosts" -R "$HOST" 2>/dev/null || true

# 3. SSH 키 복사 (비밀번호 입력 필요)
echo ""
echo "SSH 키를 $HOST에 등록합니다."
echo "비밀번호를 입력하세요:"
ssh-copy-id -i "$KEY_FILE.pub" -o StrictHostKeyChecking=accept-new "$USER@$HOST"

# 4. 테스트
echo ""
echo "=== 접속 테스트 ==="
ssh -o BatchMode=yes "$USER@$HOST" "hostname && echo '✅ SSH 키 인증 성공!'"

echo ""
echo "=== 완료 ==="
echo "이제 비밀번호 없이 접속 가능: ssh $USER@$HOST"
