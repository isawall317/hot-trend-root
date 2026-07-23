# 厂商与工具数据源

> **定位**：本项目追踪的所有厂商和工具的源头清单。**只记录输入，不记录爬取结果。**
> 爬取到的价格、套餐、模型等数据见 `plans.json` / `tools.json`。
> 最后更新：2026-07-23 | 维护者：Frank + Claude Code

---

## 一、AI 模型厂商

> 定价页 URL 用于采集，推广链接用于"优惠购买"按钮。新增厂商先在此登记，再更新 `vendors.json`。

| ID | 厂商 | 定价页 URL | 官网 | 提取策略 | 推广链接 | 备注 |
|----|------|-----------|------|:--:|------|------|
| zhipu | 智谱AI | open.bigmodel.cn/pricing | bigmodel.cn | Playwright | bigmodel.cn/invite?icode=PJ048yz3F... | 注册推广，新用户得 2000万 Tokens |
| deepseek | DeepSeek | api-docs.deepseek.com/quick_start/pricing | deepseek.com | BS4 静态 | 无推广体系 | — |
| kimi | Kimi | platform.kimi.com/docs/pricing/chat | kimi.com | Playwright | kimi-bot.com/.../A6EDXY | 注册推广，返佣待确认 |
| minimax | MiniMax | platform.minimaxi.com/docs/guides/pricing-token-plan | minimaxi.com | BS4 静态 | platform.minimaxi.com/.../Gbn3DuotEx | Token Plan 推广，好友 9折 + 10% 返利 |
| tencent | 腾讯云 | cloud.tencent.com/product/tokenhub | cloud.tencent.com | BS4 静态 | 待添加 | 云推荐奖励 |
| claude | Claude | claude.com/pricing | claude.com | Playwright | 待添加 | 待确认 |
| github | GitHub | github.com/features/copilot/plans | github.com | Playwright | 待添加 | 待确认 |
| bytedance | 字节·方舟 | volcengine.com/ark | volcengine.com | manual | 待添加 | Bot 检测拦截 |
| bailian | 阿里·百炼 | bailian.console.aliyun.com | bailian.aliyun.com | manual | 待添加 | 需登录控制台；阿里云推广返佣 |
| codex | Codex(OpenAI) | openai.com/chatgpt/pricing | openai.com | manual | 待添加 | Cloudflare 拦截 |
| mimo | 小米·MiMo | platform.xiaomimomo.com/token-plan | xiaomimomo.com | manual | platform.xiaomimomo.com?ref=NB2PJ5 | V2.5 已上线；注册推广，双方各得 ¥10 体验金 + 首单 9 折；MiMoCode: mimo.xiaomi.com/zh/mimocode；API 按量: mimo.mi.com/docs/zh-CN/price/pay-as-you-go |
| opencode | OpenCode | opencode.ai/zh/go | opencode.ai | manual | 待添加 | 待确认提取策略 |
| jd | 京东云 | jdcloud.com/cn/pages/codingplan | jdcloud.com | manual | 待添加 | 待确认 |

提取策略：`Playwright` = 渲染 SPA 后解析 | `BS4 静态` = 直接解析文档页 | `manual` = 人工定期检查

### 待接入

| ID | 厂商 | 定价页 URL |
|----|------|-----------|
| baidu | 百度·千帆 | — |
| xunfei | 讯飞·星火 | — |
| huawei | 华为云 | — |
| ollama | Ollama | — |
| taotoken | TaoToken | — |

---

## 二、AI 编程工具

> 新增工具先在此登记，再更新 `tools.json`。

| ID | 工具名 | 厂商 | 分类 | 形态 | 官网 | 工具页 | 推广链接 | 备注 |
|----|--------|------|:--:|:--:|------|------|------|------|
| codegeex | CodeGeeX | 智谱AI | 国内·厂商 | IDE | bigmodel.cn | — | — | GLM 系列集成 |
| trae | Trae | 字节·方舟 | 国内·厂商 | IDE | volcengine.com | trae.ai | — | 国内模型最全 |
| deepseek-coder | DeepSeek Coder | DeepSeek | 国内·厂商 | CLI | deepseek.com | api-docs.deepseek.com | — | API 成本最低 |
| kimi-code | Kimi Code | Kimi | 国内·厂商 | ❓ | kimi.com | kimi.com/code/zh | 同 Kimi | 待确认形态 |
| tongyi-lingma | 通义灵码 | 阿里·百炼 | 国内·厂商 | IDE | aliyun.com | — | — | 通义系列集成 |
| codebuddy | CodeBuddy | 腾讯云 | 国内·厂商 | ❓ | cloud.tencent.com | workbuddy.cn | — | 腾讯 AI 代码助手 |
| baidu-comate | 百度 Comate | 百度·千帆 | 国内·厂商 | IDE | baidu.com | — | — | 文心快码 |
| iflycode | iFlyCode | 讯飞·星火 | 国内·厂商 | IDE | xfyun.cn | — | — | — |
| minimax-code | MiniMax Code | MiniMax | 国内·厂商 | ❓ | minimaxi.com | agent.minimaxi.com/download | — | 待确认形态 |
| mimo-code | MiMo Code | 小米·MiMo | 国内·厂商 | ❓ | xiaomimomo.com | mimo.xiaomi.com/zh/mimocode | 同 MiMo | 待确认形态 |
| zcode | ZCode | 独立 | 国内·独立 | CLI | — | — | — | 中文优化，零配置 |
| qoder | Qoder | 独立 | 国内·独立 | CLI | — | — | — | 社区开源，国内模型支持全 |
| claude-code | Claude Code | Anthropic | 海外 | CLI | anthropic.com | claude.com/claude-code | — | 编程标杆 |
| cursor | Cursor | Anysphere | 海外 | IDE | anysphere.com | cursor.com | — | 500万用户 |
| github-copilot | GitHub Copilot | Microsoft | 海外 | IDE | github.com | github.com/features/copilot | — | 用户量最大 |
| codex-cli | Codex CLI | OpenAI | 海外 | CLI | openai.com | openai.com/codex | — | GPT-5.6 独占 |
| windsurf | Windsurf | Codeium | 海外 | IDE | codeium.com | windsurf.com | — | Flow 自动编程 |
| opencode | OpenCode | 社区 | 海外 | CLI | opencode.ai | github.com/opencode-ai | — | 开源最活跃 |

---

## 三、更新规则

1. **新增厂商/工具** → 先在此文件登记 → Frank 确认 → 更新对应 JSON
2. **URL 变更**（定价页/官网/推广链接）→ 改此文件 → 同步更新 JSON
3. **形态 ❓** 待确认 → Frank 确认后改；**分类** 按 `国内·厂商` / `国内·独立` / `海外` 维护

---

## 四、结算记录

| 日期 | 平台 | 金额 | 备注 |
|------|------|------|------|
| 待记录 | | | |