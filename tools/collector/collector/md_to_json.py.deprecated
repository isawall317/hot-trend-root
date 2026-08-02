"""
MD → JSON 生成器 — 从 aikb/ 的 MD 画像文件生成 database/ 结构化 JSON

用法: python -m collector.md_to_json

MD 文件是 AI 维护的真相源（YAML frontmatter + Markdown 正文）。
本模块解析 frontmatter 生成 database/ 下的 JSON 文件，供下游项目消费。

生成的文件:
  aikb/database/vendors.json   — 厂商画像
  aikb/database/tools.json     — 工具详情
  aikb/database/services.json  — 服务/套餐
  aikb/database/models.json    — 模型清单
  aikb/database/changes.json   — 变更时间线（透传，不从此模块生成）

设计原则:
  - MD 是真相源，database/ JSON 是派生输出
  - 不依赖 pyyaml，用内置解析器处理 frontmatter
  - 生成失败不阻塞 pipeline（KB 变更检测仍可对比 database/ 快照）
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from copy import deepcopy


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
AIKB_DIR = PROJECT_ROOT / "aikb"
DATABASE_DIR = AIKB_DIR / "database"
OLD_KB_DIR = PROJECT_ROOT / "data" / "knowledge-base"


# ── Frontmatter 解析 ──────────────────────────────────────

def parse_frontmatter(text: str) -> dict:
    """解析 YAML frontmatter，返回 dict。

    支持的语法:
      key: value           简单值（str/int/float/bool/null）
      key: "quoted"        引号字符串
      key: [a, b, c]       内联列表
      key:                 嵌套对象（缩进后的子键）
        sub: val
      key:                 列表（以 - 开头）
        - item1
        - item2
      key:
        -                  嵌套对象列表
          sub: val
    """
    # 提取 frontmatter 块
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return {}
    fm_text = m.group(1)

    result = {}
    lines = fm_text.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.strip().startswith("#"):
            i += 1
            continue

        # 计算缩进
        indent = len(line) - len(line.lstrip(" "))
        stripped = line.strip()

        # 匹配 key: value
        kv = re.match(r"^([\w_-]+)\s*:\s*(.*)", stripped)
        if not kv:
            i += 1
            continue

        key = kv.group(1)
        val_str = kv.group(2).strip()

        if val_str == "" or val_str == " ":
            # 空值 → 可能是嵌套对象或列表
            sub_lines = []
            j = i + 1
            while j < len(lines):
                next_line = lines[j]
                next_stripped = next_line.strip()
                if not next_stripped or next_stripped.startswith("#"):
                    j += 1
                    continue
                next_indent = len(next_line) - len(next_line.lstrip(" "))
                if next_indent <= indent:
                    break
                sub_lines.append(next_line)
                j += 1

            if sub_lines and sub_lines[0].strip().startswith("- "):
                # 列表
                result[key] = _parse_list(sub_lines)
            else:
                # 嵌套对象
                result[key] = _parse_nested(sub_lines)
            i = j
        else:
            # 简单值
            result[key] = _parse_value(val_str)
            i += 1

    return result


def _parse_value(raw: str):
    """解析单个值"""
    raw = raw.strip()
    if not raw:
        return None
    # 引号字符串
    if (raw.startswith('"') and raw.endswith('"')) or (raw.startswith("'") and raw.endswith("'")):
        return raw[1:-1]
    # 布尔
    if raw == "true": return True
    if raw == "false": return False
    if raw == "null" or raw == "~": return None
    # 内联列表 [a, b, c]
    if raw.startswith("[") and raw.endswith("]"):
        inner = raw[1:-1].strip()
        if not inner:
            return []
        items = re.split(r",\s*", inner)
        return [_parse_value(it.strip().strip('"').strip("'")) for it in items]
    # 整数
    try:
        if "." not in raw:
            return int(raw)
    except ValueError:
        pass
    # 浮点数
    try:
        return float(raw)
    except ValueError:
        pass
    # 字符串
    return raw


def _parse_list(lines: list[str]) -> list:
    """解析 YAML 列表"""
    result = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            i += 1
            continue
        indent = len(line) - len(line.lstrip(" "))

        m = re.match(r"^-\s+(.*)", stripped)
        if not m:
            i += 1
            continue

        content = m.group(1).strip()

        if content == "":
            # 嵌套对象列表项:  "  - "
            sub_lines = []
            j = i + 1
            while j < len(lines):
                next_line = lines[j]
                next_stripped = next_line.strip()
                if not next_stripped or next_stripped.startswith("#"):
                    j += 1
                    continue
                next_indent = len(next_line) - len(next_line.lstrip(" "))
                if next_indent <= indent + 1:
                    break
                sub_lines.append(next_line)
                j += 1
            result.append(_parse_nested(sub_lines))
            i = j
        elif ":" in content and not content.startswith('"'):
            # 内联键值对: "- key: value"
            sub = {}
            sub_lines = [content]
            # 检查后续行是否有更多同缩进的内容
            j = i + 1
            while j < len(lines):
                next_line = lines[j]
                next_stripped = next_line.strip()
                if not next_stripped or next_stripped.startswith("#"):
                    j += 1
                    continue
                next_indent = len(next_line) - len(next_line.lstrip(" "))
                if next_indent <= indent + 1:
                    break
                # 检查不是新的列表项
                if next_stripped.startswith("- "):
                    break
                sub_lines.append(next_line)
                j += 1
            result.append(_parse_nested(sub_lines))
            i = j
        else:
            # 简单列表项
            result.append(_parse_value(content))
            i += 1

    return result


def _parse_nested(lines: list[str]) -> dict:
    """解析嵌套对象"""
    result = {}
    # 将 lines 按缩进分组
    normalized = []
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(line) - len(line.lstrip(" "))
        normalized.append((indent, stripped))

    if not normalized:
        return result

    base_indent = min(ind for ind, _ in normalized)

    i = 0
    while i < len(normalized):
        indent, stripped = normalized[i]
        if indent != base_indent:
            i += 1
            continue

        kv = re.match(r"^([\w_-]+)\s*:\s*(.*)", stripped)
        if not kv:
            i += 1
            continue

        key = kv.group(1)
        val_str = kv.group(2).strip()

        if val_str == "":
            # 嵌套值，收集后续行
            sub_items = []
            j = i + 1
            while j < len(normalized):
                if normalized[j][0] > base_indent:
                    sub_items.append(normalized[j])
                    j += 1
                else:
                    break

            sub_lines = [" " * (ind - base_indent) + s for ind, s in sub_items]
            if sub_lines and sub_lines[0].strip().startswith("- "):
                result[key] = _parse_list(sub_lines)
            else:
                result[key] = _parse_nested(sub_lines)
            i = j
        else:
            result[key] = _parse_value(val_str)
            i += 1

    return result


# ── JSON 生成 ─────────────────────────────────────────────

def generate_vendors() -> list[dict]:
    """从 aikb/vendors/*.md 生成 vendors.json"""
    vendors = []
    vdir = AIKB_DIR / "vendors"
    if not vdir.exists():
        return vendors

    for fpath in sorted(vdir.glob("*.md")):
        fm = parse_frontmatter(fpath.read_text(encoding="utf-8"))
        if not fm.get("id"):
            continue

        urls = {}
        for k in list(fm.keys()):
            if k.startswith("url_"):
                urls[k[4:]] = fm.pop(k)

        affiliate = {}
        if fm.get("affiliate_url"):
            affiliate = {
                "url": fm.pop("affiliate_url", ""),
                "type": fm.pop("affiliate_type", "none"),
                "benefit": fm.pop("affiliate_benefit", ""),
            }

        vendor = {
            "id": fm.pop("id"),
            "name": fm.pop("name", ""),
            "logo": fm.pop("logo", ""),
            "color": fm.pop("color", ""),
            "category": fm.pop("category", ""),
            "country": fm.pop("country", ""),
            "urls": urls,
            "extractStrategy": fm.pop("extractStrategy", ""),
            "extractStatus": fm.pop("extractStatus", ""),
            "massServices": fm.pop("massServices", []),
            "affiliate": affiliate,
            "lastVerified": fm.pop("lastVerified", None),
            "notes": fm.pop("notes", ""),
        }
        vendors.append(vendor)

    return vendors


def generate_services() -> list[dict]:
    """从 aikb/vendors/*.md 的 services 字段生成 services.json"""
    services = []
    vdir = AIKB_DIR / "vendors"
    if not vdir.exists():
        return services

    for fpath in sorted(vdir.glob("*.md")):
        fm = parse_frontmatter(fpath.read_text(encoding="utf-8"))
        vendor_id = fm.get("id", "")
        if not vendor_id:
            continue

        svc_list = fm.get("services", [])
        if isinstance(svc_list, dict):
            svc_list = [svc_list]

        for svc in svc_list:
            if not isinstance(svc, dict):
                continue
            svc_type = svc.get("type", "")
            plans = svc.get("plans", [])
            if isinstance(plans, dict):
                plans = [plans]

            service = {
                "id": f"{vendor_id}-{svc_type}",
                "vendorId": vendor_id,
                "type": svc_type,
                "name": _service_display_name(svc_type),
                "status": svc.get("status", "active"),
                "plans": plans,
                "billingCore": svc.get("billingCore", ""),
                "migration": svc.get("migration", ""),
                "updatedAt": datetime.now().strftime("%Y-%m-%d"),
                "source": f"extracted-{vendor_id}",
            }
            services.append(service)

    return services


def _service_display_name(svc_type: str) -> str:
    return {
        "coding-plan": "Coding Plan",
        "token-plan": "Token Plan",
        "api-paygo": "API 按量",
        "agent-plan": "Agent Plan",
    }.get(svc_type, svc_type)


def generate_tools() -> list[dict]:
    """从 aikb/tools/*.md 生成 tools.json"""
    tools = []
    tdir = AIKB_DIR / "tools"
    if not tdir.exists():
        return tools

    for fpath in sorted(tdir.glob("*.md")):
        fm = parse_frontmatter(fpath.read_text(encoding="utf-8"))
        if not fm.get("id"):
            continue

        urls = {}
        for k in list(fm.keys()):
            if k.startswith("url_"):
                urls[k[4:]] = fm.pop(k)

        pricing = {
            "model": fm.pop("pricingModel", ""),
            "detail": fm.pop("pricingDetail", ""),
        }

        tool = {
            "id": fm.pop("id"),
            "name": fm.pop("name", ""),
            "vendorId": fm.pop("vendorId", ""),
            "vendorName": fm.pop("vendorName", ""),
            "type": fm.pop("type", ""),
            "category": fm.pop("category", ""),
            "description": fm.pop("description", ""),
            "pricing": pricing,
            "modelIntegration": fm.pop("modelIntegration", []),
            "codingPlanRelation": fm.pop("codingPlanRelation", ""),
            "features": fm.pop("features", []),
            "platforms": fm.pop("platforms", []),
            "rating": fm.pop("rating", 3),
            "bestFor": fm.pop("bestFor", []),
            "strengths": fm.pop("strengths", []),
            "weaknesses": fm.pop("weaknesses", []),
            "urls": urls,
            "tags": fm.pop("tags", []),
            "featured": fm.pop("featured", False),
            "trending": fm.pop("trending", False),
            "addedAt": fm.pop("addedAt", ""),
        }
        tools.append(tool)

    return tools


def generate_models() -> list[dict]:
    """从 aikb/vendors/*.md 的 models 字段生成 models.json"""
    models = []
    vdir = AIKB_DIR / "vendors"
    if not vdir.exists():
        return models

    for fpath in sorted(vdir.glob("*.md")):
        fm = parse_frontmatter(fpath.read_text(encoding="utf-8"))
        vendor_id = fm.get("id", "")
        model_names = fm.get("models", [])
        if isinstance(model_names, str):
            model_names = [model_names]

        for name in model_names:
            model_id = name.lower().replace(" ", "-").replace(".", "-")
            model_id = re.sub(r"[()]", "", model_id)
            models.append({
                "id": model_id,
                "vendorId": vendor_id,
                "name": name,
                "type": _infer_model_type(name),
                "status": "active",
            })

    return models


def _infer_model_type(name: str) -> str:
    name_lower = name.lower()
    if any(kw in name_lower for kw in ["asr", "voice", "speech", "tts"]):
        return "audio"
    if any(kw in name_lower for kw in ["vision", "v-", "-v", "vl", "video"]):
        return "vision"
    if any(kw in name_lower for kw in ["code", "coder"]):
        return "code"
    return "text"


def generate_changes() -> list[dict]:
    """changes.json 透传——从旧 KB 拷贝，或保留现有"""
    old_path = OLD_KB_DIR / "changes.json"
    if old_path.exists():
        return json.loads(old_path.read_text(encoding="utf-8"))
    existing = DATABASE_DIR / "changes.json"
    if existing.exists():
        return json.loads(existing.read_text(encoding="utf-8"))
    return []


# ── 主入口 ────────────────────────────────────────────────

def generate_all() -> dict[str, int]:
    """生成所有 database/ JSON 文件，返回各文件条目数"""
    DATABASE_DIR.mkdir(parents=True, exist_ok=True)

    vendors = generate_vendors()
    _write("vendors.json", vendors)

    services = generate_services()
    _write("services.json", services)

    tools = generate_tools()
    _write("tools.json", tools)

    models = generate_models()
    _write("models.json", models)

    changes = generate_changes()
    _write("changes.json", changes)

    return {
        "vendors": len(vendors),
        "services": len(services),
        "tools": len(tools),
        "models": len(models),
        "changes": len(changes),
    }


def _write(filename: str, data):
    path = DATABASE_DIR / filename
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def main():
    print("📦 md_to_json — MD 画像 → database/ JSON")
    stats = generate_all()
    print(f"  ✅ vendors:  {stats['vendors']} 家")
    print(f"  ✅ services: {stats['services']} 个")
    print(f"  ✅ tools:    {stats['tools']} 款")
    print(f"  ✅ models:   {stats['models']} 个")
    print(f"  ✅ changes:  {stats['changes']} 条")
    print(f"  → {DATABASE_DIR}")


if __name__ == "__main__":
    main()