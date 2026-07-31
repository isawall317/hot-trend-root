# Hot Trend 数据架构

> 项目数据体系的"总地图"——回答：数据从哪来、怎么采、存哪里、谁在用。
> 最后更新：2026-07-23
> 维护者：Frank + Claude Code

---

## 一、数据全景图

```
┌─────────────────────────────────────────────────────────────────────┐
│                          数据源层                                    │
│  DailyHotApi (40+平台)  Folo (本地RSS)  厂商定价页 (11家)  手动输入  │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     采集层 (tools/collector/)                        │
│                                                                     │
│  engine.py          → data/raw/{date}/      热点原始数据              │
│  sources/runner.py  → data/signals/         厂商定价提取 (7自动/4手动) │
│  price_monitor.py   → data/signals/         价格变动信号              │
│  maintenance_scanner→ data/pending/{date}/  候选文章 (实体匹配, Pipeline B)│
│  discovery_prefilter→ data/pending/{date}/  LLM 扫描输入 (Pipeline A) │
│  token_estimator    → plans.json            推算 Token 用量           │
│  pipeline.py        → 编排上述步骤，生成报告                         │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    审阅层 (Claude Code)                              │
│  /codingplan-page update  → 去噪 → 分类 → 草拟变更 → 用户确认         │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     存储层 (project/*/data/)                         │
│                                                                     │
│  codingplan-saver/  data/{site,vendors,plans,changes}.json          │
│  coding-tools/      data/{site,tools,affiliates,changes}.json        │
│  agent-patterns/    data/{site,patterns,changes}.json               │
│  aicoding-stack/    data/{site,combos,changes}.json                 │
│  aicoding-tips/     data/{site,tips,changes}.json                   │
│  ccskills-market/   data/{site,skills,changes}.json                 │
│  model-picker/      data/{site,models,changes}.json                 │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    构建层 (tools/builder/)                           │
│  build.py → dist/{project}-{timestamp}.html                         │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 二、数据源层

### 2.1 热点数据（DailyHotApi + Folo）

| 源 | 覆盖 | 采集方式 | 状态 |
|----|------|---------|------|
| DailyHotApi | 40+ 平台（知乎、微博、36氪、V2EX 等） | httpx 异步并发 | 优先本地 Docker，降级 Vercel 公共 API |
| Folo | 本地 RSS 阅读器订阅源 | `npx folocli@latest timeline` subprocess | 本地应用运行中时自动采集，未运行则跳过 |

Folo 通过 `folocli` CLI 与本地 Folo（原 Follow）RSS 阅读器交互，拉取 timeline 中已订阅源的文章。环境变量控制：
- `FOLO_LIMIT`（默认 100）：每次拉取条数
- `FOLO_VIEW`（默认 0）：0=文章 1=社交 2=图片 3=视频

归一化格式：`{title, url, hot_metric, source, source_type, collected_at}`

### 2.2 厂商定价数据

14 家 AI 模型厂商的 Coding Plan / Token Plan 定价信息。

| 状态 | 数量 | 厂商 | 提取方式 |
|------|------|------|---------|
| ✅ 自动提取 | 7 | 智谱AI, DeepSeek, Kimi, MiniMax, 腾讯云, Claude, GitHub | Playwright / BS4 静态解析 |
| ❌ 手动维护 | 7 | 字节·方舟, 阿里·百炼, Codex, 小米·MiMo, 百度·千帆, OpenRouter, 硅基流动 | 人工定期检查 |

> 详细厂商 URL、提取策略、推广链接见 [`docs/vendors-and-tools.md`](vendors-and-tools.md)（由 `kb_to_md.py` 从 `aikb/database/` JSON 自动生成）

### 2.3 AI 知识库（🆕 `aikb/`）

`aikb/` 是**AI 维护的文档数据库**：MD 文件是画像层（AI 读写），`aikb/database/` 下的 JSON 由 `kb_migrate.py` 从 `project/codingplan-saver/data/` 自动同步，供下游项目消费。

> ⚠️ **真相源说明**：套餐/价格的真实数据源是 `project/codingplan-saver/data/*.json`（builder 实际读取），`aikb/database/` 是其下游镜像。MD 画像层（`aikb/vendors|tools/*.md`）覆盖中，部分厂商尚无 MD（目标态）。

| 目录 | 内容 | 格式 | 维护方式 |
|------|------|------|---------|
| `aikb/vendors/` | 厂商画像 MD（覆盖中，14/28 家） | MD + YAML frontmatter | `/kb-update` + AI 直接编辑 |
| `aikb/tools/` | 工具详情 MD（每款一个 MD） | MD + YAML frontmatter | `/kb-update` + AI 直接编辑 |
| `aikb/database/` | 结构化 JSON（vendors/services/tools/models/changes） | JSON | `kb_migrate.py` 从 project/ 自动同步 |

> MD 是 AI 的原生语言（LLM 在 MD 上读写的准确率远高于 JSON），
> `database/` JSON 是给下游项目（codingplan-saver 等）消费的结构化视图。

### 2.4 手动输入

- 用户通过自然语言告知的变动（如"Kimi 涨价了"）
- `/codingplan-page update` 解析自然语言 → 结构化变更

---

## 三、采集层

### 3.1 模块地图

```
tools/collector/collector/
├── engine.py              # 热点采集引擎 (DailyHotApi + Folo)
├── storage.py             # 存储/读取 (load_latest, load_date_range)
├── pipeline.py            # 数据管道编排 (5步)
├── price_monitor.py       # 价格信号监控 (关键词匹配)
├── maintenance_scanner.py # 实体匹配候选文章 (Pipeline B 维护)
├── discovery_prefilter.py # LLM 扫描输入预过滤 (Pipeline A 发现)
├── token_estimator.py     # Token 用量推算 (3级策略)
└── sources/               # 厂商定价提取器
    ├── base.py            # BaseParser / BasePlaywrightParser
    ├── runner.py          # 调度器 (并行执行所有 parser)
    ├── merge.py           # 合并提取结果 → plans.json
    ├── zhipu.py           # 智谱AI (Playwright)
    ├── deepseek.py        # DeepSeek (BS4 静态)
    ├── kimi.py            # Kimi (Playwright)
    ├── minimax.py         # MiniMax (BS4 静态)
    ├── tencent.py         # 腾讯云 (BS4 静态)
    ├── claude.py          # Claude (Playwright)
    └── github.py          # GitHub (Playwright)
```

### 3.2 管道执行流程

```bash
cd tools/collector && uv run python -m collector.pipeline
```

```
Step 1: engine.py       → data/raw/{date}/*.json          热点原始数据 (DailyHotApi + Folo)
Step 2: maintenance_sc.. → data/pending/{date}/articles.json 候选文章 (实体匹配)
Step 3: price_monitor   → data/signals/{date}.json         价格信号
Step 4: sources/runner  → data/signals/extract-{date}.json 厂商提取
         sources/merge  → plans.json (合并提取结果)
Step 5: token_estimator → plans.json (推算 measuredMonthlyToken)
```

每步独立错误处理，单步失败不影响后续。

### 3.3 厂商提取策略

| 策略 | 方法 | 适用场景 |
|------|------|---------|
| `docs` (BS4 静态) | httpx + BeautifulSoup 解析静态文档页 | DeepSeek, MiniMax, 腾讯云 |
| `docs` (Playwright) | Playwright 渲染 SPA 页面后 BS4 解析 | 智谱AI, Kimi, Claude, GitHub |
| `manual` | runner 跳过，人工定期检查 | 字节·方舟, 阿里·百炼, Codex, 小米·MiMo |

决策树：`urls.api` 非空 → API 策略；`urls.docs` 非空 → docs 策略；都空 → manual。

---

## 四、存储层

### 4.1 原始数据（gitignore）

```
data/
├── raw/YYYY-MM-DD/       # 热点原始数据 (engine.py 产出)
├── signals/              # 价格/文章信号 (price_monitor + sources/runner)
├── pending/{date}/       # 候选文章 (maintenance_scanner, 待 Claude Code 审阅)
├── pipeline-reports/     # 管道运行报告
├── price-reports/        # 价格分析报告
├── cards/                # 机会卡 (/scan 产出)
└── archive/              # 历史归档
```

### 4.2 项目数据（git 跟踪）

每个项目遵循统一的数据模式：

```
project/{name}/
├── data/
│   ├── site.json         # 站点配置
│   ├── {entity}.json     # 主数据 (plans/tools/models/patterns/...)
│   ├── changes.json      # 变动时间线
│   └── ...               # 项目特有数据
├── template/             # HTML 模板
└── docs/                 # 项目文档 (可选)
```

### 4.3 AI 知识库（`aikb/`）

多个项目共享同一套厂商基础数据。**`aikb/database/` JSON 由 `kb_migrate.py` 从 `project/codingplan-saver/data/` 自动同步**（pipeline Step 5b），`aikb/vendors|tools/*.md` 是 AI 维护的画像层（覆盖中）。

```
aikb/                               ← 🆕 AI 知识库（Obsidian 兼容）
├── index.md                         ← 导航索引
├── vendors/                         ← 厂商画像（14 家，每家一个 MD）
│   ├── zhipu.md
│   ├── deepseek.md
│   └── ...
├── tools/                           ← 工具详情（31 款，每款一个 MD）
│   ├── cursor.md
│   └── ...
└── database/                        ← 结构化 JSON（md_to_json.py 自动生成）
    ├── vendors.json
    ├── services.json
    ├── tools.json
    ├── models.json
    └── changes.json
         │
         ├── docs/vendors-and-tools.md  (由 kb_to_md.py 从 database/ JSON 生成)
         ├── codingplan-saver/data/plans.json    (价格投影层：下游直接读，pipeline 维护)
         └── coding-tools/data/tools.json        (工具投影层：下游直接读)
```

> **三层架构**：MD 画像（AI 维护）→ database/ JSON（md_to_json.py 生成）→ 下游项目（直接读 JSON）。
> pipeline 每次跑同时维护两层——价格进 plans.json（已有），画像进 aikb/database/（kb_migrate re-sync）。
> AI 修改 MD 后运行 `python -m collector.md_to_json` 刷新 database/ JSON。

### 4.4 通用文件模式

| 文件 | 职责 | 出现于 |
|------|------|--------|
| `site.json` | 站点级配置（博主、推荐、社群） | 所有 7 个项目 |
| `changes.json` | 统一变动时间线（价格/模型/文章） | 所有 7 个项目 |
| `{entity}.json` | 项目主数据（plans/tools/models/patterns/skills/combos/tips） | 每个项目不同 |

> `changes.json` 的 Schema 定义见 [`project/codingplan-saver/data/SCHEMA.md`](../project/codingplan-saver/data/SCHEMA.md)（通用参考，其他项目复用相同结构）。

---

## 五、消费层

### 5.1 项目清单

| 项目 | 目录 | 主数据 | 状态 |
|------|------|--------|------|
| **CodingPlan 省钱攻略** | `project/codingplan-saver/` | `plans.json` (31条套餐) | 🟢 核心产品 |
| **AI Coding 工具对比** | `project/coding-tools/` | `tools.json` (18款工具) | 🟡 开发中 |
| **Agent Patterns** | `project/agent-patterns/` | `patterns.json` | 🟡 开发中 |
| **AI Coding Stack** | `project/aicoding-stack/` | `combos.json` | 🟡 开发中 |
| **AI Coding Tips** | `project/aicoding-tips/` | `tips.json` | 🟡 开发中 |
| **CC Skills Market** | `project/ccskills-market/` | `skills.json` | 🟡 开发中 |
| **Model Picker** | `project/model-picker/` | `models.json` | 🟡 开发中 |

### 5.2 数据依赖关系

```
project/codingplan-saver/data/*.json (套餐/价格真相源，builder 读取)
    │
    ├── codingplan-saver: 依赖 vendors.json + plans.json + changes.json
    │       └── 产出: codingplan-saver.html
    │
    ├── kb_migrate.py → aikb/database/*.json (下游镜像)
    │       └── kb_to_md.py → docs/vendors-and-tools.md (自动生成一览表)
    │
    └── coding-tools: 独立 tools.json（aikb/database/tools.json 含补充的国产工具）
            └── 产出: coding-tools.html
```

---

## 六、更新流程

### 6.1 自动管道（CronCreate 定时 或 `/codingplan-page build`）

```
python -m collector.pipeline
  ├── 1. engine.py → data/raw/
  ├── 2. maintenance_scanner → data/pending/{date}/articles.json
  ├── 3. price_monitor → data/signals/
  ├── 4. sources/runner → data/signals/extract-{date}.json
  │      └── sources/merge → plans.json (合并 7 家自动提取结果)
  └── 5. token_estimator → plans.json (推算 measuredMonthlyToken)
```

### 6.2 Claude Code 审阅（`/codingplan-page update`）

1. 读取 `data/pending/{date}/articles.json` 候选文章
2. 去噪：跳过纯技术教程、泛行业新闻
3. 收录：与 AI Coding Plan 定价/模型/订阅直接相关的文章
4. 生成结构化变动：`new_model` / `price_change` / `subscription_pause`
5. 写入 `changes.json` + 更新 `site.json`

### 6.3 手动维护（按需）

1. 定期检查 4 家 manual 厂商的定价页
2. 更新 `plans.json` 中变动项
3. 更新 `changes.json` 记录价格/模型变动
4. 新增厂商：先在 `reference/vendors-and-tools.md` 登记 → 再更新项目 JSON

---

## 七、已知问题

| 问题 | 严重程度 | 计划 |
|------|----------|------|
| 4 家厂商无法自动提取 | 中 | 字节方舟/MiMo 可尝试 Playwright；阿里/Codex 需人工 |
| coding-tools 等 6 个项目数据未体系化采集 | 中 | 后续统一采集管道 |
| 数据验证缺失 | 中 | 后续添加 data_validator.py |
| 机会卡仅 1 张 | 高 | 后续在 /scan 流程中持续产出 |
| 各项目 `changes.json` 独立维护，无统一来源 | 低 | 可考虑统一 changes 管道 |

---

## 八、相关文档

| 文档 | 用途 |
|------|------|
| [`docs/vendors-and-tools.md`](vendors-and-tools.md) | 厂商/工具 URL、提取策略、推广链接 |
| [`project/codingplan-saver/data/SCHEMA.md`](../project/codingplan-saver/data/SCHEMA.md) | plans.json / changes.json 详细字段定义 |
| [`.claude/skills/codingplan-page/SKILL.md`](../.claude/skills/codingplan-page/SKILL.md) | CodingPlan 省钱攻略更新流程 |
| [`CLAUDE.md`](../CLAUDE.md) | 项目总入口 |