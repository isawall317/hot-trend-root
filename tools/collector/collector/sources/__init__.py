"""sources 模块：按厂商提取定价数据

注册表 _VENDOR_PARSERS: vendor_id → Parser 类
未注册的 vendor_id 跳过（走 manual 策略）
"""

from .base import BaseParser, ExtractResult  # noqa: F401

_VENDOR_PARSERS: dict[str, type[BaseParser]] = {}


def register(vendor_id: str):
    """装饰器：注册 parser 类到 vendor_id"""
    def deco(cls):
        _VENDOR_PARSERS[vendor_id] = cls
        return cls
    return deco


def get_parser(vendor_id: str) -> type[BaseParser] | None:
    """获取已注册的 parser 类"""
    return _VENDOR_PARSERS.get(vendor_id)


def load_all():
    """触发所有 parser 模块导入（填充注册表）"""
    from . import deepseek, zhipu, bytedance, kimi, minimax  # noqa: F401