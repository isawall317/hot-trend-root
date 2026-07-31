# 🔍 验证报告 — Claude Code Skills 卫生与垂直套件

> 日期: 2026-07-31 | 来源: /discover 信号 1（8/10）→ /validate
> 验证对象: "Claude Code Skills 卫生工具 + 垂直套件商店"（discovery 评分 8/10）

---

## 一句话结论

**🟡 观望**。原 8/10 评分是在未查竞品时给出的；深度调研后竞品格局远比预想拥挤——官方目录已下场、cc-switch（12.2 万⭐）已是 skills 管理事实标准、marketingskills（4.2 万⭐）已验证垂直套件模式且有成熟变现。Frank 5-10h/周后发劣势明显。但有一个窄切口仍可小规模试：**中文垂直套件**（不是市场、不是卫生工具）。

---

## Step 2: 竞品深度调研

| 竞品 | 形态 | Stars | 定价 | 核心功能 | 不足之处 |
|------|------|-------|------|---------|----------|
| **anthropics/claude-plugins-official** | 官方目录 | 32.9k⭐ | 免费 | Anthropic 官方维护的高质量 plugin/skill 目录，指向 code.claude.com | 偏英文、偏 plugin、不做深度评测、"权威性"碾压后发者 |
| **farion1231/cc-switch** (ccswitch.io) | 桌面 app (Tauri) | **122.7k⭐** | MIT 免费 | skills 安装/部署/同步/备份/配置管理（CRUD）+ 跨多 agent 同步 + API 成本追踪 | ❌ 不做健康度诊断（过期/使用频率/烧钱归因）；但随时可加 |
| **hesreallyhim/awesome-claude-code** | 静态列表 | 51.4k⭐ | 免费 | 社区精选 skills/agents/statuslines/plugins | 无评测、无结构化、无中文、无变现 |
| **coreyhaines31/marketingskills** (marketing-skills.com) | 垂直套件 | 42.5k⭐ | MIT 免费 | 营销 skills 套件（CRO/copywriting/SEO/analytics） | 仅英文营销场景；变现靠引流到作者付费产品，非套件本身收费 |

### 关键洞察

1. **官方已下场**：`anthropics/claude-plugins-official` 3.3 万⭐——"中文精选市场"的权威性差异化被严重削弱
2. **cc-switch 是 skills 管理事实标准**：12.2 万⭐、MIT 免费、topics 明确含 `skills-management`。虽不做"健康度诊断"，但它有"Usage & Cost Tracking"基础，加这个功能是举手之劳——**后发者没有时间窗口**
3. **"垂直套件"模式已被 marketingskills 验证且做大**：42.5k⭐，但它变现不在套件本身（免费开源），靠引流到创作者的付费产品（代理/培训/Magister AI CMO）——**这与 Frank 的"睡后收入"期望有偏差**

### "Skills 卫生"差异化空间的残酷现实

discovery 阶段判断 cc-switch 不做健康度诊断 = 差异化窗口。validate 后发现问题：

- **"过期检测"技术可行性被高估**：skills 是自然语言 Markdown，没有 npm 那种明确的"废弃 API"信号。判断一个 skill"过期"需要语义理解它是否还匹配当前 Claude Code 行为——这本身就是个 AI 难题，不是确定性检测
- **"烧钱归因"cc-switch 已有基础**：它的 Usage & Cost Tracking 在 API 层面，扩展到 skills 维度是增量工作
- **12 万⭐的护城河**：即使 Frank 先做出健康度报告，cc-switch 一个月内就能复制并免费提供，用分发优势碾压

---

## Step 3: 种子用户验证方案（供 Frank 执行）

validate 无法只靠桌面调研定生死，建议本周做这个 30 分钟测试：

**公众号探针帖**（你 7000 粉就是实验室）：
1. 写一篇《我装了 47 个 Claude Code skills，A 社建议我删 80%》
2. 文末提问："你最头疼的是哪个 skill 问题？A. 找不到 B. 不知道哪些过期 C. 烧钱 D. 不会用"
3. 看 48h 内：阅读完成率、评论里高频痛点是什么

**判读标准**：
- 如果评论高频是 **B/C（过期/烧钱）** → 卫生工具有真实需求，值得对抗 cc-switch 做
- 如果高频是 **A/D（找不到/不会用）** → 那是"精选市场"需求，但官方目录已占，放弃
- 如果互动惨淡 → 整个赛道对中文用户太早，观望

---

## Step 4: MVP 范围定义（仅当种子验证 B/C 痛点为真）

### 唯一可行切口：中文垂直套件（不是市场、不是卫生工具）

放弃"skills 卫生"和"精选市场"，只做**中文场景垂直套件**——marketingskills 做英文营销，中文场景（公众号/小红书/知乎）空白。

### 必须做（核心价值）
1. **"公众号内容虾"套件**（5-8 个 skills：选题→大纲→配图→排版→多平台发布）— 理由：你是用户 + 7000 粉分发
2. 套件以 SKILL.md 集合形式发布（GitHub repo + 公众号文章导流）— 理由：零服务器成本，符合 5-10h/周
3. 每个 skill 附带"中文场景适配说明"（marketingskills 缺的）— 理由：这是唯一能和 4.2 万⭐头部差异化的点

### 可以不做（等验证后再加）
1. 卫生工具/健康度报告 — cc-switch 已有基础，后发无窗口
2. 精选市场/排行榜 — 官方目录已占权威位
3. 桌面 app — 12 万⭐ cc-switch 已是事实标准，不要正面碰

### 技术方案
- 形态: GitHub repo（SKILL.md 集合）+ 静态介绍页（复用 codingplan build.py）
- 技术栈: Markdown + 现有 builder
- AI 可替代: 80%（skills 内容由 AI 起草，你审阅）
- 预计工时: MVP 8-12h（1-2 周）

### 上线渠道
- 主渠道: GitHub + 公众号推文
- 冷启动: 你 7000 粉公众号发《我做了个公众号内容虾》+ 掘金/V2EX 分发

---

## Step 5: Go/No-Go 决策

## 决策: 🟡 观望（原 8/10 → 修正为 5/10）

### 支撑信号（做的话理由）
- ✅ 痛点真实：A 社自己删 80% skills、Harness 半年保质期、烧钱——这些证据是真的
- ✅ 垂直套件模式被 marketingskills 验证可行（42.5k⭐）
- ✅ Frank 有 7000 粉分发 + 自己是用户
- ✅ 中文场景套件是 marketingskills 没覆盖的窄空白

### 风险信号（不做的理由）
- ⚠️ 官方 anthropics 已下场做目录（3.3 万⭐），权威性打不过
- ⚠️ cc-switch 12.2 万⭐是 skills 管理事实标准，卫生功能它随时可加，后发无窗口
- ⚠️ marketingskills 4.2 万⭐已占垂直套件头部，且变现靠引流非睡后收入
- ⚠️ "skills 卫生"技术可行性被高估（过期检测是 AI 难题非确定性检测）
- ⚠️ 中文 Claude Code 用户基数仍小（虽重度用户高净值）

### 如果 Go（仅在 Step 3 种子验证 B/C 痛点为真时）
1. 下一步动作: 公众号发探针帖（30 分钟），48h 后看评论
2. 预计 MVP 上线时间: 验证通过后 2 周内（公众号内容虾套件）
3. 成功标准: 套件 GitHub 100⭐ 或公众号帖 50+ 互动，再投入做第二套件

### 如果 No-Go（种子验证互动惨淡 / 高频痛点是 A/D）
- 原因: 赛道拥挤（官方+12 万⭐+4.2 万⭐头部），中文用户太早，后发劣势
- 存档: 本报告存入 data/cards/，ccskills-market 项目冻结
- 备选: 回头看 7-24 的"抄袭监测 8/10"——那个赛道竞品格局本报告未调研，可能更值得

---

## 修正声明

**本验证报告修正了 discovery 报告的 8/10 评分。** discovery 阶段证据强度（10+ 条跨源）是真的，但"证据强度"不等于"竞争空间"——热点讨论多 ≠ 付费需求强 ≠ 有差异化窗口。validate 的价值就在这里：用 30 分钟竞品调研，避免在一个 12 万⭐玩家 + 官方已下场的赛道投入 5-10h/周。

**Pipeline A 闭环价值**：这是该系统第一次走完 discover → validate 完整链路。即使结论是 🟡 观望，也比 7-24 停在"建议进 validate"有价值——No-Go/观望本身是有效产出。
