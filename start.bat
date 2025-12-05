@echo off
REM Crypto-AI User Release - One-Click Launcher
REM This launcher will prefer a bundled backend executable if present,
REM otherwise it will attempt to activate a `.venv` and run the backend.

setlocal enabledelayedexpansion

cd /d "%~dp0"

REM Start backend (delegated to PowerShell script which handles .venv or bundled exe)
echo Starting Crypto-AI Backend...
start "CryptoAI Backend" powershell -NoExit -ExecutionPolicy Bypass -File "%~dp0backend\start_backend.ps1"

timeout /t 2

REM Start frontend (delegated to PowerShell script)
if exist "frontend\index.html" (
    echo Starting Frontend Server...
    start "CryptoAI Frontend" powershell -NoExit -ExecutionPolicy Bypass -File "%~dp0frontend\start_frontend.ps1"
    timeout /t 2
    echo Opening browser...
    start "" "http://localhost:3000"
) else (
    echo Frontend files not found. Backend is running at http://localhost:8000/docs
)

echo.
echo Crypto-AI startup attempted.
echo - Backend window: "CryptoAI Backend"
echo - Frontend window: "CryptoAI Frontend"
echo.
echo Close the PowerShell windows to stop the services.
pause
