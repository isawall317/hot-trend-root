"""多模型薄抽象：覆盖 OpenAI 兼容 + Anthropic 兼容 provider。

设计原则：
- OpenAI 兼容 provider（智谱/DeepSeek/Kimi/百炼/方舟）→ openai SDK + base_url
- Anthropic 兼容 provider（Claude/MiniMax）→ anthropic SDK + 可选 base_url
- 只暴露一个 chat() 方法，返回纯文本
"""
from __future__ import annotations

from dataclasses import dataclass

from .config import LLMConfig


@dataclass
class LLMResponse:
    text: str
    model: str


class LLMClient:
    """一个接口，覆盖 OpenAI 兼容 + Anthropic 兼容。"""

    # 走 anthropic SDK 的 provider（system 是顶层参数，不是 message）
    ANTHROPIC_COMPAT = frozenset({"anthropic", "minimax"})

    def __init__(self, cfg: LLMConfig):
        if not cfg.api_key:
            env_hint = "（环境变量未设置 API key，请检查 .env 或 config.yaml 的 api_key_env）"
            raise ValueError(f"LLM API key 为空 {env_hint}")
        self.cfg = cfg
        self._client = self._build_client()

    def _build_client(self):
        if self.cfg.provider in self.ANTHROPIC_COMPAT:
            from anthropic import Anthropic

            kwargs: dict = {"api_key": self.cfg.api_key}
            if self.cfg.base_url:
                kwargs["base_url"] = self.cfg.base_url
            return Anthropic(**kwargs)

        # OpenAI 兼容协议
        from openai import OpenAI

        return OpenAI(api_key=self.cfg.api_key, base_url=self.cfg.base_url)

    def chat(self, system: str, user: str, *, max_tokens: int = 3000) -> LLMResponse:
        """单轮 chat，返回纯文本。"""
        temperature = self.cfg.temperature

        if self.cfg.provider in self.ANTHROPIC_COMPAT:
            resp = self._client.messages.create(
                model=self.cfg.model,
                system=system,
                messages=[{"role": "user", "content": user}],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            text = resp.content[0].text
        else:
            resp = self._client.chat.completions.create(
                model=self.cfg.model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            text = resp.choices[0].message.content or ""

        return LLMResponse(text=text, model=self.cfg.model)


def build_client(cfg: LLMConfig) -> LLMClient:
    """工厂函数：从 LLMConfig 构造 client。"""
    return LLMClient(cfg)
