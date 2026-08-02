/**
 * MiniMax 模型测速脚本（流式请求 + 计时）
 *
 * 测量指标：
 *   - TTFT (Time To First Token): 首字延迟（ms）
 *   - TPS (Tokens Per Second): 生成速度（output_tokens / 生成耗时）
 *
 * 成本控制：每模型 1 次请求，max_tokens=100，固定短 prompt
 *
 * 用法: MINIMAX_API_KEY=xxx node tools/bench/bench_minimax.js
 *
 * 注意：key 从环境变量读，绝不硬编码进文件。
 */

const https = require("https");

const API_KEY = process.env.MINIMAX_API_KEY;
if (!API_KEY) {
  console.error("❌ 请设置 MINIMAX_API_KEY 环境变量");
  process.exit(1);
}

// MiniMax Token Plan 用专用 endpoint（sk-cp- key）
// 普通 API: https://api.minimaxi.com/v1/chat/completions
// Token Plan: 文档显示用 https://api.minimaxi.com/v1/chat/completions (同接口，key 区分)
const ENDPOINT = "https://api.minimaxi.com/v1/chat/completions";

// 要测的模型（从快照确认 MiniMax 支持的）
const MODELS = [
  "MiniMax-M3",
  "MiniMax-M2.7",
  "MiniMax-M2.5",
];

// 固定测试 prompt（编程场景，控制输入 token）
const TEST_MESSAGES = [
  { role: "user", content: "用 Python 写一个快速排序函数，只写代码不要解释。" },
];

function benchModel(model) {
  return new Promise((resolve) => {
    const body = JSON.stringify({
      model,
      messages: TEST_MESSAGES,
      max_tokens: 256,
      stream: true,
      stream_options: { include_usage: true },
      // M3 是思考模型，关闭思考以公平对比生成速度
      ...(model.includes("M3") ? { thinking: { type: "disabled" } } : {}),
    });

    const url = new URL(ENDPOINT);
    const options = {
      hostname: url.hostname,
      path: url.pathname,
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${API_KEY}`,
      },
    };

    const startReq = Date.now();
    let firstTokenTime = null;
    let outputTokens = 0;
    let lastChunkTime = null;
    let usageExact = false;

    const req = https.request(options, (res) => {
      let errBody = "";
      if (res.statusCode !== 200) {
        res.on("data", (c) => (errBody += c));
        res.on("end", () => {
          resolve({ model, error: `HTTP ${res.statusCode}: ${errBody.slice(0, 200)}` });
        });
        return;
      }

      res.setEncoding("utf8");
      let buffer = "";
      let contentChars = 0;
      res.on("data", (chunk) => {
        buffer += chunk;
        const lines = buffer.split("\n");
        buffer = lines.pop();

        for (const line of lines) {
          if (!line.startsWith("data:")) continue;
          const data = line.slice(5).trim();
          if (data === "[DONE]") continue;
          try {
            const obj = JSON.parse(data);
            const delta = obj.choices && obj.choices[0] && obj.choices[0].delta;
            if (delta && delta.content) {
              if (firstTokenTime === null) firstTokenTime = Date.now();
              lastChunkTime = Date.now();
              contentChars += delta.content.length;
            }
            // usage 可能在最后一块（include_usage）
            if (obj.usage && (obj.usage.completion_tokens || obj.usage.total_tokens)) {
              outputTokens = obj.usage.completion_tokens || (obj.usage.total_tokens - (obj.usage.prompt_tokens || 0));
              usageExact = true;
            }
          } catch (e) {}
        }
      });

      res.on("end", () => {
        const endReq = Date.now();
        const ttft = firstTokenTime ? firstTokenTime - startReq : null;
        const genTime = firstTokenTime && lastChunkTime ? lastChunkTime - firstTokenTime : null;
        // fallback: 按字符数估 token（中文约1.5字/token，混合约2字/token）
        if (!outputTokens) outputTokens = Math.round(contentChars / 2);
        const tps = genTime && outputTokens ? (outputTokens / (genTime / 1000)).toFixed(1) : null;
        resolve({
          model,
          ttftMs: ttft,
          genMs: genTime,
          outputTokens,
          outputChars: contentChars,
          tps: tps ? parseFloat(tps) : null,
          totalMs: endReq - startReq,
          estimated: !usageExact,
        });
      });
    });

    req.on("error", (e) => {
      resolve({ model, error: e.message });
    });

    req.write(body);
    req.end();
  });
}

async function main() {
  console.log("🔬 MiniMax 模型测速\n");
  console.log("测试 prompt: 用 Python 写快速排序（max_tokens=100）\n");
  console.log("模型".padEnd(16) + "TTFT(ms)".padStart(10) + "生成(ms)".padStart(10) + "输出token".padStart(10) + "TPS".padStart(10));
  console.log("-".repeat(56));

  for (const model of MODELS) {
    const r = await benchModel(model);
    if (r.error) {
      console.log(r.model.padEnd(16) + " ❌ " + r.error);
    } else {
      const tpsStr = r.tps ? r.tps + " t/s" + (r.estimated ? "*" : "") : "-";
      console.log(
        r.model.padEnd(16) +
        String(r.ttftMs || "-").padStart(10) +
        String(r.genMs || "-").padStart(10) +
        (String(r.outputTokens || "-") + (r.estimated ? "*" : "")).padStart(10) +
        tpsStr.padStart(10)
      );
    }
  }
  console.log("\n* = token 数为字符估算（API 未返回精确 usage）");
  console.log("\n✅ 测速完成");
}

main();
