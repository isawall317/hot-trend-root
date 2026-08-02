"""
HTML 构建器 — 读模板片段 + 套 JSON 数据 → 输出单文件 HTML

用法:
  python3 tools/builder/build.py [--project PROJECT_NAME]
  python3 tools/builder/build.py --project codingplan-saver
  python3 tools/builder/build.py --project ccskills-market

默认 --project 为 codingplan-saver（兼容旧调用）

输出:
  dist/{project}-{timestamp}.html  （带时间戳）
  dist/{project}.html              （latest 副本）

模板拆分结构:
  project/{project}/
  ├── template/
  │   ├── base.html          ← HTML 骨架（{{STYLE}} / {{SCRIPTS}} / {{DATA}} 占位）
  │   ├── style.css          ← 所有 CSS
  │   └── scripts/
  │       ├── utils.js       ← 工具函数
  │       ├── router.js      ← Tab 路由
  │       ├── recommend.js   ← 推荐 Tab
  │       ├── compare.js     ← 对比/浏览 Tab + ECharts
  │       ├── community.js   ← 社群 Tab + Footer
  │       └── init.js        ← DOMContentLoaded 初始化
  └── data/
      ├── site.json          ← 站点配置
      ├── ...                ← 项目特定数据文件
"""
import argparse
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent

# 脚本加载顺序（init.js 必须最后）
SCRIPT_FILES = ["utils.js", "router.js", "recommend.js", "compare.js", "community.js", "calculator.js", "init.js"]


def load_json(data_dir: Path, name: str):
    """加载 JSON 数据文件，不存在返回空"""
    p = data_dir / name
    if not p.exists():
        return {} if name == "site.json" else []
    return json.loads(p.read_text(encoding="utf-8"))


def load_all_data(data_dir: Path) -> dict:
    """加载 data/ 目录下所有 JSON 文件，加上 generatedAt"""
    data = {"generatedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    if data_dir.exists():
        for f in sorted(data_dir.glob("*.json")):
            key = f.stem  # site.json → site, skills.json → skills
            data[key] = json.loads(f.read_text(encoding="utf-8"))
    return data


def assemble(project_dir: Path) -> str:
    """组装 HTML：读片段 + 注入数据"""
    template_dir = project_dir / "template"
    data_dir = project_dir / "data"
    base = (template_dir / "base.html").read_text(encoding="utf-8")
    style = (template_dir / "style.css").read_text(encoding="utf-8")

    # 拼接所有脚本
    scripts_parts = []
    for fname in SCRIPT_FILES:
        script_path = template_dir / "scripts" / fname
        if script_path.exists():
            scripts_parts.append(script_path.read_text(encoding="utf-8"))
        else:
            print(f"⚠️  脚本缺失: {fname}")
    scripts = "\n\n".join(scripts_parts)

    # 替换占位符
    html = base.replace("{{STYLE}}", style)
    html = html.replace("{{SCRIPTS}}", scripts)

    # 注入所有数据
    data = load_all_data(data_dir)
    data_json = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    html = html.replace("{{DATA}}", data_json)

    return html


def main():
    parser = argparse.ArgumentParser(description="Build single-file HTML from template + data")
    parser.add_argument("--project", default="codingplan-saver",
                        help="Project name under project/ directory (default: codingplan-saver)")
    args = parser.parse_args()

    project_name = args.project
    project_dir = ROOT / "project" / project_name
    template_dir = project_dir / "template"
    data_dir = project_dir / "data"

    if not template_dir.exists():
        raise SystemExit(f"❌ 项目模板不存在: {template_dir}")
    if not data_dir.exists():
        raise SystemExit(f"❌ 项目数据不存在: {data_dir}")

    # 加载数据摘要
    data = load_all_data(data_dir)
    data_keys = [k for k in data.keys() if k != "generatedAt"]
    counts = ", ".join(f"{k}: {len(data[k])}" for k in sorted(data_keys) if isinstance(data[k], list))
    if counts:
        print(f"📦 数据: {counts}")

    html = assemble(project_dir)

    build_time = datetime.now()
    timestamp = build_time.strftime("%Y-%m-%d-%H%M")
    dist_dir = ROOT / "dist"
    dist_dir.mkdir(parents=True, exist_ok=True)

    dist_timestamped = dist_dir / f"{project_name}-{timestamp}.html"
    dist_latest = dist_dir / f"{project_name}.html"

    dist_timestamped.write_text(html, encoding="utf-8")
    dist_latest.write_text(html, encoding="utf-8")

    size_kb = len(html.encode("utf-8")) / 1024
    print(f"✅ 生成: {dist_timestamped}")
    print(f"   副本: {dist_latest}")
    print(f"   大小: {size_kb:.1f} KB")
    print(f"   模板: {len(SCRIPT_FILES)} 个脚本片段 + style.css + base.html")
    print(f"   打开: open {dist_latest}")


if __name__ == "__main__":
    main()