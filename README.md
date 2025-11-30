# Crypto-AI 加密貨幣 AI 投資分析系統
## 操作說明書

**版本**：1.0.0  
**最後更新**：2025年11月30日

> 本說明書用於指導使用者如何啟動和操作系統。若需了解系統設計與技術細節，請參考《系統報告書.md》。

---

## 資料夾結構

```
crypto-ai-user-release/
├── README.md               ← 你正在看的說明書
├── 系統報告書.md           ← 系統技術文檔（開發者用）
├── start.bat              ← 一鍵啟動腳本
│
├── backend/               ← 後端系統
│   ├── main.py
│   ├── chart_generator.py
│   ├── run_backend.py
│   └── [依賴套件...]
│
└── frontend/              ← 前端應用
    ├── index.html
    └── static/
```

---

## ⚙️ 系統需求

### 必要條件

- **Python 3.11+**（必須安裝）
- **網際網路連接**（調用市場數據 API）
- **瀏覽器**（Chrome、Firefox、Edge 等）

### 檢查 Python 安裝

開啟命令提示字元或 PowerShell，輸入：

```powershell
python --version
```

應該看到 `Python 3.11.x` 或更高版本。

若顯示「python 不是內部或外部命令」，表示需要安裝 Python：

#### 📥 安裝 Python 3.11

1. 訪問 [python.org](https://www.python.org/downloads/)
2. 下載 **Python 3.11** 版本
3. 執行安裝程式，**務必勾選** ✓ **「Add Python to PATH」**
4. 選擇預設安裝位置，點擊「Install Now」

> ⚠️ 務必勾選「Add Python to PATH」，否則無法在命令列使用 python 命令。

---

## 🚀 快速啟動

### 方式一：一鍵啟動（推薦 ⭐）

**步驟 1**：找到工作目錄下的 `start.bat` 檔案

**步驟 2**：雙擊執行 `start.bat`

**步驟 3**：稍等片刻，會自動：
- 🔵 開啟後端伺服器（PowerShell 視窗 1）
- 🔵 開啟前端伺服器（PowerShell 視窗 2）
- 🌐 自動打開瀏覽器進入系統

✅ **完成！** 看到網頁載入後即可開始使用

### 方式二：手動啟動（進階用戶）

如果一鍵啟動失效，可以手動啟動。

#### 啟動後端

開啟 PowerShell / CMD，進入專案目錄：

```powershell
cd backend
python run_backend.py
```

看到類似訊息代表成功：
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

#### 啟動前端（新開一個 PowerShell）

```powershell
cd frontend
python -m http.server 3000
```

看到類似訊息代表成功：
```
Serving HTTP on 0.0.0.0 port 3000
```

#### 打開瀏覽器

在瀏覽器網址欄輸入：
```
http://localhost:3000
```

---


## 🔑 AI 分析功能（選用）

### 啟用 AI 分析的三種方式

#### 方式一：使用 `.env` 檔案（推薦）

1. 在 `backend` 資料夾建立 `.env` 檔案
2. 填入以下內容：

```
GEMINI_API_KEY=AIza_your_api_key_here
```

3. 重啟後端系統

#### 方式二：系統環境變數

**Windows**：
```
設定 > 系統 > 進階系統設定 > 環境變數
新增：變數名稱 = GEMINI_API_KEY，值 = AIza_...
```

#### 方式三：前端動態輸入

啟動系統後，在網頁上直接輸入 API key，系統會即時使用。

### 獲取 Google Gemini API Key

1. 訪問 [Google AI Studio](https://aistudio.google.com/apikey)
2. 點擊「Create API Key」
3. 選擇或建立 Google Cloud 專案
4. 複製生成的 API key（格式：`AIza_...`）
5. 使用上述三種方式之一設置

> 💡 免費版本有每日配額限制，建議用於測試。

### 無 API Key 也能用？

**可以！** 系統會正常工作，但無法生成 AI 分析報告。所有技術指標和買賣建議仍然可用。
