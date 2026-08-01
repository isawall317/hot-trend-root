---
title: "模型 & 价格 | DeepSeek API Docs"
source: "https://api-docs.deepseek.com/zh-cn/quick_start/pricing"
author:
published:
created: 2026-08-01
description: "下表所列模型价格以“百万 tokens”为单位。Token 是模型用来表示自然语言文本的的最小单位，可以是一个词、一个数字或一个标点符号等。我们将根据模型输入和输出的总 token 数进行计量计费。"
tags:
  - "来源/clippings"
---
## 模型 & 价格

下表所列模型价格以“百万 tokens”为单位。Token 是模型用来表示自然语言文本的的最小单位，可以是一个词、一个数字或一个标点符号等。我们将根据模型输入和输出的总 token 数进行计量计费。

---

## 模型细节

**

<table><tbody><tr><td colspan="2">模型</td><td>deepseek-v4-flash</td><td>deepseek-v4-pro</td></tr><tr><td colspan="2">BASE URL (OpenAI 格式)</td><td colspan="2"><a href="https://api.deepseek.com/">https://api.deepseek.com</a></td></tr><tr><td colspan="2">BASE URL (Anthropic 格式)</td><td colspan="2"><a href="https://api.deepseek.com/anthropic">https://api.deepseek.com/anthropic</a></td></tr><tr><td colspan="2">模型版本</td><td>DeepSeek-V4-Flash-0731</td><td>DeepSeek-V4-Pro</td></tr><tr><td colspan="2">思考模式</td><td colspan="2">支持非思考与思考模式（默认）<br>切换方式详见 <a href="https://api-docs.deepseek.com/zh-cn/guides/thinking_mode">思考模式</a></td></tr><tr><td colspan="2">上下文长度</td><td colspan="2">1M</td></tr><tr><td colspan="2">输出长度</td><td colspan="2">最大 384K</td></tr><tr><td rowspan="6">功能</td><td><a href="https://api-docs.deepseek.com/zh-cn/guides/json_mode">Json Output</a></td><td>支持</td><td>支持</td></tr><tr><td><a href="https://api-docs.deepseek.com/zh-cn/guides/tool_calls">Tool Calls</a></td><td>支持</td><td>支持</td></tr><tr><td><a href="https://api-docs.deepseek.com/zh-cn/guides/responses_api">Responses API</a> <sup>(1)</sup></td><td>支持</td><td>暂不支持</td></tr><tr><td><a href="https://api-docs.deepseek.com/zh-cn/guides/anthropic_api">Anthropic API</a></td><td>支持</td><td>支持</td></tr><tr><td><a href="https://api-docs.deepseek.com/zh-cn/guides/chat_prefix_completion">对话前缀续写（Beta）</a></td><td>支持</td><td>支持</td></tr><tr><td><a href="https://api-docs.deepseek.com/zh-cn/guides/fim_completion">FIM 补全（Beta）</a></td><td>仅非思考模式支持</td><td>仅非思考模式支持</td></tr><tr><td rowspan="3">价格 <sup>(2)</sup></td><td>百万tokens输入（缓存命中）</td><td>0.02元</td><td>0.025元</td></tr><tr><td>百万tokens输入（缓存未命中）</td><td>1元</td><td>3元</td></tr><tr><td>百万tokens输出</td><td>2元</td><td>6元</td></tr><tr><td colspan="2">并发限制 <sup>(3)</sup></td><td>2500</td><td>500</td></tr></tbody></table>

**

(1) Responses API 目前仅支持 `deepseek-v4-flash` 模型，暂不支持 `deepseek-v4-pro` 模型。我们将于 2026 年 8 月初增加对 `deepseek-v4-pro` 模型的支持。

(2) DeepSeek API 服务即将采用峰谷定价策略，高峰时段价格为平时价格 2 倍，适用所有计费项，具体时间以正式通知为准。【高峰时段定义：北京时间每日 9:00～12:00 和 14:00～18:00】

(3) 更多并发限制细节，请参考 [限速与隔离](https://api-docs.deepseek.com/zh-cn/quick_start/rate_limit)

---

## 扣费规则

扣减费用 = token 消耗量 × 模型单价，对应的费用将直接从充值余额或赠送余额中进行扣减。 当充值余额与赠送余额同时存在时，优先扣减赠送余额。

产品价格可能发生变动，DeepSeek 保留修改价格的权利。请您依据实际用量按需充值，定期查看此页面以获知最新价格信息。