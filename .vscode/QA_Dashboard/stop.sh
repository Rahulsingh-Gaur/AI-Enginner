#!/bin/bash

# QA Dashboard - Stop Script

echo "╔══════════════════════════════════════════════════════════╗"
echo "║                                                          ║"
echo "║     🛑 Stopping QA Dashboard...                          ║"
echo "║                                                          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Find and kill the server process
PID=$(lsof -t -i :3000)

if [ -n "$PID" ]; then
    echo "Found server process (PID: $PID), stopping..."
    kill $PID
    sleep 2
    
    # Force kill if still running
    if ps -p $PID > /dev/null 2>&1; then
        echo "Force stopping..."
        kill -9 $PID
    fi
    
    echo "✅ QA Dashboard stopped"
    osascript -e 'display notification "QA Dashboard has been stopped" with title "🛑 QA Dashboard"'
else
    echo "⚠️  No server found running on port 3000"
fi
