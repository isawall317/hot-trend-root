"""
价格监控器 — 多平台 AI Coding Plan 定价采集 + 变动检测 + 报告生成

数据获取策略（按难度分级）:
  Level 1 (直接爬取): 静态定价页, 直接 HTTP GET → 解析
  Level 2 (新闻监控): 通过 DailyHotApi 监测价格变动新闻
  Level 3 (手动确认): 需登录/JS 渲染的平台, 标记为待确认

输出:
  data/price-reports/{date}.md — 变动报告 (Claude Code 消费)
  data/price-reports/{date}.json — 结构化变动数据
"""

import asyncio
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

# 项目路径
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
PLANS_PATH = PROJECT_ROOT / "project" / "codingplan-saver" / "plans.json"
REPORTS_DIR = DATA_DIR / "price-reports"

# API 地址
DAILYHOT_BASE = os.getenv("DAILYHOT_BASE", "http://localhost:6688")


# ── 平台定价页配置 ──────────────────────────────────────────────
# 每个平台定义: 名称, 定价页URL, 采集策略 (direct/news/manual)
PLATFORMS = [
    # Level 1: 可直接爬取（定价页公开，无需登录）
    {"id": "zhipu", "vendor": "智谱AI", "url": "https://open.bigmodel.cn/pricing",
     "strategy": "direct", "notes": "定价页公开，可能需要 JS 渲染"},
    {"id": "bytedance", "vendor": "字节·方舟", "url": "https://www.volcengine.com/ark",
     "strategy": "direct", "notes": "Coding Plan 在方舟平台页；详细文档: https://www.volcengine.com/docs/82379/1099320"},
    {"id": "deepseek", "vendor": "DeepSeek 官方", "url": "https://api-docs.deepseek.com/quick_start/pricing",
     "strategy": "direct", "notes": "API 文档页公开，含按量计费价格"},
    {"id": "kimi", "vendor": "Kimi",
     "url": "https://www.kimi.com/membership/pricing",
     "url_api": "https://platform.kimi.com/docs/pricing/chat",
     "strategy": "direct", "notes": "C端定价页 + API 文档；JS 渲染，需浏览器查看"},
    {"id": "minimax", "vendor": "MiniMax",
     "url": "https://platform.minimaxi.com/docs/guides/pricing-token-plan",
     "url_overview": "https://platform.minimaxi.com/docs/pricing/overview",
     "strategy": "direct", "notes": "Token Plan 定价公开，无需登录"},
    {"id": "bailian", "vendor": "阿里·百炼",
     "url": "https://bailian.console.aliyun.com/cn-beijing?tab=doc#/doc/?type=model&url=3028856",
     "strategy": "direct", "notes": "公开文档，无需登录"},
    {"id": "tencent", "vendor": "腾讯云",
     "url": "https://cloud.tencent.com/product/tokenhub?Is=home",
     "strategy": "direct", "notes": "TokenHub: 按量计费 + Token Plan 订阅，公开页面"},
    {"id": "claude", "vendor": "Claude", "url": "https://claude.com/pricing",
     "strategy": "direct", "notes": "Anthropic 定价页公开"},
    {"id": "codex", "vendor": "Codex (ChatGPT)", "url": "https://openai.com/chatgpt/pricing/",
     "strategy": "direct", "notes": "OpenAI 定价页公开"},
    {"id": "github", "vendor": "GitHub", "url": "https://github.com/features/copilot/plans",
     "strategy": "direct", "notes": "GitHub Copilot 定价页公开"},

    # Level 2: 新闻监控（需登录，通过 DailyHotApi 检测价格变动信号）
    {"id": "baidu", "vendor": "百度·千帆",
     "url": "https://qianfan.baidubce.com/",
     "strategy": "news", "notes": "需百度云登录控制台"},
    {"id": "xunfei", "vendor": "讯飞·星火",
     "url": "https://xinghuo.xfyun.cn/",
     "strategy": "news", "notes": "需登录查看 Coding Plan"},
    {"id": "huawei", "vendor": "华为云",
     "url": "https://www.huaweicloud.com/",
     "strategy": "news", "notes": "搜索 CodeArts，需登录"},
    {"id": "jd", "vendor": "京东云",
     "url": "https://www.jdcloud.com/",
     "strategy": "news", "notes": "搜索 AI Coding，需登录"},
    {"id": "mimo", "vendor": "小米·MiMo",
     "url": "https://mimo.xiaomi.com/",
     "strategy": "news", "notes": "需小米账号登录"},
    {"id": "youyun", "vendor": "优云智算",
     "url": "https://www.youyun.com/",
     "strategy": "news", "notes": "需登录查看套餐"},
    {"id": "opencode", "vendor": "OpenCode",
     "url": "https://opencode.ai/",
     "strategy": "news", "notes": "海外平台，多模型聚合"},
    {"id": "gongji", "vendor": "共继算力",
     "url": "https://gongji.ai/",
     "strategy": "news", "notes": "需登录，DeepSeek 8折中转"},
    {"id": "ollama", "vendor": "Ollama",
     "url": "https://ollama.com/",
     "strategy": "news", "notes": "海外平台，需登录"},
    {"id": "zhipu-intl", "vendor": "智谱国际版",
     "url": "https://open.bigmodel.cn/",
     "strategy": "news", "notes": "与国内版定价不同"},
]


# ── 关键词监控 ──────────────────────────────────────────────────
# 从 DailyHotApi 中检测这些关键词，发现价格变动信号
PRICE_KEYWORDS = [
    "涨价", "降价", "调价", "价格", "定价", "计费",
    "新套餐", "新增模型", "下架", "售罄", "暂停",
    "Coding Plan", "Token Plan", "月费", "额度",
    "免费", "公测", "限时", "活动", "折扣",
    "倍率", "并发", "请求", "订阅",
]


async def _fetch_dailyhot_news(client: httpx.AsyncClient) -> list[dict]:
    """从 DailyHotApi 获取科技类新闻，检测价格相关信号"""
    tech_sources = ["36kr", "ithome", "sspai", "juejin", "v2ex"]
    signals = []

    for source in tech_sources:
        try:
            resp = await client.get(f"{DAILYHOT_BASE}/{source}", timeout=15)
            if resp.status_code != 200:
                continue
            data = resp.json()
            items = data.get("data", [])
            for item in items:
                title = str(item.get("title", ""))
                # 匹配关键词
                matched = [kw for kw in PRICE_KEYWORDS if kw in title]
                if matched:
                    # 匹配平台
                    platform_matches = []
                    for p in PLATFORMS:
                        if p["vendor"] in title or p["id"] in title.lower():
                            platform_matches.append(p["vendor"])
                    signals.append({
                        "title": title,
                        "url": item.get("url", ""),
                        "source": f"dailyhot:{source}",
                        "keywords": matched,
                        "platforms": platform_matches or ["通用"],
                        "detected_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    })
        except Exception as e:
            print(f"  ⚠️ DailyHotApi/{source} 信号检测失败: {e}")

    return signals


async def _scrape_direct(client: httpx.AsyncClient, platform: dict) -> dict | None:
    """直接爬取定价页（Level 1 平台）"""
    try:
        resp = await client.get(platform["url"], timeout=20, follow_redirects=True)
        if resp.status_code != 200:
            return {"vendor": platform["vendor"], "status": "failed",
                    "error": f"HTTP {resp.status_code}", "strategy": "direct"}

        text = resp.text

        # 提取价格信息（正则匹配常见价格模式）
        prices_found = re.findall(r'(?:¥|￥|¥|CNY\s*)?(\d+[\d,]*)\s*(?:元|/月|/mo)', text)
        models_found = re.findall(r'(GLM-[\d.]+|DeepSeek-[\w.-]+|Kimi-[\w.-]+|'
                                  r'GPT-[\d.]+|Claude[\s\w.-]+|Gemini[\s\d.-]+|'
                                  r'Qwen-[\d.-]+|MiMo-[\w.-]+|Doubao-[\w.-]+)', text)

        return {
            "vendor": platform["vendor"],
            "status": "scraped",
            "strategy": "direct",
            "prices_found": list(set(prices_found))[:10],
            "models_found": list(set(models_found))[:10],
            "url": platform["url"],
        }
    except Exception as e:
        return {"vendor": platform["vendor"], "status": "failed",
                "error": str(e)[:100], "strategy": "direct"}


async def run_price_monitor() -> str | None:
    """运行价格监控，生成变动报告"""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    date_str = timestamp[:10]
    print(f"🔍 价格监控开始 — {timestamp}")

    async with httpx.AsyncClient(timeout=30) as client:
        # 1. 新闻信号检测
        print("📡 检测新闻信号...")
        signals = await _fetch_dailyhot_news(client)
        print(f"  发现 {len(signals)} 条价格相关信号")

        # 2. 直接爬取 Level 1 平台
        print("🌐 直接爬取公开定价页...")
        direct_platforms = [p for p in PLATFORMS if p["strategy"] == "direct"]
        scrape_tasks = [_scrape_direct(client, p) for p in direct_platforms]
        scrape_results = await asyncio.gather(*scrape_tasks)
        scraped = [r for r in scrape_results if r and r["status"] == "scraped"]
        failed = [r for r in scrape_results if r and r["status"] == "failed"]
        print(f"  成功: {len(scraped)} | 失败: {len(failed)}")

    # 3. 加载现有 plans.json 做对比
    existing_plans = _load_existing_plans()

    # 4. 生成报告
    report = _generate_report(timestamp, signals, scrape_results, existing_plans)

    # 5. 保存报告
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORTS_DIR / f"{date_str}.md"
    json_path = REPORTS_DIR / f"{date_str}.json"

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)

    report_data = {
        "timestamp": timestamp,
        "signals_count": len(signals),
        "signals": signals,
        "scrape_results": scrape_results,
        "existing_plans_count": len(existing_plans),
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2)

    print(f"✅ 报告已生成: {report_path}")
    print(f"📊 结构化数据: {json_path}")

    return report_path


def _load_existing_plans() -> list[dict]:
    """加载现有 plans.json"""
    if not PLANS_PATH.exists():
        return []
    with open(PLANS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _generate_report(
    timestamp: str,
    signals: list[dict],
    scrape_results: list[dict | None],
    existing_plans: list[dict],
) -> str:
    """生成 Markdown 变动报告"""
    date_str = timestamp[:10]

    # 统计各平台现有套餐数
    vendor_counts = {}
    for p in existing_plans:
        v = p.get("vendor", "未知")
        vendor_counts[v] = vendor_counts.get(v, 0) + 1

    # 按平台分组信号
    platform_signals: dict[str, list] = {}
    for s in signals:
        for plat in s["platforms"]:
            if plat not in platform_signals:
                platform_signals[plat] = []
            platform_signals[plat].append(s)

    # 构建报告
    lines = [
        f"# 🔍 价格监控报告 — {date_str}",
        f"",
        f"> 生成时间: {timestamp}",
        f"> 监控平台: {len(PLATFORMS)} 个",
        f"> 新闻信号: {len(signals)} 条",
        f"",
        f"---",
        f"",
        f"## 📊 现有数据概况",
        f"",
        f"| 平台 | 套餐数 | 需确认项 |",
        f"|------|--------|----------|",
    ]

    for p in PLATFORMS:
        v = p["vendor"]
        count = vendor_counts.get(v, 0)
        needs = "⚠️ 待验证" if p["strategy"] in ("news", "manual") else "🟢 可自动采集"
        lines.append(f"| {v} | {count} | {needs} |")

    lines.extend([
        f"",
        f"---",
        f"",
        f"## 🚨 价格变动信号",
        f"",
    ])

    if signals:
        for s in signals[:20]:  # Top 20
            kws = ", ".join(s["keywords"])
            plats = ", ".join(s["platforms"])
            lines.append(f"- **[{plats}]** {s['title']} `[{kws}]` [{s['source']}]({s['url']})")
    else:
        lines.append("_今日未检测到价格变动信号_")

    lines.extend([
        f"",
        f"---",
        f"",
        f"## 🌐 直接采集结果",
        f"",
        f"| 平台 | 状态 | 发现价格 | 发现模型 |",
        f"|------|------|----------|----------|",
    ])

    for r in scrape_results:
        if r is None:
            continue
        if r["status"] == "scraped":
            prices = ", ".join(r.get("prices_found", [])[:5])
            models = ", ".join(r.get("models_found", [])[:5])
            lines.append(f"| {r['vendor']} | ✅ | {prices} | {models} |")
        else:
            lines.append(f"| {r['vendor']} | ❌ {r.get('error', '')} | — | — |")

    lines.extend([
        f"",
        f"---",
        f"",
        f"## ⚠️ 待人工确认",
        f"",
        f"以下平台需手动登录查看定价页：",
        f"",
    ])

    for p in PLATFORMS:
        if p["strategy"] in ("news", "manual"):
            lines.append(f"- [ ] **{p['vendor']}** — {p['url']} ({p['notes']})")

    lines.extend([
        f"",
        f"---",
        f"",
        f"## 📋 建议操作",
        f"",
        f"1. 核查上述信号，确认是否有价格变动",
        f"2. 对 `待人工确认` 平台逐一检查定价页",
        f"3. 更新 `plans.json` 和 `price-changes.json`",
        f"4. 更新 `config.json` 中的 `updateDate`",
        f"",
    ])

    return "\n".join(lines)


def main():
    """CLI 入口"""
    asyncio.run(run_price_monitor())


if __name__ == "__main__":
    main()