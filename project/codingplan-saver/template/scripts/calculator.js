// ============================================================
// 成本计算引擎 — 7家厂商 × 4种计费类型
// 输入: usage = { inputM, outputM, cacheHitRate }
//   inputM: 月输入token（百万）
//   outputM: 月输出token（百万）
//   cacheHitRate: 缓存命中率 (0-1)
// 输出: { cost, status, note, precision, planName, vendorName }
//   cost: 月成本（元），null=无法计算
//   status: 'ok' | 'throttled' | 'unknown' | 'error'
// ============================================================

// usage 默认值（中度场景）
const DEFAULT_USAGE = { inputM: 30, outputM: 10, cacheHitRate: 0.7 };

/**
 * 计算所有厂商的所有套餐成本，返回排序后的结果数组
 * @param {object} models - pricing-models.json 数据
 * @param {object} usage - { inputM, outputM, cacheHitRate }
 * @param {string} selectedModel - 用户选的参考模型（影响智谱等按模型计费的厂商）
 * @returns {Array} 排序后的结果（成本从低到高，null 排最后）
 */
function calcAll(models, usage, selectedModel) {
  const results = [];
  for (const [vendorId, vendor] of Object.entries(models)) {
    if (vendorId.startsWith('_')) continue;
    const vendorResults = calcVendor(vendorId, vendor, usage, selectedModel);
    results.push(...vendorResults);
  }
  // 排序：有成本的在前（低→高），null（未公开）在后
  results.sort((a, b) => {
    if (a.cost === null && b.cost === null) return 0;
    if (a.cost === null) return 1;
    if (b.cost === null) return -1;
    return a.cost - b.cost;
  });
  return results;
}

function calcVendor(vendorId, vendor, usage, selectedModel) {
  const results = [];
  switch (vendor.type) {
    case 'payg':
      // 按量：每个模型一个结果
      for (const [modelId, prices] of Object.entries(vendor.models)) {
        const r = calcPayg(vendor, modelId, prices, usage);
        results.push(r);
      }
      // 如果有会员（Kimi），也列出
      if (vendor.membership) {
        for (const [planName, plan] of Object.entries(vendor.membership.plans)) {
          results.push({
            vendorName: vendor.name, planName: planName + '（会员）',
            cost: plan.fee, status: 'unknown', precision: vendor.membership.precision,
            note: vendor.membership.note || '额度未公开',
          });
        }
      }
      break;

    case 'credit':
      // 积分制（智谱）：用选中模型的系数算积分消耗
      for (const [planName, plan] of Object.entries(vendor.plans)) {
        const r = calcCredit(vendor, planName, plan, usage, selectedModel);
        results.push(r);
      }
      break;

    case 'pool':
      // Token池（腾讯）：每个套餐一个结果
      for (const [planName, plan] of Object.entries(vendor.plans)) {
        const r = calcPool(vendor, planName, plan, usage);
        results.push(r);
      }
      break;

    case 'call-estimate':
      // 次数估算（MiniMax）
      for (const [planName, plan] of Object.entries(vendor.plans)) {
        const r = calcCallEstimate(vendor, planName, plan, usage);
        results.push(r);
      }
      break;

    case 'call-count':
      // 调用次数（阿里）
      for (const [planName, plan] of Object.entries(vendor.plans)) {
        const r = calcCallCount(vendor, planName, plan, usage);
        results.push(r);
      }
      break;

    case 'unknown':
      // 未公开（字节）：只给月费
      for (const [planName, plan] of Object.entries(vendor.plans)) {
        results.push({
          vendorName: vendor.name, planName,
          cost: plan.fee, status: 'unknown', precision: 'unknown',
          note: vendor.note || '计费规则未公开',
        });
      }
      break;
  }
  // 给每个结果补 vendorId（用于模型过滤关联）
  results.forEach(r => { r.vendorId = vendorId; });
  return results;
}

// === 按量计费（DeepSeek / Kimi K3 API）===
function calcPayg(vendor, modelId, prices, usage) {
  const cachedInput = usage.inputM * usage.cacheHitRate;
  const missInput = usage.inputM * (1 - usage.cacheHitRate);
  // 价格单位：元/百万token，usage 单位：百万 token，直接相乘
  const cost = cachedInput * prices.inputCached + missInput * prices.inputMiss + usage.outputM * prices.output;
  return {
    vendorName: vendor.name,
    planName: modelId + '（按量）',
    cost: Math.round(cost * 100) / 100,
    status: 'ok',
    precision: vendor.precision || 'exact',
    note: '按量付费，用多少付多少',
  };
}

// === 积分制（智谱）===
function calcCredit(vendor, planName, plan, usage, selectedModel) {
  // 找模型系数：优先用户选的，否则默认 GLM-5.2
  const modelName = selectedModel && vendor.models[selectedModel] ? selectedModel : 'GLM-5.2';
  const coef = vendor.models[modelName];
  if (!coef) {
    return { vendorName: vendor.name, planName, cost: null, status: 'error', precision: 'exact', note: '模型系数缺失' };
  }
  // 积分消耗 = (输入×In + 缓存×Cached + 输出×Out) / 10000，单位：百万token→×1e6/1e4=×100
  const cachedInputM = usage.inputM * usage.cacheHitRate;
  const pointsUsed = (usage.inputM * coef.input + cachedInputM * coef.cached + usage.outputM * coef.output) * 100;
  // 月积分 ≈ 周积分 × 4.33
  const monthlyPoints = plan.weeklyPoints * 4.33;
  if (pointsUsed <= monthlyPoints) {
    return {
      vendorName: vendor.name, planName: planName + '（' + modelName + '）',
      cost: plan.fee, status: 'ok', precision: 'exact',
      note: '消耗 ' + Math.round(pointsUsed) + ' 积分/月，额度 ' + Math.round(monthlyPoints) + '，够用',
    };
  } else {
    return {
      vendorName: vendor.name, planName: planName + '（' + modelName + '）',
      cost: plan.fee, status: 'throttled', precision: 'exact',
      note: '需 ' + Math.round(pointsUsed) + ' 积分/月，超出额度 ' + Math.round(monthlyPoints) + '，会限流',
    };
  }
}

// === Token池（腾讯）===
function calcPool(vendor, planName, plan, usage) {
  // 三类 token 1:1:1 统一抵扣（缓存命中+未命中+输出）
  const cachedInputM = usage.inputM * usage.cacheHitRate;
  const missInputM = usage.inputM * (1 - usage.cacheHitRate);
  const totalTokens = (cachedInputM + missInputM + usage.outputM) * 1e6; // 转 token 数
  if (totalTokens <= plan.tokens) {
    return {
      vendorName: vendor.name, planName,
      cost: plan.fee, status: 'ok', precision: 'exact',
      note: '消耗 ' + (totalTokens / 1e6).toFixed(0) + 'M Token，额度 ' + (plan.tokens / 1e6).toFixed(0) + 'M，够用',
    };
  } else {
    return {
      vendorName: vendor.name, planName,
      cost: plan.fee, status: 'throttled', precision: 'exact',
      note: '需 ' + (totalTokens / 1e6).toFixed(0) + 'M Token，超出额度 ' + (plan.tokens / 1e6).toFixed(0) + 'M，会限流',
    };
  }
}

// === 次数估算（MiniMax）===
function calcCallEstimate(vendor, planName, plan, usage) {
  // 总token / 单次token = 调用次数
  const totalTokens = (usage.inputM + usage.outputM) * 1e6;
  const estimatedCalls = totalTokens / vendor.tokensPerCall;
  if (estimatedCalls <= plan.callsPerMonth) {
    return {
      vendorName: vendor.name, planName,
      cost: plan.fee, status: 'ok', precision: 'estimate',
      note: '约 ' + Math.round(estimatedCalls) + ' 次调用，额度 ' + plan.callsPerMonth + ' 次（按M3 50K/次估算）',
    };
  } else {
    return {
      vendorName: vendor.name, planName,
      cost: plan.fee, status: 'throttled', precision: 'estimate',
      note: '约 ' + Math.round(estimatedCalls) + ' 次调用，超额度 ' + plan.callsPerMonth + ' 次（估算，可能需购积分包）',
    };
  }
}

// === 调用次数（阿里，按提问次数）===
function calcCallCount(vendor, planName, plan, usage) {
  // token → 提问次数：总token / (callsPerQuery × avgTokensPerCall)
  // 阿里按"模型调用次数"计，1次提问≈5-30次调用，取均值15
  // 假设每次调用约 5K token（编程场景平均）
  const totalTokens = (usage.inputM + usage.outputM) * 1e6;
  const estimatedCalls = totalTokens / 5000;
  if (estimatedCalls <= plan.callsPerMonth) {
    return {
      vendorName: vendor.name, planName,
      cost: plan.fee, status: 'ok', precision: 'estimate',
      note: '约 ' + Math.round(estimatedCalls) + ' 次调用，额度 ' + plan.callsPerMonth + ' 次（按5K/次估算）',
    };
  } else {
    return {
      vendorName: vendor.name, planName,
      cost: plan.fee, status: 'throttled', precision: 'estimate',
      note: '约 ' + Math.round(estimatedCalls) + ' 次调用，超额度 ' + plan.callsPerMonth + ' 次，会限流',
    };
  }
}
