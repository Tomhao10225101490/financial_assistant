from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any

from sources.base import TTLCache, is_finite
from sources.registry import SourceRegistry
from sources.rules import build_highlights
from sources.terminalfeed import fetch_terminalfeed_headlines


class BriefingService:
    def __init__(self, market_config: dict[str, Any], index_fetcher) -> None:
        self.config = market_config
        self.index_fetcher = index_fetcher
        self.registry = SourceRegistry(market_config)
        self.cache = TTLCache(15)
        self.headline_cache = TTLCache(300)

    def build_briefing(self) -> dict[str, Any]:
        cached = self.cache.get("briefing")
        if cached:
            return cached

        indices = self.index_fetcher()
        market_pulse = self._build_market_pulse(indices)
        macro = self.registry.fetch_group_quotes("rates") + self.registry.fetch_group_quotes("volatility")
        commodities = self.registry.fetch_group_quotes("commodities")
        crypto = self.registry.fetch_group_quotes("crypto")
        fear_greed = self.registry.fetch_fear_greed()
        headlines = self._fetch_headlines()

        payload = {
            "ok": True,
            "generatedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "marketPulse": market_pulse,
            "indices": indices,
            "macro": macro,
            "commodities": commodities,
            "crypto": crypto,
            "fearGreed": fear_greed,
            "headlines": headlines,
            "meta": {
                "sources": self.registry.list_sources(),
                "cacheSeconds": 15,
            },
        }
        payload["highlights"] = build_highlights(payload)
        self.cache.set("briefing", payload)
        return payload

    def _build_market_pulse(self, indices: list[dict[str, Any]]) -> dict[str, Any]:
        regions: dict[str, dict[str, Any]] = {}
        region_labels = {
            "asia": "亚太",
            "europe": "欧洲",
            "americas": "美洲",
            "global": "全球",
        }
        for index in indices:
            if index.get("unavailable") or not is_finite(index.get("price")):
                continue
            region = index.get("region") or self._region_from_timezone(index.get("timeZone", ""))
            bucket = regions.setdefault(
                region,
                {"id": region, "label": region_labels.get(region, region), "up": 0, "down": 0, "flat": 0, "total": 0, "items": []},
            )
            bucket["total"] += 1
            change = index.get("change") or 0
            if change > 0:
                bucket["up"] += 1
            elif change < 0:
                bucket["down"] += 1
            else:
                bucket["flat"] += 1
            bucket["items"].append({
                "symbol": index.get("symbol"),
                "zhName": index.get("zhName"),
                "changePct": index.get("changePct"),
            })

        up = sum(1 for item in indices if is_finite(item.get("change")) and item["change"] > 0)
        down = sum(1 for item in indices if is_finite(item.get("change")) and item["change"] < 0)
        return {
            "up": up,
            "down": down,
            "flat": max(0, len(indices) - up - down),
            "total": len(indices),
            "regions": list(regions.values()),
        }

    def _region_from_timezone(self, time_zone: str) -> str:
        if time_zone in {"Asia/Shanghai", "Asia/Hong_Kong", "Asia/Tokyo"}:
            return "asia"
        if time_zone in {"Europe/London", "Europe/Berlin", "Europe/Paris"}:
            return "europe"
        if time_zone in {"America/New_York"}:
            return "americas"
        return "global"

    def _fetch_headlines(self) -> list[dict[str, Any]]:
        cached = self.headline_cache.get("headlines")
        if cached:
            return cached
        headlines = fetch_terminalfeed_headlines(self.registry.client, limit=8)
        self.registry._record_status("terminalfeed", bool(headlines))
        self.headline_cache.set("headlines", headlines)
        return headlines

    def list_sources(self) -> dict[str, Any]:
        return {
            "ok": True,
            "sources": self.registry.list_sources(),
            "generatedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        }

    def fetch_quotes(self, group: str = "") -> dict[str, Any]:
        if group:
            quotes = self.registry.fetch_group_quotes(group)
        else:
            quotes = self.registry.fetch_all_configured_quotes()
        return {
            "ok": True,
            "group": group or "all",
            "quotes": quotes,
            "generatedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        }
