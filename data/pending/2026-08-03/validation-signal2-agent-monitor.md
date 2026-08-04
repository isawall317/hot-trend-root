# 验证报告 — 信号 2：AI Agent 长任务运行监控 Dashboard

**验证目标**: 来自 `discovery.md` 信号 2（Qwen3.8 16 天自主编程 / Astra 多智能体 / Karpathy 3D 游戏）
**验证时间**: 2026-08-03
**验证方式**: 竞品格局调研（网络检索）

> ⚠️ **数据局限声明**: 各竞品**具体 2026 定价未联网核实**（厂商定价页未抓取），下表定价来自训练数据 + 搜索摘要，标注"未验证"。竞品**格局与形态**来自可核实搜索结果。

---

## Step 2: 竞品深度调研

### A. 通用 Agent / LLM observability（赛道已饱和）

| 竞品 | 产品形态 | 定价（未验证） | 核心功能 | 不足之处 |
|------|----------|---------------|----------|----------|
| **AgentOps** | SDK 接入 + 云仪表盘 | 免费 / Pro ~$20-50/用户/月 | agent trace、session 监控、token、错误率、eval | **要接 SDK**（改代码）；面向"自己造 agent 的团队"，非"用 Claude Code 的个人" |
| **Langfuse** | 开源 + 云 | 自部署免费 / 云 Pro ~$31/月 | LLM trace、成本、prompt 管理、eval | observability 不是"止损/卡死检测"；要接 SDK |
| **LangSmith** | 云 SaaS | Developer 免费 / Plus ~$39/用户/月 | LangChain 生态 trace、dataset 测试 | 绑 LangChain 生态；要接 SDK |
| **Phoenix (Arize)** | 开源本地 + 云 | 开源免费 / 云用量计费 | OTel-native trace、本地跑、eval、幻觉检测 | 要接 SDK；偏调试非运行态监控 |
| **Weave (W&B)** / **Arize** | 云 SaaS | 企业定价 | ML+LLM 监控、漂移检测 | 企业向，重 |

### B. 原生日志读取类（关键发现——赛道已被社区占据一部分）

| 竞品 | 产品形态 | 定价 | 核心功能 | 不足之处 |
|------|----------|------|----------|----------|
| **ccusage** | CLI | 免费（社区） | Claude Code 跨 session token/成本统计 | **已占据"Claude Code 成本追踪"这一块**；无 dashboard、无卡死检测 |
| **ccexplorer / cc-viewer** | CLI/脚本 | 免费（社区） | 解析 Claude Code JSONL 为可读格式 | 只读不分析；社区玩具项目 |
| **Claude Code 内置 `/cost`** | 内置命令 | 免费 | 单 session token 统计 | 单 session、无历史、无卡死检测；但覆盖了"基础成本查看" |
| **Cline task history** | VS Code 面板 | 免费 | 任务历史 + 工具调用序列 | 只覆盖 Cline；无跨工具、无卡死 |
| **Cursor composer logs** | 内置 | 免费 | composer 运行日志 | 只覆盖 Cursor |

### C. 卡死检测（真正的缝隙）

搜索结果明确证实："**log viewing + token burn + stuck loop detection 跨 Claude Code/Cline/Cursor 的统一工具，作为单一产品不存在**"。但：
- Langfuse/Phoenix 等已开始做 `running/paused/stuck/failed` 运行态
- 心跳超时、循环检测、步数预算等**方法已是公开实践**，不是秘密
- 卡死检测是"emerging"（正在被竞品补），不是"没人做"

---

## Step 3: 种子用户验证（未完成）

- ❌ 5118/百度指数：**无法访问**，"agent 监控""Claude Code 卡死"搜索热度未验证
- ✅ 间接证据：AgentOps/Langfuse/Phoenix 的存在 + 融资节奏 = 需求真实，有付费产品
- ❌ 但**关键反证**：需求真实 ≠ 缝隙够大。AgentOps 专做 agent observability 都还在 freemium 挣扎，说明**这个市场付费意愿尚未验证**——典型"有人用、少人付"

---

## Step 4: MVP 范围定义

### 原设想 MVP（discovery.md 里的）
读 Claude Code/Cline 日志 → 实时显示步骤/token 曲线/卡死检测

### 验证后修正：缝隙比预想窄得多

| 预想缝隙 | 验证后真相 |
|---------|-----------|
| "没人做 agent 监控" | ❌ AgentOps/Langfuse/Phoenix 都做，且开源免费 |
| "读本地日志无 SDK" 是差异化 | ⚠️ 真没人做，但 **ccusage 已占据 Claude Code 成本追踪**，cc-viewer 占了日志读取——缝隙被社区工具切成两半 |
| "卡死检测没人做" | ⚠️ 真没人做，但 Langfuse/Phoenix 已在补 `stuck` 状态——窗口期短 |
| "跨工具统一" 是壁垒 | ⚠️ Claude Code/Cline/Cursor 三家日志格式各异且会变，维护成本高，反成负担 |

### 重定位后的可能 MVP（如果硬要做）

#### 必须做
1. 读 Claude Code `~/.claude/projects/*/*.jsonl` → 实时 token 曲线 + 步骤流
2. **卡死循环检测**（同一步骤/工具调用重复 N 次告警）— 唯一真缝隙
3. 微信/飞书推送（卡死即推）

#### 可以不做
1. 跨 Cline/Cursor — 理由：三家日志格式各异，先单 Claude Code
2. Web dashboard — 理由：ccusage 已有 CLI 成本统计，做 UI 没增量
3. eval/trace — 理由：Langfuse/Phoenix 已做透

#### 技术方案
- 形态：ccusage 的 **插件/扩展**（而非独立产品）——承认 ccusage 已占位
- 技术栈：Python，复用本仓库 collector 环境
- AI 可替代：~60%（日志解析样板化，卡死检测算法是核心人工活）
- 预计工时：~8-12h

#### 上线渠道
- 主渠道：GitHub 开源（给 ccusage 提 PR 或 fork）
- 冷启动：Claude Code 中文社区（即刻/微信群）+ V2EX

---

## Step 5: Go/No-Go 决策

## 决策: 🔴 No-Go（作为独立产品）

### 支撑信号（Go 的理由，但都被风险抵消）
- ✅ 痛点真实（agent 越跑越长，卡死是真问题）
- ✅ "卡死检测"确实无成熟独立工具
- ✅ Frank 自己用 Claude Code，是用户

### 风险信号（No-Go 的理由，强）
- 🔴 **赛道比云成本更拥挤**：AgentOps / Langfuse（开源自部署免费）/ Phoenix（开源免费）/ LangSmith / Weave / Arize——开源免费方案密集，付费意愿被严重压缩
- 🔴 **社区工具已占据一半缝隙**：`ccusage` 免费 CLI 已做 Claude Code 成本统计，`cc-viewer`/`ccexplorer` 做日志读取。独立产品的差异化只剩"卡死检测"单点，太薄
- 🔴 **窗口期短**：Langfuse/Phoenix 已在补 `stuck` 运行态，卡死检测正在被主流竞品内化，3-6 个月窗口
- 🔴 **变现极难**：AgentOps 专业做这个都还在 freemium 挣扎（"有人用少人付"）；Langfuse 自部署免费——开源竞品把价格锚在 0
- 🔴 **跨工具日志格式维护负担**：Claude Code/Cline/Cursor 各改版一次就要跟，单人 5-10h/周 维护不动
- 🔴 **厂商原生 UI 在补**：Claude Code `/cost`、Cline task history 已覆盖基础需求，留给独立工具的空间被持续压缩

### 与信号 1 的对比（决定 No-Go 的关键）

| 维度 | 信号 1（AI API 花销 guard） | 信号 2（Agent 监控 dashboard） |
|------|----------------------------|------------------------------|
| 赛道拥挤度 | 中（云成本饱和但 AI API 段空） | **高（agent observability 开源免费密集）** |
| 差异化缝隙 | 大（轻量纯告警 + 读 Claude Code 日志无人做） | **窄（ccusage 已占半，剩卡死检测单点）** |
| 变现可能 | 有（托管 SaaS 层可付费） | **弱（开源竞品锚价 0）** |
| 厂商威胁 | 中（AWS 官方不够好） | **高（Langfuse/Phoenix 在补 stuck）** |

→ 信号 1 的缝隙明显更宽、变现路径更清晰。**资源应集中在信号 1，不该分到信号 2。**

### 如果 No-Go
- **原因**: 赛道拥挤（开源免费方案密集）+ 社区工具已占半缝隙 + 卡死检测窗口期短 + 变现锚在 0；作为独立产品无商业可行性
- **存档**: 本报告即机会卡，存于 `data/pending/2026-08-03/`，归入待观察池
- **未来重启条件**（三选一触发可重评）:
  1. 卡死检测在主流竞品里**仍未被解决**且 Frank 自己每周都被 Claude Code 卡死折磨（验证需求未满足）
  2. ccusage 停止维护或明确不做卡死检测（缝隙重新打开）
  3. 出现新的 agent 运行时（非 Claude Code/Cline/Cursor）日志标准化且无现成监控（新平台空白期）

---

## 总结

验证前以为信号 2"市场早期但新"——验证后修正：**agent observability 不是早期，是中后期且开源方案密集**。真正的早期窗口（Langfuse/Phoenix 出现前）已过，现在是"缝隙被切成片、付费意愿被免费锚住"的阶段。

**Frank 的资源应全部压到信号 1**（AI API 花销 guard），信号 2 归档待观察。两个信号共享的"Claude Code 日志读取"技术，在信号 1 里是读 token 烧速（读同一份 jsonl），不浪费。
