---
id: claude
name: Claude
logo: Cl
color: "#ec4899"
category: model-maker
country: us
extractStrategy: playwright
extractStatus: ok
massServices: [coding-plan, api-paygo]
notes: Playwright 渲染 claude.com/pricing → 提取套餐价格
url_home: "https://claude.com"
url_pricing: "https://claude.com/pricing"
url_docs: ""
url_api: ""
url_console: ""
services: 
  - 
    type: coding-plan
    status: active
    billingCore: token
    migration: 原生 Token 计量
    plans: 
      - 
        tier: lite
        name: Pro
        monthlyPrice: 20
        currency: $
        monthlyRequests: 未公开
        tokenLimit: 未公开
        measuredMonthlyToken: 416
        rating: 4
        models: [Claude Sonnet 4.6, Claude Opus 4.7, Claude Opus 4.6, Claude Haiku 4.5]
        tags: [模型强]
        bloggerVerdict: 原生 Claude 党的底线选项，第三方 Agent 不可用。
        status: active
      - 
        tier: max
        name: Max
        monthlyPrice: 100
        currency: $
        monthlyRequests: 未公开
        tokenLimit: 未公开
        measuredMonthlyToken: 800
        rating: 4
        models: [Fable, Opus, Sonnet, Haiku]
        tags: [模型强]
        bloggerVerdict: 5x Pro 用量，早鸟优先体验新功能。
        status: active
models: [Claude Haiku 4.5, Claude Opus 4.6, Claude Opus 4.7, Claude Sonnet 4.6, Fable, Haiku, Opus, Sonnet]
---

# Claude

> Playwright 渲染 claude.com/pricing → 提取套餐价格

## 链接

- home: [https://claude.com](https://claude.com)
- pricing: [https://claude.com/pricing](https://claude.com/pricing)

## 服务 / 套餐

### coding-plan

- 状态: active
- 计费: token
- 迁移: 原生 Token 计量

| 档位 | 价格 | 请求数 | 评分 |
|------|------|--------|------|
| Pro | $20 | 未公开 | ⭐⭐⭐⭐ |
| Max | $100 | 未公开 | ⭐⭐⭐⭐ |

## 旗下编程工具

- [[tools/claude-code|Claude Code]]
- [[tools/claude-work|Claude Work]]

## 变更历史

（由 /kb-update review 自动维护）
