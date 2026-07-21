# Hot Trend 项目 Review

> 日期: 2026-07-21 | Reviewer: Claude (Fable 5)
> 更新: 同日修复了 4 个高优先级问题（见文末"已修复"）

---

## 总览

这是一个 **AI 利基发现与变现系统**，定位清晰：从全网热点中自动发现可商业化的细分赛道，用 AI 辅助分析→验证→开发小软件产品变现。项目由一位独立创作者（Frank，公众号 7000 粉）驱动，每周投入 5-10h，追求"睡后收入"。

**整体评分: 7/10** — 架构设计优秀，核心代码扎实，但存在一些数据管道断点和文档不一致的问题。

---

## 一、架构设计 ⭐⭐⭐⭐⭐ (5/5)

### 三层架构（采集→分析→执行）非常合理

```
Docker 采集层 (DailyHotApi + RSSHub)  →  Claude Code 分析层 (skills)  →  执行层 (开发产品)
```

**做得好的地方:**

- **Claude Code Native 的决策非常聪明。** 对于每周只有 5-10h 的独立创作者来说，维护独立部署系统（服务器、数据库、Web UI）是巨大的时间黑洞。把 Claude Code 当操作系统用，Python 只做"采集"这一件事，其余全部在 Claude Code 内完成——这个设计决策非常务实。
- 采集层用 JSON 文件存储而非数据库，简单直接，Claude Code 可以直接读取。对于这个规模的数据量（每天几百条）完全够用。
- 三层之间的接口清晰：采集层产出 JSON → 分析层读取 JSON 产出报告 → 执行层开发产品。

---

## 二、代码质量 ⭐⭐⭐⭐ (4/5)

### Python 采集器 (`tools/collector/`)

**`engine.py` — 采集引擎**
- 异步设计（`asyncio` + `httpx.AsyncClient`），并发采集 40+ 源，效率高
- 自动检测本地/远程 API（`_detect_dailyhot_api` / `_detect_rsshub_api`），本地 Docker 优先，降级到公共 API
- 归一化做得不错：不同来源的数据统一为 `{title, url, hot_metric, source, source_type, collected_at}`
- 源分类合理（social / tech / news / product / content / game / other）

**`storage.py` — 存储层**
- 简洁有效，按日期分目录，按时间戳命名文件
- `load_latest()` 和 `load_date_range()` 两个接口覆盖了主要使用场景
- 项目根路径解析用了 `Path(__file__).resolve().parent.parent.parent.parent`，虽然能工作但比较脆弱

**`pipeline.py` — 数据管道**
- 清晰的 4 步管道：采集→文章发现→价格监控→Token 推算
- 每步有独立的错误处理，单步失败不影响后续
- 生成汇总报告到 `data/pipeline-reports/`

**`token_estimator.py` — Token 推算器**
- 设计良好：3 级推算策略（月请求数→5h请求数→月费反推），有兜底方案
- 用同类套餐的中位数比率反推，比简单线性外推更合理

**`sources/` — 厂商定价提取器**
- 插件注册表模式（`@register("vendor_id")`）设计优雅，扩展新厂商只需加一个文件
- `BaseParser` / `BasePlaywrightParser` 基类层次清晰
- `DeepSeekParser` 和 `MinimaxParser` 实现完整，用 BeautifulSoup 解析静态文档页
- `ZhipuParser` 用 Playwright 处理 JS 渲染的 SPA 定价页，思路正确
- Runner 调度器支持并行执行所有 parser

### 可改进的地方:

1. **项目根路径解析** — 4 层 `parent` 太脆弱，建议用环境变量或配置常量
2. **类型注解不完整** — 大部分函数返回值是 `list[dict]`，缺少严格的 TypedDict 定义
3. **缺少日志系统** — 全部用 `print()`，对调试和监控不够友好
4. **没有测试** — 整个项目零测试代码

---

## 三、技能文档 ⭐⭐⭐⭐ (4/5)

### Skills (`/scan`, `/analyze`, `/validate`, `/build-site`)

**做得好的地方:**

- 每个 skill 有清晰的触发条件、执行流程、输出格式
- 6 维评分体系（需求真实性、增长潜力、付费意愿、竞争空间、执行可行性、规模化潜力）设计合理，每个维度有 1-5 分的具体标准
- `/build-site` 的 update 模式设计精巧：并行采集 3 路信号 → 合并去重 → diff 预览 → 用户确认 → 应用变更
- 自然语言解析指引表（"X 涨价到 ¥Y" → `price_change`）很实用

**可改进的地方:**

1. `/scan` skill 引用了 `from tools.collector.collector.storage import load_latest`，但这个 import 路径在 Claude Code 环境中可能不可用（Claude Code 不走 Python runtime）
2. Skill 目录结构不一致：`scan`/`analyze`/`validate` 是 `SKILL.md` 子目录，但 `build-site` 是扁平 `.md` 文件
3. `.claude/settings.local.json` 残留了旧的文件移动操作的权限记录，应该清理

---

## 四、数据管理 ⭐⭐⭐ (3/5)

### 数据 Schema (`SCHEMA.md`)

非常详尽的数据字典，定义了每个字段的类型、用途、必填性。这是项目文档的亮点。

### 数据管道断点:

1. **`articles.json` vs `changes.json` 的数据孤岛**
   - `article_discovery.py` 写入 `articles.json`（V1 架构）
   - SCHEMA.md 已将文章合并到 `changes.json` 统一管理（V2 架构）
   - 但 `article_discovery.py` 的 `update_articles_json()` 仍在写旧的 `articles.json` 路径
   - 两套数据没有打通

2. **`reference/data-map.md` 已过时**
   - 引用了不存在的 `config.json`、`articles.json`、`price-changes.json`
   - 这些文件在 V2 架构中已合并到 `changes.json` + `site.json`
   - 更新频率描述（"每周"）与自动管道的实际频率不符

3. **信号采集结果为 0**
   - `data/signals/2026-07-21.json` 显示 `count: 0, signals: []`
   - 可能原因：DailyHotApi 科技源当天没有匹配关键词的内容，或者 API 不可达

4. **机会卡目录为空**
   - `data/cards/` 只有 `.gitkeep`，没有生成任何机会卡
   - 整个系统的核心产出物（机会卡）从未被实际产出

5. **缺少 `docker-compose.yml`**
   - CLAUDE.md 中第 3 行和工作流中引用了 `docker compose up -d`
   - 但项目根目录下不存在 `docker-compose.yml`
   - DailyHotApi 和 RSSHub 的 docker-compose 分别在各自的子目录里

---

## 五、缺失项 ⚠️

| 类别 | 缺失项 | 影响 |
|------|--------|------|
| 基础设施 | `docker-compose.yml`（根目录） | 无法一键启动采集服务 |
| 测试 | 零测试代码 | 修改代码无安全网 |
| CI/CD | 无 GitHub Actions | 手动运行一切 |
| 监控 | 无告警机制 | 采集失败不会主动通知 |
| 文档 | `data-map.md` 过时 | 误导新贡献者 |
| 数据 | 机会卡从未生成 | 系统核心产出物缺失 |
| 数据 | `articles.json` 与 `changes.json` 未打通 | 文章数据进入孤岛 |

---

## 六、建议改进（按优先级）

### 🔴 高优先级

1. **修复 `article_discovery.py` 的数据流向** — 让它写入 `changes.json`（kind: "article"）而不是独立的 `articles.json`，或者直接废弃 `articles.json`
2. **创建根目录 `docker-compose.yml`** — 把 DailyHotApi 和 RSSHub 的 Docker 配置整合到一个文件，让 `docker compose up -d` 能真正工作
3. **更新 `reference/data-map.md`** — 对齐 V2 架构，删除已废弃的文件引用

### 🟡 中优先级

4. **统一 skill 目录结构** — 把 `build-site.md` 也改成 `build-site/SKILL.md` 格式
5. **清理 `.claude/settings.local.json`** — 删除旧的文件移动权限条目
6. **添加 TypedDict 类型注解** — 为 `items`、`plans`、`changes` 等核心数据结构定义类型
7. **增加日志系统** — 替换 `print()` 为 `logging` 模块，支持按级别输出

### 🟢 低优先级

8. **添加测试** — 至少给 `storage.py` 和 `token_estimator.py` 加单元测试
9. **添加采集失败告警** — 当连续 N 次采集结果为空时发送通知
10. **机会卡自动生成** — 在 `/scan` 流程中自动产出机会卡 Markdown 文件

---

## 七、总结

这个项目有一个**非常清晰的愿景**和**务实的架构设计**。Claude Code Native 的决策是亮点——它避免了独立创作者的"系统维护陷阱"。Python 采集器的代码质量扎实，异步设计、错误处理、API 降级都做得不错。数据 Schema 文档非常详尽，是项目治理的好基础。

主要问题在于**数据管道的断点**——有几处新旧架构迁移的遗留问题没有清理干净，导致部分数据流无法贯通。另外缺少测试和监控，随着系统复杂度增加，维护成本会上升。

对于每周 5-10h 的投入来说，这个项目的完成度已经相当高了。修复上述高优先级问题（预计 2-3h）后，系统应该能跑通完整的"采集→分析→机会卡"闭环。

---

## 八、已修复（2026-07-21）

| 问题 | 修复内容 |
|------|---------|
| `article_discovery.py` 数据孤岛 | 重写 `update_articles_json()` → `update_changes_json()`，文章直接写入 `changes.json`（kind: "article"），格式对齐 SCHEMA.md |
| `pipeline.py` 文档过时 | 更新 docstring：`articles.json` → `changes.json` |
| CLAUDE.md 多处过时 | 移除 Docker 强制要求（标注为已手动部署）、修正 `build_html.py` → `build.py`、更新目录树和 skill 路径 |
| `reference/data-map.md` 过时 | 全面重写：对齐 V2 架构，删除废弃文件引用，新增 `vendors.json`、`signals/`、机会卡问题 |
| `.claude/settings.local.json` 残留 | 清理旧的 `mv` 权限条目，保留 skills 目录访问权限 |