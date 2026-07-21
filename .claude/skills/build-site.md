# Build Site - 生成 CodingPlan 省钱攻略单页 HTML

## 触发

- 用户说 `/build-site`、`build`、`构建`、`生成页面`、`更新数据并生成`
- 或定时触发

## 功能

一键运行完整数据管道 + 生成单文件 HTML 交付物。

## 执行流程

### Step 1: 更新数据（可选，如果用户要求最新数据）

```bash
cd tools/collector && source .venv/bin/activate && python -m collector.pipeline
```

如果只需要用现有数据生成页面，跳过此步。

### Step 2: 生成 HTML

```bash
cd tools/builder && python3 build_html.py
```

### Step 3: 输出

生成文件: `dist/codingplan-saver.html`

- 单文件，包含所有 CSS、JS、数据
- 多 Tab 页面: 推荐 & 动态 / 套餐对比 / 测评文章 / 选型助手 / 加入社群
- ECharts 散点图
- 完整对比表（筛选/排序/搜索）
- 选型助手（4 题问答）
- 文章列表（分页/筛选/搜索）
- 所有数据嵌入为 JSON

## 数据来源

| 数据 | 来源 | 更新工具 |
|------|------|----------|
| `config.json` | 手动编辑 | 手动 |
| `plans.json` | 手动 + token_estimator | `python -m collector.token_estimator` |
| `articles.json` | article_discovery | `python -m collector.article_discovery` |
| `price-changes.json` | 手动编辑 | 手动 |
| 热点数据 | engine.py | `python -m collector.engine` |

## 文件结构

```
dist/codingplan-saver.html     ← 最终交付物 (单文件)
tools/builder/build_html.py    ← HTML 生成器
tools/collector/               ← 数据采集管道
project/codingplan-saver/      ← 数据源 (JSON)
```

## 注意事项

- 生成的 HTML 引用 ECharts CDN（需要网络）
- 如果数据文件不存在，使用空数据
- 每次生成覆盖 `dist/codingplan-saver.html`