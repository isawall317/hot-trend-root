---
title: "老用户权益说明 - 智谱AI开放文档"
source: "https://docs.bigmodel.cn/cn/coding-plan/notice/usage-revision"
author:
published:
created: 2026-08-01
description: "帮助您快速了解 2026 年 7 月 30 日 GLM Coding Plan 套餐改版、已订阅用户权益保障及后续订阅安排。"
tags:
  - "来源/clippings"
---
> 公告发布时间：2026 年 7 月 30 日  
> 本文提及的所有日期和时间均以北京时间（UTC+8）为准

为提升额度计算的透明度和可预期性，GLM Coding Plan 套餐焕新上线，新版套餐采用以 Token 消耗为基础的积分制。新版套餐的具体档位、价格、积分额度及抵扣规则，请以 [套餐订阅页](https://www.bigmodel.cn/glm-coding) 及用量说明（ [个人版](https://docs.bigmodel.cn/cn/coding-plan/overview#%E7%94%A8%E9%87%8F%E8%AF%B4%E6%98%8E) 、 [团队版](https://docs.bigmodel.cn/cn/coding-plan/team#%E7%94%A8%E9%87%8F%E9%A2%9D%E5%BA%A6) ）为准。

**要点概览**

- **所有的老用户权益完全不受影响；同时，周末全天将按非高峰时段抵扣额度**
- **V1 老用户到期前，可按本次调整前的 V2 版本价格购买及长期使用**
- 历史版本套餐与新版套餐仅额度计算方式不同，其他权益如支持的模型将保持一致

## 一、如何判断您正在使用哪种套餐

可登录 [个人控制台](https://bigmodel.cn/coding-plan/personal/overview) 查看当前套餐类型，以对应本文中的后续影响。

| 套餐类型 | 识别方式 |
| --- | --- |
| V1 版个人套餐 | [套餐概览](https://bigmodel.cn/coding-plan/personal/overview) 页面显示”历史版本 V1” |
| V2 版个人套餐 | [套餐概览](https://bigmodel.cn/coding-plan/personal/overview) 页面显示”历史版本 V2” |
| 团队套餐 | [我的套餐](https://bigmodel.cn/coding-plan/team/my-plan) 页面显示”团队套餐” |
| 当前无生效套餐 | 套餐已到期或尚未订阅 |

## 二、不同用户将受到什么影响

### 1\. 如果您正在使用 V1 版个人套餐

- 当前已生效套餐的价格、权益、额度及计算方式均不受影响，可正常使用至当前套餐周期结束。
- 您的 V1 套餐到期前，您可按 V2 的价格（如下表）订阅（含续订、升级）V2 套餐.

此功能正在开发中，预计 8 月中旬可上线，届时您可在 [套餐概览](https://bigmodel.cn/coding-plan/personal/overview) 获得 V2 套餐订阅入口。

| 个人套餐 | 包月 | 包季 9 折 | 包年 8 折 |
| --- | --- | --- | --- |
| Lite | 49 | 44.1 | 39.2 |
| Pro | 149 | 134.1 | 119.2 |
| Max | 469 | 422.1 | 375.2 |

- 若您符合 [《老套餐迁移与补偿说明》](https://docs.bigmodel.cn/cn/coding-plan/transition) 中的相关条件，已获得的迁移折扣仍将在原有效期内生效，并可用于订阅 V2 版套餐。

### 2\. 如果您正在使用 V2 版个人套餐

- 当前套餐的价格、权益、额度及计算方式均不受影响，可按照原套餐继续使用、续订和升档。

### 3\. 如果您正在使用团队套餐

- 当前套餐的价格、权益、额度及计算方式均不受影响，可按照原套餐继续使用、续订和升档。
- 当前套餐到期前，系统不会开放切换新版积分套餐；到期后，您可以订阅新版线上在售套餐。

### 4\. 如果您当前没有生效套餐，或准备首次订阅

自 2026 年 7 月 30 日新版套餐上线后，当前没有生效套餐的用户和首次订阅用户，可以直接选择新版积分套餐。具体价格、积分额度及适用规则以订阅页面展示为准

## 三、历史套餐用量说明备查

### 个人套餐（V2 版）

为了管理资源并确保所有用户的公平访问，我们进行每 5 小时的限额和每周使用额度限制，您可以在 [用量统计](https://www.bigmodel.cn/coding-plan/personal/usage) 中查看您的额度消耗进展。一次 prompt 指一次提问，每次 prompt 预计可调用模型 15-30 次。

| 套餐类型 | 每 5 小时限额   （动态刷新，额度在请求消耗 5 小时后刷新重置） | 每周限额   （自下单时开启，以 7 天为一个周期额度刷新重置） |
| --- | --- | --- |
| Lite 套餐 | 最多约 80 次 prompts | 最多约 400 次 prompts |
| Pro 套餐 | 最多约 400 次 prompts | 最多约 2000 次 prompts |
| Max 套餐 | 最多约 1600 次 prompts | 最多约 8000 次 prompts |

上述次数为预估值，实际可用量会因项目复杂度、代码库大小以及是否启用自动接受等因素而有所不同。

**GLM-5.2/GLM-5-Turbo** 作为高阶模型，对标 Claude Opus，调用时将按照 “高峰期 3 倍，非高峰期 1 倍” 系数消耗额度。

注：“高峰期”为 **每周一至周五** 的 14:00～18:00 （UTC+8）。

### 团队套餐

自 7 月 30 日起，历史版本团队套餐各席位额度统一上调 30%，以下为调整后额度。

<table><thead><tr><th><p>套餐类型</p></th><th><p>每 5 小时限额 / 席位</p><p>（动态刷新，额度在请求消耗 5 小时后刷新重置）</p></th><th><p>每周限额 / 席位</p><p>（自下单时开启，以 7 天为一个周期额度刷新重置）</p></th></tr></thead><tbody><tr><td><p>团队标准版</p></td><td><p>最多 0.78 亿 tokens</p></td><td><p>最多 3.9 亿 tokens</p></td></tr><tr><td><p>团队高级版</p></td><td><p>最多 2.08 亿 tokens</p></td><td><p>最多 10.4 亿 tokens</p></td></tr><tr><td><p>说明</p></td><td colspan="2"><p></p><p>“最多”指在 <strong>1 倍消耗系数</strong> 下，可实际消耗的 Tokens 总量。</p><p></p><p>当前各模型的额度消耗规则如下：</p><ul><li><p><strong>GLM-4.7：</strong> 全天按 <strong>1 倍系数</strong> 消耗额度</p></li><li><p><strong>GLM-5.2/GLM-5-Turbo</strong> 作为高阶模型，调用时将按照 “高峰期 3 倍，非高峰期 1 倍” 系数消耗额度。</p></li></ul><p>* 注：“高峰期”为 <strong>每周一至周五</strong> 的 14:00～18:00 （UTC+8）。</p></td></tr></tbody></table>