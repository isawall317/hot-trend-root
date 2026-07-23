"""采集引擎 — 从 DailyHotApi + RSSHub + Folo 拉取数据，归一化存储"""

import asyncio
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import httpx

from .storage import save_raw

# 项目根目录（相对于此文件: tools/collector/collector/engine.py → 项目根）
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent

# 数据目录
DATA_DIR = PROJECT_ROOT / "data" / "raw"

# DailyHotApi 地址
DAILYHOT_BASE = os.getenv("DAILYHOT_BASE", "http://localhost:6688")
DAILYHOT_PUBLIC = os.getenv(
    "DAILYHOT_PUBLIC",
    "https://dailyhotapi-vercel-mauve.vercel.app"
)

# RSSHub 地址
RSSHUB_BASE = os.getenv("RSSHUB_BASE", "http://localhost:1200")
RSSHUB_PUBLIC = "https://rsshub.app"

# Folo 配置（本地 RSS 阅读器，通过 folocli 交互）
FOLO_LIMIT = int(os.getenv("FOLO_LIMIT", "100"))  # 每次从 Folo 拉取的条目数
FOLO_VIEW = int(os.getenv("FOLO_VIEW", "0"))       # 0=文章 1=社交 2=图片 3=视频
FOLO_NPX = os.getenv("FOLO_NPX", "npx")            # npx 路径


# ── DailyHotApi 源列表 ──────────────────────────────────────────
# 完整列表见: https://github.com/imsyy/DailyHotApi
DAILYHOT_SOURCES = [
    # 社交媒体 / 内容平台
    "zhihu",          # 知乎热榜
    "zhihu-daily",    # 知乎日报
    "weibo",          # 微博热搜
    "douyin",         # 抖音热点
    "bilibili",       # B站热门
    "tieba",          # 贴吧热议
    "kuaishou",       # 快手
    "acfun",          # A站
    # 科技 / 开发者社区
    "v2ex",           # V2EX 热门
    "juejin",         # 掘金热榜
    "csdn",           # CSDN
    "51cto",          # 51CTO
    "hellogithub",    # HelloGitHub
    "sspai",          # 少数派
    "ithome",         # IT之家
    "coolapk",        # 酷安
    "nodeseek",       # NodeSeek
    "52pojie",        # 吾爱破解
    "hostloc",        # 全球主机交流
    # 新闻 / 媒体
    "baidu",          # 百度热搜
    "toutiao",        # 今日头条
    "36kr",           # 36氪
    "thepaper",       # 澎湃新闻
    "netease-news",   # 网易新闻
    "sina-news",      # 新浪新闻
    "qq-news",        # 腾讯新闻
    "huxiu",          # 虎嗅
    "ifanr",          # 爱范儿
    # 社区 / 兴趣
    "hupu",           # 虎扑
    "douban-group",   # 豆瓣讨论精选
    "douban-movie",   # 豆瓣电影新片榜
    "jianshu",        # 简书
    "guokr",          # 果壳
    "weread",         # 微信读书飙升榜
    # 游戏
    "ngabbs",         # NGA
    "genshin",        # 原神
    "lol",            # 英雄联盟
    "starrail",       # 崩坏星穹铁道
    "honkai",         # 崩坏3
    "miyoushe",       # 米游社
    # 公共服务
    "earthquake",     # 地震速报
    "weatheralarm",   # 气象预警
    "history",        # 历史上的今天
]


# ── RSSHub 源列表 ────────────────────────────────────────────────
# 格式: (路由路径, 标签)
RSSHUB_SOURCES = [
    # 技术与开源
    ("/github/trending/daily", "github"),
    ("/hackernews/best", "hackernews"),
    # 产品与商业
    ("/producthunt/today", "producthunt"),
    # 国内内容平台（RSSHub 补充 DailyHotApi 没覆盖的）
    ("/jike/topic/553870e6e4b0c63c1a0d68e1", "jike"),  # 即刻精选
    # 小红书（DailyHotApi 不支持）
    ("/xiaohongshu/board/feed", "xiaohongshu"),
]


async def _fetch_dailyhot(client: httpx.AsyncClient, source: str, base_url: str):
    """从 DailyHotApi 拉取单个源"""
    try:
        resp = await client.get(f"{base_url}/{source}", timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return source, data
    except Exception as e:
        print(f"  ⚠️  DailyHotApi/{source} 失败: {e}")
        return source, None


async def _fetch_rsshub(client: httpx.AsyncClient, route: str, tag: str, base_url: str):
    """从 RSSHub 拉取单个 RSS 源"""
    try:
        resp = await client.get(f"{base_url}{route}", timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return tag, data
    except Exception as e:
        print(f"  ⚠️  RSSHub{route} 失败: {e}")
        return tag, None


def _fetch_folo(limit: int = 100, view: int = 0) -> list[dict]:
    """从本地 Folo (RSS 阅读器) 拉取 timeline 条目

    使用 folocli (npm 包) 与本地 Folo 应用交互。
    要求 Folo 应用正在运行。
    """
    try:
        cmd = [FOLO_NPX, "--yes", "folocli@latest", "timeline",
               "--limit", str(limit), "--view", str(view)]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if r.returncode != 0:
            print(f"  ⚠️  Folo/folocli 失败: {r.stderr[:200]}")
            return []
        data = json.loads(r.stdout)
        if not data.get("ok"):
            print(f"  ⚠️  Folo/folocli 返回异常: {data.get('error', 'unknown')}")
            return []
        entries = data.get("data", {}).get("entries", [])
        return entries
    except subprocess.TimeoutExpired:
        print("  ⚠️  Folo/folocli 超时")
        return []
    except FileNotFoundError:
        print("  ⚠️  Folo/folocli: npx 未找到，请确认 Node.js 已安装")
        return []
    except Exception as e:
        print(f"  ⚠️  Folo/folocli 异常: {e}")
        return []


def _normalize_folo(entries: list[dict], timestamp: str) -> list[dict]:
    """将 Folo timeline 条目归一化为统一格式"""
    items = []
    for entry in entries:
        e = entry.get("entries") or {}
        feed = entry.get("feeds") or {}
        sub = entry.get("subscriptions") or {}

        title = str(e.get("title", "")).strip()
        url = str(e.get("url", "")).strip()

        if not title:
            continue

        feed_title = feed.get("title") or sub.get("title") or "Folo"
        # 生成 source tag: "folo:<feed_slug>"
        feed_slug = feed_title.replace(" ", "-").replace("/", "-")[:30]

        items.append({
            "title": title,
            "url": url,
            "hot_metric": "",
            "source": f"folo:{feed_slug}",
            "source_type": _classify_folo_source(feed_title),
            "collected_at": timestamp,
            "author": str(e.get("author", "")).strip(),
            "description": str(e.get("description", "")).strip()[:500],
            "published_at": str(e.get("publishedAt", "")).strip(),
        })

    return items


def _classify_folo_source(feed_title: str) -> str:
    """将 Folo feed 标题归类"""
    TECH_FEEDS = {"机器之心", "InfoQ", "掘金", "CSDN", "51CTO", "HelloGitHub",
                  "少数派", "Ahead of AI", "OpenAI News", "Hacker News",
                  "GitHub", "Product Hunt", "V2EX", "NodeSeek"}
    NEWS_FEEDS = {"36氪", "财联社", "华尔街见闻", "IT之家", "爱范儿",
                  "虎嗅", "澎湃新闻", "新浪新闻", "腾讯新闻", "网易新闻",
                  "Readhub"}
    SOCIAL_FEEDS = {"知乎", "微博", "即刻", "小红书", "豆瓣", "雪球",
                    "今日话题"}

    for kw in TECH_FEEDS:
        if kw in feed_title:
            return "tech"
    for kw in NEWS_FEEDS:
        if kw in feed_title:
            return "news"
    for kw in SOCIAL_FEEDS:
        if kw in feed_title:
            return "social"
    return "other"


async def collect_all(sources: list[str] | None = None):
    """采集所有源数据，归一化后存入 data/raw/

    Args:
        sources: 指定采集的源列表，None 表示全部采集
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"🚀 Hot Trend 采集开始 — {timestamp}")

    # 自动检测可用 API
    async with httpx.AsyncClient() as client:
        dailyhot_base = await _detect_dailyhot_api(client)
        print(f"📡 DailyHotApi: {dailyhot_base}")

        # ── DailyHotApi ──
        selected = sources or DAILYHOT_SOURCES
        dailyhot_tasks = [
            _fetch_dailyhot(client, s, dailyhot_base)
            for s in selected
            if s in DAILYHOT_SOURCES
        ]
        dailyhot_results = await asyncio.gather(*dailyhot_tasks)

        # ── RSSHub ──
        rsshub_base = await _detect_rsshub_api(client)
        print(f"📡 RSSHub: {rsshub_base}")
        rsshub_tasks = [
            _fetch_rsshub(client, route, tag, rsshub_base)
            for route, tag in RSSHUB_SOURCES
        ]
        rsshub_results = await asyncio.gather(*rsshub_tasks)

    # ── Folo (本地 RSS 阅读器) ──
    print(f"📡 Folo: 本地 RSS (limit={FOLO_LIMIT}, view={FOLO_VIEW})")
    folo_entries = _fetch_folo(limit=FOLO_LIMIT, view=FOLO_VIEW)
    print(f"   Folo: {len(folo_entries)} 条")

    # ── 归一化 + 存储 ──
    all_items = []

    for source, data in dailyhot_results:
        if data is None:
            continue
        normalized = _normalize_dailyhot(source, data, timestamp)
        all_items.extend(normalized)

    for tag, data in rsshub_results:
        if data is None:
            continue
        normalized = _normalize_rsshub(tag, data, timestamp)
        all_items.extend(normalized)

    # Folo 归一化
    if folo_entries:
        folo_normalized = _normalize_folo(folo_entries, timestamp)
        all_items.extend(folo_normalized)

    if not all_items:
        print("❌ 没有采集到任何数据")
        return None

    # 存储
    filepath = save_raw(all_items, timestamp)

    # 统计
    sources_count = len(set(item["source"] for item in all_items))
    print(f"✅ 采集完成: {len(all_items)} 条, {sources_count} 个源")
    print(f"📁 存储: {filepath}")

    return filepath


async def _detect_dailyhot_api(client: httpx.AsyncClient) -> str:
    """检测使用本地 Docker 还是远程 API"""
    # 先试本地 Docker
    try:
        resp = await client.get(f"{DAILYHOT_BASE}/zhihu", timeout=5)
        if resp.status_code == 200:
            return DAILYHOT_BASE
    except Exception:
        pass
    return DAILYHOT_PUBLIC


async def _detect_rsshub_api(client: httpx.AsyncClient) -> str:
    """检测使用本地 Docker 还是公共 API"""
    try:
        resp = await client.get(f"{RSSHUB_BASE}/github/trending/daily", timeout=5)
        if resp.status_code == 200:
            return RSSHUB_BASE
    except Exception:
        pass
    return RSSHUB_PUBLIC


def _normalize_dailyhot(source: str, data: dict, timestamp: str) -> list[dict]:
    """将 DailyHotApi 返回数据归一化为统一格式"""
    items = []

    # DailyHotApi 返回格式: { "code": 200, "data": [...] }
    # 每个 item: { "title": "...", "url": "...", "hot": "...", ... }
    raw_items = data.get("data", []) if isinstance(data, dict) else []

    if isinstance(raw_items, list):
        for item in raw_items:
            if isinstance(item, dict):
                items.append({
                    "title": str(item.get("title", "")).strip(),
                    "url": str(item.get("url", "")).strip(),
                    "hot_metric": str(item.get("hot", "")),
                    "source": f"dailyhot:{source}",
                    "source_type": _classify_source(source),
                    "collected_at": timestamp,
                })

    return items


def _normalize_rsshub(tag: str, data: dict, timestamp: str) -> list[dict]:
    """将 RSSHub 返回数据归一化为统一格式"""
    items = []

    # RSSHub 返回格式: { "items": [{ "title": "...", "url": "...", ... }] }
    raw_items = data.get("items", []) if isinstance(data, dict) else []

    if isinstance(raw_items, list):
        for item in raw_items:
            if isinstance(item, dict):
                items.append({
                    "title": str(item.get("title", "")).strip(),
                    "url": str(item.get("url", "")).strip(),
                    "hot_metric": "",
                    "source": f"rsshub:{tag}",
                    "source_type": _classify_source(tag),
                    "collected_at": timestamp,
                })

    return items


def _classify_source(source: str) -> str:
    """将数据源归类"""
    SOCIAL = {"zhihu", "zhihu-daily", "weibo", "douyin", "bilibili", "tieba",
              "kuaishou", "acfun", "jike", "xiaohongshu"}
    TECH = {"v2ex", "juejin", "csdn", "51cto", "hellogithub", "sspai",
            "ithome", "coolapk", "nodeseek", "52pojie", "hostloc",
            "github", "hackernews"}
    NEWS = {"baidu", "toutiao", "36kr", "thepaper", "netease-news",
            "sina-news", "qq-news", "huxiu", "ifanr"}
    PRODUCT = {"producthunt"}
    CONTENT = {"douban-group", "douban-movie", "jianshu", "guokr", "weread"}
    GAME = {"ngabbs", "genshin", "lol", "starrail", "honkai", "miyoushe", "hupu"}
    OTHER = {"earthquake", "weatheralarm", "history"}

    if source in SOCIAL: return "social"
    if source in TECH: return "tech"
    if source in NEWS: return "news"
    if source in PRODUCT: return "product"
    if source in CONTENT: return "content"
    if source in GAME: return "game"
    return "other"


def main():
    """CLI 入口: python -m collector.engine"""
    asyncio.run(collect_all())


if __name__ == "__main__":
    main()