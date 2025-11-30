#!/bin/bash
# Quick setup script for GitHub

echo "🚀 GitHub Actions 설정 스크립트"
echo "================================"
echo

# Check if git is initialized
if [ ! -d .git ]; then
    echo "❌ Git 리포지토리가 아닙니다. 먼저 'git init'을 실행하세요."
    exit 1
fi

# Get remote URL
read -p "GitHub 리포지토리 URL을 입력하세요 (예: https://github.com/username/repo.git): " REPO_URL

if [ -z "$REPO_URL" ]; then
    echo "❌ URL이 필요합니다."
    exit 1
fi

echo
echo "📝 Git 설정 중..."

# Add or update remote
if git remote | grep -q "origin"; then
    git remote set-url origin "$REPO_URL"
    echo "✅ 리모트 URL 업데이트 완료"
else
    git remote add origin "$REPO_URL"
    echo "✅ 리모트 추가 완료"
fi

echo
echo "📦 파일 추가 중..."
git add .

echo
read -p "커밋 메시지를 입력하세요 (기본: 'Initial commit'): " COMMIT_MSG
COMMIT_MSG=${COMMIT_MSG:-"Initial commit: Game telemetry system"}

git commit -m "$COMMIT_MSG"

echo
echo "🚀 GitHub에 푸시 중..."
git push -u origin main

echo
echo "✅ 완료!"
echo
echo "다음 단계:"
echo "1. https://github.com/YOUR_USERNAME/YOUR_REPO/actions 에서 빌드 확인"
echo "2. 빌드 완료 후 Artifacts 다운로드"
echo
echo "릴리스 생성 (선택사항):"
echo "  git tag v1.0.0"
echo "  git push origin v1.0.0"
