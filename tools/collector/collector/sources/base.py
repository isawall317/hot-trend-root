"""base shim — 再导出 qsources.plugins.base 的类。

8 个厂商解析器 + runner.py + sources/__init__.py 的 `from .base import`
不变，全部命中本 shim。源插件框架的真实实现已迁到 qsources.plugins。
"""

from __future__ import annotations

from qsources.plugins.base import (  # noqa: F401
    BaseParser,
    BasePlaywrightParser,
    ExtractResult,
)

__all__ = ["BaseParser", "BasePlaywrightParser", "ExtractResult"]
