"""Pydantic 数据模型：贯穿全流程的数据结构。

流程：  TrendItem → extract → Article → LLM insight → Insight
                                     → LLM score   → Score
                                                    → OpportunityCard
"""
from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, field_validator


# ---------- 采集层 ----------


class TrendItem(BaseModel):
    """热榜单条。各 source 抓取后归一化到这个结构。"""

    source: Literal["github", "hn", "v2ex"]
    title: str
    url: str
    hot: str = ""  # 热度，格式化后的字符串（"1.2k stars today" / "423 points" / "89 replies"）
    raw_hot: int = 0  # 原始数值，用于排序
    extra: dict = Field(default_factory=dict)  # source 特有字段（language/by 等）


# ---------- 抽取层 ----------


class Article(BaseModel):
    """从 URL 抽取后的干净正文。"""

    url: str
    title: str = ""
    content: str  # Markdown
    excerpt: str = ""  # 前 300 字预览
    method: Literal["trafilatura", "jina"] = "trafilatura"


# ---------- 洞察层（LLM 输出 1）----------


class ProjectIdea(BaseModel):
    """项目雏形里的单条。"""

    name: str = Field(description="一句话项目名")
    description: str = Field(description="2-3 句话说明形态和差异化")


class Insight(BaseModel):
    """结构化洞察 — 9 字段。"""

    surface_topic: str = Field(description="表面话题：这条趋势表面上在讲什么")
    underlying_pain: str = Field(description="底层痛点★：用户真正在为什么发愁")
    pain_frequency: Literal["一次性", "周期性", "日常"] = Field(description="痛点频率")
    target_audience: str = Field(description="目标人群：谁有这个痛")
    current_solution: str = Field(description="现有方案：用户现在怎么解决（手工/付费/忍着）")
    payment_signal: str = Field(description="付费信号：评论区/市场是否有人愿意付钱")
    ai_leverage: str = Field(description="AI 增益点★：AI 能在哪里真正加值（理解/生成/自动化/推理）")
    anti_signal: str = Field(description="反信号：为什么这可能不值得做")
    project_ideas: list[ProjectIdea] = Field(
        description="1-3 个具体可做的 AI 项目雏形", min_length=1, max_length=3
    )


# ---------- 评分层（LLM 输出 2）----------


class Score(BaseModel):
    """6 维评分，每维 1-5。"""

    demand: int = Field(description="需求强度：痛多深，1=轻微 5=刚需", ge=1, le=5)
    willingness_to_pay: int = Field(description="付费意愿：愿不愿掏钱", ge=1, le=5)
    ai_feasibility: int = Field(description="AI 可行性：AI 能不能真正解决问题", ge=1, le=5)
    competition: int = Field(
        description="竞争（5=蓝海无竞品，1=红海满地）：注意倒扣逻辑", ge=1, le=5
    )
    dev_cost: int = Field(
        description="开发成本（5=1周内MVP，1=超1月）：注意倒扣逻辑", ge=1, le=5
    )
    monetization: int = Field(description="变现潜力：客单价×用户量", ge=1, le=5)
    rationale: str = Field(description="一句话评分理由")

    @property
    def total(self) -> int:
        return (
            self.demand
            + self.willingness_to_pay
            + self.ai_feasibility
            + self.competition
            + self.dev_cost
            + self.monetization
        )

    @field_validator("*", mode="before")
    @classmethod
    def _clamp(cls, v):
        if isinstance(v, int):
            return max(1, min(5, v))
        return v


# ---------- 机会卡（最终产物）----------


def verdict_for(total: int, incubate_threshold: int = 22, watch_threshold: int = 18) -> str:
    if total >= incubate_threshold:
        return "值得孵化"
    if total >= watch_threshold:
        return "观察"
    return "丢弃"


class OpportunityCard(BaseModel):
    """一张机会卡 = 元数据 + Insight + Score。"""

    id: int
    source: str  # source 名（github/hn/v2ex/manual）
    source_url: str
    discovered_at: date
    title: str  # 一句话标题（取自 insight.surface_topic 或趋势标题）
    insight: Insight
    score: Score

    @property
    def verdict(self) -> str:
        return verdict_for(self.score.total)
