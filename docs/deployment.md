# 部署链路 — codingplan.fyi

> 线上站点与本仓库构建产物的关系、部署方式现状、待决策事项。
> 最后更新：2026-07-31（决策落地：迁移至腾讯云 EdgeOne Makers）

---

## 决策（2026-07-31 晚）

**部署目标平台：腾讯云 EdgeOne Makers**（边缘 Web 与 Agent 托管平台，3200+ 边缘节点）。

理由：
- 国内厂商、国内节点，对目标用户（国内开发者）访问速度优于 Cloudflare
- 边缘函数 + KV + 定时触发能力，为后续**实测测速**功能预留运行位（测速数据可存 KV、API 化输出）
- CLI 部署（`edgeone makers deploy`）可挂进 `/codingplan-page` 工作流末尾，打通最后一段

**数据抢救已完成**：线上站点的数据文件可直接下载（`codingplan.fyi/plans.json` 运行时加载），
已封存至 `data/recovery/codingplan-fyi-2026-07-31/`（101 条套餐 / 29 家厂商 + config.json + HTML 壳）。
原"找回源码"问题降级为"数据回填"问题（见下方回填计划）。

## 迁移路线（四步）

```
① 通路  edgeone login → 创建项目 → repo 版（14 家）部署到 staging 域名验证      ✅ 已完成（2026-07-31）
② 对齐  线上独有的厂商回填到 project/codingplan-saver/data/（builder 真相源）→ kb_migrate.py 同步 aikb  ✅ 已完成（14→28 家）
③ 切换  EdgeOne 控制台绑定 codingplan.fyi（CNAME 验证，SSL 自动）→ DNS 从 Cloudflare 切出  ⏳ 待执行
④ 延长  /codingplan-page 终点 = tools/deploy/deploy.sh（build → 同步 site 目录 → makers deploy）  ✅ 已完成（Step 6 接进 SKILL）
```

### 数据流（② 回填的关键认知）

```
project/codingplan-saver/data/*.json   ← 真相源（builder/build.py 只读这里）
        ↓ tools/collector/collector/kb_migrate.py
aikb/database/*.json                   ← 下游产物（知识库元数据，自动同步）
```

**回填主改对象是 `project/codingplan-saver/data/`，不是 `aikb/`。** aikb 是由
`kb_migrate.py` 从 project 自动生成的下游镜像。改错方向会导致重新部署后站点内容不变。

第一批回填（2026-07-31）：14 家厂商 / 45 条 plans，由 `tools/builder/backfill_batch1.js`
从 `data/recovery/codingplan-fyi-2026-07-31/plans.json` 转换而来。跳过摩尔线程（无价占位）、
商汤·日日新（仅免费公测），第二批待真实定价。

注意：`.fyi` 域名无法 ICP 备案 → 大陆加速区域不可用，走海外节点（与现状 Cloudflare 持平）；
若未来需要大陆节点，需换可备案域名。

---

## 历史侦查（2026-07-31 白天，决策前）

**线上站点与本仓库 `dist/` 产物是两套不同的代码，当时不存在自动化部署链路。**

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

## 这意味着什么（⚠️ 决策前的历史诊断，已被上方决策取代）

> 以下内容反映的是 **2026-07-31 决策前**的认知状态。当前部署链路已打通（见文首「迁移路线」），
> 这里的描述仅供追溯历史问题。**现状以文首决策和「部署目标态」为准。**

决策前，Pipeline B 的终点（`dist/codingplan-saver.html`）曾是一个本地死胡同：

```
pipeline 采集 → 审阅 → plans.json 更新 → build → dist/*.html   ✅ 这段是通的
dist/*.html → 线上 codingplan.fyi                              ❌ 当时这段不存在
```

当时即使定时采集每天跑，数据更新也无法触达用户。同时存在**两个真相源**的风险：repo 数据与线上数据各自漂移。**这些问题已被 2026-07-31 的回填（14→28 家）和 EdgeOne 部署链路解决。**

> 当时的三选一方案（A 找回源码 / B repo 覆盖 / C 双轨）已被 2026-07-31 晚的决策取代——
> 数据直接从线上 plans.json 抢救（无需源码），部署平台改用 EdgeOne Makers，见文首。

---

## 部署目标态

```
project/codingplan-saver/data/*.json   （数据，本仓库维护，回填后 28 家）
        ↓ tools/builder/build.py
project/codingplan-site/index.html     （部署目录）
        ↓ tools/deploy/deploy.sh  →  edgeone makers deploy
EdgeOne Makers 项目 codingplan  →  staging 域名验证  →  codingplan.fyi（DNS 切换后）
```

`/codingplan-page` 工作流的终点延长为 `tools/deploy/deploy.sh`，由用户确认后执行最后一步。
