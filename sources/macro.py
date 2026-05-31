from __future__ import annotations

import math
from typing import Any

from sources.base import HttpClient, Quote, is_finite, market_number


CONVEX_BASE = "https://convextrade.com/api/public/data"


def fetch_convex_series(client: HttpClient, item: dict[str, Any]) -> Quote:
    series_id = item["convexId"]
    url = f"{CONVEX_BASE}/{series_id}"
    data = client.get_json(url, timeout=15)
    observations = data.get("data") or data.get("observations") or []
    if not observations and isinstance(data.get("values"), list):
        observations = data["values"]

    latest_value = math.nan
    previous_value = math.nan
    latest_date = None

    if isinstance(observations, list) and observations:
        rows = [row for row in observations if isinstance(row, dict)]
        if rows:
            latest = rows[-1]
            latest_value = market_number(latest.get("value") or latest.get("close") or latest.get("v"))
            latest_date = latest.get("date") or latest.get("time")
            if len(rows) > 1:
                previous_value = market_number(rows[-2].get("value") or rows[-2].get("close") or rows[-2].get("v"))

    if not is_finite(latest_value) and isinstance(data, dict):
        latest_value = market_number(data.get("latest") or data.get("value"))
        previous_value = market_number(data.get("previous"))

    change = latest_value - previous_value if is_finite(latest_value) and is_finite(previous_value) else math.nan
    change_pct = (change / previous_value) * 100 if is_finite(change) and is_finite(previous_value) and previous_value else math.nan

    return Quote(
        symbol=item["symbol"],
        name=item.get("name", item["symbol"]),
        zh_name=item.get("zhName", item.get("name", item["symbol"])),
        group=item.get("group", "rates"),
        region=item.get("region", "global"),
        price=latest_value,
        change=change,
        change_pct=change_pct,
        source="ConvexTrade / FRED",
        source_url="https://convextrade.com/tools/api",
        updated_at=f"{latest_date}T00:00:00Z" if latest_date and "T" not in str(latest_date) else latest_date,
        quality="real" if is_finite(latest_value) else "unavailable",
        extra={"unit": item.get("unit", ""), "convexId": series_id},
    )
