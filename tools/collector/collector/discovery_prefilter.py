"""
Discovery 预过滤器 — 从原始热点数据中整理 LLM 语义扫描的输入清单

设计原则:
  1. 不替 LLM 判断"内容质量" — 只做"阅读清单整理"
  2. 按源配额采样 — 不同源的热度值语义不同（平台播放量 vs 评论数），
     全量排序会让大平台娱乐内容淹没科技源。改为每源各取一些，保证多样性。
  3. 分层配额 — Tier 1（AI/科技/财经/开发者）多采，Tier 2（新闻/社交热搜）少采样捕捉跨界

输出: data/pending/{date}/discovery-input.json (≈300 条均衡输入)
"""

import json
from datetime import datetime, timezone
from pathlib import Path

from . import storage

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
PENDING_DIR = PROJECT_ROOT / "data" / "pending"

# ── 源分层配置 ─────────────────────────────────────────
# Tier 1: 核心相关源（AI/科技/财经/开发者）— 配额高，需求信号密度大
TIER1_SOURCES = {
    # 科技/商业媒体
    "dailyhot:36kr", "dailyhot:51cto", "dailyhot:ithome",
    "dailyhot:ifanr", "dailyhot:thepaper",
    # 开发者社区
    "dailyhot:juejin", "dailyhot:sspai", "dailyhot:v2ex",
    "dailyhot:nodeseek", "dailyhot:hellogithub",
    "dailyhot:zhihu", "dailyhot:zhihu-daily",
}

# Tier 1 的 Folo 源用关键词匹配（slug 不稳定）
TIER1_FOLO_KEYWORDS = {
    "机器之心", "InfoQ", "Ahead", "OpenAI", "掘金", "GitHub", "Trending",
    "少数派", "36氪", "Readhub", "财联社", "华尔街", "雪球", "科技",
}

# Tier 2: 抽样源（新闻/社交热搜）— 配额低，捕捉跨界需求
TIER2_SOURCES = {
    "dailyhot:toutiao", "dailyhot:qq-news", "dailyhot:sina-news",
    "dailyhot:netease-news", "dailyhot:baidu",
    "dailyhot:weibo", "dailyhot:douyin", "dailyhot:bilibili",
    "dailyhot:tieba", "dailyhot:douban-group",
}

# 配额
TIER1_QUOTA = 12   # 每个核心源取 top 12
TIER2_QUOTA = 3    # 每个抽样源取 top 3
TARGET_TOTAL = 300

# 标题去重阈值
SIMILARITY_THRESHOLD = 0.8


def _classify_tier(source: str) -> int:
    """源 → 分层 (1=核心, 2=抽样, 0=排除)"""
    if source in TIER1_SOURCES:
        return 1
    if source.startswith("folo:"):
        for kw in TIER1_FOLO_KEYWORDS:
            if kw in source:
                return 1
        # 其他 Folo 源默认归 Tier 2（Folo 是手动精选订阅，质量有保障）
        return 2
    if source in TIER2_SOURCES:
        return 2
    # 其余（游戏/天气/历史/体育/文学）排除
    return 0


def _normalize_title(title: str) -> str:
    import re
    title = re.sub(r'\s+', '', title.lower())
    title = re.sub(r'[【】()()\[\]「」『』、。，！？：；,.!?::;\'""]', '', title)
    return title


def _similarity(a: str, b: str) -> float:
    """归一化 Levenshtein 相似度"""
    if a == b:
        return 1.0
    if not a or not b:
        return 0.0
    m, n = len(a), len(b)
    if abs(m - n) > 50:
        return 0.0
    prev = list(range(n + 1))
    for i in range(1, m + 1):
        curr = [i] + [0] * n
        for j in range(1, n + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            curr[j] = min(curr[j - 1] + 1, prev[j] + 1, prev[j - 1] + cost)
        prev = curr
    return 1 - prev[n] / max(m, n)


def _is_dup(title: str, seen_normalized: list[str]) -> bool:
    norm = _normalize_title(title)
    for seen in seen_normalized:
        if _similarity(norm, seen) >= SIMILARITY_THRESHOLD:
            return True
    return False


def _hot_value(item: dict) -> float:
    """热度值转 float"""
    raw = item.get("hot_metric", 0)
    if isinstance(raw, (int, float)):
        return float(raw)
    if isinstance(raw, str):
        import re
        m = re.match(r'([\d.]+)\s*(万|亿)?', raw.strip())
        if m:
            num = float(m.group(1))
            unit = m.group(2)
            if unit == "亿":
                return num * 1e8
            if unit == "万":
                return num * 1e4
            return num
    return 0.0


def prefilter(top_n: int = TARGET_TOTAL) -> list[dict]:
    """主入口: 分层配额采样 + 去重

    流程:
      1. 加载原始数据，按分层分桶
      2. 每源按热度排序，取配额数量
      3. 合并去重
      4. 按分层 + 热度排序
    """
    items = storage.load_latest(limit=3000)
    if not items:
        print("  ⚠️ 无热点数据")
        return []

    # 分层分桶
    by_tier: dict[int, dict[str, list[dict]]] = {1: {}, 2: {}}
    excluded = 0
    for it in items:
        source = it.get("source", "")
        tier = _classify_tier(source)
        if tier == 0:
            excluded += 1
            continue
        by_tier[tier].setdefault(source, []).append(it)

    print(f"  分层: Tier1 源={len(by_tier[1])}, Tier2 源={len(by_tier[2])}, 排除={excluded} 条")

    # 每源按热度排序 + 取配额
    def sample(tier_sources: dict, quota: int) -> list[dict]:
        picked = []
        for source, src_items in tier_sources.items():
            src_items.sort(key=_hot_value, reverse=True)
            picked.extend(src_items[:quota])
        return picked

    tier1_picked = sample(by_tier[1], TIER1_QUOTA)
    tier2_picked = sample(by_tier[2], TIER2_QUOTA)
    print(f"  采样: Tier1={len(tier1_picked)} 条 (每源 {TIER1_QUOTA}), "
          f"Tier2={len(tier2_picked)} 条 (每源 {TIER2_QUOTA})")

    # 合并 + 去重
    all_picked = tier1_picked + tier2_picked
    seen_normalized: list[str] = []
    deduped: list[dict] = []
    dup_count = 0
    for item in all_picked:
        title = str(item.get("title", ""))
        if not title:
            continue
        if _is_dup(title, seen_normalized):
            dup_count += 1
            continue
        seen_normalized.append(_normalize_title(title))
        # 标记分层，供下游排序/报告用
        item = dict(item)
        item["_tier"] = _classify_tier(item.get("source", ""))
        deduped.append(item)

    print(f"  去重: {len(all_picked)} → {len(deduped)} (去重 {dup_count} 条)")

    # 按分层（Tier1 优先）+ 热度排序
    deduped.sort(key=lambda x: (-x.get("_tier", 0), -_hot_value(x)))

    final = deduped[:top_n]
    print(f"  最终: {len(final)} 条 (Tier1={sum(1 for f in final if f['_tier']==1)}, "
          f"Tier2={sum(1 for f in final if f['_tier']==2)})")

    return final


def save_input(items: list[dict], date_str: str | None = None) -> Path:
    """保存到 data/pending/{date}/discovery-input.json"""
    if date_str is None:
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    out_dir = PENDING_DIR / date_str
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "discovery-input.json"

    # 精简字段
    compact = []
    for item in items:
        compact.append({
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "source": item.get("source", ""),
            "hot_metric": item.get("hot_metric", ""),
            "source_type": item.get("source_type", ""),
            "tier": item.get("_tier", 0),
            "description": item.get("description", "")[:200],
        })

    tier1_count = sum(1 for c in compact if c["tier"] == 1)
    tier2_count = sum(1 for c in compact if c["tier"] == 2)

    out_path.write_text(json.dumps({
        "date": date_str,
        "total": len(compact),
        "tier1_count": tier1_count,
        "tier2_count": tier2_count,
        "filter": "discovery_prefilter (per-source quota sampling)",
        "config": {
            "tier1_quota": TIER1_QUOTA,
            "tier2_quota": TIER2_QUOTA,
        },
        "items": compact,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"✅ {out_path}")
    return out_path


def main():
    items = prefilter()
    save_input(items)


if __name__ == "__main__":
    main()