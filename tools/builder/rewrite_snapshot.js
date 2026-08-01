/**
 * 基于 8-01 官网快照全量重写 vendors.json + plans.json
 *
 * 数据源：reference/pricing-snapshots/20260801/（7 家厂商官网快照）
 * 原则：每条数据可追溯到某个快照文件，source=manual-snapshot-20260801
 *
 * 两套评测体系：
 *   - 月订阅套餐（Coding Plan / Token Plan / Agent Plan / 会员）
 *   - API 按量（无月费，按 token 消耗）
 *
 * 用法:
 *   node tools/builder/rewrite_snapshot.js          # 生成并写出
 *   node tools/builder/rewrite_snapshot.js --dry    # 只打印不写
 */

const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..", "..");
const PROJ = path.join(ROOT, "project/codingplan-saver/data");
const DRY = process.argv.includes("--dry");

const SOURCE = "manual-snapshot-20260801";
const UPDATED = "2026-08-01";

// ───────── 厂商定义（7 家）─────────
const VENDORS = [
  {
    id: "zhipu", name: "智谱AI", logo: "智", color: "#F5F527", category: "model-maker",
    urls: { pricing: "https://bigmodel.cn/glm-coding", home: "https://open.bigmodel.cn" },
    extractStrategy: "manual", lastVerified: "2026-08-01",
    notes: "7-30 套餐改版，积分制，旧版¥49/149/469已停",
  },
  {
    id: "bytedance", name: "字节·方舟", logo: "字", color: "#FF3B3B", category: "model-maker",
    urls: { pricing: "https://console.volcengine.com/ark/region:cn-beijing/subscription/coding-plan", home: "https://www.volcengine.com/ark" },
    extractStrategy: "manual", lastVerified: "2026-08-01",
    notes: "反爬+SPA，依赖人工快照",
  },
  {
    id: "tencent", name: "腾讯云", logo: "腾", color: "#eab308", category: "cloud-maas",
    urls: { pricing: "https://cloud.tencent.com/product/tokenhub", home: "https://cloud.tencent.com/product/tokenhub" },
    extractStrategy: "manual", lastVerified: "2026-08-01",
    notes: "Coding Plan已售罄，主推Token Plan 4档",
  },
  {
    id: "deepseek", name: "DeepSeek 官方", logo: "D", color: "#71717B", category: "model-maker",
    urls: { pricing: "https://api-docs.deepseek.com/zh-cn/quick_start/pricing", home: "https://api-docs.deepseek.com" },
    extractStrategy: "manual", lastVerified: "2026-08-01",
    notes: "纯API按量，无月订阅套餐，即将峰谷定价",
  },
  {
    id: "minimax", name: "MiniMax", logo: "M", color: "#f97316", category: "model-maker",
    urls: { pricing: "https://platform.minimaxi.com/subscribe/token-plan", home: "https://platform.minimaxi.com" },
    extractStrategy: "manual", lastVerified: "2026-08-01",
    notes: "Token Plan用量翻倍，多模态全共享额度",
  },
  {
    id: "kimi", name: "Kimi", logo: "K", color: "#10C2B0", category: "model-maker",
    urls: { pricing: "https://www.kimi.com/membership/pricing", home: "https://www.kimi.com" },
    extractStrategy: "manual", lastVerified: "2026-08-01",
    notes: "新会员体系即将上线，Kimi权益与Kimi Code将拆分",
  },
  {
    id: "bailian", name: "阿里·百炼", logo: "阿", color: "#22c55e", category: "cloud-maas",
    urls: { pricing: "https://www.aliyun.com/benefit/scene/codingplan", home: "https://bailian.aliyun.com" },
    extractStrategy: "manual", lastVerified: "2026-08-01",
    notes: "Lite已停售(3-20)，只剩Pro，限量抢购",
  },
];

// ───────── plans 数据（基于快照）─────────
// 字段：id/vendor/vendorId/plan/type/tier/monthlyPrice/currency/firstMonthPrice/
//       rating/models/monthlyRequests/tokenLimit/measuredMonthlyToken/tags/
//       bloggerVerdict/action/status/source/updatedAt/category/billingCore/migration/notes

const PLANS = [
  // ========== 智谱（月订阅 + API按量）==========
  // 月订阅：Coding Plan 积分制（7-30改版）
  {
    id: "zhipu-lite", vendor: "智谱AI", vendorId: "zhipu", plan: "Lite", type: "Coding Plan", tier: "lite",
    monthlyPrice: 118, currency: "¥", firstMonthPrice: null, rating: 4,
    models: ["GLM-5.2", "GLM-5-Turbo", "GLM-4.7"],
    monthlyRequests: null, tokenLimit: "每周10,000积分（5小时2,000）",
    measuredMonthlyToken: 87, // 官网参考：Lite 0.43~0.87亿/周，取上限折月
    tags: ["模型强", "需抢购", "非高峰5折"],
    bloggerVerdict: "7-30改版后入门档，积分制。GLM-5.2 代码能力 T0，非高峰5折划算。",
    action: "https://bigmodel.cn/glm-coding", status: "active", source: SOURCE, updatedAt: UPDATED,
    category: "model-maker", billingCore: "credit", migration: "7-30改版积分制，旧版¥49已停，涨价140%",
    notes: "measuredMonthlyToken 按官网'0.43~0.87亿Tokens/周'折算（取上限×4周）",
  },
  {
    id: "zhipu-pro", vendor: "智谱AI", vendorId: "zhipu", plan: "Pro", type: "Coding Plan", tier: "pro",
    monthlyPrice: 538, currency: "¥", firstMonthPrice: null, rating: 5,
    models: ["GLM-5.2", "GLM-5-Turbo", "GLM-4.7"],
    monthlyRequests: null, tokenLimit: "每周60,000积分（5小时12,000）",
    measuredMonthlyToken: 522, // 6倍Lite
    tags: ["模型强", "需抢购", "非高峰5折"],
    bloggerVerdict: "6倍Lite用量，主力档。改版后价格翻3.6倍，但GLM-5.2+非高峰5折仍有竞争力。",
    action: "https://bigmodel.cn/glm-coding", status: "active", source: SOURCE, updatedAt: UPDATED,
    category: "model-maker", billingCore: "credit", migration: "7-30改版积分制，旧版¥149已停",
    notes: "measuredMonthlyToken = Lite × 6",
  },
  {
    id: "zhipu-max", vendor: "智谱AI", vendorId: "zhipu", plan: "Max", type: "Coding Plan", tier: "max",
    monthlyPrice: 1078, currency: "¥", firstMonthPrice: null, rating: 5,
    models: ["GLM-5.2", "GLM-5-Turbo", "GLM-4.7"],
    monthlyRequests: null, tokenLimit: "每周140,000积分（5小时28,000）",
    measuredMonthlyToken: 1218, // 14倍Lite
    tags: ["模型强", "需抢购", "非高峰5折", "高峰专属资源"],
    bloggerVerdict: "14倍Lite，旗舰档。高峰期专属资源保障，重度agentic首选。",
    action: "https://bigmodel.cn/glm-coding", status: "active", source: SOURCE, updatedAt: UPDATED,
    category: "model-maker", billingCore: "credit", migration: "7-30改版积分制，旧版¥469已停，涨价130%",
    notes: "measuredMonthlyToken = Lite × 14",
  },
  // 智谱 API 按量
  {
    id: "zhipu-api-glm52", vendor: "智谱AI", vendorId: "zhipu", plan: "GLM-5.2 按量", type: "API 按量", tier: "pro",
    monthlyPrice: null, currency: "¥", firstMonthPrice: null, rating: 5,
    models: ["GLM-5.2"], monthlyRequests: null, tokenLimit: "按量",
    measuredMonthlyToken: null,
    tags: ["模型强", "1M上下文"],
    bloggerVerdict: "GLM-5.2 按量，输入8元/输出28元每百万token。1M上下文，缓存命中2元。",
    action: "https://bigmodel.cn/pricing", status: "active", source: SOURCE, updatedAt: UPDATED,
    category: "model-maker", billingCore: "token", migration: "",
    notes: "输入8/输出28/缓存命中2 元/百万token",
  },
  {
    id: "zhipu-api-glm-turbo", vendor: "智谱AI", vendorId: "zhipu", plan: "GLM-5-Turbo 按量", type: "API 按量", tier: "lite",
    monthlyPrice: null, currency: "¥", firstMonthPrice: null, rating: 4,
    models: ["GLM-5-Turbo"], monthlyRequests: null, tokenLimit: "按量",
    measuredMonthlyToken: null,
    tags: ["高性价比"],
    bloggerVerdict: "GLM-5-Turbo 按量，输入5/输出22元。比5.2便宜，日常够用。",
    action: "https://bigmodel.cn/pricing", status: "active", source: SOURCE, updatedAt: UPDATED,
    category: "model-maker", billingCore: "token", migration: "",
    notes: "输入5/输出22/缓存命中1.2 元/百万token",
  },

  // ========== 字节·方舟（月订阅 Coding+Agent + API按量）==========
  // Coding Plan 单档
  {
    id: "bytedance-coding-auto", vendor: "字节·方舟", vendorId: "bytedance", plan: "Auto", type: "Coding Plan", tier: "lite",
    monthlyPrice: 9.9, currency: "¥", firstMonthPrice: null, rating: 5,
    models: ["Doubao-Seed-2.0-Code", "Doubao-Seed-2.0-Pro", "Doubao-Seed-2.0-Lite", "GLM-5.2", "Kimi-K2.7-Code", "DeepSeek-V4-Pro", "DeepSeek-V4-Flash", "MiniMax-M3", "Doubao-Seed-Code", "MiniMax-M2.7", "Kimi-K2.6", "DeepSeek-V3.2", "Doubao-Seed-2.1-turbo"],
    monthlyRequests: null, tokenLimit: "Auto智能调度",
    measuredMonthlyToken: 250, // 估算：¥9.9 全家桶，按历史6.25 M/元
    tags: ["模型强", "性价比高", "全家桶", "无需抢购"],
    bloggerVerdict: "¥9.9全家桶，13+模型Auto调度。唯一同时支持GLM/DeepSeek/MiniMax/Kimi的平台。",
    action: "https://console.volcengine.com/ark/region:cn-beijing/subscription/coding-plan", status: "active", source: SOURCE, updatedAt: UPDATED,
    category: "model-maker", billingCore: "token", migration: "改版单档制，旧Lite¥40/Pro¥200已停",
    notes: "measuredMonthlyToken 为估算（¥9.9×25 M/元，全家桶历史比），待实测",
  },
  // Agent Plan 两档
  {
    id: "bytedance-agent-lite", vendor: "字节·方舟", vendorId: "bytedance", plan: "Agent Lite", type: "Agent Plan", tier: "lite",
    monthlyPrice: 9.9, currency: "¥", firstMonthPrice: null, rating: 4,
    models: ["Doubao-Seed-2.0-Code", "Doubao-Seed-2.0-Pro", "Doubao-Seed-2.0-Lite", "Doubao-Seed-2.0-Mini"],
    monthlyRequests: null, tokenLimit: "每月20,000 Agent燃料值",
    measuredMonthlyToken: null,
    tags: ["多模态", "Agent", "性价比高"],
    bloggerVerdict: "Agent入门档，20K燃料值，语言/图像/向量化多模态。",
    action: "https://console.volcengine.com/ark/region:cn-beijing/subscription/agent-plan", status: "active", source: SOURCE, updatedAt: UPDATED,
    category: "model-maker", billingCore: "credit", migration: "",
    notes: "燃料值制，非直接Token计量",
  },
  {
    id: "bytedance-agent-large", vendor: "字节·方舟", vendorId: "bytedance", plan: "Agent Large", type: "Agent Plan", tier: "max",
    monthlyPrice: 1000, currency: "¥", firstMonthPrice: null, rating: 4,
    models: ["Doubao-Seed-2.0-Code", "Doubao-Seed-2.0-Pro", "Doubao-Seed-2.0-Lite", "Doubao-Seed-2.0-Mini"],
    monthlyRequests: null, tokenLimit: "每月500,000 Agent燃料值（25x）",
    measuredMonthlyToken: null,
    tags: ["多模态", "Agent", "重度"],
    bloggerVerdict: "Agent旗舰档，500K燃料值，极致多模态Harness体验。",
    action: "https://console.volcengine.com/ark/region:cn-beijing/subscription/agent-plan", status: "active", source: SOURCE, updatedAt: UPDATED,
    category: "model-maker", billingCore: "credit", migration: "",
    notes: "燃料值制，25x Lite",
  },

  // ========== 腾讯云（Token Plan 4档 + API按量；Coding Plan已售罄）==========
  // Token Plan 通用版 4档
  {
    id: "tencent-tp-lite", vendor: "腾讯云", vendorId: "tencent", plan: "Token Plan Lite", type: "Token Plan", tier: "lite",
    monthlyPrice: 39, currency: "¥", firstMonthPrice: null, rating: 4,
    models: ["DeepSeek-V4-Flash", "DeepSeek-V4-Pro", "MiniMax-M2.7", "GLM-5", "GLM-5.1", "Kimi-K2.5"],
    monthlyRequests: null, tokenLimit: "3500万 Tokens/月",
    measuredMonthlyToken: 35,
    tags: ["性价比高", "多模型", "DeepSeek原厂"],
    bloggerVerdict: "入门Token池，3500万Token，含DeepSeek原厂直供。",
    action: "https://cloud.tencent.com/product/tokenhub", status: "active", source: SOURCE, updatedAt: UPDATED,
    category: "cloud-maas", billingCore: "token", migration: "Coding Plan已售罄，主推Token Plan",
    notes: "MiniMax-M2.5将于8-6下线，Kimi-K2.5将于7-31下线",
  },
  {
    id: "tencent-tp-standard", vendor: "腾讯云", vendorId: "tencent", plan: "Token Plan Standard", type: "Token Plan", tier: "pro",
    monthlyPrice: 99, currency: "¥", firstMonthPrice: null, rating: 5,
    models: ["DeepSeek-V4-Flash", "DeepSeek-V4-Pro", "MiniMax-M2.7", "GLM-5", "GLM-5.1", "Kimi-K2.5"],
    monthlyRequests: null, tokenLimit: "1亿 Tokens/月",
    measuredMonthlyToken: 100,
    tags: ["性价比高", "多模型", "DeepSeek原厂"],
    bloggerVerdict: "日常高性价比档，1亿Token，约200轮问答。",
    action: "https://cloud.tencent.com/product/tokenhub", status: "active", source: SOURCE, updatedAt: UPDATED,
    category: "cloud-maas", billingCore: "token", migration: "",
    notes: "",
  },
  {
    id: "tencent-tp-pro", vendor: "腾讯云", vendorId: "tencent", plan: "Token Plan Pro", type: "Token Plan", tier: "pro",
    monthlyPrice: 299, currency: "¥", firstMonthPrice: null, rating: 5,
    models: ["DeepSeek-V4-Flash", "DeepSeek-V4-Pro", "MiniMax-M2.7", "GLM-5", "GLM-5.1", "Kimi-K2.5"],
    monthlyRequests: null, tokenLimit: "3.2亿 Tokens/月",
    measuredMonthlyToken: 320,
    tags: ["模型强", "多模型", "高频开发"],
    bloggerVerdict: "高频AI开发档，3.2亿Token，比基础版3倍额度。",
    action: "https://cloud.tencent.com/product/tokenhub", status: "active", source: SOURCE, updatedAt: UPDATED,
    category: "cloud-maas", billingCore: "token", migration: "",
    notes: "",
  },
  {
    id: "tencent-tp-max", vendor: "腾讯云", vendorId: "tencent", plan: "Token Plan Max", type: "Token Plan", tier: "max",
    monthlyPrice: 599, currency: "¥", firstMonthPrice: null, rating: 5,
    models: ["DeepSeek-V4-Flash", "DeepSeek-V4-Pro", "MiniMax-M2.7", "GLM-5", "GLM-5.1", "Kimi-K2.5"],
    monthlyRequests: null, tokenLimit: "6.5亿 Tokens/月",
    measuredMonthlyToken: 650,
    tags: ["模型强", "多模型", "重度"],
    bloggerVerdict: "重度用户旗舰档，6.5亿Token，全栈AI生成+多Agent协同。",
    action: "https://cloud.tencent.com/product/tokenhub", status: "active", source: SOURCE, updatedAt: UPDATED,
    category: "cloud-maas", billingCore: "token", migration: "",
    notes: "",
  },
  // 腾讯 Coding Plan（已售罄，保留记录）
  {
    id: "tencent-cp-pro", vendor: "腾讯云", vendorId: "tencent", plan: "Coding Plan Pro", type: "Coding Plan", tier: "pro",
    monthlyPrice: 200, currency: "¥", firstMonthPrice: null, rating: 3,
    models: ["GLM-5.1", "Kimi-K2.5", "MiniMax-M2.7"],
    monthlyRequests: 90000, tokenLimit: "100M Tokens",
    measuredMonthlyToken: 600,
    tags: ["已售罄", "兼容Claude Code"],
    bloggerVerdict: "⚠️ 已售罄。原TokenHub Coding Plan，比API按量便宜50-80%。",
    action: "https://cloud.tencent.com/product/tokenhub", status: "sold_out", source: SOURCE, updatedAt: UPDATED,
    category: "cloud-maas", billingCore: "token", migration: "Coding Plan已售罄，迁移至Token Plan",
    notes: "售罄状态，保留供参考",
  },

  // ========== DeepSeek（纯API按量，无套餐）==========
  {
    id: "deepseek-api-flash", vendor: "DeepSeek 官方", vendorId: "deepseek", plan: "V4-Flash 按量", type: "API 按量", tier: "lite",
    monthlyPrice: null, currency: "¥", firstMonthPrice: null, rating: 5,
    models: ["DeepSeek-V4-Flash", "DeepSeek-V4-Flash-0731"], monthlyRequests: null, tokenLimit: "按量",
    measuredMonthlyToken: null,
    tags: ["性价比高", "1M上下文", "极速"],
    bloggerVerdict: "V4-Flash按量，输入1/输出2元每百万token。极速推理，1M上下文，性价比之王。",
    action: "https://api-docs.deepseek.com/zh-cn/quick_start/pricing", status: "active", source: SOURCE, updatedAt: UPDATED,
    category: "model-maker", billingCore: "token", migration: "即将峰谷定价（高峰2倍）",
    notes: "缓存命中0.02/未命中1元输入；即将峰谷定价",
  },
  {
    id: "deepseek-api-pro", vendor: "DeepSeek 官方", vendorId: "deepseek", plan: "V4-Pro 按量", type: "API 按量", tier: "pro",
    monthlyPrice: null, currency: "¥", firstMonthPrice: null, rating: 5,
    models: ["DeepSeek-V4-Pro"], monthlyRequests: null, tokenLimit: "按量",
    measuredMonthlyToken: null,
    tags: ["模型强", "1M上下文", "思考模式"],
    bloggerVerdict: "V4-Pro按量，输入3/输出6元。Agent能力显著增强，默认深度思考。",
    action: "https://api-docs.deepseek.com/zh-cn/quick_start/pricing", status: "active", source: SOURCE, updatedAt: UPDATED,
    category: "model-maker", billingCore: "token", migration: "即将峰谷定价（高峰2倍）",
    notes: "缓存命中0.025/未命中3元输入",
  },

  // ========== MiniMax（Token Plan 3档 + API按量）==========
  {
    id: "minimax-plus", vendor: "MiniMax", vendorId: "minimax", plan: "Plus", type: "Token Plan", tier: "lite",
    monthlyPrice: 49, currency: "¥", firstMonthPrice: null, rating: 5,
    models: ["MiniMax-M3", "MiniMax-M2.7", "MiniMax-M2.5"],
    monthlyRequests: null, tokenLimit: "约12,000次/月（M3）",
    measuredMonthlyToken: 600,
    tags: ["模型强", "性价比高", "多模态", "无需抢购"],
    bloggerVerdict: "入门档，用量翻倍后性价比最高。M3+多模态，养龙虾首选。",
    action: "https://platform.minimaxi.com/subscribe/token-plan", status: "active", source: SOURCE, updatedAt: UPDATED,
    category: "model-maker", billingCore: "token", migration: "Frontier模型，用量翻倍升级",
    notes: "按M3单次~50K token估算12,000次/月",
  },
  {
    id: "minimax-max", vendor: "MiniMax", vendorId: "minimax", plan: "Max", type: "Token Plan", tier: "pro",
    monthlyPrice: 119, currency: "¥", firstMonthPrice: null, rating: 5,
    models: ["MiniMax-M3", "MiniMax-M2.7", "MiniMax-M2.5"],
    monthlyRequests: null, tokenLimit: "约36,000次/月（M3）",
    measuredMonthlyToken: 1800,
    tags: ["模型强", "性价比高", "多模态", "无需抢购"],
    bloggerVerdict: "中档主力，3倍Plus用量。最划算的选择。",
    action: "https://platform.minimaxi.com/subscribe/token-plan", status: "active", source: SOURCE, updatedAt: UPDATED,
    category: "model-maker", billingCore: "token", migration: "",
    notes: "",
  },
  {
    id: "minimax-ultra", vendor: "MiniMax", vendorId: "minimax", plan: "Ultra", type: "Token Plan", tier: "max",
    monthlyPrice: 469, currency: "¥", firstMonthPrice: null, rating: 5,
    models: ["MiniMax-M3", "MiniMax-M2.7", "MiniMax-M2.5"],
    monthlyRequests: null, tokenLimit: "约140,000次/月（M3）",
    measuredMonthlyToken: 7100,
    tags: ["模型强", "多模态", "重度", "无需抢购"],
    bloggerVerdict: "重度旗舰档，140K次/月。多模态全共享，团队/多项目并行首选。",
    action: "https://platform.minimaxi.com/subscribe/token-plan", status: "active", source: SOURCE, updatedAt: UPDATED,
    category: "model-maker", billingCore: "token", migration: "",
    notes: "",
  },

  // ========== Kimi（会员 + API按量；新体系即将上线）==========
  {
    id: "kimi-daily", vendor: "Kimi", vendorId: "kimi", plan: "日常使用", type: "会员", tier: "lite",
    monthlyPrice: 39, currency: "¥", firstMonthPrice: null, rating: 4,
    models: ["Kimi-K3", "Kimi-K2.7-Code"],
    monthlyRequests: null, tokenLimit: "Agent额度",
    measuredMonthlyToken: null,
    tags: ["深度研究", "Office", "网站部署"],
    bloggerVerdict: "新会员体系日常档，含Agent额度+Office+深度研究。Kimi Code将拆分独立。",
    action: "https://www.kimi.com/membership/pricing", status: "active", source: SOURCE, updatedAt: UPDATED,
    category: "model-maker", billingCore: "credit", migration: "新体系即将上线，Kimi权益与Code拆分",
    notes: "旧Andante¥49/Allegretto¥199待新体系上线后确认",
  },

  // ========== 阿里·百炼（Coding Plan Pro + API按量；Lite已停售）==========
  {
    id: "bailian-pro", vendor: "阿里·百炼", vendorId: "bailian", plan: "Pro", type: "Coding Plan", tier: "pro",
    monthlyPrice: 200, currency: "¥", firstMonthPrice: null, rating: 5,
    models: ["qwen3.7-plus", "qwen3.6-plus", "kimi-k2.5", "glm-5", "MiniMax-M2.5", "qwen3-coder-next", "glm-4.7"],
    monthlyRequests: 90000, tokenLimit: "5h 6,000次/周45,000次/月90,000次",
    measuredMonthlyToken: 3000, // 按次计费，参考旧估算
    tags: ["模型强", "需抢购", "全家桶", "按次计费"],
    bloggerVerdict: "全家桶Coding Plan，¥200含qwen3.7/kimi-k2.5/glm-5/MiniMax-M2.5。限量抢购，每日9:30补货。",
    action: "https://www.aliyun.com/benefit/scene/codingplan", status: "active", source: SOURCE, updatedAt: UPDATED,
    category: "cloud-maas", billingCore: "request", migration: "Lite已停售(3-20)，只剩Pro",
    notes: "按次计费（非Token），简单任务5-10次/复杂10-30+次",
  },
];

// ───────── 校验 + 写出 ─────────

function build() {
  // 校验
  const vIds = new Set(VENDORS.map(v => v.id));
  const dangling = PLANS.filter(p => !vIds.has(p.vendorId));
  if (dangling.length) throw new Error(`plans 引用未定义 vendor: ${dangling.map(p => p.vendorId)}`);

  const planIds = PLANS.map(p => p.id);
  const dup = planIds.filter((id, i) => planIds.indexOf(id) !== i);
  if (dup.length) throw new Error(`plan id 重复: ${dup}`);

  // 必填字段检查
  const REQUIRED = ["id","vendor","vendorId","plan","type","tier","monthlyPrice","currency","firstMonthPrice","rating","models","monthlyRequests","tokenLimit","measuredMonthlyToken","tags","bloggerVerdict","action","status","source","updatedAt","category","billingCore","migration"];
  const missing = PLANS.filter(p => REQUIRED.some(f => !(f in p)));
  if (missing.length) throw new Error(`缺失字段: ${missing.map(p => p.id)}`);

  const summary = {
    vendors: VENDORS.length,
    plans: PLANS.length,
    monthly: PLANS.filter(p => p.monthlyPrice !== null).length,
    api: PLANS.filter(p => p.monthlyPrice === null).length,
    byType: {},
  };
  PLANS.forEach(p => { summary.byType[p.type] = (summary.byType[p.type] || 0) + 1; });

  if (DRY) {
    console.log("=== DRY RUN ===");
    console.log("规模:", summary);
    console.log("\nplans 清单:");
    PLANS.forEach(p => console.log(`  ${p.id.padEnd(28)} ${p.type.padEnd(12)} ¥${String(p.monthlyPrice).padEnd(6)} ${p.vendor}`));
    return;
  }

  // 写出
  fs.writeFileSync(path.join(PROJ, "vendors.json"), JSON.stringify(VENDORS, null, 2) + "\n", "utf8");
  fs.writeFileSync(path.join(PROJ, "plans.json"), JSON.stringify(PLANS, null, 2) + "\n", "utf8");

  console.log("✅ 重写完成");
  console.log("规模:", summary);
  console.log("\nplans 清单:");
  PLANS.forEach(p => console.log(`  ${p.id.padEnd(28)} ${p.type.padEnd(12)} ¥${String(p.monthlyPrice).padEnd(6)} ${p.vendor}`));
}

build();
