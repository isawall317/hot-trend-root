"""
Token 用量推算器 — 基于各平台公开参数推算实测月Token消耗

推算模型:
  Coding Plan 型 (按请求次数):
    典型场景: 每天 4h 编码, 20天/月, 每请求 ~50K tokens
    月Token ≈ 月请求数 × 0.05M (或 5h请求数 × 4段/天 × 20天 × 0.05M)

  Token Plan 型 (按 Token 计费):
    月Token = 套餐标称 Token 上限

  Coding Plan 型 (无请求数公开):
    月Token ≈ 月费 × 基准倍率 (基于同类套餐推算)

来源说明:
  - 优先使用官方公开的请求数推算
  - 次优先使用月费反推（基于同类套餐的 月Token/月费 比率中位数）
  - 所有推算值标注 "estimated"
"""

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
PLANS_PATH = PROJECT_ROOT / "project" / "codingplan-saver" / "plans.json"

# 基准参数
AVG_TOKENS_PER_REQUEST_M = 0.05  # 每次请求平均 50K tokens (0.05M)
CODING_HOURS_PER_DAY = 4         # 每天编码 4 小时
CODING_DAYS_PER_MONTH = 20       # 每月 20 个工作日
FIVE_HOUR_SLOTS_PER_DAY = 4      # 每天 4 个 5 小时时段 (保守估计)


def estimate_coding_plan(plan: dict) -> float | None:
    """推算 Coding Plan 的月Token消耗"""
    # 方法1: 有月请求数 → 直接乘
    monthly_requests = plan.get("monthlyRequests")
    if isinstance(monthly_requests, (int, float)) and monthly_requests > 0:
        return round(monthly_requests * AVG_TOKENS_PER_REQUEST_M)

    # 方法2: 有 5h 请求数 → 推算月请求数
    five_hour = plan.get("fiveHoursRequests")
    if isinstance(five_hour, (int, float)) and five_hour > 0:
        monthly_est = five_hour * FIVE_HOUR_SLOTS_PER_DAY * CODING_DAYS_PER_MONTH
        return round(monthly_est * AVG_TOKENS_PER_REQUEST_M)

    # 方法3: 有周请求数 → 推算月请求数
    weekly = plan.get("weeklyRequests")
    if isinstance(weekly, (int, float)) and weekly > 0:
        monthly_est = weekly * 4
        return round(monthly_est * AVG_TOKENS_PER_REQUEST_M)

    return None


def estimate_token_plan(plan: dict) -> float | None:
    """推算 Token Plan 的月Token消耗"""
    # 方法1: 有 tokenLimit 直接取
    token_limit = plan.get("tokenLimit")
    if isinstance(token_limit, str) and "M" in token_limit:
        try:
            return float(token_limit.replace("M Tokens", "").replace("M", "").strip())
        except ValueError:
            pass

    # 方法2: 从 measuredMonthlyToken 取（如果已有）
    measured = plan.get("measuredMonthlyToken")
    if isinstance(measured, (int, float)) and measured > 0:
        return float(measured)

    return None


def estimate_by_price(plan: dict, median_ratio: float) -> float | None:
    """基于月费反推（使用同类套餐的中位数比率）"""
    price = plan.get("monthlyPrice")
    if isinstance(price, (int, float)) and price > 0 and median_ratio > 0:
        return round(price * median_ratio)
    return None


def compute_median_ratio(plans: list[dict], plan_type: str) -> float:
    """计算同类套餐的月Token/月费 比率中位数"""
    ratios = []
    for p in plans:
        if p.get("type") != plan_type:
            continue
        price = p.get("monthlyPrice")
        token = p.get("measuredMonthlyToken")
        if isinstance(price, (int, float)) and isinstance(token, (int, float)) and price > 0 and token > 0:
            ratios.append(token / price)
    if not ratios:
        return 0
    ratios.sort()
    return ratios[len(ratios) // 2]


def compute_all(plans: list[dict]) -> list[dict]:
    """推算所有套餐的月Token，返回更新后的 plans"""
    # 先计算已有数据的比率中位数，用于反推
    cp_ratio = compute_median_ratio(plans, "Coding Plan")
    tp_ratio = compute_median_ratio(plans, "Token Plan")

    print(f"📊 基准比率: Coding Plan = {cp_ratio:.2f} M/元, Token Plan = {tp_ratio:.2f} M/元")

    updated = []
    for plan in plans:
        p = dict(plan)  # 浅拷贝
        plan_type = p.get("type", "")
        current = p.get("measuredMonthlyToken")

        # 已有实测数据 → 保留
        if isinstance(current, (int, float)) and current > 0:
            updated.append(p)
            continue

        # 推算
        estimated = None
        method = ""

        if "Coding" in plan_type:
            estimated = estimate_coding_plan(p)
            method = "Coding Plan 请求数推算"
        elif "Token" in plan_type:
            estimated = estimate_token_plan(p)
            method = "Token Plan 标称上限"

        # 反推兜底
        if estimated is None:
            ratio = cp_ratio if "Coding" in plan_type else tp_ratio
            estimated = estimate_by_price(p, ratio)
            method = f"月费反推 (比率={ratio:.2f})"

        if estimated is not None:
            p["measuredMonthlyToken"] = estimated
            p["_tokenEstimateMethod"] = method
        else:
            p["_tokenEstimateMethod"] = "无法推算"

        updated.append(p)

    return updated


def generate_report(original: list[dict], updated: list[dict]) -> str:
    """生成推算报告"""
    lines = ["# 📊 Token 用量推算报告", ""]
    lines.append("| 平台 | 套餐 | 类型 | 月费 | 推算Token | 方法 |")
    lines.append("|------|------|------|------|-----------|------|")

    changes = 0
    for orig, upd in zip(original, updated):
        old_val = orig.get("measuredMonthlyToken")
        new_val = upd.get("measuredMonthlyToken")
        method = upd.get("_tokenEstimateMethod", "")

        if old_val != new_val:
            changes += 1
            vendor = upd.get("vendor", "")
            plan = upd.get("plan", "")
            ptype = upd.get("type", "")
            price = upd.get("monthlyPrice", "")
            lines.append(f"| {vendor} | {plan} | {ptype} | ¥{price} | {new_val}M | {method} |")

    lines.insert(1, f"> 更新套餐数: {changes}/{len(original)}")
    lines.insert(2, "")

    return "\n".join(lines)


def main():
    """主流程: 加载 → 推算 → 保存 → 报告"""
    if not PLANS_PATH.exists():
        print("❌ plans.json 不存在")
        return

    with open(PLANS_PATH, "r", encoding="utf-8") as f:
        original = json.load(f)

    print(f"📂 加载 {len(original)} 个套餐")

    # 推算
    updated = compute_all(original)

    # 清理内部字段
    for p in updated:
        p.pop("_tokenEstimateMethod", None)

    # 保存
    with open(PLANS_PATH, "w", encoding="utf-8") as f:
        json.dump(updated, f, ensure_ascii=False, indent=2)

    print(f"✅ 已更新 {PLANS_PATH}")

    # 报告
    report = generate_report(original, updated)
    report_path = PROJECT_ROOT / "data" / "price-reports" / "token-estimate-report.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"📄 报告: {report_path}")


if __name__ == "__main__":
    main()