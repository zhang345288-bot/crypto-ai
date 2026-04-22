"""
蠟燭圖生成模組 - 使用 plotly 從 Bybit API 獲取資料並生成互動式圖表
"""
import logging
import asyncio
import httpx
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import math

logger = logging.getLogger(__name__)


async def fetch_kline_data(symbol: str, interval: str, limit: int = 500):
    """
    從 Bybit API 獲取 K 線資料
    
    Args:
        symbol: 交易對，如 "BTCUSDT"
        interval: 時間間隔，如 "15", "60", "240", "D"
        limit: 返回的 candle 數量
    
    Returns:
        包含 OHLCV 資料的列表，按時間升序排列
    """
    url = f"https://api.bybit.com/v5/market/kline?category=linear&symbol={symbol}&interval={interval}&limit={limit}"
    
    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            resp = await client.get(url)
            resp.raise_for_status()
            
            data = resp.json()
            if data.get("retCode") != 0:
                logger.error(f"Bybit API error: {data.get('retMsg')}")
                return []
            
            klist = data.get("result", {}).get("list", [])
            if not klist:
                logger.warning(f"No kline data returned for {symbol}")
                return []
            
            # 轉換為升序（最舊到最新）
            candles = []
            for item in klist:
                try:
                    candle = {
                        "time": int(item[0]) // 1000,  # 轉換為秒
                        "open": float(item[1]),
                        "high": float(item[2]),
                        "low": float(item[3]),
                        "close": float(item[4]),
                        "volume": float(item[5])
                    }
                    candles.append(candle)
                except (IndexError, ValueError) as e:
                    logger.warning(f"Failed to parse candle: {e}")
                    continue
            
            # 反轉為升序
            candles.reverse()
            return candles
            
        except Exception as e:
            logger.error(f"Failed to fetch kline data: {e}")
            return []


async def generate_candlestick_chart(
    symbol: str,
    interval: str,
    limit: int = 500,
    save_path: str = None
):
    """
    生成蠟燭圖並保存或返回
    
    Args:
        symbol: 交易對，如 "BTCUSDT"
        interval: 時間間隔
        limit: K 線數量
        save_path: 圖片保存路徑（如果為 None，返回 HTML）
    
    Returns:
        圖表對象或保存路徑
    """
    
    # 獲取資料
    candles = await fetch_kline_data(symbol, interval, limit)
    
    if not candles:
        logger.error(f"No data to plot for {symbol}")
        raise ValueError(f"Unable to fetch data for {symbol}")
    
    # 準備資料
    times = [datetime.fromtimestamp(c["time"]).strftime('%Y-%m-%d %H:%M:%S') for c in candles]
    opens = [c["open"] for c in candles]
    highs = [c["high"] for c in candles]
    lows = [c["low"] for c in candles]
    closes = [c["close"] for c in candles]
    volumes = [c["volume"] for c in candles]
    
    # 計算簡單移動平均
    ma7 = calculate_ma(closes, 7)
    ma25 = calculate_ma(closes, 25)
    
    # 建立子圖：主圖表 + 成交量
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        row_heights=[0.7, 0.3],
        specs=[[{"secondary_y": False}], [{"secondary_y": False}]]
    )
    
    # 蠟燭圖
    fig.add_trace(
        go.Candlestick(
            x=times,
            open=opens,
            high=highs,
            low=lows,
            close=closes,
            name=symbol,
            increasing_line_color='#00CC00',
            decreasing_line_color='#FF0000',
        ),
        row=1, col=1
    )
    
    # MA7
    fig.add_trace(
        go.Scatter(
            x=times,
            y=ma7,
            name='MA7',
            line=dict(color='#FFA500', width=1),
        ),
        row=1, col=1
    )
    
    # MA25
    fig.add_trace(
        go.Scatter(
            x=times,
            y=ma25,
            name='MA25',
            line=dict(color='#0099FF', width=1),
        ),
        row=1, col=1
    )
    
    # 成交量柱狀圖
    colors = ['#00CC00' if closes[i] >= opens[i] else '#FF0000' for i in range(len(closes))]
    fig.add_trace(
        go.Bar(
            x=times,
            y=volumes,
            name='Volume',
            marker_color=colors,
            opacity=0.5,
        ),
        row=2, col=1
    )
    
    # 更新圖表配置
    fig.update_layout(
        title=f"{symbol} K-Line Chart (Interval: {interval})",
        height=600,
        template='plotly_dark',
        hovermode='x unified',
        margin=dict(l=50, r=50, t=50, b=50),
        xaxis_rangeslider_visible=False,
    )
    
    # 保存或返回
    if save_path:
        fig.write_image(save_path, width=1200, height=600)
        logger.info(f"Chart saved to {save_path}")
        return save_path
    else:
        return fig.to_html()


def calculate_ma(data: list, period: int) -> list:
    """計算簡單移動平均"""
    if len(data) < period:
        return [None] * len(data)
    
    ma = []
    for i in range(len(data)):
        if i < period - 1:
            ma.append(None)
        else:
            window = data[i - period + 1:i + 1]
            ma.append(sum(window) / period)
    
    return ma


# 同步包裝器（用於非異步環境）
def generate_candlestick_chart_sync(
    symbol: str,
    interval: str,
    limit: int = 500,
    save_path: str = None
):
    """同步版本的蠟燭圖生成"""
    return asyncio.run(generate_candlestick_chart(symbol, interval, limit, save_path))
