# Hot Trend — AI 利基发现与变现系统

## 系统定位

从全网热点中自动发现**细分赛道利基** → AI 深度分析 → 快速验证 → 小软件产品变现。

当前核心产品：
- **CodingPlan 省钱攻略** ([codingplan.fyi](https://www.codingplan.fyi)) — 29 家 AI 模型厂商 Coding Plan / Token Plan 对比
- **AI Coding 工具对比** (开发中) — 18 款 AI 编程工具横向评测

**我不是在找热点新闻，而是在找可商业化的需求缺口。**

## 架构概览

```
数据源 → 采集 → 两条并行管线
  │        │       │
  │    engine.py  Pipeline A: 发现  → LLM 语义扫描 → 需求信号 → /discover
  │    sources/   Pipeline B: 维护  → 实体匹配 + 价格信号 → /codingplan-page
  │    pipeline                     (维护已有产品数据)
  │
DailyHotApi (40+平台) + Folo (本地RSS) + 14 家厂商定价页
```

> **两条管线的根本区别**：
> - **Pipeline A (Discovery)**: 开放式问题 — "今天有什么值得做的新东西？" → LLM 语义扫描，不做关键词过滤
> - **Pipeline B (Maintenance)**: 闭合式问题 — "CodingPlan/Tools 的数据需要哪些更新？" → 基于 KB 已知实体的精确匹配
> 
> 详细数据流、模块职责、更新流程 → [`docs/data-architecture.md`](docs/data-architecture.md)

## 技能

| 技能 | 触发 | 用途 |
|------|------|------|
| `/discover` | `discover` / `发现需求` | **Pipeline A**: 热点 → LLM 语义扫描 → 需求信号 |
| `/analyze` | `analyze` / `分析` | 利基深度分析 + 6 维评分 |
| `/validate` | `validate` / `验证` | 竞品调研 + MVP 定义 + Go/No-Go |
| `/codingplan-page` | 或 `build` / `update` | **Pipeline B**: CodingPlan 数据更新 + HTML 生成 |
| `/vendors-sync` | 或 `scan` | 厂商/工具信息同步，更新 docs/vendors-and-tools.md |
| `/kb-update` | 或 `kb` | 知识库更新：采集 → 检测 → 审阅 → 合并 |

> 详细执行流程见 `.claude/skills/{name}/SKILL.md`

## 日常操作

```bash
# 采集数据（launchd 定时：每天 9:17 / 14:17 / 20:17 自动跑，日志在 data/logs/）
cd tools/collector && uv run python -m collector.pipeline

# 一键全量更新 CodingPlan 页面（采集 → 审阅 → 生成 HTML）
/codingplan-page

# 单独审阅候选文章，更新 changes.json
/codingplan-page update

# 扫描信号（只读报告，不动 JSON）
/codingplan-page scan
```

> ✅ 2026-07-31 起 EdgeOne Makers 部署链路已打通（`tools/deploy/deploy.sh`：build → cp 到 codingplan-site → makers deploy）。线上最终入口 `codingplan.fyi` 待 DNS 切换，当前用默认域名访问受区域限制（401）。详见 [`docs/deployment.md`](docs/deployment.md)。

## 目录结构

```
hot-trend-root/
├── CLAUDE.md                     # 本文件
├── aikb/                         # 🆕 AI 知识库（Obsidian 兼容）
│   ├── index.md                  #   导航索引
│   ├── vendors/                  #   厂商画像 MD（AI 维护，部分厂商待补）
│   ├── tools/                    #   工具详情 MD（每款一个 MD）
│   └── database/                 #   结构化 JSON（kb_migrate.py 从 project/ 同步）
├── docs/                         # 项目文档
│   ├── data-architecture.md      # 数据体系总地图
│   └── vendors-and-tools.md      # 厂商/工具一览表（由 kb_to_md.py 自动生成）
├── .claude/skills/               # 6 个技能定义
├── data/
│   ├── raw/                      # 热点原始数据
│   ├── signals/                  # 价格/文章信号
│   └── pending/                  # 待审阅候选
├── tools/
│   ├── collector/                # Python 数据采集管道
│   └── builder/build.py          # HTML 构建器
├── project/                      # 7 个孵化项目
│   ├── codingplan-saver/         # 🟢 核心产品
│   ├── coding-tools/             # 🟡 开发中
│   ├── agent-patterns/           # 🟡 开发中
│   ├── aicoding-stack/           # 🟡 开发中
│   ├── aicoding-tips/            # 🟡 开发中
│   ├── ccskills-market/          # 🟡 开发中
│   └── model-picker/             # 🟡 开发中
├── dist/                         # HTML 交付物
└── reference/                    # 参考资料（用户画像）
```

## 文档入口

| 想知道什么 | 去看 |
|-----------|------|
| 数据从哪来、怎么采、存哪里、谁在用 | [`docs/data-architecture.md`](docs/data-architecture.md) |
| 线上站点与仓库的关系、部署链路现状 | [`docs/deployment.md`](docs/deployment.md) |
| 有哪些厂商/工具、URL、提取策略、推广链接 | [`docs/vendors-and-tools.md`](docs/vendors-and-tools.md) |
| plans.json / changes.json 字段定义 | [`project/codingplan-saver/data/SCHEMA.md`](project/codingplan-saver/data/SCHEMA.md) |
| codingplan-page 完整操作流程 | [`.claude/skills/codingplan-page/SKILL.md`](.claude/skills/codingplan-page/SKILL.md) |

## 关键原则

- **需求优先** — 先确认有人在找解决方案，再考虑怎么解决
- **数据驱动** — 让采集数据说话，不做主观判断
- **AI 撬动** — 每个环节问"AI 能做多少？我只需要做什么？"
- **快速验证** — 不要完美，先验证再打磨
- **plans.json 为价格真相源** — `project/codingplan-saver/data/*.json` 是 builder 实际读取的数据源（vendors/plans/changes）；`aikb/database/*.json` 由 `kb_migrate.py` 从 project 自动同步（pipeline Step 5b）；`aikb/vendors|tools/*.md` 是 AI 维护的画像层（部分厂商 MD 待补，目标态见 `docs/data-architecture.md`）；`docs/vendors-and-tools.md` 由 `kb_to_md.py` 从 `aikb/database/` 自动生成，勿手工编辑。**改套餐/价格 → 改 project；改完跑 `python -m collector.kb_migrate` 同步 aikb，再跑 `python -m collector.kb_to_md` 刷新一览表。**

## 用户画像（Frank）

- 公众号 7000 粉，前 AI+知识管理+读书赛道
- 盖洛普 Top 5: 交往(1) 学习(2) 理念(3) 完美(4) 成就(5)
- 0→1 构想是超能力，执行跟进是盲点
- 偏好：睡后收入（小软件产品），5-10h/周
- 商业逻辑优先，AI 补齐能力短板
- 国内优先，不碰灰产/合规雷区/重运营

## 利基评估标准（6 维）

1. **需求真实性** / 2. **增长潜力** / 3. **付费意愿** / 4. **竞争空间** / 5. **执行可行性** / 6. **规模化潜力**

> 详细评分标准见 `.claude/skills/analyze/SKILL.md`