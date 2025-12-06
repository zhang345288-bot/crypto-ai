# 智慧加密貨幣投資建議系統 (Crypto-AI)

**Crypto-AI** 是一款智能化的加密貨幣投資建議系統，透過技術指標分析與 AI 模型協助投資者做出更明智的投資決策。

---

## 🚀 快速啟動

### 最簡單的方式：雙擊 `start.bat`

1. 在當前資料夾找到 **`start.bat`** 並**雙擊執行**
2. 系統會自動啟動後端與前端服務
3. 稍候片刻，瀏覽器會自動開啟前端介面（`http://localhost:3000`）
4. 開始使用系統！

> **首次啟動可能花費 30 秒至 1 分鐘**，因為系統需要安裝所需套件。請耐心等待。

### 要求

- **Windows** 系統（PowerShell）
- **Python 3.11** 或更高版本（如未安裝，[點此下載](https://www.python.org/downloads/)，安裝時勾選「Add Python to PATH」）

---

## 📖 系統使用指南

### 前端介面

系統啟動後自動在 `http://localhost:3000` 開啟。

**主要功能：**

1. **選擇加密貨幣**
   - 在首頁選擇你想分析的加密貨幣（如 BTC、ETH、SOL 等）
   - 系統會顯示該貨幣的實時行情與技術指標圖表

2. **技術指標分析**
   - 系統自動計算 K 線圖、移動平均線、RSI、MACD 等指標
   - 這些指標幫助判斷買賣時機

3. **AI 投資建議** ⭐
   - 點擊「分析」或「獲取建議」按鈕，系統會調用 AI 模型
   - AI 會根據**最近 50 個 K 線數據**與**技術指標**生成投資建議
   - 建議內容包括：是否適合買入、賣出或觀望，以及建議原因

4. **歷史數據查看**
   - 可查看過去的行情歷史與建議記錄

### AI 如何工作

1. **數據收集**
   - 系統從 Bybit 交易所實時獲取加密貨幣的 K 線數據（最近 50 條）

2. **技術指標計算**
   - 計算移動平均線 (MA)、相對強度指數 (RSI)、MACD 等指標
   - 這些指標反映市場動量與趨勢

3. **AI 分析**
   - 將上述數據與指標輸入 AI 模型（Google Gemini）
   - AI 根據歷史模式與市場情況生成投資建議

4. **建議輸出**
   - 系統返回「買入」、「賣出」、「觀望」等建議
   - 並附帶詳細分析理由

**注意：** AI 建議僅供參考，投資決策應綜合多方信息與風險評估。過去表現不代表未來結果。

---

## ⚙️ 進階設定（可選）

### 設定 AI API Key（啟用 Gemini AI 增強分析）

系統支援 Google Gemini AI，若要啟用更智能的分析：

1. 前端啟動後，點擊右上角 **「⚙️ AI 設置」** 按鈕
2. 在彈出的「AI 深度分析設置」對話框中輸入你的 **Google Gemini API Key**
3. 點擊 **「儲存」** 按鈕，Key 會保存在本機瀏覽器快取中
4. 重新載入頁面即可開始使用 AI 建議功能

**如何獲得 Gemini API Key：**
- 前往 [Google AI Studio](https://ai.google.dev/) 
- 登入 Google 帳號並建立新的 API Key
- 複製 Key 並貼入前端設置框

> **提示：**
> - API Key 會儲存在本機 localStorage（只在你的瀏覽器中）
> - Google Gemini 免費方案含每日約 1500 次請求
> - 若未設定 API Key，系統仍可正常運作但 AI 建議功能會受限

### 手動啟動（進階用戶）

若想使用命令列手動啟動：

```powershell
# 進入系統目錄
cd 'C:\path\to\crypto-ai'

# 建立虛擬環境（首次）
python -m venv .venv

# 啟用虛擬環境
.\.venv\Scripts\Activate.ps1

# 安裝依賴
pip install -r requirements.txt

# 啟動後端
cd backend
python run_backend.py

# 另開一個 PowerShell 視窗，啟動前端
cd frontend
python -m http.server 3000
```

---

## 📍 系統地址

系統啟動後可訪問：

- **前端介面**：`http://localhost:3000` （自動打開）
- **後端 API 文檔**：`http://localhost:8000/docs` （用於開發者調試）

---

## ❓ 常見問題

### Q: 系統無法啟動 / 沒有反應
**A**: 
- 確保已安裝 Python 3.11+：`python --version`
- 關閉防火牆或允許 localhost 訪問
- 重新雙擊 `start.bat`

### Q: 出現 ModuleNotFoundError
**A**: 表示套件安裝不完整。執行以下指令重新安裝：
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Q: 端口 3000 或 8000 被佔用
**A**: 
- 關閉其他佔用這些端口的應用程式
- 或編輯 `start.bat` 改用其他端口

### Q: AI 建議不準確
**A**: 
- AI 分析基於過去 50 個 K 線與技術指標，無法 100% 準確預測市場
- 市場風險因素眾多，建議配合其他分析方法使用
- 投資需謹慎，切勿盲目跟隨建議 
- 確認後端與前端都在運行（PowerShell 視窗沒有關閉）
- 檢查防火牆是否允許 Python 網路存取（通常首次啟動會跳出提示）
- 在瀏覽器按 F12 檢查控制台是否有錯誤訊息

### Q: 如何停止服務
**A**: 關閉 PowerShell 視窗，或在視窗中按 `Ctrl+C`

## 回報問題

如果遇到問題，請將錯誤訊息與 PowerShell 中的輸出截圖回報給維護者。

---

祝使用順利！
