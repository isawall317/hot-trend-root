# AI Coding Plan 定价页 URL 参考

> 最后更新: 2026-07-21
>
> 覆盖 23 个主流 AI Coding Plan / Token Plan 供应商的定价信息来源

---

## 提取状态总览（2026-07-21 实测）

| 厂商 | extractStrategy | 状态 |
|------|----------------|------|
| DeepSeek | docs | ✅ httpx + BS4 可提取 API 定价 |
| 腾讯云 | docs | ✅ 提取 Coding Plan Lite ¥40 / Pro ¥200 |
| MiniMax | docs | ✅ 提取 Token Plan Plus ¥49 / Max ¥119 / Ultra ¥469 |
| 智谱AI | manual | ❌ SPA，需 JS 渲染 |
| 字节·方舟 | manual | ❌ SPA，需 JS 渲染 |
| Kimi | manual | ❌ Next.js SPA |
| 其余 14 家 | manual | 待探测（未注册 parser） |

---

## 国内平台

### 公开定价页（无需登录即可查看）

| 平台 | 定价页 URL | 类型 | 备注 |
|------|-----------|------|------|
| 智谱AI | https://open.bigmodel.cn/pricing | API 按量 | 公开 API 定价，Coding Plan 套餐在控制台 |
| DeepSeek 官方 | https://api-docs.deepseek.com/quick_start/pricing | API 按量 | 无订阅套餐，codingplan-saver 按 API 价格折算"虚拟套餐" |
| Kimi | https://platform.kimi.com/docs/pricing/chat | API 按量 | 模型定价总览，点击各模型查看详细费率 |
| Kimi (C端) | https://www.kimi.com/membership/pricing | 订阅套餐 | C端会员定价，含 Coding Plan 入口 |
| MiniMax | https://platform.minimaxi.com/docs/guides/pricing-token-plan | Token Plan | 公开订阅套餐：Plus ¥49 / Max ¥119 / Ultra ¥469 |
| 腾讯云 TokenHub | https://cloud.tencent.com/document/product/1823/130092 | Coding Plan + Token Plan | Coding Plan 文档 / Token Plan 文档 |
| 百度·千帆 | https://cloud.baidu.com/product-s/qianfan_home | Token Plan | 产品总览页，含"Token Plan 个人版"入口 |
| 华为云 CodeArts | https://www.huaweicloud.com/product/codearts.html | Coding Plan | 公开套餐：基础版 ¥60 / 专业版 ¥200 / 企业版 ¥600 |
| 硅基流动 | https://siliconflow.cn/pricing | API 按量 | 模型集市，按量调用 GLM / Kimi / DeepSeek / Qwen 等主流模型，无订阅套餐，常用作比价基准 |
| 千问AI | https://platform.qianwenai.com/pricing/token-plan | Token Plan | 阿里通义千问专用平台，Lite / Standard / Pro 三档 |
| 阿里·百炼 | https://www.aliyun.com/benefit/scene/tokenplan | Token Plan | 阿里云 Token Plan 活动页，含套餐价格 |

### 需登录控制台查看定价

| 平台 | 入口 URL | 类型 | 备注 |
|------|---------|------|------|
| 字节·方舟 | https://www.volcengine.com/ark | Token Plan | 方舟平台首页，Token Plan 定价在控制台内；当前 2.5 折活动 |
| 京东云 | https://www.jdcloud.com/ | Coding Plan | 京东云首页，搜索"AI Coding"找到对应产品 |
| 小米·MiMo | https://platform.xiaomimimo.com | Coding Plan | MiMo 开放平台，需小米账号登录 |

---

## 海外平台

### 大厂 AI 平台

| 平台 | 定价页 URL | 套餐 | 备注 |
|------|-----------|------|------|
| Google Gemini | https://gemini.google.com/ | Google One AI Premium $19.99/月 | 消费者端；API 定价见 ai.google.dev/pricing |
| Amazon Q Developer | https://aws.amazon.com/q/developer/pricing/ | Free · Pro $19/用户/月 | AWS 的 AI Coding 助手，Pro 支持最新 Claude 模型 |
| Mistral | https://mistral.ai/pricing | API 按量 + 企业订阅 | 欧洲主流大模型厂商，Le Chat 有免费版 |

### 主流 Coding IDE / Agent

| 平台 | 定价页 URL | 套餐 | 备注 |
|------|-----------|------|------|
| Claude | https://claude.com/pricing | Pro $20/月 · Max $100/月 · Team $25/席 | 公开；API 定价另见 anthropic.com/pricing |
| ChatGPT / Codex | https://openai.com/chatgpt/pricing/ | Plus $20/月 · Pro $200/月 | 公开，但可能被墙 |
| GitHub Copilot | https://github.com/features/copilot/plans | Free · Pro $10/月 · Business $19/月 | 公开 |
| Cursor | https://cursor.com/pricing | Hobby Free · Individual $16/月 · Teams $32/用户 | 公开 |
| Devin（原 Windsurf） | https://devin.ai/pricing | Free · Pro $20/月 · Max $200/月 · Teams $80/月 | Windsurf 已并入 Devin/Cognition |
| Replit | https://replit.com/pricing | Starter Free · Core $25/月 · Pro $100/月 | 公开 |
| JetBrains AI | https://www.jetbrains.com/ai/ | AI Assistant 订阅（IDE 内） | JetBrains IDE 生态，需配合 IDE 使用 |

### 独立 AI Coding 工具 / 模型聚合

| 平台 | 定价页 URL | 套餐 | 备注 |
|------|-----------|------|------|
| Tabnine | https://www.tabnine.com/pricing | 免费版 + 付费订阅 | 老牌 AI 代码助手，支持本地模型部署 |
| OpenCode | https://opencode.ai/ | 免费模型 + 可接入任意第三方模型 | 首页无公开定价，需注册查看 |
| Ollama | https://ollama.com/ | Pro $20/月 · Max $100/月 | 本地部署免费，云端 Pro/Max 收费 |

---

## 变更记录

| 日期 | 变更 |
|------|------|
| 2026-07-21 | 删除优云智算、共继算力、智谱国际版；新增硅基流动、Google Gemini、Amazon Q、Mistral、JetBrains AI、Tabnine；重构分类 |
| 2026-07-20 | 初始版本 |