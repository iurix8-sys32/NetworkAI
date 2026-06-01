#!/bin/bash
# NetworkAI - Stop AI Dashboard

echo "Stopping NetworkAI..."
screen -S AI -X quit 2>/dev/null
echo "Done."