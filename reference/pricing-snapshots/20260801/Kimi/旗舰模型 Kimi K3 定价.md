---
title: "旗舰模型 Kimi K3 定价"
source: "https://platform.kimi.com/docs/pricing/chat-k3"
author:
published:
created: 2026-08-01
description: "Kimi API 开放平台，提供 Kimi K3 大模型 API，1M token 超长上下文、多模态理解与 Tool Calling。专业代码生成、智能对话、视觉推理，助力开发者构建下一代 AI 应用。"
tags:
  - "来源/clippings"
---
## 产品定价

| 模型 | 计费单位 | 输入价格（缓存命中） | 输入价格（缓存未命中） | 输出价格 | 上下文窗口 |
| --- | --- | --- | --- | --- | --- |
| kimi-k3 | 1M tokens | ¥2.00 | ¥20.00 | ¥100.00 | 1,048,576 tokens |

此处 1M = 1,000,000，表格中的价格代表每消耗 1M tokens 的价格。

## 模型说明

联网搜索（ `web_search` ）正在更新升级中，近期不建议使用该功能，当前文档已经过时，请关注后续内容更新。

- Kimi K3 是 Kimi 的旗舰模型，面向长程编程与端到端知识工作，1M token 上下文，综合智能达到领先水平，详见 [Kimi K3 模型介绍](https://platform.kimi.com/docs/guide/kimi-k3-quickstart)
- 始终进行推理，支持通过请求顶层 `reasoning_effort` 配置推理强度（ `low` / `high` / `max` ，默认 `max` ），详见 [推理强度](https://platform.kimi.com/docs/guide/use-reasoning-effort)
- 支持 [自动上下文缓存](https://platform.kimi.com/docs/guide/use-context-caching-feature-of-kimi-api) 、 [工具调用（ToolCalls）](https://platform.kimi.com/docs/guide/use-kimi-api-to-complete-tool-calls) 、 [JSON Mode](https://platform.kimi.com/docs/guide/use-json-mode-feature-of-kimi-api) 、 [结构化输出（ `response_format` / JSON Schema）](https://platform.kimi.com/docs/guide/response_format) 、 [Partial Mode](https://platform.kimi.com/docs/guide/use-partial-mode-feature-of-kimi-api) 、 [联网搜索](https://platform.kimi.com/docs/guide/use-web-search) 等能力
- K3 新增 API 能力： [工具调用约束（ `tool_choice` ）](https://platform.kimi.com/docs/guide/use-tool-choice) 、 [动态加载工具](https://platform.kimi.com/docs/guide/use-dynamic-tool-loading) ，组合用法见 [K3 工具调用最佳实践](https://platform.kimi.com/docs/guide/kimi-k3-tool-calling-best-practice)