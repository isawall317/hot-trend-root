"""智谱AI 定价页提取器

目标: https://open.bigmodel.cn/pricing
状态: SPA 页面，httpx 无法提取静态定价数据。待后续找到静态文档/API JSON 端点。
"""

from . import register
from .base import BaseParser, ExtractResult


@register("zhipu")
class ZhipuParser(BaseParser):
    async def extract(self, client) -> ExtractResult:
        return ExtractResult(
            vendor_id=self.vendor_id,
            vendor_name=self.vendor_name,
            error="SPA 页面，httpx 无法提取（需 JS 渲染）",
            source_url=self.config.get("urls", {}).get("pricing", ""),
        )