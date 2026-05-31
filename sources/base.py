from __future__ import annotations

import json
import math
import ssl
import time
from dataclasses import dataclass, field
from typing import Any
from urllib.request import Request, urlopen


def is_finite(value: Any) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(value)


def market_number(value: Any) -> float:
    if value in (None, "", "N/D"):
        return math.nan
    try:
        return float(str(value).replace("%", "").replace("+", "").replace(",", "").strip())
    except ValueError:
        return math.nan


class TTLCache:
    def __init__(self, ttl_seconds: int) -> None:
        self.ttl_seconds = ttl_seconds
        self.values: dict[str, tuple[float, Any]] = {}

    def get(self, key: str) -> Any | None:
        item = self.values.get(key)
        if not item:
            return None
        saved_at, value = item
        if time.time() - saved_at > self.ttl_seconds:
            return None
        return value

    def set(self, key: str, value: Any) -> None:
        self.values[key] = (time.time(), value)

    def stale(self, key: str) -> Any | None:
        item = self.values.get(key)
        return item[1] if item else None

    def age_seconds(self, key: str) -> int | None:
        item = self.values.get(key)
        if not item:
            return None
        return int(time.time() - item[0])


@dataclass
class Quote:
    symbol: str
    name: str
    zh_name: str = ""
    group: str = ""
    region: str = ""
    price: float = math.nan
    change: float = math.nan
    change_pct: float = math.nan
    source: str = ""
    source_url: str = ""
    updated_at: str | None = None
    quality: str = "real"
    stale: bool = False
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "symbol": self.symbol,
            "name": self.name,
            "zhName": self.zh_name or self.name,
            "group": self.group,
            "region": self.region,
            "price": self.price,
            "change": self.change,
            "changePct": self.change_pct,
            "source": self.source,
            "sourceUrl": self.source_url,
            "updatedAt": self.updated_at,
            "quality": self.quality,
            "stale": self.stale,
            **self.extra,
        }


class HttpClient:
    def __init__(self) -> None:
        self.ssl_context = ssl.create_default_context()

    def get_json(self, url: str, *, timeout: int = 10, headers: dict[str, str] | None = None) -> Any:
        return json.loads(self.get_text(url, timeout=timeout, headers=headers))

    def get_text(
        self,
        url: str,
        *,
        timeout: int = 10,
        encoding: str = "utf-8",
        headers: dict[str, str] | None = None,
        attempts: int = 2,
    ) -> str:
        base_headers = {
            "User-Agent": "MarketRadar/2.0 FinancialAssistant",
            "Accept": "application/json,text/plain,*/*",
        }
        if headers:
            base_headers.update(headers)
        request = Request(url, headers=base_headers)
        last_error: Exception | None = None
        for attempt in range(attempts):
            try:
                with urlopen(request, timeout=timeout, context=self.ssl_context) as response:
                    return response.read().decode(encoding, errors="replace")
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                time.sleep(0.35 * (attempt + 1))
        raise last_error or RuntimeError("request failed")
