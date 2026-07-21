"""DeepSeek 定价页提取器

目标: https://api-docs.deepseek.com/quick_start/pricing
策略: Docusaurus 静态 HTML → httpx + BeautifulSoup 解析表格
提取: 模型名 + API 按量计费价格（$/1M tokens）
"""

import re

from bs4 import BeautifulSoup

from . import register
from .base import BaseParser, ExtractResult


DEEPSEEK_URL = "https://api-docs.deepseek.com/quick_start/pricing"
EXPECTED_FIELDS = ["models", "pricing"]  # 期望提取的字段


@register("deepseek")
class DeepSeekParser(BaseParser):
    async def extract(self, client) -> ExtractResult:
        url = self.config.get("urls", {}).get("docs") or DEEPSEEK_URL

        try:
            resp = await client.get(url, timeout=20, follow_redirects=True)
        except Exception as e:
            return ExtractResult(
                vendor_id=self.vendor_id, vendor_name=self.vendor_name,
                source_url=url, error=f"HTTP 请求失败: {e}",
            )

        if resp.status_code != 200:
            return ExtractResult(
                vendor_id=self.vendor_id, vendor_name=self.vendor_name,
                source_url=url, error=f"HTTP {resp.status_code}",
            )

        soup = BeautifulSoup(resp.text, "lxml")

        # 1. 找模型名（在 MODEL 行的 td 里）
        models = []
        for td in soup.select("table td"):
            text = td.get_text(strip=True)
            if re.match(r"^deepseek-[\w.-]+$", text, re.IGNORECASE):
                models.append(text)

        # 2. 找定价行（1M INPUT/OUTPUT TOKENS）
        pricing = {}
        for tr in soup.select("table tr"):
            cells = tr.find_all("td")
            if not cells:
                continue
            label = cells[0].get_text(strip=True)
            if "INPUT" in label and "CACHE MISS" in label:
                pricing["input_per_1m"] = [_price(cells[1]), _price(cells[2]) if len(cells) > 2 else None]
            elif "OUTPUT" in label:
                pricing["output_per_1m"] = [_price(cells[1]), _price(cells[2]) if len(cells) > 2 else None]

        extracted = []
        if models:
            extracted.append("models")
        if pricing:
            extracted.append("pricing")

        missing = [f for f in EXPECTED_FIELDS if f not in extracted]

        return ExtractResult(
            vendor_id=self.vendor_id,
            vendor_name=self.vendor_name,
            plans=[{
                "models": models,
                "pricing": pricing,
                "note": "API 按量计费，非 Coding Plan",
            }],
            extracted_fields=extracted,
            missing_fields=missing,
            source_url=url,
        )


def _price(td) -> float | None:
    """从 td 提取价格（如 $0.14）"""
    if td is None:
        return None
    text = td.get_text(strip=True)
    m = re.search(r"\$?(\d+\.?\d*)", text)
    return float(m.group(1)) if m else None