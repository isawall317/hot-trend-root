---
id: github
name: GitHub
logo: GH
color: "#71717B"
category: aggregator
country: us
extractStrategy: playwright
extractStatus: ok
massServices: [coding-plan, token-plan]
notes: Playwright 渲染 github.com/features/copilot/plans → 提取套餐价格
url_home: "https://github.com"
url_pricing: "https://github.com/features/copilot/plans"
url_docs: ""
url_api: ""
url_console: ""
services: 
  - 
    type: token-plan
    status: active
    billingCore: token
    plans: 
      - 
        tier: lite
        name: Free
        monthlyPrice: 0
        currency: $
        monthlyRequests: 未公开
        tokenLimit: 未公开
        rating: 5
        models: [GPT-5.2-Codex, GPT-4.1, GPT-5-mini, Gemini 3.1 Pro, Claude Haiku 4.5]
        tags: [性价比高, 学生认证]
        bloggerVerdict: 学生党白嫖神器，认证后高级模型 300 次。
        status: active
  - 
    type: coding-plan
    status: active
    billingCore: token
    migration: 原生 Token 计量
    plans: 
      - 
        tier: lite
        name: Copilot Pro
        monthlyPrice: 10
        currency: $
        monthlyRequests: 未公开
        tokenLimit: 未公开
        measuredMonthlyToken: 30
        rating: 3
        models: [GPT-5.3-Codex, GPT-5.4, Claude Sonnet 4.6, Gemini 3.1 Pro]
        tags: [模型强]
        bloggerVerdict: $10 拿到主流模型全家桶，海外账号党推荐。
        status: active
      - 
        tier: pro
        name: Pro+
        monthlyPrice: 39
        currency: $
        monthlyRequests: 未公开
        tokenLimit: 未公开
        measuredMonthlyToken: 200
        rating: 4
        models: [GPT-5.2-Codex, Opus, GPT-5.1, Gemini 3.1 Pro]
        tags: [模型强]
        bloggerVerdict: 含 Opus 模型，重度用户升级首选。
        status: active
      - 
        tier: max
        name: Max
        monthlyPrice: 100
        currency: $
        monthlyRequests: 未公开
        tokenLimit: 未公开
        measuredMonthlyToken: 500
        rating: 4
        models: [GPT-5.2-Codex, Opus, GPT-5.1, Gemini 3.1 Pro]
        tags: [模型强, 性价比高]
        bloggerVerdict: 最高用量，适合重度 Agent 工作流。
        status: active
models: [Claude Haiku 4.5, Claude Sonnet 4.6, GPT-4.1, GPT-5-mini, GPT-5.1, GPT-5.2-Codex, GPT-5.3-Codex, GPT-5.4, Gemini 3.1 Pro, Opus]
---

# GitHub

> Playwright 渲染 github.com/features/copilot/plans → 提取套餐价格

## 链接

- home: [https://github.com](https://github.com)
- pricing: [https://github.com/features/copilot/plans](https://github.com/features/copilot/plans)

## 服务 / 套餐

### token-plan

- 状态: active
- 计费: token

| 档位 | 价格 | 请求数 | 评分 |
|------|------|--------|------|
| Free | $0 | 未公开 | ⭐⭐⭐⭐⭐ |

### coding-plan

- 状态: active
- 计费: token
- 迁移: 原生 Token 计量

| 档位 | 价格 | 请求数 | 评分 |
|------|------|--------|------|
| Copilot Pro | $10 | 未公开 | ⭐⭐⭐ |
| Pro+ | $39 | 未公开 | ⭐⭐⭐⭐ |
| Max | $100 | 未公开 | ⭐⭐⭐⭐ |

## 旗下编程工具

- [[tools/github-copilot|GitHub Copilot]]

## 变更历史

（由 /kb-update review 自动维护）
