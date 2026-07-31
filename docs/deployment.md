# 部署链路 — codingplan.fyi

> 线上站点与本仓库构建产物的关系、部署方式现状、待决策事项。
> 最后更新：2026-07-31（由全项目 review 侦查产出）

---

## 现状结论（2026-07-31 侦查）

**线上站点与本仓库 `dist/` 产物是两套不同的代码，目前不存在自动化部署链路。**

| 维度 | 线上 codingplan.fyi | 本仓库 `dist/codingplan-saver.html` |
|------|--------------------|------------------------------------|
| 标题 | Coding Plan 对比工具 - 国内29大主流AI平台套餐对比… | CodingPlan 省钱攻略 - AI Coding Plan 选型指南 |
| 体积 | ~424 KB | ~121 KB |
| 厂商覆盖 | **29 家**（含讯飞星火、阶跃星辰、无问芯穹、联通云、天翼云、移动云等 KB 之外的厂商） | **14 家**（aikb KB 范围，28 条 plans） |
| 页面结构 | 双版本：根路径 classic 版 + `/v2/` 新版（localStorage `codingplanSiteEdition` 切换，308 重定向） | 单页 3 Tab（推荐/对比/社群） |
| SEO | 有百度站长验证码，面向搜索流量优化 | 无验证码 |
| 托管 | Cloudflare（`server: cloudflare`），Pages 可能性最大 | — |

### 已排除的可能

- ❌ GitHub 上无对应源码 repo（`gh repo list` 只有 hot-trend-root 和 dailyhotapi-vercel）
- ❌ 本机 `~/Gits/` 下无网站源码目录
- ❌ `reference/codingplan/`（.gitignore 中预留的位置）不存在
- ❌ 本机未安装 wrangler（Cloudflare CLI）
- ⚠️ `~/Gits/dist/codingplan-saver.html` 存在一份 7-21 的旧版拷贝（51KB）——说明历史上曾有"手动复制 dist → 某处上传"的动作

### 推断

线上站点源码**位置未知**：可能在另一台机器、已删除的本地目录、或直接在 Cloudflare Dashboard 上传迭代的产物。线上版本（29 家厂商 + v2 重构 + SEO 验证）在功能和覆盖面上**领先于**本仓库版本——真实开发曾短暂"出走"到仓库之外。

---

## 这意味着什么

当前 Pipeline B 的终点（`dist/codingplan-saver.html`）是一个本地死胡同：

```
pipeline 采集 → 审阅 → plans.json 更新 → build → dist/*.html   ✅ 这段是通的
dist/*.html → 线上 codingplan.fyi                              ❌ 这段不存在
```

即使定时采集每天跑，数据更新也无法触达用户。同时存在**两个真相源**的风险：repo KB（14 家）与线上数据（29 家）各自漂移，越久越难合并。

---

## 待决策（三选一）

### 方案 A：找回线上源码，纳入 repo（推荐）

线上版本是更先进的资产（29 家覆盖、v2 交互、百度收录权重），值得保留。

1. 找回线上源码（检查其他机器 / Time Machine / Cloudflare Pages 部署历史 / 浏览器下载记录）
2. 放入 `project/codingplan-site/`（与 `codingplan-saver/` 数据项目并列）
3. 线上多出来的 15 家厂商反向补录进 `aikb/`
4. 建立 `build → wrangler pages deploy` 的发布步骤

### 方案 B：以 repo 为准，重新部署

放弃线上增量，用 repo 的 14 家版本覆盖部署。代价：丢失 29 家扩展、v2 交互、可能的 SEO 资产。**不推荐**——除非线上源码确认无法找回。

### 方案 C：维持双轨（现状默认）

repo 只做数据采集和 KB 维护，线上站点手动维护。代价：两个真相源持续漂移，pipeline 产出的价值无法变现。

---

## 找回线索清单

排查线上源码时可以检查：

- [ ] 其他常用机器（公司电脑 / 旧 Mac）的 `~/Gits`、`~/Projects`
- [ ] Time Machine / iCloud 备份中 2026-06 ~ 07 的目录快照
- [ ] Cloudflare Dashboard → Pages 项目的部署历史（可看到每次部署的来源：Git 集成 vs 直接上传）
- [ ] 若是 Git 集成：Dashboard 里能看到连接的 repo 和分支
- [ ] 浏览器历史 / 下载目录中的上传记录

---

## 部署目标态（方案 A 落地后）

```
project/codingplan-saver/data/*.json   （数据，本仓库维护）
        ↓ build
project/codingplan-site/               （线上站点源码，纳入 repo）
        ↓ wrangler pages deploy（或 Git push 触发 Pages 自动部署）
codingplan.fyi
```

`/codingplan-page` 工作流的终点从 `dist/` 延长到 `wrangler pages deploy`，由用户确认后执行最后一步。
