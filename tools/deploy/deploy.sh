#!/bin/bash
# 部署 codingplan-site 到腾讯云 EdgeOne Makers
#
# 用法:
#   bash tools/deploy/deploy.sh            # 部署到生产
#   bash tools/deploy/deploy.sh preview    # 部署到预览环境
#
# 前置: edgeone login（或 export EDGEONE_PAGES_API_TOKEN=...）
# 链路: build.py → project/codingplan-site/index.html → edgeone makers deploy

set -euo pipefail
cd "$(dirname "$0")/../.."

ENV="${1:-production}"
SITE_DIR="project/codingplan-site"
PROJECT_NAME="${EDGEONE_PROJECT_NAME:-codingplan}"
EDGEONE_BIN="$(npm prefix -g)/bin/edgeone"

echo "==> 1/3 构建最新页面"
python3 tools/builder/build.py --project codingplan-saver

echo "==> 2/3 同步到部署目录 $SITE_DIR/"
cp dist/codingplan-saver.html "$SITE_DIR/index.html"

echo "==> 3/3 部署到 EdgeOne Makers ($ENV)"
"$EDGEONE_BIN" makers deploy "$SITE_DIR" -n "$PROJECT_NAME" -e "$ENV"

echo "✓ 部署完成"
