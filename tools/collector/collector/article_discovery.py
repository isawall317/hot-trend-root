"""
文章发现器 — 从采集数据中提取 AI Coding Plan 相关文章，更新 articles.json

每次采集后运行，自动发现和保存新文章。
"""

import json
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
ARTICLES_PATH = PROJECT_ROOT / "project" / "codingplan-saver" / "articles.json"
DATA_DIR = PROJECT_ROOT / "data" / "raw"

# 相关关键词
KEYWORDS = [
    "Coding Plan", "Token Plan", "Claude Code", "Cursor", "AI编程",
    "Vibe Coding", "套餐", "定价", "额度", "订阅", "抢购",
    "Kimi K3", "Kimi-K3", "DeepSeek V4", "GLM-5.2", "MiniMax",
    "字节方舟", "智谱", "Copilot", "Codex", "Anthropic",
    "大模型", "Agent", "降价", "涨价", "新模型",
]

# 分类规则（优先级从高到低）
CATEGORY_RULES = [
    (["暂停", "售罄", "涨价", "降价", "调价", "折扣", "活动", "限时", "免费"], "价格速报"),
    (["体验", "测评", "评测", "实测", "怎么样", "真香", "榨干"], "深度测评"),
    (["教程", "手把手", "实战", "指南", "封装", "Skill", "技能包"], "教程"),
    (["发布", "融资", "上市", "战略", "收购", "投资", "曝光"], "行业动态"),
    (["K3", "Kimi", "DeepSeek", "Claude", "Anthropic", "OpenAI", "GPT"], "深度测评"),
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


def _classify(title: str) -> str:
    for keywords, category in CATEGORY_RULES:
        if any(kw in title for kw in keywords):
            return category
    return "深度测评"  # default to review rather than news


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


def discover_articles() -> list[dict]:
    """从最新采集数据中发现相关文章"""
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
        articles.append({
            "id": _make_id(url),
            "title": title,
            "category": _classify(title),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "readTime": _estimate_read_time(title),
            "excerpt": title[:80] + ("..." if len(title) > 80 else ""),
            "tags": [],
            "cover": _pick_cover(title),
            "featured": "暂停" in title or "K3" in title or "DeepSeek" in title,
            "author": _extract_source(item.get("source", "")),
            "url": url,
        })

    return articles


def _make_id(url: str) -> str:
    import hashlib
    return hashlib.md5(url.encode()).hexdigest()[:12]


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


def update_articles_json():
    """更新 articles.json，合并新发现的文章"""
    # 加载现有文章
    existing = []
    if ARTICLES_PATH.exists():
        with open(ARTICLES_PATH, "r", encoding="utf-8") as f:
            existing = json.load(f)

    existing_urls = {a.get("url", "") for a in existing}

    # 发现新文章
    new_articles = discover_articles()

    # 合并：新文章在前，保留最多 30 篇
    added = 0
    for article in new_articles:
        if article["url"] not in existing_urls:
            existing.insert(0, article)
            existing_urls.add(article["url"])
            added += 1

    # 截断到 30 篇
    existing = existing[:30]

    # 保存
    with open(ARTICLES_PATH, "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)

    print(f"📰 文章发现: 新增 {added} 篇, 总计 {len(existing)} 篇")
    return ARTICLES_PATH


def main():
    update_articles_json()


if __name__ == "__main__":
    main()