# 部署链路 — codingplan.fyi

> 线上站点与本仓库构建产物的关系、部署方式、待决策事项。
> 最后更新：2026-08-02

---

## 部署目标态

```
project/codingplan-saver/data/*.json   （数据真相源，7 家厂商 / 20 条套餐）
        ↓ tools/builder/build.py
project/codingplan-site/index.html     （部署目录，单文件 HTML）
        ↓ tools/deploy/deploy.sh  →  edgeone makers deploy
EdgeOne Makers 项目 codingplan  →  codingplan-llnvmecs.edgeone.cool（默认域名）
                                  →  codingplan.fyi（待绑定自定义域名）
```

`/codingplan-page` 工作流的终点是 `tools/deploy/deploy.sh`，支持 `preview`（临时链接验证）和 `production`（更新默认域名）两种环境。

## 部署平台：腾讯云 EdgeOne Makers

- 国内厂商、国内节点，对目标用户（国内开发者）访问速度优于 Cloudflare
- 边缘函数 + KV + 定时触发能力，为后续实测测速功能预留运行位
- CLI 部署（`edgeone makers deploy`）可挂进 `/codingplan-page` 工作流末尾
- **访问鉴权**：当前项目控制台开了访问鉴权，production 也需要 `eo_token` 参数（3 小时有效）。要免 token 访问需去控制台关掉"访问限制"。

## 迁移路线（四步）

```
① 通路  edgeone login → 创建项目 → 首次部署验证              ✅ 已完成（2026-07-31）
② 对齐  线上抢救数据回填到 project/codingplan-saver/data/     ✅ 已完成（7 家核心厂商）
③ 切换  EdgeOne 控制台绑定 codingplan.fyi（CNAME + SSL）      ⏳ 待执行
④ 延长  /codingplan-page 终点 = deploy.sh（build → 部署）     ✅ 已完成
```

## 数据抢救

线上 `codingplan.fyi` 的数据文件已封存至 `data/recovery/codingplan-fyi-2026-07-31/`（101 条套餐 / 29 家厂商 + config.json + HTML 壳）。当前 `project/codingplan-saver/data/` 只跟踪 7 家核心厂商的价格，recovery 数据作为历史参考和推广链接来源。

## 域名说明

`.fyi` 域名无法 ICP 备案 → 大陆加速区域不可用，走海外节点。若未来需要大陆节点，需换可备案域名。
