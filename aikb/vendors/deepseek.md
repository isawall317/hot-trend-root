---
id: deepseek
name: DeepSeek 官方
logo: D
color: "#71717B"
category: model-maker
country: cn
extractStrategy: bs4
extractStatus: ok
lastVerified: 2026-07-21
massServices: [api-paygo]
notes: httpx + BS4 解析 API 定价
url_home: "https://api-docs.deepseek.com"
url_pricing: "https://api-docs.deepseek.com/quick_start/pricing"
url_docs: "https://api-docs.deepseek.com/quick_start/pricing"
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
        name: 虚拟套餐 40
        monthlyPrice: 40
        currency: ¥
        monthlyRequests: 无限制
        tokenLimit: 105M Tokens
        measuredMonthlyToken: 105
        rating: 4
        models: [DeepSeek-V4-Flash, DeepSeek-V4-Pro, deepseek-v4-pro]
        tags: [性价比高, 无需抢购]
        bloggerVerdict: 原生 DeepSeek-V4-Pro，¥40 估算 105M Token，7 月起高峰翻倍。
        status: active
      - 
        tier: pro
        name: 虚拟套餐 200
        monthlyPrice: 200
        currency: ¥
        monthlyRequests: 无限制
        tokenLimit: 527M Tokens
        measuredMonthlyToken: 527
        rating: 4
        models: [DeepSeek-V4-Flash, DeepSeek-V4-Pro, deepseek-v4-pro]
        tags: [性价比高, 无需抢购]
        bloggerVerdict: 原生 DeepSeek 重度档，527M Token。
        status: active
models: [DeepSeek-V4-Flash, DeepSeek-V4-Pro]
---

# DeepSeek 官方

> httpx + BS4 解析 API 定价

## 链接

- home: [https://api-docs.deepseek.com](https://api-docs.deepseek.com)
- pricing: [https://api-docs.deepseek.com/quick_start/pricing](https://api-docs.deepseek.com/quick_start/pricing)
- docs: [https://api-docs.deepseek.com/quick_start/pricing](https://api-docs.deepseek.com/quick_start/pricing)

## 服务 / 套餐

### token-plan

- 状态: active
- 计费: token

| 档位 | 价格 | 请求数 | 评分 |
|------|------|--------|------|
| 虚拟套餐 40 | ¥40 | 无限制 | ⭐⭐⭐⭐ |
| 虚拟套餐 200 | ¥200 | 无限制 | ⭐⭐⭐⭐ |

## 旗下编程工具

- [[tools/deepseek-coder|DeepSeek Coder]]

## 变更历史

（由 /kb-update review 自动维护）
