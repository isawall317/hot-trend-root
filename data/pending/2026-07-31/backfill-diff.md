# 回填 Review — 第一批（2026-07-31）

> 数据源：`data/recovery/codingplan-fyi-2026-07-31/plans.json`（线上抢救，29 家/101 条）
> 转换脚本：`tools/builder/backfill_batch1.js`（可重跑复现，估算规则全部在此）
> 目标目录：`project/codingplan-saver/data/`（builder 真相源）

## 规模变化

| | 回填前 | 回填后 | 增量 |
|---|---|---|---|
| vendors | 14 | 28 | +14 |
| plans | 28 | 73 | +45 |
| changes | 57 | 71 | +14 |
| aikb services | 16 | 30 | +14 |
| aikb models | — | 175 | — |

## 新增厂商（14 家）

| vendorId | 厂商 | category | 国家 | 服务类型 |
|---|---|---|---|---|
| unicom | 联通云 | cloud-maas | 中国 | coding-plan+token-plan |
| huawei | 华为云 | cloud-maas | 中国 | token-plan |
| xunfei | 讯飞·星火 | cloud-maas | 中国 | coding-plan |
| ctyun | 天翼云 | cloud-maas | 中国 | coding-plan |
| stepfun | 阶跃星辰 | model-maker | 中国 | coding-plan |
| zhipu-intl | 智谱国际版 | model-maker | 全球 | coding-plan |
| jd | 京东云 | cloud-maas | 中国 | coding-plan |
| cmcc | 移动云 | cloud-maas | 中国 | coding-plan |
| infini | 无问芯穹 | aggregator | 中国 | coding-plan |
| taotoken | TaoToken | aggregator | 中国 | coding-plan |
| ollama | Ollama | vertical-cloud | 全球 | coding-plan |
| opencode | OpenCode | vertical-cloud | 全球 | token-plan |
| scnet | 超算 | cloud-maas | 中国 | coding-plan |
| uyun | 优云智算 | cloud-maas | 中国 | coding-plan |

## 新增 plans（45 条）— 估算来源标注

| id | 厂商 | 套餐 | 类型 | 月费 | measured(M) | 来源 |
|---|---|---|---|---|---|---|
| zhipu-intl-lite | 智谱国际版 | Lite | Coding Plan | ¥18 | 90 | ⚠️估算(model-maker 5.0 M/元) |
| zhipu-intl-pro | 智谱国际版 | Pro | Coding Plan | ¥72 | 360 | ⚠️估算(model-maker 5.0 M/元) |
| zhipu-intl-max | 智谱国际版 | Max | Coding Plan | ¥160 | 800 | ⚠️估算(model-maker 5.0 M/元) |
| uyun-mini | 优云智算 | Mini | Coding Plan | ¥49 | 147 | ⚠️估算(cloud-maas 3.0 M/元) |
| uyun-lite | 优云智算 | Lite | Coding Plan | ¥99 | 297 | ⚠️估算(cloud-maas 3.0 M/元) |
| uyun-basic | 优云智算 | Basic | Coding Plan | ¥199 | 597 | ⚠️估算(cloud-maas 3.0 M/元) |
| uyun-pro | 优云智算 | Pro | Coding Plan | ¥499 | 1497 | ⚠️估算(cloud-maas 3.0 M/元) |
| uyun-max | 优云智算 | Max | Coding Plan | ¥799 | 2397 | ⚠️估算(cloud-maas 3.0 M/元) |
| uyun-ultra | 优云智算 | Ultra | Coding Plan | ¥999 | 2997 | ⚠️估算(cloud-maas 3.0 M/元) |
| opencode-go | OpenCode | Go | Token Plan | ¥10 | 150 | ⚠️估算(cloud Token 15 M/元) |
| xunfei-专业版 | 讯飞·星火 | 专业版 | Coding Plan | ¥39 | 117 | ⚠️估算(cloud-maas 3.0 M/元) |
| xunfei-高效版 | 讯飞·星火 | 高效版 | Coding Plan | ¥199 | 597 | ⚠️估算(cloud-maas 3.0 M/元) |
| xunfei-速通版 | 讯飞·星火 | 速通版 | Coding Plan | ¥699 | 2097 | ⚠️估算(cloud-maas 3.0 M/元) |
| taotoken-lite | TaoToken | Lite | Coding Plan | ¥39 | 117 | ⚠️估算(cloud-maas 3.0 M/元) |
| taotoken-pro | TaoToken | Pro | Coding Plan | ¥149 | 447 | ⚠️估算(cloud-maas 3.0 M/元) |
| taotoken-max | TaoToken | Max | Coding Plan | ¥388 | 1164 | ⚠️估算(cloud-maas 3.0 M/元) |
| unicom-lite | 联通云 | Lite | Coding Plan | ¥40 | 120 | ⚠️估算(运营商 cloud-maas 3.0 M/元) |
| unicom-pro | 联通云 | Pro | Coding Plan | ¥200 | 600 | ⚠️估算(运营商 cloud-maas 3.0 M/元) |
| unicom-个人-lite | 联通云 | 个人 Lite | Token Plan | ¥15 | 6 | ✅原值 |
| unicom-个人-pro | 联通云 | 个人 Pro | Token Plan | ¥30 | 12 | ✅原值 |
| unicom-个人-max | 联通云 | 个人 Max | Token Plan | ¥45 | 18 | ✅原值 |
| unicom-团队-lite | 联通云 | 团队 Lite | Token Plan | ¥198 | 200 | ✅原值 |
| unicom-团队-pro | 联通云 | 团队 Pro | Token Plan | ¥698 | 800 | ✅原值 |
| unicom-团队-max | 联通云 | 团队 Max | Token Plan | ¥1398 | 2000 | ✅原值 |
| jd-lite | 京东云 | Lite | Coding Plan | ¥40 | 120 | ⚠️估算(运营商 cloud-maas 3.0 M/元) |
| jd-pro | 京东云 | Pro | Coding Plan | ¥200 | 600 | ⚠️估算(运营商 cloud-maas 3.0 M/元) |
| stepfun-flash-mini | 阶跃星辰 | Flash Mini | Coding Plan | ¥49 | 245 | ⚠️估算(model-maker 5.0 M/元) |
| stepfun-flash-plus | 阶跃星辰 | Flash Plus | Coding Plan | ¥99 | 495 | ⚠️估算(model-maker 5.0 M/元) |
| stepfun-flash-pro | 阶跃星辰 | Flash Pro | Coding Plan | ¥199 | 995 | ⚠️估算(model-maker 5.0 M/元) |
| stepfun-flash-max | 阶跃星辰 | Flash Max | Coding Plan | ¥699 | 3495 | ⚠️估算(model-maker 5.0 M/元) |
| ctyun-glm-lite | 天翼云 | GLM Lite | Coding Plan | ¥49 | 147 | ⚠️估算(运营商 cloud-maas 3.0 M/元) |
| ctyun-glm-pro | 天翼云 | GLM Pro | Coding Plan | ¥149 | 447 | ⚠️估算(运营商 cloud-maas 3.0 M/元) |
| ctyun-glm-max | 天翼云 | GLM Max | Coding Plan | ¥469 | 1407 | ⚠️估算(运营商 cloud-maas 3.0 M/元) |
| cmcc-lite | 移动云 | Lite | Coding Plan | ¥40 | 120 | ⚠️估算(运营商 cloud-maas 3.0 M/元) |
| cmcc-pro | 移动云 | Pro | Coding Plan | ¥200 | 600 | ⚠️估算(运营商 cloud-maas 3.0 M/元) |
| scnet-lite | 超算 | Lite | Coding Plan | ¥20 | 30 | ⚠️估算(弱模型 1.5 M/元) |
| scnet-pro | 超算 | Pro | Coding Plan | ¥100 | 150 | ⚠️估算(弱模型 1.5 M/元) |
| infini-lite | 无问芯穹 | Lite | Coding Plan | ¥40 | 120 | ⚠️估算(聚合商 3.0 M/元) |
| infini-pro | 无问芯穹 | Pro | Coding Plan | ¥200 | 600 | ⚠️估算(聚合商 3.0 M/元) |
| ollama-pro | Ollama | Pro | Coding Plan | ¥20 | 60 | ⚠️估算(cloud 3.0 M/元) |
| ollama-max | Ollama | Max | Coding Plan | ¥100 | 300 | ⚠️估算(cloud 3.0 M/元) |
| huawei-lite | 华为云 | Lite | Token Plan | ¥59 | 50 | ✅原值 |
| huawei-standard | 华为云 | Standard | Token Plan | ¥149 | 130 | ✅原值 |
| huawei-pro | 华为云 | Pro | Token Plan | ¥399 | 380 | ✅原值 |
| huawei-max | 华为云 | Max | Token Plan | ¥799 | 880 | ✅原值 |

## measuredMonthlyToken 估算说明

- **原值（10 条）**：华为云 4 条（recovery 有 measuredMonthlyTokenLimit）、联通云 Token Plan 6 条（tokenLimit 数值即 M）
- **估算（35 条）**：按 category×type 经验比（来自现有 28 条反推）：
  - 运营商/cloud-maas Coding Plan：3.0 M/元（对齐腾讯云/小米同档）
  - model-maker Coding Plan（阶跃/智谱国际版）：5.0 M/元（对齐智谱/字节）
  - 弱模型（超算 rating=2）：1.5 M/元（打折）
  - OpenCode（tokenLimit 未公开，Token Plan）：15 M/元（cloud Token 中位）
- 所有估算值已在 plan 的 `notes` 字段标注，待实测校准

## 跳过的厂商（第二批）

| 厂商 | 原因 |
|---|---|
| 摩尔线程 | 4 条 plans 月费全为 0/-（纯占位），等真实定价 |
| 商汤·日日新 | 仅 Free·公测（月费 0），Lite/Pro 未上线 |

## 字段映射（recovery → project）

保留：vendor/plan/type/models/rating/tags/tokenLimit/action/firstMonthPrice/monthlyPrice
重命名：measuredMonthlyTokenLimit → measuredMonthlyToken
删除：quarterlyPrice/yearlyPrice/fiveHoursRequests/weeklyRequests/benefits/note（SCHEMA 332 行）
新增：id/vendorId/tier/currency/status/source/updatedAt/category/billingCore/migration

## 新增 changes（14 条 new_plan）

每家厂商一条，仿 TaoToken 模板，`relatedPlans` 已填充对应 plan id。

```
2026-07-31-unicom-new_plan  联通云 (8 plans)
2026-07-31-huawei-new_plan  华为云 (4 plans)
2026-07-31-xunfei-new_plan  讯飞·星火 (3 plans)
2026-07-31-ctyun-new_plan  天翼云 (3 plans)
2026-07-31-stepfun-new_plan  阶跃星辰 (4 plans)
2026-07-31-zhipu-intl-new_plan  智谱国际版 (3 plans)
2026-07-31-jd-new_plan  京东云 (2 plans)
2026-07-31-cmcc-new_plan  移动云 (2 plans)
2026-07-31-infini-new_plan  无问芯穹 (2 plans)
2026-07-31-taotoken-new_plan  TaoToken (3 plans)
2026-07-31-ollama-new_plan  Ollama (2 plans)
2026-07-31-opencode-new_plan  OpenCode (1 plans)
2026-07-31-scnet-new_plan  超算 (2 plans)
2026-07-31-uyun-new_plan  优云智算 (6 plans)
```

## 验收

- [x] build.py 成功：28 家 / 73 条 plans / 162.4 KB（原 121 KB）
- [x] plans.json 所有 plan 含 22 必填字段，无 undefined（5 个 null 是原有聚合商，非本次引入）
- [x] vendors/plans/changes 三者 vendor 名一致，无悬空引用、无 id 重复
- [x] aikb/database 已由 kb_migrate.py 同步（含 country/massServices）
- [x] deployment.md 第②步表述已修正（project 为真相源，aikb 为下游）
- [ ] **待人工 review 本文件后 commit**

## 未做（按计划留待）

- 未执行 deploy.sh（部署由你单独触发）
- 未补 `aikb/vendors/*.md` 知识库正文（不影响上站）
- 未处理 401（默认域名区域限制，最终走自定义域名解决）
- 第二批摩尔线程/商汤待真实定价
