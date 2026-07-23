# 厂商知识库 (Knowledge Base)

> **定位**：本项目所有厂商、服务、工具、模型的**唯一结构化真相源**。
> 自动采集 + Claude Code 审阅维护。`docs/vendors-and-tools.md` 由此生成。
> 最后更新：2026-07-23 | 维护者：Frank + Claude Code

---

## 文件职责

| 文件 | 职责 | 更新方式 | 下游消费 |
|------|------|---------|---------|
| `vendors.json` | 厂商画像（URL、分类、提取策略、推广） | 半自动 | 所有项目 |
| `services.json` | 厂商服务/产品（Coding Plan、Token Plan、API 按量） | 自动采集 + 审阅 | codingplan-saver |
| `tools.json` | AI 编程工具详情 | 半自动 | coding-tools |
| `models.json` | 模型清单（厂商→模型→能力） | 自动采集 | model-picker |
| `changes.json` | 统一变更时间线 | 自动检测 + 审阅 | 所有项目动态 Tab |

## 关系

```
vendors ──1:N──→ services ──1:N──→ plans (pricing tiers)
vendors ──1:N──→ models
vendors ──1:N──→ tools
changes ──N:1──→ vendors / services / tools / models
```

---

## vendors.json

### 结构

```jsonc
{
  "id": "zhipu",                      // 唯一标识
  "name": "智谱AI",                    // 显示名
  "logo": "智",                        // 单字 logo
  "color": "#F5F527",                  // 品牌色
  "category": "model-maker",           // model-maker | cloud-maas | aggregator | vertical-cloud
  "country": "cn",                     // cn | us | global
  "urls": {
    "home": "https://open.bigmodel.cn",
    "pricing": "https://open.bigmodel.cn/pricing",
    "docs": "https://open.bigmodel.cn/docs",
    "api": "",
    "console": ""
  },
  "extractStrategy": "playwright",     // playwright | bs4 | api | manual
  "extractStatus": "ok",              // ok | degraded | failed | manual
  "massServices": ["coding-plan", "api-paygo"],  // 提供的 mass 服务类型
  "affiliate": {
    "url": "https://...",
    "type": "referral",               // referral | commission | none
    "benefit": "新用户得 2000万 Tokens"
  },
  "lastVerified": "2026-07-23",
  "notes": "注册推广，新用户得 2000万 Tokens"
}
```

### `category` 枚举

| 值 | 含义 | 示例 |
|----|------|------|
| `model-maker` | 模型厂商（有自己的模型） | 智谱AI, DeepSeek, Kimi, Claude |
| `cloud-maas` | 云厂商 MaaS 平台 | 阿里·百炼, 腾讯云, 百度·千帆 |
| `aggregator` | 聚合商（集成多家模型） | OpenRouter, 硅基流动, GitHub |
| `vertical-cloud` | 垂直云厂商 | 小米·MiMo, 京东云 |

### `massServices[]` 枚举

| 值 | 含义 |
|----|------|
| `coding-plan` | 编程专用月订阅 |
| `token-plan` | 通用 Token 月订阅 |
| `api-paygo` | API 按量付费 |
| `agent-plan` | Agent 专用月订阅 |
| `enterprise` | 企业版/私有部署 |

---

## services.json

### 结构

```jsonc
{
  "id": "zhipu-coding-plan",
  "vendorId": "zhipu",
  "type": "coding-plan",              // coding-plan | token-plan | api-paygo | agent-plan
  "name": "Coding Plan",
  "status": "active",                 // active | paused | deprecated
  "plans": [
    {
      "tier": "lite",                 // lite | pro | max
      "name": "Lite",
      "monthlyPrice": 49,
      "currency": "¥",
      "firstMonthPrice": 46.55,
      "monthlyRequests": 24000,
      "tokenLimit": "无限制",
      "measuredMonthlyToken": 120,
      "rating": 5,
      "models": ["GLM-5.2", "..."],
      "tags": ["模型强", "性价比高"],
      "bloggerVerdict": "...",
      "status": "active"
    }
  ],
  "billingCore": "token",            // token | request
  "migration": "⚠️ 连续涨价 200%+",
  "updatedAt": "2026-07-23",
  "source": "extracted-zhipu"
}
```

---

## tools.json

### 结构

```jsonc
{
  "id": "claude-code",
  "name": "Claude Code",
  "vendorId": "claude",              // 关联 vendors.json
  "vendorName": "Anthropic",
  "type": "cli",                      // cli | ide | plugin | web
  "category": "overseas",            // domestic-vendor | domestic-independent | overseas
  "description": "...",
  "pricing": {
    "model": "freemium",             // free | freemium | subscription | paid
    "detail": "免费使用，需自备 API Key 或订阅 Claude Pro($20)/Max($100)"
  },
  "modelIntegration": ["Claude Opus 4", "..."],
  "features": ["Agent 模式", "MCP 协议", "..."],
  "platforms": ["Mac", "Linux", "Windows(WSL)"],
  "rating": 5,
  "bestFor": ["全栈开发", "架构设计"],
  "strengths": ["..."],
  "weaknesses": ["..."],
  "urls": { "home": "https://claude.com/claude-code", "docs": "" },
  "tags": ["CLI", "国外", "MCP", "必装"],
  "featured": true,
  "trending": false,
  "addedAt": "2025-10-01"
}
```

---

## models.json

### 结构

```jsonc
{
  "id": "glm-5.2",
  "vendorId": "zhipu",
  "name": "GLM-5.2",
  "type": "text",                     // text | vision | code | multimodal | asr | tts
  "releaseDate": "2026-06-15",
  "status": "active"
}
```

---

## changes.json

复用现有 `project/codingplan-saver/data/SCHEMA.md` 中定义的 schema，新增 `source: "kb-auto"` 表示自动检测。

---

## 更新流程

1. **pipeline 采集**（`python -m collector.pipeline`）：
   - 热点采集 → 文章发现 → 价格监控 → 厂商定价提取 → Token 推算
   - **市场发现**（`market_discovery.py`）：热点召回 + 生态页抓取 → `data/signals/market-{date}.json`
   - **KB 同步**（`kb_migrate.py`）：re-sync plans.json 价格 → KB services
   - **KB 变更检测**（`kb_diff.py`）：对比新旧 KB → `data/pending/{date}/kb-changes.json`
2. **Claude Code 审阅**（`/kb-update review`）：读取 kb-changes.json → 高风险逐条确认 → 低风险自动合并
3. **合并**：应用变更到 KB JSON
4. **生成**（`kb_to_md.py`）：更新 `docs/vendors-and-tools.md`

## 从旧数据迁移

迁移脚本：`tools/collector/collector/kb_migrate.py`
源数据：`vendors.json` + `plans.json` + `tools.json` + `vendors-and-tools.md`

## 两个关键脚本

| 脚本 | 用途 | 触发 |
|------|------|------|
| `kb_migrate.py` | 从旧数据源（plans.json 等）迁移/同步到 KB | pipeline 自动调用 |
| `kb_diff.py` | 对比当前 KB vs staging 版，产出变更报告 | pipeline 自动调用 |
| `kb_to_md.py` | 从 KB JSON 生成 `docs/vendors-and-tools.md` | `/kb-update build` 或手动 |
| `market_discovery.py` | 发现 KB 中没有的新厂商/工具候选 | pipeline 自动调用 |