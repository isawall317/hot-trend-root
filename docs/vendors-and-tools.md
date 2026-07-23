# 厂商与工具数据源

> **定位**：本项目所有数据采集的源头。新增厂商/工具、修改 URL、更新推广链接，都先改这里。
> 最后更新：2026-07-23
> 维护者：Frank + Claude Code

---

## 链接格式规范

- **定价页 URL** → 写入 `vendors.json` 的 `urls.pricing`，用于数据采集
- **联盟推广链接** → 写入 `vendors.json` 的 `urls.affiliate`，`plans[].action` 优先使用
- 统一使用 `?ref=fanluzhe` 或平台指定的邀请参数
- 所有推广链接必须在此文件登记后才能上线

---

## 一、AI 模型厂商（codingplan-saver 消费）

### 自动提取（7 家）

| ID | 厂商 | 定价页 URL | 提取方案 | 套餐 | 推广链接 | 返佣 | 最后验证 |
|----|------|-----------|---------|------|---------|------|---------|
| zhipu | 智谱AI | open.bigmodel.cn/pricing | Playwright | Lite ¥49 / Pro ¥149 / Max ¥469 | bigmodel.cn/invite?icode=PJ048yz3F... | 新用户注册得 2000万 Tokens | 2026-07-21 |
| deepseek | DeepSeek | api-docs.deepseek.com/quick_start/pricing | BS4 静态 | 虚拟套餐 ¥40 / ¥200 | 无推广体系 | — | 2026-07-21 |
| kimi | Kimi | platform.kimi.com/docs/pricing/chat | Playwright | Andante ¥49 / Allegretto ¥199 (paused) | kimi-bot.com/.../A6EDXY | 待确认 | 2026-07-21 |
| minimax | MiniMax | platform.minimaxi.com/docs/guides/pricing-token-plan | BS4 静态 | Plus ¥49 / Max ¥119 / Ultra ¥469 | platform.minimaxi.com/.../Gbn3DuotEx | 好友 9折，邀请人 10% 返利 | 2026-07-21 |
| tencent | 腾讯云 | cloud.tencent.com/product/tokenhub | BS4 静态 | Lite ¥40 / Pro ¥200 | 待添加 | 云推荐奖励 | 2026-07-21 |
| claude | Claude | claude.com/pricing | Playwright | Pro $20 / Max $100 | 待添加 | 待确认 | — |
| github | GitHub | github.com/features/copilot/plans | Playwright | Free $0 / Pro $10 / Pro+ $39 / Max $100 | 待添加 | 待确认 | — |

### 手动维护（4 家）

| ID | 厂商 | 定价页 URL | 套餐 | 原因 | 推广链接 | 最后验证 |
|----|------|-----------|------|------|---------|---------|
| bytedance | 字节·方舟 | volcengine.com/ark | Lite ¥40 / Pro ¥200 | Bot 检测拦截 | 待添加 | 2026-07-21 |
| bailian | 阿里·百炼 | bailian.console.aliyun.com | Pro ¥200 | 需登录控制台 | 待添加 | — |
| codex | Codex(OpenAI) | openai.com/chatgpt/pricing | Plus $20 | Cloudflare 拦截 | 待添加 | — |
| mimo | 小米·MiMo | platform.xiaomimomo.com/token-plan | Lite ¥39 / Pro ¥329 | SPA，待适配 | platform.xiaomimomo.com?ref=NB2PJ5 | 双方各得 ¥10 体验金 + 首单 9 折 |

### 小米·MiMo 详细 URL

| 用途 | URL |
|------|-----|
| Token Plan 订阅 | https://platform.xiaomimomo.com/token-plan |
| MiMoCode 主页 | https://mimo.xiaomi.com/zh/mimocode |
| API 按量计费 | https://mimo.mi.com/docs/zh-CN/price/pay-as-you-go |

> V2 系列已于 2026.6.30 下线，V2.5 系列已上线。Token Plan 页当前只展示 Max 年付套餐。

### 待接入厂商（7 家）

| ID | 厂商 | 定价页 URL | 状态 |
|----|------|-----------|------|
| baidu | 百度·千帆 | — | 待采集 |
| xunfei | 讯飞·星火 | — | 待采集 |
| huawei | 华为云 | — | 待采集 |
| jd | 京东云 | — | 待采集 |
| opencode | OpenCode | — | 待采集 |
| ollama | Ollama | — | 待采集 |
| taotoken | TaoToken | — | 待采集 |

> 完整 Schema 见 `project/codingplan-saver/data/SCHEMA.md`。提取策略：`docs`=静态文档页解析，`api`=JSON API，`manual`=手动维护。

---

## 二、AI 编程工具（coding-tools 消费）

### 国内 — 模型厂商自有（10 家）

| ID | 厂商 | 工具名 | 形态 | 官网 | 推广链接 | 备注 |
|----|------|--------|:--:|------|---------|------|
| codegeex | 智谱AI | CodeGeeX | IDE | — | — | GLM 系列集成 |
| trae | 字节·方舟 | Trae | IDE | — | — | 国内模型最全 |
| deepseek-coder | DeepSeek | DeepSeek Coder | CLI | — | — | API 成本最低 |
| kimi-code | Kimi | Kimi Code | ❓ | kimi.com/code/zh | kimi-bot.com/...?invitation_code=A6EDXY | 待确认 |
| tongyi-lingma | 阿里·百炼 | 通义灵码 | IDE | — | — | 通义系列集成 |
| codebuddy | 腾讯云 | CodeBuddy | ❓ | workbuddy.cn | — | 腾讯AI代码助手 |
| baidu-comate | 百度·千帆 | 百度 Comate | IDE | — | — | 文心快码 |
| iflycode | 讯飞·星火 | iFlyCode | IDE | — | — | — |
| minimax-code | MiniMax | MiniMax Code | ❓ | agent.minimaxi.com/download | — | 待确认 |
| mimo-code | 小米·MiMo | MiMo Code | ❓ | mimo.xiaomi.com/zh/mimocode | — | 待确认 |

### 国内 — 独立/社区（2 家）

| ID | 工具名 | 形态 | 官网 | 备注 |
|----|--------|:--:|------|------|
| zcode | ZCode | CLI | — | 中文优化，零配置 |
| qoder | Qoder | CLI | — | 社区开源，国内模型支持全 |

### 海外 — 头部精选（6 家）

| ID | 工具名 | 厂商 | 形态 | 官网 | 备注 |
|----|--------|------|:--:|------|------|
| claude-code | Claude Code | Anthropic | CLI | claude.com/claude-code | 编程标杆 |
| cursor | Cursor | Anysphere | IDE | cursor.com | 500万用户 |
| github-copilot | GitHub Copilot | Microsoft | IDE | github.com/features/copilot | 用户量最大 |
| codex-cli | Codex CLI | OpenAI | CLI | openai.com/codex | GPT-5.6独占 |
| windsurf | Windsurf | Codeium | IDE | windsurf.com | Flow自动编程 |
| opencode | OpenCode | 社区 | CLI | github.com/opencode-ai | 开源最活跃 |

---

## 三、推广链接汇总

> 全部推广链接集中管理，方便统一替换和追踪。

| 厂商 | 产品 | 推广链接 | 类型 | 返佣 |
|------|------|---------|------|------|
| 智谱AI | 智谱AI（C端） | bigmodel.cn/invite?icode=PJ048yz3Fl63Urk70glaphiFMcmMNhdZwR%2F1emOiVXY%3D | 注册推广 | 新用户注册得 2000万 Tokens |
| Kimi | Kimi（C端） | kimi-bot.com/activities/zh-cn/viral-referral/share?scenario=invite&from=share_poster&invitation_code=A6EDXY | 注册推广 | 待确认 |
| Kimi | Kimi Code | 同上 | 注册推广 | 待确认 |
| MiniMax | MiniMax | platform.minimaxi.com/subscribe/token-plan?code=Gbn3DuotEx&source=link | Token Plan 推广 | 好友 9折，邀请人 10% 返利 |
| 小米·MiMo | MiMo | platform.xiaomimomo.com?ref=NB2PJ5 | 注册推广 | 双方各得 ¥10 体验金 + 首单 9 折 |
| 字节·方舟 | 方舟 | 待添加 | 待确认 | 待确认 |
| 阿里·百炼 | 百炼 | 待添加 | 阿里云推广返佣 | 待确认 |
| 腾讯云 | 腾讯云 | 待添加 | 云推荐奖励 | 待确认 |
| Claude | Claude | 待添加 | 待确认 | 待确认 |
| GitHub | GitHub | 待添加 | 待确认 | 待确认 |
| DeepSeek | DeepSeek | 无推广体系 | — | — |
| Codex | Codex | 待添加 | 待确认 | 待确认 |

---

## 四、待采集字段（coding-tools 每款工具）

| 维度 | 字段 | 说明 |
|------|------|------|
| 基本信息 | name, vendor, type, websiteUrl | 名称、厂商、CLI/IDE/桌面/插件、官网 |
| 定价 | pricing, freeTier, paidPlans | 免费额度、付费套餐、与 Coding Plan 关系 |
| 模型集成 | modelIntegration | 支持的自有模型 + 三方模型 |
| 功能 | features[] | Agent模式、MCP、多文件编辑、Git、终端等 |
| 平台 | platforms[] | Mac/Win/Linux/Web/VS Code/JetBrains |
| 优势/不足 | strengths[], weaknesses[] | 每条 ≤25 字 |
| 适用场景 | bestFor[] | 什么类型开发最适合 |
| 评分 | rating(1-5) | 主观综合评分 |

---

## 五、数据文件映射

| 数据 | 存储位置 | 用途 |
|------|---------|------|
| 厂商元信息 | `project/codingplan-saver/data/vendors.json` | 采集策略、URL、配色 |
| 套餐价格 | `project/codingplan-saver/data/plans.json` | HTML 渲染数据源 |
| 变动时间线 | `project/codingplan-saver/data/changes.json` | 推荐页"最近变动" |
| 站点配置 | `project/codingplan-saver/data/site.json` | 博主信息、推荐分组、社群 |
| 编程工具 | `project/coding-tools/data/tools.json` | 工具对比数据源 |
| 推广链接 | `project/coding-tools/data/affiliates.json` | 工具推广链接 |
| 数据 Schema | `project/codingplan-saver/data/SCHEMA.md` | 字段定义 + 枚举 |

---

## 六、更新规则

1. **新增厂商/工具** → 先加到此文件 → 再到各项目 data/ 下更新对应 JSON
2. **URL 变更** → 改此文件 → 同步更新项目 JSON
3. **推广链接** → 集中登记在第三部分 → 各项目引用
4. **形态待确认**的 5 款（Kimi Code / CodeBuddy / MiniMax Code / MiMo Code / ZCode / Qoder）→ Frank 确认后把 ❓ 改为 CLI/IDE/桌面/插件
5. **新增联盟链接** → 先在此文件登记 → 更新 `vendors.json` 和 `plans.json`

---

## 七、结算记录

| 日期 | 平台 | 金额 | 备注 |
|------|------|------|------|
| 待记录 | | | |

---

## 八、变更记录

| 日期 | 变更 |
|------|------|
| 2026-07-23 | 合并 vendors-reference.md 内容：新增返佣详情、MiMo URL、链接格式规范、数据文件映射、结算记录；数据架构文档拆分为独立 `data-architecture.md` |
| 2026-07-22 | 初始版本：厂商 + 工具 + 推广链接 + 待采集字段 |