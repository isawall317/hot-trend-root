"""腾讯云 TokenHub 定价页提取器

目标: https://cloud.tencent.com/document/product/1823/130092
策略: 文档页静态 HTML → httpx + BeautifulSoup 解析表格
提取: Coding Plan 套餐名 + 月费 + 请求限制
"""

import re
from bs4 import BeautifulSoup
from . import register
from .base import BaseParser, ExtractResult


TENCENT_URL = "https://cloud.tencent.com/document/product/1823/130092"


@register("tencent")
class TencentParser(BaseParser):
    async def extract(self, client) -> ExtractResult:
        url = self.config.get("urls", {}).get("docs") or TENCENT_URL
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
            # 找表头行（含"套餐"关键词）
            header_cells = [c.get_text(strip=True) for c in rows[0].find_all(["td", "th"])]
            if not any("套餐" in c for c in header_cells): continue

            for row in rows[1:]:
                cells = [c.get_text(strip=True) for c in row.find_all(["td", "th"])]
                if len(cells) < 2: continue
                label = cells[0]
                if "套餐内容" in label:
                    # 这是表头行，cells[1:] 是套餐名
                    continue
                if "原价" in label:
                    # cells[1:] 是价格
                    for i, price_text in enumerate(cells[1:]):
                        if i >= len(plans):
                            plans.append({"plan": f"Plan-{i+1}", "type": "Coding Plan"})
                        price = _parse_price(price_text)
                        if price: plans[i]["monthlyPrice"] = price
                if "用量" in label or "请求" in label:
                    # 提取请求数
                    for i, req_text in enumerate(cells[1:]):
                        if i < len(plans):
                            reqs = re.findall(r"(\d+[\d,]*)\s*次", req_text)
                            if reqs:
                                plans[i]["monthlyRequests"] = int(reqs[-1].replace(",", ""))

        # 补充套餐名
        plan_names = ["Lite", "Pro"]
        for i, p in enumerate(plans):
            if i < len(plan_names):
                p["plan"] = plan_names[i]

        extracted = ["monthlyPrice", "monthlyRequests"] if plans else []

        return ExtractResult(
            vendor_id=self.vendor_id, vendor_name=self.vendor_name,
            plans=plans,
            extracted_fields=extracted,
            missing_fields=["measuredMonthlyToken"],
            source_url=url,
        )


def _parse_price(text: str) -> float | None:
    m = re.search(r"(\d+[\d,]*\.?\d*)\s*元", text)
    if m: return float(m.group(1).replace(",", ""))
    return None