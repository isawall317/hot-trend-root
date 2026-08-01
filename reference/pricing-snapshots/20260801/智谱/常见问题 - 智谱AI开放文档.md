---
title: "常见问题 - 智谱AI开放文档"
source: "https://docs.bigmodel.cn/cn/coding-plan/faq"
author:
published:
created: 2026-08-01
description:
tags:
  - "来源/clippings"
---
## 一、套餐详情

**Q：GLM Coding Plan 是否已支持 GLM-5.2 ？如何切换使用的模型？**

**A：** 所有套餐均支持 **GLM-5.2** 、GLM-5-Turbo、GLM-4.7。

使用 GLM 最新模型，请看 [如何切换模型](https://docs.bigmodel.cn/cn/coding-plan/latest-model)

---

**Q：套餐的用量额度大概是多少？**

**A:** 为了更好地管理计算资源并保障所有用户的公平使用，套餐采用 **每 5 小时限额 + 每周限额** 的使用机制，您可以在 [用量统计](https://www.bigmodel.cn/coding-plan/personal/usage) 中查看当前的额度消耗情况与剩余额度。

用量详情请见：

---

**Q：套餐额度有应用场景限制吗？**

**A：** GLM Coding Plan 仅限在官方支持的 [指定工具与产品环境](https://docs.bigmodel.cn/cn/coding-plan/tool/others#%E4%B8%80%E3%80%81%E9%80%82%E7%94%A8%E5%B7%A5%E5%85%B7) 中使用。在除规定工具外调用 API，不可享用 Coding 套餐的额度。 如需在自建应用、网站、机器人、SaaS 产品等场景中通过 API 集成模型能力，请使用智谱提供的标准 API 服务，并根据对应协议计费。

---

**Q：套餐体验卡支持使用什么模型？**

**A：** GLM Coding Plan 体验卡支持 `GLM-5.2` 、 `GLM-4.7` 模型。

---

**Q：套餐额度耗尽后，系统是否会继续消耗我的资源包/账户余额？**

**A：** 不会，当套餐额度耗尽后，需要等待下一个 5 小时周期恢复额度，系统不会继续消耗您的其他资源包/账户余额。

---

**Q：我可以与他人共享一个订阅套餐吗？**

**A：** 不可以。GLM Coding Plan 套餐为订阅人专享使用，若因账号共享导致出现多人共用同一套餐的情况，我们可能会视为不当使用，并在必要时对订阅权益做出相应限制，严重时或将影响账号正常使用。

---

## 二、调用 MCP

**Q：哪些套餐等级支持视觉理解、联网搜索、网页读取和开源仓库 MCP 工具？**

**A：** 所有等级的套餐都支持。

---

**Q：视觉理解、联网搜索、网页读取、开源仓库 MCP 的调用额度是多少？**

**A：** 模型与 MCP 共享套餐调用额度，详情请查看 [用量说明](https://docs.bigmodel.cn/cn/coding-plan/overview#%E7%94%A8%E9%87%8F%E8%AF%B4%E6%98%8E) 。

---

**Q：除了使用 GLM Coding Plan 套餐包，我能采用其他方式调用这些 MCP 工具吗？**

**A:** 除了套餐包，我们暂未提供其他调用这些 MCP 工具的接入方案。若您调用其他类似的 MCP 工具，使用过程产生的计费问题，不属于此套餐的范畴。

---

## 三、管理订阅

**Q: 订阅费用是如何扣除的？**

**A:** 系统会按照以下顺序扣费：

1. 优先使用赠金余额。
2. 若赠金不足，则使用现金余额。
3. 若以上余额不足，再从您绑定的第三方支付方式（如微信、支付宝）扣款。

---

**Q: 如何取消自动续费？**

**A:** 您可以在 [套餐概览页面](https://www.bigmodel.cn/coding-plan/personal/overview) 取消自动续费。请务必在下一个扣费日前 **至少 3 天** 取消，以避免自动续费。取消后，当前周期继续有效，到期后不再续费。

---

**Q: 套餐支持退款吗？**

**A:** 订阅服务一经购买即视为确认，不支持退款。即使您未使用完套餐，费用也无法退回。我们建议您根据使用需求选择合适的订阅套餐和周期。

---

## 四、套餐升级

**Q: 如何升级我的套餐？**

**A:** 在订阅管理中选择“升级”，支付差额后即可立即生效。操作步骤如下：

1. 打开 [套餐计划](https://bigmodel.cn/claude-code?t=1756888375675) 页面 。
2. 点击 **“订阅升级”** ，选择目标套餐。
3. 支付差额。
4. 新套餐立即生效。

---

## 五、使用问题

**Q：为什么购买了编码套餐还报错”1113 余额不足”？为什么购买了编码套餐还扣账号余额？**

**A：** 报错余额不足/扣账号余额的情况可能是由于未满足 GLM Coding Plan 编码套餐的使用条件：

1. 套餐仅限在官方支持的 [指定工具与产品环境](https://docs.bigmodel.cn/cn/coding-plan/tool/others#%E4%B8%80%E3%80%81%E9%80%82%E7%94%A8%E5%B7%A5%E5%85%B7) 中使用.
2. 配置特定的 Base URL 地址才能使用：
- Claude Code 中 Base URL 是： `https://open.bigmodel.cn/api/anthropic` 。
- Cherry studio 配置的 Base URL 是： `https://open.bigmodel.cn/api/coding/paas/v4/` 。
- Claude Code 和 Cherry studio 之外的工具中 Base URL 是： `https://open.bigmodel.cn/api/coding/paas/v4` 。
3. 官网体验中心不支持使用编码套餐。

---

**Q：怎么查看是否扣的是编码套餐？**

**A：** 您可以在 [费用明细](https://bigmodel.cn/finance/expensebill/list) 的抵扣资源包列表项查看是否是用编码套餐抵扣的。

---

**Q：再次购买/升级编码套餐，会在之前套餐基础上叠加时间吗？**

**A：** 不会叠加，再次购买/升级编码套餐时，会把之前的套餐作废，之前套餐未使用时间会作为现有套餐剩余价值，计算到您的再次购买中。

---

**Q：编码套餐过期后，可以使用资源包吗？**

**A：** Claude Code 中暂不支持使用其他资源包，在其他编码工具中，请将 Base URL 设置为： `https://open.bigmodel.cn/api/paas/v4` ，即可使用资源包进行调用由于 Coding Agent 场景的资源消耗较高，编码套餐提供更高的权益额度与更稳定的使用体验，建议优先购买编码套餐。