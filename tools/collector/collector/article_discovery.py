"""
文章发现器 — 从采集数据中提取 AI Coding Plan 相关文章，更新 changes.json

每次采集后运行，自动发现和保存新文章到 changes.json（kind: "article"）。
"""

import hashlib
import json
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
CHANGES_PATH = PROJECT_ROOT / "project" / "codingplan-saver" / "data" / "changes.json"
DATA_DIR = PROJECT_ROOT / "data" / "raw"

# 相关关键词
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
}


def _make_id(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()[:12]


def _extract_source(source: str) -> str:
    return SOURCE_NAMES.get(source, source.replace("dailyhot:", ""))


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
    """根据标题判断文章重要性"""
    high_signals = ["暂停", "售罄", "K3", "Kimi-K3", "DeepSeek V4", "发布"]
    if any(s in title for s in high_signals):
        return "high"
    return "medium"


def discover_articles() -> list[dict]:
    """从最新采集数据中发现相关文章，返回 changes.json 格式的条目"""
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
    today = datetime.now().strftime("%Y-%m-%d")

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
            "date": today,
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
        })

    return articles


def update_changes_json():
    """更新 changes.json，合并新发现的文章"""
    # 加载现有 changes
    existing = []
    if CHANGES_PATH.exists():
        with open(CHANGES_PATH, "r", encoding="utf-8") as f:
            existing = json.load(f)

    existing_urls = {c.get("sourceUrl", "") for c in existing if c.get("sourceUrl")}
    existing_ids = {c.get("id", "") for c in existing}

    # 发现新文章
    new_articles = discover_articles()

    # 合并：新文章在前，去重
    added = 0
    for article in new_articles:
        if article["sourceUrl"] not in existing_urls and article["id"] not in existing_ids:
            existing.insert(0, article)
            existing_urls.add(article["sourceUrl"])
            existing_ids.add(article["id"])
            added += 1

    # 保存
    with open(CHANGES_PATH, "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)

    print(f"📰 文章发现: 新增 {added} 篇, changes 总计 {len(existing)} 条")
    return CHANGES_PATH


def main():
    update_changes_json()


if __name__ == "__main__":
    main()