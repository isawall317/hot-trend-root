"""
知识库 → Markdown 生成器 — 从 KB JSON 自动生成 docs/vendors-and-tools.md

用法: python -m collector.kb_to_md

自动区块标记:
  <!-- KB-AUTO-START --> ... <!-- KB-AUTO-END -->
  包裹的内容由本脚本自动生成，每次运行覆盖。
  标记外的内容（如"待接入""结算记录"）原样保留，不触碰。
"""

import json
import re
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
KB_DIR = PROJECT_ROOT / "data" / "knowledge-base"
OUTPUT = PROJECT_ROOT / "docs" / "vendors-and-tools.md"

AUTO_START = "<!-- KB-AUTO-START -->"
AUTO_END = "<!-- KB-AUTO-END -->"

# 提取策略显示名
STRATEGY_DISPLAY = {
    "playwright": "Playwright",
    "bs4": "BS4 静态",
    "api": "API",
    "manual": "manual",
}

# 分类显示名
CATEGORY_DISPLAY = {
    "model-maker": "模型厂商",
    "cloud-maas": "云厂商 MaaS",
    "aggregator": "聚合商",
    "vertical-cloud": "垂直云",
}

# 工具分类显示名
TOOL_CATEGORY_DISPLAY = {
    "domestic-vendor": "国内·厂商",
    "domestic-independent": "国内·独立",
    "overseas": "海外",
    "unknown": "待确认",
}

TOOL_TYPE_ICON = {
    "cli": "CLI",
    "ide": "IDE",
    "desktop": "IDE",
    "plugin": "IDE",
    "web": "Web",
}


def generate():
    vendors = _load("vendors.json")
    tools = _load("tools.json")

    # 读取现有 MD（保留手动区块）
    existing_content = ""
    if OUTPUT.exists():
        existing_content = OUTPUT.read_text(encoding="utf-8")

    # 生成 header + 自动区块
    auto_sections = [
        _generate_vendor_table(vendors),
        _generate_tool_table(tools),
    ]

    # 合并：自动区块替换，手动区块保留
    new_content = _merge_content(existing_content, auto_sections)

    OUTPUT.write_text(new_content, encoding="utf-8")
    print(f"✅ 已生成: {OUTPUT}")


def _merge_content(existing: str, auto_sections: list[str]) -> str:
    """将自动区块插入到现有 MD 中。保留标记外的内容。"""
    now = datetime.now().strftime("%Y-%m-%d")

    header = f"""# 厂商与工具数据源

> **定位**：本项目追踪的所有厂商和工具的源头清单。
> **本文件由 `kb_to_md.py` 从 `data/knowledge-base/` JSON 自动生成，勿手工编辑。**
> 最后更新：{now} | 维护者：Frank + Claude Code

---

"""

    # 如果现有文件有自动标记，替换标记内的内容
    if AUTO_START in existing:
        # 提取标记外的内容（header 之前 + 标记之间 + 最后一个标记之后）
        # 简单策略：只保留第一个 AUTO_START 之前和最后一个 AUTO_END 之后的内容
        # 中间所有 AUTO_START...AUTO_END 块替换为新的 auto_sections

        parts = []
        remaining = existing
        auto_idx = 0

        while AUTO_START in remaining:
            # 保留 AUTO_START 之前的内容
            before = remaining.split(AUTO_START, 1)[0]
            parts.append(before)

            if auto_idx < len(auto_sections):
                # 插入新的自动区块
                parts.append(f"{AUTO_START}\n{auto_sections[auto_idx]}\n{AUTO_END}")
                auto_idx += 1

            # 跳到 AUTO_END 之后
            if AUTO_END in remaining:
                remaining = remaining.split(AUTO_END, 1)[1]
            else:
                remaining = ""
                break

        # 剩余未匹配的自动区块追加到末尾
        while auto_idx < len(auto_sections):
            parts.append(f"\n{AUTO_START}\n{auto_sections[auto_idx]}\n{AUTO_END}")
            auto_idx += 1

        parts.append(remaining)
        return header + "".join(parts)
    else:
        # 首次生成：全量输出
        sections = [
            f"{AUTO_START}",
            auto_sections[0],
            f"{AUTO_END}",
            "",
            f"{AUTO_START}",
            auto_sections[1],
            f"{AUTO_END}",
            "",
            "---",
            "",
            "## 三、更新规则",
            "",
            "1. **新增厂商/工具** → 更新 `data/knowledge-base/` JSON → 运行 `python -m collector.kb_to_md` 重新生成此文件",
            "2. **URL 变更** → 更新 KB JSON → 重新生成",
            "3. **数据变更** → 自动采集管道检测 → `/kb-update review` 审阅 → 更新 KB JSON",
            "4. **发现渠道** → 厂商 Token Plan / Coding Plan 页面通常会列出「本套餐支持哪些工具」，这些页面是发现新工具和竞品的最佳入口",
            "",
            "---",
            "",
            "## 四、结算记录",
            "",
            "| 日期 | 平台 | 金额 | 备注 |",
            "|------|------|------|------|",
            "| 待记录 | | | |",
        ]
        return header + "\n".join(sections)


def _generate_vendor_table(vendors: list[dict]) -> str:
    """生成厂商表格"""
    lines = [
        "## 一、AI 模型厂商",
        "",
        "> 定价页 URL 用于采集，推广链接用于\"优惠购买\"按钮。新增厂商先更新 KB JSON → 重新生成此文件。",
        "",
        "| ID | 厂商 | 分类 | 国家 | 定价页 URL | 提取策略 | 推广链接 | 备注 |",
        "|----|------|:--:|:--:|------|:--:|------|------|",
    ]

    for v in vendors:
        aff = v.get("affiliate", {})
        aff_text = ""
        if aff.get("url") and aff["type"] != "none":
            aff_text = aff.get("benefit", aff["type"])
        elif aff.get("type") == "none":
            aff_text = "待添加"

        strategy = STRATEGY_DISPLAY.get(v["extractStrategy"], v["extractStrategy"])
        category = CATEGORY_DISPLAY.get(v["category"], v["category"])
        country_flag = {"cn": "🇨🇳", "us": "🇺🇸", "global": "🌐"}.get(v.get("country", ""), "")

        notes = v.get("notes", "")[:60]
        if v.get("extractStatus") == "manual":
            notes += "（手动维护）"

        urls = v.get("urls", {})
        pricing_url = urls.get("pricing", "") or urls.get("home", "")

        lines.append(
            f"| {v['id']} | {v['name']} | {category} | {country_flag} | "
            f"{pricing_url} | {strategy} | {aff_text} | {notes} |"
        )

    lines.extend([
        "",
        "提取策略：`Playwright` = 渲染 SPA 后解析 | `BS4 静态` = 直接解析文档页 | `API` = JSON API | `manual` = 人工定期检查",
    ])

    return "\n".join(lines)


def _generate_tool_table(tools: list[dict]) -> str:
    """生成工具表格"""
    lines = [
        "## 二、AI 编程工具",
        "",
        "> 新增工具先更新 KB JSON → 重新生成此文件。",
        "",
        "| ID | 工具名 | 厂商 | 分类 | 形态 | 官网 | 定价 | 评分 | 备注 |",
        "|----|--------|------|:--:|:--:|------|------|:--:|------|",
    ]

    for t in tools:
        cat = TOOL_CATEGORY_DISPLAY.get(t.get("category", ""), t.get("category", ""))
        type_icon = TOOL_TYPE_ICON.get(t.get("type", ""), t.get("type", "").upper())
        pricing = t.get("pricing", {})
        pricing_text = pricing.get("detail", "")[:40] if isinstance(pricing, dict) else str(pricing)[:40]
        rating = "⭐" * t.get("rating", 3)
        tags = ", ".join(t.get("tags", [])[:3])
        urls = t.get("urls", {})
        website = urls.get("home", "")

        lines.append(
            f"| {t['id']} | {t['name']} | {t.get('vendorName', '')} | {cat} | {type_icon} | "
            f"{website} | {pricing_text} | {rating} | {tags} |"
        )

    return "\n".join(lines)


def _load(filename: str) -> list:
    path = KB_DIR / filename
    if not path.exists():
        print(f"⚠️  文件不存在: {path}")
        return []
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    generate()