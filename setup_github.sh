#!/bin/bash

# Setup GitHub repository and push code
GITHUB_USERNAME="JayeshVelivela"
REPO_NAME="multi-tenant-document-processing-platform"
REPO_URL="https://github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"

echo "🚀 Setting up GitHub repository..."
echo "   Username: $GITHUB_USERNAME"
echo "   Repository: $REPO_NAME"
echo ""

# Check if remote already exists
if git remote get-url origin > /dev/null 2>&1; then
    echo "⚠️  Remote 'origin' already exists"
    CURRENT_URL=$(git remote get-url origin)
    echo "   Current URL: $CURRENT_URL"
    read -p "   Replace it? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git remote remove origin
    else
        echo "❌ Aborted. Please remove the remote manually if needed."
        exit 1
    fi
fi

# Add remote
echo "📡 Adding remote repository..."
git remote add origin "$REPO_URL"

# Check if we can access the repo
echo "🔍 Checking repository status..."
if git ls-remote --heads origin main > /dev/null 2>&1; then
    echo "✅ Repository exists and is accessible"
    echo ""
    echo "📤 Pushing code to GitHub..."
    git push -u origin main
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ Successfully pushed to GitHub!"
        echo "   Repository URL: https://github.com/${GITHUB_USERNAME}/${REPO_NAME}"
        exit 0
    else
        echo "❌ Push failed. Please check your authentication."
        exit 1
    fi
else
    echo ""
    echo "⚠️  Repository doesn't exist yet or is not accessible"
    echo ""
    echo "📋 Please create the repository first:"
    echo ""
    echo "   Option 1: Create via web browser (Easiest)"
    echo "   → Go to: https://github.com/new"
    echo "   → Repository name: $REPO_NAME"
    echo "   → Make it Public (for free hosting) or Private"
    echo "   → DO NOT initialize with README, .gitignore, or license"
    echo "   → Click 'Create repository'"
    echo ""
    echo "   Option 2: Create via GitHub CLI (if installed)"
    echo "   → Run: gh repo create $REPO_NAME --public --source=. --remote=origin --push"
    echo ""
    echo "   After creating the repository, run this script again:"
    echo "   ./setup_github.sh"
    echo ""
    echo "   Or manually push with:"
    echo "   git push -u origin main"
    exit 1
fi

