"""编排核心：抽取 → LLM 洞察 → LLM 评分 → 写卡。

LLM 结构化输出校验失败 → 自动重试 1 次（追加"严格 JSON"指令）。
机会卡以 YAML frontmatter + Markdown 形式写入 opportunities/cards/。
"""
from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

from pydantic import ValidationError

from .config import Config
from .extractor import extract
from .llm import LLMClient
from .models import Insight, OpportunityCard, Score, TrendItem, verdict_for


class AnalyzerError(Exception):
    pass


# ---------- prompt 加载 ----------

_PROMPTS_DIR = Path(__file__).parent / "prompts"
_prompt_cache: dict[str, str] = {}


def _load_prompt(name: str) -> str:
    """加载 prompt 模板，返回纯文本。"""
    if name not in _prompt_cache:
        path = _PROMPTS_DIR / f"{name}.md"
        _prompt_cache[name] = path.read_text(encoding="utf-8")
    return _prompt_cache[name]


# ---------- JSON 提取 ----------


def _extract_json(text: str) -> dict:
    """从 LLM 输出里抠 JSON（容忍 ```json 包裹 / 前后散文）。"""
    # 先尝试直接 parse
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 找 ```json ... ``` 代码块
    m = re.search(r"```(?:json)?\s*\n?(.+?)\n?```", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1).strip())
        except json.JSONDecodeError:
            pass

    # 找第一个 { 到最后一个 }
    first = text.find("{")
    last = text.rfind("}")
    if first != -1 and last > first:
        try:
            return json.loads(text[first : last + 1])
        except json.JSONDecodeError:
            pass

    raise ValueError(f"无法从 LLM 输出提取 JSON，前 200 字符: {text[:200]}")


# ---------- 两步 LLM ----------


def _llm_insight(client: LLMClient, title: str, content: str) -> Insight:
    """洞察步：失败重试 1 次。"""
    template = _load_prompt("insight")
    # 用字符串拼接代替 .format()，避免正文中花括号被误解析为占位符
    separator = "---\n\n"
    input_text = f"TITLE: {title}\n\nCONTENT:\n{content[:8000]}"
    user_msg = template + separator + input_text

    # 第一次：用 system+user
    last_err = None
    for attempt in range(2):
        system = (
            "你是资深 indie hacker，从内容热点中挖掘可用 AI 工具解决的真实痛点。"
            "只输出 JSON，不要任何额外说明、不要 markdown 代码块。"
        )
        if attempt == 1:
            # 重试：追加强约束
            system += "\n\n注意：上次输出不是合法 JSON，这次必须只输出 `{...}` 形式的纯 JSON。"
        resp = client.chat(system=system, user=user_msg, max_tokens=2500)
        try:
            data = _extract_json(resp.text)
            return Insight.model_validate(data)
        except (ValueError, ValidationError) as e:
            last_err = e
            continue
    raise AnalyzerError(f"洞察步 LLM 输出无法解析，重试后仍失败: {last_err}")


def _llm_score(client: LLMClient, insight: Insight) -> Score:
    """评分步：失败重试 1 次。"""
    template = _load_prompt("score")
    insight_json = json.dumps(insight.model_dump(), ensure_ascii=False, indent=2)
    separator = "\n```json\n"
    ending = "\n```\n"
    user_msg = template.replace("{insight_json}", insight_json)  # 仅替换这一个占位符

    last_err = None
    for attempt in range(2):
        system = (
            "你是冷静的 indie hacker 导师，给学生提交的项目点子打 6 维评分。"
            "只输出 JSON，不要任何额外说明、不要 markdown 代码块。"
        )
        if attempt == 1:
            system += "\n\n注意：上次输出不是合法 JSON，这次必须只输出 `{...}` 形式的纯 JSON。"
        resp = client.chat(system=system, user=user_msg, max_tokens=600)
        try:
            data = _extract_json(resp.text)
            return Score.model_validate(data)
        except (ValueError, ValidationError) as e:
            last_err = e
            continue
    raise AnalyzerError(f"评分步 LLM 输出无法解析，重试后仍失败: {last_err}")


# ---------- 主入口 ----------


def analyze_url(
    url: str,
    cfg: Config,
    *,
    source_name: str = "manual",
    fallback_title: str = "",
) -> OpportunityCard:
    """对单个 URL 跑完整分析流程，返回机会卡。"""
    client = LLMClient(cfg.llm)

    # 1. 抽取
    article = extract(url)
    title = article.title or fallback_title or url

    # 2. 洞察
    insight = _llm_insight(client, title=title, content=article.content)

    # 3. 评分
    score = _llm_score(client, insight)

    # 4. 组装卡片（id 由调用方在写盘时分配，这里先给 0）
    card = OpportunityCard(
        id=0,
        source=source_name,
        source_url=url,
        discovered_at=date.today(),
        title=insight.surface_topic or title,
        insight=insight,
        score=score,
    )
    return card


def analyze_trend(trend: TrendItem, cfg: Config) -> OpportunityCard:
    """对一条 TrendItem 跑分析（用 trend.title 作为 fallback）。"""
    return analyze_url(
        trend.url,
        cfg,
        source_name=trend.source,
        fallback_title=trend.title,
    )


# ---------- 卡片序列化 ----------


def _yaml_escape(s: str) -> str:
    """YAML 字符串安全转义：含特殊字符就用双引号包裹。"""
    if not s:
        return '""'
    if re.search(r"[:#\[\]{}&,*?|<>=!%@`\"'\\\n]", s):
        return json.dumps(s, ensure_ascii=False)
    return s


def render_card_md(card: OpportunityCard, *, thresholds=(22, 18)) -> str:
    """把 OpportunityCard 渲染成 Markdown（YAML frontmatter + 正文）。"""
    inc, watch = thresholds
    total = card.score.total
    verdict = verdict_for(total, inc, watch)
    ideas_md = "\n".join(
        f"### {i+1}. {idea.name}\n\n{idea.description}\n"
        for i, idea in enumerate(card.insight.project_ideas)
    )

    return f"""---
id: {card.id:03d}
source: {card.source}
source_url: {_yaml_escape(card.source_url)}
discovered_at: {card.discovered_at.isoformat()}
title: {_yaml_escape(card.title)}
scores:
  demand: {card.score.demand}
  willingness_to_pay: {card.score.willingness_to_pay}
  ai_feasibility: {card.score.ai_feasibility}
  competition: {card.score.competition}
  dev_cost: {card.score.dev_cost}
  monetization: {card.score.monetization}
  total: {total}
verdict: {verdict}
---

# 机会卡 #{card.id:03d}：{card.title}

> 来源：[{card.source}]({card.source_url}) · 评分 **{total}/30** · 判定：**{verdict}**

## 表面话题
{card.insight.surface_topic}

## 底层痛点 ★
{card.insight.underlying_pain}

- **痛点频率**：{card.insight.pain_frequency}
- **目标人群**：{card.insight.target_audience}
- **现有方案**：{card.insight.current_solution}
- **付费信号**：{card.insight.payment_signal}

## AI 增益点 ★
{card.insight.ai_leverage}

## 反信号
{card.insight.anti_signal}

## 项目雏形
{ideas_md}

## 评分理由
{card.score.rationale}

| 维度 | 分数 |
|---|---|
| 需求强度 | {card.score.demand}/5 |
| 付费意愿 | {card.score.willingness_to_pay}/5 |
| AI 可行性 | {card.score.ai_feasibility}/5 |
| 竞争(倒扣) | {card.score.competition}/5 |
| 开发成本(倒扣) | {card.score.dev_cost}/5 |
| 变现潜力 | {card.score.monetization}/5 |
| **总分** | **{total}/30** |
"""


def _slugify(text: str, max_len: int = 40) -> str:
    """把标题转成文件名友好的 slug。"""
    # 保留中英文字母数字，其他转 -
    slug = re.sub(r"[^\w\u4e00-\u9fff]+", "-", text).strip("-")
    return slug[:max_len] or "untitled"


def save_card(card: OpportunityCard, cards_dir: Path) -> Path:
    """分配下一个 id，写盘，返回写入路径。"""
    cards_dir.mkdir(parents=True, exist_ok=True)

    # 找下一个 id
    existing_ids = []
    for f in cards_dir.glob("*.md"):
        m = re.match(r"^(\d+)-", f.name)
        if m:
            existing_ids.append(int(m.group(1)))
    next_id = (max(existing_ids) + 1) if existing_ids else 1

    card.id = next_id
    md = render_card_md(card)
    slug = _slugify(card.title)
    filename = f"{next_id:03d}-{slug}.md"
    path = cards_dir / filename
    path.write_text(md, encoding="utf-8")
    return path
