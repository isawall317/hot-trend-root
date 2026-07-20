# 🔥 hot-trend

> 从全网热榜中发现**可孵化的 AI GitHub 项目**机会 — 采集 → 洞察 → 评分 → 机会卡。

`hot-trend` 不做舆情监控（那是 [TRENDRADAR](https://github.com/SANSAN0/TRENDRADAR) 干的事），它专注做一件事：**判断一条趋势值不值得花一周时间做成 AI 项目**。

## 它解决什么问题

刷热榜找点子的最大痛点：99% 的"热点"只是噪音。这个工具帮你：

1. **采集** — 一条命令扫 GitHub Trending / Hacker News / V2EX 热门
2. **洞察** — LLM 把热文拆成 9 个字段（底层痛点、AI 增益点、反信号…）
3. **评分** — 6 维度量化打分，把"听起来酷"和"真值得做"分开
4. **沉淀** — 自动生成机会卡（Markdown + YAML），可 git 跟踪、可复盘

## 快速开始

```bash
# 1. 安装（开发模式）
cd tools/hot-trend
pip install -e .

# 2. 配置
cp config.example.yaml config.yaml
cp .env.example .env
# 编辑 .env，填一个 LLM API key（推荐智谱 GLM，国内稳定便宜）

# 3. 扫热榜
hot-trend scan --source github --limit 10
hot-trend scan --source hn --limit 10
hot-trend scan --source v2ex --limit 10

# 4. 分析一条你感兴趣的趋势
hot-trend analyze https://github.com/xxx/yyy
# → 抽取正文 → LLM 洞察 → LLM 评分 → 生成 opportunities/cards/001-xxx.md
```

## 命令

### `scan` — 扫热榜（仅展示）

```bash
hot-trend scan -s github -l 20            # GitHub Trending 前 20
hot-trend scan -s github --language python  # 仅 Python 项目
hot-trend scan -s hn -l 15                 # Hacker News top 15
hot-trend scan -s v2ex -l 15               # V2EX 热门前 15
```

输出 rich 表格：排名 / 标题 / 热度 / URL。看到感兴趣的，复制 URL 跑 `analyze`。

### `analyze` — 深度分析单条 URL

```bash
hot-trend analyze https://github.com/owner/repo
hot-trend analyze https://news.ycombinator.com/item?id=12345
hot-trend analyze https://www.v2ex.com/t/1234567
hot-trend analyze https://zhuanlan.zhihu.com/p/xxx

# 只预览不写盘
hot-trend analyze <url> --no-save
```

**输出**：终端实时进度 + 机会卡预览 + 写入 `opportunities/cards/` 目录。

## 机会卡格式

每张卡是 Markdown + YAML frontmatter：

```markdown
---
id: 001
source: github
source_url: https://github.com/xxx/yyy
discovered_at: 2026-07-20
title: ...
scores:
  demand: 4
  willingness_to_pay: 3
  ai_feasibility: 5
  competition: 3
  dev_cost: 4
  monetization: 4
  total: 23
verdict: 值得孵化
---

# 机会卡 #001：...

## 表面话题
## 底层痛点 ★
## AI 增益点 ★
## 反信号
## 项目雏形
```

**判定阈值**（可在 `config.yaml` 调）：
- ≥ 22：**值得孵化**
- 18-21：**观察**
- < 18：**丢弃**

## 6 维评分模型

| 维度 | 含义 | 5 分 = |
|---|---|---|
| demand | 需求强度 | 痛点，不解决就难受 |
| willingness_to_pay | 付费意愿 | 已有竞品收费 / 评论愿意付 |
| ai_feasibility | AI 可行性 | AI 是核心价值 |
| competition | 竞争（倒扣） | 蓝海，无直接竞品 |
| dev_cost | 开发成本（倒扣） | 1 周内能出 MVP |
| monetization | 变现潜力 | 高客单价或巨量用户 |

## 配置

`config.yaml`：

```yaml
llm:
  provider: zhipu          # zhipu/openai/anthropic/deepseek/kimi/bailian/ark
  model: glm-5.2
  api_key_env: ZHIPU_API_KEY
```

支持的 LLM：
- **智谱 GLM**（国内推荐，稳定便宜）— `glm-5.2`
- **OpenAI** — `gpt-4o-mini`
- **Claude** — `claude-sonnet-4-5`
- **DeepSeek** — `deepseek-chat`
- **Kimi** — `moonshot-v1-32k`
- **阿里百炼** — `qwen-plus`
- **字节火山方舟** — `doubao-pro-32k`

除 Claude 外，全部走 OpenAI 兼容协议，一个 `base_url` 切换。

## 设计理念

### 为什么不直接用 TRENDRADAR？

TRENDRADAR（60k⭐）很强，但它的核心是**舆情简报**（每条新闻打最佳匹配 tag + 叙事性简报），不做：
- 跨条目的**全局可比评分**
- **AI 项目可行性 + 变现**维度的判断
- **孵化决策**的阈值判定

`hot-trend` 把上面三件事做透。两者是互补关系，不是替代。

### 为什么不用 LiteLLM / LangChain？

- LiteLLM 2026.3 有 [供应链投毒事件](https://docs.litellm.ai/blog/security-update-march-2026)，包体 50MB+
- LangChain 对"调一下 LLM"是杀鸡用牛刀
- 国内主流 LLM（GLM/DeepSeek/Kimi/百炼/方舟）**全是 OpenAI 兼容协议**，60 行薄抽象就够

## 路线图

- **P1** ✅ scan（3 源）+ analyze（核心）
- **P2** 中文平台（知乎/微博/B站）接入 + discover 一条龙 + 本地缓存
- **P3** week 周报 + MCP server 暴露 + 测试 + 开源发布
- **P4** ref/ 竞品调研沉淀

## License

MIT
