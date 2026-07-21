# 厂商参考手册 — 定价页 URL + 联盟推广链接

> 最后更新: 2026-07-22
>
> **一站式厂商信息**：定价页（数据采集用）+ 联盟推广链接（"优惠购买"按钮用）+ 返佣信息。
> 合并自 `pricing-urls.md` + `affiliate-links.md`，避免两处维护导致按钮链接错误。

---

## 链接格式规范

- **定价页 URL** → 写入 `vendors.json` 的 `urls.pricing`，用于数据采集
- **联盟推广链接** → 写入 `vendors.json` 的 `urls.affiliate`，然后 `plans[].action` 优先使用 `affiliate`，fallback 到 `pricing`
- 统一使用 `?ref=fanluzhe` 或平台指定的邀请参数
- 推广海报统一存放 `assets/posters/`，命名规则 `{平台英文名}.png`
- 所有推广链接必须在此文件登记后才能上线
- 每月结算日前检查链接有效性

---

## 国内平台

| 平台 | 定价页 URL | 联盟推广链接 | 返佣 | 佣金 | 海报 | 提取状态 | 备注 |
|------|-----------|-------------|------|------|------|---------|------|
| 智谱AI | https://open.bigmodel.cn/pricing | https://www.bigmodel.cn/invite?icode=PJ048yz3Fl63Urk70glaphiFMcmMNhdZwR%2F1emOiVXY%3D | 邀请返利 | 待确认 | `assets/posters/zhipu.png` | ✅ API 定价 (51 models) | 新用户注册得 2000万 Tokens；Coding Plan 套餐在控制台 |
| 字节·方舟 | https://www.volcengine.com/ark | 待添加 | 待确认 | 待确认 | — | ❌ 需登录控制台 | 当前 2.5 折活动 |
| Kimi | https://www.kimi.com/membership/pricing | 待添加 | 待确认 | 待确认 | — | ⚠️ 渲染成功，非表格结构 | C 端会员定价；API 定价见 platform.kimi.com |
| MiniMax | https://platform.minimaxi.com/docs/guides/pricing-token-plan | https://platform.minimaxi.com/subscribe/token-plan?code=Gbn3DuotEx&source=link | 邀请返利 | 10% 返利 + 社区特权 | `assets/posters/minimax.png` | ✅ Token Plan Plus ¥49 / Max ¥119 / Ultra ¥469 | 好友享 9折 + Builder 权益 |
| 阿里·百炼 | https://www.aliyun.com/benefit/scene/tokenplan | 待添加 | 可能有 | 待确认 | — | ❌ console SPA | 阿里云 Token Plan 活动页；控制台需登录 |
| 腾讯云 TokenHub | https://cloud.tencent.com/document/product/1823/130092 | 待添加 | 可能有 | 待确认 | — | ✅ Coding Plan Lite ¥40 / Pro ¥200 | 腾讯云有云推荐奖励 |
| 百度·千帆 | https://cloud.baidu.com/product-s/qianfan_home | 待添加 | 待确认 | 待确认 | — | 待探测 | Token Plan 个人版 |
| 华为云 CodeArts | https://www.huaweicloud.com/product/codearts.html | 待添加 | 待确认 | 待确认 | — | 待探测 | 基础版 ¥60 / 专业版 ¥200 / 企业版 ¥600 |
| 硅基流动 | https://siliconflow.cn/pricing | https://cloud.siliconflow.cn/i/dScpIlvS | 邀请返利 | 双方各得额度 | `assets/posters/siliconflow.png` | 待探测 | 按量调用，无订阅套餐，常用作比价基准 |
| 千问AI | https://platform.qianwenai.com/pricing/token-plan | 待添加 | 待确认 | 待确认 | — | 待探测 | 阿里通义千问 Token Plan 平台 |
| 小米·MiMo | https://platform.xiaomimimo.com | https://platform.xiaomimimo.com?ref=NB2PJ5 | 邀请返利 | 双方各得 ¥10 体验金 + 首单 9 折 | `assets/posters/mimo.png` | 需登录控制台 | 注册自动填入，体验金 40 天有效 |
| DeepSeek 官方 | https://api-docs.deepseek.com/quick_start/pricing | 无（无推广体系） | — | — | — | ✅ API 定价 (2 models) | 无订阅套餐，codingplan-saver 按 API 价格折算"虚拟套餐" |

### 需登录控制台查看定价

| 平台 | 入口 URL | 类型 | 备注 |
|------|---------|------|------|
| 京东云 | https://www.jdcloud.com/ | Coding Plan | 京东云首页，搜索"AI Coding"找到对应产品 |

---

## 海外平台

| 平台 | 定价页 URL | 联盟推广链接 | 返佣 | 佣金 | 海报 | 提取状态 | 备注 |
|------|-----------|-------------|------|------|------|---------|------|
| Claude | https://claude.com/pricing | 待添加 | 待确认 | 待确认 | — | 待探测 | Pro $20/月 · Max $100/月 |
| ChatGPT / Codex | https://openai.com/chatgpt/pricing/ | 待添加 | 待确认 | 待确认 | — | ❌ SPA + 反爬（403） | Plus $20/月 · Pro $200/月 |
| GitHub Copilot | https://github.com/features/copilot/plans | 待添加 | 待确认 | 待确认 | — | 待探测 | Free · Pro $10/月 · Business $19/月 |
| Cursor | https://cursor.com/pricing | 待添加 | 待确认 | 待确认 | — | 待探测 | 有 referral program |
| Devin | https://devin.ai/pricing | 待添加 | 待确认 | 待确认 | — | 待探测 | Free · Pro $20/月 · Max $200/月 |
| Replit | https://replit.com/pricing | 待添加 | 待确认 | 待确认 | — | 待探测 | Starter Free · Core $25/月 |
| Google Gemini | https://gemini.google.com/ | 待添加 | 待确认 | 待确认 | — | 待探测 | Google One AI Premium $19.99/月 |
| Amazon Q | https://aws.amazon.com/q/developer/pricing/ | 待添加 | 待确认 | 待确认 | — | 待探测 | Free · Pro $19/用户/月 |
| Mistral | https://mistral.ai/pricing | 待添加 | 待确认 | 待确认 | — | 待探测 | API 按量 + 企业订阅 |
| JetBrains AI | https://www.jetbrains.com/ai/ | 待添加 | 待确认 | 待确认 | — | 待探测 | AI Assistant 订阅（IDE 内） |
| Tabnine | https://www.tabnine.com/pricing | 待添加 | 待确认 | 待确认 | — | 待探测 | 支持本地模型部署 |
| Ollama | https://ollama.com/ | 待添加 | 待确认 | 待确认 | — | 待探测 | Pro $20/月 · Max $100/月 |

---

## 国内平台返佣情况摸底

> 国内 AI 平台推广体系尚不成熟，多数没有公开的 affiliate program。

| 平台 | 推广体系 | 说明 |
|------|---------|------|
| MiniMax | ✅ 邀请返利 | 好友订阅 9折，邀请人 10% 返利 + 社区特权 |
| 小米·MiMo | ✅ 邀请返利 | 双方各得 ¥10 体验金 + 首单 9 折 |
| 硅基流动 | ✅ 邀请返利 | 邀请链接注册，双方各得额度 |
| 智谱AI | ✅ 邀请返利 | 新用户注册得 2000万 Tokens，邀请人返利待确认 |
| 字节·方舟 | ❓ 待确认 | |
| 阿里·百炼 | 可能有 | 阿里云有推广返佣体系 |
| 腾讯云 | 可能有 | 腾讯云有云推荐奖励 |
| 其他 | ❌ 大概率无 | 多数国内平台无公开 affiliate |

---

## 结算记录

| 日期 | 平台 | 金额 | 备注 |
|------|------|------|------|
| 待记录 | | | |

---

## 数据文件映射

| 本表字段 | 写入位置 | 用途 |
|---------|---------|------|
| 定价页 URL | `vendors.json` → `urls.pricing` | 数据采集（collector） |
| 联盟推广链接 | `vendors.json` → `urls.affiliate` | "优惠购买"按钮（HTML） |
| 返佣/佣金 | 仅本文档 | 结算参考 |
| 提取状态 | `vendors.json` → `extractStrategy` / `lastVerified` | 采集策略 |

> **规则：`plans[].action` 优先取 `vendors[].urls.affiliate`，为空时 fallback 到 `vendors[].urls.pricing`。**
> 构建脚本 `build.py` 或 AI 在生成 plans.json 时负责此映射。

---

## 变更记录

| 日期 | 变更 |
|------|------|
| 2026-07-22 | 合并 `pricing-urls.md` + `affiliate-links.md` → 本文件；修正 plans.json action 字段用联盟链接 |
| 2026-07-21 | 原始两文件分别更新 |