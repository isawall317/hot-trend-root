---
name: kb-update
description: 知识库更新 — 采集 → 变更检测 → 审阅 → 合并，维护 project/codingplan-saver/data/ 数据
metadata:
  type: skill
---

# /kb-update — 厂商数据更新

## 触发

- `/kb-update` — 全量更新：跑 pipeline → 审阅 → 合并
- `/kb-update scan` — 快速扫描：只读 kb-changes.json + market signals，出报告，不动文件
- `/kb-update review` — 审阅模式：读取上次 pipeline 产生的 kb-changes.json，逐条确认
- `/kb-update build` — 重新生成一览表：跑 `kb_to_md.py`，刷新 `project/codingplan-saver/vendors-and-tools.md`

## 定位

`project/codingplan-saver/data/` 是**唯一真相源**：厂商/套餐/变动数据只在此目录维护。
pipeline 每次跑完更新 plans.json，`kb_to_md.py` 从 data 直接生成一览表。不存在 aikb 中间镜像层。

## 核心原则

- **`project/codingplan-saver/data/` 是唯一真相源**，`vendors-and-tools.md` 由 `kb_to_md.py` 从 data 直接生成
- **自动采集 + 人工审阅**，不是全自动
- **低风险变更自动合**（新模型、小价差），**高风险人工确认**（涨价、下架、新服务）
- **先检测后审阅**，绝不盲目覆盖

---

## 工作流

### 模式 1: `update` — 全量更新

#### Step 1: 跑 pipeline

```bash
cd tools/collector && uv run python -m collector.pipeline
```

pipeline 自动完成：
- 热点采集 → 文章发现 → 价格监控 → 厂商定价提取 → Token 推算
- **市场发现**（热点召回）→ `data/signals/market-{date}.json`
- **KB 变更检测**（kb_diff）→ `data/pending/{date}/kb-changes.json`

#### Step 2: 审阅 KB 变更

读取 `data/pending/{date}/kb-changes.json`，按风险分级处理：

| 风险 | 触发条件 | 处理方式 |
|:--:|------|------|
| 🔴 high | 价格变动>10%、服务下架、新服务上线、category 变更 | 逐条展示给 Frank 确认 |
| 🟡 medium | URL 变更、新模型、新工具、massServices 增减 | 逐条展示，可批量确认 |
| 🟢 low | 备注更新、logo/color、lastVerified | 自动合并 |

#### Step 3: 审阅市场发现

读取 `data/signals/market-{date}.json`：
- 🟢 高置信度 → 建议 Frank 确认后加入数据
- 🟡 中置信度 → 标记，等更多证据
- 🔴 低置信度 → 可选跳过

#### Step 4: 确认后写回

高风险变更使用 Edit 工具逐条改 `project/codingplan-saver/data/*.json`（AI 草拟 + Frank 确认），展示 diff 预览格式：
```
+ 新增 / ~ 修改 / - 移除
```

低风险变更批量自动 patch。

#### Step 5: 重新生成一览表

```bash
cd tools/collector && uv run python -m collector.kb_to_md
```

---

### 模式 2: `scan` — 快速扫描

只读 `data/pending/{date}/kb-changes.json` + `data/signals/market-{date}.json`，出报告，不改任何文件。

适合每天快速看一眼"有没有新东西"。

---

### 模式 3: `review` — 审阅模式

读取上次 pipeline 产生的 `kb-changes.json`，执行 update 模式的 Step 2-5。

适用场景：pipeline 跑完后，单独找时间审阅。

---

### 模式 4: `build` — 重新生成一览表

```bash
cd tools/collector && uv run python -m collector.kb_to_md
```

适用场景：手动修改了 data/*.json 后，刷新一览表。

---

## 与现有 Skill 的关系

| 场景 | 用哪个 |
|------|--------|
| 发现新厂商/新工具 | `/kb-update`（pipeline 自动发现 + 人工确认） |
| 校验 URL 和提取策略 | `/vendors-sync`（专注源头校验） |
| 更新 CodingPlan 价格/套餐 | `/codingplan-page update`（专注价格层） |
| 从 data 重新生成一览表 | `/kb-update build` |

---

## 边界规则

- `project/codingplan-saver/data/*.json` 是唯一真相源，通过 kb-update skill 或手动 Edit 修改
- `project/codingplan-saver/vendors-and-tools.md` 由 `kb_to_md.py` 生成，不手动编辑
- 新增厂商：先在 `vendors.json` 登记 → 在 `plans.json` 加套餐 → 跑 `kb_to_md` 刷新一览表
