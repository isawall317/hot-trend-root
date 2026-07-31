# 厂商与工具数据源

> **定位**：本项目追踪的所有厂商和工具的源头清单。
> **本文件由 `kb_to_md.py` 从 `aikb/database/` JSON 自动生成，勿手工编辑。**
> 最后更新：2026-07-31 | 维护者：Frank + Claude Code

---

<!-- KB-AUTO-START -->
## 一、AI 模型厂商

> 定价页 URL 用于采集，推广链接用于"优惠购买"按钮。新增厂商先更新 KB JSON → 重新生成此文件。

| ID | 厂商 | 分类 | 国家 | 定价页 URL | 提取策略 | 推广链接 | 备注 |
|----|------|:--:|:--:|------|:--:|------|------|
| zhipu | 智谱AI | 模型厂商 | 🇨🇳 | https://open.bigmodel.cn/pricing | Playwright | 新用户得 2000万 Tokens | Playwright headless 渲染，提取 API 定价 |
| bytedance | 字节·方舟 | 模型厂商 | 🇨🇳 | https://www.volcengine.com/ark | manual | 待添加 | 火山方舟检测到 bot 返回 404，无法自动提取（手动维护） |
| deepseek | DeepSeek 官方 | 模型厂商 | 🇨🇳 | https://api-docs.deepseek.com/quick_start/pricing | BS4 静态 | 待添加 | httpx + BS4 解析 API 定价 |
| kimi | Kimi | 模型厂商 | 🇨🇳 | https://www.kimi.com/membership/pricing | Playwright | 待添加 | Playwright 渲染 docs 页 → 点击展开模型卡片 → 提取 API 价格 |
| minimax | MiniMax | 模型厂商 | 🇨🇳 | https://platform.minimaxi.com/docs/guides/pricing-token-plan | BS4 静态 | 好友 9折 + 10% 返利 | httpx + BS4 解析 Token Plan 表格 |
| bailian | 阿里·百炼 | 云厂商 MaaS | 🇨🇳 | https://bailian.console.aliyun.com/cn-beijing?tab=doc#/doc/?type=model&url=3028856 | manual | 待添加 | 阿里云百炼需登录控制台，定价页不可公开访问（手动维护） |
| tencent | 腾讯云 | 云厂商 MaaS | 🇨🇳 | https://cloud.tencent.com/product/tokenhub?Is=home | BS4 静态 | 待添加 | httpx + BS4 解析 Coding Plan 文档 |
| claude | Claude | 模型厂商 | 🇺🇸 | https://claude.com/pricing | Playwright | 待添加 | Playwright 渲染 claude.com/pricing → 提取套餐价格 |
| codex | Codex (ChatGPT) | 模型厂商 | 🇺🇸 | https://openai.com/chatgpt/pricing/ | manual | 待添加 | OpenAI 页面被 Cloudflare 拦截，无法自动提取（手动维护） |
| github | GitHub | 聚合商 | 🇺🇸 | https://github.com/features/copilot/plans | Playwright | 待添加 | Playwright 渲染 github.com/features/copilot/plans → 提取套餐价格 |
| mimo | 小米·MiMo | 垂直云 | 🇨🇳 | https://platform.xiaomimimo.com/token-plan | manual | 待添加 | Token Plan 页为 SPA + 按量计费 API 文档页可提取模型价格。V2→V2.5 已迁移。（手动维护） |
| openrouter | OpenRouter | 聚合商 | 🌐 | https://openrouter.ai/pricing | manual | 待添加 | 全球聚合商: 400+ 模型, 70+ 厂商, 统一 API Key, 按量付费 +5.5% 平台费（手动维护） |
| siliconflow | 硅基流动 | 聚合商 | 🇨🇳 | https://siliconflow.cn/pricing | manual | 待添加 | 国内聚合商: 实时价格同步，覆盖美团/智谱/Kimi/DeepSeek/MiniMax/通义/百度/字节等（手动维护） |
| baidu | 百度·千帆 | 云厂商 MaaS | 🇨🇳 | https://cloud.baidu.com/product-s/qianfan_home | manual | 待添加 | 2026-07-10 宣布 Coding Plan → Token Plan 升级迁移，取消高峰限流，调用次数→Toke（手动维护） |
| unicom | 联通云 | 云厂商 MaaS | 🇨🇳 | https://api.dreamfree.space/c/s/cpyqunicomcp | manual | 待添加 | 回填自线上 codingplan.fyi 抢救数据（2026-07-31）（手动维护） |
| huawei | 华为云 | 云厂商 MaaS | 🇨🇳 | https://console.huaweicloud.com/modelarts/?region=cn-southwest-2#/model-studio/resourcePlanManagement | manual | 待添加 | 回填自线上 codingplan.fyi 抢救数据（2026-07-31）（手动维护） |
| xunfei | 讯飞·星火 | 云厂商 MaaS | 🇨🇳 | https://api.dreamfree.space/c/s/cpyqxunfei | manual | 待添加 | 回填自线上 codingplan.fyi 抢救数据（2026-07-31）（手动维护） |
| ctyun | 天翼云 | 云厂商 MaaS | 🇨🇳 | https://api.dreamfree.space/c/s/cpyqctyun | manual | 待添加 | 回填自线上 codingplan.fyi 抢救数据（2026-07-31）（手动维护） |
| stepfun | 阶跃星辰 | 模型厂商 | 🇨🇳 | https://api.dreamfree.space/c/s/cpyqstepfun | manual | 待添加 | 回填自线上 codingplan.fyi 抢救数据（2026-07-31）（手动维护） |
| zhipu-intl | 智谱国际版 | 模型厂商 | 🌐 | https://api.dreamfree.space/c/s/cpyqzai | manual | 待添加 | 回填自线上 codingplan.fyi 抢救数据（2026-07-31）（手动维护） |
| jd | 京东云 | 云厂商 MaaS | 🇨🇳 | https://api.dreamfree.space/c/s/cpyqjingdong | manual | 待添加 | 回填自线上 codingplan.fyi 抢救数据（2026-07-31）（手动维护） |
| cmcc | 移动云 | 云厂商 MaaS | 🇨🇳 | https://api.dreamfree.space/c/s/cpyqmobilecp | manual | 待添加 | 回填自线上 codingplan.fyi 抢救数据（2026-07-31）（手动维护） |
| infini | 无问芯穹 | 聚合商 | 🇨🇳 | https://api.dreamfree.space/c/s/cpyqinfini | manual | 待添加 | 回填自线上 codingplan.fyi 抢救数据（2026-07-31）（手动维护） |
| taotoken | TaoToken | 聚合商 | 🇨🇳 | https://api.dreamfree.space/c/s/cpyqtaotoken | manual | 待添加 | 回填自线上 codingplan.fyi 抢救数据（2026-07-31）（手动维护） |
| ollama | Ollama | 垂直云 | 🌐 | https://api.dreamfree.space/c/s/cpyqollama | manual | 待添加 | 回填自线上 codingplan.fyi 抢救数据（2026-07-31）（手动维护） |
| opencode | OpenCode | 垂直云 | 🌐 | https://api.dreamfree.space/c/s/cpyqopencode | manual | 待添加 | 回填自线上 codingplan.fyi 抢救数据（2026-07-31）（手动维护） |
| scnet | 超算 | 云厂商 MaaS | 🇨🇳 | https://api.dreamfree.space/c/s/cpyqscnetcp | manual | 待添加 | 回填自线上 codingplan.fyi 抢救数据（2026-07-31）（手动维护） |
| uyun | 优云智算 | 云厂商 MaaS | 🇨🇳 | https://api.dreamfree.space/c/s/cpyqyyzs | manual | 待添加 | 回填自线上 codingplan.fyi 抢救数据（2026-07-31）（手动维护） |

提取策略：`Playwright` = 渲染 SPA 后解析 | `BS4 静态` = 直接解析文档页 | `API` = JSON API | `manual` = 人工定期检查
<!-- KB-AUTO-END -->

<!-- KB-AUTO-START -->
## 二、AI 编程工具

> 新增工具先更新 KB JSON → 重新生成此文件。

| ID | 工具名 | 厂商 | 分类 | 形态 | 官网 | 定价 | 评分 | 备注 |
|----|--------|------|:--:|:--:|------|------|:--:|------|
| claude-code | Claude Code | Anthropic | 海外 | CLI | https://claude.com/claude-code | 免费使用，需自备 API Key 或订阅 Claude Pro($20)/Max | ⭐⭐⭐⭐⭐ | CLI, 国外, MCP |
| codex-cli | Codex CLI | OpenAI | 海外 | CLI | https://openai.com/codex | 免费使用，需自备 API Key 或订阅 ChatGPT Pro($20)/Co | ⭐⭐⭐⭐⭐ | CLI, 国外, GPT |
| gemini-cli | Gemini CLI | Google | 海外 | CLI | https://ai.google.dev | 免费使用，需自备 API Key。Gemini API 有慷慨免费额度（每分钟  | ⭐⭐⭐⭐ | CLI, 国外, 大上下文 |
| opencode | OpenCode | 社区开源 | 海外 | CLI | https://github.com/opencode-ai/opencode | 完全免费开源。需自备 API Key（支持任何 OpenAI 兼容接口）。 | ⭐⭐⭐⭐ | CLI, 开源, 免费 |
| deepseek-coder | DeepSeek Coder | DeepSeek | 国内·厂商 | CLI | https://api-docs.deepseek.com | 免费使用，DeepSeek API 价格极低（输入 ¥0.14/1M token | ⭐⭐⭐⭐ | CLI, 国内友好, 低成本 |
| qoder | Qoder | 社区开源 | 国内·独立 | CLI | https://github.com/qoder-ai/qoder | 免费开源。需自备各厂商 API Key。 | ⭐⭐⭐⭐ | CLI, 国内友好, 开源 |
| workbuddy | WorkBuddy | WorkBuddy Inc | 国内·独立 | CLI | https://workbuddy.dev | 个人免费，团队版 $15/人/月。企业版 $30/人/月。 | ⭐⭐⭐⭐ | CLI, 团队, 企业 |
| zcode | ZCode | ZCode Team | 国内·独立 | CLI | https://zcode.dev | 个人免费（限 100 次/天），Pro ¥39/月（无限次），Team ¥99/ | ⭐⭐⭐⭐ | CLI, 国内友好, 中文 |
| hermes | Hermes | Hermes AI | 海外 | CLI | https://hermes-ai.dev | 免费基础版（安全扫描），Pro $25/月（完整功能），企业版按需定价。 | ⭐⭐⭐⭐ | CLI, 安全, 合规 |
| openclaw | OpenClaw | 社区开源 | 国内·独立 | CLI | https://github.com/openclaw | 完全免费开源。需自备 API Key。 | ⭐⭐⭐ | CLI, 开源, 垂直行业 |
| cursor | Cursor | Cursor Inc | 海外 | IDE | https://cursor.com | Hobby 免费（2000次/月），Pro $20/月，Business $40 | ⭐⭐⭐⭐⭐ | Desktop, IDE, 国外 |
| github-copilot | GitHub Copilot | GitHub(Microsoft) | 海外 | IDE | https://github.com/features/copilot | Free 免费（2000次/月），Pro $10/月，Pro+ $39/月，Ma | ⭐⭐⭐⭐⭐ | Desktop, IDE, 国外 |
| claude-work | Claude Work | Anthropic | 海外 | IDE | https://claude.com/work | 免费公测中。预计正式版集成 Claude Pro/Max 订阅。 | ⭐⭐⭐⭐ | Desktop, 国外, 公测 |
| windsurf | Windsurf | Codeium | 海外 | IDE | https://windsurf.com | Free 免费（基础功能），Pro $15/月，Teams $35/人/月。 | ⭐⭐⭐⭐ | Desktop, IDE, 国外 |
| trae | Trae | 字节跳动 | 国内·厂商 | IDE | https://trae.ai | 国内免费（基础功能），Pro ¥49/月（无限次）。海外版 Trae Pro $ | ⭐⭐⭐⭐ | Desktop, IDE, 国内友好 |
| cline | Cline | 社区开源 | 海外 | IDE | https://github.com/cline/cline | 完全免费开源。需自备 API Key。 | ⭐⭐⭐⭐ | Desktop, VS Code, 开源 |
| continue | Continue | Continue Dev | 海外 | IDE | https://continue.dev | 免费开源。Continue Hub 免费（个人），团队 $20/人/月。 | ⭐⭐⭐⭐ | Desktop, VS Code, JetBrains |
| cody | Cody | Sourcegraph | 海外 | IDE | https://sourcegraph.com/cody | Free 免费（基础功能），Pro $9/月，Enterprise $19/人/ | ⭐⭐⭐⭐ | Desktop, 代码搜索, 大项目 |
| amazon-q | Amazon Q Developer | AWS(Amazon) | 海外 | IDE | https://aws.amazon.com/q/developer | Free Tier 免费（基础功能），Pro $20/月。 | ⭐⭐⭐ | Desktop, AWS, 云 |
| tabnine | Tabnine | Tabnine | 海外 | IDE | https://tabnine.com | Free 免费（基础补全），Pro $12/月，Enterprise 私有部署按 | ⭐⭐⭐ | Desktop, 补全, 企业 |
| replit-ai | Replit AI | Replit | 海外 | Web | https://replit.com | Free 免费（基础功能），Core $25/月，Teams $40/人/月。 | ⭐⭐⭐⭐ | Web, 在线, 快速原型 |
| augment | Augment Code | Augment | 海外 | IDE | https://augmentcode.com | Free 免费（个人），Team $30/人/月，Enterprise 按需定价 | ⭐⭐⭐⭐ | Desktop, 上下文, 大项目 |
| codegeex | CodeGeeX | 智谱AI | 国内·厂商 | IDE | https://bigmodel.cn |  | ⭐⭐⭐ | IDE, 国内, 智谱 |
| kimi-code | Kimi Code | Kimi | 国内·厂商 | UNKNOWN | https://kimi.com/code/zh |  | ⭐⭐⭐ | 国内, Kimi, 待确认 |
| tongyi-lingma | 通义灵码 | 阿里·百炼 | 国内·厂商 | IDE | https://aliyun.com |  | ⭐⭐⭐ | IDE, 国内, 阿里 |
| codebuddy | CodeBuddy | 腾讯云 | 国内·厂商 | UNKNOWN | https://workbuddy.cn |  | ⭐⭐⭐ | 国内, 腾讯, 待确认 |
| baidu-comate | 百度 Comate | 百度·千帆 | 国内·厂商 | IDE | https://baidu.com |  | ⭐⭐⭐ | IDE, 国内, 百度 |
| iflycode | iFlyCode | 讯飞·星火 | 国内·厂商 | IDE | https://xfyun.cn |  | ⭐⭐⭐ | IDE, 国内, 讯飞 |
| minimax-code | MiniMax Code | MiniMax | 国内·厂商 | UNKNOWN | https://agent.minimaxi.com/download |  | ⭐⭐⭐ | 国内, MiniMax, 待确认 |
| mimo-code | MiMo Code | 小米·MiMo | 国内·厂商 | UNKNOWN | https://mimo.xiaomi.com/zh/mimocode |  | ⭐⭐⭐ | 国内, 小米, 待确认 |
| kiro | Kiro | 独立 | 待确认 | UNKNOWN |  |  | ⭐⭐⭐ | 待确认 |
<!-- KB-AUTO-END -->

---

## 三、更新规则

1. **新增厂商/工具** → 更新 `project/codingplan-saver/data/` JSON → 跑 `kb_migrate.py` 同步到 `aikb/database/` → 运行 `python -m collector.kb_to_md` 重新生成此文件
2. **URL 变更** → 更新 project JSON → 跑 kb_migrate → 重新生成
3. **数据变更** → 自动采集管道检测 → `/kb-update review` 审阅 → 更新 project JSON
4. **发现渠道** → 厂商 Token Plan / Coding Plan 页面通常会列出「本套餐支持哪些工具」，这些页面是发现新工具和竞品的最佳入口

---

## 四、结算记录

| 日期 | 平台 | 金额 | 备注 |
|------|------|------|------|
| 待记录 | | | |