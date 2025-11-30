@echo off
REM Crypto-AI User Release - One-Click Launcher
REM Double-click this file to start the system

setlocal enabledelayedexpansion

cd /d "%~dp0"

echo.
echo ============================================================
echo   Crypto-AI - 啟動中...
echo ============================================================
echo.

REM Start backend from project root
echo Starting backend on port 8000...
start "CryptoAI Backend" cmd /k python backend\run_backend.py

timeout /t 3

REM Start frontend if available
echo Starting frontend on port 3000...
if exist "frontend\index.html" (
    start "CryptoAI Frontend" cmd /k "cd /d %~dp0frontend && python -m http.server 3000"
    timeout /t 2
    echo Opening browser at http://localhost:3000
    start "" "http://localhost:3000"
) else (
    echo Frontend files not found. Backend is running at http://localhost:8000/docs
)

echo.
echo ============================================================
echo Crypto-AI started.
echo Frontend: http://localhost:3000
echo Backend: http://localhost:8000/docs
echo Health: http://localhost:8000/health
echo ============================================================
echo.

pause
