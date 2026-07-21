"""
统一数据更新管道 — 按顺序运行所有采集和更新工具

用法: python -m collector.pipeline

流程:
  1. engine.py          → 采集热点数据到 data/raw/
  2. article_discovery.py → 从热点中提取文章, 更新 articles.json
  3. price_monitor.py   → 检测价格变动信号, 生成报告
  4. token_estimator.py → 推算 Token 用量, 更新 plans.json
  5. 输出汇总报告
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
REPORTS_DIR = PROJECT_ROOT / "data" / "pipeline-reports"


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


def main():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Hot Trend 数据更新管道")
    print(f"启动时间: {timestamp}")
    print(f"")

    results = {}

    # Step 1: 采集热点数据
    results["热点采集"] = run_step("Step 1/4: 采集热点数据", "engine")

    # Step 2: 文章发现
    results["文章发现"] = run_step("Step 2/4: 发现热点文章", "article_discovery")

    # Step 3: 价格监控
    results["价格监控"] = run_step("Step 3/4: 价格变动检测", "price_monitor")

    # Step 4: Token 推算
    results["Token推算"] = run_step("Step 4/4: Token 用量推算", "token_estimator")

    # 汇总
    print(f"\n{'='*60}")
    print(f"  更新汇总")
    print(f"{'='*60}")
    for name, ok in results.items():
        status = "OK" if ok else "FAIL"
        print(f"  [{status}] {name}")

    # 保存报告
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORTS_DIR / f"{datetime.now().strftime('%Y-%m-%d')}.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"# 数据更新报告 - {timestamp}\n\n")
        for name, ok in results.items():
            f.write(f"- [{ 'OK' if ok else 'FAIL' }] {name}\n")

    print(f"\n报告: {report_path}")


if __name__ == "__main__":
    main()