// ============================================================
// Tab 2: 对比（散点图 + 筛选条 + 表格 + 移动端卡片）
// ============================================================
const compareState = {
  filters: { types: new Set(), tags: new Set(), models: new Set(), monthlyPriceMax: null, search: '' },
  sort: { key: null, dir: 'asc' },
  columnsExpanded: false
};

function renderCompare() {
  const body = document.getElementById('compare-body');
  body.innerHTML = renderChartSection() + renderTableSection();
  bindCompareFilters();
  renderCompareTable();
  setTimeout(renderChart, 200);
}

function renderChartSection() {
  return '<section class="section-sm">' +
    '<div class="container">' +
      '<div class="section-header" style="margin-bottom:var(--space-4);">' +
        '<span class="section-eyebrow">CHART</span>' +
        '<h2 class="section-title">价格 vs Token 上限</h2>' +
        '<p class="section-subtitle">横轴月费，纵轴月Token。绿色区域为高性价比区。</p>' +
      '</div>' +
      '<div class="chart-card"><div class="chart-container" id="priceVsTokenChart"></div></div>' +
    '</div></section>';
}

function renderTableSection() {
  return '<section class="section-sm">' +
    '<div class="container">' +
      '<div class="section-header" style="display:flex;justify-content:space-between;align-items:flex-end;flex-wrap:wrap;gap:var(--space-3);">' +
        '<div>' +
          '<span class="section-eyebrow">FULL COMPARISON</span>' +
          '<h2 class="section-title">完整套餐对比表</h2>' +
          '<p class="section-subtitle">点击标签筛选，点击展开看额外列。</p>' +
        '</div>' +
        '<button class="table-toggle-btn" id="toggleColumnsBtn">展开全部列</button>' +
      '</div>' +
      '<div id="compareFilterBar"></div>' +
      '<div class="table-wrap"><table class="data-table"><thead><tr>' +
        '<th>平台</th><th>套餐</th><th>类型</th><th>评分</th><th>月费</th>' +
        '<th class="col-extra">首月</th><th class="col-extra">月请求</th>' +
        '<th>实测月Token</th><th>每元Token</th>' +
        '<th class="col-extra">1M价</th><th>支持模型</th><th>标签</th><th>优惠购买</th>' +
      '</tr></thead><tbody id="plansTableBody"></tbody></table></div>' +
      '<div class="plan-cards-view" id="plansCardsView"></div>' +
    '</div></section>';
}

function renderCompareFilterBar() {
  const filterable = plans.filter(p => p.status !== 'deprecated');
  const types = [...new Set(filterable.map(p => p.type))].sort();
  const allTags = new Set();
  filterable.forEach(p => (p.tags || []).forEach(t => allTags.add(t)));
  const tags = [...allTags].sort();

  const typeChips = types.map(t => '<button class="filter-chip" data-filter-type="types" data-filter-value="' + escapeHtml(t) + '">' + escapeHtml(t) + '</button>').join('');
  const tagChips = tags.map(t => '<button class="filter-chip" data-filter-type="tags" data-filter-value="' + escapeHtml(t) + '">' + escapeHtml(t) + '</button>').join('');

  return '<div class="filter-bar">' +
    '<select class="filter-select" id="sortSelect">' +
      '<option value="">默认排序</option>' +
      '<option value="monthlyPrice-asc">月费 低-高</option>' +
      '<option value="monthlyPrice-desc">月费 高-低</option>' +
      '<option value="rating-desc">评分 高-低</option>' +
      '<option value="measuredMonthlyToken-desc">月Token 多-少</option>' +
      '<option value="tokensPerYuan-desc">性价比 高-低</option>' +
    '</select>' +
    '<input type="text" class="filter-select" id="searchInput" placeholder="搜索平台/套餐..." style="min-width:160px;">' +
    '<button class="filter-chip" id="resetBtn">重置</button>' +
    '<span class="filter-stats">显示 <strong id="filterCount">0</strong> / ' + filterable.length + ' 个套餐</span>' +
  '</div>' +
  (typeChips ? '<div class="filter-bar"><span style="font-size:11px;font-weight:700;color:var(--text-muted);">类型:</span>' + typeChips + '</div>' : '') +
  (tagChips ? '<div class="filter-bar"><span style="font-size:11px;font-weight:700;color:var(--text-muted);">标签:</span>' + tagChips + '</div>' : '');
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
    if (f.types.size && !f.types.has(p.type)) return false;
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

  if (tbody) {
    tbody.innerHTML = filtered.map(p => {
      const price = formatPrice(p.monthlyPrice, p.currency || '¥');
      const firstPrice = p.firstMonthPrice ? formatPrice(p.firstMonthPrice, p.currency || '¥') : '—';
      const measured = p.measuredMonthlyToken ? p.measuredMonthlyToken + 'M' : '—';
      const tpu = (typeof p.monthlyPrice === 'number' && typeof p.measuredMonthlyToken === 'number' && p.monthlyPrice > 0)
        ? (p.measuredMonthlyToken / p.monthlyPrice).toFixed(2) : '—';
      const pricePerM = (typeof p.monthlyPrice === 'number' && typeof p.measuredMonthlyToken === 'number' && p.measuredMonthlyToken > 0)
        ? '¥' + (p.monthlyPrice / p.measuredMonthlyToken).toFixed(2) : '—';
      const models = (p.models || []).slice(0, 4).join(', ') + ((p.models || []).length > 4 ? '...' : '');
      const statusBadge = p.status === 'paused' ? '<span class="badge badge-warning">暂停</span>' :
                          p.status === 'sold_out' ? '<span class="badge">售罄</span>' : '';
      return '<tr>' +
        '<td class="col-vendor">' + escapeHtml(p.vendor) + (statusBadge ? ' ' + statusBadge : '') + '</td>' +
        '<td>' + escapeHtml(p.plan) + '</td>' +
        '<td><span class="badge">' + escapeHtml(p.type) + '</span></td>' +
        '<td>' + renderStars(p.rating) + '</td>' +
        '<td class="col-price">' + price + '</td>' +
        '<td class="col-price col-extra col-hidden" style="color:var(--color-warning);">' + firstPrice + '</td>' +
        '<td class="col-extra col-hidden">' + formatNumber(p.monthlyRequests) + '</td>' +
        '<td class="col-price">' + measured + '</td>' +
        '<td class="col-price" style="color:var(--accent);">' + tpu + '</td>' +
        '<td class="col-extra col-hidden" style="font-size:12px;color:var(--text-tertiary);">' + pricePerM + '</td>' +
        '<td><span style="font-size:12px;">' + escapeHtml(models) + '</span></td>' +
        '<td>' + renderTagsInline(p.tags) + '</td>' +
        '<td class="col-action"><a href="' + (p.action || '#') + '" target="_blank" rel="nofollow sponsored" class="btn btn-primary btn-sm">优惠购买</a></td>' +
      '</tr>';
    }).join('');
  }

  if (cardsView) {
    cardsView.innerHTML = filtered.map(p => {
      const price = formatPrice(p.monthlyPrice, p.currency || '¥');
      const measured = p.measuredMonthlyToken ? p.measuredMonthlyToken + 'M' : '—';
      const tpu = (typeof p.monthlyPrice === 'number' && typeof p.measuredMonthlyToken === 'number' && p.monthlyPrice > 0)
        ? (p.measuredMonthlyToken / p.monthlyPrice).toFixed(2) : '—';
      const models = (p.models || []).join(', ');
      return '<div class="plan-card-item">' +
        '<div class="plan-card-header"><div><div class="plan-card-vendor">' + escapeHtml(p.vendor) + '</div><div class="plan-card-plan">' + escapeHtml(p.plan) + ' · ' + escapeHtml(p.type) + '</div></div><div class="plan-card-price">' + price + '</div></div>' +
        renderStars(p.rating) +
        '<div style="display:grid;grid-template-columns:1fr 1fr;gap:var(--space-2) var(--space-4);font-size:12px;padding:var(--space-2) 0;border-top:1px solid var(--border-subtle);margin-top:var(--space-2);">' +
          '<div><span style="color:var(--text-muted);font-size:10px;">月Token</span><br><b>' + measured + '</b></div>' +
          '<div><span style="color:var(--text-muted);font-size:10px;">每元Token</span><br><b>' + tpu + ' M</b></div>' +
          '<div><span style="color:var(--text-muted);font-size:10px;">模型</span><br>' + escapeHtml(models) + '</div>' +
          '<div><span style="color:var(--text-muted);font-size:10px;">标签</span><br>' + renderTagsInline(p.tags) + '</div>' +
        '</div>' +
        '<div style="margin-top:var(--space-3);text-align:right;"><a href="' + (p.action || '#') + '" target="_blank" rel="nofollow sponsored" class="btn btn-primary btn-sm">优惠购买 →</a></div>' +
      '</div>';
    }).join('');
  }
}

function renderChart() {
  if (typeof echarts === 'undefined') return;
  const dom = document.getElementById('priceVsTokenChart');
  if (!dom || dom.offsetParent === null) return;
  const existing = echarts.getInstanceByDom(dom);
  if (existing) existing.dispose();

  const items = plans.filter(p => p.status === 'active' && typeof p.monthlyPrice === 'number' && typeof p.measuredMonthlyToken === 'number');
  if (!items.length) return;
  const chart = echarts.init(dom);
  window._chart = chart;

  const vendorsInData = [...new Set(items.map(p => p.vendor))];
  const allP = items.map(p => p.monthlyPrice), allT = items.map(p => p.measuredMonthlyToken);
  const minP = Math.min(...allP), maxP = Math.max(...allP);
  const minT = Math.min(...allT), maxT = Math.max(...allT);
  const sP = [...allP].sort((a, b) => a - b), sT = [...allT].sort((a, b) => a - b);
  const medP = sP[Math.floor(sP.length / 2)], medT = sT[Math.floor(sT.length / 2)];
  const tpuVals = items.map(p => p.measuredMonthlyToken / p.monthlyPrice).sort((a, b) => a - b);
  const medTPU = tpuVals[Math.floor(tpuVals.length / 2)];

  const series = vendorsInData.map(v => {
    const data = items.filter(p => p.vendor === v).sort((a, b) => a.monthlyPrice - b.monthlyPrice).map(p => ({
      value: [p.monthlyPrice, p.measuredMonthlyToken],
      plan: p.plan, vendor: p.vendor, type: p.type, price: p.monthlyPrice, token: p.measuredMonthlyToken,
      tpu: (p.measuredMonthlyToken / p.monthlyPrice).toFixed(2)
    }));
    return {
      name: v, type: 'line', color: vendorColor(v), symbol: 'circle', symbolSize: 14, showSymbol: true,
      lineStyle: { width: data.length > 1 ? 1.5 : 0, opacity: data.length > 1 ? 0.3 : 0 },
      label: { show: true, position: 'right', distance: 6, color: '#94a3b8', fontSize: 10, fontWeight: 600, formatter: p => p.data.plan || '', labelLayout: { hideOverlap: true } },
      itemStyle: { color: vendorColor(v), borderColor: 'rgba(255,255,255,0.95)', borderWidth: 1.5, shadowBlur: 12, shadowColor: 'rgba(0,0,0,0.12)' },
      data, emphasis: { scale: 1.15 }
    };
  });

  const helper = {
    type: 'scatter', silent: true, animation: false, data: [], symbolSize: 0, tooltip: { show: false }, itemStyle: { opacity: 0 },
    markArea: { silent: true, label: { show: false }, data: [
      [{ itemStyle: { color: 'rgba(16,185,129,0.12)' }, xAxis: minP * 0.7, yAxis: minP * 0.7 * medTPU }, { xAxis: medP, yAxis: maxT * 1.2 }],
      [{ itemStyle: { color: 'rgba(16,185,129,0.06)' }, xAxis: medP, yAxis: medP * medTPU }, { xAxis: maxP * 1.3, yAxis: maxT * 1.2 }],
      [{ itemStyle: { color: 'rgba(148,163,184,0.04)' }, xAxis: minP * 0.7, yAxis: minT * 0.4 }, { xAxis: medP, yAxis: medP * medTPU }],
      [{ itemStyle: { color: 'rgba(239,68,68,0.08)' }, xAxis: medP, yAxis: minT * 0.4 }, { xAxis: maxP * 1.3, yAxis: medP * medTPU }]
    ]},
    markLine: { silent: true, symbol: 'none', label: { show: false }, data: [
      { xAxis: medP, lineStyle: { color: 'rgba(148,163,184,0.25)', type: 'dashed' } },
      { yAxis: medT, lineStyle: { color: 'rgba(148,163,184,0.25)', type: 'dashed' } }
    ]}
  };

  chart.setOption({
    animationDuration: 400,
    grid: { left: 90, right: 40, top: 60, bottom: 60 },
    tooltip: { trigger: 'item', backgroundColor: 'rgba(15,23,42,0.96)', borderColor: 'rgba(148,163,184,0.2)', textStyle: { color: '#f1f5f9', fontSize: 13 },
      formatter: p => { const d = p.data; return '<div style="min-width:180px"><div style="font-size:14px;font-weight:800;margin-bottom:4px;">' + d.vendor + ' ' + d.plan + '</div><div style="font-size:12px;line-height:1.7;color:#cbd5e1;"><div>类型: ' + d.type + '</div><div>月费: <b>' + d.price + '</b> | 月Token: <b>' + d.token + 'M</b></div><div>每元Token: <b>' + d.tpu + ' M</b></div></div></div>'; } },
    legend: { top: 0, left: 0, itemWidth: 10, itemHeight: 10, icon: 'circle', textStyle: { color: '#94a3b8', fontSize: 11, fontWeight: 600 } },
    graphic: [
      { type: 'text', left: 100, top: 40, silent: true, style: { text: '高性价比', fill: '#10b981', fontSize: 12, fontWeight: 700 } },
      { type: 'text', right: 40, bottom: 24, silent: true, style: { text: '低性价比', fill: '#ef4444', fontSize: 11, fontWeight: 700 } }
    ],
    xAxis: { type: 'log', logBase: 2, min: minP * 0.75, max: maxP * 1.12, name: '月费', nameTextStyle: { color: '#94a3b8', fontSize: 11, fontWeight: 700 }, axisLabel: { color: '#94a3b8', fontSize: 11, fontWeight: 700, formatter: v => '¥' + (Number.isInteger(v) ? v : v.toFixed(0)) }, splitLine: { show: true, lineStyle: { color: 'rgba(148,163,184,0.1)', type: 'dashed' } } },
    yAxis: { type: 'log', logBase: 10, min: minT * 0.65, max: maxT * 1.18, name: '月Token上限', nameTextStyle: { color: '#94a3b8', fontSize: 11, fontWeight: 700 }, axisLabel: { color: '#94a3b8', formatter: v => v >= 1000 ? (v / 1000).toFixed(1) + 'B' : v + 'M' }, splitLine: { lineStyle: { color: 'rgba(148,163,184,0.1)', type: 'dashed' } } },
    series: [helper].concat(series)
  });
  window.addEventListener('resize', () => chart.resize());
}