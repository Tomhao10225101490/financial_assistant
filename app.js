let CURRENCIES = [];
let INDEX_SYMBOLS = [];
let AUTO_REFRESH_MS = 20000;
const DEFAULT_BASE_CURRENCY = "USD";
let REQUIRED_CURRENCY_CODES = [];
const BEIJING_TIME_ZONE = "Asia/Shanghai";
const LOCAL_TIME_ZONE = Intl.DateTimeFormat().resolvedOptions().timeZone || BEIJING_TIME_ZONE;
const TREND_MODES = [
  { key: "intraday", label: "分时", chartLabel: "分时图" },
  { key: "daily", label: "日K", chartLabel: "日K线" },
  { key: "monthly", label: "月K", chartLabel: "月K线" }
];
const DEFAULT_TREND_MODE = "intraday";

const WORLD_CLOCKS = [
  { city: "北京", market: "中国", timeZone: "Asia/Shanghai", lat: 39.9042, lon: 116.4074 },
  { city: "纽约", market: "美国", timeZone: "America/New_York", lat: 40.7128, lon: -74.006 },
  { city: "伦敦", market: "英国", timeZone: "Europe/London", lat: 51.5074, lon: -0.1278 },
  { city: "法兰克福", market: "德国", timeZone: "Europe/Berlin", lat: 50.1109, lon: 8.6821 },
  { city: "东京", market: "日本", timeZone: "Asia/Tokyo", lat: 35.6762, lon: 139.6503 },
  { city: "香港", market: "中国香港", timeZone: "Asia/Hong_Kong", lat: 22.3193, lon: 114.1694 }
];

const OFFICIAL_FX_SOURCES = {
  boc: {
    label: "官方展示 · 中国银行",
    url: "https://www.boc.cn/sourcedb/whpj/"
  },
  ecb: {
    label: "官方展示 · ECB",
    url: "https://www.ecb.europa.eu/stats/eurofxref"
  },
  centralBanks: {
    USD: { label: "官方展示 · Federal Reserve", url: "https://www.federalreserve.gov/releases/h10/current/" },
    EUR: { label: "官方展示 · ECB", url: "https://www.ecb.europa.eu/stats/eurofxref" },
    JPY: { label: "官方展示 · Bank of Japan", url: "https://www.boj.or.jp/en/statistics/market/forex/fxdaily/" },
    GBP: { label: "官方展示 · Bank of England", url: "https://www.bankofengland.co.uk/boeapps/database/Rates.asp" },
    HKD: { label: "官方展示 · HKMA", url: "https://www.hkma.gov.hk/eng/market-data-and-statistics/monthly-statistical-bulletin/table/" },
    AUD: { label: "官方展示 · RBA", url: "https://www.rba.gov.au/statistics/frequency/exchange-rates.html" },
    CAD: { label: "官方展示 · Bank of Canada", url: "https://www.bankofcanada.ca/rates/exchange/" },
    CHF: { label: "官方展示 · SNB", url: "https://data.snb.ch/en/topics/ziredev/cube/devkum" },
    SGD: { label: "官方展示 · MAS", url: "https://eservices.mas.gov.sg/statistics/msb/ExchangeRates.aspx" },
    KRW: { label: "官方展示 · Bank of Korea", url: "https://www.bok.or.kr/eng/main/contents.do?menuNo=400201" },
    INR: { label: "官方展示 · Reserve Bank of India", url: "https://www.rbi.org.in/Scripts/ReferenceRateArchive.aspx" },
    CNY: { label: "官方展示 · 中国银行", url: "https://www.boc.cn/sourcedb/whpj/" }
  }
};

const ECB_SUPPORTED_CURRENCIES = new Set(["USD", "CNY", "EUR", "JPY", "GBP", "HKD", "AUD", "CAD", "CHF", "SGD", "KRW", "INR"]);

const CACHE_KEYS = {
  fx: "financialAssistant.fx.v1",
  indices: "financialAssistant.indices.v2",
  trends: "financialAssistant.trends.v2",
  baseCurrency: "financialAssistant.baseCurrency.v1",
  theme: "financialAssistant.theme.v1",
  colorMode: "financialAssistant.colorMode.v1",
  trendMode: "financialAssistant.trendMode.v1",
  briefing: "financialAssistant.briefing.v1"
};

let FALLBACK_FX = {
  base: "USD",
  timestamp: null,
  timeZone: "UTC",
  timeZoneLabel: "协调世界时",
  source: "内置参考值",
  sourceUrl: "",
  rates: {
    USD: 1,
    CNY: 7.22,
    EUR: 0.93,
    JPY: 155.5,
    GBP: 0.79,
    HKD: 7.82,
    AUD: 1.52,
    CAD: 1.37,
    CHF: 0.91,
    SGD: 1.35,
    KRW: 1365,
    INR: 83.4
  },
  stale: true
};

const state = {
  fx: null,
  indices: [],
  trends: {
    intraday: {},
    daily: {},
    monthly: {}
  },
  briefing: null,
  regionFilter: "",
  query: "",
  baseCurrency: DEFAULT_BASE_CURRENCY,
  theme: "dark",
  colorMode: "green-up",
  trendMode: DEFAULT_TREND_MODE,
  detailSymbol: null,
  detailTrendMode: DEFAULT_TREND_MODE,
  loading: false,
  trendsLoading: false,
  trendLoadingByMode: {},
  diagnostics: null,
  lastUpdatedAt: null,
  selectedClockIndex: 0
};

const elements = {
  globeStage: document.querySelector("#globeStage"),
  globeCanvas: document.querySelector("#globeCanvas"),
  globeTooltip: document.querySelector("#globeTooltip"),
  globeStatus: document.querySelector("#globeStatus"),
  worldClocks: document.querySelector("#worldClocks"),
  searchInput: document.querySelector("#searchInput"),
  themeToggle: document.querySelector("#themeToggle"),
  themeLabel: document.querySelector("#themeLabel"),
  colorModeToggle: document.querySelector("#colorModeToggle"),
  colorModeLabel: document.querySelector("#colorModeLabel"),
  trendModeButtons: document.querySelectorAll("[data-trend-mode]"),
  detailTrendModeButtons: document.querySelectorAll("[data-detail-trend-mode]"),
  refreshButton: document.querySelector("#refreshButton"),
  statusText: document.querySelector("#statusText"),
  updatedAt: document.querySelector("#updatedAt"),
  autoRefreshLabel: document.querySelector("#autoRefreshLabel"),
  baseCurrencySelect: document.querySelector("#baseCurrencySelect"),
  baseCurrencyHelp: document.querySelector("#baseCurrencyHelp"),
  marketBreadth: document.querySelector("#marketBreadth"),
  sourceLabel: document.querySelector("#sourceLabel"),
  diagnosticsLabel: document.querySelector("#diagnosticsLabel"),
  diagnosticsHelp: document.querySelector("#diagnosticsHelp"),
  fxStatus: document.querySelector("#fxStatus"),
  indexStatus: document.querySelector("#indexStatus"),
  fxGrid: document.querySelector("#fxGrid"),
  indicesBody: document.querySelector("#indicesBody"),
  indexDetail: document.querySelector("#indexDetail"),
  detailTitle: document.querySelector("#detailTitle"),
  detailMeta: document.querySelector("#detailMeta"),
  detailSource: document.querySelector("#detailSource"),
  detailClose: document.querySelector("#detailClose"),
  detailChart: document.querySelector("#detailChart"),
  chartTooltip: document.querySelector("#chartTooltip"),
  detailStats: document.querySelector("#detailStats"),
  amountInput: document.querySelector("#amountInput"),
  fromCurrency: document.querySelector("#fromCurrency"),
  toCurrency: document.querySelector("#toCurrency"),
  swapButton: document.querySelector("#swapButton"),
  converterResult: document.querySelector("#converterResult"),
  productTitle: document.querySelector("#productTitle"),
  productTagline: document.querySelector("#productTagline"),
  tickerTape: document.querySelector("#tickerTape"),
  briefingHighlights: document.querySelector("#briefingHighlights"),
  briefingHeadlines: document.querySelector("#briefingHeadlines"),
  briefingStatus: document.querySelector("#briefingStatus"),
  regionHeatmap: document.querySelector("#regionHeatmap"),
  pulseSummary: document.querySelector("#pulseSummary"),
  macroCards: document.querySelector("#macroCards"),
  commodityCards: document.querySelector("#commodityCards"),
  cryptoCards: document.querySelector("#cryptoCards"),
  watchlistBody: document.querySelector("#watchlistBody"),
  watchlistStatus: document.querySelector("#watchlistStatus"),
  fearGreedLabel: document.querySelector("#fearGreedLabel")
};

let renderFrame = null;
const globe = {
  ctx: null,
  width: 0,
  height: 0,
  dpr: 1,
  centerX: 0,
  centerY: 0,
  radius: 0,
  rotationX: -0.16,
  rotationY: -116.4 * Math.PI / 180,
  targetRotationX: null,
  targetRotationY: null,
  velocityX: 0,
  velocityY: 0,
  dragging: false,
  moved: false,
  lastX: 0,
  lastY: 0,
  hotspots: [],
  landMask: null,
  coastMask: null,
  landTextureWidth: 0,
  landTextureHeight: 0,
  landFrameCanvas: null,
  landFrameCtx: null,
  landFrameSize: 0,
  naturalEarthLoaded: false,
  naturalEarthFailed: false,
  animationFrame: null,
  paused: false,
  reducedMotion: window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches
};

function sourceLatencyBadge(item) {
  if (!item || !item.updatedAt) return '<span class="source-badge">--</span>';
  const ageMs = Date.now() - new Date(item.updatedAt).getTime();
  const seconds = Number.isFinite(ageMs) ? Math.max(0, Math.round(ageMs / 1000)) : null;
  const label = seconds === null ? "--" : seconds < 60 ? `${seconds}s` : `${Math.round(seconds / 60)}m`;
  const tone = seconds !== null && seconds <= 30 ? "ok" : seconds !== null && seconds <= 120 ? "warn" : "muted";
  const source = item.source ? escapeHtml(item.source) : "未知源";
  return `<span class="source-badge ${tone}" title="${source}">${source} · ${label}</span>`;
}

function assetGroupLabel(group) {
  const labels = {
    equity_index: "股指",
    rates: "利率",
    volatility: "波动率",
    commodities: "商品",
    crypto: "加密",
    fx: "外汇"
  };
  return labels[group] || group || "--";
}

async function fetchBriefing() {
  if (!hasBackendApi()) return null;
  try {
    const data = await fetchJson("/api/briefing", { timeout: 45000 });
    if (!data || !data.ok) throw new Error("Invalid briefing payload");
    writeCache(CACHE_KEYS.briefing, data);
    return data;
  } catch (error) {
    console.warn("Briefing API failed.", error);
    return readCache(CACHE_KEYS.briefing);
  }
}

function buildTickerItems() {
  const items = [];
  const briefing = state.briefing;
  if (briefing) {
    (briefing.indices || []).slice(0, 6).forEach((item) => {
      if (Number.isFinite(item.price)) items.push({ label: item.zhName || item.symbol, value: formatPercent(item.changePct), tone: item.change > 0 ? "up" : item.change < 0 ? "down" : "muted" });
    });
    (briefing.macro || []).slice(0, 3).forEach((item) => {
      if (Number.isFinite(item.price)) items.push({ label: item.zhName || item.symbol, value: formatNumber(item.price, 2), tone: "muted" });
    });
    (briefing.crypto || []).slice(0, 2).forEach((item) => {
      if (Number.isFinite(item.price)) items.push({ label: item.zhName || item.symbol, value: formatPercent(item.changePct), tone: item.changePct > 0 ? "up" : item.changePct < 0 ? "down" : "muted" });
    });
  }
  if (state.fx && state.fx.rates) {
    ["CNY", "EUR", "JPY"].forEach((code) => {
      if (Number.isFinite(state.fx.rates[code])) {
        items.push({ label: `${state.fx.base}/${code}`, value: formatFxRate(state.fx.rates[code]), tone: "muted" });
      }
    });
  }
  return items;
}

function renderTicker() {
  if (!elements.tickerTape) return;
  const items = buildTickerItems();
  if (!items.length) {
    elements.tickerTape.innerHTML = `<span class="ticker-item muted">正在加载全球行情带...</span>`;
    return;
  }
  const markup = items.map((item) => `
    <span class="ticker-item ${item.tone}">
      <b>${escapeHtml(item.label)}</b>
      <span>${escapeHtml(item.value)}</span>
    </span>
  `).join("");
  elements.tickerTape.innerHTML = `${markup}${markup}`;
}

function renderBriefingPanel() {
  const briefing = state.briefing;
  if (!elements.briefingHighlights) return;
  if (!briefing) {
    elements.briefingHighlights.innerHTML = `<li class="empty-state">正在生成规则简报...</li>`;
    if (elements.briefingHeadlines) elements.briefingHeadlines.innerHTML = "";
    if (elements.briefingStatus) elements.briefingStatus.textContent = "加载中";
    return;
  }
  const highlights = Array.isArray(briefing.highlights) ? briefing.highlights : [];
  elements.briefingHighlights.innerHTML = highlights.length
    ? highlights.map((line) => `<li>${escapeHtml(line)}</li>`).join("")
    : `<li class="empty-state">暂无要点</li>`;
  if (elements.briefingHeadlines) {
    const headlines = Array.isArray(briefing.headlines) ? briefing.headlines : [];
    elements.briefingHeadlines.innerHTML = headlines.length
      ? headlines.slice(0, 6).map((item) => {
          const title = escapeHtml(item.title || "");
          const url = item.url ? `<a href="${escapeHtml(item.url)}" target="_blank" rel="noopener noreferrer">${title}</a>` : `<span>${title}</span>`;
          return `<article class="headline-card">${url}<small>${escapeHtml(item.source || "News")}</small></article>`;
        }).join("")
      : `<div class="empty-state">暂无快讯标题</div>`;
  }
  if (elements.briefingStatus) {
    elements.briefingStatus.textContent = highlights.length ? "规则引擎" : "部分可用";
    elements.briefingStatus.className = `pill ${highlights.length ? "ok" : "warn"}`;
  }
}

function renderRegionHeatmap() {
  if (!elements.regionHeatmap) return;
  const regions = state.briefing?.marketPulse?.regions || [];
  if (!regions.length) {
    elements.regionHeatmap.innerHTML = `<div class="empty-state">区域数据加载中...</div>`;
    if (elements.pulseSummary) elements.pulseSummary.textContent = "--";
    return;
  }
  elements.regionHeatmap.innerHTML = regions.map((region) => {
    const total = region.total || 0;
    const up = region.up || 0;
    const down = region.down || 0;
    const ratio = total ? (up - down) / total : 0;
    const tone = ratio > 0.2 ? "up" : ratio < -0.2 ? "down" : "muted";
    const active = state.regionFilter === region.id ? "active" : "";
    return `
      <button type="button" class="region-card ${tone} ${active}" data-region-filter="${escapeHtml(region.id)}" aria-pressed="${active ? "true" : "false"}">
        <strong>${escapeHtml(region.label || region.id)}</strong>
        <span>${up} 涨 / ${down} 跌</span>
        <small>${total} 指数</small>
      </button>
    `;
  }).join("");
  const pulse = state.briefing.marketPulse;
  if (elements.pulseSummary) {
    elements.pulseSummary.textContent = pulse ? `${pulse.up} 涨 / ${pulse.down} 跌` : "--";
    elements.pulseSummary.className = "pill ok";
  }
}

function renderQuoteCards(container, rows, emptyText) {
  if (!container) return;
  if (!rows || !rows.length) {
    container.innerHTML = `<div class="empty-state">${escapeHtml(emptyText)}</div>`;
    return;
  }
  container.innerHTML = rows.map((item) => {
    const tone = item.change > 0 ? "up" : item.change < 0 ? "down" : "muted";
    return `
      <article class="quote-card ${tone}">
        <header>
          <strong>${escapeHtml(item.zhName || item.name || item.symbol)}</strong>
          <span>${escapeHtml(item.symbol || "")}</span>
        </header>
        <div class="quote-value">${Number.isFinite(item.price) ? formatNumber(item.price, item.price > 100 ? 2 : 4) : "--"}</div>
        <footer>
          <span class="${tone}">${Number.isFinite(item.changePct) ? formatPercent(item.changePct) : signedNumber(item.change)}</span>
          ${sourceLatencyBadge(item)}
        </footer>
      </article>
    `;
  }).join("");
}

function renderMacroPanels() {
  const briefing = state.briefing;
  renderQuoteCards(elements.macroCards, briefing?.macro || [], "宏观数据加载中...");
  renderQuoteCards(elements.commodityCards, briefing?.commodities || [], "商品数据加载中...");
  const cryptoRows = [...(briefing?.crypto || [])];
  if (briefing?.fearGreed && Number.isFinite(briefing.fearGreed.value)) {
    cryptoRows.push({
      symbol: "FNG",
      zhName: "恐惧贪婪",
      name: "Fear & Greed",
      price: briefing.fearGreed.value,
      changePct: NaN,
      source: briefing.fearGreed.source,
      updatedAt: briefing.fearGreed.updatedAt
    });
  }
  renderQuoteCards(elements.cryptoCards, cryptoRows, "加密数据加载中...");
  if (elements.fearGreedLabel) {
    const fear = briefing?.fearGreed;
    elements.fearGreedLabel.textContent = fear && Number.isFinite(fear.value)
      ? `${Math.round(fear.value)} · ${fear.label || "情绪指数"}`
      : "--";
  }
}

function watchlistRows() {
  const rows = [];
  const briefing = state.briefing;
  if (briefing) {
    rows.push(...(briefing.macro || []).map((item) => ({ ...item, group: item.group || "rates" })));
    rows.push(...(briefing.commodities || []).map((item) => ({ ...item, group: item.group || "commodities" })));
    rows.push(...(briefing.crypto || []).map((item) => ({ ...item, group: item.group || "crypto" })));
  }
  rows.push(...state.indices.map((item) => ({ ...item, group: "equity_index" })));
  const query = state.query.trim().toLowerCase();
  return rows.filter((item) => {
    if (state.regionFilter && item.region && item.region !== state.regionFilter) return false;
    if (!query) return true;
    return `${item.zhName || ""} ${item.name || ""} ${item.symbol || ""} ${item.group || ""}`.toLowerCase().includes(query);
  });
}

function renderWatchlist() {
  if (!elements.watchlistBody) return;
  const rows = watchlistRows();
  elements.watchlistBody.innerHTML = rows.length
    ? rows.map((item) => {
        const tone = item.change > 0 ? "up" : item.change < 0 ? "down" : "muted";
        const clickable = item.group === "equity_index" && item.symbol
          ? `class="index-row" data-index-symbol="${escapeHtml(item.symbol)}" tabindex="0"`
          : "";
        return `
          <tr ${clickable}>
            <td><span class="index-zh">${escapeHtml(item.zhName || item.name || item.symbol)}</span><span class="index-en">${escapeHtml(item.symbol || "")}</span></td>
            <td>${escapeHtml(assetGroupLabel(item.group))}</td>
            <td>${Number.isFinite(item.price) ? formatNumber(item.price, 2) : "--"}</td>
            <td class="${tone}">${Number.isFinite(item.change) ? signedNumber(item.change) : "--"}</td>
            <td class="${tone}">${Number.isFinite(item.changePct) ? formatPercent(item.changePct) : "--"}</td>
            <td>${escapeHtml(item.source || "--")}</td>
            <td>${sourceLatencyBadge(item)}</td>
          </tr>
        `;
      }).join("")
    : `<tr><td colspan="7" class="empty-state">没有匹配的观察项</td></tr>`;
  if (elements.watchlistStatus) {
    elements.watchlistStatus.textContent = `${rows.length} 项`;
    elements.watchlistStatus.className = "pill ok";
  }
}

function renderTerminal() {
  renderTicker();
  renderBriefingPanel();
  renderRegionHeatmap();
  renderMacroPanels();
  renderWatchlist();
}

function formatNumber(value, maximumFractionDigits = 4) {
  if (!Number.isFinite(value)) return "--";
  return new Intl.NumberFormat("zh-CN", {
    maximumFractionDigits,
    minimumFractionDigits: value > 1000 ? 0 : 2
  }).format(value);
}

function formatPreciseNumber(value, maximumFractionDigits = 12) {
  if (!Number.isFinite(value)) return "--";
  const normalized = Number.parseFloat(Number(value).toPrecision(15));
  return new Intl.NumberFormat("zh-CN", {
    maximumFractionDigits,
    minimumFractionDigits: 0
  }).format(normalized);
}

function formatFxRate(value) {
  return formatPreciseNumber(value, 10);
}

function formatPercent(value) {
  if (!Number.isFinite(value)) return "--";
  const sign = value > 0 ? "+" : "";
  return `${sign}${value.toFixed(2)}%`;
}

function qualityLabel(quality, cacheState) {
  const key = quality || cacheState || "real";
  return {
    real: "真实",
    delayed: "延迟",
    cache: "缓存",
    stale: "缓存",
    fallback: "兜底",
    unavailable: "不可用",
    live: "实时"
  }[key] || key;
}

function qualityLabelText(quality) {
  const label = qualityLabel(quality, quality);
  return label === "真实" ? "真实" : `${label}·`;
}

function qualityTone(quality, cacheState) {
  const key = quality || cacheState || "real";
  if (key === "real" || key === "live") return "ok";
  if (key === "delayed" || key === "cache" || key === "stale" || key === "fallback") return "warn";
  return "muted";
}

function latencyLabel(value) {
  return Number.isFinite(value) ? `${Math.max(0, Math.round(value))}ms` : "--";
}

function trendModeMeta(mode = state.trendMode) {
  return TREND_MODES.find((item) => item.key === mode) || TREND_MODES[0];
}

function normalizeTrendMode(mode) {
  return TREND_MODES.some((item) => item.key === mode) ? mode : DEFAULT_TREND_MODE;
}

function trendModeLabel(mode) {
  return trendModeMeta(mode).label;
}

function formatTimeInZone(value, timeZone, options = {}) {
  if (!value) return "--";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "--";
  return new Intl.DateTimeFormat("zh-CN", {
    timeZone,
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: options.withSeconds ? "2-digit" : undefined,
    hour12: false
  }).format(date);
}

function formatDualTime(value, timeZone = "UTC", timeZoneLabel = "数据源时间") {
  if (!value) return "--";
  const sourceTime = formatTimeInZone(value, timeZone, { withSeconds: true });
  const beijingTime = formatTimeInZone(value, BEIJING_TIME_ZONE, { withSeconds: true });
  if (sourceTime === "--" || beijingTime === "--") return "--";
  if (timeZone === BEIJING_TIME_ZONE) return `${timeZoneLabel} ${sourceTime}`;
  return `${timeZoneLabel} ${sourceTime} / 北京时间 ${beijingTime}`;
}

function formatDualTimeCell(value, timeZone = "UTC", timeZoneLabel = "数据源时间") {
  if (!value) return "--";
  const sourceTime = formatTimeInZone(value, timeZone, { withSeconds: true });
  const beijingTime = formatTimeInZone(value, BEIJING_TIME_ZONE, { withSeconds: true });
  if (sourceTime === "--" || beijingTime === "--") return "--";
  return `
    <span class="time-cell">
      <span>${timeZoneLabel} ${sourceTime}</span>
      <span>北京时间 ${beijingTime}</span>
    </span>
  `;
}

function formatClockTime(timeZone) {
  return new Intl.DateTimeFormat("zh-CN", {
    timeZone,
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false
  }).format(new Date());
}

function formatClockDate(timeZone) {
  return new Intl.DateTimeFormat("zh-CN", {
    timeZone,
    month: "2-digit",
    day: "2-digit",
    weekday: "short"
  }).format(new Date());
}

function formatClockFull(clock) {
  return `${clock.city} · ${clock.market}\n${formatClockTime(clock.timeZone)}\n${formatClockDate(clock.timeZone)} · ${clock.timeZone}`;
}

function localTimeZoneLabel() {
  return LOCAL_TIME_ZONE === BEIJING_TIME_ZONE ? "北京时间" : "本地时间";
}

function readCache(key) {
  try {
    const raw = localStorage.getItem(key);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

function writeCache(key, value) {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch {
    // Private browsing or full storage should not break the dashboard.
  }
}

function applyTheme() {
  document.documentElement.dataset.theme = state.theme;
  document.documentElement.style.colorScheme = state.theme;
  if (elements.themeLabel) {
    elements.themeLabel.textContent = state.theme === "dark" ? "浅色" : "暗色";
  }
  if (elements.themeToggle) {
    elements.themeToggle.setAttribute(
      "aria-label",
      state.theme === "dark" ? "切换到浅色模式" : "切换到暗色模式"
    );
  }
}

function applyColorMode() {
  document.documentElement.dataset.colorMode = state.colorMode;
  if (elements.colorModeLabel) {
    elements.colorModeLabel.textContent = state.colorMode === "red-up" ? "红涨绿跌" : "绿涨红跌";
  }
  if (elements.colorModeToggle) {
    elements.colorModeToggle.setAttribute(
      "aria-label",
      state.colorMode === "red-up" ? "切换到绿涨红跌" : "切换到红涨绿跌"
    );
  }
}

function toggleTheme() {
  state.theme = state.theme === "dark" ? "light" : "dark";
  writeCache(CACHE_KEYS.theme, state.theme);
  applyTheme();
}

function toggleColorMode() {
  state.colorMode = state.colorMode === "red-up" ? "green-up" : "red-up";
  writeCache(CACHE_KEYS.colorMode, state.colorMode);
  applyColorMode();
  scheduleRender();
}

function scheduleRender() {
  if (renderFrame) return;
  renderFrame = requestAnimationFrame(() => {
    renderFrame = null;
    renderAll();
  });
}

function runViewTransition(callback) {
  if (document.startViewTransition) {
    document.startViewTransition(callback);
    return;
  }
  callback();
}

function hasBackendApi() {
  return location.protocol === "http:" || location.protocol === "https:";
}

async function fetchJson(url, options = {}) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), options.timeout || 8500);
  try {
    const response = await fetch(url, {
      cache: "no-store",
      signal: controller.signal
    });
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    return await response.json();
  } finally {
    clearTimeout(timeout);
  }
}

async function fetchText(url, options = {}) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), options.timeout || 8500);
  try {
    const response = await fetch(url, {
      cache: "no-store",
      signal: controller.signal
    });
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    return await response.text();
  } finally {
    clearTimeout(timeout);
  }
}

async function fetchFxRates(base = "USD") {
  const normalizedBase = base.toUpperCase();
  const symbols = REQUIRED_CURRENCY_CODES.filter((code) => code !== normalizedBase).join(",");
  const baseLower = normalizedBase.toLowerCase();

  if (hasBackendApi()) {
    try {
      const data = await fetchJson(`/api/fx?base=${encodeURIComponent(normalizedBase)}`, { timeout: 12000 });
      if (!data || !data.ok || !data.rates) {
        throw new Error("Invalid local FX API payload");
      }
      const parsed = {
        base: (data.base || normalizedBase).toUpperCase(),
        timestamp: data.timestamp || null,
        timeZone: data.timeZone || "UTC",
        timeZoneLabel: data.timeZoneLabel || "协调世界时",
        source: data.source || "本地 Python API",
        sourceUrl: data.sourceUrl || sourceUrlForFx(data.source),
        rates: normalizeRates(data.rates),
        stale: Boolean(data.stale),
        cacheState: data.cacheState || (data.stale ? "stale" : "live"),
        quality: data.quality || (data.stale ? "cache" : "real"),
        latencyMs: finiteNumber(data.latencyMs),
        cacheAgeSeconds: finiteNumber(data.cacheAgeSeconds),
        officialSourceUrl: data.officialSourceUrl || data.sourceUrl || sourceUrlForFx(data.source),
        beijingUpdatedAt: data.beijingUpdatedAt || null,
        errors: Array.isArray(data.errors) ? data.errors : []
      };
      if (!hasRequiredRates(parsed.rates)) {
        throw new Error("Local FX API is missing required currencies");
      }
      writeCache(CACHE_KEYS.fx, parsed);
      return parsed;
    } catch (error) {
      console.warn("Local FX API failed, trying browser fallback.", error);
    }
  }

  const endpoints = [
    {
      source: "Frankfurter",
      url: `https://api.frankfurter.dev/v1/latest?base=${normalizedBase}&symbols=${symbols}`,
      parse(data) {
        if (!data || !data.rates) throw new Error("Invalid Frankfurter payload");
        return {
          base: (data.base || normalizedBase).toUpperCase(),
          timestamp: data.date ? `${data.date}T00:00:00Z` : null,
          timeZone: "UTC",
          timeZoneLabel: "协调世界时",
          source: "Frankfurter",
          sourceUrl: "https://frankfurter.dev/",
          rates: normalizeRates({ ...data.rates, [normalizedBase]: 1 })
        };
      }
    },
    {
      source: "Currency API CDN",
      url: `https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/${baseLower}.json`,
      parse(data) {
        const rates = data && data[baseLower];
        if (!rates) throw new Error("Invalid Currency API CDN payload");
        return {
          base: normalizedBase,
          timestamp: data.date ? `${data.date}T00:00:00Z` : null,
          timeZone: "UTC",
          timeZoneLabel: "协调世界时",
          source: "Currency API CDN",
          sourceUrl: "https://github.com/fawazahmed0/exchange-api",
          rates: normalizeRates({ ...rates, [baseLower]: 1 })
        };
      }
    },
    {
      source: "Currency API Cloudflare",
      url: `https://latest.currency-api.pages.dev/v1/currencies/${baseLower}.json`,
      parse(data) {
        const rates = data && data[baseLower];
        if (!rates) throw new Error("Invalid Currency API Cloudflare payload");
        return {
          base: normalizedBase,
          timestamp: data.date ? `${data.date}T00:00:00Z` : null,
          timeZone: "UTC",
          timeZoneLabel: "协调世界时",
          source: "Currency API Cloudflare",
          sourceUrl: "https://github.com/fawazahmed0/exchange-api",
          rates: normalizeRates({ ...rates, [baseLower]: 1 })
        };
      }
    }
  ];

  for (const endpoint of endpoints) {
    try {
      const data = await fetchJson(endpoint.url);
      const parsed = endpoint.parse(data);
      if (!hasRequiredRates(parsed.rates)) {
        throw new Error("FX source is missing required currencies");
      }
      writeCache(CACHE_KEYS.fx, parsed);
      return parsed;
    } catch (error) {
      console.warn(`FX source failed: ${endpoint.source}`, error);
    }
  }

  const cached = readCache(CACHE_KEYS.fx);
  if (cached) {
    return {
      ...rebaseFxSnapshot(cached, normalizedBase),
      stale: true,
      source: `${cached.source} 缓存`
    };
  }
  return rebaseFxSnapshot(FALLBACK_FX, normalizedBase);
}

function sourceUrlForFx(source = "") {
  if (source.includes("Frankfurter")) return OFFICIAL_FX_SOURCES.ecb.url;
  if (source.includes("Currency API")) return OFFICIAL_FX_SOURCES.ecb.url;
  return "";
}

function officialFxLink(base, target) {
  const normalizedBase = String(base || DEFAULT_BASE_CURRENCY).toUpperCase();
  const normalizedTarget = String(target || DEFAULT_BASE_CURRENCY).toUpperCase();
  if (normalizedBase === "CNY" || normalizedTarget === "CNY") {
    return OFFICIAL_FX_SOURCES.boc;
  }
  if (ECB_SUPPORTED_CURRENCIES.has(normalizedBase) && ECB_SUPPORTED_CURRENCIES.has(normalizedTarget)) {
    return OFFICIAL_FX_SOURCES.ecb;
  }
  return OFFICIAL_FX_SOURCES.centralBanks[normalizedTarget] ||
    OFFICIAL_FX_SOURCES.centralBanks[normalizedBase] ||
    OFFICIAL_FX_SOURCES.ecb;
}

function normalizeRates(rates) {
  return Object.fromEntries(
    Object.entries(rates).map(([code, rate]) => [code.toUpperCase(), Number(rate)])
  );
}

function hasRequiredRates(rates) {
  return REQUIRED_CURRENCY_CODES.every((code) => Number.isFinite(rates[code]));
}

function rebaseFxSnapshot(snapshot, targetBase) {
  const targetRate = snapshot.rates[targetBase];
  if (!Number.isFinite(targetRate) || targetRate === 0) return snapshot;
  const rates = Object.fromEntries(
    Object.entries(snapshot.rates).map(([code, rate]) => [code, Number(rate) / targetRate])
  );
  rates[targetBase] = 1;
  return {
    ...snapshot,
    base: targetBase,
    rates
  };
}

async function fetchIndices() {
  if (hasBackendApi()) {
    try {
      const data = await fetchJson("/api/indices", { timeout: 60000 });
      if (!data || !data.ok || !Array.isArray(data.indices)) {
        throw new Error("Invalid local index API payload");
      }
      const rows = data.indices.map(normalizeIndexRow);
      if (!rows.some((row) => Number.isFinite(row.price))) {
        throw new Error("Local index API returned no live rows");
      }
      writeCache(CACHE_KEYS.indices, rows);
      return rows;
    } catch (error) {
      console.warn("Local index API failed, trying browser fallback.", error);
    }
  }

  let data = [];
  try {
    data = await fetchStooqIndices();
  } catch (error) {
    console.warn("Index source failed: Stooq batch", error);
    data = INDEX_SYMBOLS.map((index) => unavailableIndex(index, error));
  }

  if (data.some((item) => item.unavailable)) {
    try {
      const yahooRows = await fetchYahooIndices();
      data = data.map((item) => {
        if (!item.unavailable) return item;
        return yahooRows.find((row) => row.symbol === item.symbol) || item;
      });
    } catch (error) {
      console.warn("Index source failed: Yahoo Finance fallback", error);
    }
  }

  const hasLiveRows = data.some((item) => Number.isFinite(item.price));
  if (hasLiveRows) {
    writeCache(CACHE_KEYS.indices, data);
    return data;
  }

  const cached = readCache(CACHE_KEYS.indices);
  if (cached) {
    return cached.map((item) => ({ ...item, stale: true, source: `${item.source} 缓存` }));
  }

  return data;
}

async function fetchTrends(mode = state.trendMode) {
  const trendMode = normalizeTrendMode(mode);
  if (hasBackendApi()) {
    try {
      const data = await fetchJson(`/api/trends?mode=${encodeURIComponent(trendMode)}`, { timeout: 20000 });
      if (!data || !data.ok || !Array.isArray(data.trends)) {
        throw new Error("Invalid local trends API payload");
      }
      const trends = normalizeTrends(data.trends, data.mode || trendMode);
      const cached = readCache(CACHE_KEYS.trends) || {};
      writeCache(CACHE_KEYS.trends, { ...cached, [trendMode]: trends });
      return trends;
    } catch (error) {
      console.warn("Local trend API failed.", error);
    }
  }

  const cached = readCache(CACHE_KEYS.trends);
  return cached && typeof cached === "object" && cached[trendMode] ? cached[trendMode] : {};
}

async function fetchDiagnostics() {
  if (!hasBackendApi()) return null;
  try {
    const data = await fetchJson("/api/diagnostics", { timeout: 6000 });
    return data && data.ok ? data : null;
  } catch (error) {
    console.warn("Diagnostics API failed.", error);
    return null;
  }
}

function normalizeTrends(rows, fallbackMode = state.trendMode) {
  return Object.fromEntries(rows.map((row) => [
    row.symbol,
    {
      symbol: row.symbol,
      mode: normalizeTrendMode(row.mode || fallbackMode),
      source: row.source || "趋势数据",
      sourceUrl: row.sourceUrl || "",
      updatedAt: row.updatedAt || null,
      timeZone: row.timeZone || (INDEX_SYMBOLS.find((item) => item.symbol === row.symbol) || {}).timeZone || "UTC",
      timeZoneLabel: row.timeZoneLabel || (INDEX_SYMBOLS.find((item) => item.symbol === row.symbol) || {}).timeZoneLabel || "数据源时间",
      quality: row.quality || (row.derived ? "fallback" : "real"),
      fallbackReason: row.fallbackReason || "",
      derived: Boolean(row.derived),
      cacheState: row.cacheState || "live",
      latencyMs: finiteNumber(row.latencyMs),
      cacheAgeSeconds: finiteNumber(row.cacheAgeSeconds),
      marketTimeZone: row.marketTimeZone || row.timeZone || "",
      beijingUpdatedAt: row.beijingUpdatedAt || null,
      points: Array.isArray(row.points)
        ? row.points
            .map((point) => ({
              time: point.time || "",
              value: finiteNumber(point.value),
              open: finiteNumber(point.open),
              high: finiteNumber(point.high),
              low: finiteNumber(point.low),
              close: finiteNumber(point.close)
            }))
            .filter((point) => Number.isFinite(point.value))
        : []
    }
  ]));
}

function normalizeIndexRow(row) {
  const meta = INDEX_SYMBOLS.find((item) => item.symbol === row.symbol) || {};
  return {
    name: meta.name || row.name,
    zhName: meta.zhName || row.zhName || row.name || meta.name,
    symbol: row.symbol || meta.symbol,
    price: finiteNumber(row.price),
    change: finiteNumber(row.change),
    changePct: finiteNumber(row.changePct),
    previousClose: finiteNumber(row.previousClose),
    updatedAt: row.updatedAt || null,
    timeZone: row.timeZone || meta.timeZone || "UTC",
    timeZoneLabel: row.timeZoneLabel || meta.timeZoneLabel || "数据源时间",
    detailUrl: row.detailUrl || meta.detailUrl || "",
    sourceDetailUrl: row.sourceDetailUrl || row.detailUrl || meta.detailUrl || "",
    source: row.source || "本地 Python API",
    unavailable: Boolean(row.unavailable),
    stale: Boolean(row.stale),
    quality: row.quality || (row.unavailable ? "unavailable" : row.stale ? "cache" : "real"),
    cacheState: row.cacheState || (row.stale ? "stale" : "live"),
    latencyMs: finiteNumber(row.latencyMs),
    cacheAgeSeconds: finiteNumber(row.cacheAgeSeconds),
    beijingUpdatedAt: row.beijingUpdatedAt || null
  };
}

function finiteNumber(value) {
  if (value === null || value === undefined || value === "") return NaN;
  const number = Number(value);
  return Number.isFinite(number) ? number : NaN;
}

async function fetchYahooIndices() {
  const rows = await Promise.allSettled(INDEX_SYMBOLS.map(fetchYahooChartIndex));
  const data = rows
    .filter((result) => result.status === "fulfilled")
    .map((result) => result.value)
    .filter((row) => Number.isFinite(row.price));

  if (!data.length) throw new Error("Empty Yahoo Finance Chart payload");
  return data;
}

async function fetchYahooChartIndex(index) {
  const url = `https://query1.finance.yahoo.com/v8/finance/chart/${encodeURIComponent(index.symbol)}?range=5d&interval=1d`;
  const data = await fetchYahooJson(url);
  const result = data && data.chart && Array.isArray(data.chart.result)
    ? data.chart.result[0]
    : null;
  if (!result || !result.meta) throw new Error("Invalid Yahoo Finance Chart payload");

  const quote = result.indicators && result.indicators.quote && result.indicators.quote[0];
  const closes = quote && Array.isArray(quote.close) ? quote.close.filter(Number.isFinite) : [];
  const price = Number(result.meta.regularMarketPrice || closes[closes.length - 1]);
  const previous = Number(
    result.meta.chartPreviousClose ||
    result.meta.previousClose ||
    closes[closes.length - 2]
  );
  const change = Number.isFinite(price) && Number.isFinite(previous) ? price - previous : NaN;
  const changePct = Number.isFinite(change) && Number.isFinite(previous) && previous !== 0
    ? (change / previous) * 100
    : NaN;

  return {
    name: index.name,
    zhName: index.zhName,
    symbol: index.symbol,
    price,
    change,
    changePct,
    updatedAt: result.meta.regularMarketTime
      ? new Date(Number(result.meta.regularMarketTime) * 1000).toISOString()
      : null,
    timeZone: index.timeZone,
    timeZoneLabel: index.timeZoneLabel,
    detailUrl: index.detailUrl,
    source: "Yahoo Finance Chart"
  };
}

async function fetchYahooJson(url) {
  try {
    return await fetchJson(url, { timeout: 10000 });
  } catch (error) {
    console.warn("Direct Yahoo Finance request failed, trying proxy fallback.", error);
  }

  const proxiedUrl = `https://api.allorigins.win/raw?url=${encodeURIComponent(url)}`;
  return fetchJson(proxiedUrl, { timeout: 12000 });
}

async function fetchStooqIndices() {
  const aliases = INDEX_SYMBOLS.flatMap((index) => index.stooq);
  const url = `https://stooq.com/q/l/?s=${encodeURIComponent(aliases.join(","))}&f=sd2t2ohlcpn&e=csv`;
  const csv = await fetchIndexCsv(url);
  const rows = parseStooqRows(csv);
  if (!rows.length) throw new Error("Empty Stooq payload");

  return INDEX_SYMBOLS.map((index) => {
    const row = index.stooq
      .map((alias) => rows.find((item) => item.symbolKey === alias.toLowerCase()))
      .find(Boolean);
    return row ? mapStooqRow(index, row) : unavailableIndex(index, new Error("Index quote unavailable"));
  });
}

async function fetchIndexCsv(url) {
  try {
    return await fetchText(url);
  } catch (error) {
    console.warn("Direct Stooq request failed, trying reader/proxy fallbacks.", error);
  }

  const fallbacks = [
    `https://r.jina.ai/${url}`,
    `https://api.allorigins.win/raw?url=${encodeURIComponent(url)}`
  ];

  for (const fallbackUrl of fallbacks) {
    try {
      return await fetchText(fallbackUrl, { timeout: 10000 });
    } catch (fallbackError) {
      console.warn("Index fallback failed.", fallbackError);
    }
  }

  throw new Error("All index endpoints failed");
}

function parseStooqRows(csv) {
  const lines = csv
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean);
  const headerIndex = lines.findIndex((line) => line.toLowerCase().startsWith("symbol,"));
  if (headerIndex === -1) return [];

  const headers = parseCsvLine(lines[headerIndex]).map(normalizeHeader);
  return lines.slice(headerIndex + 1).map((line) => {
    const cells = parseCsvLine(line);
    const row = Object.fromEntries(headers.map((header, i) => [header, cells[i]]));
    return {
      ...row,
      symbolKey: String(row.symbol || "").toLowerCase()
    };
  });
}

function normalizeHeader(header) {
  return header.toLowerCase().replace(/%/g, "percent").replace(/\s/g, "");
}

function mapStooqRow(index, row) {
  const close = parseMarketNumber(row.close || row.last || row.lastprice);
  const open = parseMarketNumber(row.open);
  const previous = parseMarketNumber(row.previousclose || row.previous || row.prevclose);
  const rawChange = parseMarketNumber(row.change || row.chg || row.c1);
  const rawChangePct = parseMarketNumber(row.changepercent || row.changepct || row.p2);
  const basis = Number.isFinite(previous) && previous !== 0 ? previous : open;
  const fallbackChange = Number.isFinite(basis) && Number.isFinite(close) ? close - basis : NaN;
  const change = Number.isFinite(rawChange) ? rawChange : fallbackChange;
  const changePct = Number.isFinite(rawChangePct)
    ? rawChangePct
    : Number.isFinite(basis) && basis !== 0
      ? (change / basis) * 100
      : NaN;

  if (!Number.isFinite(close)) {
    return unavailableIndex(index, new Error("Index quote unavailable"));
  }

  return {
    name: index.name,
    zhName: index.zhName,
    symbol: index.symbol,
    price: close,
    change,
    changePct,
    previousClose: Number.isFinite(previous) ? previous : null,
    updatedAt: parseStooqTime(row.date, row.time, index.timeZone),
    timeZone: index.timeZone,
    timeZoneLabel: index.timeZoneLabel,
    detailUrl: index.detailUrl,
    source: "Stooq"
  };
}

function parseMarketNumber(value) {
  if (value === undefined || value === null || value === "" || value === "N/D") return NaN;
  return Number(String(value).replace(/[%+\s,]/g, ""));
}

function parseCsvLine(line) {
  const values = [];
  let current = "";
  let quoted = false;

  for (let i = 0; i < line.length; i += 1) {
    const char = line[i];
    if (char === "\"") {
      quoted = !quoted;
    } else if (char === "," && !quoted) {
      values.push(current);
      current = "";
    } else {
      current += char;
    }
  }
  values.push(current);
  return values.map((value) => value.trim());
}

function parseStooqTime(date, time, timeZone = "UTC") {
  if (!date || date === "N/D") return null;
  const safeTime = time && time !== "N/D" ? time : "00:00:00";
  const match = `${date} ${safeTime}`.match(/^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})$/);
  if (!match) return null;
  const [, year, month, day, hour, minute, second] = match.map(Number);
  return zonedTimeToUtc(year, month, day, hour, minute, second, timeZone);
}

function zonedTimeToUtc(year, month, day, hour, minute, second, timeZone) {
  const utcGuess = new Date(Date.UTC(year, month - 1, day, hour, minute, second));
  const offset = getTimeZoneOffset(utcGuess, timeZone);
  return new Date(utcGuess.getTime() - offset).toISOString();
}

function getTimeZoneOffset(date, timeZone) {
  const parts = new Intl.DateTimeFormat("en-US", {
    timeZone,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hourCycle: "h23"
  }).formatToParts(date);
  const values = Object.fromEntries(parts.map((part) => [part.type, Number(part.value)]));
  const zonedAsUtc = Date.UTC(values.year, values.month - 1, values.day, values.hour, values.minute, values.second);
  return zonedAsUtc - date.getTime();
}

function unavailableIndex(index, error) {
  console.warn(`Index source failed: ${index.name}`, error);
  return {
    name: index.name,
    zhName: index.zhName,
    symbol: index.symbol,
    price: NaN,
    change: NaN,
    changePct: NaN,
    updatedAt: null,
    timeZone: index.timeZone || "UTC",
    timeZoneLabel: index.timeZoneLabel || "数据源时间",
    detailUrl: index.detailUrl || "",
    source: "暂不可用",
    unavailable: true
  };
}

function populateCurrencySelects() {
  const options = CURRENCIES.map(
    (currency) => `<option value="${currency.code}">${currency.code} · ${currency.name}</option>`
  ).join("");
  elements.baseCurrencySelect.innerHTML = options;
  elements.fromCurrency.innerHTML = options;
  elements.toCurrency.innerHTML = options;
  elements.baseCurrencySelect.value = state.baseCurrency;
  elements.fromCurrency.value = state.baseCurrency;
  elements.toCurrency.value = "CNY";
  if (elements.toCurrency.value === state.baseCurrency) {
    elements.toCurrency.value = "USD";
  }
}

function renderWorldClocks() {
  if (!elements.worldClocks.children.length) {
    elements.worldClocks.innerHTML = WORLD_CLOCKS.map((clock, index) => `
      <article class="clock-card ${index === state.selectedClockIndex ? "active" : ""}" data-clock-index="${index}" tabindex="0" aria-label="选中 ${clock.city} 时钟" aria-pressed="${index === state.selectedClockIndex}">
        <span class="clock-city">${clock.city}</span>
        <strong class="clock-time">${formatClockTime(clock.timeZone)}</strong>
        <small class="clock-date">${clock.market} · ${formatClockDate(clock.timeZone)}</small>
      </article>
    `).join("");
  }

  WORLD_CLOCKS.forEach((clock, index) => {
    const card = elements.worldClocks.querySelector(`[data-clock-index="${index}"]`);
    if (!card) return;
    card.classList.toggle("active", index === state.selectedClockIndex);
    card.setAttribute("aria-pressed", String(index === state.selectedClockIndex));
    const timeNode = card.querySelector(".clock-time");
    const dateNode = card.querySelector(".clock-date");
    const nextTime = formatClockTime(clock.timeZone);
    if (timeNode && timeNode.textContent !== nextTime) {
      timeNode.textContent = nextTime;
      timeNode.classList.remove("tick");
      void timeNode.offsetWidth;
      timeNode.classList.add("tick");
    }
    if (dateNode) {
      dateNode.textContent = `${clock.market} · ${formatClockDate(clock.timeZone)}`;
    }
  });
  updateGlobeTooltip();
}

function initGlobe() {
  if (!elements.globeCanvas || !elements.globeStage) return;
  const context = elements.globeCanvas.getContext("2d");
  if (!context) {
    setGlobeStatus("时钟卡片模式", "warn");
    return;
  }
  globe.ctx = context;
  resizeGlobe();
  loadNaturalEarthLand();
  window.addEventListener("resize", resizeGlobe);
  document.addEventListener("visibilitychange", () => {
    globe.paused = document.hidden;
    if (!globe.paused) animateGlobe();
  });
  elements.globeCanvas.addEventListener("pointerdown", handleGlobePointerDown);
  elements.globeCanvas.addEventListener("pointermove", handleGlobePointerMove);
  elements.globeCanvas.addEventListener("pointerup", handleGlobePointerUp);
  elements.globeCanvas.addEventListener("pointercancel", handleGlobePointerUp);
  elements.globeCanvas.addEventListener("pointerleave", handleGlobePointerUp);
  if (state.selectedClockIndex !== null) focusGlobeOnClock(state.selectedClockIndex, false);
  animateGlobe();
}

function setGlobeStatus(text, tone = "ok") {
  if (!elements.globeStatus) return;
  elements.globeStatus.textContent = text;
  elements.globeStatus.className = `pill ${tone}`;
}

function resizeGlobe() {
  if (!elements.globeCanvas || !elements.globeStage || !globe.ctx) return;
  const rect = elements.globeStage.getBoundingClientRect();
  globe.dpr = Math.min(window.devicePixelRatio || 1, 2);
  globe.width = Math.max(320, Math.floor(rect.width));
  globe.height = Math.max(260, Math.floor(rect.height));
  elements.globeCanvas.width = Math.floor(globe.width * globe.dpr);
  elements.globeCanvas.height = Math.floor(globe.height * globe.dpr);
  elements.globeCanvas.style.width = `${globe.width}px`;
  elements.globeCanvas.style.height = `${globe.height}px`;
  globe.ctx.setTransform(globe.dpr, 0, 0, globe.dpr, 0, 0);
  globe.centerX = globe.width / 2;
  globe.centerY = globe.height / 2;
  globe.radius = Math.min(globe.width, globe.height) * 0.35;
  drawGlobe();
}

function animateGlobe() {
  if (globe.animationFrame || globe.paused || !globe.ctx) return;
  const frame = () => {
    globe.animationFrame = null;
    if (globe.paused || !globe.ctx) return;
    stepGlobe();
    drawGlobe();
    updateGlobeTooltip();
    if (!globe.reducedMotion || globe.dragging || Math.abs(globe.velocityX) > 0.0002 || Math.abs(globe.velocityY) > 0.0002 || globe.targetRotationY !== null) {
      globe.animationFrame = requestAnimationFrame(frame);
    }
  };
  globe.animationFrame = requestAnimationFrame(frame);
}

function stepGlobe() {
  if (globe.targetRotationY !== null) {
    const deltaY = shortestAngle(globe.targetRotationY - globe.rotationY);
    const deltaX = (globe.targetRotationX || 0) - globe.rotationX;
    globe.rotationY += deltaY * 0.08;
    globe.rotationX += deltaX * 0.08;
    if (Math.abs(deltaY) < 0.002 && Math.abs(deltaX) < 0.002) {
      globe.targetRotationY = null;
      globe.targetRotationX = null;
    }
  } else if (!globe.dragging && !globe.reducedMotion) {
    globe.velocityY += 0.00018;
  }

  globe.rotationX += globe.velocityX;
  globe.rotationY += globe.velocityY;
  globe.rotationX = Math.max(-1.1, Math.min(1.1, globe.rotationX));
  globe.velocityX *= 0.92;
  globe.velocityY *= 0.94;
}

function drawGlobe() {
  if (!globe.ctx) return;
  const ctx = globe.ctx;
  ctx.clearRect(0, 0, globe.width, globe.height);
  drawGlobeBackground(ctx);
  drawGlobeSphere(ctx);
  drawOceanDetails(ctx);
  drawNaturalEarthLand(ctx);
  drawGlobeGrid(ctx);
  drawGlobeLoadingState(ctx);
  drawGlobeMarkets(ctx);
}

function drawGlobeBackground(ctx) {
  const gradient = ctx.createRadialGradient(globe.centerX, globe.centerY, 10, globe.centerX, globe.centerY, globe.radius * 1.8);
  gradient.addColorStop(0, "rgba(85, 199, 181, 0.18)");
  gradient.addColorStop(0.5, "rgba(18, 106, 114, 0.09)");
  gradient.addColorStop(1, "rgba(18, 106, 114, 0)");
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, globe.width, globe.height);

  ctx.save();
  ctx.globalAlpha = 0.55;
  for (let index = 0; index < 42; index += 1) {
    const x = (index * 97) % globe.width;
    const y = (index * 53) % globe.height;
    const size = 0.7 + ((index * 13) % 16) / 18;
    ctx.fillStyle = "rgba(180, 244, 233, 0.45)";
    ctx.beginPath();
    ctx.arc(x, y, size, 0, Math.PI * 2);
    ctx.fill();
  }
  ctx.restore();
}

function drawGlobeSphere(ctx) {
  ctx.save();
  ctx.shadowColor = "rgba(85, 199, 181, 0.38)";
  ctx.shadowBlur = 36;
  ctx.beginPath();
  ctx.arc(globe.centerX, globe.centerY, globe.radius, 0, Math.PI * 2);
  ctx.fillStyle = "rgba(5, 31, 52, 0.96)";
  ctx.fill();
  ctx.shadowBlur = 0;

  const surface = ctx.createRadialGradient(
    globe.centerX - globe.radius * 0.38,
    globe.centerY - globe.radius * 0.45,
    globe.radius * 0.1,
    globe.centerX,
    globe.centerY,
    globe.radius
  );
  surface.addColorStop(0, "rgba(116, 244, 223, 0.72)");
  surface.addColorStop(0.18, "rgba(28, 157, 181, 0.82)");
  surface.addColorStop(0.5, "rgba(9, 92, 136, 0.95)");
  surface.addColorStop(0.78, "rgba(4, 45, 83, 0.98)");
  surface.addColorStop(1, "rgba(1, 15, 29, 1)");
  ctx.fillStyle = surface;
  ctx.fill();

  const rim = ctx.createRadialGradient(globe.centerX, globe.centerY, globe.radius * 0.78, globe.centerX, globe.centerY, globe.radius * 1.08);
  rim.addColorStop(0, "rgba(255, 255, 255, 0)");
  rim.addColorStop(0.72, "rgba(108, 236, 220, 0.18)");
  rim.addColorStop(1, "rgba(168, 255, 238, 0.58)");
  ctx.fillStyle = rim;
  ctx.fill();

  ctx.strokeStyle = "rgba(167, 238, 226, 0.58)";
  ctx.lineWidth = 1.4;
  ctx.stroke();
  ctx.restore();
}

function drawOceanDetails(ctx) {
  withGlobeClip(ctx, () => {
    ctx.save();
    ctx.lineWidth = 0.7;
    ctx.strokeStyle = "rgba(174, 245, 242, 0.13)";
    for (let lat = -75; lat <= 75; lat += 15) {
      drawGeoLine(ctx, Array.from({ length: 121 }, (_, index) => ({
        lat: lat + Math.sin(index / 10) * 1.4,
        lon: -180 + index * 3
      })));
    }

    ctx.globalAlpha = 0.58;
    ctx.strokeStyle = "rgba(79, 207, 224, 0.18)";
    ctx.lineWidth = 1.1;
    [
      [[35, -150], [18, -125], [6, -92], [-8, -60], [-22, -30], [-32, 5]],
      [[-42, 24], [-30, 58], [-18, 86], [-8, 116], [8, 144], [26, 166]],
      [[54, -40], [44, -5], [34, 28], [22, 56], [12, 92]]
    ].forEach((line) => drawGeoLine(ctx, line.map(([lat, lon]) => ({ lat, lon }))));
    ctx.restore();
  });
}

function drawGlobeGrid(ctx) {
  ctx.save();
  ctx.lineWidth = 0.8;
  ctx.strokeStyle = "rgba(205, 255, 246, 0.22)";
  for (let lat = -60; lat <= 60; lat += 30) {
    drawGeoLine(ctx, Array.from({ length: 145 }, (_, index) => ({ lat, lon: -180 + index * 2.5 })));
  }
  for (let lon = -150; lon <= 180; lon += 30) {
    drawGeoLine(ctx, Array.from({ length: 73 }, (_, index) => ({ lat: -90 + index * 2.5, lon })));
  }
  ctx.restore();
}

async function loadNaturalEarthLand() {
  if (globe.naturalEarthLoaded) return;
  globe.naturalEarthFailed = false;
  setGlobeStatus("加载 1:10m 地球", "ok");
  try {
    const response = await fetch("world-land-10m.json?v=natural-earth-10m-20260507", { cache: "no-store" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const topology = await response.json();
    const rings = topologyToLandRings(topology);
    buildLandTexture(rings);
    globe.naturalEarthLoaded = true;
    globe.naturalEarthFailed = false;
    setGlobeStatus("1:10m 高精度", "ok");
    drawGlobe();
    animateGlobe();
  } catch (error) {
    console.warn("Natural Earth land data failed", error);
    globe.naturalEarthFailed = true;
    setGlobeStatus("高精度加载失败", "warn");
    drawGlobe();
  }
}

function topologyToLandRings(topology) {
  const scale = topology.transform?.scale || [1, 1];
  const translate = topology.transform?.translate || [0, 0];
  const decodedArcs = (topology.arcs || []).map((arc) => {
    let x = 0;
    let y = 0;
    return arc.map(([dx, dy]) => {
      x += dx;
      y += dy;
      return [x * scale[0] + translate[0], y * scale[1] + translate[1]];
    });
  });

  const rings = [];
  const geometries = topology.objects?.land?.geometries || [];
  geometries.forEach((geometry) => {
    if (geometry.type === "Polygon") {
      geometry.arcs.forEach((ring) => rings.push(stitchTopoRing(ring, decodedArcs)));
    } else if (geometry.type === "MultiPolygon") {
      geometry.arcs.forEach((polygon) => {
        polygon.forEach((ring) => rings.push(stitchTopoRing(ring, decodedArcs)));
      });
    }
  });
  return rings.filter((ring) => ring.length >= 3);
}

function stitchTopoRing(arcRefs, decodedArcs) {
  const ring = [];
  arcRefs.forEach((arcRef) => {
    const arcIndex = arcRef < 0 ? ~arcRef : arcRef;
    const sourceArc = decodedArcs[arcIndex] || [];
    const arc = arcRef < 0 ? [...sourceArc].reverse() : sourceArc;
    arc.forEach((point, index) => {
      if (ring.length && index === 0) return;
      ring.push(point);
    });
  });
  return ring;
}

function buildLandTexture(rings) {
  const width = 2048;
  const height = 1024;
  const textureCanvas = document.createElement("canvas");
  textureCanvas.width = width;
  textureCanvas.height = height;
  const textureCtx = textureCanvas.getContext("2d", { willReadFrequently: true });
  textureCtx.clearRect(0, 0, width, height);
  textureCtx.fillStyle = "#ffffff";

  rings.forEach((ring) => {
    textureCtx.beginPath();
    ring.forEach(([lon, lat], index) => {
      const x = ((lon + 180) / 360) * width;
      const y = ((90 - lat) / 180) * height;
      if (index === 0) {
        textureCtx.moveTo(x, y);
      } else {
        textureCtx.lineTo(x, y);
      }
    });
    textureCtx.closePath();
    textureCtx.fill();
  });

  const pixels = textureCtx.getImageData(0, 0, width, height).data;
  const landMask = new Uint8Array(width * height);
  for (let index = 0; index < landMask.length; index += 1) {
    landMask[index] = pixels[index * 4 + 3] > 0 ? 1 : 0;
  }

  const coastMask = new Uint8Array(width * height);
  for (let y = 1; y < height - 1; y += 1) {
    for (let x = 0; x < width; x += 1) {
      const index = y * width + x;
      if (!landMask[index]) continue;
      const left = y * width + ((x + width - 1) % width);
      const right = y * width + ((x + 1) % width);
      if (!landMask[left] || !landMask[right] || !landMask[index - width] || !landMask[index + width]) {
        coastMask[index] = 1;
      }
    }
  }

  globe.landMask = landMask;
  globe.coastMask = coastMask;
  globe.landTextureWidth = width;
  globe.landTextureHeight = height;
}

function drawNaturalEarthLand(ctx) {
  if (!globe.landMask) {
    return;
  }

  const radius = Math.max(1, Math.floor(globe.radius));
  const padding = 3;
  const size = radius * 2 + padding * 2;
  if (!globe.landFrameCanvas) {
    globe.landFrameCanvas = document.createElement("canvas");
    globe.landFrameCtx = globe.landFrameCanvas.getContext("2d", { willReadFrequently: true });
  }
  if (globe.landFrameSize !== size) {
    globe.landFrameSize = size;
    globe.landFrameCanvas.width = size;
    globe.landFrameCanvas.height = size;
  }

  const frameCtx = globe.landFrameCtx;
  const image = frameCtx.createImageData(size, size);
  const data = image.data;
  const center = radius + padding;
  const texW = globe.landTextureWidth;
  const texH = globe.landTextureHeight;
  const light = { x: -0.42, y: 0.48, z: 0.78 };

  for (let y = 0; y < size; y += 1) {
    const ny = (center - y) / radius;
    for (let x = 0; x < size; x += 1) {
      const nx = (x - center) / radius;
      const distance = nx * nx + ny * ny;
      if (distance > 1) continue;
      const nz = Math.sqrt(1 - distance);
      const world = inverseRotateVector({ x: nx, y: ny, z: nz });
      const lon = Math.atan2(world.x, world.z) * 180 / Math.PI;
      const lat = Math.asin(Math.max(-1, Math.min(1, world.y))) * 180 / Math.PI;
      const tx = Math.max(0, Math.min(texW - 1, Math.floor(((lon + 180) / 360) * texW)));
      const ty = Math.max(0, Math.min(texH - 1, Math.floor(((90 - lat) / 180) * texH)));
      const textureIndex = ty * texW + tx;
      if (!globe.landMask[textureIndex]) continue;

      const pixel = (y * size + x) * 4;
      const shade = Math.max(0.52, Math.min(1.16, 0.66 + (nx * light.x + ny * light.y + nz * light.z) * 0.42));
      const coast = globe.coastMask[textureIndex];
      data[pixel] = coast ? Math.round(128 * shade) : Math.round(54 * shade);
      data[pixel + 1] = coast ? Math.round(255 * shade) : Math.round(186 * shade);
      data[pixel + 2] = coast ? Math.round(214 * shade) : Math.round(142 * shade);
      data[pixel + 3] = coast ? 226 : 146;
    }
  }

  frameCtx.putImageData(image, 0, 0);
  ctx.save();
  ctx.shadowColor = "rgba(99, 255, 204, 0.28)";
  ctx.shadowBlur = 12;
  ctx.drawImage(globe.landFrameCanvas, globe.centerX - center, globe.centerY - center);
  ctx.restore();
}

function drawGlobeLoadingState(ctx) {
  if (globe.landMask) return;
  ctx.save();
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.font = "800 13px Inter, 'Segoe UI', sans-serif";
  ctx.fillStyle = globe.naturalEarthFailed ? "rgba(255, 190, 104, 0.92)" : "rgba(180, 244, 233, 0.9)";
  ctx.shadowColor = globe.naturalEarthFailed ? "rgba(255, 190, 104, 0.28)" : "rgba(85, 199, 181, 0.28)";
  ctx.shadowBlur = 14;
  ctx.fillText(
    globe.naturalEarthFailed ? "1:10m 数据加载失败" : "正在加载 Natural Earth 1:10m",
    globe.centerX,
    globe.centerY + globe.radius * 0.82
  );
  ctx.restore();
}

function drawGeoLine(ctx, points) {
  let drawing = false;
  points.forEach((point) => {
    const projected = projectLatLon(point.lat, point.lon);
    if (!projected.visible) {
      if (drawing) ctx.stroke();
      drawing = false;
      return;
    }
    if (!drawing) {
      ctx.beginPath();
      ctx.moveTo(projected.x, projected.y);
      drawing = true;
    } else {
      ctx.lineTo(projected.x, projected.y);
    }
  });
  if (drawing) ctx.stroke();
}

function withGlobeClip(ctx, drawer) {
  ctx.save();
  ctx.beginPath();
  ctx.arc(globe.centerX, globe.centerY, globe.radius - 1, 0, Math.PI * 2);
  ctx.clip();
  drawer();
  ctx.restore();
}

function drawGlobeMarkets(ctx) {
  globe.hotspots = [];
  WORLD_CLOCKS.forEach((clock, index) => {
    const projected = projectLatLon(clock.lat, clock.lon);
    globe.hotspots.push({ ...projected, index });
    if (!projected.visible) return;
    const selected = index === state.selectedClockIndex;
    const pulse = selected ? 1 + Math.sin(Date.now() / 220) * 0.12 : 1;
    const radius = (selected ? 7.5 : 5) * pulse;
    ctx.save();
    ctx.globalAlpha = Math.max(0.35, projected.depth);
    ctx.shadowColor = selected ? "rgba(255, 214, 112, 0.95)" : "rgba(85, 199, 181, 0.85)";
    ctx.shadowBlur = selected ? 22 : 14;
    ctx.fillStyle = selected ? "#ffd670" : "#7cf0d5";
    ctx.beginPath();
    ctx.arc(projected.x, projected.y, radius, 0, Math.PI * 2);
    ctx.fill();
    ctx.shadowBlur = 0;
    ctx.strokeStyle = selected ? "rgba(255, 246, 210, 0.95)" : "rgba(220, 255, 248, 0.82)";
    ctx.lineWidth = 1.5;
    ctx.stroke();
    ctx.restore();
  });
}

function latLonToVector(lat, lon) {
  const latRad = lat * Math.PI / 180;
  const lonRad = lon * Math.PI / 180;
  const cosLat = Math.cos(latRad);
  return {
    x: cosLat * Math.sin(lonRad),
    y: Math.sin(latRad),
    z: cosLat * Math.cos(lonRad)
  };
}

function rotateVector(vector) {
  const cosY = Math.cos(globe.rotationY);
  const sinY = Math.sin(globe.rotationY);
  const x1 = vector.x * cosY + vector.z * sinY;
  const z1 = -vector.x * sinY + vector.z * cosY;
  const cosX = Math.cos(globe.rotationX);
  const sinX = Math.sin(globe.rotationX);
  return {
    x: x1,
    y: vector.y * cosX - z1 * sinX,
    z: vector.y * sinX + z1 * cosX
  };
}

function inverseRotateVector(vector) {
  const cosX = Math.cos(globe.rotationX);
  const sinX = Math.sin(globe.rotationX);
  const y1 = vector.y * cosX + vector.z * sinX;
  const z1 = -vector.y * sinX + vector.z * cosX;
  const cosY = Math.cos(globe.rotationY);
  const sinY = Math.sin(globe.rotationY);
  return {
    x: vector.x * cosY - z1 * sinY,
    y: y1,
    z: vector.x * sinY + z1 * cosY
  };
}

function projectLatLon(lat, lon) {
  const rotated = rotateVector(latLonToVector(lat, lon));
  const visible = rotated.z >= -0.01;
  return {
    x: globe.centerX + rotated.x * globe.radius,
    y: globe.centerY - rotated.y * globe.radius,
    visible,
    depth: Math.max(0, Math.min(1, (rotated.z + 0.2) / 1.2))
  };
}

function handleGlobePointerDown(event) {
  if (!elements.globeCanvas) return;
  globe.dragging = true;
  globe.moved = false;
  globe.lastX = event.clientX;
  globe.lastY = event.clientY;
  globe.velocityX = 0;
  globe.velocityY = 0;
  globe.targetRotationX = null;
  globe.targetRotationY = null;
  if (elements.globeCanvas.setPointerCapture) {
    elements.globeCanvas.setPointerCapture(event.pointerId);
  }
  setGlobeStatus("拖拽中", "ok");
  animateGlobe();
}

function handleGlobePointerMove(event) {
  if (!globe.dragging) return;
  const dx = event.clientX - globe.lastX;
  const dy = event.clientY - globe.lastY;
  globe.moved = globe.moved || Math.abs(dx) + Math.abs(dy) > 4;
  globe.rotationY += dx * 0.006;
  globe.rotationX += dy * 0.005;
  globe.rotationX = Math.max(-1.1, Math.min(1.1, globe.rotationX));
  globe.velocityY = dx * 0.0009;
  globe.velocityX = dy * 0.0007;
  globe.lastX = event.clientX;
  globe.lastY = event.clientY;
  drawGlobe();
  updateGlobeTooltip();
}

function handleGlobePointerUp(event) {
  if (!globe.dragging) return;
  globe.dragging = false;
  if (elements.globeCanvas?.hasPointerCapture?.(event.pointerId)) {
    elements.globeCanvas.releasePointerCapture(event.pointerId);
  }
  if (!globe.moved) {
    const rect = elements.globeCanvas.getBoundingClientRect();
    selectGlobeHotspot(event.clientX - rect.left, event.clientY - rect.top);
  } else {
    setGlobeStatus("可拖拽旋转", "ok");
  }
  animateGlobe();
}

function selectGlobeHotspot(x, y) {
  const hit = globe.hotspots
    .filter((item) => item.visible)
    .map((item) => ({ ...item, distance: Math.hypot(item.x - x, item.y - y) }))
    .sort((a, b) => a.distance - b.distance)[0];
  if (hit && hit.distance < 24) {
    selectClock(hit.index, false);
    setGlobeStatus(`${WORLD_CLOCKS[hit.index].city} 已选中`, "ok");
    return true;
  }
  clearClockSelection();
  setGlobeStatus("未选中", "warn");
  return false;
}

function selectClock(index, shouldFocus = true) {
  const numericIndex = Number(index);
  if (!Number.isInteger(numericIndex) || numericIndex < 0 || numericIndex >= WORLD_CLOCKS.length) {
    clearClockSelection();
    return;
  }
  state.selectedClockIndex = numericIndex;
  setGlobeStatus(`${WORLD_CLOCKS[numericIndex].city} 已选中`, "ok");
  if (shouldFocus) focusGlobeOnClock(state.selectedClockIndex);
  renderWorldClocks();
  drawGlobe();
}

function clearClockSelection() {
  state.selectedClockIndex = null;
  renderWorldClocks();
  updateGlobeTooltip();
  drawGlobe();
}

function focusGlobeOnClock(index, animate = true) {
  if (index === null || index === undefined) return;
  const clock = WORLD_CLOCKS[index] || WORLD_CLOCKS[0];
  const targetY = -clock.lon * Math.PI / 180;
  const targetX = Math.max(-0.75, Math.min(0.75, clock.lat * Math.PI / 180 * 0.35));
  if (animate) {
    globe.targetRotationY = targetY;
    globe.targetRotationX = targetX;
    animateGlobe();
    return;
  }
  globe.rotationY = targetY;
  globe.rotationX = targetX;
}

function shortestAngle(value) {
  return Math.atan2(Math.sin(value), Math.cos(value));
}

function updateGlobeTooltip() {
  if (!elements.globeTooltip) return;
  if (state.selectedClockIndex === null) {
    elements.globeTooltip.hidden = true;
    return;
  }
  elements.globeTooltip.hidden = false;
  const clock = WORLD_CLOCKS[state.selectedClockIndex] || WORLD_CLOCKS[0];
  const hotspot = globe.hotspots.find((item) => item.index === state.selectedClockIndex);
  elements.globeTooltip.innerHTML = `
    <strong>${clock.city}</strong>
    <span>${clock.market} · ${clock.timeZone}</span>
    <b>${formatClockTime(clock.timeZone)}</b>
    <small>${formatClockDate(clock.timeZone)}</small>
  `;
  if (hotspot && hotspot.visible) {
    elements.globeTooltip.style.transform = `translate(${Math.min(Math.max(hotspot.x + 14, 10), globe.width - 190)}px, ${Math.min(Math.max(hotspot.y - 48, 10), globe.height - 112)}px)`;
  } else {
    elements.globeTooltip.style.transform = `translate(${globe.width - 208}px, 14px)`;
  }
}

function filteredFxRows() {
  const query = state.query.trim().toLowerCase();
  return CURRENCIES.filter((currency) => {
    if (!query) return true;
    return `${currency.code} ${currency.name}`.toLowerCase().includes(query);
  });
}

function filteredIndexRows() {
  const query = state.query.trim().toLowerCase();
  return state.indices.filter((item) => {
    if (state.regionFilter && item.region && item.region !== state.regionFilter) return false;
    if (!query) return true;
    return `${item.zhName || ""} ${item.name} ${item.symbol}`.toLowerCase().includes(query);
  });
}

function skeletonCards(count, className = "fx-card") {
  return Array.from({ length: count }, () => `
    <article class="${className} skeleton-card" aria-hidden="true">
      <span class="skeleton-line short"></span>
      <span class="skeleton-line long"></span>
      <span class="skeleton-line medium"></span>
    </article>
  `).join("");
}

function renderSparkline(trend, tone = "muted", mode = state.trendMode) {
  const points = trend && Array.isArray(trend.points) ? trend.points : [];
  if (points.length < 2) {
    return `
      <span class="sparkline-placeholder" aria-label="走势加载中">
        <span class="skeleton-line medium"></span>
        <span class="sparkline-caption">${trendModeLabel(mode)}</span>
      </span>
    `;
  }

  const width = 128;
  const height = 42;
  const pad = 4;
  const coords = pointCoords(points, width, height, pad);
  const line = linePath(coords);
  const area = `${line} L ${coords[coords.length - 1][0].toFixed(2)} ${height - pad} L ${coords[0][0].toFixed(2)} ${height - pad} Z`;
  const qualityLabel = trend.derived || trend.quality === "fallback" ? "区间兜底" : "真实K线";
  const label = `${trend.source || "走势"} · ${trendModeLabel(mode)} · ${qualityLabel}`;
  const svg = `
    <svg class="sparkline ${tone}" viewBox="0 0 ${width} ${height}" role="img" aria-label="${escapeHtml(label)}">
      <path class="sparkline-area" d="${area}"></path>
      <path class="sparkline-line" d="${line}"></path>
      <circle class="sparkline-dot" cx="${coords[coords.length - 1][0].toFixed(2)}" cy="${coords[coords.length - 1][1].toFixed(2)}" r="2.8"></circle>
    </svg>
    <span class="sparkline-caption">${escapeHtml(trendModeLabel(mode))}${trend.derived || trend.quality === "fallback" ? " · 兜底" : ""}</span>
  `;
  return trend.sourceUrl
    ? `<a class="sparkline-link" href="${trend.sourceUrl}" target="_blank" rel="noopener noreferrer" title="${escapeHtml(label)}">${svg}</a>`
    : `<span class="sparkline-link" title="${escapeHtml(label)}">${svg}</span>`;
}

function pointCoords(points, width, height, pad) {
  const values = points
    .flatMap((point) => [point.high, point.low, point.value])
    .filter(Number.isFinite);
  let min = Math.min(...values);
  let max = Math.max(...values);
  if (!Number.isFinite(min) || !Number.isFinite(max)) {
    min = 0;
    max = 1;
  }
  if (max === min) {
    max += 1;
    min -= 1;
  }
  return points.map((point, index) => {
    const x = pad + ((width - pad * 2) * index) / Math.max(points.length - 1, 1);
    const y = pad + (height - pad * 2) * (1 - (point.value - min) / (max - min));
    return [x, y, point];
  });
}

function linePath(coords) {
  return coords.map(([x, y], index) => `${index ? "L" : "M"} ${x.toFixed(2)} ${y.toFixed(2)}`).join(" ");
}

function renderDetailChart(index, trend, tone) {
  const points = trend && Array.isArray(trend.points) ? trend.points : [];
  if (points.length < 2) {
    return `<div class="empty-state chart-empty">暂无可用图表数据</div>`;
  }

  const width = 920;
  const height = 320;
  const padX = 34;
  const padY = 22;
  const chartMode = trend.mode || state.detailTrendMode || state.trendMode;
  const useCandles = chartMode !== "intraday" && trend.quality !== "fallback" && points.some((point) => (
    Number.isFinite(point.open) && Number.isFinite(point.high) && Number.isFinite(point.low) && Number.isFinite(point.close)
  ));
  const first = points[0].value;
  const last = points[points.length - 1].value;
  const netTone = last > first ? "up" : last < first ? "down" : "muted";
  const values = points.flatMap((point) => [point.high, point.low, point.value]).filter(Number.isFinite);
  let min = Math.min(...values);
  let max = Math.max(...values);
  if (max === min) {
    max += 1;
    min -= 1;
  }
  const xFor = (indexAt) => padX + ((width - padX * 2) * indexAt) / Math.max(points.length - 1, 1);
  const yFor = (value) => padY + (height - padY * 2) * (1 - (value - min) / (max - min));
  const coords = points.map((point, indexAt) => [xFor(indexAt), yFor(point.value), point]);
  const line = linePath(coords);
  const candleWidth = Math.max(3, Math.min(11, (width - padX * 2) / points.length * 0.58));
  const axisLines = [0.25, 0.5, 0.75].map((ratio) => {
    const y = padY + (height - padY * 2) * ratio;
    return `<line class="chart-gridline" x1="${padX}" x2="${width - padX}" y1="${y.toFixed(2)}" y2="${y.toFixed(2)}"></line>`;
  }).join("");
  const titleText = `${index.zhName || index.name} ${trendModeMeta(chartMode).chartLabel}`;

  const candleMarkup = useCandles
    ? points.map((point, indexAt) => {
        const open = Number.isFinite(point.open) ? point.open : point.value;
        const close = Number.isFinite(point.close) ? point.close : point.value;
        const high = Number.isFinite(point.high) ? point.high : Math.max(open, close);
        const low = Number.isFinite(point.low) ? point.low : Math.min(open, close);
        const x = xFor(indexAt);
        const yHigh = yFor(high);
        const yLow = yFor(low);
        const yOpen = yFor(open);
        const yClose = yFor(close);
        const candleTone = close >= open ? "up" : "down";
        const top = Math.min(yOpen, yClose);
        const bodyHeight = Math.max(2, Math.abs(yClose - yOpen));
        return `
          <g class="candle ${candleTone}">
            <line x1="${x.toFixed(2)}" x2="${x.toFixed(2)}" y1="${yHigh.toFixed(2)}" y2="${yLow.toFixed(2)}"></line>
            <rect x="${(x - candleWidth / 2).toFixed(2)}" y="${top.toFixed(2)}" width="${candleWidth.toFixed(2)}" height="${bodyHeight.toFixed(2)}" rx="1.5"></rect>
          </g>
        `;
      }).join("")
    : `
      <path class="detail-area ${netTone}" d="${line} L ${(width - padX).toFixed(2)} ${(height - padY).toFixed(2)} L ${padX.toFixed(2)} ${(height - padY).toFixed(2)} Z"></path>
      <path class="detail-line ${netTone}" d="${line}"></path>
    `;

  const hotspots = points.map((point, indexAt) => {
    const x = xFor(indexAt);
    const y = yFor(point.value);
    const tooltip = chartTooltipText(point, trend, index);
    return `
      <circle
        class="chart-hotspot"
        data-point-time="${escapeHtml(point.time)}"
        data-point-value="${escapeHtml(formatNumber(point.value, 2))}"
        data-point-title="${escapeHtml(tooltip)}"
        cx="${x.toFixed(2)}"
        cy="${y.toFixed(2)}"
        r="8"
      >
        <title>${escapeHtml(tooltip)}</title>
      </circle>
    `;
  }).join("");

  return `
    <svg class="detail-svg" viewBox="0 0 ${width} ${height}" role="img" aria-label="${escapeHtml(titleText)}">
      ${axisLines}
      ${candleMarkup}
      ${hotspots}
    </svg>
  `;
}

function chartTooltipText(point, trend, index) {
  const timeLabel = formatPointTime(point.time, trend.timeZone || index.timeZone, trend.timeZoneLabel || index.timeZoneLabel);
  const open = Number.isFinite(point.open) ? `开 ${formatNumber(point.open, 2)} · ` : "";
  const high = Number.isFinite(point.high) ? `高 ${formatNumber(point.high, 2)} · ` : "";
  const low = Number.isFinite(point.low) ? `低 ${formatNumber(point.low, 2)} · ` : "";
  const close = Number.isFinite(point.close) ? `收 ${formatNumber(point.close, 2)}` : `值 ${formatNumber(point.value, 2)}`;
  return `${timeLabel}\n${open}${high}${low}${close}`;
}

function formatPointTime(value, timeZone = "UTC", timeZoneLabel = "数据源时间") {
  if (!value) return "--";
  if (/^\d{4}-\d{2}$/.test(value)) return `${value} 月线`;
  if (/^\d{4}-\d{2}-\d{2}$/.test(value)) return `${timeZoneLabel} ${value}`;
  if (!/^\d{4}-\d{2}-\d{2}/.test(value)) return value;
  return formatDualTime(value, timeZone, timeZoneLabel);
}

function escapeHtml(value) {
  return String(value || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function renderFx() {
  const fx = state.fx || FALLBACK_FX;
  const rows = filteredFxRows();
  elements.fxGrid.innerHTML = state.loading && !state.fx
    ? skeletonCards(8)
    : rows.length
    ? rows.map((currency) => {
        const rate = fx.rates[currency.code];
        const official = officialFxLink(fx.base, currency.code);
        const dataSource = fx.source
          ? `<span class="fx-data-source">数据计算 · ${escapeHtml(fx.source)}</span>`
          : "";
        const quality = qualityLabel(fx.quality, fx.cacheState);
        const qualityClass = qualityTone(fx.quality, fx.cacheState);
        const latency = Number.isFinite(fx.latencyMs) ? ` · ${latencyLabel(fx.latencyMs)}` : "";
        const body = `
            <header>
              <span class="fx-code">${currency.code}</span>
              <span class="fx-name">${currency.name}</span>
            </header>
            <div class="fx-rate">${formatFxRate(rate)}</div>
            <small>1 ${fx.base} = ${formatFxRate(rate)} ${currency.code}</small>
            <span class="quality-badge ${qualityClass}">${quality}${latency}</span>
        `;
        return official?.url
          ? `<a class="fx-card fx-card-link" href="${escapeHtml(official.url)}" target="_blank" rel="noopener noreferrer" aria-label="打开 ${fx.base}/${currency.code} 官方汇率页面">${body}<span class="fx-source-hint">${escapeHtml(official.label)}</span>${dataSource}</a>`
          : `<article class="fx-card">${body}</article>`;
      }).join("")
    : `<div class="empty-state">没有匹配的货币</div>`;

  elements.fxStatus.textContent = fx.stale ? "缓存/参考" : "已更新";
  elements.fxStatus.className = `pill ${fx.stale ? "warn" : "ok"}`;
}

function renderIndices() {
  const rows = filteredIndexRows();
  const activeTrends = state.trends[state.trendMode] || {};
  const modeLabel = trendModeLabel(state.trendMode);
  elements.indicesBody.innerHTML = state.loading && !state.indices.length
    ? Array.from({ length: 7 }, () => `
        <tr class="skeleton-row" aria-hidden="true">
          <td><span class="skeleton-line long"></span></td>
          <td><span class="skeleton-line short"></span></td>
          <td><span class="skeleton-line medium"></span></td>
          <td><span class="skeleton-line short"></span></td>
          <td><span class="skeleton-line short"></span></td>
          <td><span class="skeleton-line medium"></span></td>
          <td><span class="skeleton-line long"></span></td>
          <td><span class="skeleton-line short"></span></td>
        </tr>
      `).join("")
    : rows.length
    ? rows.map((item) => {
        const tone = item.change > 0 ? "up" : item.change < 0 ? "down" : "muted";
        const trend = activeTrends[item.symbol];
        const zhName = item.zhName || item.name || item.symbol;
        const enName = item.name && item.name !== zhName
          ? `<span class="index-en">${item.name}</span>`
          : "";
        const nameMarkup = `<span class="index-zh">${zhName}</span>${enName}`;
        const detailLink = item.detailUrl
          ? `<a class="index-link" href="${item.detailUrl}" target="_blank" rel="noopener noreferrer">${nameMarkup}</a>`
          : `<span class="index-name">${nameMarkup}</span>`;
        const quality = qualityLabel(item.quality, item.cacheState);
        const qualityClass = qualityTone(item.quality, item.cacheState);
        const sourceUrl = item.sourceDetailUrl || item.detailUrl;
        return `
          <tr class="index-row ${state.detailSymbol === item.symbol ? "active" : ""}" data-index-symbol="${escapeHtml(item.symbol)}" tabindex="0" aria-label="打开 ${escapeHtml(zhName)} 图表详情">
            <td>
              ${detailLink}
            </td>
            <td class="index-symbol">${item.symbol}</td>
            <td>${item.unavailable ? "unavailable" : formatNumber(item.price, 2)}</td>
            <td class="${tone}">${item.unavailable ? "--" : signedNumber(item.change)}</td>
            <td class="${tone}">${item.unavailable ? "--" : formatPercent(item.changePct)}</td>
            <td class="trend-cell">${renderSparkline(trend, tone, state.trendMode)}</td>
            <td>${item.unavailable ? "--" : formatDualTimeCell(item.updatedAt, item.timeZone, item.timeZoneLabel)}</td>
            <td>
              <span class="quality-badge ${qualityClass}">${quality}</span>
              ${sourceUrl ? `<a class="source-link" href="${sourceUrl}" target="_blank" rel="noopener noreferrer">官方详情</a>` : "--"}
            </td>
          </tr>
        `;
      }).join("")
    : `<tr><td colspan="8" class="empty-state">没有匹配的指数</td></tr>`;

  const unavailableCount = state.indices.filter((item) => item.unavailable).length;
  const trendLoading = state.trendLoadingByMode[state.trendMode];
  elements.indexStatus.textContent = trendLoading
    ? `加载${modeLabel}...`
    : unavailableCount
      ? `部分可用 ${state.indices.length - unavailableCount}/${state.indices.length}`
      : "已更新";
  elements.indexStatus.className = `pill ${unavailableCount ? "warn" : "ok"}`;
  renderIndexDetail();
}

function signedNumber(value) {
  if (!Number.isFinite(value)) return "--";
  const sign = value > 0 ? "+" : "";
  return `${sign}${formatNumber(value, 2)}`;
}

function renderModeButtons() {
  elements.trendModeButtons.forEach((button) => {
    const active = button.dataset.trendMode === state.trendMode;
    button.classList.toggle("active", active);
    button.setAttribute("aria-selected", String(active));
  });
  elements.detailTrendModeButtons.forEach((button) => {
    const active = button.dataset.detailTrendMode === state.detailTrendMode;
    button.classList.toggle("active", active);
    button.setAttribute("aria-selected", String(active));
  });
}

function renderIndexDetail() {
  renderModeButtons();
  if (!elements.indexDetail) return;
  const index = state.indices.find((item) => item.symbol === state.detailSymbol);
  if (!index) {
    elements.indexDetail.hidden = true;
    return;
  }

  const mode = normalizeTrendMode(state.detailTrendMode || state.trendMode);
  const trend = (state.trends[mode] || {})[index.symbol];
  const tone = index.change > 0 ? "up" : index.change < 0 ? "down" : "muted";
  const qualityLabel = trend && (trend.derived || trend.quality === "fallback")
    ? "报价区间兜底"
    : `${qualityLabelText(trend ? trend.quality : index.quality)}K线`;
  const fallbackText = trend && trend.fallbackReason ? ` · ${trend.fallbackReason}` : "";
  const timeLabel = trend && trend.updatedAt
    ? formatDualTime(trend.updatedAt, trend.timeZone || index.timeZone, trend.timeZoneLabel || index.timeZoneLabel)
    : formatDualTime(index.updatedAt, index.timeZone, index.timeZoneLabel);

  elements.indexDetail.hidden = false;
  elements.detailTitle.textContent = `${index.zhName || index.name} · ${index.symbol}`;
  elements.detailMeta.textContent = `${trendModeMeta(mode).chartLabel} · ${qualityLabel} · ${trend ? trend.source : "走势加载中"} · ${timeLabel}${fallbackText}`;
  const sourceTarget = trend && trend.sourceUrl ? trend.sourceUrl : index.detailUrl || "";
  elements.detailSource.href = sourceTarget || "#";
  elements.detailSource.textContent = trend && trend.sourceUrl ? "打开数据源" : "打开官方详情";
  elements.detailSource.toggleAttribute("hidden", !sourceTarget);
  elements.detailChart.innerHTML = renderDetailChart(index, trend, tone);
  elements.detailStats.innerHTML = renderDetailStats(index, trend, tone);
}

function renderDetailStats(index, trend, tone) {
  const points = trend && Array.isArray(trend.points) ? trend.points : [];
  const first = points[0] && points[0].value;
  const last = points[points.length - 1] && points[points.length - 1].value;
  const rangeChange = Number.isFinite(first) && Number.isFinite(last) ? last - first : NaN;
  const rangePct = Number.isFinite(rangeChange) && first ? (rangeChange / first) * 100 : NaN;
  return `
    <span><b>最新</b>${index.unavailable ? "--" : formatNumber(index.price, 2)}</span>
    <span class="${tone}"><b>实时涨跌</b>${index.unavailable ? "--" : signedNumber(index.change)}</span>
    <span class="${tone}"><b>实时涨跌幅</b>${index.unavailable ? "--" : formatPercent(index.changePct)}</span>
    <span class="${rangeChange > 0 ? "up" : rangeChange < 0 ? "down" : "muted"}"><b>图表区间</b>${signedNumber(rangeChange)} / ${formatPercent(rangePct)}</span>
  `;
}

function renderConverter() {
  const fx = state.fx || FALLBACK_FX;
  const amount = Number(elements.amountInput.value);
  const from = elements.fromCurrency.value;
  const to = elements.toCurrency.value;
  const fromRate = fx.rates[from];
  const toRate = fx.rates[to];

  if (!Number.isFinite(amount) || !Number.isFinite(fromRate) || !Number.isFinite(toRate)) {
    elements.converterResult.textContent = "--";
    elements.converterResult.removeAttribute("title");
    return;
  }

  const result = (amount / fromRate) * toRate;
  const resultText = `${formatPreciseNumber(amount, 12)} ${from} = ${formatPreciseNumber(result, 12)} ${to}`;
  elements.converterResult.textContent = resultText;
  elements.converterResult.title = `${amount} ${from} = ${Number.parseFloat(result.toPrecision(15))} ${to}`;
}

function renderSummary() {
  const fx = state.fx || FALLBACK_FX;
  const up = state.indices.filter((item) => item.change > 0).length;
  const down = state.indices.filter((item) => item.change < 0).length;
  const sources = new Set([
    fx.source,
    ...state.indices
      .filter((item) => !item.unavailable)
      .map((item) => item.source)
  ].filter(Boolean));

  elements.baseCurrencySelect.value = state.baseCurrency;
  elements.baseCurrencyHelp.textContent = `汇率以 1 ${fx.base} 为基准`;
  elements.marketBreadth.textContent = state.indices.length ? `${up} 涨 / ${down} 跌` : "--";
  elements.sourceLabel.textContent = Array.from(sources).slice(0, 3).join(" · ") || "--";
  if (elements.diagnosticsLabel && elements.diagnosticsHelp) {
    const diagnostics = state.diagnostics;
    const sourceCount = diagnostics && diagnostics.sources ? Object.keys(diagnostics.sources).length : 0;
    const cacheCount = diagnostics && diagnostics.cache
      ? Object.values(diagnostics.cache).reduce((total, group) => total + Object.keys(group || {}).length, 0)
      : 0;
    elements.diagnosticsLabel.textContent = diagnostics
      ? `${sourceCount} 源监控 · ${cacheCount} 组缓存`
      : "本地 API · 待检测";
    elements.diagnosticsHelp.textContent = diagnostics
      ? `版本 ${diagnostics.version || "--"} · ${diagnostics.publicAccess?.cachePolicy || "no-store"}`
      : "刷新后显示数据源、缓存和公网资源状态";
  }
  elements.updatedAt.textContent = state.lastUpdatedAt
    ? formatDualTime(state.lastUpdatedAt, LOCAL_TIME_ZONE, localTimeZoneLabel())
    : "--";
}

function renderStatus(message, tone = "default") {
  elements.statusText.textContent = message;
  elements.statusText.className = tone;
}

function renderAll() {
  renderTerminal();
  renderFx();
  renderIndices();
  renderConverter();
  renderSummary();
}

async function refreshData() {
  if (state.loading) return;
  state.loading = true;
  elements.refreshButton.disabled = true;
  elements.refreshButton.classList.add("loading");
  document.body.classList.add("is-refreshing");
  renderStatus("正在刷新免费公开数据源...");
  renderAll();

  try {
    const [fx, indices, diagnostics] = await Promise.all([
      fetchFxRates(state.baseCurrency),
      fetchIndices(),
      fetchDiagnostics()
    ]);
    state.fx = fx;
    state.indices = indices;
    state.diagnostics = diagnostics;
    state.lastUpdatedAt = new Date().toISOString();

    const hasFallback = fx.stale || indices.some((item) => item.stale || item.unavailable);
    renderStatus(hasFallback ? "已加载，部分数据来自缓存或暂不可用。" : "市场数据已更新。", hasFallback ? "warn" : "ok");
    renderAll();
    loadTrends();
  } catch (error) {
    console.error(error);
    renderStatus("数据刷新失败，请稍后重试。", "warn");
  } finally {
    state.loading = false;
    elements.refreshButton.disabled = false;
    elements.refreshButton.classList.remove("loading");
    document.body.classList.remove("is-refreshing");
    renderAll();
  }
}

async function loadTrends() {
  const mode = normalizeTrendMode(state.trendMode);
  if (state.trendLoadingByMode[mode]) return;
  state.trendsLoading = true;
  state.trendLoadingByMode[mode] = true;
  scheduleRender();
  try {
    state.trends[mode] = await fetchTrends(mode);
  } catch (error) {
    console.warn("Trend refresh failed.", error);
  } finally {
    state.trendsLoading = false;
    state.trendLoadingByMode[mode] = false;
    scheduleRender();
  }
}

function loadDetailTrend(mode = state.detailTrendMode) {
  const normalized = normalizeTrendMode(mode);
  if (state.trends[normalized] && Object.keys(state.trends[normalized]).length) {
    scheduleRender();
    return;
  }
  const previousMode = state.trendMode;
  state.trendMode = normalized;
  loadTrends();
  state.trendMode = previousMode;
}

function setTrendMode(mode) {
  const normalized = normalizeTrendMode(mode);
  if (state.trendMode === normalized) return;
  state.trendMode = normalized;
  state.detailTrendMode = normalized;
  writeCache(CACHE_KEYS.trendMode, normalized);
  runViewTransition(() => renderAll());
  loadTrends();
}

function setDetailTrendMode(mode) {
  const normalized = normalizeTrendMode(mode);
  state.detailTrendMode = normalized;
  runViewTransition(() => renderIndexDetail());
  loadDetailTrend(normalized);
}

function openIndexDetail(symbol) {
  if (!symbol) return;
  state.detailSymbol = symbol;
  state.detailTrendMode = state.trendMode;
  runViewTransition(() => renderAll());
  loadDetailTrend(state.detailTrendMode);
  requestAnimationFrame(() => {
    if (elements.indexDetail && !elements.indexDetail.hidden) {
      elements.indexDetail.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }
  });
}

function closeIndexDetail() {
  state.detailSymbol = null;
  if (elements.chartTooltip) elements.chartTooltip.hidden = true;
  runViewTransition(() => renderAll());
}

function handleChartPointerMove(event) {
  if (!elements.chartTooltip) return;
  const eventTarget = event.target instanceof Element ? event.target : event.target.parentElement;
  const target = eventTarget && eventTarget.closest(".chart-hotspot");
  if (!target) {
    hideChartTooltip();
    return;
  }
  elements.chartTooltip.textContent = target.dataset.pointTitle || "--";
  elements.chartTooltip.hidden = false;
  const chartBox = elements.detailChart.getBoundingClientRect();
  const tooltipX = Math.min(Math.max(event.clientX - chartBox.left + 14, 8), chartBox.width - 190);
  const tooltipY = Math.min(Math.max(event.clientY - chartBox.top + 14, 8), chartBox.height - 70);
  elements.chartTooltip.style.transform = `translate(${tooltipX}px, ${tooltipY}px)`;
}

function hideChartTooltip() {
  if (elements.chartTooltip) elements.chartTooltip.hidden = true;
}

function bindEvents() {
  elements.searchInput.addEventListener("input", (event) => {
    state.query = event.target.value;
    scheduleRender();
  });

  elements.themeToggle.addEventListener("click", toggleTheme);
  elements.colorModeToggle.addEventListener("click", toggleColorMode);
  elements.trendModeButtons.forEach((button) => {
    button.addEventListener("click", () => setTrendMode(button.dataset.trendMode));
  });
  elements.detailTrendModeButtons.forEach((button) => {
    button.addEventListener("click", () => setDetailTrendMode(button.dataset.detailTrendMode));
  });
  elements.worldClocks.addEventListener("click", (event) => {
    const target = event.target instanceof Element ? event.target : event.target.parentElement;
    const card = target && target.closest("[data-clock-index]");
    if (!card) return;
    selectClock(card.dataset.clockIndex);
  });
  elements.worldClocks.addEventListener("keydown", (event) => {
    if (event.key !== "Enter" && event.key !== " ") return;
    const target = event.target instanceof Element ? event.target : event.target.parentElement;
    const card = target && target.closest("[data-clock-index]");
    if (!card) return;
    event.preventDefault();
    selectClock(card.dataset.clockIndex);
  });
  elements.refreshButton.addEventListener("click", refreshData);
  elements.detailClose.addEventListener("click", closeIndexDetail);
  elements.indicesBody.addEventListener("click", (event) => {
    const target = event.target instanceof Element ? event.target : event.target.parentElement;
    if (!target || target.closest("a, button")) return;
    const row = target.closest("[data-index-symbol]");
    if (row) openIndexDetail(row.dataset.indexSymbol);
  });
  elements.indicesBody.addEventListener("keydown", (event) => {
    if (event.key !== "Enter" && event.key !== " ") return;
    const target = event.target instanceof Element ? event.target : event.target.parentElement;
    const row = target && target.closest("[data-index-symbol]");
    if (!row) return;
    event.preventDefault();
    openIndexDetail(row.dataset.indexSymbol);
  });
  elements.detailChart.addEventListener("pointermove", handleChartPointerMove);
  elements.detailChart.addEventListener("pointerleave", hideChartTooltip);
  elements.baseCurrencySelect.addEventListener("change", (event) => {
    state.baseCurrency = event.target.value;
    writeCache(CACHE_KEYS.baseCurrency, state.baseCurrency);
    state.fx = rebaseFxSnapshot(state.fx || FALLBACK_FX, state.baseCurrency);
    renderAll();
    refreshData();
  });
  elements.amountInput.addEventListener("input", renderConverter);
  elements.fromCurrency.addEventListener("change", renderConverter);
  elements.toCurrency.addEventListener("change", renderConverter);

  elements.swapButton.addEventListener("click", () => {
    const currentFrom = elements.fromCurrency.value;
    elements.fromCurrency.value = elements.toCurrency.value;
    elements.toCurrency.value = currentFrom;
    renderConverter();
  });

  if (elements.regionHeatmap) {
    elements.regionHeatmap.addEventListener("click", (event) => {
      const target = event.target instanceof Element ? event.target : event.target.parentElement;
      const card = target && target.closest("[data-region-filter]");
      if (!card) return;
      const next = card.dataset.regionFilter;
      state.regionFilter = state.regionFilter === next ? "" : next;
      scheduleRender();
    });
  }

  if (elements.watchlistBody) {
    elements.watchlistBody.addEventListener("click", (event) => {
      const target = event.target instanceof Element ? event.target : event.target.parentElement;
      if (!target || target.closest("a, button")) return;
      const row = target.closest("[data-index-symbol]");
      if (row) openIndexDetail(row.dataset.indexSymbol);
    });
  }

  document.addEventListener("keydown", (event) => {
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {
      event.preventDefault();
      elements.searchInput?.focus();
    }
  });
}

function loadCachedState() {
  const cachedFx = readCache(CACHE_KEYS.fx);
  const cachedIndices = readCache(CACHE_KEYS.indices);
  const cachedTrends = readCache(CACHE_KEYS.trends);
  const cachedBaseCurrency = readCache(CACHE_KEYS.baseCurrency);
  const cachedTheme = readCache(CACHE_KEYS.theme);
  const cachedColorMode = readCache(CACHE_KEYS.colorMode);
  const cachedTrendMode = readCache(CACHE_KEYS.trendMode);
  if (REQUIRED_CURRENCY_CODES.includes(cachedBaseCurrency)) {
    state.baseCurrency = cachedBaseCurrency;
  }
  if (cachedTheme === "dark" || cachedTheme === "light") {
    state.theme = cachedTheme;
  }
  if (cachedColorMode === "red-up" || cachedColorMode === "green-up") {
    state.colorMode = cachedColorMode;
  }
  if (TREND_MODES.some((item) => item.key === cachedTrendMode)) {
    state.trendMode = cachedTrendMode;
    state.detailTrendMode = cachedTrendMode;
  }
  state.fx = cachedFx
    ? { ...rebaseFxSnapshot(cachedFx, state.baseCurrency), stale: true, source: `${cachedFx.source} 缓存` }
    : rebaseFxSnapshot(FALLBACK_FX, state.baseCurrency);
  const cachedLiveCount = Array.isArray(cachedIndices)
    ? cachedIndices.filter((item) => Number.isFinite(Number(item.price))).length
    : 0;
  state.indices = cachedLiveCount === INDEX_SYMBOLS.length
    ? cachedIndices.map((item) => ({ ...item, stale: true }))
    : [];
  if (cachedTrends && typeof cachedTrends === "object") {
    state.trends = {
      intraday: cachedTrends.intraday || {},
      daily: cachedTrends.daily || {},
      monthly: cachedTrends.monthly || {}
    };
  }
  const cachedBriefing = readCache(CACHE_KEYS.briefing);
  if (cachedBriefing) state.briefing = cachedBriefing;
}

async function loadMarketConfig() {
  const useBackend = location.protocol === "http:" || location.protocol === "https:";
  const sources = useBackend ? ["/api/config", "/market-config.json"] : ["/market-config.json"];

  for (const source of sources) {
    try {
      const config = await fetchJson(source, { timeout: 5000 });
      if (!config || !Array.isArray(config.currencies) || !Array.isArray(config.indexSymbols)) {
        throw new Error("Invalid market config payload");
      }
      CURRENCIES = config.currencies;
      INDEX_SYMBOLS = config.indexSymbols;
      REQUIRED_CURRENCY_CODES = Array.isArray(config.coreCurrencies)
        ? config.coreCurrencies
        : CURRENCIES.map((currency) => currency.code);
      AUTO_REFRESH_MS = Number(config.autoRefreshSeconds || 20) * 1000;
      if (config.fallbackFx) {
        FALLBACK_FX = { ...config.fallbackFx, stale: true };
      }
      if (elements.productTitle && config.productName) {
        elements.productTitle.textContent = config.productName;
        document.title = `${config.productName} · 全球行情读卡器`;
      }
      if (elements.productTagline && config.productTagline) {
        elements.productTagline.textContent = config.productTagline;
      }
      return;
    } catch (error) {
      console.warn(`Market config source failed: ${source}`, error);
    }
  }

  throw new Error("Unable to load market-config.json");
}

async function boot() {
  try {
    await loadMarketConfig();
  } catch (error) {
    console.error(error);
    renderStatus("市场配置加载失败，请确认 market-config.json 可访问。", "warn");
    return;
  }

  loadCachedState();
  applyTheme();
  applyColorMode();
  populateCurrencySelects();
  bindEvents();
  elements.autoRefreshLabel.textContent = `${AUTO_REFRESH_MS / 1000} 秒`;
  renderWorldClocks();
  initGlobe();
  setInterval(renderWorldClocks, 1000);
  renderAll();
  requestAnimationFrame(() => document.body.classList.add("ready"));
  refreshData();
  setInterval(refreshData, AUTO_REFRESH_MS);
}

boot();
