"""
文章发现器 — 从采集数据中提取 AI Coding Plan 相关文章，产出候选列表

每次采集后运行，生成 data/pending/{date}/articles.json（候选文章，待 Claude Code 审阅）。
不再直接写入 changes.json——编辑决策由 Claude Code 完成。
"""

import hashlib
import json
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
PENDING_DIR = PROJECT_ROOT / "data" / "pending"
DATA_DIR = PROJECT_ROOT / "data" / "raw"

# 相关关键词（召回用，宁可多召回，由 Claude Code 去噪）
KEYWORDS = [
    "Coding Plan", "Token Plan", "Claude Code", "Cursor", "AI编程",
    "Vibe Coding", "套餐", "定价", "额度", "订阅", "抢购",
    "Kimi K3", "Kimi-K3", "DeepSeek V4", "GLM-5.2", "MiniMax",
    "字节方舟", "智谱", "Copilot", "Codex", "Anthropic",
    "大模型", "Agent", "降价", "涨价", "新模型",
]

# 来源名称映射
SOURCE_NAMES = {
    "dailyhot:36kr": "36氪",
    "dailyhot:ithome": "IT之家",
    "dailyhot:sspai": "少数派",
    "dailyhot:juejin": "掘金",
    "dailyhot:51cto": "51CTO",
    "dailyhot:ifanr": "爱范儿",
    "dailyhot:hellogithub": "HelloGitHub",
    "dailyhot:zhihu": "知乎",
    "dailyhot:guokr": "果壳",
    "dailyhot:sina-news": "新浪",
    "dailyhot:netease-news": "网易",
    # Folo 源
    "folo:机器之心": "机器之心",
    "folo:InfoQ-推荐": "InfoQ",
    "folo:掘金本周最热": "掘金",
    "folo:36氪---24小时热榜": "36氪",
    "folo:华尔街见闻": "华尔街见闻",
    "folo:财联社---头条": "财联社",
    "folo:少数派": "少数派",
    "folo:Ahead-of-AI": "Ahead of AI",
    "folo:OpenAI-News": "OpenAI News",
    "folo:IT之家": "IT之家",
    "folo:爱范儿": "爱范儿",
    "folo:虎嗅": "虎嗅",
    "folo:Readhub---每日早报": "Readhub",
    "folo:雪球": "雪球",
}


def _make_id(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()[:12]


def _extract_source(source: str) -> str:
    name = SOURCE_NAMES.get(source)
    if name:
        return name
    # 兜底：去掉前缀
    for prefix in ("dailyhot:", "folo:", "rsshub:"):
        if source.startswith(prefix):
            return source[len(prefix):]
    return source


def _estimate_read_time(title: str) -> str:
    length = len(title)
    if length < 30:
        return "3 分钟"
    elif length < 50:
        return "5 分钟"
    elif length < 80:
        return "7 分钟"
    return "10 分钟"


def _pick_cover(title: str) -> str:
    if "K3" in title or "Kimi" in title:
        return "K3"
    if "DeepSeek" in title:
        return "DS"
    if "Claude" in title:
        return "CL"
    if "价格" in title or "涨价" in title or "降价" in title:
        return "UP"
    if "教程" in title or "手把手" in title:
        return "GUIDE"
    return "NEW"


def _determine_level(title: str) -> str:
    """根据标题判断文章重要性（机器预判，Claude Code 可覆盖）"""
    high_signals = ["暂停", "售罄", "K3", "Kimi-K3", "DeepSeek V4", "发布"]
    if any(s in title for s in high_signals):
        return "high"
    return "medium"


def discover_articles() -> list[dict]:
    """从最新采集数据中发现相关文章，返回 changes.json 格式的候选条目"""
    if not DATA_DIR.exists():
        return []

    # 找到最新的数据文件
    date_dirs = sorted([d for d in DATA_DIR.iterdir() if d.is_dir()], reverse=True)
    if not date_dirs:
        return []

    json_files = sorted(
        [f for f in date_dirs[0].iterdir() if f.suffix == ".json"],
        reverse=True
    )
    if not json_files:
        return []

    with open(json_files[0], "r", encoding="utf-8") as f:
        data = json.load(f)

    items = data.get("items", [])
    articles = []
    seen_urls = set()
    # 用采集日期目录名作为文章日期，而非 pipeline 运行时间
    collection_date = date_dirs[0].name  # e.g., "2026-07-21"

    for item in items:
        title = str(item.get("title", "")).strip()
        url = str(item.get("url", "")).strip()

        if not title or not url:
            continue
        if url in seen_urls:
            continue
        if not any(kw in title for kw in KEYWORDS):
            continue

        seen_urls.add(url)
        featured = "暂停" in title or "K3" in title or "DeepSeek" in title

        articles.append({
            "id": _make_id(url),
            "date": collection_date,
            "kind": "article",
            "vendor": "通用",
            "title": title,
            "detail": title[:120],
            "impact": "neutral",
            "level": _determine_level(title),
            "source": "signal-dailyhot",
            "sourceUrl": url,
            "relatedPlans": [],
            "featured": featured,
            "excerpt": title[:80] + ("..." if len(title) > 80 else ""),
            "author": _extract_source(item.get("source", "")),
            "readTime": _estimate_read_time(title),
            "cover": _pick_cover(title),
            # 候选标记 — Claude Code 审阅后移除
            "_candidate": True,
            "_reason": f"关键词匹配: {', '.join(kw for kw in KEYWORDS if kw in title)[:100]}",
        })

    return articles


def save_candidates(articles: list[dict], date_str: str = None) -> Path:
    """保存候选文章到 data/pending/{date}/articles.json"""
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")

    out_dir = PENDING_DIR / date_str
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "articles.json"

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({
            "generated_at": datetime.now().isoformat(),
            "count": len(articles),
            "candidates": articles,
        }, f, ensure_ascii=False, indent=2)

    return out_path


def main():
    articles = discover_articles()

    if not articles:
        print("📰 文章发现: 无候选文章")
        return

    out_path = save_candidates(articles)
    # 统计
    high = sum(1 for a in articles if a.get("level") == "high")
    medium = sum(1 for a in articles if a.get("level") == "medium")
    print(f"📰 文章发现: {len(articles)} 篇候选 (high={high}, medium={medium})")
    print(f"   输出: {out_path}")
    print(f"   ⚠️  候选文章尚未收录 — 请用 /codingplan-page update 审阅后写入 changes.json")


if __name__ == "__main__":
    main()