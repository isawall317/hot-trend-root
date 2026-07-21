# Hot Trend 数据地图

> 最后更新: 2026-07-20
> 维护者: 饭庐者说

---

## 数据文件清单

| 文件 | 格式 | 来源 | 更新方式 | 更新频率 | 消费方 |
|------|------|------|----------|----------|--------|
| `config.json` | JSON | 手动编辑 | 手动 | 按需 | 所有页面导航/标题 |
| `plans.json` | JSON array | 手动 + token_estimator | 手动 + 自动推算 | 每周 | compare.html, index.html, wizard.html |
| `articles.json` | JSON array | article_discovery | 自动提取 | 每次采集后 | blog.html, index.html |
| `price-changes.json` | JSON | 手动编辑 | 手动 | 每周 | index.html |
| `data/raw/YYYY-MM-DD/*.json` | JSON | engine.py | 自动采集 | 每日 | article_discovery, price_monitor |
| `data/price-reports/*.md` | Markdown | price_monitor.py | 自动生成 | 每日 | Claude Code 审阅 |

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

## 更新流程

### 日常更新（每日）
```
python -m collector.pipeline
  ├── engine.py → data/raw/
  ├── article_discovery.py → articles.json
  ├── price_monitor.py → data/price-reports/
  └── token_estimator.py → plans.json
```

### 手动更新（每周）
1. 检查 `data/price-reports/` 最新报告
2. 逐一核实"待确认"平台的定价页 URL
3. 更新 `plans.json` 中变动项
4. 更新 `price-changes.json` 记录变动
5. 更新 `config.json` 的 updateDate 和 stats

### 定价页 URL 参考
见 `reference/pricing-urls.md`

## 已知问题

| 问题 | 严重程度 | 计划 |
|------|----------|------|
| plans.json 30/31 缺 action 链接 | 中 | 补充各平台详情页 URL |
| plans.json 1 个缺价格 | 低 | 手动补充 |
| articles.json 分类偏斜 | 低 | 已改进分类算法 |
| price-changes.json 仅手动更新 | 中 | 后续自动从 price_monitor 信号生成 |
| 数据验证缺失 | 中 | 后续添加 data_validator.py |