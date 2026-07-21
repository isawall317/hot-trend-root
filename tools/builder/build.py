"""
HTML 构建器 — 读 JSON + 套模板 → 输出单文件 HTML

用法: python3 tools/builder/build.py
输出: dist/codingplan-saver.html
"""
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = ROOT / "project" / "codingplan-saver" / "data"
TEMPLATE = ROOT / "project" / "codingplan-saver" / "template" / "index.html"
DIST = ROOT / "dist" / "codingplan-saver.html"


def load_json(name: str):
    """加载 JSON 数据文件，不存在返回空"""
    p = DATA_DIR / name
    if not p.exists():
        return {} if name == "site.json" else []
    return json.loads(p.read_text(encoding="utf-8"))


def main():
    if not TEMPLATE.exists():
        raise SystemExit(f"❌ 模板不存在: {TEMPLATE}")

    data = {
        "site": load_json("site.json"),
        "vendors": load_json("vendors.json"),
        "plans": load_json("plans.json"),
        "changes": load_json("changes.json"),
        "generatedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    print(f"📦 数据: {len(data['plans'])} plans / {len(data['changes'])} changes / {len(data['vendors'])} vendors")

    tpl = TEMPLATE.read_text(encoding="utf-8")
    # 替换占位符（</script> 在 JSON 里会破坏 HTML 解析，需转义）
    data_json = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    html = tpl.replace("{{DATA}}", data_json)

    DIST.parent.mkdir(parents=True, exist_ok=True)
    DIST.write_text(html, encoding="utf-8")

    size_kb = len(html.encode("utf-8")) / 1024
    print(f"✅ 生成: {DIST}")
    print(f"   大小: {size_kb:.1f} KB")
    print(f"   打开: open {DIST}")


if __name__ == "__main__":
    main()