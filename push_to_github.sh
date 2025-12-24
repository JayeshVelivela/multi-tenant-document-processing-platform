#!/bin/bash

# Script to push project to GitHub

echo "🚀 Preparing to push to GitHub..."

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📦 Initializing git repository..."
    git init
    git branch -M main
fi

# Add all files
echo "📝 Adding files..."
git add .

# Check if there are changes
if git diff --staged --quiet; then
    echo "✅ No changes to commit"
else
    echo "💾 Committing changes..."
    git commit -m "Multi-Tenant Document Processing Platform with improved data extraction"
fi

# Check if remote exists
if git remote get-url origin > /dev/null 2>&1; then
    echo "📤 Pushing to existing remote..."
    git push -u origin main
else
    echo ""
    echo "⚠️  No GitHub remote configured yet!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Go to https://github.com and create a new repository"
    echo "2. Copy the repository URL (e.g., https://github.com/YOUR_USERNAME/your-repo-name.git)"
    echo "3. Run this command:"
    echo "   git remote add origin YOUR_REPO_URL"
    echo "   git push -u origin main"
    echo ""
    echo "Or run this script again after adding the remote."
fi

echo ""
echo "✅ Done! Check DEPLOY_TO_GITHUB.md for deployment instructions."

