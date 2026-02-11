@echo off
chcp 65001 >nul

:: QA Task Manager - Startup Script for Windows
:: Usage: start.bat

echo ╔══════════════════════════════════════════════════════════╗
echo ║                                                          ║
echo ║     🧪 QA Task Manager - Startup Script                  ║
echo ║                                                          ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

:: Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed!
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

echo ✓ Node.js found

:: Navigate to backend directory
cd backend

:: Check if node_modules exists
if not exist "node_modules" (
    echo.
    echo 📦 Installing dependencies...
    call npm install
    
    if errorlevel 1 (
        echo ❌ Failed to install dependencies
        pause
        exit /b 1
    )
    echo ✓ Dependencies installed
) else (
    echo ✓ Dependencies already installed
)

:: Check if database exists
if not exist "..\database\qa_dashboard.db" (
    echo.
    echo 🗄️  Initializing database...
    call npm run init-db
    
    if errorlevel 1 (
        echo ❌ Failed to initialize database
        pause
        exit /b 1
    )
    echo ✓ Database initialized
) else (
    echo ✓ Database already exists
)

echo.
echo 🚀 Starting server...
echo.

:: Start the server
call npm start

pause
