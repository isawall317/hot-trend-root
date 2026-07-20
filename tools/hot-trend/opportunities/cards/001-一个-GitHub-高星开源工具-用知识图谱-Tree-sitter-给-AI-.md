---
id: 001
source: manual
source_url: "https://github.com/tirth8205/code-review-graph"
discovered_at: 2026-07-20
title: 一个 GitHub 高星开源工具，用知识图谱+Tree-sitter 给 AI 编程助手做精准上下文压缩
scores:
  demand: 4
  willingness_to_pay: 4
  ai_feasibility: 4
  competition: 2
  dev_cost: 2
  monetization: 3
  total: 19
verdict: 观察
---

# 机会卡 #001：一个 GitHub 高星开源工具，用知识图谱+Tree-sitter 给 AI 编程助手做精准上下文压缩

> 来源：[manual](https://github.com/tirth8205/code-review-graph) · 评分 **19/30** · 判定：**观察**

## 表面话题
一个 GitHub 高星开源工具，用知识图谱+Tree-sitter 给 AI 编程助手做精准上下文压缩

## 底层痛点 ★
开发者用 Claude Code/Cursor 等 AI 工具做 code review 或大仓库任务时，每次都要重新喂大量代码，token 烧得飞快而且慢——他们真正愁的是"如何让 AI 只读该读的代码"，从而省钱、提速、提高 review 质量

- **痛点频率**：日常
- **目标人群**：重度使用 Claude Code / Cursor / Copilot 处理中大型代码库（500+ 文件）的个人开发者和小团队，已在 AI coding 工具上每月花 $20–$200+ 的订阅
- **现有方案**：忍着烧 token、靠人工挑选文件贴给 AI、或自己写临时脚本切分上下文；少数人尝试社区里的 ckg 等类似工具但配置门槛高
- **付费信号**：强信号：21k stars 说明开发者普遍关心 token 成本；同类竞品如 Augment Code、Codegen、Greptile 都做托管 SaaS 并成功融资；GitHub 评论区常见"愿意付费换托管版"

## AI 增益点 ★
推理 + 自动化：用静态分析（图遍历+blast radius）自动决定"这次 review 该喂哪些文件"，本质是 AI 的上下文工程优化；外加理解（图谱+Tree-sitter 把代码结构化），属于 AI 增益极强的方向

## 反信号
赛道已有 21k stars 开源标杆，复制难度低；上游 MCP 协议和 IDE 平台规则变动频繁，维护成本高；token 成本本身在快速下降（模型变便宜、上下文窗口变大），长期价值可能被通胀侵蚀

## 项目雏形
### 1. Hosted CRG Cloud

code-review-graph 的托管版：用户 GitHub App 授权后无需本地 Python/Tree-sitter，web 端提供 blast radius 可视化、按文件风险排序的 PR review 报告，按 repo 数量订阅 $19/mo 起；差异化在零配置和企业审计日志

### 2. PR Review Risk Bot

GitHub App，在每个 PR 上自动跑增量图谱，评论里只列出真正会被影响的下游文件 + 风险评分（变更文件 × 调用方数量 × 测试覆盖率），帮 reviewer 聚焦；免费 5 个 repo，超出按 PR 次数付费

### 3. TokenLens for Claude Code

桌面端 CLI 包装，实时统计每次 /review 命令实际消耗的 token、其中"浪费"在重复/无关代码的比例，给出省钱建议（如改用图谱模式可省 X%）；面向预算敏感 solo developer，$5/mo


## 评分理由
最强项是付费意愿真实且有竞品融资验证；最弱项是竞争激烈（21k stars + Greptile/Augment/Codegen 已占位），且图谱+Tree-sitter+MCP 维护成本高，MVP 至少需要数周才能跑通。

| 维度 | 分数 |
|---|---|
| 需求强度 | 4/5 |
| 付费意愿 | 4/5 |
| AI 可行性 | 4/5 |
| 竞争(倒扣) | 2/5 |
| 开发成本(倒扣) | 2/5 |
| 变现潜力 | 3/5 |
| **总分** | **19/30** |
