"""
市场发现模块 — 从已采集的热点数据发现 KB 里还没有的新厂商/工具/服务

信号源:
  热点召回（被动）: storage.load_latest() → 科技/产品类源 → 关键词命中 → 未知实体候选

设计说明:
  原计划的"生态页抓取"已移除——实测厂商 plan 页无标准化的"支持工具列表"DOM，
  通用关键词+通用标签抓取会产出整页导航噪声（"客户支持""云市场"等），且无法可靠
  区分。如需补充生态信息，应改为按厂商定制选择器，或由 /kb-update 审阅时人工录入。
  本模块坚持"零新增数据源"，只复用 engine.py 已采集的热点。

输出: data/signals/market-{date}.json
"""

import asyncio
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import httpx

from . import storage

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
KB_DIR = PROJECT_ROOT / "data" / "knowledge-base"
SIGNALS_DIR = PROJECT_ROOT / "data" / "signals"

# ── 关键词配置 ────────────────────────────────────────

# 新厂商/工具/服务发现关键词
DISCOVERY_KEYWORDS = [
    # 新工具/产品
    "发布", "上线", "推出", "开源", "公测", "内测", "发布",
    "新的", "全新", "首个", "正式版", "1.0",
    # 工具类型
    "AI IDE", "AI编程", "代码助手", "编程助手", "AI 编程", "AI 代码",
    "Coding Plan", "Token Plan", "Agent Plan",
    "CLI", "插件", "MCP", "Agent",
    # 模型
    "新模型", "模型发布", "模型升级",
    # 厂商
    "AI模型", "大模型", "MaaS", "聚合", "API 平台",
]

# 排除词（已知厂商/工具名，避免重复发现）
EXCLUDE_PATTERNS = [
    "智谱", "GLM", "DeepSeek", "Kimi", "MiniMax", "腾讯云", "阿里",
    "百炼", "字节", "方舟", "Claude", "Anthropic", "OpenAI", "Codex",
    "GitHub", "Copilot", "小米", "MiMo", "百度", "千帆", "Cursor",
    "Windsurf", "Cline", "Trae", "OpenCode", "Qoder", "ZCode",
    "OpenRouter", "硅基流动", "Tabnine", "Cody", "Replit", "Continue",
    "Augment", "Hermes", "WorkBuddy", "Codeium", "Gemini", "Amazon Q",
    "通义灵码", "CodeBuddy", "CodeGeeX", "Comate", "iFlyCode",
]

# 来源过滤: 只从科技/产品类源发现
DISCOVERY_SOURCES = {"36kr", "ithome", "sspai", "juejin", "v2ex", "zhihu", "weibo"}


def load_kb_vendor_names() -> set[str]:
    """加载 KB 中已知的厂商名和工具名"""
    known = set()
    for fname in ["vendors.json", "tools.json"]:
        path = KB_DIR / fname
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            for item in data:
                known.add(item.get("name", ""))
                known.add(item.get("id", ""))
                if "vendorName" in item:
                    known.add(item["vendorName"])
    return known


# ── 信号 1: 热点召回 ──────────────────────────────────

async def scan_hot_items(client: httpx.AsyncClient) -> list[dict]:
    """从已采集热点数据中发现未知实体"""
    items = storage.load_latest(limit=500)
    if not items:
        print("  ⚠️ 无热点数据，跳过热点召回")
        return []

    known = load_kb_vendor_names()
    signals = []

    for item in items:
        title = str(item.get("title", ""))
        source = str(item.get("source", ""))
        source_type = str(item.get("source_type", ""))

        # 过滤: 只看科技/产品类源
        if source_type not in DISCOVERY_SOURCES and source not in DISCOVERY_SOURCES:
            continue

        # 关键词命中
        matched_kw = [kw for kw in DISCOVERY_KEYWORDS if kw in title]
        if not matched_kw:
            continue

        # 排除已知实体
        if any(ex in title for ex in EXCLUDE_PATTERNS):
            continue

        # 排除已知厂商名
        already_known = any(k in title for k in known if len(k) >= 3)
        if already_known:
            continue

        # 置信度评估
        confidence = "low"
        if len(matched_kw) >= 3:
            confidence = "high"
        elif len(matched_kw) >= 2:
            confidence = "medium"

        # 推断信号类型
        sig_type = "new_tool_candidate"
        if any(kw in matched_kw for kw in ["模型", "MaaS", "API 平台", "聚合"]):
            sig_type = "new_vendor_candidate"
        elif any(kw in matched_kw for kw in ["Coding Plan", "Token Plan", "Agent Plan"]):
            sig_type = "new_service_candidate"

        signals.append({
            "type": sig_type,
            "name": _extract_entity_name(title),
            "evidence": title,
            "source": f"dailyhot:{source}" if source else "dailyhot",
            "url": item.get("url", ""),
            "keywords": matched_kw,
            "confidence": confidence,
            "reason": f"关键词命中: {', '.join(matched_kw[:3])}",
        })

    # 去重: 按 name 去重，保留最高置信度
    seen = {}
    for s in signals:
        key = s["name"]
        if key not in seen or _confidence_rank(s["confidence"]) > _confidence_rank(seen[key]["confidence"]):
            seen[key] = s

    return list(seen.values())


def _extract_entity_name(title: str) -> str:
    """从标题中提取实体名（简单启发式）"""
    # 匹配书名号中的内容
    m = re.search(r'《(.+?)》', title)
    if m:
        return m.group(1)
    # 匹配引号中的内容
    m = re.search(r'["""](.+?)["'']', title)
    if m:
        return m.group(1)
    # 匹配"推出/发布 XXX"模式
    m = re.search(r'(?:推出|发布|上线|开源)\s*[：:]?\s*(\S{2,12})', title)
    if m:
        return m.group(1)
    # fallback: 用标题前 30 字
    return title[:30]


def _confidence_rank(c: str) -> int:
    return {"high": 3, "medium": 2, "low": 1}.get(c, 0)


# ── 信号 2: 生态页抓取（已禁用）──────────────────────
#
# 以下两个函数保留为占位，记录原设计意图。实测厂商 plan 页无标准化的"支持工具列表"
# DOM，通用抓取会产出导航噪声（见模块 docstring）。如需恢复，应改为按厂商定制选择器。
# 当前 run() 不调用它们。

async def scan_ecosystem_pages(client: httpx.AsyncClient) -> list[dict]:
    """[已禁用] 厂商生态页抓取——产出导航噪声，已从 run() 移除。保留函数以记录设计。"""
    return []


# ── 主入口 ────────────────────────────────────────────

async def run() -> str:
    """主入口：热点召回 → 保存（生态页抓取已禁用，见模块 docstring）"""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    date_str = ts[:10]
    print(f"🔍 市场发现 — {ts}")

    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        hot_signals = await scan_hot_items(client)

    print(f"  热点召回: {len(hot_signals)} 条")

    SIGNALS_DIR.mkdir(parents=True, exist_ok=True)
    out = SIGNALS_DIR / f"market-{date_str}.json"
    out.write_text(json.dumps({
        "timestamp": ts,
        "count": len(hot_signals),
        "hot_signals": len(hot_signals),
        "signals": hot_signals,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ {out}")
    return str(out)


def main():
    asyncio.run(run())


if __name__ == "__main__":
    main()