---
id: mimo
name: 小米·MiMo
logo: 米
color: "#FF6900"
category: vertical-cloud
country: cn
extractStrategy: manual
extractStatus: manual
lastVerified: 2026-07-23
massServices: [token-plan, api-paygo]
notes: Token Plan 页为 SPA + 按量计费 API 文档页可提取模型价格。V2→V2.5 已迁移。
url_home: "https://mimo.xiaomi.com/zh/mimocode"
url_pricing: "https://platform.xiaomimimo.com/token-plan"
url_docs: "https://mimo.mi.com/docs/zh-CN/price/pay-as-you-go"
url_api: ""
url_console: ""
services: 
  - 
    type: token-plan
    status: active
    billingCore: token
    migration: Token Plan，V2→V2.5 迁移中
    plans: 
      - 
        tier: lite
        name: Lite
        monthlyPrice: 39
        currency: ¥
        tokenLimit: 3M Tokens
        measuredMonthlyToken: 108
        rating: 3
        models: [MiMo-V2.5-Pro, MiMo-V2.5, MiMo-V2.5-ASR, MiMo-V2.5-TTS]
        tags: []
        bloggerVerdict: 小米生态，价格低但模型少。
        status: active
      - 
        tier: pro
        name: Pro
        monthlyPrice: 329
        currency: ¥
        tokenLimit: 30M Tokens
        measuredMonthlyToken: 1002
        rating: 3
        models: [MiMo-V2.5-Pro, MiMo-V2.5, MiMo-V2.5-ASR, MiMo-V2.5-TTS]
        tags: []
        bloggerVerdict: 高用量，但模型选择少。
        status: active
models: [MiMo-V2.5, MiMo-V2.5-ASR, MiMo-V2.5-Pro, MiMo-V2.5-TTS]
---

# 小米·MiMo

> Token Plan 页为 SPA + 按量计费 API 文档页可提取模型价格。V2→V2.5 已迁移。

## 链接

- home: [https://mimo.xiaomi.com/zh/mimocode](https://mimo.xiaomi.com/zh/mimocode)
- pricing: [https://platform.xiaomimimo.com/token-plan](https://platform.xiaomimimo.com/token-plan)
- docs: [https://mimo.mi.com/docs/zh-CN/price/pay-as-you-go](https://mimo.mi.com/docs/zh-CN/price/pay-as-you-go)

## 服务 / 套餐

### token-plan

- 状态: active
- 计费: token
- 迁移: Token Plan，V2→V2.5 迁移中

| 档位 | 价格 | 请求数 | 评分 |
|------|------|--------|------|
| Lite | ¥39 | None | ⭐⭐⭐ |
| Pro | ¥329 | None | ⭐⭐⭐ |

## 旗下编程工具

- [[tools/mimo-code|MiMo Code]]

## 变更历史

（由 /kb-update review 自动维护）
