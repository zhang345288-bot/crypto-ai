import os
import sys
import logging

# 確保後端目錄在 Python 路徑中
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

try:
    from main import app
    import uvicorn
    
    if __name__ == '__main__':
        print("\n" + "="*60)
        print("🚀 Crypto-AI 後端服務啟動中...")
        print("="*60)
        print("📊 API 文檔: http://localhost:8000/docs")
        print("🔧 健康檢查: http://localhost:8000/health")
        print("="*60 + "\n")
        
        uvicorn.run(
            app, 
            host='0.0.0.0', 
            port=8000,
            log_level='info'
        )
except ImportError as e:
    print(f"\n❌ 導入錯誤: {e}")
    print("\n請確保已安裝所有依賴:")
    print("  pip install -r ../requirements.txt")
    print("\n或使用以下命令:\n")
    print("  pip install fastapi uvicorn httpx numpy plotly google-generativeai python-dotenv kaleido")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ 啟動失敗: {e}")
    print(f"詳細信息: {type(e).__name__}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
