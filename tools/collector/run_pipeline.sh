#!/bin/bash
# Hot Trend 采集管道 — launchd 定时入口
# launchd 环境 PATH 极简，必须显式声明（uv/npx 在 ~/.local/bin）
#
# 安装定时任务（新机器恢复时）：
#   cp com.hottrend.collector.plist ~/Library/LaunchAgents/
#   launchctl load ~/Library/LaunchAgents/com.hottrend.collector.plist
#   launchctl kickstart gui/$(id -u)/com.hottrend.collector   # 立即试跑一次
# 卸载：launchctl unload ~/Library/LaunchAgents/com.hottrend.collector.plist
set -u

export PATH="/Users/doumoman/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"

echo "===== $(date '+%Y-%m-%d %H:%M:%S') pipeline start ====="

cd /Users/doumoman/Gits/hot-trend-root/tools/collector
uv run python -m collector.pipeline
rc=$?

echo "===== $(date '+%Y-%m-%d %H:%M:%S') pipeline exit=$rc ====="
exit $rc
