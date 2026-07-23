# 数据架构体系化方案

## 问题诊断

经过全面梳理，当前项目数据相关文档存在以下问题：

### 1. 内容重复/重叠（3 组）

| 文件 A | 文件 B | 重叠内容 |
|--------|--------|---------|
| `reference/vendors-and-tools.md` | `project/codingplan-saver/docs/vendors-reference.md` | 都描述厂商、定价 URL、联盟链接，vendors-reference 有更多细节（返佣、结算记录） |
| `reference/data-map.md` | `project/codingplan-saver/data/SCHEMA.md` | 都描述数据文件、字段、更新流程，data-map 偏管道总览，SCHEMA 偏字段定义 |
| `reference/codingplan/README.md` | `project/codingplan-saver/template/index.html` | codingplan/README.md 是 V1 旧版静态页面的原始 Markdown 源，已被新 build 系统替代 |

### 2. 文档散落各处

数据文档分布在 4 个不同目录：
- `reference/` — data-map.md, vendors-and-tools.md
- `project/codingplan-saver/docs/` — vendors-reference.md
- `project/codingplan-saver/data/` — SCHEMA.md
- `reference/codingplan/` — 旧版 V1 站点（整个独立 git 仓库）

### 3. 多项目共享数据，但无统一入口

7 个项目（codingplan-saver, coding-tools, agent-patterns, aicoding-stack, aicoding-tips, ccskills-market, model-picker）共享同一套厂商数据源，但文档没有体现这种共享关系。

### 4. 僵尸文件

- `reference/codingplan/DESIGN.md` — 只有一行 "还是使页面原本的风格"
- `HOT-TREND-REVIEW.md` — 2026-07-21 的一次性 Review，发现的 4 个问题已修复
- `reference/codingplan/` 整个目录 — V1 旧版静态站点的 git 仓库，已归档到 `project/codingplan-saver/archive/`

---

## 方案：三步走

### 第一步：创建统一数据架构文档

**新建 `reference/data-architecture.md`** — 项目数据体系的"总地图"，整合并替代 `data-map.md`。

内容结构：
```
1. 数据全景图（一张图看懂数据从哪来、到哪去）
2. 数据源层（DailyHotApi, RSSHub, 厂商定价页, 手动输入）
3. 采集层（engine.py, sources/*, price_monitor, article_discovery）
4. 存储层（data/raw, data/signals, data/pending, project/*/data/）
5. 消费层（7 个项目 + 各自的 data/*.json）
6. 共享数据模型（vendors, plans, tools 在各项目间的复用关系）
7. 更新流程（自动管道 + Claude Code 审阅 + 手动维护）
8. 已知问题 & 改进计划
```

### 第二步：合并厂商/工具文档

**增强 `reference/vendors-and-tools.md`**，将 `project/codingplan-saver/docs/vendors-reference.md` 的独有内容合并进来：
- 返佣信息（已有但分散）
- 链接格式规范
- 结算记录
- 数据文件映射

合并后 vendors-reference.md 删除。

### 第三步：清理僵尸文档

| 删除文件 | 原因 |
|---------|------|
| `reference/data-map.md` | 被 `data-architecture.md` 替代 |
| `project/codingplan-saver/docs/vendors-reference.md` | 合并到 `reference/vendors-and-tools.md` |
| `reference/codingplan/` 整个目录 | V1 旧版站点，已归档到 `project/codingplan-saver/archive/` |
| `HOT-TREND-REVIEW.md` | 一次性 Review，问题已修复，信息已过时 |
| `project/coding-tools/docs/tracking.md` | 已在 git 中标记删除，确认删除 |

---

## 清理后的文档结构

```
reference/
  data-architecture.md          ← NEW: 数据体系总地图（替代 data-map.md）
  vendors-and-tools.md          ← ENHANCED: 厂商+工具唯一真相源（合并 vendors-reference.md）
  个人使用说明书-v2026.md        ← 保留不变

project/codingplan-saver/
  data/SCHEMA.md               ← 保留：详细字段定义（data-architecture.md 链接到此处）
  docs/                         ← 删除整个目录

HOT-TREND-REVIEW.md             ← 删除
reference/codingplan/           ← 删除整个目录
project/coding-tools/docs/      ← 删除整个目录（tracking.md 已在 git staged 删除）
```

### 文档职责清晰划分

| 文档 | 职责 | 受众 |
|------|------|------|
| `reference/data-architecture.md` | 回答"数据从哪来、怎么存、谁在用" | 新人上手、架构理解 |
| `reference/vendors-and-tools.md` | 回答"有哪些厂商/工具、URL是什么、怎么采集" | 数据维护、新增厂商 |
| `project/codingplan-saver/data/SCHEMA.md` | 回答"plans.json 每个字段什么意思" | 数据更新、代码生成 |
| 各 SKILL.md | 回答"这个技能怎么用" | 日常操作 |
| CLAUDE.md | 回答"项目是什么、怎么跑" | 项目总入口 |

---

## 实施步骤

1. 基于 `reference/data-map.md` 创建 `reference/data-architecture.md`，扩展为完整数据架构
2. 将 `project/codingplan-saver/docs/vendors-reference.md` 的独有内容合并到 `reference/vendors-and-tools.md`
3. 更新 `CLAUDE.md` 和 `codingplan-page/SKILL.md` 中的文档引用路径
4. 删除上述 5 个僵尸/冗余文档/目录
5. Git commit 记录本次清理