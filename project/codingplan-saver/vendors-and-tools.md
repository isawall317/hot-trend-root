# 厂商与套餐数据源

> **定位**：本项目跟踪的厂商和套餐的源头清单。
> **本文件由 `kb_to_md.py` 从 `project/codingplan-saver/data/` 自动生成，勿手工编辑。**
> 最后更新：2026-08-05

---

## 一、AI 模型厂商（7 家核心跟踪）

> 定价页 URL 用于采集，推广链接用于"优惠购买"按钮。

| ID | 厂商 | 分类 | 定价页 URL | 提取策略 | 推广链接 | 备注 |
|----|------|:--:|------|:--:|------|------|
| zhipu | 智谱AI | 模型厂商 | https://bigmodel.cn/glm-coding | BS4 静态 | https://www.bigmodel.cn/invite?icode=PJ0 | 7-30 套餐改版，积分制，旧版¥49/149/469已停 |
| bytedance | 字节·方舟 | 模型厂商 | https://console.volcengine.com/ark/region:cn-beijing/subscription/coding-plan | BS4 静态 | https://api.dreamfree.space/c/s/cpyqfang | 反爬+SPA，依赖人工快照 |
| tencent | 腾讯云 | 云厂商 MaaS | https://cloud.tencent.com/product/tokenhub | BS4 静态 | https://api.dreamfree.space/c/s/cpyqteng | Coding Plan已售罄，主推Token Plan 4档 |
| deepseek | DeepSeek 官方 | 模型厂商 | https://api-docs.deepseek.com/zh-cn/quick_start/pricing | BS4 静态 | 待添加 | 纯API按量，无月订阅套餐，即将峰谷定价 |
| minimax | MiniMax | 模型厂商 | https://platform.minimaxi.com/subscribe/token-plan | BS4 静态 | https://platform.minimaxi.com/subscribe/ | Token Plan用量翻倍，多模态全共享额度 |
| kimi | Kimi | 模型厂商 | https://www.kimi.com/membership/pricing | BS4 静态 | https://api.dreamfree.space/c/s/cpyqkimi | 新会员体系即将上线，Kimi权益与Kimi Code将拆分 |
| bailian | 阿里·百炼 | 云厂商 MaaS | https://www.aliyun.com/benefit/scene/codingplan | manual | https://api.dreamfree.space/c/s/cpyqbail | Lite已停售(3-20)，只剩Pro，限量抢购。无 parser，需补 sources/bailian.py 才能自动 |

提取策略：`Playwright` = 渲染 SPA 后解析 | `BS4 静态` = 直接解析文档页 | `manual` = 人工定期检查
---

## 二、套餐数据（20 条）

| 厂商 | 套餐 | 类型 | 月费 | 月 Token | 每元 Token | 状态 |
|------|------|------|------|---------|-----------|------|
| DeepSeek 官方 | V4-Flash 按量 | API 按量 | 按量 | — | — | active |
| DeepSeek 官方 | V4-Pro 按量 | API 按量 | 按量 | — | — | active |
| Kimi | 日常使用 | 会员 | ¥39 | 42M | 1.08 | active |
| MiniMax | Plus | Token Plan | ¥49 | 600M | 12.24 | active |
| MiniMax | Max | Token Plan | ¥119 | 1800M | 15.13 | active |
| MiniMax | Ultra | Token Plan | ¥469 | 7100M | 15.14 | active |
| 字节·方舟 | Auto | Coding Plan | ¥9.9 | 11M | 1.11 | active |
| 字节·方舟 | Agent Lite | Agent Plan | ¥9.9 | 11M | 1.11 | active |
| 字节·方舟 | Agent Large | Agent Plan | ¥1000 | 1085M | 1.08 | active |
| 智谱AI | GLM-5.2 按量 | API 按量 | 按量 | — | — | active |
| 智谱AI | GLM-5-Turbo 按量 | API 按量 | 按量 | — | — | active |
| 智谱AI | Lite | Coding Plan | ¥118 | 87M | 0.74 | active |
| 智谱AI | Pro | Coding Plan | ¥538 | 522M | 0.97 | active |
| 智谱AI | Max | Coding Plan | ¥1078 | 1218M | 1.13 | active |
| 腾讯云 | Token Plan Lite | Token Plan | ¥39 | 35M | 0.90 | active |
| 腾讯云 | Token Plan Standard | Token Plan | ¥99 | 100M | 1.01 | active |
| 腾讯云 | Coding Plan Pro | Coding Plan | ¥200 | 4500M | 22.50 | sold_out |
| 腾讯云 | Token Plan Pro | Token Plan | ¥299 | 320M | 1.07 | active |
| 腾讯云 | Token Plan Max | Token Plan | ¥599 | 650M | 1.09 | active |
| 阿里·百炼 | Pro | Coding Plan | ¥200 | 3000M | 15.00 | active |
---

## 三、更新规则

1. **新增厂商** → 编辑 `project/codingplan-saver/data/vendors.json` → 运行 `kb_to_md.py` 重新生成
2. **URL 变更** → 编辑 `vendors.json` 的 `urls` 字段 → 运行 `kb_to_md.py`
3. **价格变动** → 自动采集管道检测 → `/codingplan-page update` 审阅 → 更新 `plans.json`
4. **推广链接** → 编辑 `vendors.json` 的 `urls.affiliate` → 重新构建 HTML

> 唯一真相源：`project/codingplan-saver/data/*.json`（详见 `SCHEMA.md`）