from __future__ import annotations

from typing import Any

from sources.base import is_finite


def build_highlights(briefing: dict[str, Any]) -> list[str]:
    """Rule-based market briefing — explainable, no LLM required."""
    highlights: list[str] = []

    macro = briefing.get("macro") or []
    vix = next((item for item in macro if item.get("symbol") == "^VIX" or item.get("convexId") == "VIXCLS"), None)
    dgs10 = next((item for item in macro if item.get("convexId") == "DGS10"), None)
    spread = next((item for item in macro if item.get("convexId") == "T10Y2Y"), None)

    if vix and is_finite(vix.get("price")):
        if vix["price"] >= 25:
            highlights.append(f"波动率偏高：VIX 报 {vix['price']:.2f}，市场风险偏好可能下降。")
        elif vix["price"] >= 20:
            highlights.append(f"波动率抬升：VIX 报 {vix['price']:.2f}，需关注权益市场震荡。")

    if spread and is_finite(spread.get("price")):
        if spread["price"] < 0:
            highlights.append(f"收益率曲线倒挂：10Y-2Y 利差 {spread['price']:.2f}bp，衰退预期值得跟踪。")
        elif spread["price"] < 0.25:
            highlights.append(f"长短端利差偏窄：10Y-2Y 仅 {spread['price']:.2f}bp，宏观环境偏谨慎。")

    if dgs10 and is_finite(dgs10.get("price")):
        highlights.append(f"美国 10 年期国债收益率 {dgs10['price']:.2f}%，利率环境影响全球资产定价。")

    pulse = briefing.get("marketPulse") or {}
    for region in pulse.get("regions") or []:
        total = region.get("total") or 0
        down = region.get("down") or 0
        if total and down / total >= 0.7:
            highlights.append(f"{region.get('label', region.get('id', '某区域'))} 指数普遍走弱（{down}/{total} 下跌）。")
        elif total and region.get("up", 0) / total >= 0.7:
            highlights.append(f"{region.get('label', region.get('id', '某区域'))} 指数普遍走强（{region.get('up')}/{total} 上涨）。")

    crypto = briefing.get("crypto") or []
    btc = next((item for item in crypto if item.get("symbol") == "BTC"), None)
    if btc and is_finite(btc.get("changePct")):
        if abs(btc["changePct"]) >= 5:
            direction = "大涨" if btc["changePct"] > 0 else "大跌"
            highlights.append(f"加密市场异动：BTC 24h {direction} {btc['changePct']:+.2f}%。")

    fear = briefing.get("fearGreed") or {}
    if is_finite(fear.get("value")):
        if fear["value"] <= 25:
            highlights.append(f"加密恐惧贪婪指数 {int(fear['value'])}（极度恐惧），情绪偏冷。")
        elif fear["value"] >= 75:
            highlights.append(f"加密恐惧贪婪指数 {int(fear['value'])}（极度贪婪），情绪偏热。")

    commodities = briefing.get("commodities") or []
    oil = next((item for item in commodities if "CL" in str(item.get("symbol", ""))), None)
    gold = next((item for item in commodities if "GC" in str(item.get("symbol", ""))), None)
    if oil and is_finite(oil.get("changePct")) and abs(oil["changePct"]) >= 2:
        highlights.append(f"原油波动：WTI {oil['changePct']:+.2f}%，关注通胀与风险资产联动。")
    if gold and is_finite(gold.get("changePct")) and abs(gold["changePct"]) >= 1.5:
        highlights.append(f"黄金波动：{gold['changePct']:+.2f}%，避险与利率预期或正在定价。")

    if not highlights:
        highlights.append("全球主要资产暂无明显极端信号，建议结合区域指数与宏观卡片继续跟踪。")

    return highlights[:3]
