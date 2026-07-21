"""字节·方舟 定价页提取器

目标: volcengine.com/docs/82379/1099320
状态: SPA 控制台，httpx 无法提取静态定价数据。
"""

from . import register
from .base import BaseParser, ExtractResult


@register("bytedance")
class BytedanceParser(BaseParser):
    async def extract(self, client) -> ExtractResult:
        return ExtractResult(
            vendor_id=self.vendor_id,
            vendor_name=self.vendor_name,
            error="SPA 页面，httpx 无法提取（需 JS 渲染）",
            source_url=self.config.get("urls", {}).get("docs", ""),
        )
