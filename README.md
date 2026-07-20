# Hot Trend → AI GitHub 小项目孵化器

## 思路

不从零想点子，而是从**知乎、公众号、小红书等主流内容平台的相关领域热文**入手：

1. **挖掘热文** — 追踪各平台 AI / 编程 / 效率工具 / 副业 等领域的高赞文章
2. **分析需求** — 从热文中提取真实痛点、信息差、用户需求
3. **评估可行性** — 判断能否做成 AI GitHub 小项目，评估变现潜力
4. **孵化项目** — 在本目录下建立文件夹，快速出 MVP
5. **独立建仓** — 项目成熟后，单独创建 GitHub 仓库

## 孵化流程

```
热文发现 → 需求洞察 → 竞品参考（ref/） → 项目孵化（文件夹） → 独立仓库
```

## 核心工具：hot-trend

`hot-trend` 是 CLI 工具 + Workflow 编排层，从全网热榜中发现可孵化的 AI 项目机会。

**架构**：Python 纯函数库（core） + 薄 CLI + Claude Code Workflow 编排

```
┌──────────────────────────────────────────────────┐
│              用户入口                              │
├──────────┬──────────────────┬────────────────────┤
│ hot-trend│  hot-trend       │  workflows/*.js     │
│ scan     │  analyze <url>   │  (并行编排脚本)       │
└──────────┴──────────────────┴────────────────────┘
├──────────────────────────────────────────────────┤
│              hot_trend Python 核心库              │
│  sources/  extractor  llm  models  analyzer  card │
└──────────────────────────────────────────────────┘
```

### 快速开始

```bash
# 1. 安装（开发模式，从项目根目录）
pip install -e .

# 2. 配置
cp config.example.yaml config.yaml
cp .env.example .env
# 编辑 .env，填一个 LLM API key

# 3. 扫热榜
hot-trend scan --source github -l 10

# 4. 分析一条趋势
hot-trend analyze https://github.com/xxx/yyy

# 5. 批量并行分析（Claude Code 中运行）
Workflow({scriptPath: 'workflows/discover.js', args: {source: 'github', limit: 10, picks: 5}})
```

### 命令

| 命令 | 说明 | 入口 |
|------|------|------|
| `hot-trend scan` | 扫热榜（单源，展示） | Python CLI |
| `hot-trend analyze <url>` | 分析单条 URL | Python CLI |
| `workflows/discover.js` | 扫描 + 并行批量分析 | Workflow 脚本 |
| `workflows/multi-source-scan.js` | 多源并行扫描 | Workflow 脚本 |
| `workflows/cross-validate.js` | 多模型交叉验证评分 | Workflow 脚本 |
| `workflows/weekly-report.js` | 周报自动生成 | Workflow 脚本 |

### 支持的数据源

| 源 | 类型 | 是否需要 Token |
|----|------|---------------|
| `github` | GitHub Search API | 可选 GITHUB_TOKEN |
| `github-trending` | GitHub Trending HTML | 不需要 |
| `hn` | Hacker News Firebase API | 不需要 |
| `v2ex` | V2EX 官方 API | 不需要 |
| `zhihu` / `weibo` / `bilibili` / `toutiao` / `wechat-ce` | RSSHub | 需自建 RSSHub |

### 6 维评分模型

| 维度 | 含义 | 5 分 = |
|------|------|--------|
| demand | 需求强度 | 痛点，不解决就难受 |
| willingness_to_pay | 付费意愿 | 已有竞品收费 |
| ai_feasibility | AI 可行性 | AI 是核心价值 |
| competition | 竞争（倒扣） | 蓝海，无直接竞品 |
| dev_cost | 开发成本（倒扣） | 1 周内能出 MVP |
| monetization | 变现潜力 | 高客单价或巨量用户 |

**判定**：≥22 值得孵化 · 18-21 观察 · <18 丢弃

### 依赖

- Python 3.10+
- 一个 LLM API key（推荐智谱 GLM / MiniMax，国内稳定便宜）
- （可选）自建 RSSHub 实例用于中文源

## 当前项目

| 项目 | 状态 | 来源 | 说明 |
|------|------|------|------|
| [codingplan-saver](./codingplan-saver/) | 🟢 MVP 完成 | AI Coding Plan 热文 | AI Coding Plan 选型对比网站，覆盖 15+ 平台 29+ 套餐 |
| [hot-trend](./) | 🟢 v0.2 (重写完成) | — | CLI + Workflow 编排：从全网热榜扫描 → 并行分析 → 机会卡 |

## 目录结构

```
hot-trend-root/
├── src/hot_trend/           # Python 核心库
│   ├── cli.py               # 薄 CLI（scan + analyze）
│   ├── models.py            # Pydantic 数据模型
│   ├── config.py            # 配置加载
│   ├── extractor.py         # 正文抽取
│   ├── llm.py               # 多 Provider LLM 抽象
│   ├── analyzer.py          # 分析核心（洞察 + 评分）
│   ├── card.py              # 卡片渲染 + 保存
│   ├── prompts/             # LLM prompt 模板
│   └── sources/             # 数据源采集
├── workflows/                # Workflow 编排脚本
│   ├── discover.js           # 并行 discover
│   ├── multi-source-scan.js  # 多源并行扫描
│   ├── cross-validate.js     # 多模型交叉验证
│   └── weekly-report.js      # 周报生成
├── opportunities/cards/      # 机会卡输出
├── ref/                      # 竞品参考
├── deploy/                   # 部署文档
├── config.yaml / .env        # 配置
├── pyproject.toml
└── README.md
```

## 参考来源

- 知乎：AI 工具 / 编程 / 副业 / 效率 话题热文
- 微信公众号：AI 前线、机器之心、量子位等
- 小红书：AI 工具推荐、效率提升、搞钱副业
- GitHub Trending / awesome-lists