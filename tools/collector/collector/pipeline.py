"""
统一数据更新管道 — 按顺序运行采集和信号检测，产出"待审阅"候选

用法: python -m collector.pipeline

流程:
  1. engine.py            → 采集热点数据到 data/raw/
  2. article_discovery.py → 关键词召回候选文章到 data/pending/{date}/articles.json
  3. price_monitor.py     → 检测价格变动信号到 data/signals/{date}.json
  4. sources/runner.py    → Playwright/BS4 自动提取 7 家厂商定价
  5. sources/merge.py     → 合并提取结果到 plans.json
  6. token_estimator.py   → 推算 Token 用量, 更新 plans.json（纯计算）
  7. 生成统一待审阅报告 → data/pending/{date}/report.md

注意: article_discovery 不再直接写入 changes.json。
      编辑决策（哪些文章收录、哪些价格变动记录）由 Claude Code 通过
      /codingplan-page update 完成——读 data/pending/ → 去噪 → 用户确认 → 写入。
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
REPORTS_DIR = PROJECT_ROOT / "data" / "pipeline-reports"
PENDING_DIR = PROJECT_ROOT / "data" / "pending"
SIGNALS_DIR = PROJECT_ROOT / "data" / "signals"


def run_step(name: str, module: str) -> bool:
    """运行一个子模块，返回是否成功"""
    print(f"\n{'='*60}")
    print(f"  {name}")
    print(f"{'='*60}")
    result = subprocess.run(
        [sys.executable, "-m", f"collector.{module}"],
        cwd=str(PROJECT_ROOT / "tools" / "collector"),
        capture_output=False,
    )
    return result.returncode == 0


def generate_pending_report(date_str: str) -> Path:
    """汇总所有待审阅候选，生成统一报告"""
    out_dir = PENDING_DIR / date_str
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / "report.md"

    # 读取候选文章
    articles = []
    articles_path = out_dir / "articles.json"
    if articles_path.exists():
        with open(articles_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            articles = data.get("candidates", [])

    # 读取价格信号（跳过 extract- 文件，它们是 sources/runner 的提取结果）
    signals = []
    for sig_file in sorted(SIGNALS_DIR.glob("*.json"), reverse=True):
        if sig_file.name.startswith("extract-"):
            continue
        with open(sig_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            sigs = data.get("signals", [])
            if sigs:
                signals.extend(sigs)
        break  # 只取最新

    # 生成报告
    lines = [
        f"# 待审阅变更 — {date_str}",
        "",
        f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "---",
        "",
        f"## 📰 候选文章 ({len(articles)} 篇)",
        "",
    ]

    if articles:
        lines.append("| # | Level | 标题 | 来源 |")
        lines.append("|---|-------|------|------|")
        for i, a in enumerate(articles, 1):
            level_emoji = "🔴" if a.get("level") == "high" else "🟡"
            lines.append(
                f"| {i} | {level_emoji} | {a['title'][:60]} | {a.get('author', '?')} |"
            )
    else:
        lines.append("无候选文章。")

    lines.extend([
        "",
        f"## 📡 价格信号 ({len(signals)} 条)",
        "",
    ])

    if signals:
        for s in signals:
            lines.append(f"- [{s.get('type', '?')}] {s.get('vendor', '?')}: {s.get('message', '?')}")
    else:
        lines.append("无价格信号。")

    lines.extend([
        "",
        "---",
        "",
        "## 下一步",
        "",
        "在 Claude Code 中运行 `/codingplan-page update`，读取本报告并：",
        "1. 审阅候选文章 → 去噪收录到 changes.json",
        "2. 审阅价格信号 → 更新 plans.json + changes.json",
        "3. 运行 `/codingplan-page build` 重新生成 HTML",
    ])

    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path


def main():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    date_str = datetime.now().strftime("%Y-%m-%d")
    print(f"Hot Trend 数据更新管道")
    print(f"启动时间: {timestamp}")
    print(f"模式: 候选产出（不直接修改生产数据）")
    print(f"")

    results = {}

    # Step 1: 采集热点数据
    results["热点采集"] = run_step("Step 1/5: 采集热点数据", "engine")

    # Step 2: 文章发现 → data/pending/{date}/articles.json
    results["文章发现"] = run_step("Step 2/5: 关键词召回候选文章", "article_discovery")

    # Step 3: 价格监控 → data/signals/{date}.json
    results["价格监控"] = run_step("Step 3/5: 价格变动检测", "price_monitor")

    # Step 4: 厂商定价提取 → data/signals/extract-{date}.json
    results["定价提取"] = run_step("Step 4/5: 厂商定价自动提取", "sources.runner")

    # Step 4b: 合并提取结果到 plans.json
    try:
        from .sources.merge import merge_from_extract
        merge_stats = merge_from_extract(date_str)
        results["定价合并"] = merge_stats["updated"] > 0
        print(f"  📊 plans.json: {merge_stats['updated']} vendors updated")
    except Exception as e:
        results["定价合并"] = False
        print(f"  ⚠️  合并失败: {e}")

    # Step 5: Token 推算 → plans.json（纯计算，直接写入）
    results["Token推算"] = run_step("Step 5/5: Token 用量推算", "token_estimator")

    # 生成待审阅报告
    print(f"\n{'='*60}")
    print(f"  生成待审阅报告")
    print(f"{'='*60}")
    report_path = generate_pending_report(date_str)
    print(f"  报告: {report_path}")

    # 汇总
    print(f"\n{'='*60}")
    print(f"  管道汇总")
    print(f"{'='*60}")
    for name, ok in results.items():
        status = "✅" if ok else "❌"
        print(f"  {status} {name}")

    # 保存管道报告
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORTS_DIR / f"{date_str}.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"# 数据更新报告 - {timestamp}\n\n")
        f.write(f"模式: 候选产出\n\n")
        for name, ok in results.items():
            f.write(f"- [{'OK' if ok else 'FAIL'}] {name}\n")
        f.write(f"\n待审阅: data/pending/{date_str}/report.md\n")

    print(f"\n管道报告: {report_path}")
    print(f"待审阅: data/pending/{date_str}/report.md")
    print(f"\n💡 下一步: 在 Claude Code 中运行 /codingplan-page update 审阅候选")


if __name__ == "__main__":
    main()