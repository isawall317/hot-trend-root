"""URL 正文抽取：trafilatura 主，Jina Reader 兜底。

不同 URL 类型走不同路径：
- GitHub repo URL：调 GitHub API 拿 README + 描述（最准）
- 其他 URL：trafilatura 抽取，抽空/太短 → Jina Reader 兜底
"""
from __future__ import annotations

import re

import httpx

from .models import Article

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) hot-trend/0.1"


def extract(url: str, *, jina_fallback: bool = True) -> Article:
    """从 URL 抽取干净正文。

    Args:
        url: 任意 URL（GitHub repo / 博客 / 知乎专栏 / HN 帖等）
        jina_fallback: trafilatura 抽空时是否走 Jina 兜底
    """
    # GitHub repo 走专属路径（最准）
    if _is_github_repo(url):
        article = _extract_github_repo(url)
        if article and len(article.content) > 100:
            return article

    # 通用 trafilatura
    try:
        article = _extract_with_trafilatura(url)
        if article and len(article.content) > 200:
            return article
    except Exception:
        pass

    # Jina 兜底
    if jina_fallback:
        try:
            article = _extract_with_jina(url)
            if article and len(article.content) > 100:
                return article
        except Exception:
            pass

    # 全失败：返回原始 HTML 片段 + URL，让 LLM 自己处理
    return _extract_raw_fallback(url)


# ---------- URL 类型识别 ----------


def _is_github_repo(url: str) -> bool:
    """识别 https://github.com/{owner}/{repo} 形式（不含 /issues /pulls 等子路径）。"""
    m = re.match(r"https?://github\.com/([^/]+)/([^/]+)/?$", url.rstrip("/"))
    return bool(m) and "/" not in m.group(1)


# ---------- 各抽取方法 ----------


def _extract_with_trafilatura(url: str) -> Article | None:
    import trafilatura

    downloaded = trafilatura.fetch_url(url)
    if not downloaded:
        return None

    # 同时拿 metadata 和正文
    metadata = trafilatura.extract(downloaded, with_metadata=True, output_format="json")
    content = trafilatura.extract(
        downloaded,
        output_format="markdown",
        include_comments=False,
        include_tables=False,
        favor_recall=True,
    )

    if not content:
        return None

    title = ""
    if metadata:
        try:
            import json

            meta = json.loads(metadata)
            title = meta.get("title", "") or ""
        except Exception:
            pass

    excerpt = content[:300].replace("\n", " ").strip()
    return Article(
        url=url,
        title=title,
        content=content,
        excerpt=excerpt,
        method="trafilatura",
    )


def _extract_with_jina(url: str) -> Article | None:
    """Jina Reader: 在 URL 前加 https://r.jina.ai/ 即可。"""
    jina_url = f"https://r.jina.ai/{url}"
    with httpx.Client(timeout=30) as client:
        resp = client.get(jina_url, headers={"User-Agent": USER_AGENT, "Accept": "text/markdown"})
        resp.raise_for_status()
        text = resp.text

    if not text or len(text) < 100:
        return None

    # Jina 返回的 Markdown 通常以 "Title: xxx" 开头
    title = ""
    title_match = re.search(r"(?im)^Title:\s*(.+)$", text)
    if title_match:
        title = title_match.group(1).strip()
        text = re.sub(r"(?im)^Title:\s*.+\n?", "", text, count=1)

    # 去掉 Jina 加的 URL Source / Markdown Source 行
    text = re.sub(r"(?im)^(?:URL|Markdown) Source:.*\n?", "", text)

    excerpt = text[:300].replace("\n", " ").strip()
    return Article(
        url=url,
        title=title,
        content=text.strip(),
        excerpt=excerpt,
        method="jina",
    )


def _extract_github_repo(url: str) -> Article | None:
    """GitHub repo 走 API：拿 description + README，组装成结构化文本。"""
    m = re.match(r"https?://github\.com/([^/]+)/([^/]+)/?$", url.rstrip("/"))
    if not m:
        return None
    owner, repo = m.group(1), m.group(2)

    headers = {"Accept": "application/vnd.github+json", "User-Agent": USER_AGENT}

    with httpx.Client(timeout=15, headers=headers) as client:
        # 1. repo metadata
        meta_resp = client.get(f"https://api.github.com/repos/{owner}/{repo}")
        if meta_resp.status_code != 200:
            return None
        meta = meta_resp.json()

        # 2. README
        readme_resp = client.get(
            f"https://api.github.com/repos/{owner}/{repo}/readme",
            headers={**headers, "Accept": "application/vnd.github.raw"},
        )
        readme = readme_resp.text if readme_resp.status_code == 200 else ""

    # 组装成 LLM 友好的文本
    parts = [
        f"# {meta.get('full_name', url)}",
        "",
        f"> {meta.get('description', '(no description)')}",
        "",
        f"- Stars: {meta.get('stargazers_count', '?')}",
        f"- Language: {meta.get('language', '?')}",
        f"- Topics: {', '.join(meta.get('topics', []) or []) or '(none)'}",
        f"- License: {(meta.get('license') or {}).get('name', 'unknown')}",
        f"- Created: {meta.get('created_at', '?')[:10]}",
        f"- Updated: {meta.get('pushed_at', '?')[:10]}",
        f"- Homepage: {meta.get('homepage') or '(none)'}",
        "",
        "## README",
        "",
        readme[:8000] if readme else "(no README)",
    ]
    content = "\n".join(parts)
    return Article(
        url=url,
        title=meta.get("full_name", ""),
        content=content,
        excerpt=meta.get("description", "")[:300],
        method="trafilatura",  # GitHub 走的也是"干净文本"路径
    )


def _extract_raw_fallback(url: str) -> Article:
    """所有方法都失败时的兜底：抓原始 HTML 文本片段。"""
    try:
        with httpx.Client(timeout=15, follow_redirects=True) as client:
            resp = client.get(url, headers={"User-Agent": USER_AGENT})
            text = resp.text
        # 粗暴去标签
        no_tags = re.sub(r"<[^>]+>", " ", text)
        no_tags = re.sub(r"\s+", " ", no_tags).strip()
        content = no_tags[:5000] if no_tags else "(no content)"
    except Exception as e:
        content = f"(抽取失败: {e})"

    return Article(
        url=url,
        title="",
        content=content,
        excerpt="",
        method="trafilatura",
    )
