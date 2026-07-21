# /build-site — CodingPlan 省钱攻略 数据更新 + HTML 生成

## 触发

- `/build-site` 或 `/build-site build` — 读数据生成 HTML（最快，M1 可用）
- `/build-site update [自然语言]` — 更新数据（M2 实现后补全）
- `/build-site scan` — 扫描信号（M2 实现后补全）

---

## build 模式工作流

### 何时用

- 数据已更新（手动改了 JSON），想重新生成 HTML
- 模板有改动，想验证新输出

### 步骤

1. 读 `project/codingplan-saver/data/` 下 4 个 JSON
2. 运行 `python3 tools/builder/build.py`
3. 输出到 `dist/codingplan-saver.html`
4. 报告文件大小，提示 `open` 命令

### 数据校验

构建前 AI 应对照 `project/codingplan-saver/data/SCHEMA.md` 快速检查：
- `plans.json` 每条有 `id` / `vendor` / `vendorId` / `plan` / `monthlyPrice`
- `changes.json` 每条有 `id` / `date` / `kind` / `vendor` / `title`
- 缺失字段 → 用默认值（如 `status` 默认 `active`），不阻塞构建

---

## 数据 Schema 宪法

见 `project/codingplan-saver/data/SCHEMA.md`（完整字段定义 + 枚举 + 迁移规则）。

### 文件一览

| 文件 | 职责 | 更新方式 |
|------|------|---------|
| `data/site.json` | 站点配置（博主、推荐分组、社群） | 手动 |
| `data/vendors.json` | 厂商元信息（URL、提取策略） | 半自动 |
| `data/plans.json` | 套餐主数据（31 条） | 半自动 |
| `data/changes.json` | 变动时间线（40 条） | 半自动 |
| `data/history/` | plans.json 快照 | 自动 |

### 联盟变现

所有套餐链接（`plans[].action`）指向各厂商的注册/购买页。HTML 模板中所有 CTA 按钮统一为"优惠购买"，`rel="nofollow sponsored"`（SEO 合规）。Footer 保留联盟推广披露。

---

## HTML 模板

见 `project/codingplan-saver/template/index.html`（标准件）。

### 页面结构

- **3 Tab**: 推荐 / 对比 / 社群（hash 路由 `#recommend` / `#compare` / `#community`）
- **推荐页**: Hero → Top 3 Picks → 场景卡片 → 博主推荐 → 最近变动（30 天）
- **对比页**: 散点图（ECharts CDN）→ 筛选条 → 完整表格 → 移动端卡片
- **社群页**: 免费群 + 知识星球双卡
- **变现触点**: Top 3 卡片 / 推荐卡片 / 对比表格 / 移动端卡片 → 全部"优惠购买"按钮

### 数据嵌入

```html
<script id="cp-data" type="application/json">
{site, vendors, plans, changes, generatedAt}
</script>
```

---

## 文件结构

```
hot-trend-root/
├── .claude/skills/build-site.md        ← 本文件
├── project/codingplan-saver/
│   ├── data/                           ← 数据源
│   │   ├── SCHEMA.md                   ← 宪法
│   │   ├── site.json / vendors.json
│   │   ├── plans.json / changes.json
│   │   └── history/
│   ├── template/index.html             ← HTML 标准件
│   └── archive/                        ← V1 归档
├── tools/
│   ├── builder/build.py                ← 构建脚本
│   └── collector/                      ← 数据采集管道
├── dist/
│   └── codingplan-saver.html           ← 最终交付物
└── reference/
    ├── pricing-urls.md                 ← 供应商 URL 维护
    └── data-map.md                     ← 数据地图
```

---

## update 模式工作流

### 触发

`/build-site update [自然语言]`

### 步骤

**Step 1: 并行采集信号（dispatch 3 个 sub-agent）**

用 Agent 工具同时发起 3 个并行任务：

```
Agent-Scan:  python -m collector.price_monitor
             → 读 data/signals/{date}.json

Agent-RSS:   httpx 拉 RSSHub feeds (http://localhost:1200):
             /deepseek/news /qwen/blog /qbitai/category/AI /aibase/news
             → 提取标题含关键词的条目

Agent-Httpx: python -m collector.sources.runner
             → 读 data/signals/extract-{date}.json
```

**Step 2: 合并信号**

主 agent 把三路结果合并：
- 自动信号（Step 1） ∪ 解析用户的自然语言输入
- 去重（同一 vendor + 同一 kind 视为同一条）
- 分类：哪些需要改 `plans.json`，哪些只需加 `changes.json`

**Step 3: 按 schema 草拟变更**

对照 `project/codingplan-saver/data/SCHEMA.md`，生成 unified diff：
- `changes.json` 新增条目（kind / date / vendor / title / detail / impact / level）
- `plans.json` 字段修改（如 monthlyPrice / status / models）

**Step 4: 输出 diff，请用户确认**

```
变更预览：
[changes.json] +3 条
  + 2026-07-21-kimi-resume | subscription_pause | Kimi 恢复订阅 | positive
  + ...

[plans.json] 修改 2 条
  ~ kimi-moderato: status paused → active
  ~ ...

确认应用？(y/n/改某条)
```

**Step 5: 应用变更（用户 y 之后）**

1. 快照当前 plans.json → `data/history/plans-{date}.json`
2. 写入 changes.json 和 plans.json
3. 跑 `python3 -m collector.token_estimator` 补 measuredMonthlyToken
4. 更新所有变动条目的 updatedAt
5. 提示用户「说 /build-site build 生成 HTML」

**Step 6: 不自动 build**，用户确认后手动 `/build-site build`

### 错误处理

- collector 跑失败 → 降级为纯人工（只用用户的自然语言输入）
- diff 输出后用户说"改 X 条" → 单独修改那条，重新输出 diff
- 用户说 n → 不动任何文件

---

## scan 模式工作流

### 触发

`/build-site scan`

### 步骤

1. 并行跑 Layer 1 三路信号采集（同 update 的 Step 1）
2. 合并去重
3. 输出 markdown 报告到终端（**不动任何 JSON 文件**）：

```
本周信号 (共 N 条):
[价格] Kimi 涨价到 ¥99 — 来源: dailyhot:36kr [link]
[模型] 字节方舟新增 Kimi-K3 — 来源: rsshub:deepseek/news [link]
[定价] DeepSeek API 价格已更新 — 来源: extracted-deepseek
```

4. 提示用户「值得跟进的，说 /build-site update ...」

### 错误处理

- 三路信号全部失败 → 输出"本周无信号，建议手动检查各平台定价页"
- 单路失败 → 标注失败原因，继续输出其他路结果

---

## 自然语言解析指引

| 用户说 | kind 映射 | 改哪个文件 |
|--------|----------|-----------|
| "X 涨价/降价到 ¥Y" | `price_change` | plans.json（monthlyPrice）+ changes.json |
| "X 新增支持 M 模型" | `new_model` | plans.json（models）+ changes.json |
| "X 暂停订阅" | `subscription_pause` | plans.json（status=paused）+ changes.json |
| "X 新套餐上线" | `new_plan` | plans.json（新增条目）+ changes.json |
| "X 限时活动，Y 折" | `promotion` | 仅 changes.json |
| "看到一篇文章 [URL]" | `article` | 仅 changes.json（需强相关过滤） |

---

## 错误处理

- 构建时 JSON 缺失字段 → 用默认值，不阻塞
- collector 跑失败 → 降级纯人工模式
- JSON schema 校验失败 → 回滚到 `history/` 快照
- HTML 生成失败 → 保留上次 `dist/`
- 单家厂商提取失败 → 标记 `manual`，不阻塞其他厂商