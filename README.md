# Crypto-AI 使用者快速啟動指南

歡迎使用 Crypto-AI 系統！這份指南將幫助你快速啟動整套系統。

## 資料夾結構

```
crypto-ai-user-release/
├── start.bat           ← 雙擊這個檔案啟動系統（會自動選擇已打包的後端執行檔，或啟用 `.venv`）
├── README.md           ← 你正在看的說明
├── backend/            ← 後端程式碼（注意：此專案有兩種發行方式，請閱讀下方說明）
│   ├── run_backend.py
│   ├── start_backend.ps1  ← 後端啟動腳本（會自動啟用 `.venv` 或執行打包 exe）
│   └── [其他檔案...]
└── frontend/           ← 前端靜態檔案
   └── index.html
```

## 必要條件

發行模式說明：

- 打包版（推薦給非開發者下載）：release 可能包含一個已打包的後端可執行檔（Windows: `backend\crypto_ai_backend.exe`）。這種情況使用者只需雙擊 `start.bat` 即可啟動（不需另外安裝 Python 與套件）。
- 原始碼版（需要 Python）：如果 release 未包含打包執行檔，使用者須自行安裝 Python 3.11 並建立虛擬環境來安裝套件（`requirements.txt`）。

請依照你下載的 release 類型採取下列步驟：

檢查 Python（若使用原始碼版，需要 Python 3.11）：
```
python --version
```

若未安裝 Python（或你想使用原始碼版），請至官方下載： https://www.python.org/downloads/ （選擇 Python 3.11），安裝時建議勾選「Add Python to PATH」。

## 最簡單的啟動方式（推薦）

1. **雙擊 `start.bat`**（在這個資料夾）
   - 如果 release 包含 `backend\crypto_ai_backend.exe`，啟動程式會直接執行該可執行檔。
   - 否則 `start.bat` 會嘗試啟用專案內的 `.venv`（若存在）並啟動後端；若 `.venv` 不存在，會顯示建立環境的提示。
   - 會自動開啟兩個 PowerShell 視窗（後端與前端）並在瀏覽器開啟 `http://localhost:3000`（前端）

2. **查看系統運行狀況**
   - 前端：`http://localhost:3000`
   - 後端 API 文件：`http://localhost:8000/docs`

3. **停止系統**
   - 關閉那兩個 PowerShell 視窗，或在視窗中按 `Ctrl+C`

## 命令列啟動（進階）

如果你熟悉 PowerShell / CMD，也可以手動啟動（原始碼版）：

建立並啟用虛擬環境（只需做一次）：
```powershell
cd 'C:\path\to\crypto-ai-user-release'
python -m venv .venv
# 若第一次使用 PowerShell 需允許執行策略（只做一次）
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
. .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

啟動後端（在已啟用 venv 的視窗）：
```powershell
cd backend
python run_backend.py
```

啟動前端（在 `frontend` 目錄啟動靜態伺服器）：
```powershell
cd frontend
python -m http.server 3000
```

## 常見問題

### Q: 雙擊 start.bat 沒反應
**A**: 檢查是否安裝 Python。開啟命令提示字元，輸入 `python --version`。

### Q: 出現 ModuleNotFoundError 錯誤
**A**: 表示執行後端的 Python 環境沒有安裝所需套件。常見情況：

- 你下載的是原始碼版但尚未建立或啟用 `.venv`；或是你雙擊 `start.bat`，新開的 PowerShell 視窗沒有啟用 `.venv`，因此會使用系統 Python（可能未安裝套件）。

處理步驟（原始碼版）請參考上面的「建立並啟用虛擬環境」指令，或執行：
```powershell
python -m venv .venv
. .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

若你希望使用不需安裝依賴的單一可執行檔，請下載包含已打包後端執行檔的 Release（通常檔名會放在 `backend/` 裡，例如 `crypto_ai_backend.exe`）。

### Q: 端口 3000 或 8000 已被佔用
**A**: 
- 若要改用其他端口，編輯 `start.bat` 中的 `3000` 或 `8000`
- 或在命令列啟動時改用其他 port：`python -m http.server 3001`

### Q: 瀏覽器無法連到 localhost
**A**: 
- 確認後端與前端都在運行（PowerShell 視窗沒有關閉）
- 檢查防火牆是否允許 Python 網路存取（通常首次啟動會跳出提示）
- 在瀏覽器按 F12 檢查控制台是否有錯誤訊息

### Q: 如何停止服務
**A**: 關閉 PowerShell 視窗，或在視窗中按 `Ctrl+C`

## 回報問題

如果遇到問題，請將錯誤訊息與 PowerShell 中的輸出截圖回報給維護者。

---

祝使用順利！
