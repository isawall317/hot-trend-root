---
title: "套餐概览 - 智谱AI开放文档"
source: "https://docs.bigmodel.cn/cn/coding-plan/overview"
author:
published:
created: 2026-08-01
description:
tags:
  - "来源/clippings"
---
GLM Coding Plan 是专为 AI 编码打造的订阅套餐，仅需少量投入，即可覆盖需求理解、代码生成、调试修复、代码库问答与自动化任务处理等开发全流程，为您带来智能、高速、稳定的编码体验。

## 可用模型

- 所有套餐均支持 **GLM-5.2** 、GLM-5-Turbo、GLM-4.7。
- 调用历史模型 GLM-5.1/GLM-5 都将自动切换至 GLM-5.2。

## 适用工具

- 套餐仅限在官方支持的 [指定工具与产品环境](https://docs.bigmodel.cn/cn/coding-plan/tool/others#%E4%B8%80%E3%80%81%E9%80%82%E7%94%A8%E5%B7%A5%E5%85%B7) 中使用。在除规定工具外调用 API，不可享用 Coding 套餐的额度。
- 套餐支持 OpenClaw 使用，但采用 **次级调度** 与尽力交付策略，Coding Agent 任务享有资源抢占优先权，高负载下 OpenClaw 任务将自动触发包括动态排队、限流等公平使用策略。
- 订阅套餐后，在上述编程工具中调用 GLM 模型，按接入指南配置即可使用套餐额度。当套餐额度耗尽后，需要等待下一个 5 小时周期恢复额度，系统不会继续消耗您的其他资源包/账户余额。

## 用量说明

团队版用量说明，请前往 [团队版权益](https://docs.bigmodel.cn/cn/coding-plan/team) 查看。

### 积分额度

套餐同时设有每 5 小时和每周额度上限，您可以在 [用量统计](https://www.bigmodel.cn/coding-plan/personal/usage) 中查看您的额度消耗进展：

| 套餐类型 | 5 小时积分 | 每周积分 |
| --- | --- | --- |
| Lite 套餐 | 2,000 | 10,000 |
| Pro 套餐 | 12,000 | 60,000 |
| Max 套餐 | 28,000 | 140,000 |

**积分刷新规则**

- **5 小时积分** ：采用动态刷新机制，积分额度在请求消耗 5 小时后刷新重置。
- **周积分** ：自套餐下单时起，以 7 天为一个周期刷新。

### 积分抵扣计算方式

- 模型消耗积分数=（输入 Token × Input 抵扣系数 + 缓存命中 Token × Cached Input 抵扣系数 + 输出 Token × Output 抵扣系数） / 10000
- MCP 消耗积分数=调用次数 × Output 抵扣系数

您可在 [财务-费用明细](https://www.bigmodel.cn/finance-center/bill/expensebill/list) 查询具体消耗的不同价格类型的 Token 数/ 工具调用次数。

<table><thead><tr><th>产品类型</th><th>产品名称</th><th>Input 抵扣系数</th><th>Cached Input 抵扣系数</th><th>Output 抵扣系数</th></tr></thead><tbody><tr><td rowspan="4">模型</td><td>GLM-5.2</td><td>6.9</td><td>1.7</td><td>24</td></tr><tr><td>GLM-5-Turbo</td><td>5.7</td><td>1.5</td><td>21</td></tr><tr><td>GLM-4.7</td><td>4.6</td><td>1.2</td><td>16</td></tr><tr><td>GLM-4.6V（视觉理解 MCP）</td><td>1.2</td><td>0.3</td><td>2.7</td></tr><tr><td rowspan="3">MCP 工具</td><td>联网搜索</td><td>—</td><td>—</td><td>1.2</td></tr><tr><td>网页读取</td><td>—</td><td>—</td><td>1.2</td></tr><tr><td>开源仓库</td><td>—</td><td>—</td><td>1.2</td></tr></tbody></table>

**非高峰时段内，模型调用按基础积分消耗的 50% 抵扣。**

高峰时段：每周一至周五的 14:00～18:00 （UTC+8）。

### 可用额度参考

以全部使用 GLM-5.2 模型为例，当缓存命中率在 90.9% （编程场景平均水平）时，不同档位套餐每周可用 Token 额度区间大约如下：

- Lite：0.43～0.87 亿 Tokens/周
- Pro：2.63～5.26 亿 Tokens/周
- Max：6.13～12.26 亿 Tokens/周

区间说明

- 最多 Tokens：全部在非高峰时段，按 0.5 倍积分消耗
- 最少 Tokens：全部在高峰时段，按 1 倍积分消耗

**当充分利用非高峰时段优惠时，相较于按量调用 GLM-5.2 标准 API，最高可节省 92% 成本**

## 独家优势

- **畅用智谱高智能模型** ：GLM 模型上线时在推理、代码、智能体能力全面达到开源模型 SOTA，工具调用、复杂任务执行表现出色。
- **兼容多款编码工具** ：支持 Claude Code、Kilo Code、OpenClaw、OpenCode、TRAE、CodeBuddy 等主流编码工具，灵活适配多种开发场景。
- **高额用量，普惠价格** ：远超常规方案的调用额度，升级至 Pro、Max，即可轻松满足高频复杂项目需求。
- **扩展覆盖更多能力** ：套餐包含专属图像视频理解、联网搜索、网页读取、开源仓库 MCP，上线 [GLM in Excel (Beta)](https://docs.bigmodel.cn/cn/coding-plan/extension/glm-in-excel) 权益，助力完成更广泛开发任务。

## 下一步

- [快速开始](https://docs.bigmodel.cn/cn/coding-plan/quick-start) ：帮助您快速上手，从订阅套餐到在编码工具中使用，只需几分钟
- [使用须知](https://docs.bigmodel.cn/cn/coding-plan/usage-notes) ：快速了解账号使用规范、并发限制、退款政策等注意事项
- [常见问题](https://docs.bigmodel.cn/cn/coding-plan/faq) ：覆盖套餐相关的订阅、活动及使用过程中的常见问题

## [GLM Coding 开发者社区](https://zhipu-ai.feishu.cn/wiki/TrlMwahsfihLrKkZsy0cpuTenCz?from=from_copylink)

官方知识库

## GLM Coding 用户交流群

飞书扫码入群

![Main dashboard interface](https://cdn.bigmodel.cn/markdown/1783479750248img_v3_0213c_2b0624fe-e126-40a9-bc37-6f4b3b685adg.jpg?attname=img_v3_0213c_2b0624fe-e126-40a9-bc37-6f4b3b685adg.jpg)

Main dashboard interface