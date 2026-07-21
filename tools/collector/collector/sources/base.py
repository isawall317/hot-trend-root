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