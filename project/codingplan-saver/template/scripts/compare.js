// ============================================================
// Tab 2: 对比（散点图 + 筛选条 + 表格 + 移动端卡片）
// ============================================================
const compareState = {
  filters: { types: new Set(), tags: new Set(), models: new Set(), categories: new Set(), monthlyPriceMax: null, search: '' },
  sort: { key: null, dir: 'asc' },
  columnsExpanded: false,
  columnMode: 'monthly', // monthly | api | model | calc
  selectedModel: null
};

function renderCompare() {
  const body = document.getElementById('compare-body');
  body.innerHTML = renderTableSection();
  bindCompareFilters();
  renderQuickSwitch();
  bindQuickSwitch();
  renderCompareTable();
  setTimeout(renderChart, 200);
}

// 月订阅 / API按量 快捷切换（本质是 type 筛选的预设）
function renderQuickSwitch() {
  const el = document.getElementById('compareQuickSwitch');
  if (!el) return '';
  const presets = [
    { label: '月订阅套餐', types: ['Coding Plan', 'Token Plan', 'Agent Plan', '会员'] },
    { label: 'API 按量', types: ['API 按量'] },
    { label: '按模型', types: [], isModelView: true },
    { label: '成本测算', types: [], isCalcView: true },
  ];
  const btnStyle = 'display:inline-flex;align-items:center;padding:8px 16px;border:1px solid var(--border);background:transparent;color:var(--text-secondary);border-radius:0;cursor:pointer;font-size:13px;font-weight:600;transition:all .15s;';
  const btnActive = 'border-color:var(--accent);background:var(--accent);color:#fff;';
  el.innerHTML = '<div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center;">' +
    presets.map((p, i) =>
      '<button class="quick-switch-btn" style="' + btnStyle + (i === 0 ? btnActive : '') + '" data-preset="' + i + '">' + p.label + '</button>'
    ).join('') +
    '</div>';
  return '';
}

function bindQuickSwitch() {
  const el = document.getElementById('compareQuickSwitch');
  if (!el) return;
  const presets = [
    { types: ['Coding Plan', 'Token Plan', 'Agent Plan', '会员'], columnMode: 'monthly' },
    { types: ['API 按量'], columnMode: 'api' },
    { types: [], columnMode: 'model', isModelView: true },
    { types: [], columnMode: 'calc', isCalcView: true },
  ];
  el.addEventListener('click', e => {
    const btn = e.target.closest('.quick-switch-btn');
    if (!btn) return;
    const idx = parseInt(btn.dataset.preset, 10);
    const preset = presets[idx];
    compareState.filters.types = new Set(preset.types);
    compareState.columnMode = preset.columnMode;
    const btnStyle = 'display:inline-flex;align-items:center;padding:8px 16px;border:1px solid var(--border);background:transparent;color:var(--text-secondary);border-radius:0;cursor:pointer;font-size:13px;font-weight:600;transition:all .15s;';
    const btnActive = 'border-color:var(--accent);background:var(--accent);color:#fff;';
    el.querySelectorAll('.quick-switch-btn').forEach(b => {
      b.setAttribute('style', btnStyle + (b === btn ? btnActive : ''));
    });
    syncCompareFilterUI();
    renderCompareTable();
    renderChart();
  });
}

function renderChartSection() {
  return '<section class="section-sm">' +
    '<div class="container">' +
      '<div class="section-header" style="margin-bottom:var(--sp-4);">' +
        '<h2 class="section-title" id="chartTitle" style="margin:0;">价格 vs Token 额度</h2>' +
        '<p class="section-subtitle" id="chartSubtitle" style="margin:0;">越靠左下越便宜（高性价比区）</p>' +
      '</div>' +
      '<div class="chart-card"><div class="chart-container" id="priceVsTokenChart"></div></div>' +
    '</div></section>';
}

function renderTableSection() {
  const vendorCount = new Set(plans.map(p => p.vendorId)).size;
  const planCount = plans.filter(p => p.status !== 'deprecated').length;
  const updatedDate = (site.updatedAt || '').slice(5).replace('-', '.') || '官网快照';
  return '<section class="section-sm">' +
    '<div class="container">' +
      '<div class="section-header" style="margin-bottom:var(--sp-3);">' +
        '<h2 class="section-title" style="margin:0;">套餐对比</h2>' +
        '<p class="section-subtitle" style="margin:0;">' + vendorCount + ' 家厂商 · ' + planCount + ' 个套餐 · 数据源官网快照 · 更新 ' + updatedDate + '</p>' +
      '</div>' +
      '<div id="compareQuickSwitch" style="margin-bottom:var(--sp-3);"></div>' +
      // 散点图（放在搜索栏上面）
      '<div class="chart-card" style="margin-bottom:var(--sp-4);">' +
        '<div style="margin-bottom:var(--sp-3);">' +
          '<h3 class="section-title" id="chartTitle" style="margin:0;font-size:15px;">价格 vs Token 额度</h3>' +
          '<p class="section-subtitle" id="chartSubtitle" style="margin:0;">越靠左下越便宜（高性价比区）</p>' +
        '</div>' +
        '<div class="chart-container" id="priceVsTokenChart"></div>' +
      '</div>' +
      '<div id="compareFilterBar"></div>' +
      '<div class="table-wrap"><table class="data-table"><thead id="plansTableHead"><tr></tr></thead><tbody id="plansTableBody"></tbody></table></div>' +
      '<div class="plan-cards-view" id="plansCardsView"></div>' +
    '</div></section>';
}

// 渲染"点击对比"折叠触发按钮（放在表格下方，点开才显示模型对比图）
function renderModelToggle() {
  // 仅 model 模式才显示折叠触发
  const toggle = document.getElementById('modelChartToggle');
  if (toggle) toggle.remove();
  if (compareState.columnMode !== 'model') return;
  const table = document.querySelector('.table-wrap');
  if (!table) return;
  const btn = document.createElement('div');
  btn.id = 'modelChartToggle';
  const sm = compareState.selectedModel || '';
  btn.innerHTML = '<button class="btn" id="modelToggleBtn" style="margin-top:var(--sp-4);background:transparent;color:var(--accent);border-color:var(--accent);">▸ 对比' + (sm ? ' [' + sm + ']' : '') + ' 各平台 TOKEN/元</button>';
  table.parentNode.insertBefore(btn, table.nextSibling);
  btn.querySelector('#modelToggleBtn').addEventListener('click', () => {
    const card = document.getElementById('modelChartCard');
    const b = document.getElementById('modelToggleBtn');
    const open = card.style.display === 'block';
    if (open) {
      card.style.display = 'none';
      b.innerHTML = '▸ 对比' + (compareState.selectedModel ? ' [' + compareState.selectedModel + ']' : '') + ' 各平台 TOKEN/元';
    } else {
      card.style.display = 'block';
      b.innerHTML = '▾ 收起对比';
      renderModelChart(compareState.selectedModel);
      if (window._modelChart) window._modelChart.resize();
    }
  });
}

// 根据当前 columnMode 生成表头
function renderTableHead() {
  const head = document.getElementById('plansTableHead');
  if (!head) return;
  const cols = getColumns(compareState.columnMode);
  head.innerHTML = '<tr>' + cols.map(c => '<th' + (c.extra ? ' class="col-extra"' : '') + '>' + c.label + '</th>').join('') + '</tr>';
}

// 列定义：月订阅/API按量/按模型/全部 多种模式
function getColumns(mode) {
  const common = [{ key: 'vendor', label: '平台 / 套餐' }];
  const action = [{ key: 'action', label: '去购买', isAction: true }];
  if (mode === 'api') {
    return common.concat([
      { key: 'inputPrice', label: '输入价', unit: '元/M' },
      { key: 'outputPrice', label: '输出价', unit: '元/M' },
      { key: 'cachePrice', label: '缓存价', unit: '元/M' },
      { key: 'rateLimit', label: '并发/限速', isRateLimit: true },
      { key: 'contextLen', label: '上下文' },
    ]).concat(action);
  }
  if (mode === 'model') {
    return [
      { key: 'modelName', label: '模型', isModelName: true },
      { key: 'platformCount', label: '支持平台', isCount: true },
      { key: 'cheapestMonthly', label: '最便宜月订阅', isCheapest: true },
      { key: 'cheapestApi', label: '最便宜 API 按量', isCheapest: true },
      { key: 'action', label: '去购买', isAction: true },
    ];
  }
  // monthly 和 all 都用月订阅列（all 时 API 行的月费/月用量会是空，但能通过筛选切到 API 模式）
  return common.concat([
    { key: 'monthlyPrice', label: '月费', isPrice: true },
    { key: 'usage', label: '月用量' },
    { key: 'tpu', label: '每元Token', isTPU: true },
    { key: 'rateLimit', label: '限速', isRateLimit: true },
    { key: 'models', label: '关键模型' },
  ]).concat(action);
}

function renderCompareFilterBar() {
  const filterable = plans.filter(p => p.status !== 'deprecated');
  const types = [...new Set(filterable.map(p => p.type))].sort();
  const allTags = new Set();
  filterable.forEach(p => (p.tags || []).forEach(t => allTags.add(t)));
  const tags = [...allTags].sort();

  const typeChips = types.map(t => '<button class="filter-chip" data-filter-type="types" data-filter-value="' + escapeHtml(t) + '">' + escapeHtml(t) + '</button>').join('');
  const tagChips = tags.map(t => '<button class="filter-chip" data-filter-type="tags" data-filter-value="' + escapeHtml(t) + '">' + escapeHtml(t) + '</button>').join('');
  const catLabels = { 'model-maker': '原厂', 'cloud-maas': '云厂商', 'vertical-cloud': '垂直云', 'aggregator': '聚合商' };
  const cats = [...new Set(filterable.map(p => p.category || 'model-maker'))].sort();
  const catChips = cats.map(c => '<button class="filter-chip" data-filter-type="categories" data-filter-value="' + c + '">' + (catLabels[c] || c) + '</button>').join('');

  const allModels = [...new Set(filterable.flatMap(p => p.models || []))].sort();
  const modelChips = allModels.slice(0, 12).map(m =>
    '<button class="filter-chip" data-filter-type="models" data-filter-value="' + escapeHtml(m) + '">' + escapeHtml(m) + '</button>'
  ).join('');

  return '<div class="filter-bar">' +
    '<select class="filter-select" id="sortSelect">' +
      '<option value="">默认排序</option>' +
      '<option value="monthlyPrice-asc">月费 低-高</option>' +
      '<option value="monthlyPrice-desc">月费 高-低</option>' +
      '<option value="measuredMonthlyToken-desc">月用量 多-少</option>' +
      '<option value="tokensPerYuan-desc">每元Token 高-低</option>' +
    '</select>' +
    '<input type="text" class="filter-select" id="searchInput" placeholder="搜索厂商/套餐..." style="min-width:160px;">' +
    '<button class="filter-chip" id="resetBtn">重置</button>' +
    '<span class="filter-stats">显示 <strong id="filterCount">0</strong> / ' + filterable.length + ' 个套餐</span>' +
  '</div>' +
  (modelChips ? '<div class="filter-bar"><span style="font-size:11px;font-weight:700;color:var(--text-helper);">模型:</span>' + modelChips + '</div>' : '');
}

function parseHashFilter() {
  const hash = location.hash;
  const qIdx = hash.indexOf('?');
  if (qIdx < 0) return null;
  const params = new URLSearchParams(hash.slice(qIdx + 1));
  const f = {};
  for (const [k, v] of params) f[k] = v;
  return f;
}

function bindCompareFilters() {
  const fm = document.getElementById('compareFilterBar');
  if (!fm) return;
  fm.innerHTML = renderCompareFilterBar();

  const hashFilter = parseHashFilter();
  if (hashFilter) {
    if (hashFilter.monthlyPriceMax) compareState.filters.monthlyPriceMax = Number(hashFilter.monthlyPriceMax);
    if (hashFilter.model) compareState.filters.models.add(hashFilter.model);
    if (hashFilter.tag) compareState.filters.tags.add(hashFilter.tag);
    if (hashFilter.vendor) {
      compareState.filters.search = hashFilter.vendor.toLowerCase();
      const si = document.getElementById('searchInput');
      if (si) si.value = hashFilter.vendor;
    }
  }
  syncCompareFilterUI();

  fm.querySelectorAll('.filter-chip[data-filter-type]').forEach(chip => {
    chip.addEventListener('click', () => {
      const type = chip.dataset.filterType;
      const value = chip.dataset.filterValue;
      const set = compareState.filters[type];
      if (set.has(value)) set.delete(value); else set.add(value);
      syncCompareFilterUI();
      renderCompareTable();
    });
  });

  const reset = document.getElementById('resetBtn');
  if (reset) reset.addEventListener('click', () => {
    compareState.filters.types.clear();
    compareState.filters.tags.clear();
    compareState.filters.models.clear();
    compareState.filters.monthlyPriceMax = null;
    compareState.filters.search = '';
    compareState.sort = { key: null, dir: 'asc' };
    const ss = document.getElementById('sortSelect'); if (ss) ss.value = '';
    const si = document.getElementById('searchInput'); if (si) si.value = '';
    syncCompareFilterUI();
    renderCompareTable();
  });

  const ss = document.getElementById('sortSelect');
  if (ss) ss.addEventListener('change', () => {
    const val = ss.value;
    if (!val) compareState.sort = { key: null, dir: 'asc' };
    else { const [k, d] = val.split('-'); compareState.sort = { key: k, dir: d }; }
    renderCompareTable();
  });

  const si = document.getElementById('searchInput');
  if (si) si.addEventListener('input', () => {
    compareState.filters.search = si.value.trim().toLowerCase();
    renderCompareTable();
  });

  const toggle = document.getElementById('toggleColumnsBtn');
  if (toggle) toggle.addEventListener('click', () => {
    compareState.columnsExpanded = !compareState.columnsExpanded;
    document.querySelectorAll('td.col-extra').forEach(c => c.classList.toggle('col-hidden', !compareState.columnsExpanded));
    toggle.textContent = compareState.columnsExpanded ? '收起额外列' : '展开全部列';
    toggle.classList.toggle('active', compareState.columnsExpanded);
  });
}

function syncCompareFilterUI() {
  document.querySelectorAll('.filter-chip[data-filter-type]').forEach(chip => {
    const type = chip.dataset.filterType;
    const value = chip.dataset.filterValue;
    const active = compareState.filters[type] && compareState.filters[type].has(value);
    chip.classList.toggle('active', !!active);
  });
}

function filterPlans() {
  const f = compareState.filters;
  let result = plans.filter(p => {
    if (p.status === 'deprecated') return false;
    if (f.categories.size && !f.categories.has(p.category || 'model-maker')) return false;
    if (f.tags.size && !(p.tags || []).some(t => f.tags.has(t))) return false;
    if (f.models.size && !(p.models || []).some(m => f.models.has(m))) return false;
    if (f.monthlyPriceMax && typeof p.monthlyPrice === 'number' && p.monthlyPrice > f.monthlyPriceMax) return false;
    if (f.search) {
      const hay = (p.vendor + ' ' + p.plan + ' ' + (p.models || []).join(' ') + ' ' + (p.tags || []).join(' ')).toLowerCase();
      if (!hay.includes(f.search)) return false;
    }
    return true;
  });
  const { key, dir } = compareState.sort;
  if (key) {
    result.sort((a, b) => {
      if (key === 'tokensPerYuan') {
        const aVal = (typeof a.monthlyPrice === 'number' && typeof a.measuredMonthlyToken === 'number' && a.monthlyPrice > 0) ? a.measuredMonthlyToken / a.monthlyPrice : -1;
        const bVal = (typeof b.monthlyPrice === 'number' && typeof b.measuredMonthlyToken === 'number' && b.monthlyPrice > 0) ? b.measuredMonthlyToken / b.monthlyPrice : -1;
        return dir === 'asc' ? aVal - bVal : bVal - aVal;
      }
      const av = a[key], bv = b[key];
      const aNum = typeof av === 'number' ? av : (av === '无限制' ? Infinity : -1);
      const bNum = typeof bv === 'number' ? bv : (bv === '无限制' ? Infinity : -1);
      return dir === 'asc' ? aNum - bNum : bNum - aNum;
    });
  }
  return result;
}

function renderCompareTable() {
  const filtered = filterPlans();
  const countEl = document.getElementById('filterCount');
  if (countEl) countEl.textContent = filtered.length;
  const tbody = document.getElementById('plansTableBody');
  const cardsView = document.getElementById('plansCardsView');

  if (!filtered.length) {
    const empty = '<div style="text-align:center;padding:48px;color:var(--text-muted);">没有匹配的套餐，试试重置筛选</div>';
    if (tbody) tbody.innerHTML = '<tr><td colspan="99">' + empty + '</td></tr>';
    if (cardsView) cardsView.innerHTML = empty;
    return;
  }

  renderTableHead();
  // 非 calc 模式：恢复表格/图/筛选栏显示，隐藏 calcUI
  if (compareState.columnMode !== 'calc') {
    const calcUI = document.getElementById('calcUI');
    if (calcUI) calcUI.style.display = 'none';
    ['compareFilterBar', 'plansTableBody'].forEach(id => {
      const el = document.getElementById(id); if (el) el.style.display = '';
    });
    const tw = document.querySelector('.table-wrap'); if (tw) tw.style.display = '';
    const cc = document.querySelector('.chart-card'); if (cc) cc.style.display = '';
  }
  if (compareState.columnMode === 'calc') {
    renderCalculator();
    return;
  }
  if (compareState.columnMode === 'model') {
    renderModelRows(filtered);
    return;
  }
  if (tbody) {
    const cols = getColumns(compareState.columnMode);
    tbody.innerHTML = filtered.map(p => {
      const cells = cols.map(c => {
        if (c.isAction) {
          const buyBtn = p.status === 'sold_out' || p.status === 'paused' || p.status === 'deprecated'
            ? '<span class="badge">' + ({sold_out:'售罄',paused:'暂停',deprecated:'下架'}[p.status]||'—') + '</span>'
            : '<a href="' + (p.action || '#') + '" target="_blank" rel="nofollow sponsored" class="btn btn-primary btn-sm">去购买 →</a>';
          return '<td class="col-action">' + buyBtn + '</td>';
        }
        if (c.key === 'vendor') {
          return '<td class="col-vendor">' +
            '<div style="font-weight:600;">' + escapeHtml(p.vendor) + '</div>' +
            '<div style="font-size:12px;color:var(--text-helper);font-weight:400;">' + escapeHtml(p.plan) + ' · ' + escapeHtml(p.type) + '</div>' +
          '</td>';
        }
        if (c.isPrice) {
          const val = typeof p.monthlyPrice === 'number' ? formatPrice(p.monthlyPrice, p.currency || '¥') : '<span style="color:var(--text-placeholder);">—</span>';
          return '<td class="col-price">' + val + '</td>';
        }
        if (c.key === 'usage') {
          const val = p.tokenLimit || (p.measuredMonthlyToken ? p.measuredMonthlyToken + 'M Token' : '<span style="color:var(--text-placeholder);">按量</span>');
          return '<td style="font-size:12px;color:var(--text-secondary);">' + escapeHtml(val) + '</td>';
        }
        if (c.isTPU) {
          const tpu = (typeof p.monthlyPrice === 'number' && typeof p.measuredMonthlyToken === 'number' && p.monthlyPrice > 0)
            ? '<span style="font-family:var(--mono);font-weight:700;color:var(--accent);">' + (p.measuredMonthlyToken / p.monthlyPrice).toFixed(2) + '</span><span style="color:var(--text-helper);font-size:10px;"> M/元</span>'
            : '<span style="color:var(--text-placeholder);">—</span>';
          return '<td class="col-price">' + tpu + '</td>';
        }
        if (c.isRateLimit) {
          return '<td style="font-size:11px;color:var(--text-secondary);">' + escapeHtml(p.rateLimit || '—') + '</td>';
        }
        if (c.key === 'models') {
          const km = (p.models || []).slice(0, 3).join(' / ') + ((p.models || []).length > 3 ? ' +' + (p.models.length - 3) : '');
          return '<td style="font-size:12px;">' + escapeHtml(km) + '</td>';
        }
        // API 按量列
        if (c.key === 'inputPrice' || c.key === 'outputPrice' || c.key === 'cachePrice') {
          const v = p[c.key];
          const val = typeof v === 'number' ? '<span style="font-family:var(--mono);font-weight:600;">¥' + v + '</span>' : '<span style="color:var(--text-placeholder);">—</span>';
          return '<td class="col-price">' + val + '</td>';
        }
        if (c.key === 'contextLen') {
          return '<td style="font-size:12px;color:var(--text-secondary);">' + escapeHtml(p.contextLen || '—') + '</td>';
        }
        return '<td>—</td>';
      }).join('');
      return '<tr>' + cells + '</tr>';
    }).join('');
  }
  renderCompareCards(filtered);
}

// === 成本测算器 ===
function renderCalculator() {
  // 隐藏表格、筛选栏、散点图
  ['compareFilterBar', 'plansTableBody', 'plansCardsView'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.style.display = 'none';
  });
  const tableWrap = document.querySelector('.table-wrap');
  if (tableWrap) tableWrap.style.display = 'none';
  const chartCard = document.querySelector('.chart-card');
  if (chartCard) chartCard.style.display = 'none';
  const thead = document.getElementById('plansTableHead');
  if (thead) thead.innerHTML = '';

  const container = document.querySelector('#compare-body .container');
  if (!container) return;
  // 渲染测算器 UI（如果还没渲染）
  if (!document.getElementById('calcUI')) {
    container.insertAdjacentHTML('beforeend', renderCalcHTML());
    bindCalcControls();
  }
  document.getElementById('calcUI').style.display = 'block';
  // 渲染模型多选标签
  const modelFilter = document.getElementById('calcModelFilter');
  if (modelFilter && !modelFilter.dataset.rendered) {
    const allModels = [...new Set(plans.flatMap(p => p.models || []))].sort();
    modelFilter.innerHTML = allModels.map(m =>
      '<label style="display:inline-flex;align-items:center;gap:4px;padding:4px 10px;border:1px solid var(--border-subtle);font-size:11px;cursor:pointer;color:var(--text-secondary);"><input type="checkbox" value="' + escapeHtml(m) + '" style="accent-color:var(--accent);">' + escapeHtml(m) + '</label>'
    ).join('');
    modelFilter.dataset.rendered = '1';
    modelFilter.querySelectorAll('input[type=checkbox]').forEach(cb => {
      cb.addEventListener('change', updateCalcResults);
    });
  }
  updateCalcResults();
}

function renderCalcHTML() {
  const profiles = [
    { icon: '👤', name: '偶尔写代码', desc: '学生 / 体验 / 一周几次', inputM: 5, outputM: 2, cacheHitRate: 0.8 },
    { icon: '💻', name: '每天AI编程', desc: '日常工作主力', inputM: 30, outputM: 10, cacheHitRate: 0.7 },
    { icon: '🔥', name: '全天靠AI', desc: '重度编码 / 长任务', inputM: 100, outputM: 40, cacheHitRate: 0.6 },
    { icon: '🤖', name: '多Agent并行', desc: '团队 / 龙虾 / CI', inputM: 300, outputM: 100, cacheHitRate: 0.5 },
  ];
  const profileBtns = profiles.map((p, i) =>
    '<button class="calc-profile" data-i="' + i + '" style="display:flex;flex-direction:column;align-items:flex-start;padding:var(--sp-4);border:1px solid var(--border-subtle);background:transparent;text-align:left;cursor:pointer;min-width:140px;flex:1;">' +
      '<span style="font-size:20px;">' + p.icon + '</span>' +
      '<span style="font-weight:700;font-size:14px;margin-top:var(--sp-2);">' + p.name + '</span>' +
      '<span style="font-size:11px;color:var(--text-helper);margin-top:2px;">' + p.desc + '</span>' +
    '</button>'
  ).join('');
  return '<div id="calcUI">' +
    '<div style="border:1px solid var(--border-subtle);padding:var(--sp-5);margin-bottom:var(--sp-5);">' +
      '<h3 style="margin:0 0 var(--sp-4);font-size:15px;font-weight:700;">你是哪种用户？</h3>' +
      '<div style="display:flex;gap:var(--sp-3);flex-wrap:wrap;">' + profileBtns + '</div>' +
      '<div style="margin-top:var(--sp-4);border-top:1px solid var(--border-subtle);padding-top:var(--sp-4);">' +
        '<div style="font-size:12px;color:var(--text-helper);margin-bottom:var(--sp-3);">你主要用什么模型？（可多选，不选=全部）</div>' +
        '<div id="calcModelFilter" style="display:flex;gap:6px;flex-wrap:wrap;"></div>' +
      '</div>' +
      '<details style="margin-top:var(--sp-4);">' +
        '<summary style="font-size:12px;color:var(--accent);cursor:pointer;font-weight:600;">▸ 自定义精确用量（高级）</summary>' +
        '<div style="padding:var(--sp-4) 0;display:grid;gap:var(--sp-4);">' +
          '<div><label style="font-size:12px;color:var(--text-helper);">月输入 Token: <b id="calcInputVal" style="color:var(--accent);">30</b> M</label><input type="range" id="calcInput" min="1" max="500" value="30" style="width:100%;accent-color:var(--accent);"></div>' +
          '<div><label style="font-size:12px;color:var(--text-helper);">月输出 Token: <b id="calcOutputVal" style="color:var(--accent);">10</b> M</label><input type="range" id="calcOutput" min="1" max="200" value="10" style="width:100%;accent-color:var(--accent);"></div>' +
          '<div><label style="font-size:12px;color:var(--text-helper);">缓存命中率: <b id="calcCacheVal" style="color:var(--accent);">70</b>%</label><input type="range" id="calcCache" min="0" max="95" value="70" style="width:100%;accent-color:var(--accent);"></div>' +
        '</div>' +
      '</details>' +
    '</div>' +
    '<div id="calcResults" style="border:1px solid var(--border-subtle);"></div>' +
    '<p style="font-size:11px;color:var(--text-helper);margin-top:var(--sp-3);">✅精确（4家按官网规则精确计算） · ⚠️估算（3家因计费规则未完全公开） · "会限流"=用量超套餐额度</p>' +
  '</div>';
}

function bindCalcControls() {
  const profiles = [
    { inputM: 5, outputM: 2, cacheHitRate: 0.8 },
    { inputM: 30, outputM: 10, cacheHitRate: 0.7 },
    { inputM: 100, outputM: 40, cacheHitRate: 0.6 },
    { inputM: 300, outputM: 100, cacheHitRate: 0.5 },
  ];
  // 用户画像按钮：点了直接设用量并高亮
  document.querySelectorAll('.calc-profile').forEach((btn, i) => {
    if (i === 1) { btn.style.borderColor = 'var(--accent)'; btn.style.background = 'rgba(0,47,167,0.05)'; }
    btn.addEventListener('click', () => {
      const p = profiles[i];
      const inp = document.getElementById('calcInput');
      const out = document.getElementById('calcOutput');
      const cache = document.getElementById('calcCache');
      if (inp) { inp.value = p.inputM; document.getElementById('calcInputVal').textContent = p.inputM; }
      if (out) { out.value = p.outputM; document.getElementById('calcOutputVal').textContent = p.outputM; }
      if (cache) { cache.value = Math.round(p.cacheHitRate * 100); document.getElementById('calcCacheVal').textContent = Math.round(p.cacheHitRate * 100); }
      document.querySelectorAll('.calc-profile').forEach(b => { b.style.borderColor = 'var(--border-subtle)'; b.style.background = 'transparent'; });
      btn.style.borderColor = 'var(--accent)'; btn.style.background = 'rgba(0,47,167,0.05)';
      updateCalcResults();
    });
  });
  // 高级滑块
  const update = () => {
    const inp = document.getElementById('calcInput');
    const out = document.getElementById('calcOutput');
    const cache = document.getElementById('calcCache');
    if (inp) document.getElementById('calcInputVal').textContent = inp.value;
    if (out) document.getElementById('calcOutputVal').textContent = out.value;
    if (cache) document.getElementById('calcCacheVal').textContent = cache.value;
    updateCalcResults();
    document.querySelectorAll('.calc-profile').forEach(b => { b.style.borderColor = 'var(--border-subtle)'; b.style.background = 'transparent'; });
  };
  ['calcInput', 'calcOutput', 'calcCache'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.addEventListener('input', update);
  });
}

function updateCalcResults() {
  const inp = document.getElementById('calcInput');
  const out = document.getElementById('calcOutput');
  const cache = document.getElementById('calcCache');
  if (!inp || !out || !cache) return;
  const usage = {
    inputM: parseFloat(inp.value),
    outputM: parseFloat(out.value),
    cacheHitRate: parseFloat(cache.value) / 100,
  };
  // pricing-models 数据从注入的 DATA 读
  const models = (typeof DATA !== 'undefined' && DATA['pricing-models']) || (typeof pricingModels !== 'undefined' ? pricingModels : null);
  if (!models) return;
  let results = calcAll(models, usage, 'GLM-5.2');
  // 模型过滤：勾选了模型时，只保留支持选中模型的套餐
  const checkedModels = [...document.querySelectorAll('#calcModelFilter input:checked')].map(cb => cb.value);
  if (checkedModels.length) {
    // 找出支持选中模型的 vendorId 集合
    const supportedVendorIds = new Set(plans.filter(p => (p.models || []).some(m => checkedModels.includes(m))).map(p => p.vendorId));
    results = results.filter(r => supportedVendorIds.has(r.vendorId || r.vendorName));
    // 给每个结果标注支持的选中模型
    results.forEach(r => {
      const vendorPlans = plans.filter(p => (p.vendorId === r.vendorId || p.vendor === r.vendorName));
      const supModels = [...new Set(vendorPlans.flatMap(p => p.models || []))].filter(m => checkedModels.includes(m));
      if (supModels.length) r.note = (r.note || '') + ' · 支持: ' + supModels.join('/');
    });
  }
  const el = document.getElementById('calcResults');
  if (!el) return;
  el.innerHTML = '<div style="padding:var(--sp-4);">' +
    '<h3 style="margin:0 0 var(--sp-4);font-size:15px;font-weight:700;">成本排序（从低到高）</h3>' +
    results.map((r, i) => {
      const precIcon = r.precision === 'exact' ? '✅' : (r.precision === 'estimate' ? '⚠️' : '❓');
      const statusBadge = r.status === 'throttled' ? ' <span style="color:var(--text-helper);font-size:11px;">⚠️会限流</span>' : '';
      const costStr = r.cost !== null ? '¥' + r.cost + '/月' : '未公开';
      return '<div style="display:flex;align-items:center;padding:var(--sp-3);border-bottom:1px solid var(--border-subtle);">' +
        '<span style="font-family:var(--mono);font-weight:700;color:var(--text-helper);width:24px;">' + (i + 1) + '</span>' +
        '<div style="flex:1;"><div style="font-weight:600;font-size:13px;">' + escapeHtml(r.vendorName) + ' · ' + escapeHtml(r.planName) + statusBadge + '</div>' +
        '<div style="font-size:11px;color:var(--text-helper);">' + precIcon + ' ' + escapeHtml(r.note || '') + '</div></div>' +
        '<span style="font-family:var(--mono);font-weight:700;font-size:15px;color:' + (r.cost !== null ? 'var(--accent)' : 'var(--text-placeholder)') + ';">' + costStr + '</span>' +
      '</div>';
    }).join('') +
  '</div>';
}

function renderModelRows(filtered) {
  const tbody = document.getElementById('plansTableBody');
  if (!tbody) return;
  // 展平所有模型 → 支持的套餐
  const modelMap = {};
  filtered.forEach(p => {
    (p.models || []).forEach(m => {
      if (!modelMap[m]) modelMap[m] = [];
      modelMap[m].push(p);
    });
  });
  // 按支持平台数降序，再按模型名
  const models = Object.keys(modelMap).sort((a, b) => {
    const d = modelMap[b].length - modelMap[a].length;
    return d !== 0 ? d : a.localeCompare(b);
  });
  tbody.innerHTML = models.map(m => {
    const ps = modelMap[m];
    const platforms = [...new Set(ps.map(p => p.vendor))];
    // 最便宜月订阅（排除 sold_out/deprecated）
    const monthly = ps.filter(p => p.type !== 'API 按量' && typeof p.monthlyPrice === 'number' && p.status !== 'sold_out' && p.status !== 'deprecated');
    const cheapM = monthly.sort((a, b) => a.monthlyPrice - b.monthlyPrice)[0];
    // 最便宜 API（按输入价）
    const api = ps.filter(p => p.type === 'API 按量' && typeof p.inputPrice === 'number');
    const cheapA = api.sort((a, b) => a.inputPrice - b.inputPrice)[0];
    // 去购买按钮：优先最便宜月订阅，没有则 API
    const buyPlan = cheapM || cheapA;
    const buyBtn = buyPlan
      ? '<a href="' + (buyPlan.action || '#') + '" target="_blank" rel="nofollow sponsored" class="btn btn-primary btn-sm">去购买 -></a>'
      : '<span class="badge">-</span>';
    return '<tr class="model-row" data-model="' + escapeHtml(m) + '" style="cursor:pointer;">' +
      '<td class="col-vendor"><div style="font-weight:600;font-size:13px;">' + escapeHtml(m) + '</div></td>' +
      '<td><span class="badge">' + platforms.length + ' 家</span> <span style="font-size:11px;color:var(--text-helper);">' + escapeHtml(platforms.join(' / ')) + '</span></td>' +
      '<td class="col-price">' + (cheapM ? '<span style="font-family:var(--mono);font-weight:700;color:var(--accent);">¥' + cheapM.monthlyPrice + '</span><div style="font-size:11px;color:var(--text-helper);">' + escapeHtml(cheapM.vendor + ' ' + cheapM.plan) + '</div>' : '<span style="color:var(--text-placeholder);">-</span>') + '</td>' +
      '<td class="col-price">' + (cheapA ? '<span style="font-family:var(--mono);font-weight:700;color:var(--accent);">¥' + cheapA.inputPrice + '/¥' + cheapA.outputPrice + '</span><div style="font-size:11px;color:var(--text-helper);">输入/输出 per M · ' + escapeHtml(cheapA.vendor) + '</div>' : '<span style="color:var(--text-placeholder);">-</span>') + '</td>' +
      '<td class="col-action">' + buyBtn + '</td>' +
    '</tr>';
  }).join('');
  // 绑定点击事件：行内展开/收起比价图
  tbody.querySelectorAll('.model-row').forEach(row => {
    row.addEventListener('click', e => {
      if (e.target.closest('a')) return;
      const modelName = row.dataset.model;
      const next = row.nextElementSibling;
      const isOpen = next && next.classList && next.classList.contains('model-chart-row');
      // 先关闭所有已展开的
      tbody.querySelectorAll('.model-chart-row').forEach(r => r.remove());
      tbody.querySelectorAll('.model-row').forEach(r => { r.style.background = ''; });
      // 如果当前行没展开过，则展开（点已展开的行 = 收起）
      if (!isOpen) {
        row.style.background = 'var(--grey-1)';
        compareState.selectedModel = modelName;
        const chartRow = document.createElement('tr');
        chartRow.className = 'model-chart-row';
        chartRow.innerHTML = '<td colspan="5" style="padding:0;background:var(--grey-1);"><div id="inlineModelChart" style="width:100%;height:280px;"></div></td>';
        row.parentNode.insertBefore(chartRow, row.nextSibling);
        renderModelChart(modelName, 'inlineModelChart');
      }
    });
  });
  // 默认展开第一个多平台模型（行内就地展开）
  const firstMulti = models.find(m => modelMap[m].length >= 2) || models[0];
  if (firstMulti) {
    const firstRow = tbody.querySelector('.model-row[data-model="' + CSS.escape(firstMulti) + '"]');
    if (firstRow) firstRow.click();
  }
}

// 单个模型各平台 TOKEN/元 柱状图（行内就地渲染）
function renderModelChart(modelName, chartId) {
  const chartDom = document.getElementById(chartId || 'inlineModelChart');
  if (!chartDom || typeof echarts === 'undefined') return;
  const existing = echarts.getInstanceByDom(chartDom);
  if (existing) existing.dispose();

  // 收集该模型所有套餐
  const ps = plans.filter(p => p.status !== 'deprecated' && (p.models || []).includes(modelName));
  // 计算 TOKEN/元（M）：1元能买多少 M token
  // API 按量：1/输出价；月订阅：从 tokenLimit 解析总 token ÷ 月费，或用 measuredMonthlyToken
  const parseTokenM = (p) => {
    if (typeof p.measuredMonthlyToken === 'number' && p.measuredMonthlyToken > 0) return p.measuredMonthlyToken;
    if (!p.tokenLimit) return null;
    const t = p.tokenLimit;
    // 匹配 "3500万 Tokens/月" "1亿 Tokens/月" "6.5亿" 等
    const m = t.match(/([\d.]+)\s*([亿万])\s*Tokens?/i) || t.match(/([\d.]+)\s*([亿万])/);
    if (!m) return null;
    let n = parseFloat(m[1]);
    if (m[2] === '亿') n *= 100;
    else if (m[2] === '万') n /= 100; // 万 token = 0.01M
    return n; // 单位 M
  };
  const items = ps.map(p => {
    let tpu, type, isEstimate = false;
    if (p.type === 'API 按量' && typeof p.outputPrice === 'number' && p.outputPrice > 0) {
      tpu = 1 / p.outputPrice; // 1元买多少M输出
      type = 'API按量';
    } else if (typeof p.monthlyPrice === 'number' && p.monthlyPrice > 0) {
      const totalM = parseTokenM(p);
      if (!totalM) return null;
      tpu = totalM / p.monthlyPrice; // 整池总额度÷月费（估算，多模型共享）
      type = '月订阅';
      isEstimate = true;
    } else return null;
    return { name: p.vendor + ' ' + p.plan, tpu: Math.round(tpu * 100) / 100, type, isEstimate, action: p.action, status: p.status };
  }).filter(Boolean).sort((a, b) => b.tpu - a.tpu); // 高→低，越高越划算

  if (!items.length) { card.style.display = 'none'; return; }
  const C = { text: '#525252', grid: '#e0e0e0', monthly: '#002fa7', api: '#737373', tooltipBg: '#0a0a0a', tooltipText: '#fafaf8' };
  const chart = echarts.init(chartDom);
  window._modelChart = chart;
  chart.setOption({
    animationDuration: 400,
    grid: { left: 60, right: 30, top: 30, bottom: 40 },
    tooltip: { trigger: 'item', backgroundColor: C.tooltipBg, textStyle: { color: C.tooltipText, fontSize: 12 },
      formatter: p => { const d = items[p.dataIndex]; return '<b>' + d.name + '</b><div style="font-size:11px;color:#d4d4d2;margin-top:3px;">' + d.type + ' · <b>' + d.tpu + ' M/元</b>' + (d.isEstimate ? '（整池额度估算）' : '') + '</div><div style="font-size:11px;color:#d4d4d2;">1元 = ' + d.tpu + 'M token</div>'; } },
    legend: { data: ['月订阅', 'API按量'], bottom: 0, textStyle: { color: C.text, fontSize: 11 }, itemWidth: 10, itemHeight: 10 },
    xAxis: { type: 'category', data: items.map(i => i.name + (i.isEstimate ? ' *' : '')), axisLabel: { color: C.text, fontSize: 10, rotate: 20, interval: 0 }, axisLine: { lineStyle: { color: C.grid } } },
    yAxis: { type: 'value', name: 'TOKEN/元 (M)', nameTextStyle: { color: C.text, fontSize: 11 }, axisLabel: { color: C.text, formatter: v => v + 'M' }, splitLine: { lineStyle: { color: C.grid, type: 'dashed' } } },
    series: [{
      type: 'bar', barWidth: '55%',
      itemStyle: { color: p => items[p.dataIndex].type === '月订阅' ? C.monthly : C.api },
      label: { show: true, position: 'top', color: C.text, fontSize: 11, fontWeight: 700, formatter: p => items[p.dataIndex].tpu + 'M' },
      data: items.map(i => i.tpu),
    }],
    graphic: [{ type: 'text', left: 0, top: 0, silent: true, z: 100, style: { text: '* 月订阅按整池额度÷月费估算（多模型共享，非单一模型精确值）· 越高越划算', fill: C.text, fontSize: 10 } }],
  });
  window.addEventListener('resize', () => chart.resize());
}

function renderCompareCards(filtered) {
  const cardsView = document.getElementById('plansCardsView');
  if (!cardsView) return;
    cardsView.innerHTML = filtered.map(p => {
      const price = formatPrice(p.monthlyPrice, p.currency || '¥');
      const measured = p.measuredMonthlyToken ? p.measuredMonthlyToken + 'M' : '—';
      const tpu = (typeof p.monthlyPrice === 'number' && typeof p.measuredMonthlyToken === 'number' && p.monthlyPrice > 0)
        ? (p.measuredMonthlyToken / p.monthlyPrice).toFixed(2) : '—';
      const models = (p.models || []).join(', ');
      return '<div class="plan-card-item">' +
        '<div class="plan-card-header"><div><div class="plan-card-vendor">' + escapeHtml(p.vendor) + '</div><div class="plan-card-plan">' + escapeHtml(p.plan) + ' · ' + escapeHtml(p.type) + '</div></div><div class="plan-card-price">' + price + '</div></div>' +
        renderStars(p.rating) +
        '<div style="display:grid;grid-template-columns:1fr 1fr;gap:var(--sp-3) var(--sp-5);font-size:12px;padding:var(--sp-3) 0;border-top:1px solid var(--border-subtle);margin-top:var(--sp-3);">' +
          '<div><span style="color:var(--text-helper);font-size:10px;">月Token</span><br><b>' + measured + '</b></div>' +
          '<div><span style="color:var(--text-helper);font-size:10px;">每元Token</span><br><b>' + tpu + ' M</b></div>' +
          '<div><span style="color:var(--text-helper);font-size:10px;">模型</span><br>' + escapeHtml(models) + '</div>' +
          '<div><span style="color:var(--text-helper);font-size:10px;">标签</span><br>' + renderTagsInline(p.tags) + '</div>' +
        '</div>' +
        '<div style="margin-top:var(--sp-4);text-align:right;"><a href="' + (p.action || '#') + '" target="_blank" rel="nofollow sponsored" class="btn btn-primary btn-sm">去购买 →</a></div>' +
      '</div>';
    }).join('');
}

function renderChart() {
  if (typeof echarts === 'undefined') return;
  const dom = document.getElementById('priceVsTokenChart');
  if (!dom || dom.offsetParent === null) return;
  const existing = echarts.getInstanceByDom(dom);
  if (existing) existing.dispose();

  const mode = compareState.columnMode;
  const isApi = mode === 'api';
  const isModel = mode === 'model';

  // 更新标题
  const titleEl = document.getElementById('chartTitle');
  const subEl = document.getElementById('chartSubtitle');
  dom.style.height = '';
  if (titleEl) titleEl.textContent = isModel ? '模型覆盖度 vs 最便宜月订阅价' : (isApi ? '输入价 vs 输出价' : '月费 vs 月Token额度');
  if (subEl) subEl.textContent = isModel ? '越靠右下越优（覆盖广 + 便宜）' : (isApi ? '越靠左下越便宜（¥/百万token）' : '越靠左下越便宜（高性价比区）');

  // 瑞士风配色
  const C = {
    text: '#525252', grid: '#e0e0e0', accent: '#002fa7', accentSoft: 'rgba(0,47,167,0.1)',
    tooltipBg: '#0a0a0a', tooltipText: '#fafaf8', tooltipBorder: '#737373',
    cheap: 'rgba(0,47,167,0.08)', expensive: 'rgba(115,115,115,0.05)',
  };

  if (isModel) {
    // 按模型散点图：X=支持平台数, Y=最便宜月订阅价
    const modelMap = {};
    plans.filter(p => p.status !== 'deprecated').forEach(p => (p.models||[]).forEach(m => {
      if (!modelMap[m]) modelMap[m] = [];
      modelMap[m].push(p);
    }));
    const items = Object.entries(modelMap).map(([m, ps]) => {
      const platforms = [...new Set(ps.map(p => p.vendor))];
      const monthly = ps.filter(p => p.type !== 'API 按量' && typeof p.monthlyPrice === 'number' && p.status !== 'sold_out');
      const cheap = monthly.sort((a,b) => a.monthlyPrice - b.monthlyPrice)[0];
      return cheap ? { model: m, platformCount: platforms.length, price: cheap.monthlyPrice, vendor: cheap.vendor, plan: cheap.plan } : null;
    }).filter(Boolean);
    if (!items.length) return;
    const chart = echarts.init(dom);
    window._chart = chart;
    const allP = items.map(i => i.price);
    const minP = Math.min(...allP), maxP = Math.max(...allP);
    chart.setOption({
      animationDuration: 400,
      grid: { left: 70, right: 100, top: 40, bottom: 50 },
      tooltip: { trigger: 'item', backgroundColor: C.tooltipBg, borderColor: C.tooltipBorder, textStyle: { color: C.tooltipText, fontSize: 13 },
        formatter: p => { const d = p.data; return '<b>' + d.model + '</b><div style="font-size:12px;color:#d4d4d2;margin-top:4px;">支持 ' + d.platformCount + ' 平台 · 最便宜 ¥' + d.price + '/月</div><div style="font-size:11px;color:#d4d4d2;">' + d.vendor + ' ' + d.plan + '</div>'; } },
      xAxis: { type: 'value', name: '支持平台数', nameTextStyle: { color: C.text, fontSize: 11 }, min: 0.5, max: 3.5, axisLabel: { color: C.text, formatter: v => v + ' 家' }, splitLine: { lineStyle: { color: C.grid, type: 'dashed' } } },
      yAxis: { type: 'log', name: '最便宜月订阅 (¥)', nameTextStyle: { color: C.text, fontSize: 11 }, min: minP * 0.5, max: maxP * 2, axisLabel: { color: C.text, formatter: v => '¥' + v }, splitLine: { lineStyle: { color: C.grid, type: 'dashed' } } },
      series: [{
        type: 'scatter', symbolSize: 16, color: C.accent,
        label: { show: true, position: 'right', distance: 8, color: C.text, fontSize: 10, fontWeight: 600, formatter: p => p.data.model, labelLayout: { hideOverlap: true } },
        itemStyle: { color: C.accent, borderColor: '#fff', borderWidth: 1.5 },
        data: items.map(i => ({ value: [i.platformCount, i.price], model: i.model, platformCount: i.platformCount, price: i.price, vendor: i.vendor, plan: i.plan })),
        emphasis: { scale: 1.2 },
      }],
      graphic: [
        { type: 'text', right: 40, bottom: 20, silent: true, style: { text: '最优：覆盖广 + 便宜', fill: C.accent, fontSize: 11, fontWeight: 700 } }
      ],
    });
    window.addEventListener('resize', () => chart.resize());
    return;
  }

  if (isApi) {
    // API 按量图：X=输入价, Y=输出价
    const items = plans.filter(p => p.status === 'active' && p.type === 'API 按量' && typeof p.inputPrice === 'number' && typeof p.outputPrice === 'number');
    if (!items.length) return;
    const chart = echarts.init(dom);
    window._chart = chart;
    const vendors = [...new Set(items.map(p => p.vendor))];
    const series = vendors.map(v => {
      const data = items.filter(p => p.vendor === v).map(p => ({
        value: [p.inputPrice, p.outputPrice],
        plan: p.plan, vendor: p.vendor, input: p.inputPrice, output: p.outputPrice, cache: p.cachePrice,
      }));
      return { name: v, type: 'scatter', color: vendorColor(v), symbolSize: 14,
        label: { show: true, position: 'right', distance: 6, color: C.text, fontSize: 10, fontWeight: 600, formatter: p => p.data.plan, labelLayout: { hideOverlap: true } },
        itemStyle: { color: vendorColor(v), borderColor: '#fff', borderWidth: 1.5 },
        data };
    });
    const allX = items.map(p => p.inputPrice), allY = items.map(p => p.outputPrice);
    chart.setOption({
      animationDuration: 400,
      grid: { left: 60, right: 40, top: 40, bottom: 50 },
      tooltip: { trigger: 'item', backgroundColor: C.tooltipBg, borderColor: C.tooltipBorder, textStyle: { color: C.tooltipText, fontSize: 13 },
        formatter: p => { const d = p.data; return '<div style="min-width:160px"><b>' + d.vendor + ' ' + d.plan + '</b><div style="font-size:12px;color:#d4d4d2;margin-top:4px;">输入: <b>¥' + d.input + '/M</b> | 输出: <b>¥' + d.output + '/M</b></div><div style="font-size:12px;color:#d4d4d2;">缓存命中: <b>¥' + d.cache + '/M</b></div></div>'; } },
      xAxis: { type: 'log', name: '输入价 (¥/M)', nameTextStyle: { color: C.text, fontSize: 11 }, min: 0.5, max: 12, axisLabel: { color: C.text, formatter: v => '¥' + v }, splitLine: { lineStyle: { color: C.grid, type: 'dashed' } } },
      yAxis: { type: 'log', name: '输出价 (¥/M)', nameTextStyle: { color: C.text, fontSize: 11 }, min: 1, max: 40, axisLabel: { color: C.text, formatter: v => '¥' + v }, splitLine: { lineStyle: { color: C.grid, type: 'dashed' } } },
      series,
    });
    window.addEventListener('resize', () => chart.resize());
    return;
  }

  // 月订阅图（默认 + all 模式）
  const items = plans.filter(p => p.status === 'active' && typeof p.monthlyPrice === 'number' && typeof p.measuredMonthlyToken === 'number' && p.monthlyPrice > 0);
  if (!items.length) return;
  const chart = echarts.init(dom);
  window._chart = chart;
  const vendorsInData = [...new Set(items.map(p => p.vendor))];
  const allP = items.map(p => p.monthlyPrice), allT = items.map(p => p.measuredMonthlyToken);
  const minP = Math.min(...allP), maxP = Math.max(...allP);
  const minT = Math.min(...allT), maxT = Math.max(...allT);

  const series = vendorsInData.map(v => {
    const data = items.filter(p => p.vendor === v).sort((a, b) => a.monthlyPrice - b.monthlyPrice).map(p => ({
      value: [p.monthlyPrice, p.measuredMonthlyToken],
      plan: p.plan, vendor: p.vendor, type: p.type, price: p.monthlyPrice, token: p.measuredMonthlyToken,
      tpu: (p.measuredMonthlyToken / p.monthlyPrice).toFixed(2)
    }));
    return {
      name: v, type: 'line', color: vendorColor(v), symbol: 'circle', symbolSize: 14, showSymbol: true,
      lineStyle: { width: data.length > 1 ? 1.5 : 0, opacity: data.length > 1 ? 0.3 : 0 },
      label: { show: true, position: 'right', distance: 6, color: C.text, fontSize: 10, fontWeight: 600, formatter: p => p.data.plan || '', labelLayout: { hideOverlap: true } },
      itemStyle: { color: vendorColor(v), borderColor: '#fff', borderWidth: 1.5 },
      data, emphasis: { scale: 1.15 }
    };
  });

  const medP = [...allP].sort((a, b) => a - b)[Math.floor(allP.length / 2)];
  const medT = [...allT].sort((a, b) => a - b)[Math.floor(allT.length / 2)];

  const helper = {
    type: 'scatter', silent: true, animation: false, data: [], symbolSize: 0,
    markArea: { silent: true, label: { show: false }, data: [
      [{ itemStyle: { color: C.cheap }, xAxis: minP * 0.7, yAxis: minT * 0.5 }, { xAxis: medP, yAxis: maxT * 1.2 }],
      [{ itemStyle: { color: C.expensive }, xAxis: medP, yAxis: minT * 0.5 }, { xAxis: maxP * 1.3, yAxis: medT }]
    ]},
    markLine: { silent: true, symbol: 'none', label: { show: false }, data: [
      { xAxis: medP, lineStyle: { color: 'rgba(115,115,115,0.25)', type: 'dashed' } },
      { yAxis: medT, lineStyle: { color: 'rgba(115,115,115,0.25)', type: 'dashed' } }
    ]}
  };

  chart.setOption({
    animationDuration: 400,
    grid: { left: 70, right: 40, top: 40, bottom: 50 },
    tooltip: { trigger: 'item', backgroundColor: C.tooltipBg, borderColor: C.tooltipBorder, textStyle: { color: C.tooltipText, fontSize: 13 },
      formatter: p => { const d = p.data; return '<div style="min-width:160px"><b>' + d.vendor + ' ' + d.plan + '</b><div style="font-size:12px;color:#d4d4d2;margin-top:4px;">月费: <b>¥' + d.price + '</b> | 月Token: <b>' + d.token + 'M</b></div><div style="font-size:12px;color:#d4d4d2;">每元Token: <b>' + d.tpu + ' M</b></div></div>'; } },
    legend: { top: 0, left: 0, itemWidth: 10, itemHeight: 10, icon: 'circle', textStyle: { color: C.text, fontSize: 11, fontWeight: 600 } },
    graphic: [
      { type: 'text', left: 80, top: 32, silent: true, style: { text: '高性价比', fill: C.accent, fontSize: 11, fontWeight: 700 } },
      { type: 'text', right: 40, bottom: 20, silent: true, style: { text: '低性价比', fill: C.text, fontSize: 11, fontWeight: 700 } }
    ],
    xAxis: { type: 'log', logBase: 2, min: minP * 0.75, max: maxP * 1.12, name: '月费 (¥)', nameTextStyle: { color: C.text, fontSize: 11, fontWeight: 700 }, axisLabel: { color: C.text, fontSize: 11, fontWeight: 700, formatter: v => '¥' + (Number.isInteger(v) ? v : v.toFixed(0)) }, splitLine: { show: true, lineStyle: { color: C.grid, type: 'dashed' } } },
    yAxis: { type: 'log', logBase: 10, min: minT * 0.65, max: maxT * 1.18, name: '月Token额度', nameTextStyle: { color: C.text, fontSize: 11, fontWeight: 700 }, axisLabel: { color: C.text, formatter: v => v >= 1000 ? (v / 1000).toFixed(1) + 'B' : v + 'M' }, splitLine: { lineStyle: { color: C.grid, type: 'dashed' } } },
    series: [helper].concat(series)
  });
  window.addEventListener('resize', () => chart.resize());
}