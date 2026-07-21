# build-site Skill 设计文档

> **日期**: 2026-07-21
> **状态**: Draft（待用户 review）
> **作者**: brainstorming 协作产出
> **相关**: 替换现有 `.claude/skills/build-site.md`

---

## 1. 背景与目标

### 1.1 要解决的问题

现有 `project/codingplan-saver/` 有两套并行实现（多页面 HTML + Python 构建器 `build_html.py`），数据维护纯手工，构建链断裂。需要重新设计为：

> **一个 skill，输入是"本周有什么变动"（自然语言 + 自动信号），输出是一个可双击打开的单文件 HTML。**

### 1.2 目标（Must）

1. **单文件交付**：`dist/codingplan-saver.html`，内联所有 CSS/JS/JSON，双击可开
2. **半自动数据更新**：人喂自然语言信号 + collector 自动采集信号，AI 按 schema 归一化、写入 JSON
3. **全自动 HTML 生成**：读 JSON → 套模板 → 输出，无构建依赖
4. **URL 文档化维护**：供应商定价页 URL 集中在一份文档，用户 review，实测反馈记录

### 1.3 非目标（Won't）

- ❌ 不做实时联网搜索（当前环境 WebSearch/webReader 配额受限）
- ❌ 不依赖 Playwright/浏览器（除非未来某家厂商彻底没有静态/API 源）
- ❌ 不保留多页面架构（归档不删）
- ❌ 不做选型助手 wizard

### 1.4 关键现实约束（影响所有设计）

- **WebSearch/WebFetch 在当前环境配额耗尽**（8/18 重置），skill 不能依赖 AI 实时联网
- **collector 的 `_scrape_direct()` 实测产垃圾数据**（SPA 正则匹配到噪声），需重构
- **plans.json 现有 31 条套餐是手工录入**，不是抓出来的
- **RSSHub 对国内 AI 厂商定价基本无覆盖**（仅 deepseek/news、qwen/blog）

---

## 2. 总体架构

三层 + 并行工作流：

```
┌─────────────────────────────────────────────────────────┐
│  Layer 1: 信号采集（并行，3 路 dispatch）                │
│  ├─ Agent-Scan:  DailyHotApi 科技源关键词扫描            │
│  ├─ Agent-RSS:   RSSHub feeds (deepseek/qwen/qbitai/...) │
│  └─ Agent-Httpx: 供应商定价页/API 提取（sources/*.py）   │
│         → data/signals/{date}.json                       │
├─────────────────────────────────────────────────────────┤
│  Layer 2: 归一化 + 人工确认（串行，AI 主导）              │
│  ├─ 合并：自动信号 ∪ 用户的自然语言输入                   │
│  ├─ AI 按 schema 草拟 changes/plans JSON 变更             │
│  ├─ 输出 unified diff，用户确认（y/n/改）                │
│  ├─ 快照 history/ → 应用变更                             │
│  └─ 跑 token_estimator 补 measuredMonthlyToken           │
│         → project/codingplan-saver/data/*.json 更新       │
├─────────────────────────────────────────────────────────┤
│  Layer 3: 生成交付（串行）                                │
│  └─ 读 JSON → 套模板 → dist/codingplan-saver.html        │
└─────────────────────────────────────────────────────────┘
```

**并行点**：Layer 1 的三路信号采集天然独立，用 dispatching-parallel-agents 模式并发跑。Layer 2 必须串行（需用户确认）。Layer 3 纯计算。

---

## 3. 数据 Schema

### 3.1 设计原则

> **Schema 由「页面要展示什么」×「数据源能拿到什么」共同决定，按需迭代。**

基线字段来自第 4 节的页面展示需求清单。能稳定拿到的字段进 schema，拿不到的不进（避免假数据）。

### 3.2 文件组织

```
project/codingplan-saver/data/
├── site.json           # 站点级配置（手动维护）
├── vendors.json        # 厂商元信息（半自动：URL 在 reference/pricing-urls.md 维护）
├── plans.json          # 套餐主数据（半自动更新核心）
├── changes.json        # 统一变动时间线（合并旧 price-changes + articles）
└── history/            # 历史快照
    └── plans-2026-07-20.json   # 每次 update 前自动快照
```

### 3.3 site.json（手动维护，从旧 config.json 精简）

```jsonc
{
  "name": "CodingPlan 省钱攻略",
  "tagline": "每月在 AI Coding Plan 上花 200-1000 块？饭庐者说帮你选最划算的",
  "domain": "codingplan-saver",
  "logo": "CP",
  "primaryColor": "#10b981",
  "accentColor": "#06b6d4",
  "blogger": {
    "name": "饭庐者说",
    "avatar": "FL",
    "title": "AI 工具重度用户 / 独立博主",
    "bio": "...",
    "platforms": [
      { "name": "公众号", "handle": "饭庐者说", "url": "#" }
    ]
  },
  "header": {
    "updateDate": "更新于 2026.7.20",
    "highlights": "本周关注：...",
    "stats": [
      { "label": "覆盖平台", "value": "20", "unit": "家" }
    ]
  },
  "quickEntries": [
    {
      "id": "budget-under-50",
      "icon": "¥",
      "title": "预算 50 元以内",
      "desc": "学生党 / 体验党",
      "filter": { "monthlyPriceMax": 50 }
    }
  ],
  "recommendationGroups": [
    {
      "id": "best-overall",
      "title": "综合推荐",
      "subtitle": "...",
      "items": [
        {
          "vendor": "智谱AI", "plan": "Pro", "rating": 5,
          "verdict": "我的主力套餐",
          "reasons": ["...", "**需要抢购**"]
        }
      ]
    }
  ],
  "community": {
    "free": { "title": "...", "highlights": [], "ctaText": "..." },
    "paid": { "title": "...", "highlights": [], "ctaText": "...", "url": "#" }
  },
  "disclosure": "...",
  "footer": { "about": "...", "links": [] }
}
```

**变化**：去掉 `nav`（HTML 内部 Tab 不需要）、`site.url`（暂不用）。保留 `quickEntries`、`recommendationGroups`、`community`——这些是博主主观编辑内容，必须手动。

### 3.4 vendors.json（半自动）

```jsonc
[
  {
    "id": "zhipu",                      // 唯一标识，对齐 plans.json 的 vendor 字段
    "name": "智谱AI",                    // 显示名
    "logo": "智",                        // 单字 logo（HTML 卡片用）
    "color": "#F5F527",                  // 散点图配色
    "urls": {
      "pricing": "https://...",          // 定价页（人 review，见 pricing-urls.md）
      "docs": "https://...",             // 文档页（httpx 提取目标，可空）
      "api": "https://...",              // API JSON 端点（httpx 提取目标，可空）
      "home": "https://open.bigmodel.cn"
    },
    "extractStrategy": "docs",           // httpx | docs | manual（决定 sources/{id}.py 怎么跑）
    "lastVerified": "2026-07-20",        // 最后实测日期
    "notes": "SPA 控制台，文档页可提取"
  }
]
```

**关键**：`urls.docs` / `urls.api` 是 httpx 提取的真正目标，不是 `urls.pricing`（那是给人看的）。`extractStrategy` 声明该厂商怎么采：
- `docs` — 静态文档页，httpx + BeautifulSoup 解析
- `api` — 厂商提供 JSON API 端点，httpx 直接拿
- `manual` — 无可靠源，靠人喂自然语言

### 3.5 plans.json（半自动更新核心）

```jsonc
{
  "id": "zhipu-pro",                      // {vendor-id}-{plan-lower} 全局唯一
  "vendor": "智谱AI",                      // 对齐 vendors.json 的 name
  "vendorId": "zhipu",                     // 对齐 vendors.json 的 id
  "plan": "Pro",
  "type": "Coding Plan",                   // Coding Plan | Token Plan
  "tier": "pro",                           // lite | pro | max（便于分组排序）
  "monthlyPrice": 149,
  "currency": "¥",
  "firstMonthPrice": 141.55,               // 可选，有则展示
  "rating": 5,
  "models": ["GLM-5.1", "GLM-5.2"],
  "monthlyRequests": 120000,               // Coding Plan 才有
  "tokenLimit": null,                       // Token Plan 才有
  "measuredMonthlyToken": 600,             // token_estimator 自动补
  "tags": ["模型强", "需抢购"],
  "bloggerVerdict": "我的主力套餐...",
  "action": "https://open.bigmodel.cn/pricing",
  "status": "active",                      // active | paused | sold_out | deprecated
  "source": "manual",                      // manual | extracted-zhipu（数据来源追溯）
  "updatedAt": "2026-07-20"
}
```

**变化（vs 旧 schema）**：
- 新增 `vendorId`（解耦显示名和 id）
- 新增 `tier`（轻量分组）
- 新增 `source`（追溯每条数据来源，混合人工/自动时关键）
- 删除 `quarterlyPrice` / `yearlyPrice`（页面未用，需要时加回）
- 删除 `fiveHoursRequests` / `weeklyRequests`（页面未用）
- `status` 枚举化

### 3.6 changes.json（统一变动时间线）

合并旧 `price-changes.json` + `articles.json`。

```jsonc
[
  {
    "id": "2026-07-20-kimi-pause",          // {date}-{slug}，全局唯一
    "date": "2026-07-20",
    "kind": "subscription_pause",            // 见下方枚举
    "vendor": "Kimi",                        // 对齐 vendors.name；可为 "通用"
    "title": "Kimi 暂停 C 端新用户订阅",      // ≤30 字
    "detail": "K3 发布后算力告急...",         // ≤120 字；article 类型可更长
    "impact": "negative",                    // positive | negative | neutral
    "level": "high",                         // high | medium | low
    "source": "manual",                      // manual | signal-dailyhot | signal-rsshub | extracted
    "sourceUrl": null,                       // 可选，来源链接（文章类必有）
    "relatedPlans": ["kimi-moderato"],       // 可选，关联 plan id
    "featured": false,                       // 是否在首页高亮
    // article 类型额外字段：
    "excerpt": null,                          // 文章摘要
    "author": null,                           // 文章来源（36氪/IT之家...）
    "readTime": null,                         // 阅读时长
    "cover": null                             // 封面字母标识（K3/DS/NEW...）
  }
]
```

**`kind` 枚举**（统一原来散落的类型）：
| kind | 含义 | 原 price-changes 对应 |
|------|------|----------------------|
| `price_change` | 涨价/降价/计费调整 | "计费调整" |
| `new_model` | 新增支持某模型 | "新增模型" |
| `new_plan` | 新套餐上线 | "新增平台" |
| `subscription_pause` | 暂停订阅 | "暂停订阅" |
| `promotion` | 限时活动/折扣 | "活动" |
| `outage` | 故障/下架 | — |
| `article` | 行业文章/资讯 | 原 articles.json |

页面"动态" Tab 按 `kind` 筛选：全部 / 价格（price_change+promotion）/ 模型（new_model+new_plan）/ 订阅（subscription_pause+outage）/ 文章（article）。

---

## 4. 页面展示信息需求（schema 的源头）

> 这一节是 schema 的"需求规格"，未来 schema 迭代时先回来改这里。

### 4.1 Tab「推荐」字段需求

| UI 元素 | 字段 | 来源文件 |
|---------|------|---------|
| Hero 标语/统计 | site.tagline, header.{updateDate,highlights,stats[]} | site.json |
| Top 3 自动排序卡片 | plans: vendor/plan/type/monthlyPrice/currency/rating/measuredMonthlyToken | plans.json |
| Top 3 计算字段 | tokensPerYuan = measuredMonthlyToken / monthlyPrice（运行时） | — |
| 场景卡片 | site.quickEntries[] | site.json |
| 博主推荐分组 | site.recommendationGroups[] | site.json |

### 4.2 Tab「对比」字段需求

| 表格列 | 字段 | 备注 |
|--------|------|------|
| 平台/套餐/类型/评分 | vendor/plan/type/rating | 基础 |
| 月费 | monthlyPrice/currency | 基础 |
| 首月（额外列） | firstMonthPrice | 可选 |
| 月请求（额外列） | monthlyRequests | Coding Plan |
| 实测月Token | measuredMonthlyToken | 自动算 |
| 每元Token | 运行时算 | = token/price |
| 1M Token价（额外列） | 运行时算 | = price/token |
| 支持模型 | models[] | |
| 标签 | tags[] | |
| 详情链接 | action | |
| **散点图** | x=monthlyPrice, y=measuredMonthlyToken | ECharts，按 vendor.color 着色 |

### 4.3 Tab「动态」字段需求（合并文章+价格变动）

| UI 元素 | 字段 |
|---------|------|
| 时间线条目 | date/vendor/kind/title/detail/impact/level |
| 文章类额外 | excerpt/author/url/readTime/cover/featured |
| 顶部筛选 | 按 kind 分组过滤 |

### 4.4 Tab「社群」字段需求

| UI 元素 | 字段 |
|---------|------|
| 免费群卡 | site.community.free.{title,subtitle,description,highlights[],qrImage,ctaText} |
| 知识星球卡 | site.community.paid.{title,subtitle,description,highlights[],ctaText,url} |

---

## 5. HTML 交付物结构

### 5.1 Tab 布局

```
┌──────────────────────────────────────────────────┐
│ Nav: 站名  [推荐] [对比] [动态] [社群]   加入社群  │
├──────────────────────────────────────────────────┤
│ Tab 1「推荐」                                     │
│   Hero (标语 + 3 个统计数字)                       │
│   Top 3 Picks (评分×性价比 自动排序)              │
│   场景卡片 (点击跳对比 Tab 并筛选)                 │
│   博主推荐分组                                     │
│                                                   │
│ Tab 2「对比」                                     │
│   散点图 (价格 vs 月Token)                        │
│   筛选条 (类型/标签/搜索/排序)                      │
│   完整套餐表格 (可展开额外列)                      │
│   移动端自动切换卡片视图                            │
│                                                   │
│ Tab 3「动态」  ← 合并旧"价格变动"+"文章"            │
│   顶部按 kind 筛选 (全部/价格/模型/订阅/文章)      │
│   统一时间线 (按 date 倒序)                        │
│   每条: impact 徽章 + vendor + title + detail + 日期│
│   kind=article 可展开看 excerpt，点击跳原文        │
│                                                   │
│ Tab 4「社群」                                     │
│   免费群 + 知识星球双卡                            │
├──────────────────────────────────────────────────┤
│ Footer (披露声明 + 链接)                           │
└──────────────────────────────────────────────────┘
```

### 5.2 技术实现要点

- **单文件**：所有 CSS 内联 `<style>`，所有 JS 内联 `<script>`，所有 JSON 嵌入 `<script id="cp-data" type="application/json">`
- **Tab 路由**：URL hash（`#recommend` / `#compare` / `#updates` / `#community`），支持直链 + 浏览器后退
- **场景卡片 → 对比**：点击跳 `#compare?model=GLM-5.2`，对比页解析 query 自动筛选
- **散点图**：ECharts CDN（唯一外部依赖，离线时降级为表格）
- **设计 token**：沿用现有 `styles/shared.css` 的 CSS 变量系统（配色/间距/字号）
- **响应式**：移动端表格自动切换为卡片视图

---

## 6. 供应商 URL 维护机制

### 6.1 文档位置

`reference/pricing-urls.md`（已存在，需重构为下方结构）。

### 6.2 文档结构（重构后）

```markdown
# AI Coding Plan 供应商 URL 参考

> 最后更新: 2026-07-21
> 维护方式: 用户 review + 实测反馈

## 厂商清单

### 智谱AI (zhipu)
| 用途 | URL | httpx 可用 | 实测日期 | 备注 |
|------|-----|-----------|---------|------|
| 人看定价页 | https://open.bigmodel.cn/pricing | ❌ SPA | 2026-07-20 | 控制台 JS 渲染 |
| 文档页（提取目标） | _待补充_ | ? | - | 需找静态文档 |
| API JSON | _待补充_ | ? | - | |

### DeepSeek (deepseek)
| 用途 | URL | httpx 可用 | 实测日期 | 备注 |
|------|-----|-----------|---------|------|
| 人看定价页 | https://api-docs.deepseek.com/quick_start/pricing | 🟡 待测 | - | 文档站 |
...

## 待补充厂商
- TaoToken（出现在 plans.json 但无 URL 配置）
```

### 6.3 维护流程

1. **用户 review**：用户在文档里补充/纠正 URL，标注每个 URL 的用途（人看 / 提取目标）
2. **AI 实测**：skill 执行时跑 `sources/{vendor}.py`，把结果（成功/失败/字段覆盖）回写文档的"httpx 可用"和"实测日期"列
3. **迭代**：提取失败 → AI 在文档标 ❌ 并建议替代 URL → 用户确认 → 再测

### 6.4 extractStrategy 决策树

对每个厂商，按顺序尝试：
1. 有 `urls.api`？→ 走 `api` 策略（httpx 拿 JSON，最稳）
2. 有 `urls.docs`？→ 走 `docs` 策略（httpx + BeautifulSoup）
3. 都没有？→ `manual` 策略（只接收人喂的信号）

---

## 7. Skill 工作流（4 个子命令）

### 7.1 `/build-site`（默认 = full）

完整 pipeline。**不推荐日常用**，因为会跑完所有 Layer。

```
Layer 1 并行 dispatch 3 个 sub-agent
  ├─ Agent-Scan:  python -m collector.price_monitor（DailyHotApi 科技源）
  ├─ Agent-RSS:   httpx 拉 RSSHub feeds（deepseek/qwen/qbitai/aibase/infoq）
  └─ Agent-Httpx: python -m collector.sources（按 vendors.json 跑各厂商 parser）
       → data/signals/{date}.json
Layer 2 合并 + 确认（见 7.2）
Layer 3 生成（见 7.3）
```

### 7.2 `/build-site update [自然语言]`（最常用）

```
Step 1: 并行 dispatch 信号采集（同 Layer 1）
Step 2: 主 agent 合并
  • 自动信号 ∪ 解析用户的自然语言输入
  • 去重（同一变动多源命中）
  • 按 schema 草拟 changes.json 新条目
  • 若涉及套餐本身字段变更 → 草拟 plans.json 修改
Step 3: 输出 unified diff（changes.json + plans.json 的增删改）
Step 4: 用户确认（y / n / 改某条）
Step 5: 写入
  • 快照当前 plans.json → history/plans-{date}.json
  • 应用变更
  • 跑 python -m collector.token_estimator（补 measuredMonthlyToken）
  • 更新所有 updatedAt 时间戳
Step 6: 不自动 build，提示用户"说 /build-site build 生成 HTML"
```

**自然语言解析指引**（SKILL.md 里详细写）：

| 用户说 | kind 映射 | 改哪个文件 |
|--------|----------|-----------|
| "Kimi 涨价到 99" | `price_change` | plans.json（改 monthlyPrice）+ changes.json（加条目） |
| "字节方舟新增 Kimi-K3 支持" | `new_model` | plans.json（加 models）+ changes.json |
| "Kimi 暂停订阅" | `subscription_pause` | plans.json（status=paused）+ changes.json |
| "方舟 2.5 折活动到 8.8" | `promotion` | changes.json（plans.json 不改基础价） |
| "看到一篇文章说..."（带 URL） | `article` | changes.json |

### 7.3 `/build-site build`

纯 Layer 3，最快。

```
1. 读 project/codingplan-saver/data/{site,vendors,plans,changes}.json
2. 校验 schema（缺失字段用默认值）
3. 套 HTML 模板（SKILL.md 内联的"标准件"）
4. 数据点位替换（占位符 → 真实数据）
5. 输出 dist/codingplan-saver.html
6. 报告：文件大小 + 在浏览器打开的命令
```

### 7.4 `/build-site scan`

只跑 Layer 1，纯看信号不改任何 JSON。

```
1. 并行 dispatch 三路信号采集
2. 合并去重
3. 输出"本周可能值得关注的变动"报告（markdown 到终端）
4. 不动任何文件，等用户决定哪些值得 update
```

适合周一打开电脑先 scan 一下，再决定要不要 update。

---

## 8. 文件结构与旧代码归档

```
hot-trend-root/
├── .claude/skills/
│   └── build-site.md                    ← NEW: 主 skill（替换旧同名）
├── project/codingplan-saver/
│   ├── data/                            ← NEW: 数据目录（重新组织）
│   │   ├── site.json
│   │   ├── vendors.json
│   │   ├── plans.json
│   │   ├── changes.json
│   │   └── history/
│   ├── template/                        ← NEW: HTML 模板参考实现
│   │   └── index.html
│   └── archive/                         ← NEW: 旧代码归档（不删）
│       ├── old-multi-page/              ← 旧 6 个 HTML
│       ├── old-scripts/                 ← 旧 scripts/shared.js
│       ├── old-styles/                  ← 旧 styles/shared.css
│       ├── old-config.json              ← 旧 config.json
│       ├── old-plans.json               ← 旧 plans.json
│       ├── old-articles.json
│       ├── old-price-changes.json
│       └── old-src/                     ← 旧 src/ + vite.config.ts + package.json
├── tools/
│   ├── builder/
│   │   └── build_html.py                ← 归档到 project/codingplan-saver/archive/
│   └── collector/
│       └── collector/
│           ├── price_monitor.py         ← 重构：去掉 _scrape_direct，只保留信号扫描
│           ├── sources/                 ← NEW: 每家厂商一个 parser
│           │   ├── __init__.py
│           │   ├── base.py              ← 通用 httpx + BeautifulSoup 框架
│           │   ├── deepseek.py
│           │   ├── zhipu.py
│           │   └── ...（按 vendors.json 逐家实现）
│           ├── token_estimator.py       ← 保留不动
│           └── article_discovery.py     ← 改：输出目标变为 changes.json（kind=article）
├── reference/
│   ├── pricing-urls.md                  ← 重构（见 §6.2）
│   └── data-map.md                      ← 更新（反映新数据流）
├── data/
│   ├── signals/                         ← NEW: Layer 1 信号产出
│   │   └── {date}.json
│   ├── raw/                             ← 保留
│   └── price-reports/                   ← 保留（price_monitor 还写这里）
└── dist/
    └── codingplan-saver.html            ← 最终交付物
```

### 8.1 归档规则

- **不删任何旧文件**，全部 `git mv` 到 `project/codingplan-saver/archive/` 对应子目录
- 归档目录加 `README.md` 说明"这是 V1 多页面架构，已被单文件 + skill 替代，保留供参考"
- `tools/builder/build_html.py` 移到 `archive/old-builder/`

### 8.2 .gitignore 更新

`dist/` 当前被 ignore——但这是最终交付物，需要决定：
- **选项 A**：从 .gitignore 移除 `dist/`，让交付物进 git（方便分享、版本追溯）
- **选项 B**：保持 ignore，靠 GitHub Actions 或手动 release 发布

**推荐 A**（交付物进 git，符合"最终交付"语义）。

---

## 9. collector 改造细节

### 9.1 price_monitor.py 重构

**保留**：`_fetch_dailyhot_news()`（DailyHotApi 科技源关键词扫描，实测可用）
**删除**：`_scrape_direct()`（SPA 正则产垃圾）
**改写**：`run_price_monitor()` 只做信号扫描，输出 `data/signals/{date}.json`

### 9.2 sources/ 新模块

```
sources/
├── __init__.py          # 注册表：VENDOR_ID → parser 类
├── base.py              # BaseParser: 通用 httpx + BeautifulSoup 框架
├── deepseek.py          # DeepSeekParser: 解析 api-docs 页
├── zhipu.py             # ZhipuParser: 解析文档页（URL 待用户补充）
└── ...
```

**BaseParser 接口**：
```python
class BaseParser:
    vendor_id: str
    def extract(self, client) -> ExtractResult:
        """返回提取到的套餐字段，未拿到的字段不返回"""
```

**ExtractResult**：
```python
{
  "vendor": "DeepSeek",
  "plans": [{"plan": "...", "monthlyPrice": ..., ...}],
  "extractedFields": ["monthlyPrice", "models"],  # 实际拿到的字段
  "missingFields": ["measuredMonthlyToken"],       # 没拿到的
  "sourceUrl": "...",
  "fetchedAt": "..."
}
```

### 9.3 依赖更新

`tools/collector/pyproject.toml` 新增：
- `beautifulsoup4` — HTML 解析
- `lxml` — BS4 的快速 parser

不加 Playwright（按用户决策"优先找 API/文档页"）。

---

## 10. SKILL.md 章节大纲

```markdown
# /build-site — CodingPlan 省钱攻略 数据更新 + HTML 生成

## 触发
`/build-site` | `/build-site update [自然语言]` | `/build-site build` | `/build-site scan`

## 子命令工作流
（§7 的四张流程图，每张配具体步骤 + bash 命令）

## 数据 Schema（宪法）
（§3 的完整 schema 定义）

## 页面展示需求
（§4 的字段需求清单——schema 迭代时先改这里）

## HTML 模板规范
- 4 Tab 结构 + hash 路由
- CSS 设计 token（内联完整样式表）
- JS 交互逻辑（Tab 切换、筛选、散点图、展开）
- 数据嵌入方式（<script type="application/json">）
- 完整模板源码（作为"标准件"内联在文档里）

## collector 集成
- Layer 1 三路信号并行命令
- sources/{vendor}.py parser 编写规范
- token_estimator 调用时机

## 供应商 URL 维护
- reference/pricing-urls.md 结构说明
- extractStrategy 决策树
- 实测反馈回写规则

## 自然语言解析指引
（§7.2 的关键词 → kind → 文件映射表）

## 错误处理
- collector 跑失败 → 降级纯人工模式
- JSON schema 校验失败 → 回滚到 history 快照
- HTML 生成失败 → 保留上次 dist/
- 单家厂商提取失败 → 标记 manual，不阻塞其他厂商
```

---

## 11. 关键决策记录

| # | 决策点 | 选择 | 理由 |
|---|--------|------|------|
| 1 | HTML 形态 | 单文件 | 双击可开、易分享 |
| 2 | 技术栈 | 纯静态 HTML | 无构建依赖 |
| 3 | 数据源策略 | 人喂信号 + collector 自动信号 | WebSearch 配额受限 + collector SPA 实测失败 |
| 4 | SPA 解决方案 | 优先找 API/文档页 | 用户决策，避免 Playwright 重量依赖 |
| 5 | articles 去留 | 合并进 changes.json (kind=article) | 用户要求合并 |
| 6 | wizard 去留 | 去掉 | 用户决策 |
| 7 | Tab 数 | 4 个 | 推荐/对比/动态/社群 |
| 8 | 旧代码 | 归档不删 | 保留参考、可回滚 |
| 9 | URL 维护 | pricing-urls.md 文档化 | 用户 review + AI 实测反馈 |
| 10 | schema 演进 | 按页面需求 × 数据源能力迭代 | 避免假数据 |
| 11 | dist/ 是否进 git | 待用户确认（推荐进 git） | 符合"最终交付"语义，便于分享和版本追溯 |
| 12 | 并行点 | Layer 1 三路信号 | 用户要求"充分考虑并联任务" |
| 13 | update 后自动 build | 不自动 | 避免未确认就覆盖交付物 |

---

## 12. 风险与未决项

### 12.1 已知风险

| 风险 | 影响 | 缓解 |
|------|------|------|
| 部分厂商找不到静态/API 源 | 那 N 家只能靠人喂 | extractStrategy=manual，文档标记 ❌ 待补 |
| ECharts CDN 离线不可用 | 散点图不显示 | 降级为表格，不阻塞 |
| BS4 解析各厂商文档页结构差异大 | 每家 parser 要单独写 | sources/ 框架支持，逐家迭代 |
| changes.json 合并后条目膨胀 | 时间线过长 | 默认只展示最近 30 天，分页 |
| 自然语言解析歧义 | 写错 JSON | diff 确认环节兜底 |

### 12.2 未决项（需用户后续决策）

1. **dist/ 是否进 git**（§8.2 推荐进 git，待确认）
2. **Top 5 优先实现哪些厂商的 sources/ parser**（建议：DeepSeek、智谱、字节方舟、Kimi、MiniMax）
3. **changes.json 历史数据迁移**：旧 price-changes.json (10 条) + articles.json (30 条) 怎么合并进新 schema？保留全部还是只迁最近 30 天？旧 articles 的 hash id（如 `4ad193bdc013`）迁移时统一改为 `{date}-{slug}` 还是保留原 id？
4. **站点配色**：沿用现有 emerald (#10b981) 主色，还是借这次重做换一套？

### 12.3 迁移时的 id 处理规则（默认方案）

- `price-changes.json` 的条目无 id → 迁移时生成 `{date}-{vendor-slug}-{kind}`
- `articles.json` 的条目已有 hash id → **保留原 id**（避免破坏外链），新增字段补齐 kind/date/vendor
- 新增的 changes 一律用 `{date}-{slug}` 规则

---

## 13. 实现阶段建议（供 writing-plans 参考）

建议分 3 个 milestone，每个可独立验证：

**M1 - 骨架打通**（先让 build 能跑）
- 归档旧代码
- 建 data/ 新目录结构
- 写 site.json / vendors.json / plans.json / changes.json 的最小可用版本（迁移现有数据）
- 写 SKILL.md 的 build 模式 + HTML 模板
- 验证：`/build-site build` 能输出单文件 HTML，4 个 Tab 都能渲染

**M2 - 数据更新闭环**（让 update 能跑）
- 重构 price_monitor.py（去掉 _scrape_direct）
- 实现 sources/base.py + 2-3 家示范 parser（DeepSeek + 智谱）
- 写 SKILL.md 的 update/scan 模式
- 验证：`/build-site scan` 能出信号，`/build-site update "..."` 能改 JSON 并 diff

**M3 - 厂商覆盖扩展**（迭代）
- 按 priority 逐家实现 sources/{vendor}.py
- 重构 pricing-urls.md
- 完善 token_estimator 与新 plans.json schema 的适配
- 验证：Top 5 厂商都能自动提取

每个 milestone 完成后 commit，不跨 milestone 提交。
