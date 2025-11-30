@echo off
REM Crypto-AI User Release - One-Click Launcher
REM Double-click this file to start the system

setlocal enabledelayedexpansion

cd /d "%~dp0"

REM Start backend
echo Starting Crypto-AI Backend...
start "CryptoAI Backend" powershell -NoExit -Command "cd '%~dp0backend' ; python run_backend.py"

timeout /t 2

REM Start frontend if available
if exist "frontend\index.html" (
    echo Starting Frontend Server...
    start "CryptoAI Frontend" powershell -NoExit -Command "cd '%~dp0frontend' ; python -m http.server 3000"
    timeout /t 2
    echo Opening browser...
    start "" "http://localhost:3000"
) else (
    echo Frontend files not found. Backend is running at http://localhost:8000/docs
)

echo.
echo Crypto-AI is now running:
echo   Frontend: http://localhost:3000
echo   Backend API Docs: http://localhost:8000/docs
echo.
echo Close the PowerShell windows to stop the services.
pause
