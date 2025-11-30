# main.py
from fastapi import FastAPI, Request
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import httpx
import numpy as np
import math
import logging
from chart_generator import generate_candlestick_chart
import os
from datetime import datetime
import google.generativeai as genai
import json
from dotenv import load_dotenv

# 加載 .env 文件（優先於系統環境變數）
load_dotenv()

# 初始化 Google Gemini client（從環境變數讀 GEMINI_API_KEY）
gemini_api_key = os.getenv("GEMINI_API_KEY", "").strip()
gemini_model = None

# 檢查是否為有效的 API key（排除 placeholder）
is_valid_key = (
    gemini_api_key 
    and len(gemini_api_key) > 10 
    and not gemini_api_key.startswith("your-")
    and gemini_api_key.startswith("AIza")
)

if is_valid_key:
    try:
        genai.configure(api_key=gemini_api_key)
        # 使用最新的 Gemini 2.5 Flash 模型
        gemini_model = genai.GenerativeModel("models/gemini-2.5-flash")
        logging.info("✓ Google Gemini API 已配置 - AI 深度分析功能已啟用")
    except Exception as e:
        logging.warning(f"⚠ Gemini API 初始化失敗: {e}")
        logging.warning("⚠ AI 深度分析功能暫時無法使用")
        gemini_model = None
else:
    logging.info("ℹ Gemini API key 未設置或無效 - AI 深度分析功能已禁用（可選功能）")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

app = FastAPI(
    title="加密貨幣 AI 投資分析系統",
    description="後端 API - 提供技術分析、AI 深度分析與圖表生成功能",
    version="1.0.0"
)

# CORS（允許本機開發前端呼叫）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 開發時可用 "*"，上線請改成前端網域
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# interval 映射（前端值 -> Bybit v5 interval ）
INTERVAL_MAP = {
    "15m": "15",
    "1h": "60",
    "4h": "240",
    "1d": "D",
}

# ====== 技術指標實作（純 numpy，不依賴 talib） ======

def ma_series(data: list[float], period: int) -> list[float]:
    """返回與 data 相同長度的移動平均（leading 用第一個有效值填補）"""
    x = np.array(data, dtype=float)
    if len(x) == 0:
        return []
    if len(x) < period:
        # 若資料不足，回傳 copy 的原價（避免 null）
        return x.tolist()
    # 使用卷積計算 simple MA
    kernel = np.ones(period) / period
    ma_valid = np.convolve(x, kernel, mode="valid")  # 長度 len(x)-period+1
    # pad 前面的 (period-1) 個值，使用第一個有效 ma 值填補
    pad_val = float(ma_valid[0])
    pads = np.full(period - 1, pad_val)
    ma_full = np.concatenate([pads, ma_valid])
    return ma_full.tolist()

def compute_rsi(data: list[float], period: int = 14) -> list[float]:
    """簡單的 RSI 計算，回傳與 data 相同長度（前面用第一個有效 RSI 填補）"""
    prices = np.array(data, dtype=float)
    if len(prices) == 0:
        return []
    deltas = np.diff(prices)
    if len(deltas) < period:
        # 不足則回傳價格（避免 null）
        return prices.tolist()
    seed = deltas[:period]
    up = seed[seed > 0].sum() / period
    down = -seed[seed < 0].sum() / period
    rs = up / down if down != 0 else np.inf
    first_rsi = 100 - 100 / (1 + rs) if not math.isinf(rs) else 100.0
    rsi_list = [first_rsi]
    up_ema = up
    down_ema = down
    for d in deltas[period:]:
        gain = max(d, 0)
        loss = -min(d, 0)
        up_ema = (up_ema * (period - 1) + gain) / period
        down_ema = (down_ema * (period - 1) + loss) / period
        rs = up_ema / down_ema if down_ema != 0 else np.inf
        r = 100 - 100 / (1 + rs) if not math.isinf(rs) else 100.0
        rsi_list.append(r)
    # rsi_list 長度 = len(deltas) - period +1
    # pad 前面 period 個值用 first_rsi
    pad = [first_rsi] * period
    rsi_full = pad + rsi_list
    # 若因任何原因長度錯誤，調整
    if len(rsi_full) < len(prices):
        # pad tail
        rsi_full = rsi_full + [rsi_full[-1]] * (len(prices) - len(rsi_full))
    elif len(rsi_full) > len(prices):
        rsi_full = rsi_full[-len(prices):]
    return [float(x) for x in rsi_full]

def compute_macd(data: list[float], short: int = 12, long: int = 26, signal: int = 9):
    """計算 MACD 與 signal，回傳兩個與 data 相同長度的陣列（前面用 0 填補）"""
    prices = np.array(data, dtype=float)
    n = len(prices)
    if n == 0:
        return [], []
    # EMA 用公式逐步計算
    def ema(series, period):
        res = np.zeros(len(series))
        k = 2 / (period + 1)
        res[0] = series[0]
        for i in range(1, len(series)):
            res[i] = series[i] * k + res[i - 1] * (1 - k)
        return res
    if n < 1:
        return [0.0] * n, [0.0] * n
    ema_short = ema(prices, short)
    ema_long = ema(prices, long)
    macd = ema_short - ema_long
    signal_line = ema(macd, signal)
    return macd.tolist(), signal_line.tolist()


def ema_series(data: list[float], period: int) -> list[float]:
    """計算 EMA 序列（與輸入等長），初始值用第一個元素作為 seed"""
    if not data:
        return []
    res = [0.0] * len(data)
    k = 2 / (period + 1)
    res[0] = float(data[0])
    for i in range(1, len(data)):
        res[i] = float(data[i]) * k + res[i - 1] * (1 - k)
    return res


def atr_series(highs: list[float], lows: list[float], closes: list[float], period: int = 14) -> list[float]:
    """計算 ATR（Average True Range），回傳與輸入等長"""
    n = len(closes)
    if n == 0:
        return []
    tr = [0.0] * n
    for i in range(n):
        h = highs[i]
        l = lows[i]
        if i == 0:
            prev_close = closes[0]
        else:
            prev_close = closes[i - 1]
        tr[i] = max(h - l, abs(h - prev_close), abs(l - prev_close))
    # ATR 使用 Wilder smoothing (EMA with k=1/period)
    atr = [0.0] * n
    atr[0] = tr[0]
    alpha = 1 / period
    for i in range(1, n):
        atr[i] = (atr[i - 1] * (period - 1) + tr[i]) / period
    return atr


def volatility_pct(closes: list[float], period: int = 14) -> float:
    """回傳最近 period 的年化波動性百分比（近似）"""
    if not closes or len(closes) < 2:
        return 0.0
    import math
    arr = np.array(closes[-period:], dtype=float)
    logrets = np.diff(np.log(arr + 1e-12))
    if len(logrets) < 2:
        return 0.0
    sd = float(np.std(logrets, ddof=1))
    # daily-ish to annualize: 假設 timeframe 可視為日級別視為 sqrt(252)，若 intraday 則此為近似
    annualized = sd * math.sqrt(252)
    return annualized * 100


def support_resistance_simple(prices: list[float], lookback: int = 50, levels: int = 3) -> dict:
    """簡單地找出最近 lookback 範圍內的高低 percentile 作為阻力/支撐"""
    if not prices:
        return {"support": [], "resistance": []}
    arr = np.array(prices[-lookback:], dtype=float)
    # 支撐取 10%/25%/40% 百分位，阻力取 60%/75%/90%
    supports = np.percentile(arr, [10, 25, 40]).tolist()
    resistances = np.percentile(arr, [60, 75, 90]).tolist()
    return {"support": supports[-levels:], "resistance": resistances[-levels:]}


def detect_trend_via_ema(closes: list[float]) -> str:
    """用長短 EMA 交叉判斷趨勢：短 EMA 在長 EMA 上方 => 上升，反之下跌，否則中性"""
    if not closes or len(closes) < 26:
        return "中性"
    ema_short = ema_series(closes, 12)
    ema_long = ema_series(closes, 26)
    if ema_short[-1] > ema_long[-1] and ema_short[-2] <= ema_long[-2]:
        return "上升"
    if ema_short[-1] < ema_long[-1] and ema_short[-2] >= ema_long[-2]:
        return "下跌"
    # 若兩者差距顯著則也視為趨勢
    diff = (ema_short[-1] - ema_long[-1]) / (ema_long[-1] + 1e-9)
    if diff > 0.02:
        return "上升"
    if diff < -0.02:
        return "下跌"
    return "中性"


# ====== AI 分析函式（使用 Gemini，由用戶自行提供 API key） ======

def generate_ai_analysis(
    coin: str,
    last_price: float,
    indicators: dict,
    trend: str,
    support_resistance: dict,
    rationale: list[str],
    action: str,
    risk: str,
) -> Optional[str]:
    """調用 Google Gemini 生成分析（用戶需自行提供 API key）"""
    
    # 若未配置 API key，返回 None（前端會隱藏 AI 區塊）
    if not gemini_model:
        return None
    
    prompt = f"""You are a professional crypto analyst. Provide investment advice based on:

MARKET DATA:
- Current Price: ${last_price:.2f}
- Trend: {trend}
- Risk Preference: {risk} (low=conservative, medium=neutral, high=aggressive)

TECHNICAL INDICATORS:
- RSI(14): {indicators.get('rsi14', 'N/A')}
- MACD: {indicators.get('macd', 'N/A')}
- Signal: {indicators.get('signal', 'N/A')}
- ATR: {indicators.get('atr', 'N/A')}
- Volatility: {indicators.get('volatility_pct', 'N/A')}%
- MA(7): {indicators.get('ma7', 'N/A')}
- MA(25): {indicators.get('ma25', 'N/A')}

SUPPORT & RESISTANCE:
- Support: {support_resistance.get('support', [])}
- Resistance: {support_resistance.get('resistance', [])}

TECHNICAL ASSESSMENT:
{'; '.join(rationale)}

RECOMMENDATION:
{action}

Please provide concise, practical advice (5 points):
1. Market analysis (2-3 sentences): Current state and key signals
2. Entry strategy: Suggested entry prices and batch allocation based on risk preference
3. Risk management: Suggested stop-loss and profit targets
4. Risk warnings: Main current risk factors
5. Follow-up points: Key levels or indicator changes to monitor

Be concise and actionable. Answer in Traditional Chinese."""
    
    try:
        response = gemini_model.generate_content(prompt)
        ai_text = response.text
        logging.info(f"{coin} AI analysis completed successfully")
        return ai_text
    except Exception as e:
        error_msg = str(e)
        logging.exception(f"{coin} AI analysis failed")
        # 詳細記錄錯誤以便用戶調試
        if "429" in error_msg or "quota" in error_msg.lower():
            return f"[配額已滿] API 配額已達上限。請在 24 小時後重試或升級付費方案。"
        elif "invalid_api_key" in error_msg or "INVALID_ARGUMENT" in error_msg:
            return f"[API 金鑰無效] 請檢查 GEMINI_API_KEY 是否正確設置。"
        else:
            return f"[AI 分析失敗] {error_msg[:100]}"

# ====== Bybit K 線取得（v5 API） ======

async def fetch_kline_from_bybit(symbol: str, interval: str, limit: int = 200) -> list[float]:
    """
    symbol: e.g. "BTCUSDT"
    interval: Bybit interval string (e.g. "15" / "60" / "240" / "D")
    limit: 要求筆數
    回傳：時間序列的收盤價 (從最舊到最新)
    """
    url = f"https://api.bybit.com/v5/market/kline?category=linear&symbol={symbol}&interval={interval}&limit={limit}"
    logging.info(f"抓取 Bybit K 線: {symbol}, interval={interval}, url={url}")
    async with httpx.AsyncClient(timeout=15.0) as client:
        res = await client.get(url)
    # 印出原始回傳（除錯用）
    logging.debug(f"Bybit 回傳 ({symbol}): status={res.status_code}, text={res.text[:800]}")
    if res.status_code != 200:
        raise ValueError(f"Bybit HTTP {res.status_code}")
    try:
        j = res.json()
    except Exception as e:
        raise ValueError(f"回傳非 JSON: {e}")
    if j.get("retCode") != 0:
        raise ValueError(f"Bybit API 錯誤: {j.get('retMsg')}")
    result = j.get("result", {})
    klist = result.get("list") or []
    if not klist:
        # 回傳空 list 代表無資料
        raise ValueError("K 線資料為空")
    # klist 項目範例: ["1760274000000","111733.8","111887.9","111500","111523.5","770.477","86055557.1538"]
    # index 4 是 close price
    closes = []
    for item in klist:
        try:
            closes.append(float(item[4]))
        except Exception:
            closes.append(float("nan"))
    # Bybit 回傳順序是從最新到最舊（視情況），為了畫圖通常要調成從最舊到最新
    closes = closes[::-1]
    # 若有 nan，替補為前一個有效值或 0
    for i, v in enumerate(closes):
        if math.isnan(v):
            closes[i] = closes[i - 1] if i > 0 else 0.0
    logging.info(f"{symbol} 收盤價取得: {len(closes)} 筆 (first={closes[0] if closes else 'n/a'}, last={closes[-1] if closes else 'n/a'})")
    return closes

# ====== 分析與建議邏輯 ======

def normalize_risk(risk_str: str) -> str:
    """把前端可能的 risk 字串標準化為 'low'/'medium'/'high'"""
    if not risk_str:
        return "medium"
    s = risk_str.lower()
    if "low" in s or "保守" in s:
        return "low"
    if "high" in s or "積極" in s:
        return "high"
    return "medium"

def analyze_one_coin(
    coin: str,
    opens: list[float],
    highs: list[float],
    lows: list[float],
    closes: list[float],
    volumes: list[float],
    indicator: str,
    risk_raw: str,
) -> dict:
    """更嚴謹的分析函式，回傳包含建議、進出場、停損、目標價、資金配置與指標快照的物件。"""
    ind = (indicator or "").upper()
    risk = normalize_risk(risk_raw)

    n = len(closes)
    # 若資料不足，回傳無法分析
    if n < 10:
        return {
            "coin": coin,
            "action": "無法分析",
            "confidence": 0,
            "position_pct": 0,
            "entry": None,
            "stop_loss": None,
            "take_profit": [],
            "rationale": ["K 線資料不足，無法進行嚴謹分析"],
            "indicators": {},
            "risk": risk,
            "risk_raw": risk_raw,
        }

    # 基本指標
    ma7 = ma_series(closes, 7)
    ma25 = ma_series(closes, 25)
    ema12 = ema_series(closes, 12)
    ema26 = ema_series(closes, 26)
    rsi = compute_rsi(closes, period=14)
    macd, signal = compute_macd(closes, short=12, long=26, signal=9)
    atr = atr_series(highs, lows, closes, period=14)
    vol_pct = volatility_pct(closes, period=14)
    sr = support_resistance_simple(closes, lookback=min(200, n), levels=3)
    trend = detect_trend_via_ema(closes)

    last_price = float(closes[-1])
    last_atr = float(atr[-1]) if atr else 0.0

    # 初始得分與信心分數組成
    score = 0.0
    rationale: list[str] = []

    # 趨勢與均線
    if ema12[-1] > ema26[-1]:
        score += 20
        rationale.append("短期 EMA 在長期 EMA 之上，趨勢偏多。")
    else:
        score -= 10
        rationale.append("短期 EMA 在長期 EMA 之下，趨勢偏空。")

    if ma7[-1] > ma25[-1]:
        score += 10
        rationale.append("短期 MA 在長期 MA 之上，動能偏多。")
    else:
        score -= 5

    # RSI 判斷
    last_rsi = float(rsi[-1])
    rationale.append(f"RSI(14)={last_rsi:.1f}")
    if last_rsi < 25:
        score += 25
        rationale.append("RSI 進入超賣，可能有反彈機會。")
    elif last_rsi < 40:
        score += 5
    elif last_rsi > 75:
        score -= 25
        rationale.append("RSI 過高，存在回調風險。")
    elif last_rsi > 60:
        score -= 5

    # MACD 判斷
    if len(macd) >= 2 and len(signal) >= 2:
        if macd[-1] > signal[-1] and macd[-2] <= signal[-2]:
            score += 15
            rationale.append("MACD 黃金交叉，短期動能轉強。")
        elif macd[-1] < signal[-1] and macd[-2] >= signal[-2]:
            score -= 15
            rationale.append("MACD 死叉，短期動能轉弱。")

    # 波動性調整：高波動性降低得分
    if vol_pct > 80:
        score -= 15
        rationale.append(f"波動性高 ({vol_pct:.1f}%), 風險較大。")
    elif vol_pct > 40:
        score -= 5

    # 支撐阻力：若價格接近支撐，增加買進可能性
    supports = sr.get("support", [])
    resistances = sr.get("resistance", [])
    if supports:
        nearest_support = supports[-1]
        if last_price <= nearest_support * 1.02:
            score += 8
            rationale.append(f"價格接近支撐 {nearest_support:.4f}，風險回報較佳。")

    # 依指標加權修正
    if ind == "RSI":
        if last_rsi < 30:
            score += 10
        elif last_rsi > 70:
            score -= 10
    elif ind == "MACD":
        # 已在 MACD 檢查中處理
        pass
    elif ind == "MA":
        if ma7[-1] > ma25[-1]:
            score += 8
        else:
            score -= 8

    # 風險偏好影響基礎倉位
    base_pct_map = {"low": 0.01, "medium": 0.03, "high": 0.07}
    base_pct = base_pct_map.get(risk, 0.03)
    # 以波動性調整倉位：vol_pct = 100 => 降為原來 1/2
    adj_pct = base_pct / (1 + vol_pct / 100)
    position_pct = max(0.002, adj_pct) * 100  # 以百分比表示，最低 0.2%

    # 由 score 決定 action 與 confidence
    # score 大於 ~15 視為偏多，低於 -15 偏空
    if score >= 20:
        action = "建議買入"
    elif score >= 5:
        action = "小額買入"
    elif score > -5:
        action = "觀望"
    elif score > -20:
        action = "小額減倉"
    else:
        action = "建議賣出"

    # confidence 0-100：由 score 與資料完整度組成
    conf = min(95, max(10, int(50 + score)))
    if n < 50:
        conf = max(10, int(conf * 0.7))
        rationale.append("資料筆數偏少，建議降低信心評估。")

    # 進出場與停損（以 ATR 決定距離）
    if last_atr <= 0:
        stop_loss = None
        take_profit = []
    else:
        # 停損距離 1.5 ATR（保守）~2.5 ATR（積極）
        sl_multiplier = 1.5 if risk == "low" else (2.0 if risk == "medium" else 2.5)
        tp_multipliers = [2.0, 3.5]
        stop_loss = max(0.0, last_price - sl_multiplier * last_atr)
        take_profit = [last_price + m * last_atr for m in tp_multipliers]

    # 如果 action 為 建議賣出，翻轉停損/目標邏輯為做空（若該策略允許），否則保留 sell 提示
    # 最後組裝 rationale 與指標快照
    indicators_snapshot = {
        "last_price": last_price,
        "ma7": float(ma7[-1]) if ma7 else None,
        "ma25": float(ma25[-1]) if ma25 else None,
        "ema12": float(ema12[-1]) if ema12 else None,
        "ema26": float(ema26[-1]) if ema26 else None,
        "rsi14": float(last_rsi),
        "macd": float(macd[-1]) if macd else None,
        "signal": float(signal[-1]) if signal else None,
        "atr": float(last_atr),
        "volatility_pct": float(vol_pct),
    }

    # 建立分批進場計畫（entry_plan）
    entry_plan = []
    total_pct = position_pct
    if action == "小額買入":
        total_pct = max(0.1, total_pct * 0.5)  # 小額買入，減半建議，但至少 0.1%

    # 三段分批比例（初始/中段/加碼）
    tranche_ratios = [0.5, 0.3, 0.2]
    tranche_ratios = [r / sum(tranche_ratios) for r in tranche_ratios]

    # 若接近支撐，建議初始以市價或接近支撐的限價分批進場
    nearest_support = supports[-1] if supports else None
    nearest_resistance = resistances[-1] if resistances else None

    if action in ["建議買入", "小額買入"]:
        if nearest_support and last_price <= nearest_support * 1.02:
            # 價格已接近支撐，第一批市價，後兩批以支撐附近限價
            entry_plan = [
                {"type": "market", "price": round(last_price, 6), "pct": round(total_pct * tranche_ratios[0], 3)},
                {"type": "limit", "price": round(nearest_support * 1.005, 6), "pct": round(total_pct * tranche_ratios[1], 3)},
                {"type": "limit", "price": round(nearest_support * 0.995, 6), "pct": round(total_pct * tranche_ratios[2], 3)},
            ]
            # 停損設在支撐下方 ATR 倍數
            stop_loss_levels = [round(max(0.0, last_price - sl_multiplier * last_atr), 6),
                                 round(max(0.0, nearest_support - sl_multiplier * last_atr), 6)]
        else:
            # 建議等待回調到支撐或分批限價下單；第一批小量市價/限價
            if nearest_support:
                entry_plan = [
                    {"type": "limit", "price": round(last_price * 0.997, 6), "pct": round(total_pct * 0.2, 3)},
                    {"type": "limit", "price": round(nearest_support * 1.01, 6), "pct": round(total_pct * 0.5, 3)},
                    {"type": "limit", "price": round(nearest_support * 0.995, 6), "pct": round(total_pct * 0.3, 3)},
                ]
                stop_loss_levels = [round(max(0.0, nearest_support - sl_multiplier * last_atr), 6)]
            else:
                # 無明確支撐，建議小額市價試單或觀望
                entry_plan = [
                    {"type": "market", "price": round(last_price, 6), "pct": round(total_pct * 0.2, 3)},
                    {"type": "limit", "price": round(last_price * 0.995, 6), "pct": round(total_pct * 0.3, 3)},
                    {"type": "limit", "price": round(last_price * 0.99, 6), "pct": round(total_pct * 0.5, 3)},
                ]
                stop_loss_levels = [round(max(0.0, last_price - sl_multiplier * last_atr), 6)]

        # 停損採用最寬的 stop_loss（保守做法）
        stop_loss = stop_loss_levels[-1] if stop_loss_levels else stop_loss

    elif action in ["建議賣出", "小額減倉"]:
        # 賣出或減倉：建議以市價為主或阻力附近分批賣出
        if nearest_resistance and last_price >= nearest_resistance * 0.98:
            entry_plan = [
                {"type": "market", "price": round(last_price, 6), "pct": round(total_pct * 0.6, 3)},
                {"type": "limit", "price": round(nearest_resistance * 0.995, 6), "pct": round(total_pct * 0.4, 3)},
            ]
        else:
            entry_plan = [
                {"type": "market", "price": round(last_price, 6), "pct": round(total_pct, 3)},
            ]
        # 賣出時的止損可視為回補觸發（此處保留 stop_loss 作為風控參考）

    else:
        # 觀望或未知
        entry_plan = [{"type": "none", "reason": "觀察，等待明確訊號"}]

    # 將 take_profit 四捨五入並以價格表示（若為空，保持原樣）
    take_profit_prices = [round(tp, 6) for tp in take_profit] if take_profit else []

    # 調用 AI 生成深入分析（若已配置 API key）
    ai_analysis = generate_ai_analysis(
        coin=coin,
        last_price=last_price,
        indicators=indicators_snapshot,
        trend=trend,
        support_resistance=sr,
        rationale=rationale,
        action=action,
        risk=risk,
    )

    return {
        "coin": coin,
        "action": action,
        "confidence": conf,
        "position_pct": round(position_pct, 3),
        "entry_plan": entry_plan,
        "stop_loss": stop_loss,
        "take_profit": take_profit_prices,
        "rationale": rationale,
        "trend": trend,
        "support_resistance": sr,
        "indicators": indicators_snapshot,
        "risk": risk,
        "risk_raw": risk_raw,
        "ai_analysis": ai_analysis,  # 若未配置 API key 則為 None
    }

# ====== API 路由 ======

@app.post("/analyze")
async def analyze(request: Request):
    global gemini_model  # 允許動態修改模型
    
    body = await request.json()
    logging.info(f"收到分析請求: {body}")
    
    # 若前端提供了 API key，則動態配置 Gemini
    frontend_api_key = body.get("gemini_api_key", "").strip()
    if frontend_api_key and frontend_api_key != gemini_api_key:
        try:
            genai.configure(api_key=frontend_api_key)
            gemini_model = genai.GenerativeModel("models/gemini-2.5-flash")
            logging.info("✓ 使用前端提供的 Gemini API key")
        except Exception as e:
            logging.warning(f"前端 API key 配置失敗: {e}")
            # 保持使用原有的 gemini_model
    
    indicator = body.get("indicator", "")
    risk = body.get("risk", "")
    coins = body.get("coins", [])
    interval_in = body.get("interval", "1h")  # 前端預設為 "1h"

    # map interval
    bybit_interval = INTERVAL_MAP.get(interval_in, "60")

    results = []
    async with httpx.AsyncClient(timeout=20.0) as client:
        # 我們對每個 coin 逐一抓取（也可改為並行 gather）
        for coin in coins:
            symbol = f"{coin}USDT"
            try:
                # 取 200 根 candle（若你要更少可改 limit）
                url = f"https://api.bybit.com/v5/market/kline?category=linear&symbol={symbol}&interval={bybit_interval}&limit=200"
                logging.info(f"Fetching {symbol} -> {url}")
                resp = await client.get(url)
                logging.debug(f"{symbol} resp status {resp.status_code}")
                if resp.status_code != 200:
                    raise ValueError(f"HTTP {resp.status_code}")

                j = resp.json()
                if j.get("retCode") != 0:
                    raise ValueError(f"Bybit error: {j.get('retMsg')}")
                klist = j.get("result", {}).get("list") or []
                if not klist:
                    raise ValueError("K 線資料為空")

                # 取得完整 OHLCV 並轉 float，將順序改成 earliest -> latest
                opens = []
                highs = []
                lows = []
                closes = []
                volumes = []
                timestamps = []
                for item in klist:
                    try:
                        timestamps.append(int(item[0]))
                        opens.append(float(item[1]))
                        highs.append(float(item[2]))
                        lows.append(float(item[3]))
                        closes.append(float(item[4]))
                        try:
                            volumes.append(float(item[5]))
                        except Exception:
                            volumes.append(0.0)
                    except Exception:
                        # 若解析失敗，補 0 或 nan，之後會處理
                        timestamps.append(0)
                        opens.append(0.0)
                        highs.append(0.0)
                        lows.append(0.0)
                        closes.append(float("nan"))
                        volumes.append(0.0)

                # 轉成 earliest -> latest
                opens = opens[::-1]
                highs = highs[::-1]
                lows = lows[::-1]
                closes = closes[::-1]
                volumes = volumes[::-1]
                timestamps = timestamps[::-1]

                # 補 nan 為前一個有效值或 0
                for i in range(len(closes)):
                    if math.isnan(closes[i]):
                        closes[i] = closes[i - 1] if i > 0 else 0.0
                    if math.isnan(opens[i]):
                        opens[i] = closes[i]
                    if math.isnan(highs[i]):
                        highs[i] = closes[i]
                    if math.isnan(lows[i]):
                        lows[i] = closes[i]

                logging.info(f"{symbol} data count={len(closes)} first={closes[0]:.6f} last={closes[-1]:.6f}")

                analysis = analyze_one_coin(coin, opens, highs, lows, closes, volumes, indicator, risk)
                results.append(analysis)
            except Exception as e:
                logging.exception(f"{coin} 分析失敗")
                results.append({
                    "coin": coin,
                    "suggestion": "無法分析",
                    "reason": str(e),
                    "trend": "未知",
                    "kLine": [],
                    "ma7": [],
                    "ma25": [],
                    "rsi": [],
                    "macd": [],
                    "signal": []
                })

    return {"recommendations": results}


@app.get("/generate-chart/{symbol}")
async def generate_chart(
    symbol: str,
    interval: str = "60",
    limit: int = 200
):
    """生成 K 線圖並返回圖片"""
    # 確保輸出目錄存在
    output_dir = "chart_output"
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成唯一的檔案名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{symbol}_{interval}_{timestamp}.png"
    save_path = os.path.join(output_dir, filename)
    
    # 生成圖表
    await generate_candlestick_chart(
        symbol=symbol,
        interval=interval,
        limit=limit,
        save_path=save_path
    )
    
    # 返回圖片
    return FileResponse(
        save_path,
        media_type="image/png",
        filename=filename
    )


@app.get("/history")
async def history(symbol: str, interval: str = "60", limit: int = 500, endTime: Optional[int] = None):
    """返回歷史 candles（從最舊到最新），每個 candle 包含 ts, open, high, low, close, volume
    例: /history?symbol=BTC&interval=60&limit=500 或 /history?symbol=BTCUSDT&interval=60&limit=500
    """
    # 自動補上 USDT 後綴（如果沒有）
    if not symbol.endswith("USDT"):
        symbol = f"{symbol}USDT"
    
    bybit_interval = interval
    limit = max(1, min(2000, int(limit)))

    def _interval_to_seconds(iv: str) -> int:
        if iv == "D":
            return 86400
        if iv == "W":
            return 7 * 86400
        if iv == "M":
            return 30 * 86400
        try:
            return int(iv) * 60
        except Exception:
            return 3600

    from_ts = None
    if endTime is not None:
        try:
            end_sec = max(0, int(endTime) // 1000)
            window = _interval_to_seconds(bybit_interval) * limit
            from_ts = max(0, end_sec - window)
        except Exception:
            from_ts = None

    base = f"https://api.bybit.com/v5/market/kline?category=linear&symbol={symbol}&interval={bybit_interval}&limit={limit}"
    if from_ts:
        base += f"&from={from_ts}"
    logging.info(f"history fetch {symbol} interval={bybit_interval} limit={limit} from={from_ts}")

    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            resp = await client.get(base)
            if resp.status_code != 200:
                return {"error": f"HTTP {resp.status_code}"}
            j = resp.json()
            if j.get("retCode") != 0:
                return {"error": f"Bybit: {j.get('retMsg')}"}
            lst = j.get("result", {}).get("list") or []
            candles = []
            for it in lst:
                try:
                    ts = int(it[0])
                    o = float(it[1]); h = float(it[2]); l = float(it[3]); c = float(it[4])
                    vol = None
                    try:
                        vol = float(it[5])
                    except Exception:
                        vol = None
                    candles.append({"ts": ts, "open": o, "high": h, "low": l, "close": c, "volume": vol})
                except Exception:
                    continue
            candles = candles[::-1]  # oldest -> latest
            return {"candles": candles}
        except Exception as e:
            logging.exception("history fetch failed")
            return {"error": str(e)}
