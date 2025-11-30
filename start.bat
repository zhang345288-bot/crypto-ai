@echo off
REM Crypto-AI User Release - One-Click Launcher
REM Double-click this file to start the system

setlocal enabledelayedexpansion

cd /d "%~dp0"

echo.
echo ============================================================
echo   Crypto-AI 加密貨幣 AI 投資分析系統
echo   啟動中...
echo ============================================================
echo.

REM Start backend from project root
echo 🚀 啟動後端服務 (Port 8000)...
start "CryptoAI Backend" cmd /k python backend\run_backend.py

timeout /t 3

REM Start frontend - change to frontend dir first, then start server
echo 🌐 啟動前端伺服器 (Port 3000)...
if exist "frontend\index.html" (
    start "CryptoAI Frontend" cmd /k "cd /d "%~dp0frontend" & python -m http.server 3000"
    timeout /t 2
    echo 🌍 在瀏覽器中打開應用...
    start "" "http://localhost:3000"
) else (
    echo ⚠️  前端檔案未找到，但後端已運行
    echo    API 文檔: http://localhost:8000/docs
)

echo.
echo ============================================================
echo ✓ Crypto-AI 已啟動！
echo.
echo 📱 前端: http://localhost:3000
echo 🔧 後端 API 文檔: http://localhost:8000/docs
echo 🏥 健康檢查: http://localhost:8000/health
echo.
echo 💡 提示: 關閉任一 PowerShell 視窗會停止相應服務
echo ============================================================
echo.

pause
