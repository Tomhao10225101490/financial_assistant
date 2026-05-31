# -*- coding: utf-8 -*-
"""Generate competition materials for the Financial Assistant project.

The script deliberately uses only Python's standard library so it works with the
portable Python bundled in this project. It keeps the reference files intact and
creates a new set of files under 比赛文件/.
"""

from __future__ import annotations

import html
import re
import textwrap
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
COMP = ROOT / "比赛文件"
ASSETS = COMP / "金融小助手_图文素材"
TEMPLATE_PPTX = COMP / "钟于钢琴工作室教学管理小程序_双创展示PPT.pptx"
TEMPLATE_FORM = COMP / "第十一届创新创业大赛作品赛作品情况表_钟于钢琴.docx"

TEAM_SECTION = (
    "史健申：组长，负责项目统筹、需求抽象、数据可信度测试、公开访问验证、路演表达与演示路径统筹；\n"
    "钟浩：组员，负责产品设计、Python 后端接口、数据源适配、前端核心交互、3D 可视化与最终工程交付；\n"
    "曹桂涛老师：指导老师，负责技术路线指导、架构与创新性把关、项目规范指导。"
)


def clean(text: str) -> str:
    text = text.replace("**", "").replace("`", "")
    return text


def wrap(s: str) -> str:
    return textwrap.dedent(s).strip() + "\n"


SPEAKER_MD = wrap(
    """
    # 金融小助手 双创展示PPT讲稿

    建议时长：5-6 分钟。讲述时保持节奏稳定，重点突出“全球数据、真实可用、可信兜底、零成本公开访问、交互体验前沿”。本项目不是静态展示页，而是一个可现场启动、可公网访问、可切换数据与图表模式的本地金融数据终端。

    ![产品总览](金融小助手_图文素材/product-overview.svg)

    ## 第 1 页：封面

    各位老师好，我们展示的项目是“金融小助手”。它是一个面向普通用户和金融学习者的全球市场看板，用最轻的本地 Python 服务和原生前端，实现汇率、换汇计算、全球指数、趋势图表、市场时钟、3D 交互地球和公开访问演示。我们的目标不是做一个昂贵的交易终端，而是用第一性原理拆解金融数据看板：用户真正需要的是快、准、清楚、可信、随手可访问。

    ## 第 2 页：目录

    接下来我会从团队分工、项目背景、产品方案、核心展示、技术架构、数据可信度、体验创新和比赛演示路径七个方面展开。整体逻辑是：先说明为什么需要这个工具，再说明我们如何把免费公开数据源、缓存兜底、图表交互和公网演示组合成一个可运行产品，最后说明它为什么有继续扩展成金融学习与市场观察平台的价值。

    ## 第 3 页：团队成员

    我们团队分工保持不变，但组长调整为史健申。史健申负责项目统筹、需求抽象、数据可信度测试、公开访问验证、路演表达与演示路径统筹；钟浩负责产品设计、Python 后端接口、数据源适配、前端核心交互、3D 可视化与最终工程交付；曹桂涛老师负责技术路线指导、架构与创新性把关、项目规范指导。团队推进原则是：每一个功能都要能跑通，每一个数据源都要有来源说明，每一个展示点都能在现场打开验证。

    ## 第 4 页：项目背景

    普通用户看金融市场时常遇到三个问题。第一，信息散：汇率在一个网站，指数在另一个网站，市场时间又要自己换算。第二，可信度不清：免费数据可能延迟，但很多页面不会告诉用户数据质量。第三，部署门槛高：很多项目只能在开发机上看，评委和其他同学无法直接访问。我们的项目把这些问题收敛成一个本地可运行、零成本可公开、数据质量明确标注的金融小助手。

    ## 第 5 页：产品主界面

    主界面采用高密度金融控制台风格。顶部是全球主流市场时钟和可交互地球，中间是状态、更新时间、自动刷新和搜索控制，核心区包括汇率、换汇计算、全球指数和趋势图。它不是营销式首页，而是打开后就能使用的工作台。用户可以快速搜索货币或指数，切换暗色和浅色主题，也可以按中西方习惯切换红涨绿跌或绿涨红跌。

    ## 第 6 页：汇率与换汇计算

    汇率模块支持 USD、CNY、EUR、JPY、GBP、HKD、AUD、CAD、CHF、SGD、KRW、INR 等常用货币。用户可以选择任意基础货币，系统会按最新可用汇率刷新卡片和换汇计算。内部保留完整数值，展示时采用高精度自适应格式，避免小额汇率被粗暴四舍五入。点击任意汇率卡片，不是跳到 API 网站，而是跳到中国银行、ECB 或相关央行等官方展示页面，数值来源和官方展示页面在 UI 上分开说明。

    ## 第 7 页：全球指数与三模式图表

    指数模块覆盖美股三大、欧洲主要指数、日经、恒生、上证和沪深 300 等样本。每个指数展示中文名、英文名、代码、最新点位、涨跌、涨跌幅、市场时间、北京时间和数据质量。趋势图支持分时、日 K、月 K 三种模式，顶部可以全局切换，点击指数行可以打开详情大图。涨跌幅坚持使用同源字段，不用错误基准自行推算，拿不到真实 K 线时会明确标注“缓存、延迟或兜底”，避免误导。

    ## 第 8 页：3D 交互地球时钟

    这是项目的视觉亮点。全球主流时钟不再只是静态卡片，而是一个可拖拽旋转的 3D 地球。地球中心固定，用户可以拖拽旋转，主要市场城市以高亮光点显示。点击光点会出现城市、市场、时区、日期和实时跳动时间；点击空白处取消选中；点击下方时钟卡片也会联动选中地球上的对应光点。地球优先加载 Natural Earth 1:10m 高精度边界，配合海洋、陆地、海岸线、市场弧线、星空和气辉效果，暗色和浅色模式分别优化可读性。

    ## 第 9 页：系统总体架构

    技术上，我们没有引入重型框架。后端采用 Python 标准库实现本地 HTTP 服务，提供 /api/fx、/api/indices、/api/trends、/api/health 和 /api/diagnostics。前端采用原生 HTML、CSS、JavaScript 和本地 vendor 化的 Three.js。数据层把 Frankfurter、Sina Finance、Stooq、Yahoo 等免费公开源封装为适配器，前端只消费统一结构，降低页面逻辑复杂度。

    ```mermaid
    flowchart LR
      用户浏览器 --> 前端[原生 HTML/CSS/JS]
      前端 --> API[Python 本地服务]
      API --> FX[汇率适配器]
      API --> IDX[指数适配器]
      API --> TREND[趋势适配器]
      API --> CACHE[分层缓存与诊断]
      FX --> PUBLIC[免费公开数据源]
      IDX --> PUBLIC
      TREND --> PUBLIC
    ```

    ## 第 10 页：缓存、诊断与稳定性

    为了避免 20 秒自动刷新造成请求风暴，后端做了分层缓存和 stale-while-revalidate 思路。汇率和指数使用短缓存，图表趋势使用更长缓存；连续失败时保留最近成功数据并标注缓存状态。新增 /api/diagnostics 可以展示数据源最近成功时间、失败原因、缓存年龄和接口耗时。这个接口不是给普通用户看的花活，而是比赛和调试时证明系统可观测、可解释、可排障的关键能力。

    ## 第 11 页：体验与动画设计

    前端体验遵循“快、清楚、少干扰”的原则。动画主要使用 transform、opacity、requestAnimationFrame 和 SVG 过渡，保证主题切换、卡片刷新、图表切换、地球旋转和详情展开都比较丝滑。页面尊重 prefers-reduced-motion，移动端会控制地球高度和表格滚动，避免元素重叠。暗色模式突出科技感，浅色模式强调阅读和展示，红绿涨跌偏好让不同文化习惯的用户都能快速理解行情。

    ## 第 12 页：数据可信度与边界

    金融产品最重要的是不能装作自己比数据源更权威。我们使用免费公开数据源，因此明确标注“实时、延迟、缓存、兜底”等质量状态，并在页面保留免责说明：数据仅用于学习和市场观察，不构成投资建议。指数详情和汇率卡片都提供来源跳转，CNY 相关汇率优先跳中国银行外汇牌价，国际参考汇率跳 ECB 或相关央行页面，指数跳到官方或可信来源详情页。

    ## 第 13 页：创新价值

    项目的创新不是单点炫技，而是把多个真实约束合在一起解决。第一，零付费 API 条件下仍然提供可用的全球市场看板；第二，数据质量在界面上显式表达，不混淆真实数据和兜底数据；第三，用 3D 地球把市场时间和空间位置结合起来，降低跨时区理解成本；第四，本地运行加 Cloudflare Quick Tunnel，使作品能够以 0 成本快速公开演示；第五，诊断接口和缓存策略让项目从“能看”升级为“能解释为什么这样显示”。

    ## 第 14 页：进度与计划

    目前项目已经完成本地服务、汇率、换汇计算、全球指数、趋势图三模式、暗浅主题、红绿偏好、搜索、20 秒自动刷新、3D 地球、官方来源跳转、诊断接口和公开访问脚本。短期计划是继续补充更多稳定指数源、增加更多市场和商品品类；中期可以加入自选列表、历史对比、风险提示和学习卡片；长期可以演进为面向金融学习场景的轻量市场实验室。

    ## 第 15 页：展示路径

    现场展示可以按五条线展开。第一，打开首页展示地球和市场时钟，拖拽并点击光点。第二，切换主题和红绿习惯，证明交互偏好可配置。第三，切换基础货币并做换汇计算，点击卡片进入官方展示页。第四，查看全球指数，切换分时、日 K、月 K，并打开详情图。第五，访问 /api/diagnostics，说明数据源、缓存、耗时和失败兜底都可观测。最后用公开访问脚本生成 trycloudflare.com 链接，让其他人直接打开体验。

    ## 第 16 页：致谢

    以上就是我们的项目展示。用一句话总结：金融小助手用最低成本做出一个可运行、可公开、可解释、可交互的全球市场控制台。它不把免费数据包装成交易级终端，而是把数据来源、质量状态、跨时区时间、趋势图和公开访问都摆到用户面前，让普通用户真正看得懂、用得上、查得到来源。谢谢各位老师。
    """
)


QA_ITEMS = [
    ("你们这个项目一句话解决什么问题？", "金融小助手解决的是普通用户看全球市场时“信息分散、时间难换算、来源不清楚、演示不容易公开”的问题。它把汇率、换汇计算、全球指数、趋势图、市场时钟和数据质量说明放到一个本地可运行的控制台里，并能通过 Cloudflare 临时公网链接让别人直接访问。", "它不是交易软件，而是市场观察和金融学习工具；我们把边界说清楚，数据仅用于学习和展示，不构成投资建议。"),
    ("为什么选择金融市场看板这个方向？", "汇率和指数是最容易被普通用户接触、也最容易产生跨网站查询成本的金融信息。这个方向既能体现实时数据处理、可视化、缓存和异常兜底，也适合比赛现场演示，因为评委能立刻看懂功能是否真的跑通。", "我们先聚焦汇率和主要指数，后续可以扩展商品、债券、基金和自选组合。"),
    ("项目和普通网页行情页相比有什么不同？", "普通行情页通常只展示一类数据，而我们把跨时区时钟、3D 地球、汇率、官方来源跳转、指数图表、数据质量标签和诊断接口组合成完整体验。更重要的是，项目可本地运行、可公网临时分享，适合教学、展示和轻量市场观察。", "差异点不是信息堆叠，而是把数据可信度、交互和部署方式一起做成闭环。"),
    ("为什么强调 0 成本公开访问？", "比赛和真实展示时，最怕作品只能在开发机上看。我们通过本地 Python 服务加 Cloudflare Quick Tunnel，让作品不买服务器、不买域名也能生成公网访问链接。只要电脑和网络不断开，别人就能通过链接体验产品。", "这不是长期商业部署方案，而是最快、最低成本、最适合比赛现场的展示方案。"),
    ("你们如何证明不是静态网页？", "页面数据由 Python 后端接口动态提供，包含 /api/fx、/api/indices、/api/trends、/api/diagnostics 等接口。前端会自动刷新、切换基础货币、请求趋势图数据、更新世界时钟读秒，并支持 3D 地球交互。", "如果断网或数据源失败，页面会显示缓存或兜底状态，这也说明它有真实数据链路。"),
    ("团队成员具体分工是什么？", "史健申作为组长，负责项目统筹、需求抽象、数据可信度测试、公开访问验证、路演表达与演示路径统筹；钟浩负责产品设计、Python 后端接口、数据源适配、前端核心交互、3D 可视化与最终工程交付；曹桂涛老师负责技术路线指导、架构与创新性把关、项目规范指导。", "分工覆盖了需求、实现、测试、展示和指导，不是只做页面包装。"),
    ("指导老师在项目中起到什么作用？", "指导老师主要帮助我们把作品从一个可运行工具提升为结构清晰、创新点明确、边界严谨的参赛项目。她关注技术路线是否合理、材料表达是否规范、项目价值是否能被评委理解。", "核心实现由学生团队完成，指导老师负责方向和规范把关。"),
    ("为什么不用 React、Vue 这类框架？", "本项目的第一目标是本地启动快、交付可靠、评委无需安装复杂环境。原生 HTML/CSS/JS 足够完成交互，而且减少构建步骤和依赖风险。Three.js 作为 3D 渲染库被本地 vendor 化，避免 CDN 不稳定。", "这不是排斥框架，而是在这个场景下选择最稳、最轻的技术路径。"),
    ("后端为什么用 Python 标准库？", "用户机器上 node/npm 不稳定，而项目已经有 portable Python。用 Python 标准库实现 HTTP 服务可以减少安装依赖，双击 bat 就能启动。后端承担数据源适配、缓存、诊断和静态资源服务，职责清晰。", "如果未来规模扩大，可以平滑迁移到 FastAPI 或 Flask，但比赛版不依赖它们。"),
    ("你们有哪些 API？", "核心 API 包括 /api/fx 获取汇率，/api/indices 获取指数，/api/trends 获取分时、日 K、月 K 趋势，/api/health 做健康检查，/api/diagnostics 输出数据源状态、缓存年龄、接口耗时和失败原因。", "这些接口使前端不是写死数据，而是消费统一的后端数据结构。"),
    ("汇率数据来源是什么？", "汇率数值主要来自 Frankfurter 等免费公开源，页面同时把官方展示入口和 API 数据来源分开说明。CNY 相关货币对点击后跳中国银行外汇牌价，国际参考汇率跳 ECB 或相关央行页面。", "API 用来计算，官方页面用来核验和展示，两者在 UI 上不混淆。"),
    ("为什么汇率点击不直接跳 API？", "普通用户点击卡片希望看到权威解释，而不是开发者 API 文档。因此我们新增官方跳转逻辑：涉及人民币的跳中国银行，欧元参考汇率跳 ECB，其它货币尽量跳央行或监管机构页面。", "这提升了可信度，也符合金融信息产品应该尊重权威来源的原则。"),
    ("指数数据来源是什么？", "指数模块采用 Sina Finance、Stooq、Yahoo 等公开源的适配器组合。不同市场的数据稳定性不同，所以页面会显示实时、延迟、缓存或兜底等质量标签，并提供来源链接。", "我们不使用 ETF 或相近资产冒充指数，拿不到真实 K 线会明确提示。"),
    ("如何保证涨跌幅不算错？", "我们在后端约束：指数涨跌和涨跌幅优先使用数据源返回的同源字段，不用错误基准自行推算。早期版本发现过上证等指数点位对但涨跌幅不一致的问题，后续已按同源字段原则修正。", "当来源没有可靠涨跌幅时，页面宁愿标注质量问题，也不伪造精确结果。"),
    ("免费数据源会不会不可靠？", "会有短时不可用或延迟，这正是我们设计数据质量标签、缓存和诊断接口的原因。系统不会假装免费源有交易级 SLA，而是把最近成功时间、失败原因和缓存状态展示出来。", "项目价值在于真实面对限制，而不是隐藏限制。"),
    ("缓存策略是什么？", "后端对汇率、指数和趋势做分层缓存。汇率和指数是短缓存，适合 20 秒刷新；趋势图缓存更长，避免频繁请求历史数据。同一刷新周期尽量复用结果，连续失败时保留最近成功数据。", "这样能减少请求风暴，也能在网络抖动时保持页面可用。"),
    ("什么是 stale-while-revalidate 思路？", "意思是当缓存还可用或刚过期时，先把旧数据给用户看，再在后台或下一次请求中刷新。用户不会因为某个源短暂卡住而看到整页崩掉。", "我们在本地 Python 服务中用轻量方式实现这一思想，而不是引入复杂缓存中间件。"),
    ("诊断接口有什么意义？", "/api/diagnostics 可以显示服务版本、缓存状态、数据源最近成功和失败、接口耗时、公开演示建议等。比赛现场如果老师问数据是否真能跑，我们可以直接打开诊断接口验证。", "它把系统内部状态透明化，是工程可信度的一部分。"),
    ("3D 地球的技术实现是什么？", "地球使用本地 vendor 化 Three.js 渲染，城市光点根据经纬度贴在球体表面，拖拽通过旋转 globe group 实现，点击用 Raycaster 做拾取，tooltip 每秒与世界时钟共用时间格式化逻辑更新。", "页面隐藏时减少渲染，移动端控制画布高度，保证体验稳定。"),
    ("为什么要做 3D 地球？", "金融市场天然和时区、地理位置有关。只展示文字时钟很难形成空间感，而 3D 地球能让北京、纽约、伦敦、法兰克福、东京、香港这些市场位置和时间建立联系。", "它不是装饰，而是把跨时区理解成本降下来。"),
    ("地球精度如何处理？", "比赛版优先加载 Natural Earth 1:10m 边界数据，避免使用随手画的低精度板块。加载前不会展示旧低精度轮廓，失败时才进入可说明的 fallback 状态。", "我们承认浏览器里不可能做到地球物理级 1:1，但在前端可交互展示中采用了公开高精度边界数据。"),
    ("点击空白取消选中是怎么做的？", "地球点击事件会先用 Raycaster 判断是否命中市场光点，如果没有命中，就清空 selectedClockIndex 并隐藏 tooltip，同时更新状态标签为未选中。", "这个细节能让交互符合用户直觉。"),
    ("图表为什么要支持分时、日 K、月 K？", "不同用户的问题不一样。分时看当天波动，日 K 看近期趋势，月 K 看长期方向。全局切换可以快速比较所有指数，点击单个指数进入详情可以看大图。", "对拿不到稳定 K 线的数据，页面会标注兜底原因。"),
    ("图表是用什么库做的？", "核心图表使用原生 SVG/Canvas 思路实现，没有引入重型图表框架。这样启动快、体积小，也方便根据数据质量显示不同标识。", "如果未来要做更复杂指标，可以考虑引入 ECharts 或 TradingView Lightweight Charts。"),
    ("暗色和浅色模式为什么重要？", "金融看板常常需要长时间查看，暗色模式有科技感并降低眩光，浅色模式适合汇报和阅读。我们把主题切换做成用户偏好，并让地球、图表、卡片和涨跌颜色一起适配。", "主题不是换背景色，而是完整视觉系统。"),
    ("为什么支持红涨绿跌和绿涨红跌？", "中国用户习惯红涨绿跌，很多海外市场习惯绿涨红跌。金融工具如果只支持一种习惯，会增加理解成本。我们允许用户切换，并把偏好应用到指数、汇率和图表。", "这是尊重用户认知习惯的细节。"),
    ("搜索功能覆盖什么？", "搜索可以按货币、指数、代码和中文名过滤内容。用户不需要滚动查找某个市场，直接输入 USD、上证、Nasdaq 或 CNY 就能定位。", "对高密度看板来说，搜索是核心效率功能。"),
    ("自动刷新为什么是 20 秒？", "早期是 60 秒，后来根据使用反馈改成 20 秒。20 秒在演示和准实时观察中更有反馈感，同时通过缓存和请求合并避免造成数据源压力。", "免费数据源本身可能延迟，所以刷新频率不是承诺交易级实时。"),
    ("如何避免请求风暴？", "前端合并同一轮刷新中的请求，后端使用缓存和超时控制，趋势图缓存时间更长，失败时不无限重试。这样即使页面自动刷新，也不会每 20 秒对每个外部源发大量请求。", "服务端日志也会避免把客户端中断当成严重错误堆栈刷屏。"),
    ("公开访问脚本做了什么？", "公开访问金融小助手.bat 会先启动本地 Python 服务，再拉起 Cloudflare Quick Tunnel，终端里出现 trycloudflare.com 链接后，把链接发给别人即可访问。", "窗口、电脑和网络必须保持运行，关闭后链接失效。"),
    ("为什么别人可能看到旧地球？", "浏览器或公网边缘可能缓存旧的 app.js、CSS 或地球数据。比赛版增加资源版本号和 no-store 缓存头，并明确检查 world-land-10m.json 是否能通过公网加载。", "如果仍异常，可以让对方强制刷新或重新生成公网链接。"),
    ("安全边界是什么？", "项目不做登录，不保存隐私，不收集用户数据。公网访问只是把本机演示服务临时暴露出去，适合比赛展示，不适合作为长期生产服务。", "如果长期上线，需要正式服务器、HTTPS 域名、访问控制和审计。"),
    ("为什么没有接付费行情 API？", "比赛版目标是 0 成本、可复现、快速交付。付费 API 会提高门槛，也会让评委难以复现。我们选择免费公开源并明确标注数据质量。", "商业化版本可以接入合规付费源提升实时性和 SLA。"),
    ("项目最大的技术难点是什么？", "难点不在单个页面，而在多个约束同时成立：免费数据源不稳定、本地无 node/npm、要公网演示、要高交互体验、还要不误导用户。我们通过 Python 标准库、原生前端、缓存、诊断和数据质量标签把这些约束统一起来。", "这体现的是工程整合能力。"),
    ("项目有哪些创新点？", "一是零成本可公开的金融数据终端；二是数据质量可视化和诊断接口；三是 3D 地球与市场时钟联动；四是红绿习惯和主题双偏好；五是汇率官方来源跳转和 API 数据来源分离。", "创新点都能在现场点开验证。"),
    ("相比商业金融终端差距在哪里？", "商业终端有付费实时数据、专业指标、交易接口和合规服务，我们当前没有这些。我们的定位是学习、展示和轻量观察，不替代交易终端。", "承认边界能让项目更可信。"),
    ("如果数据源全部不可用怎么办？", "页面会显示错误、缓存或不可用状态，/api/diagnostics 会记录失败原因。汇率和指数尽量使用最近成功缓存，趋势图无法获取时会显示明确兜底说明。", "不会用假数据冒充实时数据。"),
    ("项目是否支持移动端？", "支持。布局会在窄屏下调整，地球高度固定，卡片和表格避免横向溢出，触控可拖拽地球和查看图表 tooltip。", "移动端是金融信息快速查看的重要场景。"),
    ("性能优化做了哪些？", "前端动画优先使用 transform 和 opacity，地球用 requestAnimationFrame，页面隐藏时减少渲染；后端用缓存、超时和请求合并减少等待；资源本地化避免 CDN 失败。", "这些优化保证比赛现场操作更流畅。"),
    ("为什么说项目可维护？", "后端数据源被封装为适配器，API 输出统一结构；前端渲染按模块分为汇率、指数、趋势、地球、偏好；诊断接口能看到数据源状态。", "后续换数据源或增加品类不需要重写整页。"),
    ("作品安装方式是什么？", "双击启动金融小助手.bat 即可本地启动；浏览器访问 http://127.0.0.1:18765。公开演示时双击公开访问金融小助手.bat，等待 trycloudflare.com 链接出现。", "不要求评委安装 node/npm 或数据库。"),
    ("演示时最推荐展示哪几步？", "先拖拽 3D 地球并点击城市光点，再切换主题和红绿习惯；然后切基础货币、点汇率官方来源；接着查看指数和图表三模式；最后打开 diagnostics 说明系统可信度。", "这条路径能覆盖视觉、数据、交互和工程能力。"),
    ("项目现在有哪些已知限制？", "免费数据源可能延迟或短时不可用；Cloudflare 临时链接关闭后失效；当前没有用户账号和自选组合；图表指标还比较轻量。", "这些限制不会影响比赛版演示，但未来产品化需要继续增强。"),
    ("未来如何商业化？", "可以向金融学习社群、财经课程、校园社团和小型研究团队提供轻量看板；商业路径包括自选组合、学习卡片、数据报告、私有化部署和合规数据源接入。", "前提是明确非投顾边界，并接入更可靠的数据服务。"),
    ("如果要长期上线怎么做？", "需要把临时公网链接换成正式云服务器和域名，加入访问控制、日志审计、HTTPS、稳定数据源和错误监控。Python 标准库服务可以升级为 FastAPI，前端仍可复用。", "比赛版已经把模块边界打好。"),
    ("这个项目为什么适合创新创业比赛？", "它有真实需求、可运行产品、技术亮点、成本优势和明确边界。评委不只听概念，可以现场访问、点击、刷新、看诊断接口，验证它确实是一个完整系统。", "可展示性和工程可信度是它的竞争力。"),
    ("如果评委质疑数据不是交易级实时，怎么回答？", "我们会直接承认：比赛版使用免费公开源，不承诺交易级实时，也不提供投资建议。我们的价值是把数据源、质量状态、缓存和官方跳转透明呈现。", "不夸大数据能力，反而体现了金融产品应有的严谨。"),
    ("如果评委问为什么不用数据库？", "当前数据主要是实时查询和短期缓存，不需要持久化用户数据。用内存缓存和本地 JSON/静态资源就能满足比赛版目标，减少部署负担。", "未来加入自选组合、用户偏好云同步时可以引入 SQLite 或 PostgreSQL。"),
    ("如果网络断了还能用吗？", "本地页面和已有缓存可以显示，但外部行情无法更新，页面会标注缓存或不可用。公开访问链接也依赖电脑网络，因此网络断开后别人无法访问。", "这是零成本临时公网方案的自然边界。"),
    ("项目中最能体现第一性原理的地方是什么？", "我们把金融看板拆成最基本需求：用户要看什么、数据从哪里来、什么时候更新、可信度如何、打不开时怎么办、如何让别人访问。每个功能都围绕这些问题做取舍，而不是堆砌框架。", "这也是项目从静态网页升级成完整产品的主线。"),
    ("如果给你们更多时间，会优先做什么？", "第一接入更稳定的合规数据源；第二加入自选市场和提醒；第三增强图表指标和对比能力；第四把公网演示升级为正式部署；第五补充自动化浏览器测试和性能面板。", "这些方向都基于现有架构自然扩展。"),
]


def build_qa_md() -> str:
    sections = [
        (1, 5, "一、项目定位与需求价值"),
        (6, 8, "二、团队与分工"),
        (9, 18, "三、数据、后端与 API 可信度"),
        (19, 29, "四、前端体验、图表与 3D 地球"),
        (30, 41, "五、部署、安全与公开访问"),
        (42, 50, "六、创新创业价值与未来规划"),
    ]
    lines = [
        "# 金融小助手 答辩 Q&A 50 题",
        "",
        "使用建议：回答时先给结论，再给依据，最后落到项目取舍。遇到老师追问局限，先承认边界，再说明当前阶段为什么这样做合理，以及下一步如何增强。",
        "",
        "![系统架构](金融小助手_图文素材/architecture.svg)",
        "",
    ]
    for start, end, title in sections:
        lines.append(f"## {title}")
        lines.append("")
        for idx in range(start, end + 1):
            q, answer, follow = QA_ITEMS[idx - 1]
            lines.append(f"### {idx:02d}. 老师可能问：{q}")
            lines.append("")
            lines.append("**回答：**  ")
            lines.append(answer)
            lines.append("")
            lines.append("**追问：**  ")
            lines.append(follow)
            lines.append("")
    return "\n".join(lines).strip() + "\n"


QA_MD = build_qa_md()


SITUATION_MD = wrap(
    f"""
    # 第十一届创新创业大赛作品赛作品情况表：金融小助手

    ## 作品名称

    金融小助手：零成本公开访问的全球金融市场数据控制台

    ## 作者信息

    组长：史健申。参赛队员保持为史健申、钟浩，指导老师为曹桂涛。

    | 角色 | 院系 | 姓名 | 学号 | 信箱 | 电话 |
    | --- | --- | --- | --- | --- | --- |
    | 作者一 | 软件工程 | 史健申 | 10235101561 | 18130570903@163.com | 18130570903 |
    | 作者二 | 软件工程 | 钟浩 | 10225101490 | 2177686531@qq.com | 19279985142 |

    ## 指导教师

    曹桂涛，华东师范大学软件工程学院，021-62232557，gtcao@sei.ecnu.edu.cn

    ## 作品简介（约 200 字）

    金融小助手面向普通用户、金融学习者和比赛展示场景，解决汇率、全球指数、跨时区市场时间和数据来源分散的问题。作品采用本地 Python 标准库后端与原生前端实现，提供汇率、换汇计算、全球主要指数、分时/日K/月K趋势图、3D 交互地球时钟、暗浅主题和红绿涨跌偏好。后端统一封装免费公开数据源，提供缓存、超时、失败兜底和 /api/diagnostics 诊断接口；前端明确展示实时、延迟、缓存、兜底等数据质量，并为汇率和指数提供官方来源跳转。作品支持双击本地启动，也可通过 Cloudflare Quick Tunnel 生成 0 成本公网链接，适合现场演示和快速分享。

    ## 作品安装说明

    1. 在 Windows 环境进入项目目录，双击“启动金融小助手.bat”，或运行 `.\\.python\\python.exe server.py`。
    2. 终端出现 `http://127.0.0.1:18765` 后，用现代浏览器打开该地址。
    3. 若需要让其他人访问，双击“公开访问金融小助手.bat”，等待终端打印 `https://xxxx.trycloudflare.com`，把该链接发给评委或同学。
    4. 公网链接依赖本机、网络、本地服务和 Cloudflare 窗口持续运行；关闭窗口或断网后链接失效。
    5. 推荐使用支持 WebGL 的新版 Chrome、Edge 或 Firefox，以获得 3D 地球和图表的完整体验。

    ## 作品效果图与关键视觉

    ![产品总览](金融小助手_图文素材/product-overview.svg)

    ![3D地球交互](金融小助手_图文素材/globe-interaction.svg)

    ![数据流与缓存](金融小助手_图文素材/data-flow.svg)

    ## 设计思路（可附图）

    金融信息工具的核心不是把数字堆到页面上，而是回答用户最关心的几个问题：现在主要货币的汇率是多少，全球指数正在怎样变化，这个时间到底对应哪个市场，数据从哪里来，是否可靠，别人能不能直接访问我的作品。金融小助手从这些第一性问题出发，选择了“本地快速运行 + 免费公开数据源 + 明确质量标注 + 零成本公网演示”的路线。

    产品层面，页面不是传统宣传首页，而是打开即可使用的金融控制台。顶部的全球主流市场时钟结合 3D 地球，把北京、纽约、伦敦、法兰克福、东京、香港等市场与真实时区联系起来。用户可以拖拽旋转地球，点击市场光点查看城市、市场、时区、日期和实时读秒时间；点击空白处取消选中；点击时钟卡片也会联动地球。这一设计把跨时区理解从文字换算变成空间交互，既有展示冲击力，也有实际使用价值。

    汇率模块围绕“计算”和“核验”两条线设计。系统使用 Frankfurter 等免费公开源获取汇率数值，内部保留完整精度，前端根据货币和数量级自适应显示小数，避免小额汇率显示失真。用户点击汇率卡片时，页面不会跳转到 API 文档，而是优先打开中国银行外汇牌价、ECB 欧元参考汇率或相关央行页面。这样既保留了自动计算能力，又尊重金融数据应有的权威来源核验路径。

    指数模块强调“同源字段”和“质量透明”。全球主要指数来自 Sina Finance、Stooq、Yahoo 等公开源适配器。早期版本曾出现指数点位正确但涨跌幅与来源页面不一致的问题，因此后端约束涨跌和涨跌幅只使用同一数据源返回字段，不用错误基准自行推算。每条指数记录都展示中文名、代码、最新点位、涨跌、涨跌幅、市场时间、北京时间和数据质量。趋势图支持分时、日 K、月 K 三种模式，拿不到稳定 K 线时明确显示缓存、延迟或兜底原因，避免把不确定数据包装成精确实时行情。

    技术架构上，后端使用 Python 标准库实现 HTTP 服务，避免 node/npm 不可用导致的部署阻塞。服务端接口包括 `/api/fx`、`/api/indices`、`/api/trends`、`/api/health` 和 `/api/diagnostics`。其中 diagnostics 输出数据源最近成功时间、失败原因、缓存年龄、接口耗时和公开演示建议，使系统具备可观测性。前端采用原生 HTML/CSS/JavaScript，Three.js 本地 vendor 化，避免依赖 CDN。图表使用原生 SVG/Canvas 思路实现，减少包体和构建步骤。

    稳定性方面，系统采用分层缓存和 stale-while-revalidate 思路。汇率与指数适合短缓存，趋势图因为历史数据更重而使用较长缓存。自动刷新间隔为 20 秒，既能保证演示反馈，又通过缓存、超时和请求合并避免请求风暴。当某个数据源短暂失败时，页面优先展示最近成功缓存并标注状态，而不是让整页崩溃。所有 HTML、JS、CSS 和 JSON 响应设置 no-store 或版本号策略，减少公开访问时别人看到旧资源的问题。

    交互体验上，作品提供暗色和浅色模式，并支持红涨绿跌与绿涨红跌切换，尊重中西方金融颜色习惯差异。动画主要使用 transform、opacity、requestAnimationFrame 和 SVG 过渡，保证主题切换、卡片刷新、地球旋转和图表切换足够流畅。移动端布局控制地球高度、表格滚动和卡片间距，避免元素重叠。

    创新创业价值上，本作品的亮点不是把某个单点技术包装成概念，而是在免费、低依赖、可公开演示、数据源有波动这些真实约束下做出完整系统。它可以服务金融学习、课堂展示、校园社团市场观察和小型研究讨论，也具备继续扩展到自选市场、学习卡片、风险提示、正式云部署和合规付费数据源的路线。比赛版已经完成从“能看”到“能跑、能解释、能分享”的转变，具备良好的展示性和工程可信度。
    """
)


SLIDES = [
    [
        "金融小助手",
        "创新创业作品展示",
        "01",
        "Global Market Console",
        "零成本公开访问的全球金融市场数据控制台",
        "汇率 / 全球指数 / 三模式图表 / 3D 地球 / 数据诊断",
        "第十一届创新创业大赛作品赛",
        "一句话定位",
        "用本地 Python + 原生前端，把全球金融数据做成可运行、可公开、可解释的市场观察工作台。",
        "核心亮点",
        "20 秒刷新 · 官方来源跳转 · 质量标签 · Cloudflare 临时公网链接",
    ],
    [
        "目录",
        "从金融数据痛点，到产品方案、技术架构、可信兜底和比赛演示路径。",
        "01 团队成员 - 分工保持不变",
        "02 项目背景 - 汇率、指数、时区与来源分散",
        "03 产品方案 - 一屏式金融控制台",
        "04 作品展示 - 汇率、指数、图表、3D 地球",
        "05 技术架构 - Python 后端 + 原生前端",
        "06 数据可信 - 缓存、诊断、官方跳转",
        "07 创新价值 - 零成本公开访问与后续路线",
    ],
    [
        "金融小助手",
        "创新创业作品展示",
        "03",
        "团队成员",
        "成员分工围绕真实可运行、数据可信、体验展示和项目规范展开。",
        "史健申",
        "组长",
        "统筹项目方向、需求抽象、可信度验证与现场路演表达。",
        "需求分析",
        "项目统筹",
        "数据可信度测试",
        "公开访问验证",
        "钟浩",
        "组员",
        "负责产品方案、数据源适配、前端交互、3D 可视化与工程交付。",
        "产品设计",
        "Python 后端与 API",
        "前端核心交互整合",
        "3D 可视化实现",
        "文档与演示材料协作",
        "曹桂涛",
        "指导老师",
        "华东师范大学软件工程学院党委副书记、教授、博士生导师。",
        "技术路线指导",
        "架构与创新性把关",
        "项目规范指导",
    ],
    [
        "金融小助手",
        "创新创业作品展示",
        "04",
        "为什么需要这个项目？",
        "普通用户看全球市场，不缺网站，缺的是一个能把数据、时间、来源和体验整合起来的轻量工具。",
        "信息分散",
        "汇率、指数、市场时间散落在不同网站，切换成本高。",
        "来源不清",
        "免费数据可能延迟，但很多页面不告诉用户质量状态。",
        "部署困难",
        "很多作品只能本机看，评委和同学无法直接访问体验。",
        "体验割裂",
        "跨时区市场难理解，图表、换算和来源核验不在同一工作流。",
        "设计判断：先让核心数据真实跑通，再把可信度和体验前置给用户。",
    ],
    [
        "金融小助手",
        "创新创业作品展示",
        "05",
        "产品主界面：一屏式金融控制台",
        "不是营销首页，而是打开即可使用的市场观察工作台。",
        "全球时钟 + 3D 地球",
        "拖拽旋转、点击光点、时钟卡片联动，市场时间实时跳动。",
        "汇率 + 换汇",
        "基础货币可选，高精度自适应显示，官方来源可跳转。",
        "全球指数 + 图表",
        "中文名、涨跌幅、市场时间、北京时间、数据质量和趋势图。",
        "偏好与搜索",
        "暗浅主题、红绿习惯、货币/指数/代码搜索和 20 秒刷新。",
    ],
    [
        "金融小助手",
        "创新创业作品展示",
        "06",
        "汇率模块：计算与权威核验分离",
        "让用户既能快速换算，也能点击查看官方展示来源。",
        "常用货币",
        "USD、CNY、EUR、JPY、GBP、HKD、AUD、CAD、CHF、SGD、KRW、INR。",
        "基础货币可选",
        "不固定 USD，用户可按自己的场景选择基准。",
        "高精度换算",
        "内部保留完整数值，展示按数量级和币种自适应小数。",
        "官方跳转",
        "CNY 相关跳中国银行，国际参考跳 ECB 或相关央行页面。",
        "API 数据源用于计算，官方页面用于用户核验。",
    ],
    [
        "金融小助手",
        "创新创业作品展示",
        "07",
        "全球指数：同源字段 + 三模式图表",
        "指数点位、涨跌、涨跌幅和趋势图坚持真实优先，不用相近标的冒充。",
        "覆盖样本",
        "美股三大、FTSE、DAX、CAC、Nikkei、Hang Seng、上证、沪深 300。",
        "中文名展示",
        "每个指数同时展示中文名、英文名和代码，降低理解门槛。",
        "三模式图表",
        "分时 / 日 K / 月 K，可全局切换，也可进入单指数详情。",
        "数据质量",
        "实时、延迟、缓存、兜底都会明确标注，不伪装成交易级实时。",
    ],
    [
        "金融小助手",
        "创新创业作品展示",
        "08",
        "3D 交互地球：市场时间的空间化表达",
        "把时区、城市和市场位置从文字变成可拖拽、可点击、可联动的视觉体验。",
        "高精度优先",
        "优先加载 Natural Earth 1:10m 边界，失败才进入可说明 fallback。",
        "交互完整",
        "拖拽惯性、点击光点选中、点击空白取消、卡片联动、tooltip 读秒。",
        "视觉效果",
        "海洋、陆地、海岸线、星空、市场弧线、气辉和城市光点。",
        "性能控制",
        "requestAnimationFrame 渲染，页面隐藏时降低负载，移动端固定高度。",
    ],
    [
        "金融小助手",
        "创新创业作品展示",
        "09",
        "系统总体架构",
        "本地服务降低部署门槛，统一 API 把多个免费公开源封装成前端可消费的数据结构。",
        "浏览器前端",
        "原生 HTML/CSS/JS + 本地 Three.js + SVG/Canvas 图表。",
        "Python 后端",
        "/api/fx /api/indices /api/trends /api/health /api/diagnostics。",
        "数据源适配器",
        "Frankfurter、Sina Finance、Stooq、Yahoo、Natural Earth。",
        "缓存与诊断",
        "TTL 缓存、超时、失败原因、最近成功时间、接口耗时。",
        "取舍：不靠重框架堆叠，优先保证本机可跑、现场可演示、别人可访问。",
    ],
    [
        "金融小助手",
        "创新创业作品展示",
        "10",
        "数据可信与后端稳定性",
        "免费公开源天然有波动，所以系统必须能解释、能兜底、能被检查。",
        "同源字段",
        "指数涨跌幅使用来源返回字段，不用错误基准自行推算。",
        "分层缓存",
        "汇率/指数短缓存，趋势图较长缓存，降低 20 秒刷新压力。",
        "失败兜底",
        "保留最近成功数据，显示缓存/延迟/兜底状态。",
        "诊断接口",
        "/api/diagnostics 输出数据源状态、缓存年龄、耗时和失败原因。",
        "金融产品的可信度来自透明边界，而不是夸大实时性。",
    ],
    [
        "金融小助手",
        "创新创业作品展示",
        "11",
        "体验与动画设计",
        "金融看板要快、稳、清楚，同时具备足够展示冲击力。",
        "主题系统",
        "暗色模式突出科技感，浅色模式适合答辩展示和阅读。",
        "红绿习惯",
        "支持红涨绿跌 / 绿涨红跌，适配中西方市场认知。",
        "丝滑动画",
        "transform、opacity、requestAnimationFrame、SVG 过渡和 View Transition 思路。",
        "响应式",
        "移动端固定地球高度，表格横向滚动，按钮和文字避免重叠。",
        "体验目标：用户第一次打开就能理解，连续操作也不卡顿。",
    ],
    [
        "金融小助手",
        "创新创业作品展示",
        "12",
        "官方来源与合规边界",
        "把 API 数据源、官方展示页和投资风险提示分开说明。",
        "汇率官方入口",
        "CNY 相关跳中国银行，欧元参考跳 ECB，其它跳央行/监管机构。",
        "指数来源入口",
        "每条指数提供官方或可信详情页，方便现场核验。",
        "质量标签",
        "实时、延迟、缓存、兜底、不可用都有明确 UI 文案。",
        "免责声明",
        "免费公开源可能延迟，数据仅用于学习和市场观察，不构成投资建议。",
        "不把不确定数据包装成权威实时数据，是金融项目的基本底线。",
    ],
    [
        "金融小助手",
        "创新创业作品展示",
        "13",
        "创新价值与竞争力",
        "在低成本、低依赖、可公开演示的限制下做出完整金融数据产品。",
        "零成本公网展示",
        "本机 Python + Cloudflare Quick Tunnel，评委可直接打开链接。",
        "可观测数据链",
        "诊断接口让数据源、缓存、失败和耗时都可解释。",
        "空间化市场时钟",
        "3D 地球把跨时区理解变成交互体验。",
        "真实优先图表",
        "三模式趋势图 + 数据质量标签，避免误导。",
        "核心价值：从静态网页升级为可运行、可分享、可说明边界的产品。",
    ],
    [
        "金融小助手",
        "创新创业作品展示",
        "14",
        "进度与后续计划",
        "已完成比赛版核心闭环，后续围绕数据源、学习场景和正式部署增强。",
        "已完成",
        "本地服务、汇率、换汇、全球指数、趋势图、3D 地球、主题偏好、公开访问。",
        "短期",
        "补充更多稳定指数源，完善公网缓存检查和自动化浏览器验收。",
        "中期",
        "自选市场、学习卡片、价格提醒、更多资产类别和历史对比。",
        "长期",
        "正式云部署、合规付费数据源、账号体系、报表导出和教育版产品化。",
    ],
    [
        "金融小助手",
        "创新创业作品展示",
        "15",
        "展示路径",
        "现场演示按视觉冲击、数据可信、交互完整和公网访问四条线展开。",
        "1. 3D 地球",
        "拖拽旋转，点击城市光点，展示实时读秒和时区。",
        "2. 汇率换算",
        "切换基础货币，做高精度换汇，点击官方来源。",
        "3. 指数图表",
        "切换分时 / 日 K / 月 K，打开指数详情和来源页。",
        "4. 数据诊断",
        "打开 /api/diagnostics，说明缓存、耗时和数据源状态。",
        "5. 公网体验",
        "双击公开访问脚本，把 trycloudflare.com 链接发给评委。",
    ],
    [
        "谢谢聆听",
        "金融小助手",
        "欢迎体验与交流",
        "一个可运行、可公开、可解释、可交互的全球金融市场控制台。",
    ],
]


SVG_ASSETS = {
    "product-overview.svg": """
    <svg xmlns="http://www.w3.org/2000/svg" width="1200" height="720" viewBox="0 0 1200 720">
      <defs>
        <linearGradient id="bg" x1="0" x2="1" y1="0" y2="1"><stop stop-color="#061815"/><stop offset="1" stop-color="#123850"/></linearGradient>
        <linearGradient id="card" x1="0" x2="1"><stop stop-color="#11271f"/><stop offset="1" stop-color="#153b50"/></linearGradient>
        <filter id="glow"><feGaussianBlur stdDeviation="6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
      </defs>
      <rect width="1200" height="720" rx="32" fill="url(#bg)"/>
      <text x="70" y="90" fill="#d9fff6" font-size="48" font-family="Microsoft YaHei, Arial" font-weight="800">金融小助手</text>
      <text x="72" y="132" fill="#94bdb5" font-size="24" font-family="Microsoft YaHei, Arial">全球市场数据控制台 · 汇率 · 指数 · 图表 · 3D 地球 · 公开访问</text>
      <g transform="translate(70 180)">
        <rect width="510" height="430" rx="26" fill="url(#card)" stroke="#315c54"/>
        <circle cx="255" cy="215" r="145" fill="#063d73" stroke="#58e6d2" stroke-width="3" filter="url(#glow)"/>
        <path d="M135 195 C180 120, 290 115, 365 165 C320 177, 265 180, 235 225 C210 258, 160 250, 135 195Z" fill="#33d59f" opacity=".55"/>
        <path d="M275 265 C325 245, 385 260, 397 315 C350 360, 287 344, 275 265Z" fill="#33d59f" opacity=".45"/>
        <path d="M125 215 C230 160, 320 155, 400 220" fill="none" stroke="#88fff0" stroke-width="2" opacity=".6"/>
        <path d="M120 250 C240 320, 342 312, 408 232" fill="none" stroke="#88fff0" stroke-width="2" opacity=".35"/>
        <circle cx="170" cy="150" r="10" fill="#5df2d2" filter="url(#glow)"/>
        <circle cx="348" cy="180" r="10" fill="#ffd166" filter="url(#glow)"/>
        <circle cx="320" cy="312" r="10" fill="#5df2d2" filter="url(#glow)"/>
        <text x="40" y="390" fill="#d9fff6" font-size="28" font-family="Microsoft YaHei, Arial" font-weight="700">可交互市场地球</text>
      </g>
      <g transform="translate(625 180)" font-family="Microsoft YaHei, Arial">
        <rect width="505" height="95" rx="18" fill="#10251f" stroke="#2f544b"/>
        <text x="28" y="38" fill="#9fbdb7" font-size="20" font-weight="700">FX RATES</text>
        <text x="28" y="72" fill="#f4fff9" font-size="30" font-weight="800">CNY → USD 0.1468</text>
        <text x="330" y="72" fill="#54e3cf" font-size="20" font-weight="700">官方展示</text>
        <rect y="120" width="505" height="95" rx="18" fill="#10251f" stroke="#2f544b"/>
        <text x="28" y="158" fill="#9fbdb7" font-size="20" font-weight="700">WORLD INDICES</text>
        <text x="28" y="192" fill="#f4fff9" font-size="30" font-weight="800">上证指数 / S&P 500</text>
        <text x="365" y="192" fill="#54e3cf" font-size="20" font-weight="700">日K/月K</text>
        <rect y="240" width="505" height="95" rx="18" fill="#10251f" stroke="#2f544b"/>
        <text x="28" y="278" fill="#9fbdb7" font-size="20" font-weight="700">DIAGNOSTICS</text>
        <text x="28" y="312" fill="#f4fff9" font-size="30" font-weight="800">缓存 · 耗时 · 失败原因</text>
        <rect y="360" width="505" height="70" rx="18" fill="#1f4f45" stroke="#56e3cf"/>
        <text x="28" y="405" fill="#dffff8" font-size="26" font-weight="800">Cloudflare Quick Tunnel 公开访问</text>
      </g>
    </svg>
    """,
    "architecture.svg": """
    <svg xmlns="http://www.w3.org/2000/svg" width="1200" height="680" viewBox="0 0 1200 680">
      <rect width="1200" height="680" rx="30" fill="#f4f7f6"/>
      <text x="60" y="80" font-size="44" font-family="Microsoft YaHei, Arial" font-weight="800" fill="#10201c">金融小助手系统架构</text>
      <g font-family="Microsoft YaHei, Arial" font-size="24" font-weight="700">
        <rect x="70" y="150" width="250" height="120" rx="18" fill="#dff6f1" stroke="#36b6a4"/>
        <text x="105" y="205" fill="#10201c">用户浏览器</text><text x="105" y="240" fill="#42736b" font-size="18">HTML / CSS / JS</text>
        <rect x="475" y="150" width="250" height="120" rx="18" fill="#e8f0ff" stroke="#5a8dff"/>
        <text x="505" y="205" fill="#10201c">Python 本地服务</text><text x="505" y="240" fill="#506a92" font-size="18">统一 API + 静态资源</text>
        <rect x="880" y="150" width="250" height="120" rx="18" fill="#fff1df" stroke="#ffaf45"/>
        <text x="922" y="205" fill="#10201c">公开数据源</text><text x="922" y="240" fill="#8a6432" font-size="18">Frankfurter / Sina / Stooq</text>
        <rect x="475" y="355" width="250" height="120" rx="18" fill="#e9fff5" stroke="#31c48d"/>
        <text x="520" y="408" fill="#10201c">分层缓存</text><text x="520" y="443" fill="#4b7966" font-size="18">TTL / stale / fallback</text>
        <rect x="70" y="355" width="250" height="120" rx="18" fill="#f0e8ff" stroke="#9c72ff"/>
        <text x="105" y="408" fill="#10201c">3D 地球与图表</text><text x="105" y="443" fill="#675090" font-size="18">Three.js / SVG / Canvas</text>
        <rect x="880" y="355" width="250" height="120" rx="18" fill="#ffecef" stroke="#ed6a83"/>
        <text x="925" y="408" fill="#10201c">诊断接口</text><text x="925" y="443" fill="#8f4b58" font-size="18">耗时 / 缓存 / 失败原因</text>
        <path d="M320 210 L475 210" stroke="#1c3933" stroke-width="5" marker-end="url(#a)"/>
        <path d="M725 210 L880 210" stroke="#1c3933" stroke-width="5" marker-end="url(#a)"/>
        <path d="M600 270 L600 355" stroke="#1c3933" stroke-width="5" marker-end="url(#a)"/>
        <path d="M475 420 L320 420" stroke="#1c3933" stroke-width="5" marker-end="url(#a)"/>
        <path d="M725 420 L880 420" stroke="#1c3933" stroke-width="5" marker-end="url(#a)"/>
      </g>
      <defs><marker id="a" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto"><path d="M0,0 L10,3 L0,6 Z" fill="#1c3933"/></marker></defs>
    </svg>
    """,
    "data-flow.svg": """
    <svg xmlns="http://www.w3.org/2000/svg" width="1200" height="640" viewBox="0 0 1200 640">
      <rect width="1200" height="640" rx="28" fill="#071c1a"/>
      <text x="60" y="82" fill="#eafff8" font-size="44" font-family="Microsoft YaHei, Arial" font-weight="800">数据流与可信兜底</text>
      <g font-family="Microsoft YaHei, Arial" font-size="24" font-weight="700">
        <rect x="70" y="160" width="220" height="90" rx="18" fill="#143d35" stroke="#55dfc5"/><text x="105" y="215" fill="#eafff8">前端刷新</text>
        <rect x="355" y="160" width="220" height="90" rx="18" fill="#123652" stroke="#5aa8ff"/><text x="385" y="215" fill="#eafff8">统一 API</text>
        <rect x="640" y="160" width="220" height="90" rx="18" fill="#3d3214" stroke="#ffc95a"/><text x="672" y="215" fill="#eafff8">外部数据源</text>
        <rect x="925" y="160" width="220" height="90" rx="18" fill="#3d1a24" stroke="#ff7a91"/><text x="955" y="215" fill="#eafff8">失败/超时</text>
        <rect x="355" y="360" width="220" height="90" rx="18" fill="#143d35" stroke="#55dfc5"/><text x="398" y="415" fill="#eafff8">缓存命中</text>
        <rect x="640" y="360" width="220" height="90" rx="18" fill="#143d35" stroke="#55dfc5"/><text x="682" y="415" fill="#eafff8">质量标签</text>
        <rect x="925" y="360" width="220" height="90" rx="18" fill="#123652" stroke="#5aa8ff"/><text x="958" y="415" fill="#eafff8">诊断接口</text>
        <path d="M290 205 L355 205 M575 205 L640 205 M860 205 L925 205 M465 250 L465 360 M750 250 L750 360 M1035 250 L1035 360 M575 405 L640 405 M860 405 L925 405" stroke="#9eece0" stroke-width="5" fill="none"/>
      </g>
      <text x="75" y="555" fill="#9ec6bd" font-size="26" font-family="Microsoft YaHei, Arial">原则：能取到真实数据就展示真实数据；取不到就展示缓存或兜底，并明确告诉用户质量状态。</text>
    </svg>
    """,
    "globe-interaction.svg": """
    <svg xmlns="http://www.w3.org/2000/svg" width="1200" height="700" viewBox="0 0 1200 700">
      <defs><radialGradient id="o" cx=".45" cy=".35"><stop stop-color="#55f1e6"/><stop offset=".45" stop-color="#0d84bd"/><stop offset="1" stop-color="#062747"/></radialGradient><filter id="g"><feGaussianBlur stdDeviation="5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
      <rect width="1200" height="700" rx="30" fill="#071714"/>
      <text x="60" y="85" fill="#f4fff9" font-size="44" font-family="Microsoft YaHei, Arial" font-weight="800">3D 交互地球时钟</text>
      <circle cx="405" cy="365" r="210" fill="url(#o)" stroke="#77f4e5" stroke-width="3" opacity=".95"/>
      <path d="M258 285 C330 210 435 210 520 285 C455 298 400 320 362 374 C330 420 286 392 258 285Z" fill="#42d89f" opacity=".55"/>
      <path d="M445 430 C505 390 574 422 585 485 C520 542 460 506 445 430Z" fill="#42d89f" opacity=".45"/>
      <path d="M210 350 C330 258 480 260 600 350 M220 430 C360 500 495 505 590 370 M405 155 C460 260 463 470 405 575 M405 155 C348 265 348 468 405 575" fill="none" stroke="#b7fff6" stroke-width="2" opacity=".35"/>
      <circle cx="292" cy="252" r="13" fill="#67fff0" filter="url(#g)"/><text x="245" y="232" fill="#dffff8" font-size="22" font-family="Microsoft YaHei">伦敦</text>
      <circle cx="518" cy="268" r="13" fill="#ffd166" filter="url(#g)"/><text x="538" y="255" fill="#dffff8" font-size="22" font-family="Microsoft YaHei">北京</text>
      <circle cx="545" cy="438" r="13" fill="#67fff0" filter="url(#g)"/><text x="562" y="445" fill="#dffff8" font-size="22" font-family="Microsoft YaHei">东京</text>
      <g font-family="Microsoft YaHei, Arial" font-size="26" font-weight="700">
        <rect x="720" y="185" width="380" height="78" rx="18" fill="#122c25" stroke="#47d9c0"/><text x="750" y="235" fill="#eafff8">拖拽旋转：中心固定</text>
        <rect x="720" y="300" width="380" height="78" rx="18" fill="#122c25" stroke="#47d9c0"/><text x="750" y="350" fill="#eafff8">点击光点：显示时间</text>
        <rect x="720" y="415" width="380" height="78" rx="18" fill="#122c25" stroke="#47d9c0"/><text x="750" y="465" fill="#eafff8">点击空白：取消选中</text>
      </g>
    </svg>
    """,
}


def write_assets() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    for name, svg in SVG_ASSETS.items():
        (ASSETS / name).write_text(textwrap.dedent(svg).strip() + "\n", encoding="utf-8")


def docx_paragraph(text: str, style: str | None = None) -> str:
    text = clean(text)
    props = ""
    if style:
        props = f'<w:pPr><w:pStyle w:val="{style}"/></w:pPr>'
    parts = []
    for idx, line in enumerate(text.split("\n")):
        if idx:
            parts.append("<w:br/>")
        parts.append(f"<w:t>{html.escape(line)}</w:t>")
    return f"<w:p>{props}<w:r>{''.join(parts)}</w:r></w:p>"


def markdown_to_docx_body(markdown_text: str) -> str:
    body: list[str] = []
    in_code = False
    for raw in markdown_text.splitlines():
        line = raw.rstrip()
        if line.startswith("```"):
            in_code = not in_code
            continue
        if not line.strip():
            body.append(docx_paragraph(""))
            continue
        if in_code:
            body.append(docx_paragraph(line, "Code"))
            continue
        if line.startswith("# "):
            body.append(docx_paragraph(line[2:].strip(), "Title"))
        elif line.startswith("## "):
            body.append(docx_paragraph(line[3:].strip(), "Heading1"))
        elif line.startswith("### "):
            body.append(docx_paragraph(line[4:].strip(), "Heading2"))
        elif line.startswith("!["):
            m = re.match(r"!\[(.*?)\]\((.*?)\)", line)
            if m:
                body.append(docx_paragraph(f"【图】{m.group(1)}：{m.group(2)}", "Caption"))
        elif line.startswith("- "):
            body.append(docx_paragraph("• " + line[2:].strip()))
        elif line.startswith("|"):
            body.append(docx_paragraph(line.replace("|", "    ")))
        else:
            body.append(docx_paragraph(line))
    return "\n".join(body)


def write_docx(path: Path, markdown_text: str) -> None:
    now = datetime.now(timezone.utc).isoformat()
    document_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    {markdown_to_docx_body(markdown_text)}
    <w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1200" w:right="1100" w:bottom="1200" w:left="1100" w:header="720" w:footer="720" w:gutter="0"/></w:sectPr>
  </w:body>
</w:document>"""
    styles_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:rPr><w:rFonts w:eastAsia="Microsoft YaHei" w:ascii="Aptos"/><w:sz w:val="22"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:rPr><w:rFonts w:eastAsia="Microsoft YaHei"/><w:b/><w:sz w:val="36"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:rPr><w:rFonts w:eastAsia="Microsoft YaHei"/><w:b/><w:sz w:val="30"/><w:color w:val="143D35"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="heading 2"/><w:rPr><w:rFonts w:eastAsia="Microsoft YaHei"/><w:b/><w:sz w:val="26"/><w:color w:val="245A52"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Caption"><w:name w:val="caption"/><w:rPr><w:rFonts w:eastAsia="Microsoft YaHei"/><w:i/><w:color w:val="667A75"/><w:sz w:val="20"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Code"><w:name w:val="code"/><w:rPr><w:rFonts w:ascii="Consolas" w:eastAsia="Microsoft YaHei"/><w:color w:val="374151"/><w:sz w:val="20"/></w:rPr></w:style>
</w:styles>"""
    content_types = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>"""
    rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""
    core = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>{html.escape(path.stem)}</dc:title><dc:creator>金融小助手团队</dc:creator><cp:lastModifiedBy>Codex</cp:lastModifiedBy><dcterms:created xsi:type="dcterms:W3CDTF">{now}</dcterms:created><dcterms:modified xsi:type="dcterms:W3CDTF">{now}</dcterms:modified>
</cp:coreProperties>"""
    app = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"><Application>Microsoft Word</Application></Properties>"""
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("_rels/.rels", rels)
        zf.writestr("word/document.xml", document_xml)
        zf.writestr("word/styles.xml", styles_xml)
        zf.writestr("docProps/core.xml", core)
        zf.writestr("docProps/app.xml", app)


def strip_pictures(root: ET.Element) -> None:
    pic_tag = "{http://schemas.openxmlformats.org/presentationml/2006/main}pic"
    for parent in root.iter():
        for child in list(parent):
            if child.tag == pic_tag:
                parent.remove(child)


P_NS = "http://schemas.openxmlformats.org/presentationml/2006/main"
A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
CT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"

ET.register_namespace("p", P_NS)
ET.register_namespace("a", A_NS)
ET.register_namespace("r", R_NS)


def q(ns: str, tag: str) -> str:
    return f"{{{ns}}}{tag}"


def add_svg_picture(root: ET.Element, rid: str, name: str) -> None:
    sp_tree = root.find(f".//{q(P_NS, 'spTree')}")
    if sp_tree is None:
        return
    pic_id = str(900 + len(sp_tree))
    pic = ET.Element(q(P_NS, "pic"))
    nv = ET.SubElement(pic, q(P_NS, "nvPicPr"))
    ET.SubElement(nv, q(P_NS, "cNvPr"), {"id": pic_id, "name": name})
    ET.SubElement(nv, q(P_NS, "cNvPicPr"))
    ET.SubElement(nv, q(P_NS, "nvPr"))
    blip_fill = ET.SubElement(pic, q(P_NS, "blipFill"))
    ET.SubElement(blip_fill, q(A_NS, "blip"), {q(R_NS, "embed"): rid})
    stretch = ET.SubElement(blip_fill, q(A_NS, "stretch"))
    ET.SubElement(stretch, q(A_NS, "fillRect"))
    sp_pr = ET.SubElement(pic, q(P_NS, "spPr"))
    xfrm = ET.SubElement(sp_pr, q(A_NS, "xfrm"))
    ET.SubElement(xfrm, q(A_NS, "off"), {"x": "6100000", "y": "1860000"})
    ET.SubElement(xfrm, q(A_NS, "ext"), {"cx": "5600000", "cy": "3150000"})
    geom = ET.SubElement(sp_pr, q(A_NS, "prstGeom"), {"prst": "rect"})
    ET.SubElement(geom, q(A_NS, "avLst"))
    sp_tree.append(pic)


def ensure_svg_content_type(data: bytes) -> bytes:
    root = ET.fromstring(data)
    has_svg = any(child.attrib.get("Extension") == "svg" for child in root)
    if not has_svg:
        ET.SubElement(root, q(CT_NS, "Default"), {"Extension": "svg", "ContentType": "image/svg+xml"})
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def slide_relationships(data: bytes, slide_no: int, asset_name: str | None) -> bytes:
    root = ET.fromstring(data)
    rel_tag = q(REL_NS, "Relationship")
    for child in list(root):
        target = child.attrib.get("Target", "")
        if child.tag == rel_tag and target.startswith("../media/"):
            root.remove(child)
    if asset_name:
        ET.SubElement(
            root,
            rel_tag,
            {
                "Id": f"rIdFinancialVisual{slide_no}",
                "Type": "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image",
                "Target": f"../media/{asset_name}",
            },
        )
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def write_pptx() -> None:
    target = COMP / "金融小助手_双创展示PPT.pptx"
    source_path = TEMPLATE_PPTX if TEMPLATE_PPTX.exists() else target
    if not source_path.exists():
        print("Skip PPTX generation: no template or existing PPTX found")
        return
    output_path = target.with_name("_金融小助手_双创展示PPT.tmp.pptx") if source_path == target else target
    ns = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"}
    slide_visuals = {
        1: "product-overview.svg",
        8: "globe-interaction.svg",
        9: "architecture.svg",
        10: "data-flow.svg",
    }
    with zipfile.ZipFile(source_path, "r") as src, zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as dst:
        for item in src.infolist():
            if item.filename.startswith("ppt/media/"):
                continue
            data = src.read(item.filename)
            if item.filename == "[Content_Types].xml":
                data = ensure_svg_content_type(data)
            elif item.filename.startswith("ppt/slides/_rels/") and item.filename.endswith(".rels"):
                slide_no = int(Path(item.filename).stem.replace("slide", "").replace(".xml", ""))
                data = slide_relationships(data, slide_no, slide_visuals.get(slide_no))
            if item.filename.startswith("ppt/slides/slide") and item.filename.endswith(".xml"):
                slide_no = int(Path(item.filename).stem.replace("slide", ""))
                root = ET.fromstring(data)
                strip_pictures(root)
                nodes = root.findall(".//a:t", ns)
                replacement = SLIDES[slide_no - 1]
                for i, node in enumerate(nodes):
                    node.text = replacement[i] if i < len(replacement) else ""
                if slide_no in slide_visuals:
                    add_svg_picture(root, f"rIdFinancialVisual{slide_no}", slide_visuals[slide_no])
                data = ET.tostring(root, encoding="utf-8", xml_declaration=True)
            elif item.filename in {"docProps/core.xml", "docProps/app.xml"}:
                try:
                    root = ET.fromstring(data)
                    for elem in root.iter():
                        if elem.text and "钟于钢琴" in elem.text:
                            elem.text = elem.text.replace("钟于钢琴工作室教学管理小程序", "金融小助手")
                    data = ET.tostring(root, encoding="utf-8", xml_declaration=True)
                except ET.ParseError:
                    pass
            dst.writestr(item, data)
        for asset_name in set(slide_visuals.values()):
            dst.writestr(f"ppt/media/{asset_name}", (ASSETS / asset_name).read_bytes())
    if output_path != target:
        output_path.replace(target)


def write_markdown_files() -> None:
    (COMP / "金融小助手_双创展示PPT讲稿.md").write_text(SPEAKER_MD, encoding="utf-8")
    (COMP / "金融小助手_答辩Q&A_50题.md").write_text(QA_MD, encoding="utf-8")
    (COMP / "第十一届创新创业大赛作品赛作品情况表_金融小助手.md").write_text(SITUATION_MD, encoding="utf-8")
    checklist = wrap(
        """
        # 金融小助手参赛材料清单

        ## 新版主展示材料

        - 金融小助手_HTML路演展示/index.html：比赛现场主展示页，12 页动态全屏展示，含成员照片页。
        - 金融小助手_HTML路演展示/演示讲稿.md：高级版 5-6 分钟讲稿。
        - 金融小助手_HTML路演展示/打开HTML路演展示.bat：双击打开动态展示页。

        ## 备份与提交材料

        - 第十一届创新创业大赛作品赛作品情况表_金融小助手.docx
        - 金融小助手_双创展示PPT.pptx：旧版备份，不建议作为主展示。
        - 金融小助手_双创展示PPT讲稿.docx / .md
        - 金融小助手_答辩Q&A_50题.docx / .md
        - 金融小助手_图文素材/：产品总览、系统架构、数据流、3D 地球交互示意图

        队员信息沿用参考材料：史健申、钟浩，指导老师曹桂涛；组长为史健申。

        演示建议：先启动本地服务，再展示 3D 地球、汇率官方跳转、指数三模式图表、/api/diagnostics，最后用“公开访问金融小助手.bat”生成公网链接。
        """
    )
    (COMP / "金融小助手_参赛材料清单.md").write_text(checklist, encoding="utf-8")


def write_docx_files() -> None:
    write_docx(COMP / "金融小助手_双创展示PPT讲稿.docx", SPEAKER_MD)
    write_docx(COMP / "金融小助手_答辩Q&A_50题.docx", QA_MD)
    write_situation_docx_from_template()


def remove_word_media(root: ET.Element) -> None:
    drawing_tag = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}drawing"
    pict_tag = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}pict"
    for parent in root.iter():
        for child in list(parent):
            if child.tag in {drawing_tag, pict_tag}:
                parent.remove(child)


def replace_rel_media(data: bytes) -> bytes:
    try:
        root = ET.fromstring(data)
    except ET.ParseError:
        return data
    rel_tag = "{http://schemas.openxmlformats.org/package/2006/relationships}Relationship"
    for child in list(root):
        if child.tag == rel_tag and (child.attrib.get("Target", "").startswith("media/")):
            root.remove(child)
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def write_situation_docx_from_template() -> None:
    """Preserve the original competition form layout while replacing content."""

    if not TEMPLATE_FORM.exists():
        write_docx(COMP / "第十一届创新创业大赛作品赛作品情况表_金融小助手.docx", SITUATION_MD)
        return

    target = COMP / "第十一届创新创业大赛作品赛作品情况表_金融小助手.docx"
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    intro = (
        "金融小助手是一套面向金融学习、市场观察与比赛展示的轻量级全球市场数据控制台。"
        "作品以本地 Python Edge Gateway 为核心，融合汇率、全球指数、三模式趋势图、3D 市场地球、跨时区时钟、官方来源跳转和数据质量标签。"
        "系统强调 Data Fusion、Observability 与 Resilience：通过多源适配、分层缓存、失败兜底、同源涨跌幅校验和 /api/diagnostics 诊断视图，在零付费 API、零复杂部署条件下实现可运行、可解释、可公网分享的金融数据产品原型。"
    )
    install = [
        "1. 在 Windows 环境进入项目目录，双击“启动金融小助手.bat”，或运行 .\\.python\\python.exe server.py。",
        "2. 终端出现 http://127.0.0.1:18765 后，用现代浏览器打开该地址，即可体验汇率、指数、图表和 3D 地球。",
        "3. 如需让其他人访问，双击“公开访问金融小助手.bat”，等待终端打印 https://xxxx.trycloudflare.com，把该链接发给评委或同学。",
        "4. 公网链接依赖本机、网络、本地服务和 Cloudflare 窗口持续运行；关闭窗口或断网后链接失效。推荐使用支持 WebGL 的新版 Chrome、Edge 或 Firefox。",
        "演示视频建议现场录制：先展示 3D 地球，再展示汇率官方跳转、指数三模式图表和 /api/diagnostics。",
        "",
    ]
    design = [
        "金融小助手的设计并不从“做一个行情页面”出发，而是从金融信息消费链路出发：用户需要获得跨市场数据、理解市场时间、判断数据可信度、查看趋势变化，并把作品快速分享给他人。项目将这些需求抽象为一个轻量 Market Intelligence Console，强调统一入口、可信边界和低成本分发。",
        "系统采用本地边缘服务架构。前端是原生 HTML/CSS/JavaScript 与 Canvas/SVG/Three.js 可视化层，负责沉浸式展示、主题偏好、图表交互和响应式体验；后端是 Python Edge Gateway，负责统一 API、数据源适配、缓存治理、诊断输出和静态资源分发。该架构避免复杂依赖，适合比赛现场、课堂展示和低成本试点。",
        "数据层采用 Multi-source Adapter 思路，将 Frankfurter、Sina Finance、Stooq、Yahoo、Natural Earth 等公开源接入统一数据结构。它不是简单抓取，而是做字段归一、市场时区标注、北京时间对照、质量状态标记和失败原因沉淀。前端不需要理解每个源的差异，只消费稳定的领域对象。",
        "可信数据层是作品的核心能力。金融展示最忌讳把免费数据源包装成交易级实时系统，因此作品引入 Quality of Data 概念，把实时、延迟、缓存、兜底、不可用等状态显式呈现。指数涨跌幅优先使用同源字段，避免点位正确但涨跌幅错误；缺少稳定 K 线时宁可标注兜底，也不使用相近标的冒充指数。",
        "性能与稳定性上，系统采用分层 TTL 缓存、请求合并、超时控制和 stale-while-revalidate 思路。汇率与指数使用短缓存保证演示反馈，趋势图使用更长缓存降低历史数据请求压力。当外部源短时失败时，页面优先展示最近成功数据并标注缓存状态，而不是让核心体验崩溃。",
        "/api/diagnostics 是工程可信度的集中体现。它输出服务健康、数据源最近成功与失败、缓存年龄、接口耗时和公开演示建议。比赛现场不仅能展示漂亮界面，还能解释系统为什么这样显示、哪里来自缓存、哪个源失败过，从而把项目从“页面作品”提升为“可观测系统”。",
        "体验层面，作品把全球市场时间空间化。3D 地球优先加载 Natural Earth 1:10m 高精度边界，配合海洋、陆地、海岸线、市场光点和气辉效果。北京、纽约、伦敦、法兰克福、东京、香港等市场不再只是文字列表，而是可拖拽、可点击、可读秒的空间节点。",
        "图表体验采用渐进式探索。总览页提供全球指数与小趋势，用户可以在分时、日 K、月 K 之间切换；点击单一指数进入详情后，可查看更大图表、市场时间、北京时间、来源链接和质量标签。这样的设计兼顾展示冲击力与信息密度。",
        "汇率模块围绕“计算”和“核验”分离。系统内部保留完整精度并根据币种数量级自适应显示，避免韩元、日元、卢比等小额汇率失真。点击汇率卡片时优先跳转中国银行、ECB 或相关央行页面，让用户看到官方展示，而不是 API 文档。",
        "视觉系统支持暗色/浅色模式和红涨绿跌/绿涨红跌切换。暗色模式强化科技感和路演氛围，浅色模式适合阅读与日常使用；涨跌颜色偏好则尊重中西方市场认知差异。动画采用 transform、opacity 与 requestAnimationFrame，兼顾丝滑感和性能。",
        "公开访问采用本地 Python 服务加 Cloudflare Quick Tunnel。作品不依赖购买服务器、域名或付费 API，即可在现场生成 trycloudflare.com 链接，让评委和同学用自己的设备直接访问。服务端通过 no-store 与资源版本策略减少公网缓存导致的旧资源问题。",
        "从创新创业角度看，本作品的价值在于把低成本、低依赖、免费数据源波动、跨时区理解和公开演示这些真实约束统一进一个完整产品闭环：Data Fusion、Cache QoS、Observability、Immersive UX 和 Zero-cost Distribution 共同构成项目的技术与展示壁垒。",
        "作品可面向金融学习、课堂演示、校园社团、轻量研究小组和市场观察场景推广。后续可以扩展自选市场、学习卡片、价格提醒、跨资产对比、合规付费数据源、账号体系和正式云部署，逐步演进为教育版 Market Intelligence Lab。",
        "",
        "",
        "",
        "",
    ]
    hard = [
        "数据可信边界。免费公开源天然存在延迟、限流和短时不可用，系统必须将数据质量显式化，避免用户把学习型看板误解为交易级终端。",
        "多源字段归一。不同市场数据源返回结构差异较大，指数涨跌幅、市场时间、来源链接和趋势数据必须统一成稳定领域模型，前端才能保持简洁。",
        "同源涨跌幅校验。早期版本出现过点位正确但涨跌幅不一致的问题，后续将涨跌和涨跌幅约束为同源字段，缺失时显示质量状态而不是自行推导。",
        "缓存 QoS 设计。20 秒自动刷新需要兼顾反馈速度和外部源压力，系统通过短缓存、长缓存、请求合并和 stale-while-revalidate 平衡体验与稳定性。",
        "3D 地球精度与性能平衡。高精度陆地边界、城市光点和市场弧线会增加渲染压力，作品通过 Natural Earth 1:10m、Canvas/WebGL 和移动端高度控制保证流畅。",
        "公网分发与缓存一致性。Cloudflare 临时公网链接适合零成本展示，但可能带来旧资源缓存问题，项目通过 no-store、资源版本和公开访问检查降低风险。",
        "汇率精度表达。不同货币数量级差异明显，展示层需要高精度自适应格式，既避免数值失真，也保证界面可读。",
        "跨文化视觉语义。中国市场常用红涨绿跌，海外市场常用绿涨红跌，因此涨跌颜色不能写死，而要成为用户可配置偏好。",
        "金融合规边界。作品必须明确数据仅用于学习与市场观察，不构成投资建议，同时提供官方来源跳转和免责说明，保证展示表达严谨。",
    ]
    progress = [
        "已完成：本地 Python 服务、/api/fx、/api/indices、/api/trends、/api/health、/api/diagnostics、汇率、换汇计算、全球指数、分时/日K/月K图表、3D 交互地球、暗浅主题、红绿偏好、搜索、20 秒自动刷新、官方来源跳转和公开访问脚本。",
        "短期计划：补充更多稳定指数源，完善公网缓存检查、浏览器验收截图和自动化测试；中期计划：增加自选市场、学习卡片、价格提醒、更多资产类别和历史对比。",
        "长期计划：正式云部署、合规付费数据源接入、账号体系、报表导出、访问控制和教育版产品化。",
    ]

    replacements = {
        1: "金融小助手：零成本公开访问的全球金融市场数据控制台",
        12: "史健申",
        13: "钟浩",
        15: "10235101561",
        16: "10225101490",
        18: "18130570903@163.com",
        19: "2177686531@qq.com",
        22: "18130570903",
        23: "19279985142",
        34: intro,
        35: "",
        36: "",
        37: "",
        38: "作品支持本地运行与 Cloudflare 临时公网演示，适合比赛现场快速分享体验。",
        46: "作品效果图（整体、关键点和特效，见同目录“金融小助手_图文素材”：产品总览、系统架构、数据流、3D地球交互）",
        81: "团队组长为史健申，参赛队员为史健申、钟浩，指导老师为曹桂涛。本作品不提供投资建议；免费公开源可能延迟。公开演示时请保持本机服务、Cloudflare 窗口和网络连接持续运行。",
    }
    for offset, value in enumerate(install):
        replacements[40 + offset] = value
    for offset, value in enumerate(design):
        replacements[48 + offset] = value
    for offset, value in enumerate(hard):
        replacements[66 + offset] = value
    for offset, value in enumerate(progress):
        replacements[76 + offset] = value

    with zipfile.ZipFile(TEMPLATE_FORM, "r") as src, zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as dst:
        for item in src.infolist():
            if item.filename.startswith("word/media/"):
                continue
            data = src.read(item.filename)
            if item.filename == "word/document.xml":
                root = ET.fromstring(data)
                remove_word_media(root)
                texts = root.findall(".//w:t", ns)
                for idx, value in replacements.items():
                    if idx < len(texts):
                        texts[idx].text = value
                data = ET.tostring(root, encoding="utf-8", xml_declaration=True)
            elif item.filename == "word/_rels/document.xml.rels":
                data = replace_rel_media(data)
            elif item.filename in {"docProps/core.xml", "docProps/app.xml"}:
                try:
                    root = ET.fromstring(data)
                    for elem in root.iter():
                        if elem.text and "钟于钢琴" in elem.text:
                            elem.text = elem.text.replace("钟于钢琴工作室教学管理小程序", "金融小助手")
                    data = ET.tostring(root, encoding="utf-8", xml_declaration=True)
                except ET.ParseError:
                    pass
            dst.writestr(item, data)


def main() -> None:
    COMP.mkdir(exist_ok=True)
    write_assets()
    write_markdown_files()
    write_docx_files()
    write_pptx()
    print("Generated competition files in", COMP)


if __name__ == "__main__":
    main()
