# /build-site — CodingPlan 省钱攻略 数据更新 + HTML 生成

## 触发

- `/build-site` 或 `/build-site build` — 读数据生成 HTML（最快，M1 可用）
- `/build-site update [自然语言]` — 更新数据（M2 实现后补全）
- `/build-site scan` — 扫描信号（M2 实现后补全）

---

## build 模式工作流

### 何时用

- 数据已更新（手动改了 JSON），想重新生成 HTML
- 模板有改动，想验证新输出

### 步骤

1. 读 `project/codingplan-saver/data/` 下 4 个 JSON
2. 运行 `python3 tools/builder/build.py`
3. 输出到 `dist/codingplan-saver.html`
4. 报告文件大小，提示 `open` 命令

### 数据校验

构建前 AI 应对照 `project/codingplan-saver/data/SCHEMA.md` 快速检查：
- `plans.json` 每条有 `id` / `vendor` / `vendorId` / `plan` / `monthlyPrice`
- `changes.json` 每条有 `id` / `date` / `kind` / `vendor` / `title`
- 缺失字段 → 用默认值（如 `status` 默认 `active`），不阻塞构建

---

## 数据 Schema 宪法

见 `project/codingplan-saver/data/SCHEMA.md`（完整字段定义 + 枚举 + 迁移规则）。

### 文件一览

| 文件 | 职责 | 更新方式 |
|------|------|---------|
| `data/site.json` | 站点配置（博主、推荐分组、社群） | 手动 |
| `data/vendors.json` | 厂商元信息（URL、提取策略） | 半自动 |
| `data/plans.json` | 套餐主数据（31 条） | 半自动 |
| `data/changes.json` | 变动时间线（40 条） | 半自动 |
| `data/history/` | plans.json 快照 | 自动 |

### 联盟变现

所有套餐链接（`plans[].action`）指向各厂商的注册/购买页。HTML 模板中所有 CTA 按钮统一为"优惠购买"，`rel="nofollow sponsored"`（SEO 合规）。Footer 保留联盟推广披露。

---

## HTML 模板

见 `project/codingplan-saver/template/index.html`（标准件）。

### 页面结构

- **3 Tab**: 推荐 / 对比 / 社群（hash 路由 `#recommend` / `#compare` / `#community`）
- **推荐页**: Hero → Top 3 Picks → 场景卡片 → 博主推荐 → 最近变动（30 天）
- **对比页**: 散点图（ECharts CDN）→ 筛选条 → 完整表格 → 移动端卡片
- **社群页**: 免费群 + 知识星球双卡
- **变现触点**: Top 3 卡片 / 推荐卡片 / 对比表格 / 移动端卡片 → 全部"优惠购买"按钮

### 数据嵌入

```html
<script id="cp-data" type="application/json">
{site, vendors, plans, changes, generatedAt}
</script>
```

---

## 文件结构

```
hot-trend-root/
├── .claude/skills/build-site.md        ← 本文件
├── project/codingplan-saver/
│   ├── data/                           ← 数据源
│   │   ├── SCHEMA.md                   ← 宪法
│   │   ├── site.json / vendors.json
│   │   ├── plans.json / changes.json
│   │   └── history/
│   ├── template/index.html             ← HTML 标准件
│   └── archive/                        ← V1 归档
├── tools/
│   ├── builder/build.py                ← 构建脚本
│   └── collector/                      ← 数据采集管道
├── dist/
│   └── codingplan-saver.html           ← 最终交付物
└── reference/
    ├── pricing-urls.md                 ← 供应商 URL 维护
    └── data-map.md                     ← 数据地图
```

---

## update 模式（M2 实现后补全）

> TODO: 信号采集（Layer 1 并行 dispatch）→ 归一化合并 → 用户确认 diff → 写入 JSON → 跑 token_estimator

## scan 模式（M2 实现后补全）

> TODO: 只跑 Layer 1，输出本周信号报告，不动任何 JSON

---

## 自然语言解析指引

| 用户说 | kind 映射 | 改哪个文件 |
|--------|----------|-----------|
| "X 涨价/降价到 ¥Y" | `price_change` | plans.json（monthlyPrice）+ changes.json |
| "X 新增支持 M 模型" | `new_model` | plans.json（models）+ changes.json |
| "X 暂停订阅" | `subscription_pause` | plans.json（status=paused）+ changes.json |
| "X 新套餐上线" | `new_plan` | plans.json（新增条目）+ changes.json |
| "X 限时活动，Y 折" | `promotion` | 仅 changes.json |
| "看到一篇文章 [URL]" | `article` | 仅 changes.json（需强相关过滤） |

---

## 错误处理

- 构建时 JSON 缺失字段 → 用默认值，不阻塞
- collector 跑失败 → 降级纯人工模式
- JSON schema 校验失败 → 回滚到 `history/` 快照
- HTML 生成失败 → 保留上次 `dist/`
- 单家厂商提取失败 → 标记 `manual`，不阻塞其他厂商