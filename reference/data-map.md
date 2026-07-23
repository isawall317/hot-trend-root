# Hot Trend 数据地图

> 最后更新: 2026-07-23
> 维护者: 饭庐者说

---

## 数据文件清单

| 文件 | 格式 | 来源 | 更新方式 | 更新频率 | 消费方 |
|------|------|------|----------|----------|--------|
| `site.json` | JSON | 手动编辑 | 手动 | 按需 | codingplan-saver.html (Nav/Footer/推荐) |
| `vendors.json` | JSON array | 手动 + sources/ 提取 | 半自动 | 按需 | codingplan-saver.html (散点图配色/详情链接) |
| `plans.json` | JSON array | sources/merge.py + token_estimator | 自动提取 + 自动推算 | 每次 pipeline | codingplan-saver.html (Top3/对比表/散点图) |
| `changes.json` | JSON array | article_discovery + Claude Code 审阅 | 半自动 | 每次 pipeline 后审阅 | codingplan-saver.html (推荐页"最近变动") |
| `data/raw/YYYY-MM-DD/*.json` | JSON | engine.py | 自动采集 | 每日 | article_discovery |
| `data/pending/{date}/articles.json` | JSON | article_discovery.py | 关键词召回 | 每次 pipeline | Claude Code 审阅 |
| `data/signals/*.json` | JSON | price_monitor.py + sources/runner.py | 自动扫描 | 每次 pipeline | sources/merge.py |
| `data/cards/*.md` | Markdown | /scan + /analyze | Claude Code 生成 | 按需 | 机会跟踪 |

## 厂商自动提取覆盖

| 状态 | 数量 | 厂商 |
|------|------|------|
| ✅ 自动提取 | 7 | 智谱AI, DeepSeek, Kimi, MiniMax, 腾讯云, Claude, GitHub |
| ❌ 无法提取 | 4 | 字节·方舟 (bot拦截), 阿里·百炼 (需登录), Codex (Cloudflare), 小米·MiMo (SPA) |

## plans.json 字段说明

| 字段 | 类型 | 来源 | 可信度 |
|------|------|------|--------|
| `monthlyPrice` | number | sources/ 自动提取 + 手动 | 高（7/11 自动验证） |
| `monthlyRequests` | number | sources/ 自动提取 | 中（仅腾讯云可提取） |
| `measuredMonthlyToken` | number | token_estimator 推算 | 中（推算值） |
| `models` | array | sources/ 自动提取 + 手动 | 高 |
| `status` | string | 手动（新闻/社区） | 高 |
| `source` | string | 自动标注 | 高（extracted-{vendor} / manual） |

详细 Schema 定义见 `project/codingplan-saver/data/SCHEMA.md`。

## 更新流程

### 自动管道（/codingplan-page 或 CronCreate 定时）

```
python -m collector.pipeline
  ├── engine.py → data/raw/
  ├── article_discovery.py → data/pending/{date}/articles.json（候选，不直接写入）
  ├── price_monitor.py → data/signals/
  ├── sources/runner.py → data/signals/extract-{date}.json（7 家厂商自动提取）
  ├── sources/merge.py → plans.json（合并提取结果）
  └── token_estimator.py → plans.json（推算 Token 用量）
```

### Claude Code 审阅（/codingplan-page update）

1. 读取 `data/pending/{date}/articles.json` 候选文章
2. 去噪：跳过纯技术教程、泛行业新闻
3. 收录：与 AI Coding Plan 定价/模型/订阅直接相关的文章
4. 生成结构化变动：关键事件 → new_model / price_change / subscription_pause
5. 写入 `changes.json` + 更新 `site.json`

### 手动更新（按需）

1. 检查 `data/signals/` 最新信号
2. 逐一核实 4 家 manual 厂商的定价页
3. 更新 `plans.json` 中变动项
4. 更新 `changes.json` 记录价格/模型变动

### 厂商 URL 参考

见 `project/codingplan-saver/docs/vendors-reference.md`

## 已知问题

| 问题 | 严重程度 | 计划 |
|------|----------|------|
| 4 家厂商无法自动提取 | 中 | 字节方舟/MiMo 可尝试 Playwright；阿里/Codex 需人工 |
| MiMo 价格可能已过期 | 中 | V2→V2.5 迁移后套餐结构变化，待重新验证 |
| Kimi API 价格可提取但 Coding Plan 需登录 | 低 | 当前 plans 价格仍为手动数据 |
| DeepSeek 无 Coding Plan | 低 | 当前为 API 价格折算"虚拟套餐" |
| 数据验证缺失 | 中 | 后续添加 data_validator.py |
| 机会卡仅 1 张 | 高 | 后续在 /scan 流程中持续产出 |