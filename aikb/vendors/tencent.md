---
id: tencent
name: 腾讯云
logo: 腾
color: "#eab308"
category: cloud-maas
country: cn
extractStrategy: bs4
extractStatus: ok
lastVerified: 2026-07-21
massServices: [coding-plan, token-plan, api-paygo]
notes: httpx + BS4 解析 Coding Plan 文档
url_home: "https://cloud.tencent.com/product/tokenhub"
url_pricing: "https://cloud.tencent.com/product/tokenhub?Is=home"
url_docs: ""
url_api: ""
url_console: ""
services: 
  - 
    type: coding-plan
    status: active
    billingCore: token
    migration: ✅ 已切换 Token Plan
    plans: 
      - 
        tier: pro
        name: Pro
        monthlyPrice: 200
        currency: ¥
        monthlyRequests: 90000
        tokenLimit: 100M Tokens
        measuredMonthlyToken: 600
        rating: 3
        models: [GLM-5.1, Kimi-K2.5, MiniMax-M2.7]
        tags: [模型强, 兼容 Claude Code]
        bloggerVerdict: TokenHub Token Plan，比 API 按量便宜 50-80%。100M Token 仅 200 轮问答，性价比偏低。
        status: active
      - 
        tier: lite
        name: Lite
        monthlyPrice: 40
        currency: ¥
        monthlyRequests: 18000
        measuredMonthlyToken: 120
        rating: 3
        models: [DeepSeek-V4, GLM-5.2]
        tags: [性价比高, 无需抢购]
        bloggerVerdict: 入门便宜，适合轻度用户。
        status: active
models: [DeepSeek-V4, GLM-5.1, GLM-5.2, Kimi-K2.5, MiniMax-M2.7]
---

# 腾讯云

> httpx + BS4 解析 Coding Plan 文档

## 链接

- home: [https://cloud.tencent.com/product/tokenhub](https://cloud.tencent.com/product/tokenhub)
- pricing: [https://cloud.tencent.com/product/tokenhub?Is=home](https://cloud.tencent.com/product/tokenhub?Is=home)

## 服务 / 套餐

### coding-plan

- 状态: active
- 计费: token
- 迁移: ✅ 已切换 Token Plan

| 档位 | 价格 | 请求数 | 评分 |
|------|------|--------|------|
| Pro | ¥200 | 90000 | ⭐⭐⭐ |
| Lite | ¥40 | 18000 | ⭐⭐⭐ |

## 旗下编程工具

- [[tools/codebuddy|CodeBuddy]]

## 变更历史

（由 /kb-update review 自动维护）
