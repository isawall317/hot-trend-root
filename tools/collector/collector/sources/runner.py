"""sources 调度器：读 vendors.json，并行跑所有 parser"""

import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path

import httpx

from . import get_parser, load_all
from .base import BaseParser, ExtractResult

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
VENDORS_PATH = PROJECT_ROOT / "project" / "codingplan-saver" / "data" / "vendors.json"
SIGNALS_DIR = PROJECT_ROOT / "data" / "signals"


async def run_all() -> list[ExtractResult]:
    """并行跑所有注册的 parser，返回结果列表"""
    load_all()
    vendors = json.loads(VENDORS_PATH.read_text(encoding="utf-8"))

    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        tasks = []
        for v in vendors:
            if v.get("extractStrategy") == "manual":
                continue
            parser_cls = get_parser(v["id"])
            if not parser_cls:
                continue
            tasks.append(_safe_extract(parser_cls(v), client))
        results = await asyncio.gather(*tasks)

    return [r for r in results if r]


async def _safe_extract(parser: BaseParser, client) -> ExtractResult | None:
    try:
        # Playwright 解析器不需要 client
        if hasattr(parser, "fetch_rendered_html"):
            result = await parser.extract(None)
        else:
            result = await parser.extract(client)
        result.fetched_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        print(f"  ✅ {parser.vendor_name}: {len(result.plans)} plans, fields={result.extracted_fields}")
        return result
    except Exception as e:
        print(f"  ❌ {parser.vendor_name}: {e}")
        return ExtractResult(
            vendor_id=parser.vendor_id,
            vendor_name=parser.vendor_name,
            error=str(e)[:200],
            fetched_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        )


def save_results(results: list[ExtractResult], date_str: str) -> str:
    """保存到 data/signals/extract-{date}.json"""
    SIGNALS_DIR.mkdir(parents=True, exist_ok=True)
    out = SIGNALS_DIR / f"extract-{date_str}.json"
    data = [
        {
            "vendorId": r.vendor_id,
            "vendor": r.vendor_name,
            "plans": r.plans,
            "extractedFields": r.extracted_fields,
            "missingFields": r.missing_fields,
            "sourceUrl": r.source_url,
            "fetchedAt": r.fetched_at,
            "error": r.error,
        }
        for r in results
    ]
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ {out}")
    return str(out)


async def main():
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    print(f"🌐 sources 提取 — {date_str}")
    results = await run_all()
    save_results(results, date_str)


if __name__ == "__main__":
    asyncio.run(main())