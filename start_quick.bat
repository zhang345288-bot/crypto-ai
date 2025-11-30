@echo off
REM Crypto-AI 快速啟動腳本 - 包含依賴檢查和錯誤處理

setlocal enabledelayedexpansion

cd /d "%~dp0"

echo.
echo ============================================================
echo   Crypto-AI 加密貨幣 AI 投資分析系統
echo   Quick Start Script
echo ============================================================
echo.

REM 檢查 Python 是否已安裝
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 錯誤: Python 未安裝或不在 PATH 中
    echo.
    echo 請訪問 https://www.python.org/downloads/ 安裝 Python 3.8+
    echo.
    pause
    exit /b 1
)

echo ✓ Python 已檢測到
python --version

REM 檢查並安裝依賴
echo.
echo 📦 檢查 Python 依賴...

pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo ⚠️  缺少依賴，正在安裝...
    echo.
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ 依賴安裝失敗
        pause
        exit /b 1
    )
    echo ✓ 依賴已安裝
)

REM 檢查 .env 檔案
echo.
echo 🔑 檢查 API 配置...

if not exist "backend\.env" (
    echo ⚠️  backend\.env 未找到
    echo.
    echo 如要啟用 Google Gemini AI 功能，請:
    echo   1. 在 backend\ 目錄創建 .env 檔案
    echo   2. 添加 GEMINI_API_KEY=AIza...你的密鑰...
    echo   3. 重新啟動此腳本
    echo.
    echo 無 API Key 時，系統仍可用，只是無法使用 AI 分析功能
) else (
    echo ✓ 找到 .env 配置檔案
)

REM 啟動後端
echo.
echo 🚀 啟動後端服務 (Port 8000)...
echo.

start "Crypto-AI Backend" powershell -NoExit -Command ^
  "cd '%~dp0backend' ; ^
   python run_backend.py ; ^
   echo. ; ^
   echo ❌ 後端已關閉 ; ^
   pause"

REM 等待後端啟動
timeout /t 3 /nobreak

REM 測試後端連接
echo.
echo 🔍 測試後端連接...

for /L %%i in (1,1,5) do (
    powershell -Command "try { $r = Invoke-WebRequest -Uri 'http://localhost:8000/docs' -TimeoutSec 2 -ErrorAction Stop; exit 0 } catch { exit 1 }"
    if !errorlevel! equ 0 (
        echo ✓ 後端已連接成功
        goto frontend_start
    )
    echo   嘗試中... (%%i/5)
    timeout /t 1 /nobreak
)

echo ⚠️  無法連接到後端服務
echo 請檢查後端視窗中的錯誤信息
echo.
pause

:frontend_start
REM 啟動前端
echo.
if exist "frontend\index.html" (
    echo 🌐 啟動前端伺服器 (Port 3000)...
    echo.
    start "Crypto-AI Frontend" powershell -NoExit -Command ^
      "cd '%~dp0frontend' ; ^
       python -m http.server 3000 ; ^
       echo. ; ^
       echo ❌ 前端已關閉 ; ^
       pause"
    
    timeout /t 2 /nobreak
    
    echo 🌍 在瀏覽器中打開應用...
    start "" "http://localhost:3000"
) else (
    echo ⚠️  前端檔案不存在
    echo 後端 API 文檔: http://localhost:8000/docs
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
