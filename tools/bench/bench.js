/**
 * 通用 API 模型测速脚本
 *
 * 用法: node tools/bench/bench.js --vendor deepseek --key "$KEY" [--model X]
 *
 * 或从环境变量读: DEEPSEEK_API_KEY / ZHIPU_API_KEY / ...
 *
 * 测量: TTFT (首字延迟) + TPS (生成速度 tokens/s)
 * 成本控制: max_tokens=256, 每模型1次请求
 */

const https = require("https");
const http = require("http");

const CONFIG = {
  minimax: {
    endpoint: "https://api.minimaxi.com/v1/chat/completions",
    models: ["MiniMax-M3", "MiniMax-M2.7", "MiniMax-M2.5"],
    envKey: "MINIMAX_API_KEY",
    extraBody: (m) => (m.includes("M3") ? { thinking: { type: "disabled" } } : {}),
  },
  deepseek: {
    endpoint: "https://api.deepseek.com/chat/completions",
    models: ["deepseek-v4-flash", "deepseek-v4-pro"],
    envKey: "DEEPSEEK_API_KEY",
    extraBody: () => ({}),
  },
  zhipu: {
    endpoint: "https://open.bigmodel.cn/api/paas/v4/chat/completions",
    models: ["glm-5.2", "glm-5-turbo", "glm-4.7"],
    envKey: "ZHIPU_API_KEY",
    extraBody: () => ({}),
  },
};

function parseArgs() {
  const args = process.argv.slice(2);
  const opts = { vendor: null, key: null, models: null };
  for (let i = 0; i < args.length; i++) {
    if (args[i] === "--vendor" && args[i + 1]) opts.vendor = args[++i];
    if (args[i] === "--key" && args[i + 1]) opts.key = args[++i];
    if (args[i] === "--models" && args[i + 1]) opts.models = args[++i].split(",");
  }
  return opts;
}

const opts = parseArgs();
const vendor = opts.vendor || (process.argv[2] && process.argv[2] in CONFIG ? process.argv[2] : null);
if (!vendor || !CONFIG[vendor]) {
  console.error("用法: node bench.js <vendor>");
  console.error("支持:", Object.keys(CONFIG).join(", "));
  console.error("或: node bench.js --vendor deepseek --key sk-xxx");
  process.exit(1);
}

const cfg = CONFIG[vendor];
const API_KEY = opts.key || process.env[cfg.envKey];
if (!API_KEY) {
  console.error(`❌ 未找到 key。请设置 ${cfg.envKey} 环境变量或 --key`);
  process.exit(1);
}

const MODELS = opts.models || cfg.models;
const TEST_MSG = [{ role: "user", content: "用 Python 写一个快速排序函数，只输出代码不解释。用中文注释。" }];

function bench(model) {
  return new Promise((resolve) => {
    const body = JSON.stringify({
      model,
      messages: TEST_MSG,
      max_tokens: 256,
      stream: true,
      stream_options: { include_usage: true },
      ...cfg.extraBody(model),
    });

    const url = new URL(cfg.endpoint);
    const lib = url.protocol === "https:" ? https : http;
    const req = lib.request({
      hostname: url.hostname, path: url.pathname, method: "POST",
      headers: { "Content-Type": "application/json", "Authorization": `Bearer ${API_KEY}` },
    }, (res) => {
      if (res.statusCode !== 200) {
        let eb = "";
        res.on("data", (c) => (eb += c));
        res.on("end", () => resolve({ model, error: `HTTP ${res.statusCode}: ${eb.slice(0, 80)}` }));
        return;
      }
      let buf = "", firstTokenTime = null, lastChunkTime = null, outputTokens = 0, contentChars = 0, usageExact = false;
      const startReq = Date.now();
      res.setEncoding("utf8");
      res.on("data", (chunk) => {
        buf += chunk;
        const lines = buf.split("\n");
        buf = lines.pop();
        for (const line of lines) {
          if (!line.startsWith("data:")) continue;
          const d = line.slice(5).trim();
          if (d === "[DONE]") continue;
          try {
            const obj = JSON.parse(d);
            const delta = obj.choices && obj.choices[0] && obj.choices[0].delta;
            if (delta && delta.content) {
              if (!firstTokenTime) firstTokenTime = Date.now();
              lastChunkTime = Date.now();
              contentChars += delta.content.length;
            }
            if (obj.usage && (obj.usage.completion_tokens || obj.usage.total_tokens)) {
              outputTokens = obj.usage.completion_tokens || (obj.usage.total_tokens - (obj.usage.prompt_tokens || 0));
              usageExact = true;
            }
          } catch (e) {}
        }
      });
      res.on("end", () => {
        const ttft = firstTokenTime ? firstTokenTime - startReq : null;
        const genMs = firstTokenTime && lastChunkTime ? lastChunkTime - firstTokenTime : null;
        if (!outputTokens) outputTokens = Math.round(contentChars / 2);
        const tps = genMs && outputTokens ? outputTokens / (genMs / 1000) : null;
        resolve({ model, ttftMs: ttft, genMs, outputTokens, outputChars: contentChars, tps: tps ? Math.round(tps * 10) / 10 : null, estimated: !usageExact });
      });
    });
    req.on("error", (e) => resolve({ model, error: e.message }));
    req.write(body);
    req.end();
  });
}

async function main() {
  console.log(`🔬 ${vendor.toUpperCase()} 模型测速\n`);
  console.log("模型".padEnd(22) + "TTFT(ms)".padStart(10) + "生成(ms)".padStart(10) + "输出tok".padStart(9) + "TPS".padStart(10));
  console.log("-".repeat(61));
  for (const m of MODELS) {
    const r = await bench(m);
    if (r.error) {
      console.log(m.padEnd(22) + " ❌ " + r.error);
    } else {
      console.log(
        m.padEnd(22) +
        String(r.ttftMs || "-").padStart(10) +
        String(r.genMs || "-").padStart(10) +
        (String(r.outputTokens || "-") + (r.estimated ? "*" : "")).padStart(9) +
        (r.tps ? r.tps + " t/s" : "-").padStart(10)
      );
    }
  }
  console.log("\n✅ 测速完成");
}

main();
