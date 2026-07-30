---
name: discover
description: 需求发现 — 从全网热点中用 LLM 语义扫描，识别可产品化的需求信号
metadata:
  type: skill
---

# /discover — 需求发现（Pipeline A）

## 触发

- `/discover` — 全流程：采集 → 预过滤 → LLM 语义扫描 → 生成报告
- `/discover scan` — 扫描模式：只跑预过滤 + LLM 扫描，不采集新数据
- `/discover input` — 只生成输入文件（discovery-input.json），不调 LLM

## 定位

**Use Case 1: 热点 → 需求发现 → 新项目**

与 `/codingplan-page`（Use Case 2: 已有项目维护）并列。
这条管线只回答"今天有什么值得做的新东西？"，不维护任何已有产品。

## 核心原则

- **不做关键词匹配** — 关键词无法预知新需求，让 LLM 理解语义
- **面向"需求缺口"** — 不是新闻摘要，而是"哪个需求没被满足"
- **可产品化导向** — 只输出 5-10h/周 + AI 能撬动的方向
- **不与维护管线抢任务** — CodingPlan/Tools 的更新走 `/codingplan-page`

---

## 工作流

### 模式 1: `discover` — 全流程

#### Step 1: 跑数据采集

```bash
cd tools/collector && uv run python -m collector.pipeline
```

确保 `data/raw/{date}/` 有今天的原始数据。

#### Step 2: 跑预过滤

```bash
cd tools/collector && uv run python -m collector.discovery_prefilter
```

输入: `data/raw/{date}/*.json` (1200+ 条)
输出: `data/pending/{date}/discovery-input.json` (top 300 条)

预过滤做了什么：
- 过滤来源：只保留 tech / news / social（去掉 game/content/other）
- 标题去重：相似度 > 0.8 视为同一事件
- 按热度排序：取前 300

**预过滤不做关键词匹配** —— LLM 自己判断相关性。

#### Step 3: LLM 语义扫描（Claude Code 执行）

读取 `data/pending/{date}/discovery-input.json`，按以下 prompt 进行语义扫描：

```
你是 AI 利基发现助手。读取 discovery-input.json 中的 300 条今日热点，
从中识别 3-5 个"可产品化的需求缺口"。

判断标准：
1. 不是新闻本身，而是新闻背后的需求（为什么这么多人讨论？）
2. 是否能用 AI + 小软件产品解决？
3. 5-10h/周 + 睡后收入模式是否可行？
4. 国内可做、合规无雷区

输出格式（JSON 数组）：
[{
  "signal_title": "一句话概括的需求",
  "evidence_count": 命中该需求的热点数,
  "evidence_examples": ["标题1", "标题2", "标题3"],
  "underlying_need": "底层需求（不是产品形态）",
  "target_user": "谁会付费",
  "ai_solution": "AI 能做什么、剩下要做什么",
  "mvp_shape": "MVP 大致形态（1-2 句话）",
  "feasibility_score": 1-10,
  "monetization": "可能的变现路径",
  "risks": ["风险1", "风险2"]
}]

只输出 feasibility_score >= 6 的信号。
不要为了凑数输出低质量信号，宁可少输出。
```

#### Step 4: 写入发现报告

LLM 扫描结果写入 `data/pending/{date}/discovery.md`：

```markdown
# 需求发现报告 — 2026-07-24

**扫描时间**: 2026-07-24 14:30
**输入规模**: 300 条（tech/news/social 来源，已去重）
**LLM 评分阈值**: ≥ 6/10

---

## 🔥 信号 1: AI 短剧出海工具链

**底层需求**: 国内短剧团队想出海，但不懂外语 + 海外分发
**目标用户**: 短剧制作团队（2000+ 家）
**AI 解决方案**: AI 翻译 + 配音 + 字幕 + 分发适配
**MVP 形态**: 上传短剧 → AI 一键生成 TikTok/YouTube 适配版本
**可行性**: 8/10
**变现**: SaaS ¥99/月 / 翻译按次计费
**风险**: 短剧行业波动 / 海外分发合规

**证据热点** (3 条):
- [36氪] AI 短剧出海月入百万，新工具走红
- [微博] 短剧团队招不到外语翻译
- [V2EX] 自建短剧出海流水线分享

---

## 🔥 信号 2: ...

---

## 下一步

- 值得做的 → 进 `/validate` 深度验证
- 不值得做的 → 跳过，下周再看
```

#### Step 5: 汇报

输出信号摘要，询问 Frank "哪些值得深挖？"

---

### 模式 2: `discover scan` — 只跑扫描

适用: 今天已经跑过 pipeline，只需要 LLM 重新扫描

```bash
cd tools/collector && uv run python -m collector.discovery_prefilter
# 然后 Claude Code 执行 Step 3-5
```

---

### 模式 3: `discover input` — 只生成输入

适用: 调试 / 想看预过滤效果 / 手动挑数据

```bash
cd tools/collector && uv run python -m collector.discovery_prefilter
```

只生成 `discovery-input.json`，不调 LLM。

---

## 与其他 Skill 的关系

| 场景 | 用哪个 |
|------|--------|
| 发现新需求 → 评估做不做 | `/discover` (这个 skill) |
| 决定做了 → 深度分析 | `/analyze` |
| 决定做了 → 验证 MVP | `/validate` |
| 维护 CodingPlan 数据 | `/codingplan-page` (Pipeline B) |
| 同步厂商/工具信息 | `/kb-update` |

## 输入文件

`discovery-input.json` 结构：
```json
{
  "date": "2026-07-24",
  "total": 300,
  "filter": "discovery_prefilter",
  "items": [
    {
      "title": "...",
      "url": "...",
      "source": "dailyhot:36kr",
      "hot_metric": "1.2万",
      "source_type": "tech",
      "description": "..."
    }
  ]
}
```

## 输出文件

`discovery.md`（人工审阅后决定后续动作）

## 边界规则

- 不维护已有产品（那是 `/codingplan-page` 的活）
- 不直接产出 changes.json（需求未验证，不算确定变更）
- 不自动触发 build / deploy（需要人工决策）
- LLM 评分阈值 ≥ 6/10，宁缺毋滥