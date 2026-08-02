# 厂商知识库搭建方案

## 现状分析

### 当前数据散落在 4 个地方

| 位置 | 内容 | 更新方式 | 问题 |
|------|------|---------|------|
| `docs/vendors-and-tools.md` | 15 厂商 + 20 工具 + 4 待接入 | 手动编辑 | 人写的，容易过时 |
| `vendors.json` | 14 厂商元信息（URL/策略/分类） | 半自动 | 与 md 不同步 |
| `plans.json` | 31 条套餐 | 半自动（7 家自动提取） | 只覆盖有 parser 的厂商 |
| `tools.json` | 18 款工具详情 | 手动 | 完全手工维护 |

### 核心痛点

1. **双源问题**：markdown 和 JSON 各说各的，不知道谁是最新
2. **覆盖不全**：15 家厂商只有 7 家有自动提取，工具数据全靠手
3. **无变更感知**：厂商改价/上新模型/下架服务，不会自动发现
4. **数据孤岛**：codingplan-saver、coding-tools、model-picker 各自维护一份数据

---

## 方案设计

### 总体思路

**统一知识库 JSON → 自动采集 → 变更检测 → Claude Code 审阅 → 自动合并**

```
                    ┌──────────────────────────┐
                    │   data/knowledge-base/    │  ← 唯一真相源
                    │   ├── vendors.json        │
                    │   ├── services.json       │
                    │   ├── tools.json          │
                    │   ├── models.json         │
                    │   └── changes.json        │
                    └──────────┬───────────────┘
                               │
            ┌──────────────────┼──────────────────┐
            ▼                  ▼                  ▼
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │ 自动采集管道  │  │ Claude 审阅  │  │ 下游产品消费  │
    │ (Python)     │  │ (/kb-update) │  │ (build.py)   │
    │ 每天定时跑    │  │ 去噪+确认    │  │ 生成 HTML    │
    └──────────────┘  └──────────────┘  └──────────────┘
```

### 第一阶段：统一知识库数据模型（本次）

创建 `data/knowledge-base/` 目录，定义 5 个核心 JSON 文件，从现有数据迁移：

#### `vendors.json` — 厂商画像
```jsonc
{
  "id": "zhipu",
  "name": "智谱AI",
  "category": "model-maker",          // model-maker | cloud-maas | aggregator | vertical-cloud
  "country": "cn",                     // cn | us | global
  "urls": { "home": "...", "pricing": "...", "docs": "...", "api": "...", "console": "..." },
  "extractStrategy": "playwright",     // playwright | bs4 | api | manual
  "extractStatus": "ok",              // ok | degraded | failed | manual
  "affiliate": { "url": "...", "type": "referral", "note": "..." },
  "massServices": ["token-plan", "api-paygo", "coding-plan"],  // 提供的 mass 服务类型
  "lastVerified": "2026-07-23",
  "notes": "..."
}
```

#### `services.json` — 厂商服务/产品
```jsonc
{
  "id": "zhipu-coding-plan",
  "vendorId": "zhipu",
  "type": "coding-plan",              // coding-plan | token-plan | api-paygo | agent-plan | enterprise
  "name": "Coding Plan",
  "status": "active",                 // active | paused | deprecated
  "plans": [
    { "tier": "lite", "name": "Lite", "monthlyPrice": 49, "currency": "¥", ... },
    { "tier": "pro", "name": "Pro", "monthlyPrice": 149, ... }
  ],
  "models": ["GLM-5.2", "GLM-5.1", ...],
  "updatedAt": "2026-07-23"
}
```

#### `tools.json` — AI 编程工具
```jsonc
{
  "id": "claude-code",
  "name": "Claude Code",
  "vendorId": "claude",              // 关联厂商
  "type": "cli",                      // cli | ide | plugin | web
  "category": "overseas",            // domestic-vendor | domestic-independent | overseas
  "status": "active",
  "pricing": { "model": "freemium", "detail": "..." },
  "urls": { "home": "...", "docs": "..." },
  "features": [...],
  "rating": 5,
  // ...
}
```

#### `models.json` — 模型清单
```jsonc
{
  "id": "glm-5.2",
  "vendorId": "zhipu",
  "name": "GLM-5.2",
  "type": "text",                     // text | vision | code | multimodal
  "releaseDate": "2026-06-15",
  "status": "active"
}
```

#### `changes.json` — 统一变更时间线
复用现有 schema，新增 `source: "kb-auto"` 表示自动检测到的变更。

#### 关系总结

```
vendors ──1:N──→ services ──1:N──→ plans (pricing tiers)
vendors ──1:N──→ models
vendors ──1:N──→ tools
changes ──N:1──→ vendors / services / tools / models
```

### 第二阶段：扩展自动采集（后续）

#### 2a. 新增 Parser 覆盖

| 厂商 | 当前策略 | 可行方案 | 难度 |
|------|:--:|------|:--:|
| 字节·方舟 | manual | Playwright + stealth 反检测 | 中 |
| 小米·MiMo | manual | Playwright SPA 渲染 | 低 |
| 百度·千帆 | manual | 文档页 BS4 解析 | 低 |
| 京东云 | manual | 页面结构简单，BS4 可行 | 低 |
| OpenCode | manual | 开源，API 可能有 JSON | 低 |
| 阿里·百炼 | manual | 需登录，难以自动化 | 高 |
| Codex(OpenAI) | manual | Cloudflare 拦截 | 高 |
| OpenRouter | manual | 有公开 API，直接调 JSON | 低 |
| 硅基流动 | manual | 页面简单，BS4 可行 | 低 |

预计：7→12 家自动提取（新增 5 家：字节/MiMo/百度/京东/OpenRouter）

#### 2b. 新增发现模块

- `service_discovery.py` — 监控厂商页面，检测新服务上线
- `model_discovery.py` — 追踪新模型发布（从厂商文档页/API 响应中提取模型列表）
- `tool_discovery.py` — 从 GitHub trending、ProductHunt、厂商生态页发现新工具

#### 2c. 变更检测引擎

```python
# 每次采集后自动对比
def detect_changes(new_data, stored_data):
    - 价格变动 → 告警
    - 新增模型 → 自动收录（低风险）
    - 服务下架 → 告警
    - 新套餐上线 → 告警
    - URL 失效 → 告警
```

### 第三阶段：持续更新机制

#### 定时任务

```
CronCreate: "0 9,21 * * *" (每天 9:00 和 21:00)
  → python -m collector.pipeline --kb-mode
  → 自动采集 → 变更检测 → 生成报告
  → 低风险变更自动合并
  → 高风险变更标记待审阅
```

#### 审阅工作流

```
/kb-update review
  → 读取待审阅变更
  → Claude Code 去噪 + 分类
  → 展示给 Frank 确认
  → 应用变更到 KB JSON
  → 重新生成下游产品
```

#### `vendors-and-tools.md` 自动生成

从 KB JSON 自动生成 markdown 表格，不再手动维护。用 `tools/builder/kb_to_md.py` 实现。

---

## 实施建议

### 推荐路径：渐进式，不推倒重来

1. **先建 KB JSON 数据模型**（本次）— 不影响现有系统，新数据存在 `data/knowledge-base/`
2. **写迁移脚本** — 从现有 `vendors.json` + `plans.json` + `tools.json` + `vendors-and-tools.md` 迁移到 KB
3. **扩展 parser**（下次）— 按难度从低到高逐个击破
4. **接上定时任务**（后续）— CronCreate 自动跑
5. **下游产品切到 KB**（最后）— `build.py` 从 KB 读数据而非分散 JSON

### 核心原则

- **KB JSON 是唯一真相源**，markdown 由它生成
- **自动采集 + 人工审阅**，不是全自动
- **低风险变更自动合**（新模型、小价差），**高风险人工确认**（涨价、下架）
- **先建后切**，不影响现有产品运行

---

## 需要你确认的

1. 知识库范围：只覆盖目前 15 家厂商 + 20 款工具，还是扩展到更多？（如增加海外厂商 Together AI、Groq、Fireworks 等）
2. 更新频率：每天 2 次够不够？还是每周 1 次就够了？
3. 是否需要反向生成 `vendors-and-tools.md`（即 markdown 变成自动生成），还是保留手动维护？