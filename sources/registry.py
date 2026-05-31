from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

from sources.base import HttpClient, Quote, TTLCache
from sources.crypto import fetch_coingecko_quote, fetch_fear_greed
from sources.macro import fetch_convex_series
from sources.yahoo_quotes import fetch_yahoo_quote


class SourceRegistry:
    """Register and fetch quotes from configured asset groups."""

    SOURCE_META = [
        {"id": "sina", "label": "Sina Finance", "channels": ["equity_index"], "ttlSeconds": 20},
        {"id": "stooq", "label": "Stooq", "channels": ["equity_index"], "ttlSeconds": 20},
        {"id": "yahoo", "label": "Yahoo Finance", "channels": ["equity_index", "commodities", "volatility"], "ttlSeconds": 20},
        {"id": "frankfurter", "label": "Frankfurter", "channels": ["fx"], "ttlSeconds": 20},
        {"id": "convex", "label": "ConvexTrade / FRED", "channels": ["rates", "volatility"], "ttlSeconds": 3600},
        {"id": "coingecko", "label": "CoinGecko", "channels": ["crypto"], "ttlSeconds": 60},
        {"id": "terminalfeed", "label": "TerminalFeed", "channels": ["headlines"], "ttlSeconds": 300},
        {"id": "feargreed", "label": "Alternative.me", "channels": ["crypto"], "ttlSeconds": 300},
    ]

    def __init__(self, market_config: dict[str, Any]) -> None:
        self.config = market_config
        self.client = HttpClient()
        self.quote_cache = TTLCache(20)
        self.macro_cache = TTLCache(3600)
        self.crypto_cache = TTLCache(60)
        self._status: dict[str, dict[str, Any]] = {}

    def list_sources(self) -> list[dict[str, Any]]:
        rows = []
        for meta in self.SOURCE_META:
            status = self._status.get(meta["id"], {})
            rows.append({**meta, **status})
        return rows

    def _record_status(self, source_id: str, ok: bool, error: str = "") -> None:
        from datetime import datetime, timezone

        self._status[source_id] = {
            "ok": ok,
            "lastCheckedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "error": error or None,
        }

    def fetch_group_quotes(self, group_id: str) -> list[dict[str, Any]]:
        cache_key = f"group:{group_id}"
        cached = self.quote_cache.get(cache_key)
        if cached:
            return cached

        items = self._items_for_group(group_id)
        if not items:
            return []

        quotes: list[Quote] = []
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = {executor.submit(self._fetch_item, item): item for item in items}
            for future in as_completed(futures):
                item = futures[future]
                try:
                    quotes.append(future.result())
                except Exception as exc:  # noqa: BLE001
                    quotes.append(
                        Quote(
                            symbol=item.get("symbol", ""),
                            name=item.get("name", ""),
                            zh_name=item.get("zhName", ""),
                            group=group_id,
                            region=item.get("region", ""),
                            quality="unavailable",
                            source="暂不可用",
                            extra={"error": str(exc)},
                        )
                    )

        payload = [quote.to_dict() for quote in quotes]
        self.quote_cache.set(cache_key, payload)
        return payload

    def fetch_all_configured_quotes(self) -> list[dict[str, Any]]:
        groups = self.config.get("assetGroups") or []
        rows: list[dict[str, Any]] = []
        for group in groups:
            rows.extend(self.fetch_group_quotes(group["id"]))
        return rows

    def _items_for_group(self, group_id: str) -> list[dict[str, Any]]:
        for group in self.config.get("assetGroups") or []:
            if group.get("id") == group_id:
                return list(group.get("items") or [])
        return []

    def _fetch_item(self, item: dict[str, Any]) -> Quote:
        provider = item.get("provider", "yahoo")
        if provider == "convex":
            quote = fetch_convex_series(self.client, item)
            self._record_status("convex", quote.quality != "unavailable")
            return quote
        if provider == "coingecko":
            quote = fetch_coingecko_quote(self.client, item)
            self._record_status("coingecko", quote.quality != "unavailable")
            return quote
        quote = fetch_yahoo_quote(self.client, item)
        self._record_status("yahoo", quote.quality != "unavailable")
        return quote

    def fetch_fear_greed(self) -> dict[str, Any]:
        cached = self.crypto_cache.get("feargreed")
        if cached:
            return cached
        data = fetch_fear_greed(self.client)
        self.crypto_cache.set("feargreed", data)
        self._record_status("feargreed", data.get("value") is not None)
        return data
