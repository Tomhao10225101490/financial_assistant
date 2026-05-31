# 金融小助手比赛版测试报告

## 测试目标

验证项目可以作为比赛演示产品稳定运行，重点覆盖：

- Python 后端是否可启动、可编译。
- 前端 JavaScript 是否无语法错误。
- 核心 API 是否返回兼容数据和比赛版诊断字段。
- 高精度地球资源是否可访问。
- 浏览器页面是否可渲染、可交互、不卡死。
- Cloudflare 公网演示脚本是否具备启动前检查。

## 静态检查

### 本轮实测摘要

已完成自动化检查：

- `server.py` Python 编译通过。
- `app.js` Node VM 语法解析通过。
- `/api/health`、`/api/fx?base=CNY`、`/api/indices`、`/api/trends?mode=intraday`、`/api/diagnostics` smoke test 通过。
- `/`、`/app.js?v=20260514-competition`、`/api/diagnostics` 均返回 `Cache-Control: no-store, max-age=0`。
- `world-land-10m.json` 可访问，资源大小约 3.09 MB。

浏览器交互验收需要本机服务保持运行后继续执行，验收项见下文。

### Python 编译检查

命令：

```powershell
.\.python\python.exe -m py_compile server.py
```

期望：

- 命令退出码为 `0`。
- 不输出 Python 语法错误。

### JavaScript 语法检查

使用 Node VM 解析 `app.js`。

期望：

- `app.js syntax ok`
- 无阻塞性语法错误。

## API Smoke Test

启动本地服务后访问：

```text
http://127.0.0.1:18765/api/health
http://127.0.0.1:18765/api/fx?base=CNY
http://127.0.0.1:18765/api/indices
http://127.0.0.1:18765/api/trends?mode=intraday
http://127.0.0.1:18765/api/diagnostics
```

验收要点：

- `/api/health` 返回 `version`、`fxSource`、`indicesLive`、`autoRefreshSeconds`。
- `/api/fx` 返回 `cacheState`、`quality`、`latencyMs`、`officialSourceUrl`、`beijingUpdatedAt`。
- `/api/indices` 每行返回 `quality`、`cacheState`、`latencyMs`、`sourceDetailUrl`。
- `/api/trends` 每条趋势返回 `quality`、`fallbackReason`、`marketTimeZone`、`beijingUpdatedAt`。
- `/api/diagnostics` 返回缓存状态、外部源状态和公网演示建议。

## 浏览器验收

页面：

```text
http://127.0.0.1:18765/
```

桌面验收：

- 顶部地球显示 `1:10m 高精度`。
- 地球非空白，陆地边界、海洋、城市光点和市场连线可见。
- 拖拽地球时中心不偏移，释放后有轻微惯性。
- 点击北京、纽约、伦敦、法兰克福、东京、香港光点，tooltip 显示实时读秒。
- 点击空白处取消选中。
- 汇率卡片显示官方展示链接和数据计算来源。
- 指数表格显示中文名、代码、价格、涨跌、图表、更新时间、质量标签和官方详情。
- 指数详情支持分时、日 K、月 K 切换。
- 暗色/浅色、红涨绿跌/绿涨红跌切换正常。

移动验收：

- 宽度 360px 到 430px 不出现横向页面溢出。
- 地球、时钟卡片、搜索、刷新按钮不重叠。
- 表格可横向滚动，页面主体仍可顺畅滚动。

## 公网访问验收

运行：

```text
公开访问金融小助手.bat
```

脚本应完成：

- 检查 `.python\python.exe`。
- 检查 `server.py`。
- 检查 `cloudflared.exe`。
- 检查 `world-land-10m.json`。
- 启动或复用本地服务。
- 请求 `/api/diagnostics`。
- 请求 `/world-land-10m.json?v=competition` 并确认资源体积足够。
- 输出 `https://xxxx.trycloudflare.com`。

公网验收：

- 通过公网链接打开首页。
- 页面资源不使用旧缓存。
- 地球仍显示高精度版本。
- `/api/diagnostics` 可公网访问。

## 已知限制

- 免费公开金融数据源可能延迟或临时不可用。
- Cloudflare Quick Tunnel 是临时链接，不适合长期生产部署。
- 本项目无鉴权，不应暴露敏感数据或长期公开运行。
- 指数图表对部分海外指数可能使用区间兜底，页面会明确标注。

## 比赛演示建议

推荐演示顺序：

1. 打开首页，展示全球市场时钟和 1:10m 高精度地球。
2. 拖拽地球，点击不同市场光点。
3. 切换暗色/浅色和红涨绿跌习惯。
4. 切换基础货币，点击汇率官方链接。
5. 打开指数详情，切换分时、日 K、月 K。
6. 打开 `/api/diagnostics`，展示数据源监控和缓存策略。
7. 运行公网脚本，生成链接让其他设备访问。
