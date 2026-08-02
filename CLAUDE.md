# Hot Trend — AI 利基发现与变现系统

## 系统定位

从全网热点中自动发现**细分赛道利基** → AI 深度分析 → 快速验证 → 小软件产品变现。

当前核心产品：
- **CodingPlan 省钱攻略** ([codingplan.fyi](https://www.codingplan.fyi)) — 7 家 AI 模型厂商 Coding Plan / Token Plan 对比（当前跟踪价格的核心厂商）
- **AI Coding 工具对比** (开发中) — 31 款 AI 编程工具横向评测

**我不是在找热点新闻，而是在找可商业化的需求缺口。**

## 架构概览

```
数据源 → 采集 → 两条并行管线
  │        │       │
  │    engine.py  Pipeline A: 发现  → LLM 语义扫描 → 需求信号 → /discover
  │    sources/   Pipeline B: 维护  → 实体匹配 + 价格信号 → /codingplan-page
  │    pipeline                     (维护已有产品数据)
  │
DailyHotApi (40+平台) + Folo (本地RSS) + 8 家厂商定价页自动提取
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
| `/scan` | `scan` / `扫描` | 热点扫描 + 初筛（聚类 + 利基信号） |
| `/analyze` | `analyze` / `分析` | 利基深度分析 + 6 维评分 |
| `/validate` | `validate` / `验证` | 竞品调研 + MVP 定义 + Go/No-Go |
| `/codingplan-page` | 或 `build` / `update` | **Pipeline B**: CodingPlan 数据更新 + HTML 生成 |
| `/vendors-sync` | `vendors-sync` | 厂商信息同步，更新 project/codingplan-saver/vendors-and-tools.md |
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

> ✅ 2026-07-31 EdgeOne Makers 部署链路已打通并首次部署成功（7 家核心厂商版本已上线 production）。`tools/deploy/deploy.sh`（跨平台 Win/Mac/Unix）已接进 `/codingplan-page` 的 Step 6，支持 `preview` 先验证再 `production` 上线。最终入口 `codingplan.fyi` 待绑定自定义域名（迁移路线 ③）。详见 [`project/codingplan-saver/deployment.md`](project/codingplan-saver/deployment.md)。

## 目录结构

```
hot-trend-root/
├── CLAUDE.md                     # 本文件（系统总纲）
├── docs/
│   └── data-architecture.md      # 数据体系总地图（系统级）
├── .claude/skills/               # 7 个技能定义
├── data/
│   ├── raw/                      # 热点原始数据
│   ├── signals/                  # 价格/文章信号
│   ├── pending/                  # 待审阅候选
│   └── recovery/                 # 线上抢救数据（只读）
├── tools/
│   ├── collector/                # Python 数据采集管道
│   ├── builder/build.py          # HTML 构建器
│   └── deploy/deploy.sh          # EdgeOne Makers 部署脚本
├── project/                      # 孵化项目矩阵
│   ├── codingplan-saver/         # 🟢 核心产品
│   │   ├── data/                 #   唯一真相源（*.json + SCHEMA.md）
│   │   ├── template/             #   HTML 模板 + 脚本
│   │   ├── deployment.md         #   部署链路
│   │   ├── vendors-and-tools.md  #   厂商一览表（kb_to_md.py 自动生成）
│   │   └── archive/              #   V1 + aikb 历史归档
│   ├── codingplan-site/          #   codingplan-saver 的部署目录
│   └── (其他项目: coding-tools/agent-patterns/...)
├── dist/                         # HTML 交付物
└── reference/                    # 参考资料
```

## 文档入口

| 想知道什么 | 去看 |
|-----------|------|
| 数据从哪来、怎么采、存哪里、谁在用 | [`docs/data-architecture.md`](docs/data-architecture.md) |
| 线上站点与仓库的关系、部署链路 | [`project/codingplan-saver/deployment.md`](project/codingplan-saver/deployment.md) |
| 有哪些厂商、URL、提取策略、推广链接 | [`project/codingplan-saver/vendors-and-tools.md`](project/codingplan-saver/vendors-and-tools.md) |
| plans.json / changes.json 字段定义 | [`project/codingplan-saver/data/SCHEMA.md`](project/codingplan-saver/data/SCHEMA.md) |
| codingplan-page 完整操作流程 | [`.claude/skills/codingplan-page/SKILL.md`](.claude/skills/codingplan-page/SKILL.md) |

## 关键原则

- **需求优先** — 先确认有人在找解决方案，再考虑怎么解决
- **数据驱动** — 让采集数据说话，不做主观判断
- **AI 撬动** — 每个环节问"AI 能做多少？我只需要做什么？"
- **快速验证** — 不要完美，先验证再打磨
- **project/data 是唯一真相源** — `project/codingplan-saver/data/*.json` 是 builder 和所有下游唯一读取的数据源。`project/codingplan-saver/vendors-and-tools.md` 由 `kb_to_md.py` 从 data 直接生成。**改套餐/价格 → 改 project/data → 跑 `python -m collector.kb_to_md` 刷新一览表 → 跑 build.py 重建 HTML。** 不存在 aikb/ 中间镜像层。

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