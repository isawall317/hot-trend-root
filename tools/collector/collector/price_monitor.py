"""
价格信号扫描器 — 从 DailyHotApi 科技源检测 AI Coding Plan 价格变动信号

输出: data/signals/{date}.json
  [{title, url, source, keywords, vendors, detected_at}, ...]

注: 不再尝试直接爬取 SPA 定价页（实测产垃圾数据）。
    定价页结构化提取由 sources/ 模块负责（按厂商单独实现）。
"""

import asyncio
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import httpx

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
SIGNALS_DIR = PROJECT_ROOT / "data" / "signals"
VENDORS_PATH = PROJECT_ROOT / "project" / "codingplan-saver" / "data" / "vendors.json"
DAILYHOT_BASE = os.getenv("DAILYHOT_BASE", "http://localhost:6688")

# 监测的科技类源
TECH_SOURCES = ["36kr", "ithome", "sspai", "juejin", "v2ex"]

# 关键词（命中任一即列入信号）
PRICE_KEYWORDS = [
    "涨价", "降价", "调价", "价格", "定价", "计费",
    "新套餐", "新增模型", "下架", "售罄", "暂停",
    "Coding Plan", "Token Plan", "月费", "额度",
    "免费", "公测", "限时", "活动", "折扣",
    "倍率", "并发", "请求", "订阅",
]


def load_vendors() -> list[dict]:
    """加载 vendors.json，用于匹配信号中的厂商名"""
    if not VENDORS_PATH.exists():
        return []
    return json.loads(VENDORS_PATH.read_text(encoding="utf-8"))


async def scan_dailyhot(client: httpx.AsyncClient) -> list[dict]:
    """从 DailyHotApi 科技源扫描价格相关信号"""
    vendors = load_vendors()
    signals = []

    for source in TECH_SOURCES:
        try:
            resp = await client.get(f"{DAILYHOT_BASE}/{source}", timeout=15)
            if resp.status_code != 200:
                continue
            items = resp.json().get("data", [])
            for item in items:
                title = str(item.get("title", ""))
                matched_kw = [kw for kw in PRICE_KEYWORDS if kw in title]
                if not matched_kw:
                    continue
                # 匹配厂商名
                matched_vendors = [
                    v["name"] for v in vendors
                    if v["name"] in title or v["id"] in title.lower()
                ] or ["通用"]
                signals.append({
                    "title": title,
                    "url": item.get("url", ""),
                    "source": f"dailyhot:{source}",
                    "keywords": matched_kw,
                    "vendors": matched_vendors,
                    "detected_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                })
        except Exception as e:
            print(f"  ⚠️ DailyHotApi/{source} 失败: {e}")

    return signals


async def run() -> str:
    """主入口：扫描信号 → 保存到 data/signals/{date}.json"""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    date_str = ts[:10]
    print(f"🔍 信号扫描 — {ts}")

    async with httpx.AsyncClient(timeout=30) as client:
        signals = await scan_dailyhot(client)

    print(f"  发现 {len(signals)} 条信号")

    SIGNALS_DIR.mkdir(parents=True, exist_ok=True)
    out = SIGNALS_DIR / f"{date_str}.json"
    out.write_text(json.dumps({
        "timestamp": ts,
        "count": len(signals),
        "signals": signals,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ {out}")
    return str(out)


def main():
    asyncio.run(run())


if __name__ == "__main__":
    main()