---
id: kimi
name: Kimi
logo: K
color: "#10C2B0"
category: model-maker
country: cn
extractStrategy: playwright
extractStatus: ok
lastVerified: 2026-07-21
massServices: [coding-plan, api-paygo]
notes: Playwright 渲染 docs 页 → 点击展开模型卡片 → 提取 API 价格
url_home: "https://www.kimi.com"
url_pricing: "https://www.kimi.com/membership/pricing"
url_docs: "https://platform.kimi.com/docs/pricing/chat"
url_api: ""
url_console: ""
services: 
  - 
    type: coding-plan
    status: active
    billingCore: token
    migration: 内核 Token 计量 (2026-01)，保留订阅名
    plans: 
      - 
        tier: pro
        name: Allegretto
        monthlyPrice: 199
        currency: ¥
        monthlyRequests: 未公开
        tokenLimit: 无限制
        measuredMonthlyToken: 1428
        rating: 4
        models: 
          - Kimi-K2.6
          - Kimi-K2.7-Code
          - Kimi-K3
          - moonshot-v1-128k
          - moonshot-v1-128k-vision-preview
          - moonshot-v1-32k
          - moonshot-v1-32k-vision-preview
          - moonshot-v1-8k
          - moonshot-v1-8k-vision-preview
        tags: [模型强, 性价比高]
        bloggerVerdict: 20 倍额度档，长上下文场景无可替代。⚠️ 7.20 起暂停新用户订阅。
        status: paused
      - 
        tier: lite
        name: Andante
        monthlyPrice: 49
        currency: ¥
        monthlyRequests: 未公开
        tokenLimit: 无限制
        measuredMonthlyToken: 84
        rating: 4
        models: 
          - Kimi-K2.6
          - Kimi-K2.7-Code
          - Kimi-K3
          - moonshot-v1-128k
          - moonshot-v1-128k-vision-preview
          - moonshot-v1-32k
          - moonshot-v1-32k-vision-preview
          - moonshot-v1-8k
          - moonshot-v1-8k-vision-preview
        tags: [模型强]
        bloggerVerdict: Kimi 入门档，Agent 4 倍速，体验原生 Kimi-K3。⚠️ 7.20 起暂停新用户订阅。
        status: paused
models: 
  - Kimi-K2.6
  - Kimi-K2.7-Code
  - Kimi-K3
  - moonshot-v1-128k
  - moonshot-v1-128k-vision-preview
  - moonshot-v1-32k
  - moonshot-v1-32k-vision-preview
  - moonshot-v1-8k
  - moonshot-v1-8k-vision-preview
---

# Kimi

> Playwright 渲染 docs 页 → 点击展开模型卡片 → 提取 API 价格

## 链接

- home: [https://www.kimi.com](https://www.kimi.com)
- pricing: [https://www.kimi.com/membership/pricing](https://www.kimi.com/membership/pricing)
- docs: [https://platform.kimi.com/docs/pricing/chat](https://platform.kimi.com/docs/pricing/chat)

## 服务 / 套餐

### coding-plan

- 状态: active
- 计费: token
- 迁移: 内核 Token 计量 (2026-01)，保留订阅名

| 档位 | 价格 | 请求数 | 评分 |
|------|------|--------|------|
| Allegretto | ¥199 | 未公开 | ⭐⭐⭐⭐ |
| Andante | ¥49 | 未公开 | ⭐⭐⭐⭐ |

## 旗下编程工具

- [[tools/kimi-code|Kimi Code]]

## 变更历史

（由 /kb-update review 自动维护）
