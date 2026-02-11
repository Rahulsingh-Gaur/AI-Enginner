#!/bin/bash

# QA Dashboard Launcher - Run this script to launch the dashboard
# This can be saved as an Automator "Application" for single-click launch

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"

# Check if server is running
if lsof -i :3000 > /dev/null 2>&1; then
    echo "Server is already running, opening browser..."
    open "http://localhost:3000"
    osascript -e 'display notification "QA Dashboard opened" with title "QA Dashboard"'
else
    echo "Starting QA Dashboard..."
    
    # Open Terminal with the launch script
    osascript <<APPLESCRIPT
tell application "Terminal"
    activate
    do script "cd '$PROJECT_DIR' && ./launch.sh"
end tell
APPLESCRIPT
fi
