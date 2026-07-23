# 厂商参考手册 — 定价页 URL + 联盟推广链接

> 最后更新: 2026-07-23
>
> **一站式厂商信息**：定价页（数据采集用）+ 联盟推广链接（"优惠购买"按钮用）+ 返佣信息。
> 与 `vendors.json` 保持同步，本文件为人工可读版本。

---

## 链接格式规范

- **定价页 URL** → 写入 `vendors.json` 的 `urls.pricing`，用于数据采集
- **联盟推广链接** → 写入 `vendors.json` 的 `urls.affiliate`，`plans[].action` 优先使用
- 统一使用 `?ref=fanluzhe` 或平台指定的邀请参数
- 推广海报统一存放 `assets/posters/`，命名规则 `{平台英文名}.png`
- 所有推广链接必须在此文件登记后才能上线

---

## 已接入厂商（11 家）

### 自动提取（7 家）

| 平台 | 定价页 URL | 套餐 | 提取方案 |
|------|-----------|------|---------|
| 智谱AI | https://open.bigmodel.cn/pricing | Lite ¥49 / Pro ¥149 / Max ¥469 | Playwright |
| DeepSeek | https://api-docs.deepseek.com/quick_start/pricing | 虚拟套餐 ¥40 / ¥200 | BS4 静态 |
| Kimi | https://platform.kimi.com/docs/pricing/chat | Andante ¥49 / Allegretto ¥199 (paused) | Playwright |
| MiniMax | https://platform.minimaxi.com/docs/guides/pricing-token-plan | Plus ¥49 / Max ¥119 / Ultra ¥469 | BS4 静态 |
| 腾讯云 | https://cloud.tencent.com/product/tokenhub | Lite ¥40 / Pro ¥200 | BS4 静态 |
| Claude | https://claude.com/pricing | Pro $20 / Max $100 | Playwright |
| GitHub | https://github.com/features/copilot/plans | Free $0 / Pro $10 / Pro+ $39 / Max $100 | Playwright |

### 手动维护（4 家）

| 平台 | 定价页 URL | 套餐 | 原因 |
|------|-----------|------|------|
| 字节·方舟 | https://www.volcengine.com/ark | Lite ¥40 / Pro ¥200 | Bot 检测拦截 |
| 阿里·百炼 | https://bailian.aliyun.com | Pro ¥200 | 需登录控制台 |
| Codex | https://openai.com/chatgpt/pricing/ | Plus $20 | Cloudflare 拦截 |
| 小米·MiMo | https://platform.xiaomimimo.com/token-plan | Lite ¥39 / Pro ¥329 | SPA，待适配 |

---

## 联盟推广链接

| 平台 | 联盟链接 | 返佣 |
|------|---------|------|
| 智谱AI | `https://www.bigmodel.cn/invite?icode=PJ048yz3Fl63Urk70glaphiFMcmMNhdZwR%2F1emOiVXY%3D` | 新用户注册得 2000万 Tokens |
| MiniMax | `https://platform.minimaxi.com/subscribe/token-plan?code=Gbn3DuotEx&source=link` | 好友 9折，邀请人 10% 返利 |
| 小米·MiMo | `https://platform.xiaomimimo.com?ref=NB2PJ5` | 双方各得 ¥10 体验金 + 首单 9 折 |
| Claude | 待添加 | 待确认 |
| GitHub | 待添加 | 待确认 |
| 腾讯云 | 待添加 | 云推荐奖励 |
| 字节·方舟 | 待添加 | 待确认 |
| 阿里·百炼 | 待添加 | 阿里云推广返佣 |
| DeepSeek | 无推广体系 | — |
| Kimi | 待添加 | 待确认 |
| Codex | 待添加 | 待确认 |

---

## 小米·MiMo 详细 URL

| 用途 | URL |
|------|-----|
| Token Plan 订阅 | https://platform.xiaomimimo.com/token-plan |
| MiMoCode 主页 | https://mimo.xiaomi.com/zh/mimocode |
| API 按量计费 | https://mimo.mi.com/docs/zh-CN/price/pay-as-you-go |

> V2 系列已于 2026.6.30 下线，V2.5 系列已上线。Token Plan 页当前只展示 Max 年付套餐。

---

## 数据文件映射

| 数据 | 存储位置 | 用途 |
|------|---------|------|
| 厂商元信息 | `vendors.json` | 采集策略、URL、配色 |
| 套餐价格 | `plans.json` | HTML 渲染数据源 |
| 变动时间线 | `changes.json` | 推荐页"最近变动" |
| 站点配置 | `site.json` | 博主信息、推荐分组、社群 |
| 数据 Schema | `SCHEMA.md` | 字段定义 + 枚举 |

---

## 结算记录

| 日期 | 平台 | 金额 | 备注 |
|------|------|------|------|
| 待记录 | | | |

---

## 变更记录

| 日期 | 变更 |
|------|------|
| 2026-07-23 | 同步当前实际状态：11 家厂商，7 自动提取/4 手动；新增 MiMo 3 URL；更新 Claude/GitHub 提取状态 |
| 2026-07-22 | 合并 pricing-urls.md + affiliate-links.md → 本文件 |
| 2026-07-21 | 原始两文件分别更新 |