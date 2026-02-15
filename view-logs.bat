@echo off
echo ==========================================
echo    Be-Productive - Unified Log Viewer
echo ==========================================
echo.
if not exist "logs" (
    echo [ERROR] Log directory not found. Run start.bat first.
    pause
    exit /b
)

echo Streaming: backend.log, recommender.log, frontend.log
echo [Press Ctrl+C to stop]
echo.

powershell -Command "Get-Content logs\*.log -Wait -Tail 10"
