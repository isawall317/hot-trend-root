"""
厂商一览表生成器 — 从 project/codingplan-saver/data/ 直接生成 vendors-and-tools.md

数据源: project/codingplan-saver/data/vendors.json + plans.json
输出:   project/codingplan-saver/vendors-and-tools.md（或 docs/ 下）

用法: cd tools/collector && uv run python -m collector.kb_to_md
"""

import json
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DATA_DIR = PROJECT_ROOT / "project" / "codingplan-saver" / "data"
OUTPUT = PROJECT_ROOT / "project" / "codingplan-saver" / "vendors-and-tools.md"

STRATEGY_DISPLAY = {
    "playwright": "Playwright",
    "bs4": "BS4 静态",
    "httpx": "BS4 静态",
    "docs": "BS4 静态",
    "api": "API",
    "manual": "manual",
}

CATEGORY_DISPLAY = {
    "model-maker": "模型厂商",
    "cloud-maas": "云厂商 MaaS",
    "aggregator": "聚合商",
    "vertical-cloud": "垂直云",
}


def load(filename: str):
    path = DATA_DIR / filename
    if not path.exists():
        print(f"⚠️  文件不存在: {path}")
        return [] if filename != "vendors.json" else []
    return json.loads(path.read_text(encoding="utf-8"))


def generate():
    vendors = load("vendors.json")
    plans = load("plans.json")

    now = datetime.now().strftime("%Y-%m-%d")
    header = f"""# 厂商与套餐数据源

> **定位**：本项目跟踪的厂商和套餐的源头清单。
> **本文件由 `kb_to_md.py` 从 `project/codingplan-saver/data/` 自动生成，勿手工编辑。**
> 最后更新：{now}

---

"""

    sections = [
        generate_vendor_table(vendors),
        "---",
        "",
        generate_plan_table(plans),
        "---",
        "",
        "## 三、更新规则",
        "",
        "1. **新增厂商** → 编辑 `project/codingplan-saver/data/vendors.json` → 运行 `kb_to_md.py` 重新生成",
        "2. **URL 变更** → 编辑 `vendors.json` 的 `urls` 字段 → 运行 `kb_to_md.py`",
        "3. **价格变动** → 自动采集管道检测 → `/codingplan-page update` 审阅 → 更新 `plans.json`",
        "4. **推广链接** → 编辑 `vendors.json` 的 `urls.affiliate` → 重新构建 HTML",
        "",
        "> 唯一真相源：`project/codingplan-saver/data/*.json`（详见 `SCHEMA.md`）",
    ]

    OUTPUT.write_text(header + "\n".join(sections), encoding="utf-8")
    print(f"✅ 已生成: {OUTPUT}")
    print(f"   厂商: {len(vendors)} 家 | 套餐: {len(plans)} 条")


def generate_vendor_table(vendors: list[dict]) -> str:
    lines = [
        "## 一、AI 模型厂商（7 家核心跟踪）",
        "",
        "> 定价页 URL 用于采集，推广链接用于\"优惠购买\"按钮。",
        "",
        "| ID | 厂商 | 分类 | 定价页 URL | 提取策略 | 推广链接 | 备注 |",
        "|----|------|:--:|------|:--:|------|------|",
    ]

    for v in vendors:
        urls = v.get("urls", {})
        aff = urls.get("affiliate", "")
        aff_text = aff if aff else "待添加"

        strategy = STRATEGY_DISPLAY.get(v.get("extractStrategy", "manual"), "manual")
        category = CATEGORY_DISPLAY.get(v.get("category", ""), v.get("category", ""))
        pricing_url = urls.get("pricing", "") or urls.get("home", "")
        notes = (v.get("notes") or "")[:60]

        lines.append(
            f"| {v['id']} | {v['name']} | {category} | "
            f"{pricing_url} | {strategy} | {aff_text[:40]} | {notes} |"
        )

    lines.extend([
        "",
        "提取策略：`Playwright` = 渲染 SPA 后解析 | `BS4 静态` = 直接解析文档页 | `manual` = 人工定期检查",
    ])
    return "\n".join(lines)


def generate_plan_table(plans: list[dict]) -> str:
    lines = [
        "## 二、套餐数据（20 条）",
        "",
        "| 厂商 | 套餐 | 类型 | 月费 | 月 Token | 每元 Token | 状态 |",
        "|------|------|------|------|---------|-----------|------|",
    ]

    for p in sorted(plans, key=lambda x: (x["vendor"], x.get("monthlyPrice") or 0)):
        price = p.get("monthlyPrice")
        price_str = f"¥{price}" if isinstance(price, (int, float)) else "按量"
        token = p.get("measuredMonthlyToken")
        token_str = f"{token}M" if isinstance(token, (int, float)) else "—"
        if isinstance(price, (int, float)) and isinstance(token, (int, float)) and price > 0:
            tpu = f"{token / price:.2f}"
        else:
            tpu = "—"
        status = p.get("status", "active")
        lines.append(
            f"| {p['vendor']} | {p['plan']} | {p['type']} | "
            f"{price_str} | {token_str} | {tpu} | {status} |"
        )

    return "\n".join(lines)


if __name__ == "__main__":
    generate()
