# CodingPlan Saver 数据 Schema

> **本文件是数据更新的"宪法"。** AI 更新任何 JSON 前必须对照此文档，用户 review 数据时也以此为准。
>
> Schema 由「页面要展示什么」×「数据源能拿到什么」共同决定，按需迭代。
> 任何字段变更先改这里，再改 JSON。

## 文件职责

| 文件 | 职责 | 更新方式 | 页面消费 |
|------|------|---------|---------|
| `site.json` | 站点级配置（博主信息、推荐、社群） | 手动 | 所有 Tab 的 Nav / Footer / 推荐分组 / 社群卡 |
| `vendors.json` | 厂商元信息（URL、提取策略） | 半自动（人 review URL） | 散点图配色、详情链接 |
| `plans.json` | 套餐主数据 | 半自动（核心更新对象） | Top3、对比表、散点图 |
| `changes.json` | 变动时间线（价格/模型/文章统一） | 半自动 | "动态" Tab 时间线 |
| `history/` | plans.json 历史快照 | 自动（每次 update 前快照） | 未来价格走势（暂未用） |

---

## site.json

站点配置，全部手动维护。从 V1 `config.json` 精简而来（去掉了 `nav` 和 `site.url`，HTML Tab 内部路由不需要这些）。

### 顶层结构

```jsonc
{
  "name": "...",
  "tagline": "...",
  "domain": "...",
  "logo": "...",
  "primaryColor": "...",
  "accentColor": "...",
  "blogger": { ... },
  "header": { ... },
  "quickEntries": [ ... ],
  "recommendationGroups": [ ... ],
  "community": { ... },
  "disclosure": "...",
  "footer": { ... }
}
```

### 字段说明

| 字段 | 类型 | 用途 | 必填 |
|------|------|------|------|
| `name` | string | 站点名（Nav brand） | ✓ |
| `tagline` | string | Hero 副标题 | ✓ |
| `domain` | string | 域名（暂未用） | |
| `logo` | string | 单字 logo（Nav brand 前缀） | ✓ |
| `primaryColor` | string | CSS 主色（如 `#10b981`） | ✓ |
| `accentColor` | string | CSS 强调色 | ✓ |
| `blogger` | object | 博主信息 | ✓ |
| `header` | object | Hero 区配置 | ✓ |
| `quickEntries` | array | 场景卡片（推荐 Tab） | ✓ |
| `recommendationGroups` | array | 博主推荐分组（推荐 Tab） | ✓ |
| `community` | object | 社群卡（社群 Tab） | ✓ |
| `disclosure` | string | 披露声明（Footer） | ✓ |
| `footer` | object | Footer 配置 | ✓ |

### `blogger` 结构

```jsonc
{
  "name": "饭庐者说",
  "avatar": "FL",                    // 双字符 avatar
  "title": "AI 工具重度用户 / 独立博主",
  "bio": "...",
  "platforms": [
    { "name": "公众号", "handle": "饭庐者说", "url": "#" }
  ]
}
```

### `header` 结构

```jsonc
{
  "updateDate": "更新于 2026.7.20",   // 显示用，非 ISO 格式
  "highlights": "本周关注：...",       // Hero 区高亮文字
  "stats": [
    { "label": "覆盖平台", "value": "20", "unit": "家" }
  ]
}
```

### `quickEntries[]` 结构（场景卡片）

```jsonc
{
  "id": "budget-under-50",            // 唯一 id
  "icon": "¥",                         // 卡片左上角 icon
  "title": "预算 50 元以内",
  "desc": "学生党 / 体验党",
  "filter": {                          // 点击后跳对比 Tab 的筛选条件
    "monthlyPriceMax": 50,             // 可选：月费上限
    "model": "GLM-5.2",                // 可选：模型筛选
    "tag": "无需抢购",                 // 可选：标签筛选
    "vendor": "智谱AI"                 // 可选：厂商筛选
  }
}
```

### `recommendationGroups[]` 结构（博主推荐分组）

```jsonc
{
  "id": "best-overall",
  "title": "综合推荐",
  "subtitle": "...",
  "items": [
    {
      "vendor": "智谱AI",              // 必须对齐 vendors.json 的 name
      "plan": "Pro",                   // 必须对齐 plans.json 的 plan
      "rating": 5,                     // 1-5
      "verdict": "我的主力套餐",
      "reasons": [                      // 支持简单 markdown: **加粗** [链接](url)
        "GLM-5.2 模型 T0 级别",
        "**需要抢购**，加群交流"
      ],
      "action": "https://..."          // 可选，覆盖 plan 的 action
    }
  ]
}
```

### `community` 结构

```jsonc
{
  "free": {
    "title": "免费微信群",
    "subtitle": "每周价格变动推送",
    "description": "...",
    "qrImage": "",                     // 可选，二维码图片 URL
    "highlights": ["每周价格变动速报", ...],
    "ctaText": "扫码进免费群"
  },
  "paid": {
    "title": "知识星球",
    "subtitle": "¥199/年（早鸟价 ¥99）",
    "description": "...",
    "highlights": [...],
    "ctaText": "加入知识星球",
    "url": "#"                          // 必填，付费社群链接
  }
}
```

---

## vendors.json

厂商元信息，决定每家厂商的数据怎么采、HTML 散点图怎么配色。

### 结构（数组）

```jsonc
[
  {
    "id": "zhipu",                      // 唯一标识，对齐 plans.json 的 vendorId
    "name": "智谱AI",                    // 显示名，对齐 plans.json 的 vendor
    "logo": "智",                        // 单字 logo（HTML 卡片用，可空）
    "color": "#F5F527",                  // 散点图配色
    "urls": {
      "pricing": "https://...",          // 人看的定价页
      "docs": "https://...",             // httpx 提取目标：静态文档页（可空字符串）
      "api": "https://...",              // httpx 提取目标：API JSON 端点（可空字符串）
      "home": "https://open.bigmodel.cn"
    },
    "extractStrategy": "manual",         // httpx | docs | api | manual（见下方枚举）
    "lastVerified": null,                // ISO 日期，最后实测日
    "notes": "SPA 控制台，文档页可提取"
  }
]
```

### `extractStrategy` 枚举

| 值 | 含义 | sources/ 模块行为 |
|----|------|------------------|
| `api` | 厂商提供 JSON API 端点 | httpx 直接拿 JSON，最稳 |
| `docs` | 静态文档页 | httpx + BeautifulSoup 解析 |
| `httpx` | 旧值，等同 docs（兼容） | 同 docs |
| `manual` | 无可靠源 | runner 跳过，只接收人喂的信号 |

**决策树**（runner 内部按此顺序判断）：
1. `urls.api` 非空 → 走 api 策略
2. `urls.docs` 非空 → 走 docs 策略
3. 都空 → 走 manual（跳过）

---

## plans.json

套餐主数据。半自动更新核心——人喂信号 + AI 草拟变更 + diff 确认。

### 结构（数组）

```jsonc
{
  "id": "zhipu-pro",                   // {vendorId}-{plan-lower} 全局唯一
  "vendor": "智谱AI",                   // 对齐 vendors.json 的 name
  "vendorId": "zhipu",                  // 对齐 vendors.json 的 id
  "plan": "Pro",
  "type": "Coding Plan",                // 枚举: 见下方 type 表
  "tier": "pro",                        // 枚举: lite | pro | max（便于分组排序）
  "monthlyPrice": 149,
  "currency": "¥",                      // ¥ | $
  "firstMonthPrice": 141.55,            // 可选，首月价（有则展示）
  "rating": 5,                          // 1-5，博主主观评分
  "models": ["GLM-5.1", "GLM-5.2"],
  "monthlyRequests": 120000,            // Coding Plan 才有
  "tokenLimit": null,                   // Token Plan 才有（字符串如 "10M Tokens" 或 null）
  "measuredMonthlyToken": 600,          // token_estimator 自动补（单位 M）；散点图/每元Token 列依赖
  "tags": ["模型强", "需抢购"],          // 字符串数组
  "bloggerVerdict": "我的主力套餐...",   // 博主点评
  "action": "https://open.bigmodel.cn/pricing",  // 套餐购买/详情页 URL
  "status": "active",                   // 枚举: active | paused | sold_out | deprecated
  "source": "manual",                   // 数据来源追溯: manual | extracted-{vendorId}
  "updatedAt": "2026-07-20",            // ISO 日期
  // —— 以下为画像层字段（kb_migrate 透传到 aikb/database/services.json）——
  "category": "model-maker",            // 枚举: model-maker | cloud-maas | aggregator | vertical-cloud（对齐 vendors.json）
  "billingCore": "token",               // 枚举: token | request（核心计费维度）
  "migration": "⚠️ 连续涨价 200%+",     // 可选，自由文本，迁移/计费变动提示
  "notes": "..."                        // 可选，自由文本，数据质量/估算说明（如 measuredMonthlyToken 为估算值）
}
```

### `type` 枚举与分类逻辑

| type | 含义 | 计费方式 | 典型厂商 | 适用场景 |
|------|------|---------|---------|---------|
| `Coding Plan` | 月订阅，专用于 AI 编程 | 固定月费 | 智谱/腾讯云/Claude/GitHub/Kimi/字节 | Claude Code / Cursor / Codex 用户 |
| `Token Plan` | 月订阅，给 token 额度池，通用场景 | 固定月费 | MiniMax/阿里百炼/小米·MiMo/华为云 | 通用 AI 调用，不限编程 |
| `API 按量` | 无月费，按 token 消耗付费 | 按量后付费 | DeepSeek/OpenRouter/硅基流动 | 弹性用量，测试，不确定用量 |
| `Agent Plan` | 月订阅，专用于 AI Agent 工作流 | 固定月费 | _暂未使用（字节方舟预留）_ | 构建 AI Agent，MCP/工具调用 |

**分类决策树：**
1. 有月费吗？→ 无 → `API 按量`
2. 专用于编程（含 Claude Code/Cursor 等工具）？→ 是 → `Coding Plan`
3. 专用于 Agent 工作流？→ 是 → `Agent Plan`
4. 通用 token 额度池 → `Token Plan`

### `status` 枚举

| 值 | 含义 | HTML 显示 |
|----|------|----------|
| `active` | 在售 | 正常 |
| `paused` | 暂停订阅（如 Kimi 当前状态） | 灰色徽章 |
| `sold_out` | 售罄 | 灰色徽章 |
| `deprecated` | 已下架 | 删除线 + 灰色 |

### `tier` 枚举

| 值 | 含义 |
|----|------|
| `lite` | 入门档（Lite/Mini/Starter） |
| `pro` | 中档（Pro/Plus/标准） |
| `max` | 旗舰档（Max/Ultra/Premium） |

### 运行时计算字段（不存 JSON，HTML 渲染时算）

| 字段 | 公式 | 用途 |
|------|------|------|
| `tokensPerYuan` | `measuredMonthlyToken / monthlyPrice` | 对比表"每元Token"列 |
| `pricePerM` | `monthlyPrice / measuredMonthlyToken` | 对比表"1M Token价"列 |

---

## changes.json

统一变动时间线，合并 V1 的 `price-changes.json` + `articles.json`。

### 结构（数组）

```jsonc
{
  "id": "2026-07-20-kimi-pause",        // {date}-{slug} 全局唯一
  "date": "2026-07-20",                 // ISO 日期
  "kind": "subscription_pause",          // 枚举: 见下方 kind 表
  "vendor": "Kimi",                      // 对齐 vendors.name；可为 "通用"
  "title": "Kimi 暂停 C 端新用户订阅",    // ≤30 字
  "detail": "K3 发布后算力告急...",       // ≤120 字；article 类型可更长
  "impact": "negative",                  // 枚举: positive | negative | neutral
  "level": "high",                       // 枚举: high | medium | low
  "source": "manual",                    // 枚举: manual | signal-dailyhot | signal-rsshub | extracted-{vendorId}
  "sourceUrl": null,                     // 可选，来源链接（article 必有）
  "relatedPlans": ["kimi-moderato"],     // 可选，关联 plan id
  "featured": false,                     // 是否在首页高亮
  // === article 类型额外字段 ===
  "excerpt": null,                       // 文章摘要
  "author": null,                        // 文章来源（36氪/IT之家...）
  "readTime": null,                      // 阅读时长（如 "5 分钟"）
  "cover": null                          // 封面字母标识（K3/DS/NEW/CL 等）
}
```

### `kind` 枚举

| kind | 含义 | 原 price-changes 类型 |
|------|------|----------------------|
| `price_change` | 涨价/降价/计费调整 | "计费调整" / "订阅调整" |
| `new_model` | 新增支持某模型 | "新增模型" / "新模型即将发布" |
| `new_plan` | 新套餐上线 | "新增平台" |
| `subscription_pause` | 暂停订阅 | "暂停订阅" |
| `promotion` | 限时活动/折扣 | _暂未使用_ |
| `outage` | 故障/下架 | _暂未使用_ |
| `article` | 行业文章/资讯 | 原 articles.json |

页面"动态" Tab 的筛选分组：
- **全部**：所有 kind
- **价格**：`price_change` + `promotion`
- **模型**：`new_model` + `new_plan`
- **订阅**：`subscription_pause` + `outage`
- **文章**：`article`

### `source` 枚举

| 值 | 含义 |
|----|------|
| `manual` | 用户直接告知的变动 |
| `signal-dailyhot` | DailyHotApi 科技源关键词命中 |
| `signal-rsshub` | RSSHub feed 命中 |
| `extracted-{vendorId}` | sources/ parser 自动提取发现（如 `extracted-deepseek`） |

---

## 迁移规则（从 V1 数据）

### plans.json 迁移

- V1 `vendor` → 新 `vendor` + 新 `vendorId`（通过 VENDOR_ID_MAP 查表）
- 新增 `id` = `{vendorId}-{plan-lower}`
- 新增 `tier`：根据 plan 名推断（Lite/Mini→lite，Max/Ultra→max，其余→pro）
- 删除 `quarterlyPrice` / `yearlyPrice` / `fiveHoursRequests` / `weeklyRequests`（页面未用）
- `status` 默认 `active`，已知暂停的（Kimi）手工改 `paused`
- `source` 统一设为 `manual`（迁移自人工数据）
- `updatedAt` 设为迁移当天

### changes.json 迁移

- **price-changes** 条目：生成新 id `{date}-{vendor-slug}-{kind}`，kind 按 V1 `type` 字段映射
- **articles** 条目：**保留原 hash id**（避免破坏外链），新增 `kind: "article"` + 其他字段
- 按 `date` 倒序排序

### VENDOR_ID_MAP（迁移用）

```python
VENDOR_ID_MAP = {
    "智谱AI": "zhipu", "智谱国际版": "zhipu-intl",
    "字节·方舟": "bytedance", "DeepSeek 官方": "deepseek",
    "Kimi": "kimi", "MiniMax": "minimax",
    "阿里·百炼": "bailian", "腾讯云": "tencent",
    "Claude": "claude", "Codex (ChatGPT)": "codex", "GitHub": "github",
    "百度·千帆": "baidu", "讯飞·星火": "xunfei",
    "华为云": "huawei", "京东云": "jd",
    "小米·MiMo": "mimo",
    "OpenCode": "opencode",
    "Ollama": "ollama", "TaoToken": "taotoken",
}
```

---

## 迭代规则

1. **页面需求变化** → 先改本文件相应 schema 段 → 再改 JSON 数据 → 最后改 HTML 模板
2. **数据源能力变化**（如某厂商 docs 页结构变了）→ 改对应 `vendors.json` 条目的 `extractStrategy` 和 `notes` → 在 `reference/pricing-urls.md` 记录实测
3. **新增字段** → 先在本文件定义 → 再在 JSON 里加 → 最后在 HTML 模板里消费
4. **删除字段** → 先从 HTML 模板移除消费 → 再从 JSON 清理 → 最后从本文件移除定义
