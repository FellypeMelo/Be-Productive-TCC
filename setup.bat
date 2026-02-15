@echo off
REM Be-Productive - Setup Script for Windows
REM Run this script once to install all dependencies

echo ==========================================
echo    Be-Productive - Setup
echo ==========================================
echo.

REM Check Node.js
echo [1/4] Checking Node.js...
where node >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo ERROR: Node.js not found. Please install from https://nodejs.org
    pause
    exit /b 1
)
node --version

REM Check Python
echo.
echo [2/4] Checking Python...
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo ERROR: Python not found. Please install from https://python.org
    pause
    exit /b 1
)
python --version

REM Install Frontend dependencies
echo.
echo [3/4] Installing Frontend dependencies...
cd frontend
call npm install
if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to install frontend dependencies
    pause
    exit /b 1
)
cd ..

REM Check Go
echo.
echo [3/5] Checking Go...
where go >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo ERROR: Go not found. Please install from https://go.dev
    pause
    exit /b 1
)
go version

REM Build Backend
echo.
echo [4/5] Building Backend...
cd backend
go mod tidy
go build -o server.exe ./cmd/server/main.go
if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to build backend
    pause
    exit /b 1
)
cd ..

REM Install Python dependencies
echo.
echo [5/5] Installing Python dependencies...
cd recommender
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)
call venv\Scripts\activate.bat
echo Installing requirements...
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo WARNING: Some Python dependencies failed to install. 
    echo Check recommender/requirements.txt for details. 
    echo Recommender might run in fallback mode.
)
call venv\Scripts\deactivate.bat
cd ..

echo.
echo ==========================================
echo    Setup Complete!
echo ==========================================
echo.
echo Next steps:
echo   1. Start MySQL (XAMPP/Docker)
echo   2. Seed Database and Run Migrations:
echo      cd backend
echo      go run cmd/seeder/main.go
echo   3. Start all services:
echo      call start.bat
echo.
pause

