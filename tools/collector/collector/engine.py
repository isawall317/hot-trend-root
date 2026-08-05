"""engine shim — 转调 qsources.collect_all，data_dir 预绑死。

pipeline.py step1 仍 subprocess `python -m collector.engine`（pyproject console
script `collect` 也指向 collector.engine:main），行为不变：抓 DailyHotApi + Folo，
落盘到 hot-trend-root/data/raw/。

采集逻辑（源清单、fetcher、normalize）已迁到 qsources 包，本文件只做项目绑死。
"""

from __future__ import annotations

import asyncio
from pathlib import Path

from qsources import collect_all

# 项目根目录（相对此文件: tools/collector/collector/engine.py → 4 层上）
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent


def main():
    """CLI 入口: python -m collector.engine"""
    asyncio.run(collect_all(data_dir=PROJECT_ROOT / "data"))


if __name__ == "__main__":
    main()
