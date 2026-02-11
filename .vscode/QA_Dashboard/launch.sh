#!/bin/bash

# QA Dashboard - One-Click Launcher
# Usage: ./launch.sh or double-click in Finder

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "╔══════════════════════════════════════════════════════════╗"
echo "║                                                          ║"
echo "║     🚀 QA Dashboard - One-Click Launcher                 ║"
echo "║                                                          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "${RED}❌ Node.js is not installed!${NC}"
    echo "Please install Node.js from https://nodejs.org/"
    osascript -e 'display alert "Node.js Required" message "Please install Node.js from https://nodejs.org/"'
    exit 1
fi

echo "${GREEN}✓ Node.js found:${NC} $(node --version)"

# Check if server is already running
if lsof -i :3000 &> /dev/null; then
    echo "${YELLOW}⚠️  Server is already running on port 3000${NC}"
    echo "${GREEN}🌐 Opening browser...${NC}"
    open "http://localhost:3000"
    sleep 1
    osascript -e 'display notification "QA Dashboard opened in browser" with title "QA Dashboard"'
    exit 0
fi

# Navigate to backend directory
cd backend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo ""
    echo "${YELLOW}📦 Installing dependencies (first time only)...${NC}"
    npm install
    
    if [ $? -ne 0 ]; then
        echo "${RED}❌ Failed to install dependencies${NC}"
        osascript -e 'display alert "Installation Failed" message "Failed to install dependencies. Check terminal for details."'
        exit 1
    fi
    echo "${GREEN}✓ Dependencies installed${NC}"
fi

# Check if database exists
if [ ! -f "../database/qa_dashboard.db" ]; then
    echo ""
    echo "${YELLOW}🗄️  Initializing database (first time only)...${NC}"
    npm run init-db
    
    if [ $? -ne 0 ]; then
        echo "${RED}❌ Failed to initialize database${NC}"
        exit 1
    fi
    echo "${GREEN}✓ Database initialized${NC}"
fi

echo ""
echo "${GREEN}🚀 Starting QA Dashboard Server...${NC}"
echo "${BLUE}⏳ Please wait while the server starts...${NC}"
echo ""

# Start the server in background
npm start > /dev/null 2>&1 &
SERVER_PID=$!

# Wait for server to be ready
echo "${YELLOW}⏳ Waiting for server to start...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:3000/api/health > /dev/null 2>&1; then
        echo "${GREEN}✓ Server is ready!${NC}"
        break
    fi
    sleep 1
    echo -n "."
done

echo ""
echo "${GREEN}🌐 Opening browser...${NC}"

# Open the dashboard in default browser
open "http://localhost:3000"

# Also try to open Dashboard.HTML as fallback (for offline use)
sleep 2
if [ -f "../Dashboard.HTML" ]; then
    # Check if server is responding
    if ! curl -s http://localhost:3000/api/health > /dev/null 2>&1; then
        echo "${YELLOW}⚠️  Server not responding, opening static file...${NC}"
        open "../Dashboard.HTML"
    fi
fi

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  ${GREEN}✅ QA Dashboard is running!${NC}                           ║"
echo "║                                                          ║"
echo "║  🌐 URL: http://localhost:3000                          ║"
echo "║  📁 Location: $SCRIPT_DIR"
echo "║                                                          ║"
echo "║  ${YELLOW}To stop:${NC} Run ./stop.sh or press Ctrl+C              ║"
echo "╚══════════════════════════════════════════════════════════╝"

# Show macOS notification
osascript -e 'display notification "QA Dashboard is running at http://localhost:3000" with title "✅ QA Dashboard Started"'

# Keep the terminal window open
read -p "Press Enter to close this window..."
