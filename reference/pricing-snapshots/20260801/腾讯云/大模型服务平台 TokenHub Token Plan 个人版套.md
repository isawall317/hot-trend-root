最近更新时间：2026-07-24 18:02:34

**说明：**

通用 Token Plan，原名称为 Token Plan，此次名称调整对用户使用体验无影响。

## 套餐对比速览

|   |   |   |
|---|---|---|
|**套餐类型**|**通用 Token Plan**|**Hy Token Plan**|
|**套餐规格和价格**|[通用 Token Plan 套餐详情](https://cloud.tencent.com/document/product/1823/130060#95731ac3-c172-4f17-9637-bcc148cb8a21)|[Hy Token Plan 套餐详情](https://cloud.tencent.com/document/product/1823/130060#df39746c-e64a-45d7-b6e1-8797ead5f927)|
|**套餐购买、套餐详情页面**|[通用 Token Plan 控制台](https://console.cloud.tencent.com/tokenhub/tokenplan/common)|[Hy Token Plan 控制台](https://console.cloud.tencent.com/tokenhub/tokenplan/hy)|
|**可用模型**|Auto<br><br>DeepSeek-V4-Flash 原厂直供<br><br>DeepSeek-V4-Pro 原厂直供<br><br>MiniMax-M2.5（将于2026年8月6日下线）<br><br>MiniMax-M2.7<br><br>GLM-5<br><br>GLM-5.1<br><br>Kimi-K2.5（将于2026年7月31日下线）|Hy3|
||**注意：**<br><br>为持续优化模型服务能力与使用体验，平台套餐内提供的 AI 模型为动态更新的模型库，可能根据模型性能、服务稳定性、合规要求、授权状况及第三方模型供应情况等进行新增、替换、版本升级、可用范围调整或逐步下线。套餐所提供的是“可使用平台当期模型库中相应模型”的服务，而非对任一特定模型的持续、固定或永久提供作出承诺。用户在订阅时所见的模型仅代表当时的可用情况，实际可用模型、版本及调用范围以购买页、控制台展示及平台公告为准。对可能影响已订阅用户使用的模型下线或重大调整，平台将通过公告、站内信或控制台提示等合理方式提前告知。|   ||
|**URL**|**Base URL**<br><br>兼容 OpenAI 接口协议工具：`https://api.lkeap.cloud.tencent.com/plan/v3`<br><br>兼容 Anthropic 接口协议工具：`https://api.lkeap.cloud.tencent.com/plan/anthropic`<br><br>**完整 URL**<br><br>兼容 OpenAI 接口协议工具：`https://api.lkeap.cloud.tencent.com/plan/v3/chat/completions`<br><br>兼容 Anthropic 接口协议工具：`https://api.lkeap.cloud.tencent.com/plan/anthropic/v1/messages`|   ||
|**API Key**|两个套餐共用同一个 API Key|   ||

## 快速入门

## 通用 Token Plan 套餐

### 套餐优势

**集合主流国产模型，可按需切换：**一次订阅即可自由切换 MiniMax-M2.5、MiniMax-M2.7、Kimi-K2.5、GLM-5、GLM-5.1、DeepSeek-V4-Flash、DeepSeek-V4-Pro 等模型，更多模型在持续接入中。

**适配热门龙虾工具、兼容主流 AI 编码工具**：支持 OpenClaw、Claude Code、OpenCode、Cline、Cursor、Kilo Code、Codex CLI 等 AI 工具，共享套餐额度，让龙虾随时随地干活，体验 AI 编码自由。

**多种套餐适配不同场景**：提供 Lite、Standard、Pro、Max 四档套餐，满足从新手体验龙虾到高强度编程不同场景选择。

**同等用量费用节省超过 50%**：同模型套餐价相比于直接调用 [文本生成服务](https://cloud.tencent.com/document/product/1823/130079) 低 50% 以上，套餐分阶定价，等级越高，百万 Token 单价越低。

### 套餐详情

**说明：**

通用 Token Plan 套餐包额度抵扣遵循统一规则，缓存命中的输入内容、缓存未命中的输入内容、输出内容所产生的 Token 数，均从套餐包内统一抵扣。建议您密切关注 [套餐 Token 用量](https://cloud.tencent.com/document/product/1823/130119#4c0fa474-9007-46a4-94e7-94a62b8500b0) 消耗情况，避免产生超预期的消耗。

|   |   |   |   |
|---|---|---|---|
|**套餐**|**用量限制**|**价格**|**适用场景**|
|**体验套餐**<br><br>**（Lite）**|**每订阅月**<br><br>**3500万 Tokens**|**39元/月**|**新手尝鲜，入门首选。**<br><br>适合用于首次体验龙虾能力，可实现网页操作、文件处理、数据分析、定时任务等。<br><br>**注意：**<br><br>按龙虾基础使用场景预估可支持**约 70 轮问答式交互**（实际轮次受单轮输入输出内容长度、任务复杂度、代码量等因素影响，具体以实际使用为准）。|
|**基础套餐**<br><br>**（Standard）**|**每订阅月**<br><br>**1亿 Tokens**|**99元/月**|**日常使用，高性价比。**<br><br>适合日常用龙虾办公和轻量开发，可实现批量文件处理、Demo 制作、自动化工作流等。<br><br>**注意：**<br><br>按龙虾基础使用场景预估可支持**约 200 轮问答式交互**（实际轮次受单轮输入输出内容长度、任务复杂度、代码量等因素影响，具体以实际使用为准）。|
|**进阶套餐**<br><br>**（Pro）**|**每订阅月**<br><br>**3.2亿 Tokens**|**299元/月**|**高频 AI 开发，Token 配额相比基础版提升至 3 倍。**<br><br>适合每天高频使用 AI 的开发者和效率达人，多仓库并行、复杂逻辑生成、代码重构、Agent 编排等。|
|**专业套餐**<br><br>**（Max）**|**每订阅月**<br><br>**6.5亿 Tokens**|**599元/月**|**更多额度加持，重度 AI 开发首选。**<br><br>适合把 AI 当核心生产力工具的重度用户，全栈 AI 生成、多 Agent 协同、CI 自动化等。|

### 可用模型

四个档位套餐均支持以下模型，更多模型将持续接入中。

|   |   |   |   |
|---|---|---|---|
|**Model Name**|**Model ID**|模型能力|**说明**|
|Auto|tc-code-latest|深度思考、文本生成|Auto 智能路由，系统会通过算法自动匹配模型。|
|DeepSeek-V4-Flash 原厂直供|deepseek-v4-flash-202605|深度思考、文本生成|由 DeepSeek 直接提供的 DeepSeek V4 Flash 模型服务，TokenHub 不对该服务提供 SLA 保障。使用该模型即视为您已知晓并同意遵守 [DeepSeek 的服务协议](https://cdn.deepseek.com/policies/zh-CN/deepseek-terms-of-use.html)，请您在使用前务必仔细阅读相关内容，如不接受上述内容，请立即停止使用。|
|DeepSeek-V4-Pro 原厂直供|deepseek-v4-pro-202606|深度思考、文本生成|由 DeepSeek 直接提供的 DeepSeek V4 Pro 模型服务，TokenHub 不对该服务提供 SLA 保障。使用该模型即视为您已知晓并同意遵守 [DeepSeek 的服务协议](https://cdn.deepseek.com/policies/zh-CN/deepseek-terms-of-use.html)，请您在使用前务必仔细阅读相关内容，如不接受上述内容，请立即停止使用。|
|MiniMax-M2.5|minimax-m2.5<br><br>minimax-m-2-5|深度思考、文本生成|将于2026年8月6日下线。|
|MiniMax-M2.7|minimax-m2.7<br><br>minimax-m-2-7|深度思考、文本生成|-|
|GLM-5|glm-5<br><br>glm-5-0|深度思考、文本生成|-|
|GLM-5.1|glm-5.1<br><br>glm-5-1|深度思考、文本生成|-|
|Kimi-K2.5|kimi-k2.5<br><br>kimi-k-2-5|深度思考、文本生成、图片理解|将于2026年7月31日下线。<br><br>资源负载较高，高峰时段可能触发请求限频机制，为保障使用体验，请优先选用其他模型。|
|Tencent HY 2.0 Instruct|hunyuan-2.0-instruct|文本生成|2026年6月22号下线。|
|Tencent HY 2.0 Think|hunyuan-2.0-thinking|深度思考、文本生成|2026年6月22号下线。|
|Hunyuan-T1|hunyuan-t1|文本生成|2026年6月22号下线。|
|Hunyuan-TurboS|hunyuan-turbos|文本生成|2026年6月22号下线。|

## Hy Token Plan 套餐

### 套餐优势

**基于腾讯自研混元模型打造：**集成 Hy3 模型，面向 Agent 工作负载设计，适配 Coding Agent、文档自动化、多步工具调用等工作流。

**适配热门龙虾工具、兼容主流 AI 编码工具**：支持 OpenClaw、Claude Code、OpenCode、Cline、Cursor、Kilo Code、Codex CLI 等 AI 工具，共享套餐额度，让龙虾随时随地干活，体验 AI 编码自由。

**多种套餐适配不同场景**：提供 Lite、Standard、Pro、Max 四档套餐，满足从新手体验龙虾到高强度编程不同场景选择。

**同等用量费用比通用版更优惠**：满足开发者对任务完成可靠性与推理成本可控的双重需求。

### 套餐详情

**说明：**

Hy Token Plan 个人版套餐包额度抵扣遵循统一规则，缓存命中的输入内容、缓存未命中的输入内容、输出内容所产生的 Token 数，均从套餐包内统一抵扣。建议您密切关注 [套餐 Token 用量](https://cloud.tencent.com/document/product/1823/130119#4c0fa474-9007-46a4-94e7-94a62b8500b0) 消耗情况，避免产生超预期的消耗。

|   |   |   |   |
|---|---|---|---|
|**套餐**|**用量限制**|**价格**|**适用场景**|
|**体验套餐**<br><br>**（Lite）**|**每订阅月**<br><br>**3500万 Tokens**|**28元/月**|**新手尝鲜，入门首选。**<br><br>适合用于首次体验龙虾能力，可实现网页操作、文件处理、数据分析、定时任务等。<br><br>**注意：**<br><br>按龙虾基础使用场景预估可支持**约 70 轮问答式交互**（实际轮次受单轮输入输出内容长度、任务复杂度、代码量等因素影响，具体以实际使用为准）。|
|**基础套餐**<br><br>**（Standard）**|**每订阅月**<br><br>**1亿 Tokens**|**78元/月**|**日常使用，高性价比。**<br><br>适合日常用龙虾办公和轻量开发，可实现批量文件处理、Demo 制作、自动化工作流等。<br><br>**注意：**<br><br>按龙虾基础使用场景预估可支持**约 200 轮问答式交互**（实际轮次受单轮输入输出内容长度、任务复杂度、代码量等因素影响，具体以实际使用为准）。|
|**进阶套餐**<br><br>**（Pro）**|**每订阅月**<br><br>**3.2亿 Tokens**|**238元/月**|**高频 AI 开发，Token 配额相比基础版提升至 3 倍。**<br><br>适合每天高频使用 AI 的开发者和效率达人，多仓库并行、复杂逻辑生成、代码重构、Agent 编排等。|
|**专业套餐**<br><br>**（Max）**|**每订阅月**<br><br>**6.5亿 Tokens**|**468元/月**|**更多额度加持，重度 AI 开发首选。**<br><br>适合把 AI 当核心生产力工具的重度用户，全栈 AI 生成、多 Agent 协同、CI 自动化等。|

### 可用模型

四个档位套餐均支持 Hy3 模型。

|   |   |   |   |
|---|---|---|---|
|**Model Name**|**Model ID**|**模型能力**|**说明**|
|Hy3|hy3、hy3-preview|深度思考、文本生成|Hy3 正式版面向真实业务场景打磨，相比 Preview 版本，Hy3 基于腾讯元宝、WorkBuddy、ima 、Marvis 等真实业务反馈，重点提升了 Coding Agent、长文理解、多轮上下文承接、搜索问答与复杂任务执行能力，在减少幻觉、提升任务完成度和工程可用性方面表现更稳。更加适合前端任务、跨文件代码开发、长文档分析、办公自动化和多步骤 Agent 工作流等实用场景。|

## 订阅须知

**通用 Token Plan、Hy Token Plan 均不支持退款**。因此在订阅前请知悉以下重要内容：

1. **订阅账号规范：**为订阅人专享使用，**严禁账号共享**。若存在账号共享行为，可能**导致订阅权益受限**，腾讯无法保障您的权益，敬请知悉。

2. **严禁 API 调用**：仅限在 AI 工具（例如：Claude Code、CodeBuddy Code、OpenClaw 等）中使用，禁止以 API 调用的形式用于自动化脚本、自定义应用程序后端或任何非交互式批量调用场景。将套餐 API Key 用于允许范围之外的调用将被视为违反腾讯与您的约定，可能会导致订阅被暂停或 API Key 被封禁。对于违规而导致服务受损，腾讯不承担赔偿责任。

3. **速率限制：**并发速率与您的套餐等级相关，平台会根据资源进行动态调整，基本原则 Max > Pro > Standard > Lite。

4. **续费说明：**请在套餐过期前完成续费，**套餐到期后将无法进行续费**，套餐将失效，**剩余 Token 量不支持结转到下个月，API Key 也会失效，**使用该 API Key 的工具/应用/服务将立即无法调用 API。详情请参见 [续费规则](https://cloud.tencent.com/document/product/1823/130119#3c0f69d4-013e-4b67-b269-15b3be98ef18)。

## 支持 AI 工具

## 套餐抵扣规则

通用 Token Plan 与 Hy Token Plan 共用同一套 API Key 和调用地址，将根据您调用时指定的 Model ID，自动从支持该 Model ID 的对应套餐包中抵扣 Token 量。

## 套餐有效期

通用 Token Plan 与 Hy Token Plan 为两个独立套餐，各自有效期独立计算，均以自然月为单位，自购买成功当日起算。1 个月套餐有效期示例如下：

|   |   |   |
|---|---|---|
|**购买日期**|**购买时长**|**结束日期**|
|01.04 10:00:00|1 个月|02.04 9:59:59|
|01.31 10:00:00|1 个月|02.28 9:59:59|
|02.01 10:00:00|1 个月|03.01 9:59:59|

## 配额与限制

### 配额

|   |   |
|---|---|
|**配额**|**说明**|
|每个主账号最多可同时持有 2 个​ Token Plan同一系列仅可购买 1 个档位的套餐|每个主账号（包含其名下的所有子账号）最多可同时持有 2 个​ Token Plan：<br><br>1 个通用 Token Plan（不区分 Lite、Standard、Pro、Max 等具体套餐规格）；<br><br>1 个 Hy Token Plan（不区分 Lite、Standard、Pro、Max 等具体套餐规格）。|
|Token Plan 个人版套餐仅支持生成一个 API Key|通用 Token Plan、Hy Token Plan 套餐使用同一个 API Key，详见 [API Key 的管理](https://cloud.tencent.com/document/product/1823/130119#18ae03c7-fd6b-4bd1-8241-26ffcc39a641)。|

### 限制

通用 Token Plan、Hy Token Plan 套餐支持 [升配](https://cloud.tencent.com/document/product/1823/130119#02fac2dd-dc34-425f-947d-f07b5fded6e1)，**不支持降配**。

通用 Token Plan、Hy Token Plan 套餐一经购买均**不支持退订**。

## Token Plan 体验交流群

为方便您更好地使用 Token Plan 服务，我们设立了专属体验交流群。您可通过下方二维码入群：

![](https://qcloudimg.tencent-cloud.cn/image/document/2bf4e6f80c3a4b6e7266e1b80688b38a.png)

## 常见问题