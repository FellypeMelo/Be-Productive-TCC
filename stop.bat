@echo off
REM Be-Productive - Robust Stop Script for Windows
REM Stops all running services and clears bound ports

echo Stopping Be-Productive services...

REM 1. Kill the Frontend (Node.js)
echo ... Stopping Frontend
taskkill /f /im node.exe >nul 2>nul

REM 2. Kill the Backend (Go)
echo ... Stopping Backend
taskkill /f /im main.exe >nul 2>nul
taskkill /f /im server.exe >nul 2>nul
taskkill /f /im go.exe >nul 2>nul

REM 3. Kill the Recommender (Python/Uvicorn)
echo ... Stopping Recommender
taskkill /f /im python.exe >nul 2>nul
taskkill /f /im uvicorn.exe >nul 2>nul

REM 4. Port Cleanup Fallback (ensures no "bind: address already in use" errors)
echo ... Clearing ports 8080, 8002, 5173
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8080 ^| findstr LISTENING') do taskkill /f /pid %%a >nul 2>nul
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5173 ^| findstr LISTENING') do taskkill /f /pid %%a >nul 2>nul
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8002 ^| findstr LISTENING') do taskkill /f /pid %%a >nul 2>nul

echo.
echo ==========================================
echo    All services and ports cleared.
echo ==========================================
pause
