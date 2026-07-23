# /vendors-sync 技能设计

## 定位

自动维护 `docs/vendors-and-tools.md` 的厂商/工具信息，确保与各家最新公开页面一致。

**不是 Python 脚本，是 Claude Code 技能** — Python collector 负责结构化提取（JSON），本 skill 负责"读 JSON + 读网页 → 对比差异 → 更新 markdown"。

## 两个模式

### `/vendors-sync` — 全量同步
采集 → 对比 → 出 diff → 用户确认 → 写入

### `/vendors-sync scan` — 快速扫描
采集 → 对比 → 出报告（只读，不动文件）

## 执行流程

### Step 1: 采集最新数据

```bash
cd tools/collector && uv run python -m collector.pipeline
```

产出：plans.json（7 家 auto 厂商最新定价）、signals/（价格变动信号）

### Step 2: 读取三份数据源

- `plans.json` — 结构化定价数据（31 条套餐）
- `vendors.json` — 厂商元信息（URL、提取策略）
- `docs/vendors-and-tools.md` — 当前文档状态

### Step 3: 逐家对比（模型厂商 11 家）

对每家厂商，对比 `plans.json` ↔ `vendors-and-tools.md` 的**套餐列**：

| 对比项 | 数据来源 | 判断逻辑 |
|--------|---------|---------|
| 套餐价格 | plans.json monthlyPrice | 价格变了 → 更新 |
| 套餐名称 | plans.json plan | 新增/删除套餐 → 标记 |
| 套餐状态 | plans.json status | active→paused 等 → 标记 |
| 支持模型 | plans.json models | 新增模型 → 标记 |
| 最后验证 | 当天日期 | 全部更新 |

**7 家 auto 厂商**：plans.json 有数据，直接对比。
**4 家 manual 厂商**：plans.json 可能过期，用 WebFetch 抓定价页补充。

### Step 4: 补充工具信息（18 款）

对 `vendors-and-tools.md` 第二节列出的 18 款工具：

- 用 WebFetch 抓各工具官网
- 对比：定价变了？新功能？状态变了？
- 只更新**可验证的硬信息**（价格、模型、功能列表），不改评分/判断

### Step 5: 输出 diff

```
厂商变更预览：
  [智谱AI] 套餐价格：Lite ¥49→¥49 ✓ 不变
  [智谱AI] 模型新增：+GLM-5.3 (来源: plans.json)
  [Kimi] 套餐状态：Allegretto paused→active (来源: plans.json)
  [字节·方舟] 需人工确认：WebFetch 被拦截，请手动检查
  [Claude Code] 功能新增：+Gemini 3.1 模型支持 (来源: WebFetch)

工具变更预览：
  [Cursor] 定价：$20→$30 (来源: WebFetch)
  [GitHub Copilot] 状态：Pro+ 新增 GPT-5.6 模型 (来源: WebFetch)

确认应用？(y/n/逐条确认)
```

### Step 6: 用户确认后写入

- 更新 `docs/vendors-and-tools.md` 对应表格
- 更新 `最后更新` 日期
- 更新各家 `最后验证` 日期
- 更新第八节 `变更记录`

## 边界规则

### 不改的内容
- 厂商/工具列表（增删由 Frank 决定）
- 定价页 URL（稳定不变）
- 推广链接（Frank 的商业关系）
- 评分/推荐语（Frank 的主观判断）
- `待确认` 标记（除非有明确证据）

### 需要标记的内容
- 网页抓取失败 → 标记为"需人工确认"，不改数据
- 价格与 plans.json 差异过大（>50%）→ 标记为"疑似异常，请确认"
- 提取策略失效（网页结构变了）→ 标记为"提取策略可能需更新"

### 降级处理
- pipeline 跑失败 → 跳过 auto 对比，只做 WebFetch 部分，标注"auto 数据未更新"
- WebFetch 大面积失败 → 只做 plans.json 对比，标注"WebFetch 不可用"
- 全部失败 → 输出"本次无法同步，建议手动检查"

## 文件位置

```
.claude/skills/vendors-sync/SKILL.md
```

## 与现有 skill 的关系

| 技能 | 职责 |
|------|------|
| `/codingplan-page` | 更新 codingplan-saver 的 JSON 数据 + 生成 HTML |
| `/vendors-sync` | 更新 docs/vendors-and-tools.md 的 markdown 文档 |
| `collector.pipeline` | 自动提取 7 家厂商定价 → plans.json |

不重叠：codingplan-page 操作 JSON，vendors-sync 操作 markdown。pipeline 是两者的共同上游。