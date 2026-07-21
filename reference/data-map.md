# Hot Trend 数据地图

> 最后更新: 2026-07-21
> 维护者: 饭庐者说

---

## 数据文件清单

| 文件 | 格式 | 来源 | 更新方式 | 更新频率 | 消费方 |
|------|------|------|----------|----------|--------|
| `site.json` | JSON | 手动编辑 | 手动 | 按需 | codingplan-saver.html (Nav/Footer/推荐) |
| `vendors.json` | JSON array | 手动 + sources/ 提取 | 半自动 | 按需 | codingplan-saver.html (散点图配色/详情链接) |
| `plans.json` | JSON array | 手动 + token_estimator | 手动 + 自动推算 | 每周 | codingplan-saver.html (Top3/对比表/散点图) |
| `changes.json` | JSON array | article_discovery + 手动 | 自动提取 + 手动 | 每次采集后 | codingplan-saver.html (动态 Tab 时间线) |
| `data/raw/YYYY-MM-DD/*.json` | JSON | engine.py | 自动采集 | 每日 | article_discovery, price_monitor |
| `data/signals/*.json` | JSON | price_monitor.py + sources/runner.py | 自动扫描 | 每日 | Claude Code 审阅 |
| `data/price-reports/*.md` | Markdown | price_monitor.py | 自动生成 | 每日 | Claude Code 审阅 |

> V2 架构变更：`articles.json` + `price-changes.json` 已合并为 `changes.json`（统一 kind 字段区分类型），`config.json` 已重命名为 `site.json`。旧文件归档在 `project/codingplan-saver/archive/`。

## plans.json 字段说明

| 字段 | 类型 | 来源 | 可信度 |
|------|------|------|--------|
| `vendor` | string | 手动 | 高 |
| `plan` | string | 手动 | 高 |
| `type` | string | 手动 | 高 |
| `monthlyPrice` | number | 手动（官方定价页） | 中（需定期验证） |
| `measuredMonthlyToken` | number | 手动实测 + token_estimator 推算 | 中（推算值标注 estimation） |
| `models` | array | 手动（官方公告） | 高 |
| `tags` | array | 手动 | 高 |
| `rating` | number | 手动（博主评分） | 主观 |
| `status` | string | 手动（新闻/社区） | 高 |
| `action` | string | 手动 | 低（30/31 缺失） |

详细 Schema 定义见 `project/codingplan-saver/data/SCHEMA.md`。

## 更新流程

### 自动管道（每日）
```
python -m collector.pipeline
  ├── engine.py → data/raw/
  ├── article_discovery.py → changes.json (kind: "article")
  ├── price_monitor.py → data/signals/ + data/price-reports/
  └── token_estimator.py → plans.json
```

### 手动更新（按需）
1. 检查 `data/signals/` 最新信号
2. 逐一核实"待确认"平台的定价页 URL
3. 更新 `plans.json` 中变动项
4. 更新 `changes.json` 记录价格/模型变动
5. 更新 `site.json` 的 updateDate 和 stats

### 定价页 URL 参考
见 `reference/pricing-urls.md`

## 已知问题

| 问题 | 严重程度 | 计划 |
|------|----------|------|
| plans.json 部分缺 action 链接 | 中 | 补充各平台详情页 URL |
| plans.json 部分缺价格 | 低 | 手动补充 |
| 价格变动检测仅关键词匹配 | 中 | 后续从 sources/ parser 自动提取 |
| 数据验证缺失 | 中 | 后续添加 data_validator.py |
| 机会卡未自动生成 | 高 | 后续在 /scan 流程中产出 |