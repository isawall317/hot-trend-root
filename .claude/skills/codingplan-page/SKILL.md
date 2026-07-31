---
name: codingplan-page
description: CodingPlan 省钱攻略 — 数据更新 + HTML 生成
metadata:
  type: skill
---

# /codingplan-page — CodingPlan 省钱攻略 数据更新 + HTML 生成

## 触发

- `/codingplan-page` 或 `/codingplan-page build` — **全量更新**：采集 → 审阅 → 生成 HTML（每次都是最新数据）
- `/codingplan-page update [自然语言]` — 单独审阅候选文章，更新 changes.json（不采集）
- `/codingplan-page scan` — 扫描信号（只读报告）

---

## build 模式工作流（默认）

### 核心原则

**每次生成 HTML 前，必须拉取最新数据。** 不依赖缓存，不依赖上次运行结果。

### 步骤

**Step 1: 运行数据管道**

```bash
cd tools/collector && uv run python -m collector.pipeline
```

产出：
- `data/raw/{date}/` — 最新热点数据
- `data/pending/{date}/articles.json` — 候选文章
- `data/signals/{date}.json` — 价格信号
- `plans.json` — token_estimator 更新

**Step 2: 审阅候选文章**

读取 `data/pending/{date}/articles.json`，去噪：
- 纯技术教程（无商业价值）→ 跳过
- 泛泛行业新闻 → 跳过
- 与 AI Coding Plan 定价/模型/订阅直接相关 → 收录
- 关键事件（Kimi、Claude、DeepSeek 等）→ 同时生成结构化变动（new_model/price_change/subscription_pause）

**Step 3: 写入 changes.json**

将审阅后的文章和结构化变动写入 `changes.json`。

**Step 4: 更新 site.json**

更新 `updateDate` 和 `highlights` 为当前日期和本周关注点。

**Step 5: 生成 HTML**

```bash
python3 tools/builder/build.py
```

输出到 `dist/codingplan-saver-{YYYY-MM-DD-HHMM}.html` + `dist/codingplan-saver.html`（latest 副本）。

**Step 6: 汇报 + 部署**

告知用户：采集条数、候选文章数、收录数、结构化变动数、文件大小。提示 `open` 命令预览本地产物。

然后**询问用户是否部署上线**（部署是 outward-facing 操作，必须用户确认）：

```bash
# 稳妥流程：先 preview 验证，用户确认后再 production
bash tools/deploy/deploy.sh preview      # 生成带 token 的预览链接，用户打开验证
bash tools/deploy/deploy.sh production    # 用户确认后，推生产（更新默认域名内容）
```

deploy.sh 自动完成 build → cp 到 codingplan-site → edgeone makers deploy 三步（跨平台 Win/Mac/Unix 自适应）。

- **preview 环境**：生成带 `eo_token` 的临时链接，不受默认域名区域限制，专供验证
- **production 环境**：更新 `codingplan-llnvmecs.edgeone.cool` 默认域名内容
- **前置**：`edgeone login` 已完成（或设置 `EDGEONE_PAGES_API_TOKEN` 环境变量）
- **自定义域名**：最终入口 `codingplan.fyi` 需在 EdgeOne 控制台绑定（CNAME 验证），见 [`docs/deployment.md`](../../../docs/deployment.md) 迁移路线 ③

### 数据校验

构建前 AI 应对照 `project/codingplan-saver/data/SCHEMA.md` 快速检查（字段全集以 SCHEMA 为准）：
- `plans.json` 每条含必填字段（id / vendor / vendorId / plan / type / tier / monthlyPrice / measuredMonthlyToken / category / billingCore 等）
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
| `data/plans.json` | 套餐主数据（核心更新对象） | 半自动 |
| `data/changes.json` | 变动时间线 | 半自动 |
| `data/history/` | plans.json 快照 | 自动 |

### 联盟变现

所有套餐链接（`plans[].action`）优先使用 `vendors[].urls.affiliate`（联盟推广链接），为空时 fallback 到 `vendors[].urls.pricing`（定价页）。HTML 模板中所有 CTA 按钮统一为"优惠购买"，`rel="nofollow sponsored"`（SEO 合规）。Footer 保留联盟推广披露。

> **厂商参考手册**：`docs/vendors-and-tools.md` — 统一管理定价页 URL（数据采集用）+ 联盟推广链接（"优惠购买"按钮用）+ 返佣信息。新增联盟链接时先在手册登记，再更新 `vendors.json` 和 `plans.json`。

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
├── .claude/skills/codingplan-page/      ← 本文件
│   └── SKILL.md
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
└── docs/
    ├── data-architecture.md            ← 数据体系总地图
    └── vendors-and-tools.md            ← 厂商/工具一览表（kb_to_md.py 自动生成）
```

---

## update 模式工作流

### 前置条件

`python -m collector.pipeline` 已运行，产出了 `data/pending/{date}/` 下的候选文件。

### 触发

`/codingplan-page update [自然语言]`

### 步骤

**Step 1: 读取待审阅候选**

读取 `data/pending/{date}/report.md`（如果 pipeline 刚跑完）或直接读以下文件：
- `data/pending/{date}/articles.json` — 候选文章（关键词召回）
- `data/signals/{date}.json` — 价格信号（price_monitor）
- `data/signals/extract-{date}.json` — 提取信号（sources/runner）

**Step 2: 去噪 + 分类**

主 agent 审阅候选文章，去噪规则：
- 泛泛而谈的产品介绍 → 跳过
- 纯技术教程（无 AI Coding Plan 关联）→ 跳过
- 与 AI Coding Plan 定价/模型/订阅变动直接相关 → 收录
- 行业趋势分析有深度 → 收录

同时解析用户的自然语言输入（如有），合并到变更中。

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
5. 提示用户「说 /codingplan-page build 生成 HTML」

**Step 6: 不自动 build**，用户确认后手动 `/codingplan-page build`

### 错误处理

- collector 跑失败 → 降级为纯人工（只用用户的自然语言输入）
- diff 输出后用户说"改 X 条" → 单独修改那条，重新输出 diff
- 用户说 n → 不动任何文件

---

## scan 模式工作流

### 触发

`/codingplan-page scan`

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

4. 提示用户「值得跟进的，说 /codingplan-page update ...」

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