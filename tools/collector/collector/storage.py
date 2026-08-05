"""storage shim — 再导出 qsources.storage，data_dir 预绑死到本项目 data/。

下游 maintenance_scanner / price_monitor / market_discovery / discovery_weekly
仍按原签名调用（不带 data_dir），落盘位置 hot-trend-root/data/raw/ 不变。

唯一真相源已迁到 qsources.storage（参数化 data_dir），本文件只做项目绑死。
"""

from __future__ import annotations

from pathlib import Path

from qsources.storage import (
    save_raw as _save_raw,
    load_latest as _load_latest,
    load_date_range as _load_date_range,
)

# 项目根目录（相对此文件: tools/collector/collector/storage.py → 4 层上）
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
_DATA_DIR = PROJECT_ROOT / "data"


def save_raw(items: list[dict], timestamp: str) -> Path:
    """将采集数据保存为 JSON（落 data/raw/<date>/<ts>.json）。"""
    return _save_raw(items, timestamp, data_dir=_DATA_DIR)


def load_latest(limit: int = 500) -> list[dict]:
    """加载最近一次采集的数据。"""
    return _load_latest(limit=limit, data_dir=_DATA_DIR)


def load_date_range(from_date: str, to_date: str | None = None) -> list[dict]:
    """加载指定日期范围内的数据。"""
    return _load_date_range(from_date, to_date, data_dir=_DATA_DIR)
