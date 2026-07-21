"""智谱AI 定价页提取器

目标: https://open.bigmodel.cn/pricing
策略: Playwright headless Chromium 渲染 → BS4 解析
提取: API 按量计费模型名 + 价格
"""

import re
from bs4 import BeautifulSoup
from . import register
from .base import BasePlaywrightParser, ExtractResult


ZHIPU_URL = "https://open.bigmodel.cn/pricing"


@register("zhipu")
class ZhipuParser(BasePlaywrightParser):
    async def extract(self, client) -> ExtractResult:
        url = self.config.get("urls", {}).get("pricing") or ZHIPU_URL
        html = await self.fetch_rendered_html(url)
        if not html:
            return ExtractResult(
                vendor_id=self.vendor_id, vendor_name=self.vendor_name,
                source_url=url, error="Playwright 渲染失败",
            )

        soup = BeautifulSoup(html, "lxml")
        models = []
        current_model = None

        for table in soup.find_all("table"):
            rows = table.find_all("tr")
            for row in rows:
                cells = [c.get_text(strip=True) for c in row.find_all(["td", "th"])]
                if not cells or len(cells) < 2:
                    continue
                # 检查是否是模型名行
                model_match = re.match(r"^(GLM-[-\d.A-Za-z]+)", cells[0])
                if model_match:
                    model = {"name": model_match.group(1)}
                    # 列2+: 价格
                    for i, cell in enumerate(cells[2:], 2):
                        price = _parse_price(cell)
                        if price is not None:
                            if i == 2: model["input_price_per_1m"] = price
                            elif i == 3: model["output_price_per_1m"] = price
                            elif i == 4: model["cache_price_per_1m"] = price
                    if "input_price_per_1m" in model:
                        models.append(model)
                        current_model = model
                elif current_model and cells[0] and "输入长度" in cells[0]:
                    # 子行：同一模型不同上下文长度，取更低的价格
                    for i, cell in enumerate(cells[1:], 1):
                        price = _parse_price(cell)
                        if price is not None:
                            key = {1: "input_price_per_1m", 2: "output_price_per_1m", 3: "cache_price_per_1m"}.get(i)
                            if key and (key not in current_model or price < current_model[key]):
                                current_model[key] = price

        extracted = ["models"] if models else []

        return ExtractResult(
            vendor_id=self.vendor_id, vendor_name=self.vendor_name,
            plans=[{"models": models, "count": len(models),
                    "note": "API 按量计费，Coding Plan 需登录控制台"}],
            extracted_fields=extracted,
            missing_fields=["monthlyPrice"],
            source_url=url,
        )


def _parse_price(text: str) -> float | None:
    """提取价格: '8元', '¥5  / M Tokens', '0.5元'"""
    m = re.search(r"[¥￥]\s*(\d+[\d,]*\.?\d*)", text)
    if m: return float(m.group(1).replace(",", ""))
    m = re.search(r"(\d+[\d,]*\.?\d*)\s*元", text)
    if m: return float(m.group(1).replace(",", ""))
    return None
