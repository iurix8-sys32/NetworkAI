#!/bin/bash
# NetworkAI - Update Script
# Pulls latest changes while preserving local data

echo "============================================"
echo "  NetworkAI - Update"
echo "============================================"
echo ""

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_DIR"

# Files to preserve (won't be overwritten)
PRESERVE_FILES=(
    "/tmp/.gh_token.enc"
    "/tmp/.gh_token.salt"
    "ai.log"
)

echo "[*] Checking for updates..."

# Stash local changes but keep untracked important files
# We need to be careful here

# Check if there are updates
git fetch origin main 2>/dev/null

LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)

if [ "$LOCAL" = "$REMOTE" ]; then
    echo "[✓] Already up to date!"
    exit 0
fi

echo "[!] New version available!"
echo ""
echo "Local:  $LOCAL"
echo "Remote: $REMOTE"
echo ""

# Create backup of critical files
echo "[*] Backing up critical files..."
BACKUP_DIR="$REPO_DIR/.backup_$(date +%s)"
mkdir -p "$BACKUP_DIR"

# Backup token files if they exist
if [ -f "/tmp/.gh_token.enc" ]; then
    cp "/tmp/.gh_token.enc" "$BACKUP_DIR/"
    echo "  - Saved encrypted token"
fi

if [ -f "/tmp/.gh_token.salt" ]; then
    cp "/tmp/.gh_token.salt" "$BACKUP_DIR/"
    echo "  - Saved salt file"
fi

if [ -f "chat_history.json" ]; then
    cp "chat_history.json" "$BACKUP_DIR/"
    echo "  - Saved chat history"
fi

echo ""
echo "[*] Updating files..."

# Use git pull with strategy to preserve local changes
git stash push -m "local_changes_backup" 2>/dev/null || true

# Pull latest
git pull origin main

# Restore critical files if they were overwritten
if [ -d "$BACKUP_DIR" ]; then
    if [ -f "$BACKUP_DIR/.gh_token.enc" ] && [ ! -f "/tmp/.gh_token.enc" ]; then
        cp "$BACKUP_DIR/.gh_token.enc" "/tmp/.gh_token.enc"
        echo "[+] Restored encrypted token"
    fi
    
    if [ -f "$BACKUP_DIR/.gh_token.salt" ] && [ ! -f "/tmp/.gh_token.salt" ]; then
        cp "$BACKUP_DIR/.gh_token.salt" "/tmp/.gh_token.salt"
        echo "[+] Restored salt file"
    fi
    
    if [ -f "$BACKUP_DIR/chat_history.json" ] && [ ! -f "chat_history.json" ]; then
        cp "$BACKUP_DIR/chat_history.json" "chat_history.json"
        echo "[+] Restored chat history"
    fi
    
    # Cleanup backup
    rm -rf "$BACKUP_DIR"
fi

echo ""
echo "[✓] Update complete!"
echo ""
echo "Restarting dashboard..."
./stop.sh 2>/dev/null
sleep 1
./start.sh

echo ""
echo "[✓] Done! Check screen -r AI"