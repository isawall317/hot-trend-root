"""MiniMax Token Plan 定价页提取器

目标: https://platform.minimaxi.com/docs/guides/pricing-token-plan
策略: 文档页静态 HTML → httpx + BeautifulSoup 解析表格
提取: Token Plan 套餐名 + 月费 + 描述
"""

import re
from bs4 import BeautifulSoup
from . import register
from .base import BaseParser, ExtractResult


MINIMAX_URL = "https://platform.minimaxi.com/docs/guides/pricing-token-plan"


@register("minimax")
class MinimaxParser(BaseParser):
    async def extract(self, client) -> ExtractResult:
        # 用 docs 文档页（含价格表），非 urls.pricing（那是订阅 SPA，登录态无表）
        url = self.config.get("urls", {}).get("docs") or MINIMAX_URL
        try:
            resp = await client.get(url, timeout=20, follow_redirects=True,
                                    headers={"User-Agent": "Mozilla/5.0"})
        except Exception as e:
            return ExtractResult(vendor_id=self.vendor_id, vendor_name=self.vendor_name,
                                 source_url=url, error=f"HTTP 请求失败: {e}")

        if resp.status_code != 200:
            return ExtractResult(vendor_id=self.vendor_id, vendor_name=self.vendor_name,
                                 source_url=url, error=f"HTTP {resp.status_code}")

        soup = BeautifulSoup(resp.text, "lxml")
        plans = []

        for table in soup.find_all("table"):
            rows = table.find_all("tr")
            if not rows: continue
            header = [c.get_text(strip=True) for c in rows[0].find_all(["td", "th"])]
            if not header or not any(h in ("Plus", "Max", "Ultra") for h in header):
                # 只处理套餐对比表（表头含 Plus/Max/Ultra），跳过积分购买表等
                continue

            for row in rows[1:]:
                cells = [c.get_text(strip=True) for c in row.find_all(["td", "th"])]
                if len(cells) < 2: continue
                label = cells[0]
                if "价格" in label:
                    for i, price_text in enumerate(cells[1:]):
                        if i >= len(plans):
                            plans.append({})
                        price = _parse_price(price_text)
                        if price:
                            plans[i]["monthlyPrice"] = price
                            plans[i]["currency"] = "¥"
                if "适合场景" in label:
                    for i, desc in enumerate(cells[1:]):
                        if i < len(plans):
                            plans[i]["description"] = desc

            for i, h in enumerate(header[1:]):
                if i < len(plans) and h:
                    plans[i]["plan"] = h
                    plans[i]["type"] = "Token Plan"

        extracted = ["monthlyPrice"] if plans else []

        return ExtractResult(
            vendor_id=self.vendor_id, vendor_name=self.vendor_name,
            plans=plans,
            extracted_fields=extracted,
            missing_fields=["measuredMonthlyToken"],
            source_url=url,
        )


def _parse_price(text: str) -> float | None:
    m = re.search(r"[¥￥]\s*(\d+[\d,]*)", text)
    if m: return float(m.group(1).replace(",", ""))
    return None
