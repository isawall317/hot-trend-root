"""厂商定价页提取器基类"""

from dataclasses import dataclass, field


@dataclass
class ExtractResult:
    """单次提取结果"""
    vendor_id: str
    vendor_name: str
    plans: list[dict] = field(default_factory=list)       # 提取到的套餐字段
    extracted_fields: list[str] = field(default_factory=list)  # 实际拿到的字段名
    missing_fields: list[str] = field(default_factory=list)    # 期望但没拿到的
    source_url: str = ""
    fetched_at: str = ""
    error: str | None = None


class BaseParser:
    """每个厂商的 parser 继承此类

    vendor_config 来自 vendors.json 的对应条目。
    子类实现 extract() 方法，用 client httpx.get 拉页面/JSON，返回 ExtractResult。
    """
    vendor_id: str = ""
    vendor_name: str = ""

    def __init__(self, vendor_config: dict):
        self.config = vendor_config
        self.vendor_id = vendor_config["id"]
        self.vendor_name = vendor_config["name"]

    async def extract(self, client) -> ExtractResult:
        raise NotImplementedError


class BasePlaywrightParser(BaseParser):
    """需要 JS 渲染的厂商继承此类

    使用 Playwright headless Chromium 获取渲染后的页面 HTML，
    然后子类用 BeautifulSoup 解析。
    """
    playwright = None  # 类级别共享的 Playwright 实例

    async def fetch_rendered_html(self, url: str) -> str | None:
        """用 Playwright 获取渲染后的 HTML"""
        from playwright.async_api import async_playwright
        try:
            if BasePlaywrightParser.playwright is None:
                BasePlaywrightParser.playwright = await async_playwright().start()
            browser = await BasePlaywrightParser.playwright.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-setuid-sandbox"],
            )
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
            )
            page = await context.new_page()
            await page.goto(url, wait_until="load", timeout=30000)
            await page.wait_for_timeout(5000)  # 等 JS 渲染完成
            html = await page.content()
            await browser.close()
            return html
        except Exception:
            return None

    @classmethod
    async def shutdown(cls):
        if cls.playwright:
            await cls.playwright.stop()
            cls.playwright = None