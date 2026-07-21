"""GitHub Copilot 定价页提取器

目标: https://github.com/features/copilot/plans
策略: Playwright 渲染 → 提取套餐名称和价格
"""

import re
from . import register
from .base import BasePlaywrightParser, ExtractResult


GITHUB_URL = "https://github.com/features/copilot/plans"


@register("github")
class GitHubParser(BasePlaywrightParser):
    async def extract(self, client) -> ExtractResult:
        url = self.config.get("urls", {}).get("pricing") or GITHUB_URL

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

        # Parse: Pro ... $10 USD per user / month
        patterns = [
            (r"Pro\n.*?\n\$\s*(\d+)\s*\n.*?\n.*?per user / month", "Pro", "pro"),
            (r"Pro\+\n.*?\n\$\s*(\d+)\s*\n.*?\n.*?per user / month", "Pro+", "pro"),
            (r"Max\n.*?\n\$\s*(\d+)\s*\n.*?\n.*?per user / month", "Max", "max"),
        ]

        for pattern, plan_name, tier in patterns:
            m = re.search(pattern, text, re.DOTALL)
            if m:
                plans.append({
                    "plan": plan_name,
                    "type": "Coding Plan",
                    "tier": tier,
                    "monthlyPrice": int(m.group(1)),
                    "currency": "$",
                    "note": "Playwright 自动提取",
                })

        # Fallback: simpler pattern matching
        if not plans:
            for line in text.split("\n"):
                line = line.strip()
                # Match: "Pro $10 USD per user / month"
                m = re.match(r"(Pro\+?|Max)\s+\$(\d+)\s+USD", line)
                if m:
                    plan_name = m.group(1)
                    tier = "max" if plan_name == "Max" else "pro"
                    plans.append({
                        "plan": plan_name, "type": "Coding Plan", "tier": tier,
                        "monthlyPrice": int(m.group(2)), "currency": "$",
                        "note": "Playwright 文本匹配",
                    })

        extracted = ["monthlyPrice"] if plans else []

        return ExtractResult(
            vendor_id=self.vendor_id,
            vendor_name=self.vendor_name,
            plans=plans,
            extracted_fields=extracted,
            missing_fields=["monthlyRequests", "measuredMonthlyToken"],
            source_url=url,
        )