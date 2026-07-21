# 🔍 利基分析报告: Claude Code Skills 市场

> 日期: 2026-07-21 | 来源: /scan 热点扫描 → /analyze 深度分析

## 一句话总结

做一个 **Claude Code Skills 精选市场**——和 codingplan-saver 完全相同的模式：信息聚合 → 结构化数据 → 静态页面 → 联盟/付费变现。codingplan-saver 的模板、数据架构、部署流程可以直接复用，MVP 开发时间预计 5-8h。

---

## 需求分析

### 核心需求

Claude Code 用户（开发者和 AI 爱好者）需要知道**哪些 Skills 值得用、怎么用、谁维护的**。当前信息散落在 GitHub、掘金、Reddit、Discord，没有一个集中的评测/推荐平台。

### 需求证据

- **讨论量**: 掘金上 "Claude Code Skills" 相关文章 7 月激增（"手把手带你封装 Claude Code Skill"、"10万人都在用的 top10 skills"、"让 AI 不再凭感觉做事"）
- **社区项目**: GitHub 上已出现 `awesome-claude-code-skills`、`claude-code-skills-marketplace` 等社区仓库
- **搜索趋势**: "Claude Code Skills" 在中文开发者社区从 2026 年 5 月开始有明显搜索量
- **类比验证**: VS Code Extension 市场、Raycast Store、Alfred Workflow 市场——每个开发者工具平台都催生了生态市场

### 目标用户

- 中文 Claude Code 用户（开发者、独立创作者、技术博主）
- 想快速上手 AI 编程的新用户（不知道选什么 Skills）
- 有自己的 Skills 想分享/变现的创作者

---

## 竞争格局

### 已有"竞品"

| 产品 | 类型 | 问题 |
|------|------|------|
| GitHub `awesome-claude-code-skills` | 静态列表 | 无评测、无评分、无中文、无筛选 |
| GitHub `claude-code-skills-marketplace` | 社区仓库 | 非产品化、无 UI、无商业化 |
| 掘金/CSDN 文章 | 内容 | 非结构化、无法检索、时效性差 |
| Claude Code 官方文档 | 官方 | 只教你怎么写，不告诉你哪个好用 |

### 差异化空间

- **中文优先** — 所有内容中文，服务中国开发者
- **结构化评测** — 每个 Skill 有评分、使用场景、优缺点、安装量
- **精选而非海量** — 只推荐经过验证的优质 Skills，不做垃圾场
- **变现路径清晰** — 和 codingplan-saver 一样的联盟+付费群模式

---

## 商业化路径

### 推荐模式

**codingplan-saver 模式的复刻**：

1. 静态 HTML 页面（单文件，和 codingplan-saver 共用模板引擎）
2. 数据驱动（JSON → build.py → dist/）
3. 变现：免费内容 + 付费社群（知识星球 ¥99/年）
4. 流量来源：公众号 7000 粉 + 掘金/知乎分发

### 内容矩阵

- **Skills 排行榜** — 按评分/热度排序
- **场景推荐** — "前端开发必备 5 个 Skills"、"学术写作专用 Skills"
- **每周精选** — 新发现的优质 Skills 简报
- **创作者专区** — 优秀 Skills 作者访谈

### 预估客单价

- 免费层：所有 Skills 信息和评测
- 付费层：知识星球 ¥99/年（精选 Skills 更新 + 使用技巧 + 社群）

---

## 6 维评分

| 维度 | 评分 | 理由 |
|------|------|------|
| 需求真实性 | ⭐⭐⭐⭐ (4) | 社区讨论活跃，已有自发组织的仓库，但付费证据尚弱 |
| 增长潜力 | ⭐⭐⭐⭐⭐ (5) | Claude Code 用户基数快速增长，Skills 生态刚起步 |
| 付费意愿 | ⭐⭐⭐ (3) | 开发者付费意愿中等，但 ¥99/年 知识星球门槛低 |
| 竞争空间 | ⭐⭐⭐⭐ (4) | 现有方案都是 GitHub 仓库，无产品化、无中文、无商业化 |
| 执行可行性 | ⭐⭐⭐⭐⭐ (5) | 复用 codingplan-saver 模板/数据架构，AI 可完成 80%+ |
| 规模化潜力 | ⭐⭐⭐⭐ (4) | Skills 数量增长快，AI 可辅助评测和维护，边际成本低 |
| **综合** | **25/30** | 🟢 强烈推荐 |

---

## 建议

### 🟢 强烈推荐

**理由**: 这是 codingplan-saver 的"姐妹产品"——相同的技术架构、相同的商业模式、相同的目标用户，但赛道不同。codingplan-saver 帮用户选 AI Coding Plan，这个帮用户选 Claude Code Skills。两个产品可以互相导流，形成"AI 编程工具选型"内容矩阵。

### 下一步

1. 在 `project/ccskills-market/` 创建项目骨架
2. 复用 codingplan-saver 的 `build.py` 和模板架构
3. 手动精选 20-30 个优质 Skills，写好评测数据
4. 生成 MVP 页面，发布到公众号测试反馈
5. 如果数据好，加入知识星球变现

### 风险提示

- Claude Code 官方可能推出官方 Skills 市场（但官方市场通常不解决"中文精选"需求）
- Skills 生态可能不够大（目前只有几百个优质 Skills，但增长速度很快）
- 需要持续维护（但 AI 可以承担大部分维护工作）

---

## 附录: 数据信号源

| 信号 | 来源 | 链接 |
|------|------|------|
| 手把手带你封装 Claude Code Skill | 掘金 | — |
| 10万人都在用的 top10 skills | 掘金 | — |
| 让 AI 不再凭感觉做事——Claude Code Skills 的实践与思考 | 掘金 | — |
| Claude Code 之父的夜班 AI 军团 | 51CTO | — |
| 企业 AI 编程落地实践与 Harness 基建 | 51CTO | — |