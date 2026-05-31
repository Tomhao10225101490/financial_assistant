from __future__ import annotations

import math
from typing import Any
from urllib.parse import quote

from sources.base import HttpClient, Quote, is_finite, market_number


def fetch_yahoo_quote(client: HttpClient, item: dict[str, Any]) -> Quote:
    symbol = item["symbol"]
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{quote(symbol)}?range=5d&interval=1d"
    data = client.get_json(url, timeout=12)
    result = data["chart"]["result"][0]
    meta = result["meta"]
    quote_row = result.get("indicators", {}).get("quote", [{}])[0]
    closes = [value for value in quote_row.get("close", []) if is_finite(value)]
    price = market_number(meta.get("regularMarketPrice") or (closes[-1] if closes else None))
    previous = market_number(
        meta.get("chartPreviousClose")
        or meta.get("previousClose")
        or (closes[-2] if len(closes) > 1 else None)
    )
    change = price - previous if is_finite(price) and is_finite(previous) else math.nan
    change_pct = (change / previous) * 100 if is_finite(change) and is_finite(previous) and previous else math.nan
    updated_at = None
    if meta.get("regularMarketTime"):
        from datetime import datetime, timezone

        updated_at = datetime.fromtimestamp(float(meta["regularMarketTime"]), timezone.utc).isoformat().replace("+00:00", "Z")

    return Quote(
        symbol=symbol,
        name=item.get("name", symbol),
        zh_name=item.get("zhName", item.get("name", symbol)),
        group=item.get("group", ""),
        region=item.get("region", ""),
        price=price,
        change=change,
        change_pct=change_pct,
        source="Yahoo Finance",
        source_url=f"https://finance.yahoo.com/quote/{quote(symbol, safe='')}",
        updated_at=updated_at,
        quality="real" if is_finite(price) else "unavailable",
    )
