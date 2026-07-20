"""Hacker News 采集源 — 官方 Firebase API（实测稳定，无需 token）。"""
from __future__ import annotations

import httpx

from ..models import TrendItem

TOP_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{id}.json"


def fetch(limit: int = 20) -> list[TrendItem]:
    """抓 HN 前端页面 top stories。

    Args:
        limit: 最多返回多少条（HN topstories 共 ~500 条，我们只取前 N）
    """
    with httpx.Client(timeout=15) as client:
        resp = client.get(TOP_URL)
        resp.raise_for_status()
        ids: list[int] = resp.json()[:limit]

        # 并发拿详情
        items = []
        for story_id in ids:
            detail = client.get(ITEM_URL.format(id=story_id)).json()
            if not detail:
                continue
            items.append(_to_trend_item(detail))

    return items


def _to_trend_item(detail: dict) -> TrendItem:
    score = int(detail.get("score", 0))
    comments = int(detail.get("descendants", 0))
    url = detail.get("url") or f"https://news.ycombinator.com/item?id={detail['id']}"
    title = detail.get("title", "")
    by = detail.get("by", "")
    hot = f"{score} points · {comments} comments"

    return TrendItem(
        source="hn",
        title=title,
        url=url,
        hot=hot,
        raw_hot=score,
        extra={"by": by, "comments": comments, "hn_id": detail.get("id")},
    )
