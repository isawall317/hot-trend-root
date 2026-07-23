---
id: baidu
name: 百度·千帆
logo: 千
color: "#2468f0"
category: cloud-maas
country: cn
extractStrategy: manual
extractStatus: manual
lastVerified: 2026-07-23
massServices: [coding-plan, token-plan, api-paygo]
notes: 2026-07-10 宣布 Coding Plan → Token Plan 升级迁移，取消高峰限流，调用次数→Token 额度
url_home: "https://qianfan.cloud.baidu.com"
url_pricing: "https://cloud.baidu.com/product-s/qianfan_home"
url_docs: ""
url_api: ""
url_console: ""
services: 
  - 
    type: coding-plan
    status: active
    billingCore: token
    migration: → Token Plan (2026-07)，旧权益平移+顺延1月
    plans: 
      - 
        tier: lite
        name: Lite
        monthlyPrice: 99
        currency: ¥
        tokenLimit: 4200万 Token
        measuredMonthlyToken: 42
        rating: 3
        models: [ERNIE-4.5, ERNIE-Speed, DeepSeek-V4, GLM-5.2]
        tags: [多模型, 无高峰限流]
        bloggerVerdict: Coding Plan 升级为 Token Plan，取消限流+多模型，老用户顺延1个月。
        status: active
      - 
        tier: pro
        name: Pro
        monthlyPrice: 199
        currency: ¥
        tokenLimit: 2.3亿 Token
        measuredMonthlyToken: 230
        rating: 3
        models: [ERNIE-4.5, ERNIE-Speed, DeepSeek-V4, GLM-5.2]
        tags: [多模型, 无高峰限流, 高频开发]
        bloggerVerdict: Pro 档升级为 2.3亿 Token，取消高峰限流，适合高频开发。
        status: active
models: [DeepSeek-V4, ERNIE-4.5, ERNIE-Speed, GLM-5.2]
---

# 百度·千帆

> 2026-07-10 宣布 Coding Plan → Token Plan 升级迁移，取消高峰限流，调用次数→Token 额度

## 链接

- home: [https://qianfan.cloud.baidu.com](https://qianfan.cloud.baidu.com)
- pricing: [https://cloud.baidu.com/product-s/qianfan_home](https://cloud.baidu.com/product-s/qianfan_home)

## 服务 / 套餐

### coding-plan

- 状态: active
- 计费: token
- 迁移: → Token Plan (2026-07)，旧权益平移+顺延1月

| 档位 | 价格 | 请求数 | 评分 |
|------|------|--------|------|
| Lite | ¥99 | None | ⭐⭐⭐ |
| Pro | ¥199 | None | ⭐⭐⭐ |

## 旗下编程工具

- [[tools/baidu-comate|百度 Comate]]

## 变更历史

（由 /kb-update review 自动维护）
