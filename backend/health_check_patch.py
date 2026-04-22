"""
健康檢查路由補丁
在 main.py 的 app 定義後添加此端點
"""

# 在 main.py 中的 app = FastAPI(...) 後面添加：

# ====== 健康檢查和系統信息 ======

@app.get("/health")
async def health_check():
    """
    系統健康檢查端點
    返回後端服務狀態、依賴情況和 API 配置
    """
    import sys
    
    # 檢查 Gemini API 狀態
    gemini_status = "✓ 已配置" if is_valid_key else "✗ 未配置（可選）"
    
    return {
        "status": "healthy",
        "service": "Crypto-AI 後端 API",
        "version": "1.0.0",
        "python_version": sys.version.split()[0],
        "backend_features": {
            "technical_analysis": True,
            "chart_generation": True,
            "ai_analysis": bool(is_valid_key),
            "gemini_api": gemini_status
        },
        "dependencies": {
            "fastapi": "✓",
            "numpy": "✓",
            "httpx": "✓",
            "plotly": "✓"
        },
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "analyze": "/analyze",
            "chart": "/chart",
            "history": "/history"
        }
    }


@app.get("/")
async def root():
    """根路由 - 重定向到 API 文檔"""
    return {
        "message": "歡迎使用 Crypto-AI 加密貨幣 AI 投資分析系統",
        "api_docs": "http://localhost:8000/docs",
        "health_check": "http://localhost:8000/health",
        "status": "running"
    }

"""
若想手動添加，請在 main.py 的適當位置（建議在所有路由定義後）添加上述代碼
"""
