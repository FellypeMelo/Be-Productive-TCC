@echo off
REM Be-Productive - Start Script for Windows
REM Starts Frontend and Recommender services

echo ==========================================
echo    Be-Productive - Starting Services
echo ==========================================
echo.

echo [0/3] Preparing log environment...
if not exist "logs" mkdir logs
echo Log directory initialized: %cd%\logs
echo.

REM Start Recommender (Python)
echo [1/3] Starting Recommender Service (Port 8002)...
cd recommender
start "Be-Productive Recommender" powershell -NoExit -Command "venv\Scripts\activate; uvicorn src.api.main:app --port 8002 | Tee-Object -FilePath ..\logs\recommender.log"
cd ..

REM Wait for recommender
timeout /t 3 /nobreak >nul

REM Start Backend (Go)
echo [2/3] Starting Backend Service (Port 8080)...
cd backend
start "Be-Productive Backend" powershell -NoExit -Command "go run cmd/server/main.go | Tee-Object -FilePath ..\logs\backend.log"
cd ..

REM Wait for backend
timeout /t 3 /nobreak >nul

REM Start Frontend (SvelteKit)
echo [3/3] Starting Frontend (Port 5173)...
cd frontend
start "Be-Productive Frontend" powershell -NoExit -Command "npm run dev | Tee-Object -FilePath ..\logs\frontend.log"
cd ..

echo.
echo ==========================================
echo    All Services Started!
echo ==========================================
echo.
echo Frontend:    http://localhost:5173
echo Backend API: http://localhost:8080
echo Recommender: http://localhost:8002
echo Logs:        %cd%\logs
echo.
echo Press any key to open the app in your browser...
pause >nul

start http://localhost:5173
