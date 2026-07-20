"""V2EX 采集源 — 官方 API（实测稳定，~120 req/h 限速）。"""
from __future__ import annotations

import time

import httpx

from ..models import TrendItem

HOT_URL = "https://www.v2ex.com/api/topics/hot.json"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) hot-trend/0.1"

# 简单的内存缓存（10 分钟）：避免短时间内重复请求触发限速
_CACHE: dict[str, tuple[float, list]] = {}
_CACHE_TTL = 600


def fetch(limit: int = 20) -> list[TrendItem]:
    """抓 V2EX hot topics。

    V2EX hot.json 返回近期热帖，本身就是排序的。我们直接取前 N。
    """
    now = time.time()
    cached = _CACHE.get("hot")
    if cached and now - cached[0] < _CACHE_TTL:
        topics = cached[1]
    else:
        with httpx.Client(timeout=15, headers={"User-Agent": UA}) as client:
            resp = client.get(HOT_URL)
            resp.raise_for_status()
            topics = resp.json()
        _CACHE["hot"] = (now, topics)

    return [_to_trend_item(t) for t in topics[:limit]]


def _to_trend_item(topic: dict) -> TrendItem:
    replies = int(topic.get("replies", 0))
    title = topic.get("title", "")
    url = topic.get("url", "")
    node = (topic.get("node") or {}).get("title", "")
    member = (topic.get("member") or {}).get("username", "")
    hot = f"{replies} replies · {node}" if node else f"{replies} replies"

    return TrendItem(
        source="v2ex",
        title=title,
        url=url,
        hot=hot,
        raw_hot=replies,
        extra={"node": node, "member": member},
    )
