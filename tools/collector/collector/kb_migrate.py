"""
知识库迁移脚本 — 从现有数据源迁移到统一 KB JSON

源数据:
  - project/codingplan-saver/data/vendors.json  → kb/vendors.json
  - project/codingplan-saver/data/plans.json    → kb/services.json
  - project/coding-tools/data/tools.json         → kb/tools.json
  - plans.json 中的 models 字段                  → kb/models.json
  - project/codingplan-saver/data/changes.json   → kb/changes.json

用法: python -m collector.kb_migrate
"""

import json
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
KB_DIR = PROJECT_ROOT / "aikb" / "database"

# ── 源数据路径 ────────────────────────────────────────────
OLD_VENDORS = PROJECT_ROOT / "project" / "codingplan-saver" / "data" / "vendors.json"
OLD_PLANS = PROJECT_ROOT / "project" / "codingplan-saver" / "data" / "plans.json"
OLD_TOOLS = PROJECT_ROOT / "project" / "coding-tools" / "data" / "tools.json"
OLD_CHANGES = PROJECT_ROOT / "project" / "codingplan-saver" / "data" / "changes.json"

# ── 手动维护的额外信息（从 vendors-and-tools.md 补充）─────
# 推广链接详情
AFFILIATE_DETAILS = {
    "zhipu": {"type": "referral", "benefit": "新用户得 2000万 Tokens"},
    "kimi": {"type": "referral", "benefit": "注册推广，返佣待确认"},
    "minimax": {"type": "referral", "benefit": "好友 9折 + 10% 返利"},
    "tencent": {"type": "referral", "benefit": "云推荐奖励"},
    "mimo": {"type": "referral", "benefit": "双方各得 ¥10 体验金 + 首单 9 折"},
    "bailian": {"type": "referral", "benefit": "阿里云推广返佣"},
}

# 厂商国家映射
VENDOR_COUNTRY = {
    "zhipu": "cn", "deepseek": "cn", "kimi": "cn", "minimax": "cn",
    "tencent": "cn", "bytedance": "cn", "bailian": "cn", "mimo": "cn",
    "baidu": "cn", "jd": "cn", "siliconflow": "cn",
    "claude": "us", "codex": "us", "github": "us",
    "openrouter": "global",
    "opencode": "global",
    # 第一批回填厂商（2026-07-31）
    "unicom": "cn", "huawei": "cn", "xunfei": "cn", "ctyun": "cn",
    "cmcc": "cn", "infini": "cn", "scnet": "cn", "uyun": "cn",
    "zhipu-intl": "global", "stepfun": "cn", "taotoken": "cn",
    "ollama": "global",
}

# 厂商 mass 服务类型（从现有 plans 数据反推 + 手动补充）
VENDOR_MASS_SERVICES = {
    "zhipu": ["coding-plan", "api-paygo"],
    "deepseek": ["api-paygo"],
    "kimi": ["coding-plan", "api-paygo"],
    "minimax": ["token-plan", "api-paygo"],
    "tencent": ["coding-plan", "token-plan", "api-paygo"],
    "bytedance": ["coding-plan", "agent-plan", "api-paygo"],
    "bailian": ["coding-plan", "token-plan", "api-paygo"],
    "claude": ["coding-plan", "api-paygo"],
    "codex": ["coding-plan", "api-paygo"],
    "github": ["coding-plan", "token-plan"],
    "mimo": ["token-plan", "api-paygo"],
    "baidu": ["coding-plan", "token-plan", "api-paygo"],
    "openrouter": ["api-paygo"],
    "siliconflow": ["api-paygo"],
    # 第一批回填厂商（2026-07-31）—— 按 recovery plans.json 的 type 反推
    "unicom": ["coding-plan", "token-plan"],
    "huawei": ["token-plan"],
    "xunfei": ["coding-plan"],
    "ctyun": ["coding-plan"],
    "cmcc": ["coding-plan"],
    "jd": ["coding-plan"],
    "infini": ["coding-plan"],
    "scnet": ["coding-plan"],
    "uyun": ["coding-plan"],
    "zhipu-intl": ["coding-plan"],
    "stepfun": ["coding-plan"],
    "taotoken": ["coding-plan"],
    "ollama": ["coding-plan"],
    "opencode": ["token-plan"],
}

# 提取策略映射（vendors.json 旧值 → 新值）
STRATEGY_MAP = {
    "docs": "playwright",  # 大部分 docs 实际用 Playwright
    "httpx": "bs4",
    "api": "api",
    "manual": "manual",
}

# BS4 静态的实际厂商
BS4_VENDORS = {"deepseek", "minimax", "tencent"}


def migrate_vendors() -> list[dict]:
    """从旧 vendors.json 迁移到 KB 格式"""
    with open(OLD_VENDORS, "r", encoding="utf-8") as f:
        old_vendors = json.load(f)

    kb_vendors = []
    for v in old_vendors:
        # 提取策略
        strategy = v.get("extractStrategy", "manual")
        if strategy == "docs" and v["id"] in BS4_VENDORS:
            strategy = "bs4"
        elif strategy == "docs":
            strategy = "playwright"

        # 推广信息
        aff = {"url": v.get("urls", {}).get("affiliate", ""), "type": "none", "benefit": ""}
        if v["id"] in AFFILIATE_DETAILS:
            aff.update(AFFILIATE_DETAILS[v["id"]])
        if not aff["url"]:
            aff["type"] = "none"

        kb_vendor = {
            "id": v["id"],
            "name": v["name"],
            "logo": v.get("logo", v["name"][0]),
            "color": v.get("color", "#71717B"),
            "category": v.get("category", "model-maker"),
            "country": VENDOR_COUNTRY.get(v["id"], "cn"),
            "urls": {
                "home": v.get("urls", {}).get("home", ""),
                "pricing": v.get("urls", {}).get("pricing", ""),
                "docs": v.get("urls", {}).get("docs", ""),
                "api": v.get("urls", {}).get("api", ""),
                "console": v.get("urls", {}).get("console", ""),
            },
            "extractStrategy": strategy,
            "extractStatus": "ok" if strategy != "manual" else "manual",
            "massServices": VENDOR_MASS_SERVICES.get(v["id"], []),
            "affiliate": aff,
            "lastVerified": v.get("lastVerified"),
            "notes": v.get("notes", ""),
        }
        kb_vendors.append(kb_vendor)

    return kb_vendors


def migrate_services() -> list[dict]:
    """从旧 plans.json 迁移到 KB services 格式"""
    with open(OLD_PLANS, "r", encoding="utf-8") as f:
        old_plans = json.load(f)

    # 按 vendorId + type 分组
    groups: dict[str, dict] = {}
    for p in old_plans:
        vendor_id = p["vendorId"]
        svc_type = p.get("type", "Coding Plan")

        # 标准化 type
        type_map = {
            "Coding Plan": "coding-plan",
            "Token Plan": "token-plan",
            "API 按量": "api-paygo",
            "Agent Plan": "agent-plan",
        }
        kb_type = type_map.get(svc_type, svc_type.lower().replace(" ", "-"))

        key = f"{vendor_id}-{kb_type}"
        if key not in groups:
            groups[key] = {
                "id": key,
                "vendorId": vendor_id,
                "type": kb_type,
                "name": svc_type,
                "status": "active",
                "plans": [],
                "billingCore": p.get("billingCore", "token"),
                "migration": p.get("migration", ""),
                "updatedAt": p.get("updatedAt", ""),
                "source": p.get("source", "manual"),
            }

        plan_tier = {
            "tier": p.get("tier", "pro"),
            "name": p.get("plan", ""),
            "monthlyPrice": p.get("monthlyPrice"),
            "currency": p.get("currency", "¥"),
            "firstMonthPrice": p.get("firstMonthPrice"),
            "monthlyRequests": p.get("monthlyRequests"),
            "tokenLimit": p.get("tokenLimit"),
            "measuredMonthlyToken": p.get("measuredMonthlyToken"),
            "rating": p.get("rating", 3),
            "models": p.get("models", []),
            "tags": p.get("tags", []),
            "bloggerVerdict": p.get("bloggerVerdict", ""),
            "status": p.get("status", "active"),
        }
        groups[key]["plans"].append(plan_tier)

        # 更新 service 级别的字段
        if p.get("updatedAt", "") > groups[key]["updatedAt"]:
            groups[key]["updatedAt"] = p["updatedAt"]
        if p.get("migration"):
            groups[key]["migration"] = p["migration"]

    return list(groups.values())


# 国产厂商工具补充清单 —— tools.json 未收录，从 docs/vendors-and-tools.md 历史记录恢复。
# 这些是厂商官方出的编程工具（CodeGeeX/通义灵码/Comate 等），丢失会让 KB 国产工具断层。
# 仅画像级字段；详细信息待后续 /kb-update 逐步补全。
SUPPLEMENTAL_TOOLS = [
    {
        "id": "codegeex", "name": "CodeGeeX", "vendorId": "zhipu", "vendorName": "智谱AI",
        "type": "ide", "category": "domestic-vendor",
        "description": "智谱AI 官方编程助手，GLM 系列集成。",
        "urls": {"home": "https://bigmodel.cn", "docs": "", "github": ""},
        "tags": ["IDE", "国内", "智谱"], "rating": 3,
    },
    {
        "id": "kimi-code", "name": "Kimi Code", "vendorId": "kimi", "vendorName": "Kimi",
        "type": "unknown", "category": "domestic-vendor",
        "description": "Kimi 官方编程工具，形态待确认。",
        "urls": {"home": "https://kimi.com/code/zh", "docs": "", "github": ""},
        "tags": ["国内", "Kimi", "待确认"], "rating": 3,
    },
    {
        "id": "tongyi-lingma", "name": "通义灵码", "vendorId": "bailian", "vendorName": "阿里·百炼",
        "type": "ide", "category": "domestic-vendor",
        "description": "阿里通义系列集成的编程助手。",
        "urls": {"home": "https://aliyun.com", "docs": "", "github": ""},
        "tags": ["IDE", "国内", "阿里"], "rating": 3,
    },
    {
        "id": "codebuddy", "name": "CodeBuddy", "vendorId": "tencent", "vendorName": "腾讯云",
        "type": "unknown", "category": "domestic-vendor",
        "description": "腾讯 AI 代码助手，形态待确认。",
        "urls": {"home": "https://workbuddy.cn", "docs": "", "github": ""},
        "tags": ["国内", "腾讯", "待确认"], "rating": 3,
    },
    {
        "id": "baidu-comate", "name": "百度 Comate", "vendorId": "baidu", "vendorName": "百度·千帆",
        "type": "ide", "category": "domestic-vendor",
        "description": "百度文心快码编程助手。",
        "urls": {"home": "https://baidu.com", "docs": "", "github": ""},
        "tags": ["IDE", "国内", "百度"], "rating": 3,
    },
    {
        "id": "iflycode", "name": "iFlyCode", "vendorId": "xunfei", "vendorName": "讯飞·星火",
        "type": "ide", "category": "domestic-vendor",
        "description": "讯飞星火官方编程助手。",
        "urls": {"home": "https://xfyun.cn", "docs": "", "github": ""},
        "tags": ["IDE", "国内", "讯飞"], "rating": 3,
    },
    {
        "id": "minimax-code", "name": "MiniMax Code", "vendorId": "minimax", "vendorName": "MiniMax",
        "type": "unknown", "category": "domestic-vendor",
        "description": "MiniMax 官方编程工具，形态待确认。",
        "urls": {"home": "https://agent.minimaxi.com/download", "docs": "", "github": ""},
        "tags": ["国内", "MiniMax", "待确认"], "rating": 3,
    },
    {
        "id": "mimo-code", "name": "MiMo Code", "vendorId": "mimo", "vendorName": "小米·MiMo",
        "type": "unknown", "category": "domestic-vendor",
        "description": "小米 MiMo 官方编程工具，形态待确认。",
        "urls": {"home": "https://mimo.xiaomi.com/zh/mimocode", "docs": "", "github": ""},
        "tags": ["国内", "小米", "待确认"], "rating": 3,
    },
    {
        "id": "kiro", "name": "Kiro", "vendorId": "", "vendorName": "独立",
        "type": "unknown", "category": "unknown",
        "description": "信息待确认。",
        "urls": {"home": "", "docs": "", "github": ""},
        "tags": ["待确认"], "rating": 3,
    },
]


def migrate_tools() -> list[dict]:
    """从旧 tools.json 迁移到 KB 格式，并合并国产厂商工具补充清单"""
    with open(OLD_TOOLS, "r", encoding="utf-8") as f:
        old_tools = json.load(f)

    # 工具名 → vendorId 映射
    TOOL_VENDOR_MAP = {
        "Anthropic": "claude",
        "OpenAI": "codex",
        "Google": "google",
        "社区开源": "community",
        "DeepSeek": "deepseek",
        "Cursor Inc": "cursor",
        "GitHub(Microsoft)": "github",
        "Codeium": "windsurf",
        "字节跳动": "bytedance",
        "Sourcegraph": "cody",
        "AWS(Amazon)": "aws",
        "Tabnine": "tabnine",
        "Replit": "replit",
        "Augment": "augment",
        "ZCode Team": "zcode",
        "Hermes AI": "hermes",
        "WorkBuddy Inc": "workbuddy",
        "Continue Dev": "continue",
    }

    kb_tools = []
    for t in old_tools:
        vendor_name = t.get("vendor", "")
        vendor_id = ""
        for k, v in TOOL_VENDOR_MAP.items():
            if k in vendor_name or vendor_name in k:
                vendor_id = v
                break

        kb_tool = {
            "id": t["id"],
            "name": t["name"],
            "vendorId": vendor_id,
            "vendorName": vendor_name,
            "type": t.get("type", "CLI").lower(),
            "category": _infer_tool_category(t),
            "description": t.get("description", ""),
            "pricing": {
                "model": _infer_pricing_model(t.get("pricing", "")),
                "detail": t.get("pricing", ""),
            },
            "modelIntegration": t.get("modelIntegration", []),
            "codingPlanRelation": t.get("codingPlanRelation", ""),
            "features": t.get("features", []),
            "platforms": t.get("platforms", []),
            "rating": t.get("rating", 3),
            "bestFor": t.get("bestFor", []),
            "strengths": t.get("strengths", []),
            "weaknesses": t.get("weaknesses", []),
            "urls": {
                "home": t.get("websiteUrl", ""),
                "docs": "",
                "github": "",
            },
            "tags": t.get("tags", []),
            "featured": t.get("featured", False),
            "trending": t.get("trending", False),
            "addedAt": t.get("addedAt", ""),
        }
        kb_tools.append(kb_tool)

    # 合并国产厂商工具补充清单（tools.json 未收录的厂商官方工具）
    existing_ids = {t["id"] for t in kb_tools}
    for supp in SUPPLEMENTAL_TOOLS:
        if supp["id"] not in existing_ids:
            kb_tools.append(dict(supp))  # copy，避免改常量

    return kb_tools


def _infer_pricing_model(pricing_text: str) -> str:
    """从定价文本推断定价模式"""
    if not pricing_text:
        return "unknown"
    text = pricing_text.lower()
    if "免费" in text and ("订阅" in text or "api key" in text or "自备" in text):
        return "freemium"
    if "完全免费" in text or "免费开源" in text:
        return "free"
    if "订阅" in text or "/月" in text or "/人/月" in text:
        return "subscription"
    return "freemium"


# 国内厂商（有自己的模型/平台）—— 属于"国内·厂商"
DOMESTIC_VENDOR_KEYWORDS = {
    # 模型厂商 / 云厂商
    "字节", "ByteDance", "DeepSeek", "智谱", "Kimi", "MiniMax",
    "阿里", "通义", "腾讯", "百度", "千帆", "讯飞", "小米", "MiMo",
    "CodeGeeX", "Comate", "灵码", "iFlyCode",
}

# 国内独立 / 社区项目 —— 属于"国内·独立"
DOMESTIC_INDEPENDENT_KEYWORDS = {
    "ZCode", "Qoder", "WorkBuddy", "OpenClaw",
}


def _infer_tool_category(tool: dict) -> str:
    """从 vendor 名、id、tags 推断工具分类。

    tools.json 无 category 字段，旧版一律 fallback 到 overseas 导致国产工具全判海外。
    规则:
      - vendor 含国内厂商关键字 → domestic-vendor
      - vendor/id 含国内独立项目关键字 → domestic-independent
      - 否则 → overseas
    """
    vendor = tool.get("vendor", "") or ""
    tid = tool.get("id", "") or ""
    blob = f"{vendor} {tid}"

    if any(kw.lower() in blob.lower() for kw in DOMESTIC_VENDOR_KEYWORDS):
        return "domestic-vendor"
    if any(kw.lower() in blob.lower() for kw in DOMESTIC_INDEPENDENT_KEYWORDS):
        return "domestic-independent"
    return "overseas"


def migrate_models() -> list[dict]:
    """从 plans.json 的 models 字段提取模型清单"""
    with open(OLD_PLANS, "r", encoding="utf-8") as f:
        old_plans = json.load(f)

    models_map: dict[str, dict] = {}
    for p in old_plans:
        vendor_id = p["vendorId"]
        for model_name in p.get("models", []):
            # 跳过聚合描述
            if any(skip in model_name for skip in ["400+", "70+", "任何", "等"]):
                continue
            key = f"{vendor_id}:{model_name.lower()}"
            if key not in models_map:
                models_map[key] = {
                    "id": _model_to_id(model_name),
                    "vendorId": vendor_id,
                    "name": model_name,
                    "type": _infer_model_type(model_name),
                    "status": "active",
                }

    return list(models_map.values())


def _model_to_id(name: str) -> str:
    """模型名 → kebab-case id"""
    return name.lower().replace(" ", "-").replace(".", "-").replace("(", "").replace(")", "")


def _infer_model_type(name: str) -> str:
    """从模型名推断类型"""
    name_lower = name.lower()
    if any(kw in name_lower for kw in ["asr", "voice", "speech", "tts"]):
        return "audio"
    if any(kw in name_lower for kw in ["vision", "v-", "-v", "vl", "video"]):
        return "vision"
    if any(kw in name_lower for kw in ["code", "coder"]):
        return "code"
    if any(kw in name_lower for kw in ["flash", "speed", "lite", "mini", "air", "haiku"]):
        return "text"
    return "text"


def migrate_changes() -> list[dict]:
    """迁移变更时间线"""
    if not OLD_CHANGES.exists():
        return []
    with open(OLD_CHANGES, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    print("📦 知识库迁移 — 从旧数据源迁移到统一 KB JSON")
    KB_DIR.mkdir(parents=True, exist_ok=True)

    # 1. vendors
    print("\n🏢 迁移厂商数据...")
    vendors = migrate_vendors()
    _write_json(KB_DIR / "vendors.json", vendors)
    print(f"   ✅ {len(vendors)} 家厂商")

    # 2. services
    print("📦 迁移服务数据...")
    services = migrate_services()
    _write_json(KB_DIR / "services.json", services)
    plan_count = sum(len(s["plans"]) for s in services)
    print(f"   ✅ {len(services)} 个服务, {plan_count} 个套餐")

    # 3. tools
    print("🛠️  迁移工具数据...")
    tools = migrate_tools()
    _write_json(KB_DIR / "tools.json", tools)
    print(f"   ✅ {len(tools)} 款工具")

    # 4. models
    print("🧠 提取模型清单...")
    models = migrate_models()
    _write_json(KB_DIR / "models.json", models)
    print(f"   ✅ {len(models)} 个模型")

    # 5. changes
    print("📅 迁移变更时间线...")
    changes = migrate_changes()
    _write_json(KB_DIR / "changes.json", changes)
    print(f"   ✅ {len(changes)} 条变更记录")

    # 汇总
    print(f"\n{'='*50}")
    print(f"  知识库迁移完成！")
    print(f"  data/knowledge-base/")
    print(f"    ├── vendors.json   ({len(vendors)} 家)")
    print(f"    ├── services.json  ({len(services)} 个服务)")
    print(f"    ├── tools.json     ({len(tools)} 款)")
    print(f"    ├── models.json    ({len(models)} 个)")
    print(f"    └── changes.json   ({len(changes)} 条)")
    print(f"{'='*50}")


def _write_json(path: Path, data):
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()