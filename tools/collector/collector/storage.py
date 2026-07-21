"""统一存储 — 将归一化数据写入 data/raw/"""

import json
from datetime import datetime
from pathlib import Path


def save_raw(items: list[dict], timestamp: str) -> Path:
    """将采集数据保存为 JSON 文件

    Args:
        items: 归一化后的数据列表
        timestamp: 采集时间戳

    Returns:
        保存的文件路径
    """
    # 按日期分目录: data/raw/2026-07-20/
    date_str = timestamp[:10]  # "2026-07-20"
    dir_path = Path(__file__).resolve().parent.parent.parent.parent / "data" / "raw" / date_str
    dir_path.mkdir(parents=True, exist_ok=True)

    # 文件名: 2026-07-20T143000Z.json
    time_str = timestamp.replace(":", "").replace("-", "")[:15]  # "20260720T143000Z"
    filepath = dir_path / f"{time_str}.json"

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump({
            "collected_at": timestamp,
            "total": len(items),
            "items": items,
        }, f, ensure_ascii=False, indent=2)

    return filepath


def load_latest(limit: int = 500) -> list[dict]:
    """加载最近一次采集的数据

    Args:
        limit: 最多返回条数

    Returns:
        归一化数据列表
    """
    data_dir = Path(__file__).resolve().parent.parent.parent.parent / "data" / "raw"

    if not data_dir.exists():
        return []

    # 找到最新的日期目录
    date_dirs = sorted(
        [d for d in data_dir.iterdir() if d.is_dir()],
        reverse=True
    )
    if not date_dirs:
        return []

    # 找到最新目录中最新的文件
    json_files = sorted(
        [f for f in date_dirs[0].iterdir() if f.suffix == ".json"],
        reverse=True
    )
    if not json_files:
        return []

    with open(json_files[0], "r", encoding="utf-8") as f:
        data = json.load(f)

    return data.get("items", [])[:limit]


def load_date_range(from_date: str, to_date: str | None = None) -> list[dict]:
    """加载指定日期范围内的数据

    Args:
        from_date: 开始日期 "2026-07-15"
        to_date: 结束日期，None 表示到今天

    Returns:
        归一化数据列表
    """
    data_dir = Path(__file__).resolve().parent.parent.parent.parent / "data" / "raw"

    if not data_dir.exists():
        return []

    if to_date is None:
        to_date = datetime.now().strftime("%Y-%m-%d")

    all_items = []
    for date_dir in sorted(data_dir.iterdir()):
        if not date_dir.is_dir():
            continue
        dir_name = date_dir.name
        if from_date <= dir_name <= to_date:
            for json_file in sorted(date_dir.iterdir()):
                if json_file.suffix == ".json":
                    with open(json_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    all_items.extend(data.get("items", []))

    return all_items