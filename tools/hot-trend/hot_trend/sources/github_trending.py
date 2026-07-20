"""GitHub Trending 采集源。

直接抓 github.com/trending 的 HTML（实测稳定，不需要 API/token）。
选择器参考稳定多年的结构：article.Box-row > h2 > a。
"""
from __future__ import annotations

import re

import httpx

from ..models import TrendItem

TRENDING_URL = "https://github.com/trending"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) hot-trend/0.1"


def fetch(limit: int = 20, *, since: str = "daily", language: str = "") -> list[TrendItem]:
    """抓 GitHub Trending。

    Args:
        limit: 最多返回多少条
        since: daily / weekly / monthly
        language: 语言过滤（如 "python"），空字符串=全部
    """
    params = {"since": since}
    if language:
        url = f"{TRENDING_URL}/{language}"
    else:
        url = TRENDING_URL

    with httpx.Client(timeout=15, headers={"User-Agent": UA}) as client:
        resp = client.get(url, params=params)
        resp.raise_for_status()
        html = resp.text

    return _parse(html, limit=limit)


def _parse(html: str, *, limit: int) -> list[TrendItem]:
    items: list[TrendItem] = []

    # 每个 repo 是一个 <article class="Box-row"> ... </article>
    # h2 > a href="/owner/repo"
    repo_blocks = re.findall(
        r'<article[^>]*class="Box-row"[^>]*>(.*?)</article>',
        html,
        re.DOTALL,
    )

    for block in repo_blocks[:limit]:
        # owner/repo
        m = re.search(
            r'<h2[^>]*>\s*<a[^>]*href="(/[^"]+)"[^>]*>',
            block,
            re.DOTALL,
        )
        if not m:
            continue
        path = m.group(1).strip().lstrip("/")
        if path.count("/") != 1:
            continue
        url = f"https://github.com/{path}"
        owner_repo = path

        # 描述
        desc_m = re.search(r'<p class="col-9[^"]*"[^>]*>(.*?)</p>', block, re.DOTALL)
        desc = _clean_html(desc_m.group(1)) if desc_m else ""

        # 语言
        lang_m = re.search(
            r'<span itemprop="programmingLanguage">([^<]+)</span>', block
        )
        lang = lang_m.group(1).strip() if lang_m else ""

        # stars today / total
        stars_today_m = re.search(r"([\d,]+)\s+stars\s+(today|this week|this month)", block)
        stars_today = int(stars_today_m.group(1).replace(",", "")) if stars_today_m else 0
        period = stars_today_m.group(2) if stars_today_m else ""

        title = f"{owner_repo}: {desc[:80]}" if desc else owner_repo
        hot_str = f"{stars_today} stars {period}" if stars_today else ""

        items.append(
            TrendItem(
                source="github",
                title=title,
                url=url,
                hot=hot_str,
                raw_hot=stars_today,
                extra={"language": lang, "description": desc, "repo": owner_repo},
            )
        )

    return items


def _clean_html(s: str) -> str:
    s = re.sub(r"<[^>]+>", "", s)
    return re.sub(r"\s+", " ", s).strip()
