"""CLI 入口：click 子命令。

P1 实现：
- scan:    抓热榜，rich 表格展示
- analyze: 对单条 URL 跑完整分析，输出机会卡

P2/P3 再加：
- discover: scan + analyze 一条龙
- week:     周报
"""
from __future__ import annotations

import sys
import webbrowser
from typing import Literal

import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, IntPrompt
from rich.table import Table

from .analyzer import analyze_url, render_card_md, save_card
from .config import load_config
from .models import verdict_for

console = Console()

SourceName = Literal["github", "hn", "v2ex"]


# ---------- 通用工具 ----------


def _fetch_source(source: SourceName, limit: int):
    if source == "github":
        from .sources import github_trending

        return github_trending.fetch(limit=limit)
    if source == "hn":
        from .sources import hackernews

        return hackernews.fetch(limit=limit)
    if source == "v2ex":
        from .sources import v2ex

        return v2ex.fetch(limit=limit)
    raise click.BadParameter(f"未知源: {source}")


def _render_trend_table(items, *, title: str) -> None:
    table = Table(title=title, show_lines=False, header_style="bold cyan")
    table.add_column("#", style="dim", width=3)
    table.add_column("标题", overflow="fold", ratio=3)
    table.add_column("热度", style="yellow", width=18)
    table.add_column("URL", style="blue", overflow="ellipsis", ratio=2)
    for i, item in enumerate(items, 1):
        table.add_row(str(i), item.title, item.hot, item.url)
    console.print(table)


# ---------- 子命令 ----------


@click.group()
@click.version_option()
def main():
    """🔥 hot-trend: 从全网热榜中发现可孵化的 AI 项目机会。

        流程：采集 (scan) → 洞察 + 评分 (analyze) → 机会卡
    """


@main.command()
@click.option(
    "-s",
    "--source",
    type=click.Choice(["github", "hn", "v2ex"]),
    default="github",
    show_default=True,
    help="采集源",
)
@click.option(
    "-l", "--limit", type=int, default=15, show_default=True, help="最多条数"
)
@click.option(
    "--language",
    default="",
    help="（仅 GitHub）语言过滤，如 python。留空=全部",
)
def scan(source: str, limit: int, language: str):
    """📊 扫热榜 — 只采集展示，不分析。"""
    console.print(f"\n[bold cyan]扫描源：[/] [yellow]{source}[/] · 条数 {limit}\n")
    try:
        if source == "github":
            from .sources import github_trending

            items = github_trending.fetch(limit=limit, language=language)
        else:
            items = _fetch_source(source, limit)  # type: ignore[arg-type]
    except Exception as e:
        console.print(f"[red]采集失败：[/] {e}")
        sys.exit(1)

    if not items:
        console.print("[yellow]未抓到任何条目。[/]")
        return

    title = f"{source.upper()} Trending · 共 {len(items)} 条"
    _render_trend_table(items, title=title)

    console.print(
        "\n[dim]提示：对感兴趣的条目，复制 URL 跑 [/]"
        "[bold]hot-trend analyze <url>[/]"
    )


@main.command()
@click.argument("url")
@click.option(
    "--source-name",
    default="manual",
    help="标注来源（manual/github/hn/v2ex），写入机会卡",
)
@click.option(
    "--no-save", is_flag=True, help="只终端预览，不写盘（默认会写到 opportunities/cards/）"
)
def analyze(url: str, source_name: str, no_save: bool):
    """🔍 分析单条 URL — 抽取正文 → LLM 洞察 → LLM 评分 → 机会卡。

    URL 可以是 GitHub repo / HN 帖 / V2EX 帖 / 知乎专栏 / 博客 等。
    """
    cfg = load_config()

    # 校验 API key 提前提示
    if not cfg.llm.api_key:
        console.print(
            Panel(
                f"[red]✗ LLM API key 未设置[/]\n\n"
                f"provider=[bold]{cfg.llm.provider}[/]\n"
                f"请在项目根目录创建 [/][bold].env[/][dim] 文件，加入对应的 key，"
                f"或设置环境变量。\n"
                f"参考 [/][bold].env.example[/]",
                title="配置错误",
                border_style="red",
            )
        )
        sys.exit(2)

    console.print(f"\n[bold cyan]🔍 分析中：[/] [blue]{url}[/]")
    console.print(f"[dim]LLM: {cfg.llm.provider} / {cfg.llm.model}\n")

    try:
        with console.status("[bold green]抽取正文..."):
            from .extractor import extract

            article = extract(url)
        console.print(
            f"[green]✓ 正文抽取[/] ({len(article.content)} chars, method={article.method})"
        )

        from .llm import LLMClient

        client = LLMClient(cfg.llm)
        from .analyzer import _llm_insight, _llm_score  # type: ignore[name-defined]
        from .models import Insight, Score

        with console.status("[bold green]LLM 洞察中（第 1 步）..."):
            insight: Insight = _llm_insight(
                client, title=article.title or url, content=article.content
            )
        console.print("[green]✓ 洞察完成[/]")

        with console.status("[bold green]LLM 评分中（第 2 步）..."):
            score: Score = _llm_score(client, insight)
        console.print(f"[green]✓ 评分完成[/] — [bold]{score.total}/30[/]")

    except Exception as e:
        console.print(f"\n[red]✗ 分析失败：[/] {e}")
        sys.exit(1)

    # 组装卡片（id 先占位 0，save_card 会分配真实 id）
    from datetime import date as _date

    from .models import OpportunityCard

    card = OpportunityCard(
        id=0,
        source=source_name,
        source_url=url,
        discovered_at=_date.today(),
        title=insight.surface_topic or article.title or url,
        insight=insight,
        score=score,
    )

    # 终端预览
    md = render_card_md(card)
    console.print(
        Panel(
            md,
            title=f"机会卡预览 · {verdict_for(score.total)}",
            border_style="green" if score.total >= 22 else "yellow",
        )
    )

    # 写盘
    if no_save:
        console.print("\n[dim]--no-save 模式，未写盘[/]")
        return

    saved = save_card(card, cfg.opportunities_dir)
    console.print(f"\n[bold green]✓ 已保存：[/] {saved}")


if __name__ == "__main__":
    main()
