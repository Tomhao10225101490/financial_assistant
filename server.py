from __future__ import annotations

import csv
import json
import math
import mimetypes
import ssl
import sys
import threading
import time
import traceback
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from email.utils import formatdate
from concurrent.futures import ThreadPoolExecutor, as_completed
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Callable
from urllib.parse import parse_qs, quote, unquote, urlparse
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parent
HOST = "127.0.0.1"
PORT = 18765
AUTO_REFRESH_SECONDS = 20
TREND_MODES = {"intraday", "daily", "monthly"}

CURRENCIES = [
    {"code": "USD", "name": "美元"},
    {"code": "CNY", "name": "人民币"},
    {"code": "EUR", "name": "欧元"},
    {"code": "JPY", "name": "日元"},
    {"code": "GBP", "name": "英镑"},
    {"code": "HKD", "name": "港币"},
    {"code": "AUD", "name": "澳元"},
    {"code": "CAD", "name": "加元"},
    {"code": "CHF", "name": "瑞郎"},
    {"code": "SGD", "name": "新加坡元"},
    {"code": "KRW", "name": "韩元"},
    {"code": "INR", "name": "印度卢比"},
]

REQUIRED_CURRENCIES = [item["code"] for item in CURRENCIES]

INDEX_SYMBOLS = [
    {"name": "S&P 500", "zhName": "标普500指数", "symbol": "^GSPC", "sinaGlobal": "gb_$inx", "sinaType": "us", "sinaDaily": ".inx", "stooq": ["^spx", "^gspc"], "timeZone": "America/New_York", "timeZoneLabel": "美东时间", "detailUrl": "https://www.spglobal.com/spdji/en/indices/equity/sp-500/"},
    {"name": "Nasdaq Composite", "zhName": "纳斯达克综合指数", "symbol": "^IXIC", "sinaGlobal": "gb_ixic", "sinaType": "us", "sinaDaily": ".ixic", "stooq": ["^ndq", "^comp", "^ixic"], "timeZone": "America/New_York", "timeZoneLabel": "美东时间", "detailUrl": "https://www.nasdaq.com/market-activity/index/comp"},
    {"name": "Dow Jones Industrial Average", "zhName": "道琼斯工业平均指数", "symbol": "^DJI", "sinaGlobal": "gb_$dji", "sinaType": "us", "sinaDaily": ".dji", "stooq": ["^dji"], "timeZone": "America/New_York", "timeZoneLabel": "美东时间", "detailUrl": "https://www.spglobal.com/spdji/en/indices/equity/dow-jones-industrial-average/"},
    {"name": "FTSE 100", "zhName": "富时100指数", "symbol": "^FTSE", "sinaGlobal": "b_FTSE", "sinaType": "b", "stooq": ["^uk100", "^ukx", "^ftse"], "timeZone": "Europe/London", "timeZoneLabel": "伦敦时间", "detailUrl": "https://www.lseg.com/en/ftse-russell/indices/uk"},
    {"name": "DAX", "zhName": "德国DAX指数", "symbol": "^GDAXI", "sinaGlobal": "b_DAX", "sinaType": "b", "stooq": ["^dax"], "timeZone": "Europe/Berlin", "timeZoneLabel": "法兰克福时间", "detailUrl": "https://www.dax-indices.com/"},
    {"name": "CAC 40", "zhName": "法国CAC40指数", "symbol": "^FCHI", "sinaGlobal": "b_CAC", "sinaType": "b", "stooq": ["^cac"], "timeZone": "Europe/Paris", "timeZoneLabel": "巴黎时间", "detailUrl": "https://live.euronext.com/en/product/indices/FR0003500008-XPAR"},
    {"name": "Nikkei 225", "zhName": "日经225指数", "symbol": "^N225", "sinaGlobal": "b_NKY", "sinaType": "b", "stooq": ["^nkx", "^n225"], "timeZone": "Asia/Tokyo", "timeZoneLabel": "东京时间", "detailUrl": "https://indexes.nikkei.co.jp/en/nkave/index/profile?idx=nk225"},
    {"name": "Hang Seng Index", "zhName": "恒生指数", "symbol": "^HSI", "stooq": ["^hsi"], "sina": "rt_hkHSI", "timeZone": "Asia/Hong_Kong", "timeZoneLabel": "香港时间", "detailUrl": "https://www.hsi.com.hk/eng/indexes/all-indexes/hsi"},
    {"name": "Shanghai Composite", "zhName": "上证综合指数", "symbol": "000001.SS", "stooq": ["^shc", "^ssec"], "sina": "sh000001", "timeZone": "Asia/Shanghai", "timeZoneLabel": "上海时间", "detailUrl": "https://english.sse.com.cn/markets/indices/overview/"},
    {"name": "CSI 300", "zhName": "沪深300指数", "symbol": "000300.SS", "stooq": ["csi300", "^csi300"], "sina": "sh000300", "timeZone": "Asia/Shanghai", "timeZoneLabel": "上海时间", "detailUrl": "https://www.csindex.com.cn/en/indices/index-detail/000300"},
]

FALLBACK_FX = {
    "base": "USD",
    "timestamp": None,
    "timeZone": "UTC",
    "timeZoneLabel": "协调世界时",
    "source": "内置参考值",
    "sourceUrl": "",
    "rates": {
        "USD": 1,
        "CNY": 7.22,
        "EUR": 0.93,
        "JPY": 155.5,
        "GBP": 0.79,
        "HKD": 7.82,
        "AUD": 1.52,
        "CAD": 1.37,
        "CHF": 0.91,
        "SGD": 1.35,
        "KRW": 1365,
        "INR": 83.4,
    },
    "stale": True,
}


class MiniApp:
    def __init__(self) -> None:
        self.routes: dict[tuple[str, str], Callable[["RequestContext"], Any]] = {}

    def get(self, path: str) -> Callable[[Callable[["RequestContext"], Any]], Callable[["RequestContext"], Any]]:
        def decorator(func: Callable[["RequestContext"], Any]) -> Callable[["RequestContext"], Any]:
            self.routes[("GET", path)] = func
            return func

        return decorator

    def dispatch(self, context: "RequestContext") -> Any:
        route = self.routes.get((context.method, context.path))
        if route:
            return route(context)
        return serve_static(context)


@dataclass
class RequestContext:
    method: str
    path: str
    query: dict[str, list[str]]
    handler: BaseHTTPRequestHandler

    def query_one(self, name: str, default: str = "") -> str:
        values = self.query.get(name)
        return values[0] if values else default


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


class MarketDataService:
    def __init__(self) -> None:
        self.fx_cache = TTLCache(AUTO_REFRESH_SECONDS)
        self.index_cache = TTLCache(AUTO_REFRESH_SECONDS)
        self.trend_cache = TTLCache(180)
        self.fx_lock = threading.Lock()
        self.index_lock = threading.Lock()
        self.trend_lock = threading.Lock()
        self.ssl_context = ssl.create_default_context()

    def fetch_fx(self, base: str) -> dict[str, Any]:
        normalized_base = normalize_currency(base)
        cache_key = f"fx:{normalized_base}"
        cached = self.fx_cache.get(cache_key)
        if cached:
            return cached

        with self.fx_lock:
            cached = self.fx_cache.get(cache_key)
            if cached:
                return cached
            return self._fetch_fx_uncached(normalized_base, cache_key)

    def _fetch_fx_uncached(self, normalized_base: str, cache_key: str) -> dict[str, Any]:
        errors: list[str] = []
        for fetcher in (self._fetch_fx_frankfurter, self._fetch_fx_currency_cdn, self._fetch_fx_currency_cloudflare):
            try:
                result = fetcher(normalized_base)
                if not has_required_rates(result["rates"]):
                    raise ValueError("missing required currencies")
                self.fx_cache.set(cache_key, result)
                return result
            except Exception as exc:  # noqa: BLE001
                errors.append(f"{fetcher.__name__}: {exc}")

        stale = self.fx_cache.stale(cache_key)
        if stale:
            return {**stale, "stale": True, "source": f'{stale["source"]} 缓存', "errors": errors}
        return {**rebase_fx(FALLBACK_FX, normalized_base), "errors": errors}

    def fetch_indices(self) -> list[dict[str, Any]]:
        cached = self.index_cache.get("indices")
        if cached:
            return cached

        with self.index_lock:
            cached = self.index_cache.get("indices")
            if cached:
                return cached
            return self._fetch_indices_uncached()

    def _fetch_indices_uncached(self) -> list[dict[str, Any]]:
        results = self._fetch_sina_indices_batch(INDEX_SYMBOLS)
        stooq_fallback = [
            index
            for index in INDEX_SYMBOLS
            if index.get("stooq") and results.get(index["symbol"], {}).get("unavailable")
        ]
        if stooq_fallback:
            try:
                results.update(self._fetch_stooq_indices_batch(stooq_fallback))
            except Exception:
                pass
        data = [results.get(index["symbol"], unavailable_index(index)) for index in INDEX_SYMBOLS]

        if any(item.get("unavailable") for item in data):
            yahoo_rows = self._fetch_yahoo_indices()
            by_symbol = {item["symbol"]: item for item in yahoo_rows if not item.get("unavailable")}
            data = [by_symbol.get(item["symbol"], item) if item.get("unavailable") else item for item in data]

        if any(is_finite(item.get("price")) for item in data):
            self.index_cache.set("indices", data)
            return data

        stale = self.index_cache.stale("indices")
        if stale:
            return [{**item, "stale": True, "source": f'{item["source"]} 缓存'} for item in stale]
        return data

    def health(self) -> dict[str, Any]:
        fx = self.fetch_fx("USD")
        indices = self.fetch_indices()
        live_indices = sum(1 for item in indices if is_finite(item.get("price")))
        return {
            "ok": has_required_rates(fx["rates"]) and live_indices == len(indices),
            "fxSource": fx.get("source"),
            "indicesLive": live_indices,
            "indicesTotal": len(indices),
            "autoRefreshSeconds": AUTO_REFRESH_SECONDS,
        }

    def fetch_trends(self, mode: str = "intraday", symbols: list[str] | None = None) -> list[dict[str, Any]]:
        trend_mode = normalize_trend_mode(mode)
        wanted_symbols = normalize_symbol_filter(symbols)
        cache_key = f"trends:{trend_mode}"
        cached = self.trend_cache.get(cache_key)
        if cached:
            return filter_trends(cached, wanted_symbols)

        with self.trend_lock:
            cached = self.trend_cache.get(cache_key)
            if cached:
                return filter_trends(cached, wanted_symbols)
            indices = {item["symbol"]: item for item in self.fetch_indices()}
            data = self._fetch_trends_uncached(indices, trend_mode)
            if data:
                self.trend_cache.set(cache_key, data)
                return filter_trends(data, wanted_symbols)
            stale = self.trend_cache.stale(cache_key)
            return filter_trends(stale or [], wanted_symbols)

    def _fetch_trends_uncached(self, current_rows: dict[str, dict[str, Any]], mode: str) -> list[dict[str, Any]]:
        trends: list[dict[str, Any]] = []
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = {
                executor.submit(self._fetch_index_trend, index, current_rows.get(index["symbol"], {}), mode): index
                for index in INDEX_SYMBOLS
            }
            for future in as_completed(futures):
                index = futures[future]
                try:
                    trends.append(future.result())
                except Exception:
                    trends.append(derive_session_trend(index, current_rows.get(index["symbol"], {}), mode))
        by_symbol = {item["symbol"]: item for item in trends}
        return [by_symbol[index["symbol"]] for index in INDEX_SYMBOLS if index["symbol"] in by_symbol]

    def _fetch_index_trend(self, index: dict[str, Any], current: dict[str, Any], mode: str) -> dict[str, Any]:
        if mode == "intraday":
            if index.get("sina") in {"sh000001", "sh000300"}:
                trend = self._fetch_sina_cn_intraday_trend(index)
                if trend["points"]:
                    return trend
            return derive_session_trend(index, current, mode, "公开分时 K 线暂不可用，使用同源行情区间兜底")

        if mode == "monthly":
            if index.get("sinaDaily"):
                trend = self._fetch_sina_us_daily_trend(index, limit=520)
                monthly = aggregate_monthly_trend(index, trend)
                if monthly["points"]:
                    return monthly
            if index.get("sina") in {"sh000001", "sh000300"}:
                trend = self._fetch_sina_cn_daily_trend(index, limit=720)
                monthly = aggregate_monthly_trend(index, trend)
                if monthly["points"]:
                    return monthly
            return derive_session_trend(index, current, mode, "暂无稳定真实月 K，使用同源行情区间兜底")

        if index.get("sinaDaily"):
            trend = self._fetch_sina_us_daily_trend(index, limit=90)
            if trend["points"]:
                return trend
        if index.get("sina") in {"sh000001", "sh000300"}:
            trend = self._fetch_sina_cn_daily_trend(index, limit=90)
            if trend["points"]:
                return trend
        return derive_session_trend(index, current, mode, "暂无稳定真实日 K，使用同源行情区间兜底")

    def _fetch_fx_frankfurter(self, base: str) -> dict[str, Any]:
        symbols = ",".join(code for code in REQUIRED_CURRENCIES if code != base)
        url = f"https://api.frankfurter.dev/v1/latest?base={quote(base)}&symbols={quote(symbols)}"
        data = self._json(url)
        rates = normalize_rates({**data["rates"], base: 1})
        return {
            "base": data.get("base", base).upper(),
            "timestamp": f'{data["date"]}T00:00:00Z' if data.get("date") else None,
            "timeZone": "UTC",
            "timeZoneLabel": "协调世界时",
            "source": "Frankfurter",
            "sourceUrl": "https://www.ecb.europa.eu/stats/eurofxref",
            "rates": rates,
        }

    def _fetch_fx_currency_cdn(self, base: str) -> dict[str, Any]:
        return self._fetch_fx_currency_api(base, "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest")

    def _fetch_fx_currency_cloudflare(self, base: str) -> dict[str, Any]:
        return self._fetch_fx_currency_api(base, "https://latest.currency-api.pages.dev")

    def _fetch_fx_currency_api(self, base: str, origin: str) -> dict[str, Any]:
        lower = base.lower()
        data = self._json(f"{origin}/v1/currencies/{quote(lower)}.json")
        rates = data.get(lower)
        if not isinstance(rates, dict):
            raise ValueError("invalid currency payload")
        return {
            "base": base,
            "timestamp": f'{data["date"]}T00:00:00Z' if data.get("date") else None,
            "timeZone": "UTC",
            "timeZoneLabel": "协调世界时",
            "source": "Currency API",
            "sourceUrl": "https://www.ecb.europa.eu/stats/eurofxref",
            "rates": normalize_rates({**rates, lower: 1}),
        }

    def _fetch_stooq_indices_batch(self, indices: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
        if not indices:
            return {}

        primary_aliases = [index["stooq"][0] for index in indices]
        url = f"https://stooq.com/q/l/?s={quote(','.join(primary_aliases), safe='^,')}&f=sd2t2ohlcpn&e=csv"
        rows = parse_stooq_quotes(self._stooq_text(url))
        rows_by_symbol = {row.get("symbol", "").lower(): row for row in rows}
        results: dict[str, dict[str, Any]] = {}

        for index in indices:
            row = next(
                (rows_by_symbol.get(alias.lower()) for alias in index["stooq"] if rows_by_symbol.get(alias.lower())),
                None,
            )
            mapped = map_stooq_index(index, row or {})
            if mapped.get("unavailable"):
                mapped = self._fetch_stooq_index(index)
            if not mapped.get("unavailable"):
                mapped["source"] = "Stooq Batch"
            results[index["symbol"]] = mapped
        return results

    def _fetch_stooq_index(self, index: dict[str, Any]) -> dict[str, Any]:
        for alias in index["stooq"]:
            try:
                url = f"https://stooq.com/q/l/?s={quote(alias, safe='^')}&f=sd2t2ohlcpn&e=csv"
                row = parse_stooq_quote(self._stooq_text(url))
                mapped = map_stooq_index(index, row)
                if not mapped.get("unavailable"):
                    return mapped
            except Exception as exc:  # noqa: BLE001
                continue
        return unavailable_index(index)

    def _fetch_sina_indices_batch(self, indices: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
        codes = [index.get("sinaGlobal") or index.get("sina") for index in indices]
        codes = [code for code in codes if code]
        if not codes:
            return {}

        text = self._sina_text(f"https://hq.sinajs.cn/list={quote(','.join(codes), safe='$,')}")
        payloads = parse_sina_payloads(text)
        results: dict[str, dict[str, Any]] = {}
        for index in indices:
            code = index.get("sinaGlobal") or index.get("sina")
            fields = payloads.get(code, [])
            try:
                if index.get("sinaType") == "us":
                    results[index["symbol"]] = map_sina_us_global_index(index, fields)
                elif index.get("sinaType") == "b":
                    results[index["symbol"]] = map_sina_b_global_index(index, fields)
                elif code and code.startswith("rt_hk"):
                    results[index["symbol"]] = map_sina_hk_index(index, fields)
                elif code:
                    results[index["symbol"]] = map_sina_cn_index(index, fields)
                else:
                    results[index["symbol"]] = unavailable_index(index)
            except Exception:
                results[index["symbol"]] = unavailable_index(index)
        return results

    def _fetch_sina_index(self, index: dict[str, Any]) -> dict[str, Any]:
        try:
            code = index["sina"]
            text = self._sina_text(f"https://hq.sinajs.cn/list={quote(code)}")
            payload = text.split('="', 1)[1].rsplit('";', 1)[0]
            fields = payload.split(",")
            if code.startswith("rt_hk"):
                return map_sina_hk_index(index, fields)
            return map_sina_cn_index(index, fields)
        except Exception:
            return unavailable_index(index)

    def _fetch_yahoo_indices(self) -> list[dict[str, Any]]:
        rows = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(self._fetch_yahoo_index, index): index for index in INDEX_SYMBOLS}
            for future in as_completed(futures):
                try:
                    rows.append(future.result())
                except Exception:
                    rows.append(unavailable_index(futures[future]))
        return rows

    def _fetch_yahoo_index(self, index: dict[str, Any]) -> dict[str, Any]:
        symbol = quote(index["symbol"])
        data = self._json(f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=5d&interval=1d")
        result = data["chart"]["result"][0]
        meta = result["meta"]
        quote_row = result.get("indicators", {}).get("quote", [{}])[0]
        closes = [value for value in quote_row.get("close", []) if is_finite(value)]
        price = market_number(meta.get("regularMarketPrice") or (closes[-1] if closes else None))
        previous = market_number(meta.get("chartPreviousClose") or meta.get("previousClose") or (closes[-2] if len(closes) > 1 else None))
        change = price - previous if is_finite(price) and is_finite(previous) else math.nan
        change_pct = (change / previous) * 100 if is_finite(change) and is_finite(previous) and previous else math.nan
        return {
            "name": index["name"],
            "zhName": index.get("zhName", index["name"]),
            "symbol": index["symbol"],
            "price": price,
            "change": change,
            "changePct": change_pct,
            "updatedAt": iso_from_epoch(meta.get("regularMarketTime")),
            "timeZone": index["timeZone"],
            "timeZoneLabel": index["timeZoneLabel"],
            "detailUrl": index["detailUrl"],
            "source": "Yahoo Finance Chart",
        }

    def _fetch_yahoo_trend(self, index: dict[str, Any], mode: str) -> dict[str, Any]:
        range_value, interval = {
            "intraday": ("1d", "5m"),
            "daily": ("6mo", "1d"),
            "monthly": ("5y", "1mo"),
        }.get(mode, ("6mo", "1d"))
        symbol = quote(index["symbol"])
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range={range_value}&interval={interval}"
        data = self._json(url)
        result = data["chart"]["result"][0]
        timestamps = result.get("timestamp") or []
        quote_row = result.get("indicators", {}).get("quote", [{}])[0]
        closes = quote_row.get("close") or []
        opens = quote_row.get("open") or []
        highs = quote_row.get("high") or []
        lows = quote_row.get("low") or []
        points: list[dict[str, Any]] = []

        for index_at, raw_time in enumerate(timestamps):
            close = market_number(closes[index_at] if index_at < len(closes) else None)
            if not is_finite(close):
                continue
            point = {
                "time": iso_from_epoch(raw_time),
                "value": close,
                "open": market_number(opens[index_at] if index_at < len(opens) else None),
                "high": market_number(highs[index_at] if index_at < len(highs) else None),
                "low": market_number(lows[index_at] if index_at < len(lows) else None),
                "close": close,
            }
            points.append(clean_point(point))

        return make_trend(
            index,
            points[-120:],
            mode,
            "Yahoo Finance Chart",
            f"https://finance.yahoo.com/chart/{quote(index['symbol'], safe='')}",
            "real",
        )

    def _fetch_sina_us_daily_trend(self, index: dict[str, Any], limit: int = 90) -> dict[str, Any]:
        symbol = index["sinaDaily"]
        url = f"https://stock.finance.sina.com.cn/usstock/api/jsonp.php/var%20trend=/US_MinKService.getDailyK?symbol={quote(symbol)}"
        rows = parse_jsonp_array(self._text(url))
        points = [
            clean_point({
                "time": row.get("d"),
                "value": market_number(row.get("c")),
                "open": market_number(row.get("o")),
                "high": market_number(row.get("h")),
                "low": market_number(row.get("l")),
                "close": market_number(row.get("c")),
            })
            for row in rows[-limit:]
            if isinstance(row, dict) and is_finite(market_number(row.get("c")))
        ]
        return make_trend(index, points, "daily", "Sina US Daily K", "https://finance.sina.com.cn/stock/usstock/", "real")

    def _fetch_sina_cn_intraday_trend(self, index: dict[str, Any]) -> dict[str, Any]:
        symbol = index["sina"]
        urls = [
            f"https://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol={quote(symbol)}&scale=5&ma=0&datalen=96",
            f"https://quotes.sina.cn/cn/api/json_v2.php/CN_MarketData.getKLineData?symbol={quote(symbol)}&scale=5&ma=0&datalen=96",
        ]
        rows: Any = []
        for url in urls:
            try:
                rows = self._json(url)
                if isinstance(rows, list) and rows:
                    break
            except Exception:
                rows = []
        if not isinstance(rows, list):
            rows = []
        points = [
            clean_point({
                "time": row.get("day"),
                "value": market_number(row.get("close")),
                "open": market_number(row.get("open")),
                "high": market_number(row.get("high")),
                "low": market_number(row.get("low")),
                "close": market_number(row.get("close")),
            })
            for row in rows[-96:]
            if isinstance(row, dict) and is_finite(market_number(row.get("close")))
        ]
        return make_trend(index, points, "intraday", "Sina CN 5m K", "https://finance.sina.com.cn/", "real")

    def _fetch_sina_cn_daily_trend(self, index: dict[str, Any], limit: int = 90) -> dict[str, Any]:
        symbol = index["sina"]
        url = f"https://quotes.sina.cn/cn/api/json_v2.php/CN_MarketDataService.getKLineData?symbol={quote(symbol)}&scale=240&datalen={limit}"
        rows = self._json(url)
        if not isinstance(rows, list):
            rows = []
        points = [
            clean_point({
                "time": row.get("day"),
                "value": market_number(row.get("close")),
                "open": market_number(row.get("open")),
                "high": market_number(row.get("high")),
                "low": market_number(row.get("low")),
                "close": market_number(row.get("close")),
            })
            for row in rows[-limit:]
            if isinstance(row, dict) and is_finite(market_number(row.get("close")))
        ]
        return make_trend(index, points, "daily", "Sina CN Daily K", "https://finance.sina.com.cn/", "real")

    def _json(self, url: str) -> Any:
        return json.loads(self._text(url))

    def _text(self, url: str) -> str:
        return self._request_text(url, "utf-8")

    def _stooq_text(self, url: str) -> str:
        return self._request_text(url, "utf-8", timeout=7, attempts=2)

    def _sina_text(self, url: str) -> str:
        return self._request_text(url, "gbk", {"Referer": "https://finance.sina.com.cn/"})

    def _request_text(
        self,
        url: str,
        encoding: str,
        extra_headers: dict[str, str] | None = None,
        timeout: int = 10,
        attempts: int = 2,
    ) -> str:
        headers = {
            "User-Agent": "Mozilla/5.0 FinancialAssistant/1.0",
            "Accept": "application/json,text/csv,text/plain,*/*",
        }
        if extra_headers:
            headers.update(extra_headers)
        request = Request(
            url,
            headers=headers,
        )
        last_error: Exception | None = None
        for attempt in range(attempts):
            try:
                with urlopen(request, timeout=timeout, context=self.ssl_context) as response:
                    return response.read().decode(encoding, errors="replace")
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                time.sleep(0.35 * (attempt + 1))
        raise last_error or RuntimeError("request failed")


service = MarketDataService()
app = MiniApp()


@app.get("/api/fx")
def api_fx(context: RequestContext) -> dict[str, Any]:
    return {"ok": True, **service.fetch_fx(context.query_one("base", "USD"))}


@app.get("/api/indices")
def api_indices(_: RequestContext) -> dict[str, Any]:
    return {"ok": True, "indices": service.fetch_indices()}


@app.get("/api/trends")
def api_trends(context: RequestContext) -> dict[str, Any]:
    mode = normalize_trend_mode(context.query_one("mode", "intraday"))
    raw_symbols = context.query_one("symbols", "")
    symbols = [item.strip() for item in raw_symbols.split(",") if item.strip()] if raw_symbols else None
    return {"ok": True, "mode": mode, "trends": service.fetch_trends(mode, symbols)}


@app.get("/api/health")
def api_health(_: RequestContext) -> dict[str, Any]:
    return service.health()


def normalize_currency(value: str) -> str:
    code = (value or "USD").upper()
    return code if code in REQUIRED_CURRENCIES else "USD"


def normalize_rates(rates: dict[str, Any]) -> dict[str, float]:
    return {str(code).upper(): float(rate) for code, rate in rates.items()}


def has_required_rates(rates: dict[str, Any]) -> bool:
    return all(is_finite(rates.get(code)) for code in REQUIRED_CURRENCIES)


def normalize_trend_mode(value: str) -> str:
    mode = (value or "intraday").strip().lower()
    return mode if mode in TREND_MODES else "intraday"


def normalize_symbol_filter(symbols: list[str] | None) -> set[str]:
    return {symbol.strip().upper() for symbol in symbols or [] if symbol.strip()}


def filter_trends(trends: list[dict[str, Any]], wanted_symbols: set[str]) -> list[dict[str, Any]]:
    if not wanted_symbols:
        return trends
    return [item for item in trends if str(item.get("symbol", "")).upper() in wanted_symbols]


def rebase_fx(snapshot: dict[str, Any], target_base: str) -> dict[str, Any]:
    target_rate = snapshot["rates"].get(target_base)
    if not is_finite(target_rate) or target_rate == 0:
        return snapshot
    rates = {code: float(rate) / float(target_rate) for code, rate in snapshot["rates"].items()}
    rates[target_base] = 1
    return {**snapshot, "base": target_base, "rates": rates}


def parse_stooq_quote(text: str) -> dict[str, str]:
    rows = parse_stooq_quotes(text)
    return rows[0] if rows else {}


def parse_stooq_quotes(text: str) -> list[dict[str, str]]:
    lines = [item.strip() for item in text.splitlines() if item.strip()]
    if not lines:
        return []

    first_cells = next(csv.reader([lines[0]]))
    has_header = bool(first_cells and first_cells[0].strip().lower() == "symbol")
    data_lines = lines[1:] if has_header else lines
    if has_header:
        keys = [normalize_stooq_header(cell) for cell in first_cells]
    else:
        keys = ["symbol", "date", "time", "open", "high", "low", "close", "previousClose", "name"]

    rows = []
    for line in data_lines:
        cells = next(csv.reader([line]))
        row = {key: cells[index] if index < len(cells) else "" for index, key in enumerate(keys)}
        rows.append(row)
    return rows


def normalize_stooq_header(header: str) -> str:
    normalized = header.strip().lower().replace(" ", "")
    aliases = {
        "previousclose": "previousClose",
        "prevclose": "previousClose",
    }
    return aliases.get(normalized, normalized)


def parse_sina_payloads(text: str) -> dict[str, list[str]]:
    payloads: dict[str, list[str]] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("var hq_str_") or '="' not in line:
            continue
        code = line.split("=", 1)[0].replace("var hq_str_", "").strip()
        payload = line.split('="', 1)[1].rsplit('";', 1)[0]
        payloads[code] = payload.split(",") if payload else []
    return payloads


def parse_jsonp_array(text: str) -> list[Any]:
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1 or end <= start:
        return []
    try:
        value = json.loads(text[start : end + 1])
        return value if isinstance(value, list) else []
    except json.JSONDecodeError:
        return []


def clean_point(point: dict[str, Any]) -> dict[str, Any]:
    cleaned: dict[str, Any] = {
        "time": point.get("time") or "",
        "value": market_number(point.get("value")),
    }
    for key in ("open", "high", "low", "close"):
        value = market_number(point.get(key))
        if is_finite(value):
            cleaned[key] = value
    return cleaned


def make_trend(
    index: dict[str, Any],
    points: list[dict[str, Any]],
    mode: str,
    source: str,
    source_url: str,
    quality: str,
    fallback_reason: str = "",
    derived: bool = False,
) -> dict[str, Any]:
    return {
        "symbol": index["symbol"],
        "mode": mode,
        "points": points,
        "source": source,
        "sourceUrl": source_url,
        "updatedAt": trend_updated_at(points, index.get("timeZone", "UTC")),
        "timeZone": index.get("timeZone", "UTC"),
        "timeZoneLabel": index.get("timeZoneLabel", "数据源时间"),
        "quality": quality,
        "fallbackReason": fallback_reason,
        "derived": derived,
    }


def aggregate_monthly_trend(index: dict[str, Any], daily_trend: dict[str, Any]) -> dict[str, Any]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for point in daily_trend.get("points", []):
        raw_time = str(point.get("time") or "")
        month = raw_time[:7]
        if len(month) == 7:
            groups.setdefault(month, []).append(point)

    monthly: list[dict[str, Any]] = []
    for month, rows in sorted(groups.items()):
        values = [market_number(row.get("value")) for row in rows if is_finite(market_number(row.get("value")))]
        if not values:
            continue
        opens = [market_number(row.get("open")) for row in rows if is_finite(market_number(row.get("open")))]
        highs = [market_number(row.get("high") or row.get("value")) for row in rows if is_finite(market_number(row.get("high") or row.get("value")))]
        lows = [market_number(row.get("low") or row.get("value")) for row in rows if is_finite(market_number(row.get("low") or row.get("value")))]
        monthly.append(clean_point({
            "time": month,
            "open": opens[0] if opens else values[0],
            "high": max(highs) if highs else max(values),
            "low": min(lows) if lows else min(values),
            "close": values[-1],
            "value": values[-1],
        }))

    return make_trend(
        index,
        monthly[-60:],
        "monthly",
        f'{daily_trend.get("source", "Daily K")} 月线聚合',
        daily_trend.get("sourceUrl", index.get("detailUrl", "")),
        "real",
    )


def trend_updated_at(points: list[dict[str, Any]], time_zone: str) -> str | None:
    if not points:
        return None
    raw_time = str(points[-1].get("time") or "")
    if not raw_time:
        return None
    if "T" in raw_time:
        return raw_time
    if len(raw_time) == 7:
        raw_time = f"{raw_time}-01"
    try:
        if len(raw_time) == 10:
            local_dt = datetime.strptime(raw_time, "%Y-%m-%d").replace(hour=15)
            return local_datetime_to_utc_iso(local_dt, time_zone)
        if len(raw_time) >= 19:
            local_dt = datetime.strptime(raw_time[:19], "%Y-%m-%d %H:%M:%S")
            return local_datetime_to_utc_iso(local_dt, time_zone)
    except ValueError:
        return None
    return None


def local_datetime_to_utc_iso(local_dt: datetime, time_zone: str) -> str:
    offset_minutes = timezone_offset_minutes(time_zone, local_dt)
    utc_timestamp = local_dt.replace(tzinfo=timezone.utc).timestamp() - (offset_minutes * 60)
    return datetime.fromtimestamp(utc_timestamp, timezone.utc).isoformat().replace("+00:00", "Z")


def map_stooq_index(index: dict[str, Any], row: dict[str, str]) -> dict[str, Any]:
    close = market_number(row.get("close"))
    open_price = market_number(row.get("open"))
    previous = market_number(row.get("previousClose") or row.get("previousclose") or row.get("prevClose"))
    change = close - previous if is_finite(close) and is_finite(previous) else math.nan
    change_pct = (change / previous) * 100 if is_finite(change) and previous else math.nan

    if not is_finite(close):
        return unavailable_index(index)

    return {
        "name": index["name"],
        "zhName": index.get("zhName", index["name"]),
        "symbol": index["symbol"],
        "price": close,
        "change": change,
        "changePct": change_pct,
        "previousClose": previous if is_finite(previous) else None,
        "sessionOpen": open_price if is_finite(open_price) else None,
        "dayHigh": market_number(row.get("high")) if is_finite(market_number(row.get("high"))) else None,
        "dayLow": market_number(row.get("low")) if is_finite(market_number(row.get("low"))) else None,
        "updatedAt": parse_stooq_time(row.get("date"), row.get("time"), index["timeZone"]),
        "timeZone": index["timeZone"],
        "timeZoneLabel": index["timeZoneLabel"],
        "detailUrl": index["detailUrl"],
        "source": "Stooq",
    }


def map_sina_us_global_index(index: dict[str, Any], fields: list[str]) -> dict[str, Any]:
    price = market_number(fields[1] if len(fields) > 1 else None)
    change_pct = market_number(fields[2] if len(fields) > 2 else None)
    change = market_number(fields[4] if len(fields) > 4 else None)
    session_open = market_number(fields[5] if len(fields) > 5 else None)
    day_high = market_number(fields[6] if len(fields) > 6 else None)
    day_low = market_number(fields[7] if len(fields) > 7 else None)
    previous = market_number(fields[26] if len(fields) > 26 else None)
    if not is_finite(previous) and is_finite(price) and is_finite(change):
        previous = price - change
    updated_at = parse_sina_beijing_datetime(fields[3] if len(fields) > 3 else None)
    if not is_finite(price):
        return unavailable_index(index)
    return {
        "name": index["name"],
        "zhName": index.get("zhName", index["name"]),
        "symbol": index["symbol"],
        "price": price,
        "change": change,
        "changePct": change_pct,
        "previousClose": previous if is_finite(previous) else None,
        "sessionOpen": session_open if is_finite(session_open) else None,
        "dayHigh": day_high if is_finite(day_high) else None,
        "dayLow": day_low if is_finite(day_low) else None,
        "updatedAt": updated_at,
        "timeZone": index["timeZone"],
        "timeZoneLabel": index["timeZoneLabel"],
        "detailUrl": index["detailUrl"],
        "source": "Sina Finance Global",
    }


def map_sina_b_global_index(index: dict[str, Any], fields: list[str]) -> dict[str, Any]:
    price = market_number(fields[1] if len(fields) > 1 else None)
    change = market_number(fields[2] if len(fields) > 2 else None)
    change_pct = market_number(fields[3] if len(fields) > 3 else None)
    date = fields[6] if len(fields) > 6 else None
    raw_time = first_clock_time(fields[5] if len(fields) > 5 else None, fields[7] if len(fields) > 7 else None)
    session_open = market_number(fields[8] if len(fields) > 8 else None)
    previous = market_number(fields[9] if len(fields) > 9 else None)
    day_high = market_number(fields[10] if len(fields) > 10 else None)
    day_low = market_number(fields[11] if len(fields) > 11 else None)
    if not is_finite(previous) and is_finite(price) and is_finite(change):
        previous = price - change
    if not is_finite(price):
        return unavailable_index(index)
    return {
        "name": index["name"],
        "zhName": index.get("zhName", index["name"]),
        "symbol": index["symbol"],
        "price": price,
        "change": change,
        "changePct": change_pct,
        "previousClose": previous if is_finite(previous) else None,
        "sessionOpen": session_open if is_finite(session_open) else None,
        "dayHigh": day_high if is_finite(day_high) else None,
        "dayLow": day_low if is_finite(day_low) else None,
        "updatedAt": parse_stooq_time(date, raw_time, "Asia/Shanghai"),
        "timeZone": index["timeZone"],
        "timeZoneLabel": index["timeZoneLabel"],
        "detailUrl": index["detailUrl"],
        "source": "Sina Finance Global",
    }


def map_sina_cn_index(index: dict[str, Any], fields: list[str]) -> dict[str, Any]:
    session_open = market_number(fields[1] if len(fields) > 1 else None)
    previous = market_number(fields[2] if len(fields) > 2 else None)
    price = market_number(fields[3] if len(fields) > 3 else None)
    day_high = market_number(fields[4] if len(fields) > 4 else None)
    day_low = market_number(fields[5] if len(fields) > 5 else None)
    change = price - previous if is_finite(price) and is_finite(previous) else math.nan
    change_pct = (change / previous) * 100 if is_finite(change) and previous else math.nan
    date = fields[30] if len(fields) > 30 else None
    raw_time = fields[31] if len(fields) > 31 else None
    if not is_finite(price):
        return unavailable_index(index)
    return {
        "name": index["name"],
        "zhName": index.get("zhName", index["name"]),
        "symbol": index["symbol"],
        "price": price,
        "change": change,
        "changePct": change_pct,
        "previousClose": previous if is_finite(previous) else None,
        "sessionOpen": session_open if is_finite(session_open) else None,
        "dayHigh": day_high if is_finite(day_high) else None,
        "dayLow": day_low if is_finite(day_low) else None,
        "updatedAt": parse_stooq_time(date, raw_time, index["timeZone"]),
        "timeZone": index["timeZone"],
        "timeZoneLabel": index["timeZoneLabel"],
        "detailUrl": index["detailUrl"],
        "source": "Sina Finance",
    }


def map_sina_hk_index(index: dict[str, Any], fields: list[str]) -> dict[str, Any]:
    session_open = market_number(fields[2] if len(fields) > 2 else None)
    previous = market_number(fields[3] if len(fields) > 3 else None)
    day_high = market_number(fields[4] if len(fields) > 4 else None)
    day_low = market_number(fields[5] if len(fields) > 5 else None)
    price = market_number(fields[6] if len(fields) > 6 else None)
    change = market_number(fields[7] if len(fields) > 7 else None)
    change_pct = market_number(fields[8] if len(fields) > 8 else None)
    if not is_finite(previous) and is_finite(price) and is_finite(change):
        previous = price - change
    date = fields[17].replace("/", "-") if len(fields) > 17 else None
    raw_time = fields[18] if len(fields) > 18 else None
    if not is_finite(price):
        return unavailable_index(index)
    return {
        "name": index["name"],
        "zhName": index.get("zhName", index["name"]),
        "symbol": index["symbol"],
        "price": price,
        "change": change,
        "changePct": change_pct,
        "previousClose": previous if is_finite(previous) else None,
        "sessionOpen": session_open if is_finite(session_open) else None,
        "dayHigh": day_high if is_finite(day_high) else None,
        "dayLow": day_low if is_finite(day_low) else None,
        "updatedAt": parse_stooq_time(date, raw_time, index["timeZone"]),
        "timeZone": index["timeZone"],
        "timeZoneLabel": index["timeZoneLabel"],
        "detailUrl": index["detailUrl"],
        "source": "Sina Finance",
    }


def market_number(value: Any) -> float:
    if value in (None, "", "N/D"):
        return math.nan
    try:
        return float(str(value).replace("%", "").replace("+", "").replace(",", "").strip())
    except ValueError:
        return math.nan


def is_finite(value: Any) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(value)


def parse_sina_beijing_datetime(value: str | None) -> str | None:
    if not value:
        return None
    try:
        date, raw_time = value.strip().split(" ", 1)
    except ValueError:
        return None
    return parse_stooq_time(date, raw_time, "Asia/Shanghai")


def first_clock_time(*values: str | None) -> str | None:
    for value in values:
        if not value:
            continue
        candidate = value.strip()
        try:
            datetime.strptime(candidate, "%H:%M:%S")
            return candidate
        except ValueError:
            continue
    return None


def derive_session_trend(
    index: dict[str, Any],
    current: dict[str, Any],
    mode: str = "intraday",
    fallback_reason: str = "真实 K 线暂不可用，使用同源行情区间兜底",
) -> dict[str, Any]:
    price = market_number(current.get("price"))
    previous = market_number(current.get("previousClose"))
    session_open = market_number(current.get("sessionOpen"))
    high = market_number(current.get("dayHigh"))
    low = market_number(current.get("dayLow"))

    points: list[dict[str, Any]] = []
    for label, value in (
        ("昨收", previous),
        ("开盘", session_open),
        ("低点", low),
        ("高点", high),
        ("最新", price),
    ):
        if is_finite(value):
            points.append({"time": label, "value": value})

    if len(points) < 2:
        points = [{"time": "最新", "value": price}] if is_finite(price) else []

    return {
        "symbol": index["symbol"],
        "mode": mode,
        "points": points,
        "source": current.get("source", "Session Range"),
        "sourceUrl": current.get("detailUrl", index.get("detailUrl", "")),
        "updatedAt": current.get("updatedAt"),
        "timeZone": index.get("timeZone", "UTC"),
        "timeZoneLabel": index.get("timeZoneLabel", "数据源时间"),
        "quality": "fallback",
        "fallbackReason": fallback_reason,
        "derived": True,
    }


def parse_stooq_time(date: str | None, raw_time: str | None, time_zone: str) -> str | None:
    if not date or date == "N/D":
        return None
    safe_time = raw_time if raw_time and raw_time != "N/D" else "00:00:00"
    try:
        local_dt = datetime.strptime(f"{date} {safe_time}", "%Y-%m-%d %H:%M:%S")
        offset_minutes = timezone_offset_minutes(time_zone, local_dt)
        utc_timestamp = local_dt.replace(tzinfo=timezone.utc).timestamp() - (offset_minutes * 60)
        return datetime.fromtimestamp(utc_timestamp, timezone.utc).isoformat().replace("+00:00", "Z")
    except ValueError:
        return None


def timezone_offset_minutes(time_zone: str, local_dt: datetime) -> int:
    if time_zone == "America/New_York":
        return -240 if is_us_dst(local_dt) else -300
    if time_zone == "Europe/London":
        return 60 if is_europe_dst(local_dt) else 0
    if time_zone in {"Europe/Berlin", "Europe/Paris"}:
        return 120 if is_europe_dst(local_dt) else 60
    if time_zone == "Asia/Tokyo":
        return 540
    if time_zone in {"Asia/Hong_Kong", "Asia/Shanghai"}:
        return 480
    return 0


def is_us_dst(local_dt: datetime) -> bool:
    start = nth_weekday(local_dt.year, 3, 6, 2).replace(hour=2)
    end = nth_weekday(local_dt.year, 11, 6, 1).replace(hour=2)
    return start <= local_dt < end


def is_europe_dst(local_dt: datetime) -> bool:
    start = last_weekday(local_dt.year, 3, 6).replace(hour=1)
    end = last_weekday(local_dt.year, 10, 6).replace(hour=2)
    return start <= local_dt < end


def nth_weekday(year: int, month: int, weekday: int, nth: int) -> datetime:
    day = datetime(year, month, 1)
    days_until = (weekday - day.weekday()) % 7
    return day.replace(day=1 + days_until + ((nth - 1) * 7))


def last_weekday(year: int, month: int, weekday: int) -> datetime:
    if month == 12:
        day = datetime(year + 1, 1, 1)
    else:
        day = datetime(year, month + 1, 1)
    day = day.replace(day=1) - timedelta(days=1)
    return day.replace(day=day.day - ((day.weekday() - weekday) % 7))


def iso_from_epoch(value: Any) -> str | None:
    if not value:
        return None
    try:
        return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(float(value)))
    except (TypeError, ValueError):
        return None


def unavailable_index(index: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": index["name"],
        "zhName": index.get("zhName", index["name"]),
        "symbol": index["symbol"],
        "price": math.nan,
        "change": math.nan,
        "changePct": math.nan,
        "updatedAt": None,
        "timeZone": index.get("timeZone", "UTC"),
        "timeZoneLabel": index.get("timeZoneLabel", "数据源时间"),
        "detailUrl": index.get("detailUrl", ""),
        "source": "暂不可用",
        "unavailable": True,
    }


def serve_static(context: RequestContext) -> tuple[bytes, str] | None:
    path = unquote(context.path)
    if path == "/":
        path = "/index.html"
    candidate = (ROOT / path.lstrip("/")).resolve()
    if ROOT not in candidate.parents and candidate != ROOT:
        return None
    if not candidate.is_file():
        return None
    content_type = mimetypes.guess_type(candidate.name)[0] or "application/octet-stream"
    if content_type.startswith("text/") or content_type in {"application/javascript", "application/json"}:
        content_type = f"{content_type}; charset=utf-8"
    return candidate.read_bytes(), content_type


def to_jsonable(value: Any) -> Any:
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, dict):
        return {key: to_jsonable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [to_jsonable(item) for item in value]
    return value


class Handler(BaseHTTPRequestHandler):
    server_version = "FinancialAssistant/1.0"

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        context = RequestContext("GET", parsed.path, parse_qs(parsed.query), self)
        try:
            result = app.dispatch(context)
            if result is None:
                self.send_error(404, "Not found")
                return
            if isinstance(result, tuple):
                body, content_type = result
                self._send_bytes(200, body, content_type)
                return
            self._send_json(200, result)
        except (BrokenPipeError, ConnectionAbortedError, ConnectionResetError):
            return
        except Exception as exc:  # noqa: BLE001
            traceback.print_exc()
            try:
                self._send_json(500, {"ok": False, "error": str(exc)})
            except (BrokenPipeError, ConnectionAbortedError, ConnectionResetError):
                return

    def log_message(self, fmt: str, *args: Any) -> None:
        print(f"[{formatdate(time.time(), localtime=True)}] {self.address_string()} {fmt % args}")

    def _send_json(self, status: int, payload: Any) -> None:
        body = json.dumps(to_jsonable(payload), ensure_ascii=False).encode("utf-8")
        self._send_bytes(status, body, "application/json; charset=utf-8")

    def _send_bytes(self, status: int, body: bytes, content_type: str) -> None:
        try:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            if content_type.startswith(("text/html", "application/javascript", "application/json")):
                self.send_header("Cache-Control", "no-store, max-age=0")
            else:
                self.send_header("Cache-Control", "public, max-age=3600")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionAbortedError, ConnectionResetError):
            return


def main() -> None:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
    server = ThreadingHTTPServer((HOST, port), Handler)
    print(f"金融小助手已启动: http://{HOST}:{port}")
    print("按 Ctrl+C 停止服务")
    server.serve_forever()


if __name__ == "__main__":
    main()
