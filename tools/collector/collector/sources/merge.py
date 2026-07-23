"""
提取结果合并器 — 将 sources/runner 的提取结果合并到 plans.json

用法: python -m collector.sources.merge
读取 data/signals/extract-{date}.json → 更新 plans.json 的 monthlyPrice/monthlyRequests/models
"""

import json
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
PLANS_PATH = PROJECT_ROOT / "project" / "codingplan-saver" / "data" / "plans.json"
SIGNALS_DIR = PROJECT_ROOT / "data" / "signals"

# 提取结果 → plans.json 的映射规则
# key: vendorId
# 每个 vendor 的 merge 函数接收 (plan_entry, extracted_plan) 并更新 plan_entry
MERGE_RULES = {}


def rule(vendor_id: str):
    """装饰器：注册合并规则"""
    def deco(fn):
        MERGE_RULES[vendor_id] = fn
        return fn
    return deco


@rule("tencent")
def merge_tencent(plan_entry: dict, extracted: dict) -> bool:
    """腾讯云: 提取结果有 plan/monthlyPrice/monthlyRequests"""
    changed = False
    for ext in extracted.get("plans", []):
        if ext.get("plan", "").lower() == plan_entry.get("plan", "").lower():
            for field in ["monthlyPrice", "monthlyRequests"]:
                if field in ext and ext[field] != plan_entry.get(field):
                    plan_entry[field] = ext[field]
                    changed = True
    return changed


@rule("minimax")
def merge_minimax(plan_entry: dict, extracted: dict) -> bool:
    """MiniMax: 按 plan 名匹配 monthlyPrice。

    注意: 曾用 tier+price 容差匹配，但 plans.json 存在多个同 tier plan（新Max/新Ultra
    都是 tier=max），extract 的价格会同时命中多个 plan 造成数据污染。改为只用 plan 名
    匹配——minimax 定价页命名与 plans.json 不一致时宁可不更新，也不误改。
    名字归一化: 去掉"新"前缀和空格，大小写不敏感。
    """
    changed = False
    norm_entry = _norm_mm_name(plan_entry.get("plan", ""))
    for ext in extracted.get("plans", []):
        norm_ext = _norm_mm_name(ext.get("plan", ""))
        if not norm_ext or norm_ext != norm_entry:
            continue
        price = ext.get("monthlyPrice")
        if price is not None and plan_entry.get("monthlyPrice") != price:
            plan_entry["monthlyPrice"] = price
            changed = True
    return changed


def _norm_mm_name(name: str) -> str:
    """归一化 minimax plan 名: 去'新'前缀、去空格、小写"""
    return (name or "").replace("新", "").replace(" ", "").lower()


@rule("claude")
def merge_claude(plan_entry: dict, extracted: dict) -> bool:
    """Claude: 提取结果有 monthlyPrice，按 plan 名匹配"""
    changed = False
    for ext in extracted.get("plans", []):
        if ext.get("plan", "").lower() == plan_entry.get("plan", "").lower():
            for field in ["monthlyPrice"]:
                if field in ext and ext[field] != plan_entry.get(field):
                    plan_entry[field] = ext[field]
                    changed = True
    return changed


@rule("github")
def merge_github(plan_entry: dict, extracted: dict) -> bool:
    """GitHub: 提取结果有 monthlyPrice，按 plan 名匹配"""
    changed = False
    for ext in extracted.get("plans", []):
        if ext.get("plan", "").lower() == plan_entry.get("plan", "").lower():
            for field in ["monthlyPrice"]:
                if field in ext and ext[field] != plan_entry.get(field):
                    plan_entry[field] = ext[field]
                    changed = True
    return changed


@rule("zhipu")
def merge_zhipu(plan_entry: dict, extracted: dict) -> bool:
    """智谱AI: 提取结果有 models 列表，更新 models 字段"""
    changed = False
    for ext in extracted.get("plans", []):
        models = ext.get("models", [])
        if models:
            model_names = [m.get("name", "") for m in models if m.get("name")]
            existing = set(plan_entry.get("models", []))
            new_models = [m for m in model_names if m not in existing]
            if new_models:
                plan_entry["models"] = sorted(existing | set(model_names))
                changed = True
    return changed


@rule("deepseek")
def merge_deepseek(plan_entry: dict, extracted: dict) -> bool:
    """DeepSeek: 提取结果有 models 列表，更新 models 字段"""
    changed = False
    for ext in extracted.get("plans", []):
        models = ext.get("models", [])
        if models:
            existing = set(plan_entry.get("models", []))
            new_models = [m for m in models if m not in existing]
            if new_models:
                plan_entry["models"] = sorted(existing | set(models))
                changed = True
    return changed


@rule("kimi")
def merge_kimi(plan_entry: dict, extracted: dict) -> bool:
    """Kimi: 提取结果有 models 列表"""
    changed = False
    for ext in extracted.get("plans", []):
        models = [m.get("name", "") for m in ext.get("models", []) if m.get("name")]
        if models:
            existing = set(plan_entry.get("models", []))
            new_models = [m for m in models if m not in existing]
            if new_models:
                plan_entry["models"] = sorted(existing | set(models))
                changed = True
    return changed


def merge_from_extract(date_str: str = None) -> dict:
    """读取最新提取结果，合并到 plans.json"""
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")

    # 找到最新提取结果
    extract_files = sorted(SIGNALS_DIR.glob("extract-*.json"), reverse=True)
    if not extract_files:
        return {"status": "no_extract_file"}

    with open(extract_files[0], "r", encoding="utf-8") as f:
        extract_results = json.load(f)

    # 加载 plans
    with open(PLANS_PATH, "r", encoding="utf-8") as f:
        plans = json.load(f)

    today = datetime.now().strftime("%Y-%m-%d")
    stats = {"total": len(plans), "updated": 0, "vendors_updated": []}

    for result in extract_results:
        vendor_id = result.get("vendorId", "")
        if result.get("error") or not result.get("plans"):
            continue

        rule_fn = MERGE_RULES.get(vendor_id)
        if not rule_fn:
            continue

        vendor_updated = False
        for plan_entry in plans:
            if plan_entry.get("vendorId") != vendor_id:
                continue
            if rule_fn(plan_entry, result):
                plan_entry["updatedAt"] = today
                plan_entry["source"] = f"extracted-{vendor_id}"
                vendor_updated = True

        if vendor_updated:
            stats["updated"] += 1
            stats["vendors_updated"].append(vendor_id)

    # 保存
    with open(PLANS_PATH, "w", encoding="utf-8") as f:
        json.dump(plans, f, ensure_ascii=False, indent=2)

    return stats


def main():
    stats = merge_from_extract()
    print(f"📊 plans.json 合并: {stats['total']} plans")
    print(f"   更新: {stats['updated']} vendors ({', '.join(stats['vendors_updated'])})")


if __name__ == "__main__":
    main()