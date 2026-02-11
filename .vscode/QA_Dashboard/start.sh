#!/bin/bash

# QA Task Manager - Startup Script
# Usage: ./start.sh

echo "╔══════════════════════════════════════════════════════════╗"
echo "║                                                          ║"
echo "║     🧪 QA Task Manager - Startup Script                  ║"
echo "║                                                          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "${RED}❌ Node.js is not installed!${NC}"
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi

echo "${GREEN}✓ Node.js found:${NC} $(node --version)"

# Navigate to backend directory
cd backend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo ""
    echo "${YELLOW}📦 Installing dependencies...${NC}"
    npm install
    
    if [ $? -ne 0 ]; then
        echo "${RED}❌ Failed to install dependencies${NC}"
        exit 1
    fi
    echo "${GREEN}✓ Dependencies installed${NC}"
else
    echo "${GREEN}✓ Dependencies already installed${NC}"
fi

# Check if database exists
if [ ! -f "../database/qa_dashboard.db" ]; then
    echo ""
    echo "${YELLOW}🗄️  Initializing database...${NC}"
    npm run init-db
    
    if [ $? -ne 0 ]; then
        echo "${RED}❌ Failed to initialize database${NC}"
        exit 1
    fi
    echo "${GREEN}✓ Database initialized${NC}"
else
    echo "${GREEN}✓ Database already exists${NC}"
fi

echo ""
echo "${GREEN}🚀 Starting server...${NC}"
echo ""

# Start the server
npm start
