/**
 * 回填第一批厂商：从线上抢救数据 → project/codingplan-saver/data
 *
 * 数据流（已核实）：
 *   真相源 = project/codingplan-saver/data/*.json（builder 只读它）
 *   aikb/database/*.json = 下游产物（由 kb_migrate.py 从 project 同步）
 *
 * 所以回填主改 project 侧，再跑 kb_migrate.py 同步 aikb。
 *
 * 用法:
 *   node tools/builder/backfill_batch1.js          # 生成并写出（覆盖 project 3 个文件）
 *   node tools/builder/backfill_batch1.js --dry     # 只打印，不写文件
 *
 * 本脚本是审计记录：可重跑复现，估算规则和字段映射全部在此文件里。
 */

const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..", "..");
const RECOVERY = path.join(ROOT, "data/recovery/codingplan-fyi-2026-07-31/plans.json");
const PROJ = path.join(ROOT, "project/codingplan-saver/data");

const DRY = process.argv.includes("--dry");

// ───────── 第一批入网厂商配置 ─────────
// vendorId 优先用 SCHEMA.md 的 VENDOR_ID_MAP，缺失的补。
// 商汤·日日新（仅 Free·公测月费 0）、摩尔线程（4 条全无价）= 占位，跳过，第二批再补。
const VENDOR_CFG = {
  联通云: { id: "unicom", logo: "联", color: "#ca0a14", category: "cloud-maas", migration: "" },
  华为云: { id: "huawei", logo: "华", color: "#ff0000", category: "cloud-maas", migration: "" },
  "讯飞·星火": { id: "xunfei", logo: "讯", color: "#0a7efa", category: "cloud-maas", migration: "" },
  天翼云: { id: "ctyun", logo: "天", color: "#1a73e8", category: "cloud-maas", migration: "" },
  阶跃星辰: { id: "stepfun", logo: "阶", color: "#7c3aed", category: "model-maker", migration: "" },
  智谱国际版: { id: "zhipu-intl", logo: "智", color: "#facc15", category: "model-maker", migration: "海外版，独立计费" },
  京东云: { id: "jd", logo: "京", color: "#c7162d", category: "cloud-maas", migration: "" },
  移动云: { id: "cmcc", logo: "移", color: "#005bac", category: "cloud-maas", migration: "" },
  无问芯穹: { id: "infini", logo: "芯", color: "#06b6d4", category: "aggregator", migration: "" },
  TaoToken: { id: "taotoken", logo: "TT", color: "#10b981", category: "aggregator", migration: "" },
  Ollama: { id: "ollama", logo: "Ol", color: "#22c55e", category: "vertical-cloud", migration: "本地部署代理" },
  OpenCode: { id: "opencode", logo: "OC", color: "#f97316", category: "vertical-cloud", migration: "" },
  超算: { id: "scnet", logo: "算", color: "#64748b", category: "cloud-maas", migration: "" },
  优云智算: { id: "uyun", logo: "优", color: "#0ea5e9", category: "cloud-maas", migration: "" },
};

// ───────── 转换规则 ─────────

/** tier 推断：Max/Ultra/速通→max，Mini/Lite/Free→lite，其余→pro */
function inferTier(planName) {
  if (/max|ultra|allegro|flash max|glm max|团队 max|个人 max|速通/i.test(planName)) return "max";
  if (/mini|lite|andante|free|flash mini|个人 lite|团队 lite|glm lite|虚拟套餐 40/i.test(planName)) return "lite";
  return "pro";
}

/** plan id slug：小写 + 空格转连字符，中文保留（对齐现有 github-学生 等命名） */
function planSlug(planName) {
  return planName
    .toLowerCase()
    .replace(/\s+/g, "-")
    .replace(/\*/g, "")
    .replace(/·/g, "-");
}

/**
 * measuredMonthlyToken 估算（单位 M）。
 * 优先级：
 *   1. recovery 有 measuredMonthlyTokenLimit 数值 → 直接用（华为云、有原值的）
 *   2. Token Plan 且 tokenLimit 是数值 → 原值即 M（联通云个人/团队 6/12/18/200/800/2000）
 *   3. 按 category×vendor 经验比估算（来自现有 28 条反推，见下表）
 *
 * 估算基准（M Token/元，现有数据反推）：
 *   cloud-maas|Coding Plan 中位 3.0（腾讯云/小米档）
 *   model-maker|Coding Plan 中位 5.0（智谱/字节档）
 *   弱模型(rating≤2) 打折 1.5（超算）
 *   cloud Token Plan 中位 15（OpenCode tokenLimit 未公开时）
 */
function estimateMeasured(p, vendorId) {
  if (typeof p.measuredMonthlyTokenLimit === "number") {
    return { val: p.measuredMonthlyTokenLimit, est: false, note: "" };
  }
  if (p.type === "Token Plan" && typeof p.tokenLimit === "number") {
    return { val: p.tokenLimit, est: false, note: "按 tokenLimit 原值(M)" };
  }
  const price = p.monthlyPrice;
  const ratio = {
    unicom: 3.0, ctyun: 3.0, jd: 3.0, cmcc: 3.0, infini: 3.0, xunfei: 3.0,
    stepfun: 5.0, "zhipu-intl": 5.0, taotoken: 3.0, scnet: 1.5, ollama: 3.0, uyun: 3.0,
    opencode: 15,
  }[vendorId];
  const desc = {
    unicom: "运营商 cloud-maas 3.0", ctyun: "运营商 cloud-maas 3.0", jd: "运营商 cloud-maas 3.0",
    cmcc: "运营商 cloud-maas 3.0", infini: "聚合商 3.0", xunfei: "cloud-maas 3.0",
    stepfun: "model-maker 5.0", "zhipu-intl": "model-maker 5.0", taotoken: "cloud-maas 3.0",
    scnet: "弱模型 1.5", ollama: "cloud 3.0", uyun: "cloud-maas 3.0", opencode: "cloud Token 15",
  }[vendorId];
  if (ratio && typeof price === "number" && price > 0) {
    return { val: Math.round(price * ratio), est: true, note: `估算(${desc} M/元)` };
  }
  return { val: null, est: true, note: "估算失败" };
}

/** bloggerVerdict：用 recovery note 第一行事实信息，无则通用描述 */
function makeVerdict(p) {
  if (p.note && typeof p.note === "string") {
    const firstLine = p.note.split("\n")[0].replace(/^[•·\-\s]+/, "").trim();
    if (firstLine) return firstLine;
  }
  return `${p.vendor} ${p.plan} 档套餐。`;
}

// ───────── 主流程 ─────────

function build() {
  const recovery = JSON.parse(fs.readFileSync(RECOVERY, "utf8"));
  const projVendors = JSON.parse(fs.readFileSync(path.join(PROJ, "vendors.json"), "utf8"));
  const projPlans = JSON.parse(fs.readFileSync(path.join(PROJ, "plans.json"), "utf8"));
  const projChanges = JSON.parse(fs.readFileSync(path.join(PROJ, "changes.json"), "utf8"));

  // 1. 新 vendors
  const vendorUrl = {};
  recovery.forEach((p) => {
    if (VENDOR_CFG[p.vendor] && !vendorUrl[p.vendor]) vendorUrl[p.vendor] = p.action;
  });
  const newVendors = Object.entries(VENDOR_CFG).map(([name, cfg]) => ({
    id: cfg.id,
    name,
    logo: cfg.logo,
    color: cfg.color,
    category: cfg.category,
    urls: { pricing: vendorUrl[name] || "", home: vendorUrl[name] || "" },
    extractStrategy: "manual",
    lastVerified: "2026-07-31",
    notes: "回填自线上 codingplan.fyi 抢救数据（2026-07-31）",
  }));

  // 2. 新 plans
  const newPlans = [];
  const estReport = [];
  recovery
    .filter((p) => VENDOR_CFG[p.vendor])
    .forEach((p) => {
      const cfg = VENDOR_CFG[p.vendor];
      const { val: measured, est, note: estNote } = estimateMeasured(p, cfg.id);
      const id = `${cfg.id}-${planSlug(p.plan)}`;
      let tokenLimitField = p.tokenLimit;
      if (typeof p.tokenLimit === "number") tokenLimitField = `${p.tokenLimit}M Tokens`;
      if (p.tokenLimit === "未公开" || p.tokenLimit === "-") tokenLimitField = "未公开";
      if (p.type === "Coding Plan" && (p.tokenLimit === "无限制" || p.tokenLimit === "-" || p.tokenLimit === "未公开")) {
        tokenLimitField = "无限制";
      }
      const newPlan = {
        id,
        vendor: p.vendor,
        vendorId: cfg.id,
        plan: p.plan,
        type: p.type,
        tier: inferTier(p.plan),
        monthlyPrice: typeof p.monthlyPrice === "number" ? p.monthlyPrice : null,
        currency: "¥",
        firstMonthPrice: typeof p.firstMonthPrice === "number" ? p.firstMonthPrice : null,
        rating: p.rating ?? 3,
        models: p.models || [],
        monthlyRequests: p.type === "Coding Plan" ? p.monthlyRequests : null,
        tokenLimit: tokenLimitField,
        measuredMonthlyToken: measured,
        tags: p.tags || [],
        bloggerVerdict: makeVerdict(p),
        action: p.action || "",
        status: "active",
        source: "manual",
        updatedAt: "2026-07-31",
        category: cfg.category,
        billingCore: "token",
        migration: cfg.migration,
      };
      if (est) newPlan.notes = `measuredMonthlyToken 为${estNote}，待实测`;
      newPlans.push(newPlan);
      estReport.push({ id, vendor: p.vendor, plan: p.plan, price: p.monthlyPrice, measured, est, note: estNote });
    });

  // 3. 新 changes（每家一条 new_plan，仿 TaoToken 模板）
  const newChanges = Object.entries(VENDOR_CFG).map(([name, cfg]) => {
    const cnt = recovery.filter((p) => p.vendor === name).length;
    const planNames = [...new Set(recovery.filter((p) => p.vendor === name).map((p) => p.plan))];
    const planIds = newPlans.filter((p) => p.vendor === name).map((p) => p.id);
    return {
      id: `2026-07-31-${cfg.id}-new_plan`,
      date: "2026-07-31",
      kind: "new_plan",
      vendor: name,
      title: `${name} 新增平台`,
      detail: `${cnt} 档套餐上线：${planNames.join(" / ")}`,
      impact: "positive",
      level: "medium",
      source: "manual",
      sourceUrl: null,
      relatedPlans: planIds,
      featured: false,
      excerpt: null,
      author: null,
      readTime: null,
      cover: null,
    };
  });

  // 合并（幂等：跳过已存在的 id/name，支持安全重跑）
  const existVendorId = new Set(projVendors.map((v) => v.id));
  const existPlanId = new Set(projPlans.map((p) => p.id));
  const existChangeId = new Set(projChanges.map((c) => c.id));
  const addVendors = newVendors.filter((v) => !existVendorId.has(v.id));
  const addPlans = newPlans.filter((p) => !existPlanId.has(p.id));
  const addChanges = newChanges.filter((c) => !existChangeId.has(c.id));
  const mergedVendors = [...projVendors, ...addVendors];
  const mergedPlans = [...projPlans, ...addPlans];
  const mergedChanges = [...addChanges, ...projChanges];

  // 校验
  const vNames = new Set(mergedVendors.map((v) => v.name));
  const dangling = [...new Set(mergedPlans.map((p) => p.vendor))].filter((v) => !vNames.has(v));
  const planDup = mergedPlans.map((p) => p.id).filter((id, i, arr) => arr.indexOf(id) !== i);
  const changeDup = mergedChanges.map((c) => c.id).filter((id, i, arr) => arr.indexOf(id) !== i);
  if (dangling.length) throw new Error(`plans 引用未定义 vendor: ${dangling}`);
  if (planDup.length) throw new Error(`plan id 重复: ${planDup}`);
  if (changeDup.length) throw new Error(`change id 重复: ${changeDup}`);

  const summary = {
    vendors: `${projVendors.length} → ${mergedVendors.length} (+${addVendors.length})`,
    plans: `${projPlans.length} → ${mergedPlans.length} (+${addPlans.length})`,
    changes: `${projChanges.length} → ${mergedChanges.length} (+${addChanges.length})`,
    measured原值: estReport.filter((r) => !r.est).length,
    measured估算: estReport.filter((r) => r.est).length,
  };

  if (DRY) {
    console.log("=== DRY RUN ===");
    console.log("规模:", summary);
    console.log("\n估算明细:");
    estReport.forEach((r) =>
      console.log(`  ${r.id.padEnd(28)} ¥${String(r.price).padEnd(6)} ${String(r.measured).padEnd(6)} ${r.est ? "⚠️估算" : "✅原值"} ${r.note}`)
    );
    return;
  }

  // 写出
  const opts = { encoding: "utf-8" };
  fs.writeFileSync(path.join(PROJ, "vendors.json"), JSON.stringify(mergedVendors, null, 2) + "\n", opts);
  fs.writeFileSync(path.join(PROJ, "plans.json"), JSON.stringify(mergedPlans, null, 2) + "\n", opts);
  fs.writeFileSync(path.join(PROJ, "changes.json"), JSON.stringify(mergedChanges, null, 2) + "\n", opts);

  console.log("✅ 回填完成");
  console.log("规模:", summary);
  console.log("\n估算明细（写入各 plan 的 notes 字段）:");
  estReport.forEach((r) =>
    console.log(`  ${r.est ? "⚠️" : "✅"} ${r.id.padEnd(28)} ¥${String(r.price).padEnd(6)} ${String(r.measured).padEnd(6)}M ${r.note}`)
  );
}

build();
