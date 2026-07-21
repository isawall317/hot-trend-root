"""Claude 定价页提取器

目标: https://claude.com/pricing
策略: Playwright 渲染 → 提取套餐名称和价格
"""

import re
from . import register
from .base import BasePlaywrightParser, ExtractResult


CLAUDE_URL = "https://claude.com/pricing"


@register("claude")
class ClaudeParser(BasePlaywrightParser):
    async def extract(self, client) -> ExtractResult:
        url = self.config.get("urls", {}).get("pricing") or CLAUDE_URL

        try:
            from playwright.async_api import async_playwright
            pw = await async_playwright().start()
            browser = await pw.chromium.launch(headless=True, args=["--no-sandbox"])
            page = await browser.new_page()
            await page.goto(url, wait_until="load", timeout=30000)
            await page.wait_for_timeout(5000)
            text = await page.evaluate("() => document.body.innerText")
            await browser.close()
            await pw.stop()
        except Exception as e:
            return ExtractResult(
                vendor_id=self.vendor_id, vendor_name=self.vendor_name,
                source_url=url, error=f"Playwright 失败: {e}",
            )

        plans = []

        # Simpler approach: find plan names and their prices
        lines = text.split("\n")
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            # Match plan names: Pro, Max
            if line in ("Pro", "Max"):
                plan_name = line
                tier = "pro" if plan_name == "Pro" else "max"
                # Look ahead for price: "$17" or "From $100"
                for j in range(i + 1, min(i + 20, len(lines))):
                    next_line = lines[j].strip()
                    # "From $100" pattern
                    m = re.match(r"From \$(\d+)", next_line)
                    if m:
                        plans.append({
                            "plan": plan_name, "type": "Coding Plan", "tier": tier,
                            "monthlyPrice": int(m.group(1)), "currency": "$",
                            "note": "Playwright 自动提取",
                        })
                        break
                    # "$17" pattern (standalone price)
                    m = re.match(r"^\$(\d+)$", next_line)
                    if m:
                        price = int(m.group(1))
                        # Check if there's a monthly billing price a few lines later
                        monthly_price = price
                        for k in range(j + 1, min(j + 5, len(lines))):
                            m2 = re.match(r".*\$(\d+) if billed monthly", lines[k].strip())
                            if m2:
                                monthly_price = int(m2.group(1))
                                break
                        plans.append({
                            "plan": plan_name, "type": "Coding Plan", "tier": tier,
                            "monthlyPrice": monthly_price, "currency": "$",
                            "note": "Playwright 自动提取",
                        })
                        break
                    # "Free" or "$0" pattern
                    if next_line == "$0" or next_line == "Free":
                        plans.append({
                            "plan": plan_name, "type": "Coding Plan", "tier": "lite",
                            "monthlyPrice": 0, "currency": "$",
                            "note": "Playwright 自动提取",
                        })
                        break
            i += 1

        extracted = ["monthlyPrice"] if plans else []

        return ExtractResult(
            vendor_id=self.vendor_id,
            vendor_name=self.vendor_name,
            plans=plans,
            extracted_fields=extracted,
            missing_fields=["monthlyRequests", "measuredMonthlyToken"],
            source_url=url,
        )