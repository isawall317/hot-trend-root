"""配置加载：config.yaml + .env 环境变量。

config.yaml 声明用哪个 LLM provider/model，敏感 key 从 .env 读取。
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from dotenv import load_dotenv

# OpenAI 兼容 provider 的预置 base_url（不写 base_url 时按 provider 查表）
KNOWN_BASE_URLS: dict[str, str | None] = {
    "openai": None,  # 走 openai SDK 默认
    "anthropic": None,  # 走 anthropic SDK 默认
    "minimax": "https://api.minimaxi.com/anthropic",
    "zhipu": "https://open.bigmodel.cn/api/paas/v4/",
    "deepseek": "https://api.deepseek.com/v1",
    "kimi": "https://api.moonshot.ai/v1",
    "bailian": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "ark": "https://ark.cn-beijing.volces.com/api/v3",
}


@dataclass
class LLMConfig:
    provider: str = "zhipu"
    model: str = "glm-5.2"
    api_key: str = ""
    base_url: str | None = None
    temperature: float = 0.3


@dataclass
class ScoringConfig:
    incubate_threshold: int = 22  # >=22 标 "值得孵化"
    watch_threshold: int = 18  # 18-22 标 "观察"


@dataclass
class Config:
    llm: LLMConfig = field(default_factory=LLMConfig)
    scoring: ScoringConfig = field(default_factory=ScoringConfig)
    opportunities_dir: Path = Path("opportunities/cards")


def find_config_path(start: Path | None = None) -> Path | None:
    """从当前目录向上找 config.yaml（最多到 home 目录）。"""
    start = start or Path.cwd()
    for p in [start, *start.parents]:
        candidate = p / "config.yaml"
        if candidate.exists():
            return candidate
        if p == Path.home():
            break
    return None


def load_config() -> Config:
    """加载 config.yaml + .env，构造 Config 对象。

    找不到 config.yaml 时返回默认值（智谱 GLM-5.2），但 API key 需要环境变量。
    """
    load_dotenv()  # 加载 .env，不报错如果不存在

    cfg_path = find_config_path()
    data = {}
    if cfg_path:
        with open(cfg_path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

    llm_data = data.get("llm", {})
    provider = llm_data.get("provider", "zhipu")
    api_key_env = llm_data.get("api_key_env", _default_key_env_name(provider))
    api_key = os.environ.get(api_key_env, "")
    base_url = llm_data.get("base_url") or KNOWN_BASE_URLS.get(provider)

    llm = LLMConfig(
        provider=provider,
        model=llm_data.get("model", _default_model_name(provider)),
        api_key=api_key,
        base_url=base_url,
        temperature=float(llm_data.get("temperature", 0.3)),
    )

    scoring_data = data.get("scoring", {})
    scoring = ScoringConfig(
        incubate_threshold=int(scoring_data.get("incubate_threshold", 22)),
        watch_threshold=int(scoring_data.get("watch_threshold", 18)),
    )

    return Config(
        llm=llm,
        scoring=scoring,
        opportunities_dir=Path(data.get("opportunities_dir", "opportunities/cards")),
    )


def _default_key_env_name(provider: str) -> str:
    return {
        "zhipu": "ZHIPU_API_KEY",
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "minimax": "MINIMAX_API_KEY",
        "deepseek": "DEEPSEEK_API_KEY",
        "kimi": "MOONSHOT_API_KEY",
        "bailian": "DASHSCOPE_API_KEY",
        "ark": "ARK_API_KEY",
    }.get(provider, f"{provider.upper()}_API_KEY")


def _default_model_name(provider: str) -> str:
    return {
        "zhipu": "glm-5.2",
        "openai": "gpt-4o-mini",
        "anthropic": "claude-sonnet-4-5",
        "minimax": "MiniMax-M3",
        "deepseek": "deepseek-chat",
        "kimi": "moonshot-v1-32k",
        "bailian": "qwen-plus",
        "ark": "doubao-pro-32k",
    }.get(provider, "")
