from __future__ import annotations

import math
from typing import Any

from sources.base import HttpClient, Quote, is_finite, market_number


def fetch_coingecko_quote(client: HttpClient, item: dict[str, Any]) -> Quote:
    coin_id = item.get("coinGeckoId", "bitcoin")
    url = (
        "https://api.coingecko.com/api/v3/simple/price"
        f"?ids={coin_id}&vs_currencies=usd&include_24hr_change=true"
    )
    data = client.get_json(url, timeout=12)
    row = data.get(coin_id) or {}
    price = market_number(row.get("usd"))
    change_pct = market_number(row.get("usd_24h_change"))
    change = price * (change_pct / 100) if is_finite(price) and is_finite(change_pct) else math.nan

    return Quote(
        symbol=item["symbol"],
        name=item.get("name", item["symbol"]),
        zh_name=item.get("zhName", item.get("name", item["symbol"])),
        group="crypto",
        region="global",
        price=price,
        change=change,
        change_pct=change_pct,
        source="CoinGecko",
        source_url=f"https://www.coingecko.com/en/coins/{coin_id}",
        quality="real" if is_finite(price) else "unavailable",
    )


def fetch_fear_greed(client: HttpClient) -> dict[str, Any]:
    try:
        data = client.get_json("https://api.alternative.me/fng/?limit=1", timeout=10)
        row = (data.get("data") or [{}])[0]
        return {
            "value": market_number(row.get("value")),
            "label": row.get("value_classification") or "",
            "source": "Alternative.me Fear & Greed",
            "updatedAt": row.get("timestamp"),
        }
    except Exception:
        try:
            data = client.get_json("https://terminalfeed.io/api/fear-greed", timeout=10)
            return {
                "value": market_number(data.get("value") or data.get("score")),
                "label": data.get("classification") or data.get("label") or "",
                "source": "TerminalFeed Fear & Greed",
                "updatedAt": data.get("updated_at"),
            }
        except Exception:
            return {"value": None, "label": "暂不可用", "source": "Fear & Greed", "updatedAt": None}
