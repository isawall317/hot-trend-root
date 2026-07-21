"""Kimi 定价页提取器

目标: https://platform.kimi.com/docs/pricing/chat
策略: Playwright headless Chromium 渲染 → 点击展开模型卡片 → 提取价格
"""

import re
from . import register
from .base import BasePlaywrightParser, ExtractResult


KIMI_URL = "https://platform.kimi.com/docs/pricing/chat"


@register("kimi")
class KimiParser(BasePlaywrightParser):
    async def extract(self, client) -> ExtractResult:
        url = self.config.get("urls", {}).get("docs") or KIMI_URL

        # 使用 Playwright 交互：渲染 → 点击展开卡片 → 提取文本
        try:
            from playwright.async_api import async_playwright
            pw = await async_playwright().start()
            browser = await pw.chromium.launch(headless=True, args=["--no-sandbox"])
            page = await browser.new_page()
            await page.goto(url, wait_until="load", timeout=30000)
            await page.wait_for_timeout(3000)

            # 点击展开所有模型卡片
            model_names = [
                "Kimi K3", "Kimi K2.7 Code", "Kimi K2.6",
                "Kimi K2.5", "Moonshot V1",
            ]
            for name in model_names:
                try:
                    await page.click(f"text={name}", timeout=2000)
                    await page.wait_for_timeout(500)
                except Exception:
                    pass

            text = await page.evaluate("() => document.body.innerText")
            await browser.close()
            await pw.stop()
        except Exception as e:
            return ExtractResult(
                vendor_id=self.vendor_id, vendor_name=self.vendor_name,
                source_url=url, error=f"Playwright 失败: {e}",
            )

        if not text:
            return ExtractResult(
                vendor_id=self.vendor_id, vendor_name=self.vendor_name,
                source_url=url, error="页面内容为空",
            )

        # 解析价格行: model-id  1M tokens  ¥input  ¥output  ¥cache  context
        models = []
        for line in text.split("\n"):
            line = line.strip()
            m = re.match(
                r"([\w.-]+)\s+1M\s+tokens\s+¥([\d.]+)\s+¥([\d.]+)\s+¥([\d.]+)\s+([\d,]+)\s+tokens",
                line,
            )
            if m:
                models.append({
                    "name": m.group(1),
                    "input_price_per_1m": float(m.group(2)),
                    "output_price_per_1m": float(m.group(3)),
                    "cache_price_per_1m": float(m.group(4)),
                    "context": int(m.group(5).replace(",", "")),
                })

        extracted = ["models"] if models else []

        return ExtractResult(
            vendor_id=self.vendor_id,
            vendor_name=self.vendor_name,
            plans=[{"models": models, "count": len(models),
                    "note": "API 按量计费，Coding Plan 需登录控制台"}],
            extracted_fields=extracted,
            missing_fields=["monthlyPrice"],
            source_url=url,
        )