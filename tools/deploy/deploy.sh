#!/bin/bash
# 部署 codingplan-site 到腾讯云 EdgeOne Makers
#
# 用法:
#   bash tools/deploy/deploy.sh            # 部署到生产
#   bash tools/deploy/deploy.sh preview    # 部署到预览环境
#
# 前置: edgeone login（或 export EDGEONE_PAGES_API_TOKEN=...）
# 链路: build.py → project/codingplan-site/index.html → edgeone makers deploy
#
# 跨平台: 自动适配 Win (Git Bash) / macOS / Linux。
#   - edgeone: 优先用 PATH 中的命令；找不到则 fallback 到 npm 全局目录推导
#   - python:  优先 python3（Unix），fallback 到 python（Win）

set -euo pipefail
cd "$(dirname "$0")/../.."

ENV="${1:-production}"
SITE_DIR="project/codingplan-site"
PROJECT_NAME="${EDGEONE_PROJECT_NAME:-codingplan}"

# ── 解析 edgeone CLI 路径（跨平台）──────────────────────────
resolve_edgeone() {
  # 1) PATH 里直接能调（最常见：npm 全局目录通常在 PATH）
  if command -v edgeone >/dev/null 2>&1; then
    echo "edgeone"
    return
  fi
  # 2) Win: npm 全局目录下 edgeone.cmd / edgeone
  local npm_global; npm_global="$(npm prefix -g 2>/dev/null)"
  if [ -n "$npm_global" ]; then
    for cand in "$npm_global/edgeone.cmd" "$npm_global/edgeone" "$npm_global/bin/edgeone"; do
      if [ -f "$cand" ]; then echo "$cand"; return; fi
    done
  fi
  echo ""
}

EDGEONE_BIN="$(resolve_edgeone)"
if [ -z "$EDGEONE_BIN" ]; then
  echo "❌ 未找到 edgeone CLI。请先 npm install -g edgeone"
  exit 1
fi
# Win 下若解析到 .cmd，需经 cmd 调用；否则直接执行
if [[ "$EDGEONE_BIN" == *.cmd ]]; then
  EDGEONE_CMD=(cmd //c "$EDGEONE_BIN")
else
  EDGEONE_CMD=("$EDGEONE_BIN")
fi

# ── 解析 python（Unix 用 python3，Win 用 python）────────────
resolve_python() {
  if command -v python3 >/dev/null 2>&1; then echo "python3"; return; fi
  if command -v python  >/dev/null 2>&1; then echo "python";  return; fi
  echo ""
}
PYTHON_BIN="$(resolve_python)"
if [ -z "$PYTHON_BIN" ]; then
  echo "❌ 未找到 python。请先安装 Python 3"
  exit 1
fi

echo "==> 1/3 构建最新页面"
"$PYTHON_BIN" tools/builder/build.py --project codingplan-saver

echo "==> 2/3 同步到部署目录 $SITE_DIR/"
cp dist/codingplan-saver.html "$SITE_DIR/index.html"

echo "==> 3/3 部署到 EdgeOne Makers ($ENV)"
"${EDGEONE_CMD[@]}" makers deploy "$SITE_DIR" -n "$PROJECT_NAME" -e "$ENV"

echo "✓ 部署完成"
