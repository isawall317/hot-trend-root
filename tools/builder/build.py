"""
HTML 构建器 — 读模板片段 + 套 JSON 数据 → 输出单文件 HTML

用法: python3 tools/builder/build.py
输出: dist/codingplan-saver.html

模板拆分结构:
  template/
  ├── base.html          ← HTML 骨架（{{STYLE}} / {{SCRIPTS}} / {{DATA}} 占位）
  ├── style.css          ← 所有 CSS
  └── scripts/
      ├── utils.js       ← 工具函数（escapeHtml, formatPrice 等）
      ├── router.js      ← Tab 路由
      ├── recommend.js   ← 推荐 Tab
      ├── compare.js     ← 对比 Tab + ECharts 散点图
      ├── community.js   ← 社群 Tab + Footer
      └── init.js        ← DOMContentLoaded 初始化
"""
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
TEMPLATE_DIR = ROOT / "project" / "codingplan-saver" / "template"
DATA_DIR = ROOT / "project" / "codingplan-saver" / "data"

# 带时间戳的文件名，同时保留 latest 副本
BUILD_TIME = datetime.now()
TIMESTAMP = BUILD_TIME.strftime("%Y-%m-%d-%H%M")
DIST_TIMESTAMPED = ROOT / "dist" / f"codingplan-saver-{TIMESTAMP}.html"
DIST_LATEST = ROOT / "dist" / "codingplan-saver.html"

# 脚本加载顺序（init.js 必须最后）
SCRIPT_FILES = ["utils.js", "router.js", "recommend.js", "compare.js", "community.js", "init.js"]


def load_json(name: str):
    """加载 JSON 数据文件，不存在返回空"""
    p = DATA_DIR / name
    if not p.exists():
        return {} if name == "site.json" else []
    return json.loads(p.read_text(encoding="utf-8"))


def assemble() -> str:
    """组装 HTML：读片段 + 注入数据"""
    base = (TEMPLATE_DIR / "base.html").read_text(encoding="utf-8")
    style = (TEMPLATE_DIR / "style.css").read_text(encoding="utf-8")

    # 拼接所有脚本
    scripts_parts = []
    for fname in SCRIPT_FILES:
        script_path = TEMPLATE_DIR / "scripts" / fname
        if script_path.exists():
            scripts_parts.append(script_path.read_text(encoding="utf-8"))
        else:
            print(f"⚠️  脚本缺失: {fname}")
    scripts = "\n\n".join(scripts_parts)

    # 替换占位符
    html = base.replace("{{STYLE}}", style)
    html = html.replace("{{SCRIPTS}}", scripts)

    # 注入数据
    data = {
        "site": load_json("site.json"),
        "vendors": load_json("vendors.json"),
        "plans": load_json("plans.json"),
        "changes": load_json("changes.json"),
        "generatedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    data_json = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    html = html.replace("{{DATA}}", data_json)

    return html


def main():
    if not (TEMPLATE_DIR / "base.html").exists():
        raise SystemExit(f"❌ 模板不存在: {TEMPLATE_DIR / 'base.html'}")

    data = {
        "site": load_json("site.json"),
        "vendors": load_json("vendors.json"),
        "plans": load_json("plans.json"),
        "changes": load_json("changes.json"),
    }
    print(f"📦 数据: {len(data['plans'])} plans / {len(data['changes'])} changes / {len(data['vendors'])} vendors")

    html = assemble()

    DIST_TIMESTAMPED.parent.mkdir(parents=True, exist_ok=True)
    DIST_TIMESTAMPED.write_text(html, encoding="utf-8")
    # 同时保存一份 latest 副本，方便直接打开
    DIST_LATEST.write_text(html, encoding="utf-8")

    size_kb = len(html.encode("utf-8")) / 1024
    print(f"✅ 生成: {DIST_TIMESTAMPED}")
    print(f"   副本: {DIST_LATEST}")
    print(f"   大小: {size_kb:.1f} KB")
    print(f"   模板: {len(SCRIPT_FILES)} 个脚本片段 + style.css + base.html")
    print(f"   打开: open {DIST_LATEST}")


if __name__ == "__main__":
    main()