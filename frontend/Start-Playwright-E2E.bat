@echo off
setlocal enabledelayedexpansion

echo.
echo ============================================
echo  Be-Productive: Playwright E2E Test Runner
echo ============================================
echo.

cd /d "%~dp0"

echo [1/3] Checking Go backend on port 8080...
netstat -ano | findstr ":8080" >nul 2>nul
if not errorlevel 1 (
    echo   Go backend is already running.
) else (
    echo   Starting Go backend...
    start "Go Backend" /min cmd /k "cd ..\backend && go run cmd/server/main.go"
    echo   Waiting 10 seconds for backend startup...
    timeout /t 10 /nobreak >nul
    netstat -ano | findstr ":8080" >nul 2>nul || goto :NO_BACKEND
)

echo.
echo [2/3] Checking Python recommender on port 8002...
netstat -ano | findstr ":8002" >nul 2>nul
if not errorlevel 1 (
    echo   Python recommender is already running.
) else (
    echo   Starting Python recommender...
    start "Python Recommender" /min cmd /k "cd ..\recommender && venv\Scripts\activate && uvicorn src.api.main:app --port 8002 --reload"
    echo   Waiting 10 seconds for recommender startup...
    timeout /t 10 /nobreak >nul
)

echo.
echo [3/3] Running Playwright E2E tests...
echo.
call npx playwright test --reporter=list
set E2E_EXIT=%errorlevel%

echo.
echo ============================================
if %E2E_EXIT% equ 0 (
    echo  E2E Tests PASSED
) else (
    echo  E2E Tests FAILED (exit code: %E2E_EXIT%)
)
echo ============================================
echo.
pause

exit /b %E2E_EXIT%

:NO_BACKEND
echo   ERROR: Go backend failed to start. Please check:
echo     - MySQL is running
echo     - Database 'be_productive' exists
echo     - .env is configured in .\..\backend\
echo.
pause
exit /b 1
