# Hot Trend — AI 利基发现与变现系统

## 系统定位

从全网热点中自动发现**细分赛道利基** → AI 深度分析 → 快速验证 → 小软件产品变现。

**我不是在找热点新闻，而是在找可商业化的需求缺口。**

## 架构

```
Docker 采集层              Claude Code 分析层              执行层
DailyHotApi (40+平台)  →   /scan 热点扫描     →   机会卡
RSSHub (500+源)        →   /analyze 利基分析  →   /validate 验证
     ↓                      ↓                      ↓
Python collector 归一化     Claude Code 直接读取     Claude Code 开发产品
     ↓
data/raw/YYYY-MM-DD/*.json
```

## 技能

### /build-site — 生成 CodingPlan 省钱攻略 HTML

一键运行数据管道 + 生成最终交付物。

```bash
# 更新数据 + 生成页面
cd tools/collector && source .venv/bin/activate && python -m collector.pipeline
cd tools/builder && python3 build_html.py
# 输出: dist/codingplan-saver.html
```

详见 `.claude/skills/build-site.md`

## 目录结构

```
hot-trend-root/
├── CLAUDE.md                  # 本文件
├── docker-compose.yml         # 数据采集服务
├── .claude/
│   ├── skills/                # Claude Code skills
│   │   ├── scan.md            # 热点扫描 + 初筛
│   │   ├── analyze.md         # 利基深度分析 + 6维评分
│   │   └── validate.md        # 快速验证 + Go/No-Go
│   └── workflows/
├── tools/
│   └── collector/             # Python 数据采集聚合器
│       ├── collector/
│       │   ├── engine.py      # 采集引擎
│       │   └── storage.py     # 存储/读取
│       └── pyproject.toml
├── data/
│   ├── raw/                   # 原始采集数据（.gitignore）
│   ├── cards/                 # 机会卡（git 跟踪）
│   └── archive/               # 历史归档
├── reference/                 # 用户画像/参考资料
└── project/                   # 已孵化项目
```

## 日常使用流程

### 1. 启动采集服务（一次性）
```bash
docker compose up -d
```

### 2. 采集数据（每天 2-3 次，或 CronCreate 定时）
```bash
cd tools/collector && python -m collector.engine
```

### 3. 使用 Claude Code 分析
- 说 `/scan` 或 "扫描一下最近热点" → 自动读取 data/raw/ 最新数据，聚类筛选
- 说 `/analyze` 或 "分析这个利基" → 对感兴趣的信号做深度分析+评分
- 说 `/validate` 或 "验证这个方向" → 竞品调研+种子验证+Go/No-Go

### 4. 开发产品
- 机会卡进入 🟢 开发中 → Claude Code 直接开发 MVP
- 目标：每个 MVP 不超过 10h AI 辅助开发时间

## 用户画像（Frank）

- 公众号 7000 粉，前 AI+知识管理+读书赛道
- 盖洛普 Top 5: 交往(1) 学习(2) 理念(3) 完美(4) 成就(5)
- 0→1 构想是超能力，执行跟进是盲点
- 偏好：睡后收入（小软件产品），5-10h/周
- 商业逻辑优先，AI 补齐能力短板
- 国内优先，不碰灰产/合规雷区/重运营

## 利基评估标准（6 维评分）

每次分析机会时，按以下 6 个维度打分（1-5）：

1. **需求真实性** — 有真实用户在找解决方案吗？（搜索量、讨论热度、付费证据）
2. **增长潜力** — 赛道在增长吗？是新需求还是存量竞争？
3. **付费意愿** — 用户愿意为这个付多少钱？有付费替代品吗？
4. **竞争空间** — 有没有差异化空间？还是巨头林立？
5. **执行可行性** — AI 能帮我做多少？技术难度？时间投入？
6. **规模化潜力** — 能做成睡后收入吗？还是需要持续运营？

## 关键原则

- **需求优先** — 先确认有人在找解决方案，再考虑怎么解决
- **AI 撬动** — 每个环节问"AI 能做多少？我只需要做什么？"
- **快速验证** — 不要完美，先验证再打磨
- **数据驱动** — 让采集数据说话，不做主观判断