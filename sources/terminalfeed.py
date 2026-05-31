from __future__ import annotations

from typing import Any

from sources.base import HttpClient


def fetch_terminalfeed_headlines(client: HttpClient, limit: int = 8) -> list[dict[str, Any]]:
    try:
        data = client.get_json("https://terminalfeed.io/api/briefing", timeout=12)
        headlines: list[dict[str, Any]] = []
        for key in ("news", "headlines", "items"):
            rows = data.get(key)
            if isinstance(rows, list):
                for row in rows[:limit]:
                    if isinstance(row, dict):
                        headlines.append({
                            "title": row.get("title") or row.get("headline") or str(row),
                            "url": row.get("url") or row.get("link") or "",
                            "source": row.get("source") or "TerminalFeed",
                        })
                if headlines:
                    return headlines[:limit]
        if isinstance(data.get("markets"), dict):
            for section, rows in data["markets"].items():
                if isinstance(rows, list):
                    for row in rows[:3]:
                        if isinstance(row, dict):
                            headlines.append({
                                "title": f"[{section}] {row.get('name', row.get('symbol', ''))} {row.get('change', '')}",
                                "url": "",
                                "source": "TerminalFeed Briefing",
                            })
        return headlines[:limit]
    except Exception:
        return []
