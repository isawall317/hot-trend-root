# Hot Trend 系统方案

## 核心判断：Claude Code Native

**为什么不是独立 Python 工具？**

你只有 5-10h/周，维护独立部署的系统（服务器、定时任务、数据库）会吃掉你大部分时间。你已经在用 Claude Code 了——它就是你的 AI 操作系统。系统应该活在 Claude Code 里，而不是另起炉灶。

**一句话架构：** Claude Code 是中央大脑，Python 脚本只做"采集"这一件 Claude Code 做不了的事（定时爬取），其余分析、评分、验证、执行全部在 Claude Code 内完成。

---

## 三层架构

```
┌─────────────────────────────────────────────────┐
│              Layer 3: 执行层                      │
│   Claude Code 直接开发产品 → 上线 → 变现          │
│   (skills: /build-mvp, /deploy, /launch)         │
├─────────────────────────────────────────────────┤
│              Layer 2: 分析决策层                   │
│   Claude Code 工作流: 洞察 → 评分 → 验证 → 机会卡  │
│   (skills: /scan, /analyze, /validate)           │
├─────────────────────────────────────────────────┤
│              Layer 1: 数据采集层                   │
│   Python 脚本 + RSSHub → 定时采集 → 结构化存储     │
│   (cron: 每天 2-3 次自动运行)                     │
└─────────────────────────────────────────────────┘
```

---

## Layer 1: 数据采集层（唯一需要写代码的层）

### 采集源设计

| 类别 | 来源 | 采集方式 | 频率 |
|------|------|----------|------|
| **平台热点** | 知乎热榜、微博热搜、B站热门、即刻 | RSSHub | 每 4h |
| **商业化信号** | 知识星球精选、小报童畅销榜、少数派 | 自定义爬虫 | 每天 1 次 |
| **搜索信号** | 微信指数、百度指数、5118 | API + 爬虫 | 每天 1 次 |
| **开发社区** | GitHub Trending、V2EX、ProductHunt | RSSHub + API | 每 4h |
| **付费信号** | 淘宝搜索词、闲鱼需求 | 爬虫 | 每天 1 次 |

### 技术方案

```
tools/collector/           # Python 采集器（最小化）
├── pyproject.toml
├── collector/
│   ├── __init__.py
│   ├── engine.py          # 采集引擎：遍历源 → 调用对应采集器 → 去重 → 存储
│   ├── sources/
│   │   ├── rss.py         # RSSHub 统一接口
│   │   ├── weixin.py      # 微信指数/公众号
│   │   ├── xiaohongshu.py # 小红书
│   │   ├── zhihu.py       # 知乎热榜
│   │   ├── xiaobaotong.py # 小报童
│   │   ├── github.py      # GitHub Trending
│   │   └── producthunt.py # ProductHunt
│   └── storage.py         # 统一存储：JSON 文件 → data/raw/
└── data/
    ├── raw/               # 原始采集数据（按日期分文件）
    ├── cards/             # 机会卡（git 跟踪）
    └── archive/           # 历史归档
```

### 运行方式

- **本地运行**：`python -m collector.engine` 手动触发
- **定时运行**：通过 Claude Code CronCreate 或系统 crontab
- **输出格式**：统一 JSON Schema，方便 Claude Code 直接读取分析

### 为什么这么轻？

- 不需要数据库：JSON 文件足够，Claude Code 可以直接读
- 不需要 API 服务：Claude Code 就是你的交互界面
- 不需要复杂调度：cron 足够，Claude Code CronCreate 管理

---

## Layer 2: 分析决策层（Claude Code Skills）

### 工作流

```
采集完成 → /scan → /analyze → /validate → 机会卡
```

### Skill 1: `/scan` — 热点扫描

**触发：** 手动或定时（每天早晚各一次）
**动作：**
1. 读取 `data/raw/` 最新采集数据
2. LLM 初筛：过滤噪音、去重、按主题聚类
3. 输出：热点简报（Markdown），含 20-30 条候选信号

### Skill 2: `/analyze` — 利基深度分析

**触发：** 对 scan 结果中感兴趣的信号
**动作：**
1. 需求真实性验证（搜索量、讨论量、付费证据）
2. 竞争格局分析（已有产品、内容供给、差异化空间）
3. 商业化潜力评估（付费意愿、客单价、市场规模）
4. 执行可行性评估（技术难度、时间投入、AI 可替代程度）
**输出：** 利基分析报告 + 6 维评分卡

### Skill 3: `/validate` — 快速验证

**触发：** 对评分 Top 3 的机会
**动作：**
1. 竞品深度调研（功能、定价、用户反馈、流量来源）
2. 种子用户验证（在小红书/知乎发测试内容看反馈）
3. MVP 范围定义（最小可行产品要做什么、不做什么）
**输出：** 验证报告 + Go/No-Go 建议

### 机会卡产物

每个验证通过的机会生成一张"机会卡"存入 `data/cards/`：

```markdown
# 机会卡: [标题]
- 发现日期: 2026-07-20
- 来源信号: [知乎热榜/小报童畅销/...]
- 利基描述: [一句话]
- 商业化路径: [产品/社群/...]
- 6维评分: ...
- 技术方案: [推荐的技术栈]
- 预计工时: [AI 辅助下 X 小时可完成 MVP]
- 状态: 🔍验证中 | 🟢开发中 | 🟡已上线 | 🔴放弃
```

---

## Layer 3: 执行层（Claude Code 直接开发）

当机会卡进入 🟢 开发中状态：

1. **Claude Code 直接开发** — 你就是产品经理 + AI 是工程师
2. **技术栈按需选择** — 浏览器插件 / Web 应用 / 小程序 / AI Agent
3. **快速上线** — 目标：每个 MVP 不超过 10h AI 辅助开发时间
4. **数据驱动迭代** — 上线后看数据，好就继续投入，不好就换下一个

---

## 目录结构总览

```
hot-trend-root/
├── CLAUDE.md                    # Claude Code 项目指令（核心）
├── .claude/
│   ├── skills/
│   │   ├── scan.md             # 热点扫描 skill
│   │   ├── analyze.md          # 利基分析 skill
│   │   └── validate.md         # 快速验证 skill
│   └── workflows/
│       └── daily-scan.js       # 每日扫描自动化工作流
├── tools/
│   └── collector/              # Python 采集器
├── data/
│   ├── raw/                    # 原始数据（.gitignore）
│   ├── cards/                  # 机会卡（git 跟踪）
│   └── archive/                # 历史归档
├── reference/                  # 参考资料
│   └── 个人使用说明书-v2026.md
└── project/                    # 已孵化项目
    └── codingplan-saver/       # 已有项目
```

---

## 实施路线图

### Phase 1: 搭骨架（本周，~3h）
- [ ] 创建目录结构
- [ ] 写 `CLAUDE.md`（让 Claude Code 理解整个系统）
- [ ] 实现 `/scan` skill（先用手动采集数据验证流程）
- [ ] 跑通第一次扫描 → 分析 → 机会卡全流程

### Phase 2: 数据管道（下周，~4h）
- [ ] 搭建 Python 采集器（RSSHub + 核心 3-5 个源）
- [ ] 配置 CronCreate 定时采集
- [ ] 调试 `/scan` → `/analyze` → `/validate` 工作流

### Phase 3: 持续运转（持续）
- [ ] 每天早晚扫描，生成机会卡
- [ ] 每周复盘：哪些机会卡值得验证
- [ ] 每月复盘：哪些验证通过的机会值得开发
- [ ] 第一个产品 MVP 上线

---

## 关键设计决策

### 为什么是 Claude Code Native 而不是独立系统？

| 独立 Python 系统 | Claude Code Native |
|---|---|
| 需要部署服务器 | 本地运行，零部署 |
| 需要自己建数据库 | JSON 文件，Claude 直接读 |
| 需要写 Web UI | Claude Code 就是交互界面 |
| 需要自己对接 LLM | Claude Code 内置 |
| 定时任务需要自己维护 | CronCreate 管理 |
| 采集和分析是两套系统 | 采集轻量，分析全部在 Claude Code 内 |
| 你每周要花时间维护系统 | 你只花时间做决策 |

### 为什么采集层还用 Python？

因为 Claude Code 不能做定时网络请求。但采集层被设计成**最小化**——只负责"把数据拉下来存成 JSON"，不做任何分析。分析全部交给 Claude Code。

---

## 待确认

1. **采集源优先级**：全量覆盖是目标，但 Phase 1 先做哪 3-5 个源？建议：知乎热榜 + 小报童畅销 + GitHub Trending + V2EX + 即刻
2. **扫描频率**：每天 2 次（早晚）够不够？还是需要更高频率？
3. **机会卡存储**：用 Markdown 文件（git 跟踪）还是 JSON？Markdown 更适合 Claude Code 直接阅读