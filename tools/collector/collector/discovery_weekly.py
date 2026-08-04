"""一次性脚本: 加载最近 7 天原始数据 → 复用 prefilter 逻辑 → 生成周报 discovery-input.json。

用法:
    cd tools/collector && uv run python -m collector.discovery_weekly
"""

from datetime import datetime, timedelta, timezone

from collector import discovery_prefilter as dp
from collector import storage

DAYS = 7


def main() -> None:
    today = datetime.now(timezone.utc)
    from_date = (today - timedelta(days=DAYS - 1)).strftime("%Y-%m-%d")
    to_date = today.strftime("%Y-%m-%d")
    label = f"{from_date}~{to_date}"

    print(f"📥 加载原始数据范围: {label}")
    items = storage.load_date_range(from_date, to_date)
    print(f"  原始条数: {len(items)}")

    # 复用 prefilter 的去重/排序逻辑，但用 balanced 采样（按 source_type 均衡，
    # 强制混入大众/消费/生活类声量，解决"输出全偏技术"的结构性偏差）
    original_load_latest = storage.load_latest
    storage.load_latest = lambda limit=500: items[:limit]
    try:
        picked = dp.prefilter_balanced(top_n=120)
    finally:
        storage.load_latest = original_load_latest

    out_path = dp.save_input(picked, date_str=f"weekly-{label}")
    print(f"✅ {out_path}")
    print(f"   周报输入: {len(picked)} 条 (来自 {DAYS} 天)")


if __name__ == "__main__":
    main()
