## 🔧 後端連線故障排除指南

### ❌ 常見問題和解決方案

#### 問題 1：後端無法啟動（ImportError）
**症狀**：PowerShell 視窗顯示找不到 `main.py` 或相關模組

**原因**：缺少必要的 Python 依賴套件

**解決方案**：
```powershell
# 方法 1：使用 requirements.txt（推薦）
pip install -r requirements.txt

# 方法 2：逐個安裝
pip install fastapi uvicorn httpx numpy plotly google-generativeai python-dotenv kaleido
```

---

#### 問題 2：連線被拒絕（Connection refused）
**症狀**：前端顯示「無法連接到 http://localhost:8000」

**原因**：
- 後端服務未正確啟動
- 埠 8000 被其他程式佔用
- 防火牆阻擋

**解決方案**：

**步驟 1：檢查後端是否運行**
```powershell
# 在新的 PowerShell 視窗中測試
curl http://localhost:8000/docs
```
如果顯示 `Connection refused`，代表後端未運行。

**步驟 2：確認埠 8000 未被佔用**
```powershell
# 查看佔用 8000 埠的程式
netstat -ano | findstr :8000

# 如果有程式佔用，可以強制結束（xxx 是 PID）
taskkill /PID xxx /F

# 或修改後端埠號（在 backend/main.py 最後修改）
```

**步驟 3：手動啟動後端**
```powershell
cd backend
python run_backend.py
```

期望輸出：
```
============================================================
🚀 Crypto-AI 後端服務啟動中...
============================================================
📊 API 文檔: http://localhost:8000/docs
🔧 健康檢查: http://localhost:8000/health
============================================================
```

---

#### 問題 3：Gemini API 錯誤
**症狀**：AI 深度分析功能無法使用，但其他功能正常

**原因**：
- 未設置 `GEMINI_API_KEY` 環境變數
- API Key 無效或已過期

**解決方案**：

**步驟 1：創建 `.env` 檔案**
在 `backend/` 目錄創建 `.env` 檔案：
```
GEMINI_API_KEY=AIza...你的API密鑰...
```

**步驟 2：取得 Google Gemini API Key**
1. 訪問 [Google AI Studio](https://aistudio.google.com/app/apikey)
2. 點擊「Create API key」
3. 複製 API 密鑰到 `.env` 檔案

**步驟 3：重啟後端**
重新運行 `run_backend.py`，應該會看到：
```
✓ Google Gemini API 已配置 - AI 深度分析功能已啟用
```

**注意**：如果沒有 Gemini API Key，系統仍可用，只是無法使用 AI 分析功能。

---

#### 問題 4：前端無法啟動
**症狀**：前端伺服器無法啟動或無法訪問

**原因**：
- Python http.server 無法啟動
- 埠 3000 被佔用

**解決方案**：

**方法 1：手動啟動前端伺服器**
```powershell
cd frontend
python -m http.server 3000
```

**方法 2：使用其他埠**
```powershell
# 使用埠 5000
python -m http.server 5000

# 然後在瀏覽器訪問 http://localhost:5000
```

**方法 3：檢查埠佔用**
```powershell
netstat -ano | findstr :3000
# 強制結束佔用程式
taskkill /PID xxx /F
```

---

### ✅ 完整啟動檢查清單

- [ ] **安裝依賴**
  ```powershell
  pip install -r requirements.txt
  ```

- [ ] **設置 Gemini API**（可選，但推薦）
  ```
  在 backend/ 創建 .env 檔案，設置 GEMINI_API_KEY
  ```

- [ ] **啟動後端**
  ```powershell
  cd backend
  python run_backend.py
  ```
  期望看到：`🚀 Crypto-AI 後端服務啟動中...`

- [ ] **測試後端連接**
  在另一個 PowerShell 視窗執行：
  ```powershell
  curl http://localhost:8000/docs
  ```

- [ ] **啟動前端**
  ```powershell
  cd frontend
  python -m http.server 3000
  ```

- [ ] **訪問應用**
  在瀏覽器打開 `http://localhost:3000`

---

### 🐛 調試技巧

**查看詳細日誌**
修改 `backend/main.py` 頂部的日誌級別：
```python
logging.basicConfig(level=logging.DEBUG)  # 改為 DEBUG
```

**測試 API 端點**
```powershell
# 測試健康檢查
curl http://localhost:8000/health

# 測試技術分析
curl "http://localhost:8000/analyze?symbol=BTCUSDT&interval=1h"

# 查看 API 文檔
# 在瀏覽器打開 http://localhost:8000/docs
```

**檢查 Python 版本**
```powershell
python --version
# 應為 Python 3.8+
```

---

### 📞 仍有問題？

1. **查看錯誤日誌** - 注意 PowerShell 視窗中的完整錯誤信息
2. **檢查依賴安裝** - `pip list | grep -E "fastapi|uvicorn|httpx"`
3. **確認網路連接** - 測試 `curl https://api.bybit.com/v5/market/kline`
4. **嘗試重新安裝** - `pip install --upgrade -r requirements.txt`

