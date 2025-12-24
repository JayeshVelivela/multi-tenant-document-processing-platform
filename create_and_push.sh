#!/bin/bash

GITHUB_USERNAME="JayeshVelivela"
REPO_NAME="multi-tenant-document-processing-platform"
REPO_URL="https://github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"

echo "🚀 Automated GitHub Setup"
echo "=========================="
echo ""

# Step 1: Add remote (remove if exists)
if git remote get-url origin > /dev/null 2>&1; then
    echo "📡 Removing existing remote..."
    git remote remove origin
fi

echo "📡 Adding remote: $REPO_URL"
git remote add origin "$REPO_URL"

# Step 2: Try to create repo using GitHub CLI if available
if command -v gh &> /dev/null; then
    echo "🔧 GitHub CLI found. Attempting to create repository..."
    
    # Check if authenticated
    if gh auth status &> /dev/null; then
        echo "✅ GitHub CLI authenticated"
        echo "📦 Creating repository: $REPO_NAME"
        gh repo create "$REPO_NAME" --public --source=. --remote=origin --push 2>&1
        if [ $? -eq 0 ]; then
            echo ""
            echo "✅ SUCCESS! Repository created and code pushed!"
            echo "   URL: https://github.com/${GITHUB_USERNAME}/${REPO_NAME}"
            exit 0
        fi
    else
        echo "⚠️  GitHub CLI not authenticated"
        echo "   Run: gh auth login"
    fi
fi

# Step 3: If CLI method failed, try direct push (repo might exist)
echo ""
echo "📤 Attempting to push to repository..."
echo "   (If repository doesn't exist, you'll need to create it first)"
echo ""

git push -u origin main 2>&1

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ SUCCESS! Code pushed to GitHub!"
    echo "   URL: https://github.com/${GITHUB_USERNAME}/${REPO_NAME}"
else
    echo ""
    echo "⚠️  Push failed. Repository needs to be created first."
    echo ""
    echo "📋 Quick Setup:"
    echo "   1. Go to: https://github.com/new"
    echo "   2. Repository name: $REPO_NAME"
    echo "   3. Make it Public"
    echo "   4. DO NOT check any boxes (no README, .gitignore, license)"
    echo "   5. Click 'Create repository'"
    echo ""
    echo "   Then run this script again: ./create_and_push.sh"
fi
