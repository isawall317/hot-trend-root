"""DeepSeek 定价页提取器 — 占位（Task 14 实现）"""

from . import register
from .base import BaseParser, ExtractResult


@register("deepseek")
class DeepSeekParser(BaseParser):
    async def extract(self, client) -> ExtractResult:
        return ExtractResult(
            vendor_id=self.vendor_id,
            vendor_name=self.vendor_name,
            error="parser 未实现（待 M2-T14）",
        )