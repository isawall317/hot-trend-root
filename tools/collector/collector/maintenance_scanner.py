"""
维护扫描器 — 基于已知实体（厂商/工具）匹配热点，替代 article_discovery.py 的关键词方案

设计原则:
  1. 实体驱动 — 从 KB 加载已知厂商/工具名，按实体名 + 别名匹配标题
  2. 评分制 — 实体匹配 (3分) + 价格信号 (1分) + 来源质量 (0-1分) = 总分 ≥ 3 才入选
  3. 窄信号 — 关键词只作为加分项，不单独触发。避免"Agent"匹配房产新闻

输出: data/pending/{date}/articles.json (与 article_discovery.py 相同格式，兼容下游)
"""

import json
from datetime import datetime, timezone
from pathlib import Path

from . import storage

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
KB_DIR = PROJECT_ROOT / "aikb" / "database"
PENDING_DIR = PROJECT_ROOT / "data" / "pending"

# ── 价格/商业信号关键词（仅当实体已匹配时加分）──
PRICE_SIGNALS = [
    "涨价", "降价", "调价", "定价", "计费", "新套餐",
    "Coding Plan", "Token Plan", "额度", "免费", "订阅",
    "月费", "折扣", "活动", "限时",
]

# ── 模型/产品变更信号（仅当实体已匹配时加分）──
MODEL_SIGNALS = [
    "新模型", "新增模型", "模型升级", "模型发布", "发布",
    "上线", "推出", "开源", "公测", "内测",
]

# ── 状态变更信号（仅当实体已匹配时加分）──
STATUS_SIGNALS = [
    "下架", "暂停", "恢复", "售罄", "关闭",
]

# ── 高价值信号（命中即 +2 分，而非 +1）──
HIGH_VALUE_SIGNALS = [
    "涨价", "降价", "Coding Plan", "Token Plan", "新套餐",
    "下架", "暂停", "售罄",
]

# ── 高价值来源（+1 分）──
QUALITY_SOURCES = {
    "folo",        # 手动精选 RSS
    "36kr", "ithome", "sspai",  # 科技媒体
    "juejin", "v2ex",           # 开发者社区
}

# ── 实体别名映射（匹配用，不修改 KB）──
# 格式: "KB 中的实体名" → ["别名1", "别名2", ...]
ENTITY_ALIASES: dict[str, list[str]] = {
    # ── 厂商 ──
    "智谱AI": ["智谱", "GLM", "ChatGLM", "Zhipu", "CodeGeeX"],
    "字节·方舟": ["字节", "方舟", "字节方舟", "豆包", "火山引擎", "Ark", "Volcengine"],
    "DeepSeek 官方": ["DeepSeek", "Deepseek", "deepseek", "DeepSeek V4", "DeepSeek R1", "DeepSeek R2"],
    "Kimi": ["Kimi", "kimi", "Moonshot", "月之暗面", "Kimi K3", "Kimi-K3"],
    "MiniMax": ["MiniMax", "minimax", "海螺", "Hailuo"],
    "阿里·百炼": ["阿里", "百炼", "阿里巴巴", "通义", "Qwen", "DashScope"],
    "腾讯云": ["腾讯", "腾讯云", "Tencent", "Hunyuan", "混元"],
    "Claude": ["Claude", "claude", "Anthropic", "Opus", "Sonnet", "Haiku"],
    "Codex (ChatGPT)": ["Codex", "ChatGPT", "OpenAI", "GPT-5", "GPT-4", "GPT", "o3", "o4"],
    "GitHub": ["GitHub", "github", "Copilot", "GitHub Copilot", "GHCP"],
    "小米·MiMo": ["小米", "MiMo", "Xiaomi"],
    "OpenRouter": ["OpenRouter", "Open Router"],
    "硅基流动": ["硅基流动", "SiliconFlow", "硅基"],
    "百度·千帆": ["百度", "千帆", "Baidu", "ERNIE", "文心"],
    # ── 工具 ──
    "Claude Code": ["Claude Code", "claude code", "ClaudeCode"],
    "Codex CLI": ["Codex CLI", "Codex CLI", "codex-cli"],
    "Gemini CLI": ["Gemini CLI", "GeminiCLI", "Gemini CLI"],
    "OpenCode": ["OpenCode", "Open Code"],
    "DeepSeek Coder": ["DeepSeek Coder", "DeepSeekCoder"],
    "Qoder": ["Qoder"],
    "WorkBuddy": ["WorkBuddy", "Work Buddy"],
    "ZCode": ["ZCode", "Z Code"],
    "Hermes": ["Hermes"],
    "OpenClaw": ["OpenClaw", "Open Claw"],
    "Cursor": ["Cursor", "cursor"],
    "GitHub Copilot": ["GitHub Copilot", "Copilot", "GH Copilot"],
    "Claude Work": ["Claude Work", "ClaudeWork"],
    "Windsurf": ["Windsurf", "Codeium", "Windsurf Editor"],
    "Trae": ["Trae", "Trae IDE", "字节 Trae"],
    "Cline": ["Cline", "Cline Bot"],
    "Continue": ["Continue", "Continue.dev"],
    "Cody": ["Cody", "Sourcegraph Cody"],
    "Amazon Q Developer": ["Amazon Q", "Amazon Q Developer", "AWS Q"],
    "Tabnine": ["Tabnine", "TabNine"],
    "Replit AI": ["Replit", "Replit AI", "Replit Agent"],
    "Augment Code": ["Augment", "Augment Code"],
    "CodeGeeX": ["CodeGeeX", "CodeGeeX"],
    "Kimi Code": ["Kimi Code", "KimiCode"],
    "通义灵码": ["通义灵码", "Tongyi Lingma", "Lingma"],
    "CodeBuddy": ["CodeBuddy", "Code Buddy", "腾讯 CodeBuddy"],
    "百度 Comate": ["Comate", "百度 Comate", "Baidu Comate"],
    "iFlyCode": ["iFlyCode", "iFly Code", "讯飞"],
    "MiniMax Code": ["MiniMax Code", "MiniMaxCode"],
    "MiMo Code": ["MiMo Code", "MiMoCode", "小米 Code"],
    "Kiro": ["Kiro"],
}


def _load_entity_map() -> dict[str, str]:
    """从 KB 加载已知实体 → 构建 name/alias → canonical_name 映射"""
    entity_map: dict[str, str] = {}  # match_key → canonical_name

    for fname in ["vendors.json", "tools.json"]:
        path = KB_DIR / fname
        if not path.exists():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        for item in data:
            name = item.get("name", "")
            if not name:
                continue
            # 实体名本身
            entity_map[name.lower()] = name
            # 别名
            for alias in ENTITY_ALIASES.get(name, []):
                entity_map[alias.lower()] = name

    return entity_map


def _match_entity(title: str, entity_map: dict[str, str]) -> tuple[str | None, int]:
    """匹配标题中的已知实体。返回 (实体名, 得分)。

    得分规则:
      - 3 分: 实体名精确匹配（case-insensitive）
      - 2 分: 别名匹配
      - 0 分: 无匹配
    """
    title_lower = title.lower()

    # 先检查精确匹配（实体名本身）
    for match_key, canonical_name in entity_map.items():
        if match_key in title_lower:
            # 检查是否是实体名本身（非别名）
            for fname in ["vendors.json", "tools.json"]:
                path = KB_DIR / fname
                if not path.exists():
                    continue
                data = json.loads(path.read_text(encoding="utf-8"))
                for item in data:
                    if item.get("name", "").lower() == match_key:
                        return (canonical_name, 3)  # 实体名精确匹配

            return (canonical_name, 2)  # 别名匹配

    return (None, 0)


def _signal_score(title: str) -> int:
    """计算信号加分"""
    score = 0
    for kw in HIGH_VALUE_SIGNALS:
        if kw in title:
            score += 2
            break  # 最高 2 分
    if score == 0:
        for kw in PRICE_SIGNALS + MODEL_SIGNALS + STATUS_SIGNALS:
            if kw in title:
                score += 1
                break
    return score


def _source_score(source: str, source_type: str) -> int:
    """来源质量加分"""
    if source in QUALITY_SOURCES or source_type in QUALITY_SOURCES:
        return 1
    return 0


def _classify_level(score: int) -> str:
    """评分 → 优先级"""
    if score >= 5:
        return "high"
    elif score >= 3:
        return "medium"
    return "low"


def scan(date_str: str | None = None) -> list[dict]:
    """主入口: 扫描最新热点数据，按实体匹配 + 评分筛选候选文章

    Args:
        date_str: 日期字符串，None 表示今天

    Returns:
        候选文章列表（与 article_discovery.py 相同格式）
    """
    if date_str is None:
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    entity_map = _load_entity_map()
    print(f"  已加载 {len(entity_map)} 个实体匹配词（含别名）")

    # 加载最新热点数据
    items = storage.load_latest(limit=2000)
    if not items:
        print("  ⚠️ 无热点数据")
        return []

    print(f"  扫描 {len(items)} 条热点...")

    candidates = []
    seen_urls = set()

    for item in items:
        title = str(item.get("title", ""))
        url = str(item.get("url", ""))
        source = str(item.get("source", ""))
        source_type = str(item.get("source_type", ""))

        # 跳过无标题
        if not title:
            continue

        # 实体匹配
        entity_name, entity_score = _match_entity(title, entity_map)
        if entity_score == 0:
            continue  # 没有匹配到已知实体，跳过

        # 信号加分
        signal_bonus = _signal_score(title)

        # 来源加分
        source_bonus = _source_score(source, source_type)

        total_score = entity_score + signal_bonus + source_bonus

        # 阈值: 至少 3 分
        if total_score < 3:
            continue

        # URL 去重
        if url and url in seen_urls:
            continue
        if url:
            seen_urls.add(url)

        level = _classify_level(total_score)

        candidates.append({
            "title": title,
            "url": url,
            "hot_metric": item.get("hot_metric", 0),
            "source": source,
            "source_type": source_type,
            "author": f"{entity_name} (score={total_score})",
            "level": level,
            "collected_at": item.get("collected_at", ""),
            "_score": total_score,          # 调试用，报告生成时移除
            "_entity": entity_name,          # 调试用
            "_signals": signal_bonus,        # 调试用
            "_source_bonus": source_bonus,   # 调试用
        })

    # 按分数降序
    candidates.sort(key=lambda x: x["_score"], reverse=True)

    print(f"  匹配到 {len(candidates)} 条候选 (high={sum(1 for c in candidates if c['level']=='high')}, "
          f"medium={sum(1 for c in candidates if c['level']=='medium')}, "
          f"low={sum(1 for c in candidates if c['level']=='low')})")

    return candidates


def save_candidates(candidates: list[dict], date_str: str | None = None) -> Path:
    """保存候选文章到 data/pending/{date}/articles.json"""
    if date_str is None:
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    out_dir = PENDING_DIR / date_str
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "articles.json"

    # 移除调试字段
    clean = []
    for c in candidates:
        clean.append({
            k: v for k, v in c.items() if not k.startswith("_")
        })

    out_path.write_text(json.dumps({
        "date": date_str,
        "total": len(clean),
        "scanner": "maintenance_scanner",
        "candidates": clean,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"✅ {out_path}")
    return out_path


def main():
    candidates = scan()
    save_candidates(candidates)


if __name__ == "__main__":
    main()