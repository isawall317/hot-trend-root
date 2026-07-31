"""
KB 变更检测 — 对比上次快照与当前 KB，产出结构化变更报告 + 风险分级

机制:
  pipeline 每次跑会先把"上一次的 KB"快照到 data/knowledge-base/.last-run/，
  然后 kb_migrate 把最新数据写入 data/knowledge-base/。
  kb_diff 对比二者:
    - .last-run/  = 上一次的 KB（"old"）
    - KB_DIR/     = 本次 kb_migrate 刚写完的 KB（"new"）
  对比完成后，把当前 KB 再快照一份到 .last-run/，供下一次对比。

首次运行（.last-run/ 不存在）→ 用当前 KB 初始化快照，报告 0 条变更。

输出: data/pending/{date}/kb-changes.json

风险分级:
  🔴 high   — 价格变动>10%、服务下架、新服务上线、category 变更
  🟡 medium — URL 变更、新模型、新工具、massServices 增减
  🟢 low    — 备注更新、logo/color、lastVerified
"""

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
KB_DIR = PROJECT_ROOT / "aikb" / "database"
LAST_RUN_DIR = KB_DIR / ".last-run"
PENDING_DIR = PROJECT_ROOT / "data" / "pending"

# 参与 diff 的 KB 实体文件
ENTITY_FILES = ["vendors.json", "services.json", "tools.json", "models.json"]


def diff_all(date_str: str | None = None) -> dict:
    """对比 .last-run（上一次 KB）vs 当前 KB，返回结构化变更报告。

    首次运行（.last-run 不存在）→ 初始化快照，报告 0 条变更。
    正常运行 → 对比后，把当前 KB 快照到 .last-run/，供下次用。
    """
    if date_str is None:
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    is_first_run = not LAST_RUN_DIR.exists()

    if is_first_run:
        # 首次：用当前 KB 初始化 baseline，不报变更（没有"上一次"可对比）
        _snapshot_current_kb()
        print(f"📦 首次运行：已初始化 KB 快照到 {LAST_RUN_DIR}（本次不报变更）")
        changes = _empty_report(date_str)
    else:
        changes = {
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "date": date_str,
            "vendors": _diff_vendors(),
            "services": _diff_services(),
            "tools": _diff_tools(),
            "models": _diff_models(),
            "summary": {},
        }
        all_changes = (
            changes["vendors"] + changes["services"]
            + changes["tools"] + changes["models"]
        )
        changes["summary"] = {
            "total": len(all_changes),
            "high": sum(1 for c in all_changes if c.get("risk") == "high"),
            "medium": sum(1 for c in all_changes if c.get("risk") == "medium"),
            "low": sum(1 for c in all_changes if c.get("risk") == "low"),
        }
        # 对比完成后，更新快照供下一次用
        _snapshot_current_kb()

    # 保存报告
    out_dir = PENDING_DIR / date_str
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "kb-changes.json"
    out_path.write_text(json.dumps(changes, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ KB 变更报告: {out_path}")
    s = changes["summary"]
    print(f"   总计 {s['total']} 条 (🔴{s['high']} 🟡{s['medium']} 🟢{s['low']})")

    return changes


def _empty_report(date_str: str) -> dict:
    return {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "date": date_str,
        "vendors": [], "services": [], "tools": [], "models": [],
        "summary": {"total": 0, "high": 0, "medium": 0, "low": 0},
        "note": "首次运行，已初始化 baseline 快照，无变更可对比",
    }


def _snapshot_current_kb() -> None:
    """把当前 KB 的实体文件快照到 .last-run/ 目录"""
    if LAST_RUN_DIR.exists():
        shutil.rmtree(LAST_RUN_DIR)
    LAST_RUN_DIR.mkdir(parents=True)
    for fname in ENTITY_FILES:
        src = KB_DIR / fname
        if src.exists():
            shutil.copy2(src, LAST_RUN_DIR / fname)


def _load_json(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def _index_by_id(data: list[dict]) -> dict[str, dict]:
    return {item["id"]: item for item in data}


def _diff_vendors() -> list[dict]:
    """对比 vendors.json"""
    old = _index_by_id(_load_json(LAST_RUN_DIR / "vendors.json"))
    new = _index_by_id(_load_json(KB_DIR / "vendors.json"))
    return _diff_entities("vendor", old, new, _classify_vendor_change)


def _diff_services() -> list[dict]:
    """对比 services.json"""
    old = _index_by_id(_load_json(LAST_RUN_DIR / "services.json"))
    new = _index_by_id(_load_json(KB_DIR / "services.json"))
    return _diff_entities("service", old, new, _classify_service_change)


def _diff_tools() -> list[dict]:
    """对比 tools.json"""
    old = _index_by_id(_load_json(LAST_RUN_DIR / "tools.json"))
    new = _index_by_id(_load_json(KB_DIR / "tools.json"))
    return _diff_entities("tool", old, new, _classify_tool_change)


def _diff_models() -> list[dict]:
    """对比 models.json"""
    old = _index_by_id(_load_json(LAST_RUN_DIR / "models.json"))
    new = _index_by_id(_load_json(KB_DIR / "models.json"))
    model_changes = _diff_entities("model", old, new, _classify_model_change)
    # 模型变更默认低风险
    for c in model_changes:
        if "risk" not in c:
            c["risk"] = "low"
    return model_changes


def _diff_entities(
    entity_type: str,
    old: dict[str, dict],
    new: dict[str, dict],
    classifier,
) -> list[dict]:
    """通用实体对比"""
    changes = []
    all_ids = set(old.keys()) | set(new.keys())

    for eid in sorted(all_ids):
        if eid not in old:
            # 新增
            changes.append({
                "entity": entity_type,
                "id": eid,
                "change": "added",
                "risk": "medium",
                "detail": f"新增 {entity_type}: {new[eid].get('name', eid)}",
                "new_data": new[eid],
            })
        elif eid not in new:
            # 删除
            changes.append({
                "entity": entity_type,
                "id": eid,
                "change": "removed",
                "risk": "high",
                "detail": f"{entity_type} 已移除: {old[eid].get('name', eid)}",
                "old_data": old[eid],
            })
        else:
            # 逐字段对比
            field_changes = _compare_fields(old[eid], new[eid])
            if field_changes:
                risk = classifier(old[eid], new[eid], field_changes)
                changes.append({
                    "entity": entity_type,
                    "id": eid,
                    "name": new[eid].get("name", eid),
                    "change": "modified",
                    "risk": risk,
                    "fields": field_changes,
                    "detail": _summarize_changes(entity_type, eid, field_changes),
                })

    return changes


def _compare_fields(old_obj: dict, new_obj: dict) -> dict[str, dict]:
    """逐字段对比，返回变更字段字典"""
    diffs = {}
    all_keys = set(old_obj.keys()) | set(new_obj.keys())

    for key in sorted(all_keys):
        old_val = old_obj.get(key)
        new_val = new_obj.get(key)

        if isinstance(old_val, list) and isinstance(new_val, list):
            # 列表对比：dict 元素用 json.dumps 标准化（避免 Python repr 串污染），
            # 其余元素（str/int）用 str。按稳定序列化后做 set 差集。
            def _serialize(x):
                return json.dumps(x, ensure_ascii=False, sort_keys=True) if isinstance(x, (dict, list)) else str(x)
            old_set = set(_serialize(x) for x in old_val)
            new_set = set(_serialize(x) for x in new_val)
            added = [x for x in new_val if _serialize(x) not in old_set]
            removed = [x for x in old_val if _serialize(x) not in new_set]
            if added or removed:
                diffs[key] = {"old": old_val, "new": new_val, "added": added, "removed": removed}
        elif isinstance(old_val, dict) and isinstance(new_val, dict):
            # 嵌套字典对比
            nested = _compare_fields(old_val, new_val)
            if nested:
                diffs[key] = {"old": old_val, "new": new_val, "nested": nested}
        elif old_val != new_val:
            diffs[key] = {"old": old_val, "new": new_val}

    return diffs


def _classify_vendor_change(old: dict, new: dict, diffs: dict) -> str:
    """厂商变更风险分级"""
    high_fields = {"category", "extractStrategy", "extractStatus"}
    medium_fields = {"urls", "massServices", "name"}

    for key in diffs:
        if key in high_fields:
            return "high"
    for key in diffs:
        if key in medium_fields:
            return "medium"
    return "low"


def _classify_service_change(old: dict, new: dict, diffs: dict) -> str:
    """服务变更风险分级"""
    if "status" in diffs:
        return "high"
    if "plans" in diffs:
        # 检查 plan 内的价格变动
        return _check_price_change_risk(diffs.get("plans", {}))
    if "type" in diffs or "name" in diffs:
        return "high"
    return "medium"


def _check_price_change_risk(plans_diff: dict) -> str:
    """检查价格变动幅度"""
    try:
        if "old" not in plans_diff or "new" not in plans_diff:
            return "medium"
        # 尝试匹配同 tier 的 plan 对比价格
        old_plans = {p.get("tier", ""): p for p in plans_diff["old"]}
        new_plans = {p.get("tier", ""): p for p in plans_diff["new"]}
        for tier in set(old_plans.keys()) & set(new_plans.keys()):
            old_price = old_plans[tier].get("monthlyPrice", 0) or 0
            new_price = new_plans[tier].get("monthlyPrice", 0) or 0
            if old_price > 0 and new_price > 0:
                change_pct = abs(new_price - old_price) / old_price
                if change_pct > 0.10:
                    return "high"
    except Exception:
        pass
    return "medium"


def _classify_tool_change(old: dict, new: dict, diffs: dict) -> str:
    """工具变更风险分级"""
    high_fields = {"pricing"}
    medium_fields = {"name", "features", "urls", "platforms", "modelIntegration"}

    for key in diffs:
        if key in high_fields:
            return "high"
    for key in diffs:
        if key in medium_fields:
            return "medium"
    return "low"


def _classify_model_change(old: dict, new: dict, diffs: dict) -> str:
    """模型变更风险分级"""
    # 新增/删除模型通常是 medium，其他 low
    return "low"


def _summarize_changes(entity_type: str, eid: str, diffs: dict) -> str:
    """生成可读的变更摘要"""
    parts = []
    for key in sorted(diffs.keys()):
        if key in ("updatedAt", "lastVerified", "source"):
            continue
        change = diffs[key]
        if "added" in change and "removed" in change:
            parts.append(f"{key}: +{len(change['added'])}/-{len(change['removed'])}")
        else:
            parts.append(f"{key} 变更")
    return f"{entity_type} {eid}: {', '.join(parts)}" if parts else f"{entity_type} {eid}: 字段变更"


def main():
    print("📊 KB 变更检测")
    diff_all()


if __name__ == "__main__":
    main()