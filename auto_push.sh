#!/bin/bash

# Auto-push script that waits for repository to be created
GITHUB_USERNAME="JayeshVelivela"
REPO_NAME="multi-tenant-document-processing-platform"
REPO_URL="https://github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"

echo "🔄 Auto-push script running..."
echo "   Waiting for repository to be created..."
echo ""

# Ensure remote is set
if ! git remote get-url origin > /dev/null 2>&1; then
    git remote add origin "$REPO_URL"
fi

# Try pushing (will retry if repo doesn't exist)
MAX_ATTEMPTS=10
ATTEMPT=1

while [ $ATTEMPT -le $MAX_ATTEMPTS ]; do
    echo "📤 Attempt $ATTEMPT/$MAX_ATTEMPTS: Checking repository..."
    
    # Check if repo exists
    if git ls-remote --heads origin main > /dev/null 2>&1; then
        echo "✅ Repository found! Pushing code..."
        git push -u origin main
        if [ $? -eq 0 ]; then
            echo ""
            echo "🎉 SUCCESS! Code pushed to GitHub!"
            echo "   Repository: https://github.com/${GITHUB_USERNAME}/${REPO_NAME}"
            exit 0
        fi
    else
        echo "   ⏳ Repository not found yet. Waiting 5 seconds..."
        sleep 5
    fi
    
    ATTEMPT=$((ATTEMPT + 1))
done

echo ""
echo "⚠️  Repository not created yet or not accessible."
echo "   Please create it at: https://github.com/new"
echo "   Then run this script again: ./auto_push.sh"

