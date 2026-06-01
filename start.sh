#!/bin/bash
# NetworkAI - Start AI Dashboard in Screen
# Usage: ./start.sh

SESSION_NAME="AI"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/ai.log"

# Kill existing session if running
screen -S "$SESSION_NAME" -X quit 2>/dev/null

echo "============================================"
echo "  NetworkAI - Starting Dashboard"
echo "============================================"
echo ""
echo "Press Ctrl+A, then D to detach"
echo "Use 'screen -r AI' to reconnect"
echo ""

# Start in screen
cd "$SCRIPT_DIR"
screen -dmS "$SESSION_NAME" bash -c "python3 dashboard.py 2>&1 | tee $LOG_FILE; exec bash"

sleep 2

# Check if running
if screen -list | grep -q "$SESSION_NAME"; then
    echo ""
    echo -e "\033[0;32m[✓] NetworkAI started successfully!\033[0m"
    echo ""
    echo "Connect with:  screen -r AI"
    echo "Logs:         tail -f ai.log"
    echo ""
    echo "Access Dashboard at: http://$(hostname -I | awk '{print $1}'):5000"
else
    echo ""
    echo -e "\033[0;31m[✗] Failed to start. Check logs: cat ai.log\033[0m"
fi