# 金融小助手（比赛版）

一个面向比赛演示的金融数据看板，提供 **汇率、换汇计算、全球主要指数、分时/日K/月K图表、世界市场时钟、交互式高精度地球、数据源诊断、零成本公网访问**。

项目采用 **Python 标准库后端 + 原生 HTML/CSS/JavaScript 前端**，无需 npm、无需数据库、无需付费 API，适合在 Windows 电脑上快速启动并通过 Cloudflare 临时链接分享给评委或同学。

## 核心亮点

- **比赛级交付**：本地运行，Cloudflare Quick Tunnel 一键生成公网链接。
- **高精度地球**：使用 Natural Earth 1:10m 地理数据，市场城市光点可点击、可拖拽旋转、实时读秒。
- **数据可信度可见**：每条汇率、指数和趋势数据都标注来源、缓存状态、质量标签和更新时间。
- **图表完整**：全球指数支持分时、日 K、月 K，并可打开详情大图。
- **用户体验完整**：暗色/浅色模式、红涨绿跌/绿涨红跌习惯、快速搜索、手动刷新、20 秒自动刷新。
- **高容错**：公开数据源失败时使用缓存或兜底，不让页面空白。

## 快速启动

### 本地访问

双击：

```text
启动金融小助手.bat
```

然后访问：

```text
http://127.0.0.1:18765
```

也可以用命令行启动：

```powershell
powershell -ExecutionPolicy Bypass -File .\run.ps1
```

### 公网访问

双击：

```text
公开访问金融小助手.bat
```

终端出现类似下面的链接后，把它发给别人：

```text
https://xxxx.trycloudflare.com
```

注意：电脑、本地服务窗口、Cloudflare 窗口和网络都必须保持运行，关闭后公网链接失效。

## 推荐比赛演示路径

1. 展示顶部 3D 地球，拖拽旋转并点击市场光点。
2. 展示实时跳动的北京、纽约、伦敦、法兰克福、东京、香港时钟。
3. 切换暗色/浅色和红涨绿跌习惯。
4. 切换基础货币，点击汇率卡片打开官方汇率展示页。
5. 打开指数详情，切换分时、日 K、月 K。
6. 打开 `/api/diagnostics`，展示数据源、缓存、版本和公网演示状态。
7. 启动公网脚本，让其他设备访问同一个产品。

## API

```text
GET /api/fx?base=CNY
GET /api/indices
GET /api/trends?mode=intraday
GET /api/health
GET /api/diagnostics
```

比赛版新增字段包括：

- `cacheState`：`live`、`fresh`、`stale`、`fallback`
- `quality`：`real`、`delayed`、`cache`、`fallback`、`unavailable`
- `latencyMs`：接口耗时
- `beijingUpdatedAt`：北京时间
- `sourceDetailUrl` / `officialSourceUrl`：权威参考入口

## 项目结构

```text
financialAssistant/
├─ index.html                    # 页面结构
├─ styles.css                    # UI、动画、响应式样式
├─ app.js                        # 前端交互、图表、地球、状态管理
├─ server.py                     # Python 本地 API 和数据聚合
├─ world-land-10m.json           # Natural Earth 1:10m 高精度地球数据
├─ run.bat                       # 本地启动
├─ run.ps1                       # PowerShell 启动
├─ 启动金融小助手.bat             # 中文本地启动入口
├─ 公开访问金融小助手.bat         # Cloudflare 临时公网访问
├─ TECHNICAL_DESIGN.md           # 详细技术设计文档
└─ TEST_REPORT.md                # 测试报告和验收清单
```

## 数据源说明

汇率：

- Frankfurter
- Currency API CDN
- Currency API Cloudflare
- 最近成功缓存
- 内置参考兜底

指数：

- Sina Finance
- Stooq
- Yahoo Finance Chart
- 最近成功缓存
- 报价区间兜底

免费公开源可能存在延迟、限流或不可用，因此页面会显示数据质量，不把兜底数据伪装为交易级实时行情。

## 技术文档

详细设计请阅读：

```text
TECHNICAL_DESIGN.md
```

测试和验收请阅读：

```text
TEST_REPORT.md
```

## 免责声明

本项目仅用于比赛演示、学习和信息参考，不构成投资、交易、换汇或资产配置建议。免费公开数据源可能存在延迟或误差，请勿基于本工具直接做出交易决策。
