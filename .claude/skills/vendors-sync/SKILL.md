---
name: vendors-sync
description: 厂商/工具源头信息校验 — 检查 URL 可达性、提取策略有效性、推广链接状态
metadata:
  type: skill
---

# /vendors-sync — 厂商/工具源头信息校验

## 触发

- `/vendors-sync` — 全量校验：检查 URL 可达性 + 提取策略有效性 → 出报告 → 用户确认后更新
- `/vendors-sync scan` — 快速扫描：只出报告，不动文件

## 定位

`project/codingplan-saver/vendors-and-tools.md` 是**输入源头一览表**（由 `kb_to_md.py` 从 `data/*.json` 自动生成），只记录 URL、提取策略、推广链接。本 skill 校验这些输入是否仍然有效，不涉及爬取结果（价格/套餐/模型在 `plans.json` 中）。

## 核心原则

- **只校验输入**（URL 可达性、提取策略是否还适用、推广链接是否有效）
- **不更新爬取结果**（价格/套餐/模型变化 → `/codingplan-page update` 处理）
- **先出报告，Frank 确认后再改**，绝不自动覆盖

---

## sync 模式工作流

### Step 1: 读取源头文档

读 `project/codingplan-saver/vendors-and-tools.md`（或直接读 `data/vendors.json`），提取所有厂商的 URL。

### Step 2: 逐家校验

对每家厂商，检查：

| 校验项 | 方法 | 判断 |
|--------|------|------|
| 定价页 URL 可达 | WebFetch | 返回 200 → ✅；404/重定向 → ⚠️ URL 可能变了 |
| 提取策略是否仍适用 | 对 auto 厂商，跑 pipeline 看是否成功 | 提取到数据 → ✅；失败 → ⚠️ 页面结构可能变了 |
| 推广链接是否有效 | WebFetch 链接 | 正常跳转 → ✅；失效 → ⚠️ |

对每款工具，检查：

| 校验项 | 方法 | 判断 |
|--------|------|------|
| 官网 URL 可达 | WebFetch | 返回 200 → ✅；否则 → ⚠️ |
| 形态 ❓ 是否可确认 | WebFetch 官网 | 能找到明确信息 → 建议更新 |

### Step 3: 跑 pipeline（仅 auto 厂商）

```bash
cd tools/collector && uv run python -m collector.pipeline
```

检查 7 家 auto 厂商的提取是否成功。

### Step 4: 输出报告

```
# 厂商源头校验 — 2026-07-23

## 定价页 URL
✅ 全部可达 (11/11)

## 提取策略
✅ 7 家 auto 提取成功: 智谱AI, DeepSeek, Kimi, MiniMax, 腾讯云, Claude, GitHub
⚠️ 1 家需关注: 字节·方舟 — manual，建议重新尝试 Playwright

## 推广链接
⚠️ 6 家待添加: 字节·方舟, 阿里·百炼, 腾讯云, Claude, GitHub, Codex

## 工具官网
✅ 全部可达 (6/6 海外)
⚠️ 5 款形态待确认: Kimi Code, CodeBuddy, MiniMax Code, MiMo Code, ZCode, Qoder
```

### Step 5: Frank 确认后更新

只更新以下字段：
- 提取策略（manual → Playwright 等）
- 推广链接（待添加 → 具体链接）
- 备注（补充说明）
- 形态 ❓ → 确认后的类型

**不更新**：定价、套餐、模型（这些在 plans.json 中，通过 `/codingplan-page` 更新）。

---

## scan 模式

`/vendors-sync scan` — 只出报告，不提示写入。

---

## 边界规则

- URL 返回非 200 → 标记 ⚠️，不改 URL（URL 变更需 Frank 确认）
- 提取策略失效 → 标记 ⚠️，建议排查方向，不改策略
- 推广链接大面积"待添加" → 提醒 Frank 补充，但这是正常状态
- 所有变更需 Frank 确认后写入 `project/codingplan-saver/data/vendors.json`，再跑 `kb_to_md` 刷新一览表