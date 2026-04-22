#!/usr/bin/env python3
"""
Crypto-AI Backend Launcher
啟動後端服務 (Port 8000)

注意：此腳本必須從專案根目錄執行，或從 backend/ 目錄執行
執行方法：
  - 從專案根目錄：python .\backend\run_backend.py
  - 從 backend 目錄：python run_backend.py
"""

import os
import sys
import logging
from pathlib import Path

# 確定當前位置
current_file = Path(__file__).resolve()
backend_dir = current_file.parent
project_root = backend_dir.parent

# 清理 sys.path，移除任何指向 backend 目錄下套件的路徑
# （這些是不完整的本地套件，會導致 ModuleNotFoundError）
sys.path = [p for p in sys.path if 'backend' not in str(p).lower() or str(p) == str(backend_dir)]

# 確保 backend 目錄在路徑中（用於導入 main.py）
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    try:
        # 導入 FastAPI 應用
        from main import app
        import uvicorn

        print("\n" + "="*60)
        print("🚀 Crypto-AI 後端服務啟動中...")
        print("="*60)
        print("📊 API 文檔: http://localhost:8000/docs")
        print("🔧 健康檢查: http://localhost:8000/health")
        print("="*60 + "\n")

        # 啟動 Uvicorn
        uvicorn.run(
            app,
            host='0.0.0.0',
            port=8000,
            log_level='info'
        )

    except ModuleNotFoundError as e:
        print(f"\n❌ 模組導入錯誤: {e}")
        print("\n問題排查:")
        print("1. 確認 Python 環境已安裝所有依賴:")
        print("   pip install -r requirements.txt")
        print("\n2. 或手動安裝依賴包:")
        print("   pip install fastapi uvicorn httpx numpy plotly google-generativeai python-dotenv kaleido")
        print("\n3. 確認執行位置: 應從專案根目錄執行")
        print("   cd 到專案根目錄，再執行: python .\backend\run_backend.py")
        print("\n4. 若使用虛擬環境，確認已啟用:")
        print("   .\\venv\\Scripts\\Activate.ps1")
        logger.exception("詳細錯誤信息:")
        sys.exit(1)

    except Exception as e:
        print(f"\n❌ 啟動失敗: {e}")
        print(f"詳細信息: {type(e).__name__}")
        logger.exception("完整堆棧追蹤:")
        sys.exit(1)
