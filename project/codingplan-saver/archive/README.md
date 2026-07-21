# V1 归档（多页面架构）

这是 codingplan-saver 的 V1 实现，已被 V2（单文件 + skill 驱动）替代。

## 保留内容

| 路径 | 内容 |
|------|------|
| `old-multi-page/` | 6 个独立 HTML 页面（index/compare/blog/article/wizard/join + coding-agents） |
| `old-scripts/shared.js` | 渲染逻辑（全局 CPS 对象 + 渲染函数） |
| `old-styles/shared.css` | 设计 token 和样式系统（V2 沿用） |
| `old-src/` | Vite + React 脚手架（未真正启用） |
| `old-builder/build_html.py` | 旧 Python 单文件生成器 |
| `old-config.json` | 迁移前原始 site 配置 |
| `old-plans.json` | 迁移前原始套餐数据（31 条） |
| `old-articles.json` | 迁移前原始文章数据 |
| `old-price-changes.json` | 迁移前原始价格变动数据 |
| `old-coding-agents.json` | 旧的 coding-agents 配置 |

## 为什么不删

保留供参考和回滚。V2 的 CSS 设计 token 直接继承自 `old-styles/shared.css`，JS 工具函数移植自 `old-scripts/shared.js`。

## V2 在哪

V2 实现在 `../data/`（JSON 数据）+ `../template/`（HTML 模板）+ `../../tools/builder/build.py`（构建脚本）+ `../../../.claude/skills/build-site.md`（skill 文档）。
