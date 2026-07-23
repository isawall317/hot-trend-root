// ============================================================
// Tab 2: 浏览（筛选栏 + 工具组合卡片网格 + 搜索）
// ============================================================
const browseState = {
  filters: { scenarios: new Set(), tags: new Set(), search: '' },
  sort: { key: null, dir: 'asc' }
};

function renderBrowse() {
  const body = document.getElementById('browse-body');
  body.innerHTML = renderBrowseSection();
  bindBrowseFilters();
  renderComboCards();
}

function renderBrowseSection() {
  return '<section class="section-sm">' +
    '<div class="container">' +
      '<div class="section-header" style="display:flex;justify-content:space-between;align-items:flex-end;flex-wrap:wrap;gap:var(--space-3);">' +
        '<div>' +
          '<span class="section-eyebrow">BROWSE ALL</span>' +
          '<h2 class="section-title">全部工具组合</h2>' +
          '<p class="section-subtitle">点击分类筛选，搜索框输入关键词。找到适合你的工具搭配。</p>' +
        '</div>' +
      '</div>' +
      '<div id="browseFilterBar"></div>' +
      '<div class="combo-grid" id="comboGrid"></div>' +
    '</div></section>';
}

function renderBrowseFilterBar() {
  const scenarios = [...new Set(combos.map(c => c.scenario))].sort();
  const allTags = new Set();
  combos.forEach(c => (c.tags || []).forEach(t => allTags.add(t)));
  const tags = [...allTags].sort();

  const scChips = scenarios.map(s => '<button class="filter-chip" data-filter-type="scenarios" data-filter-value="' + escapeHtml(s) + '">' + scenarioLabel(s) + '</button>').join('');
  const tagChips = tags.map(t => '<button class="filter-chip" data-filter-type="tags" data-filter-value="' + escapeHtml(t) + '">' + escapeHtml(t) + '</button>').join('');

  return '<div class="filter-bar">' +
    '<select class="filter-select" id="sortSelect">' +
      '<option value="">默认排序</option>' +
      '<option value="rating-desc">评分 高-低</option>' +
      '<option value="difficulty-asc">难度 低-高</option>' +
      '<option value="addedAt-desc">最新收录</option>' +
    '</select>' +
    '<input type="text" class="filter-select" id="searchInput" placeholder="搜索工具/组合名..." style="min-width:200px;">' +
    '<button class="filter-chip" id="resetBtn">重置</button>' +
    '<span class="filter-stats">显示 <strong id="filterCount">0</strong> / ' + combos.length + ' 套组合</span>' +
  '</div>' +
  (scChips ? '<div class="filter-bar"><span style="font-size:11px;font-weight:700;color:var(--text-muted);">场景:</span>' + scChips + '</div>' : '') +
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

function bindBrowseFilters() {
  const fm = document.getElementById('browseFilterBar');
  if (!fm) return;
  fm.innerHTML = renderBrowseFilterBar();

  const hashFilter = parseHashFilter();
  if (hashFilter) {
    if (hashFilter.scenario) browseState.filters.scenarios.add(hashFilter.scenario);
    if (hashFilter.tag) browseState.filters.tags.add(hashFilter.tag);
    if (hashFilter.search) {
      browseState.filters.search = hashFilter.search.toLowerCase();
      const si = document.getElementById('searchInput');
      if (si) si.value = hashFilter.search;
    }
  }
  syncBrowseFilterUI();

  fm.querySelectorAll('.filter-chip[data-filter-type]').forEach(chip => {
    chip.addEventListener('click', () => {
      const type = chip.dataset.filterType;
      const value = chip.dataset.filterValue;
      const set = browseState.filters[type];
      if (set.has(value)) set.delete(value); else set.add(value);
      syncBrowseFilterUI();
      renderComboCards();
    });
  });

  const reset = document.getElementById('resetBtn');
  if (reset) reset.addEventListener('click', () => {
    browseState.filters.scenarios.clear();
    browseState.filters.tags.clear();
    browseState.filters.search = '';
    browseState.sort = { key: null, dir: 'asc' };
    const ss = document.getElementById('sortSelect'); if (ss) ss.value = '';
    const si = document.getElementById('searchInput'); if (si) si.value = '';
    syncBrowseFilterUI();
    renderComboCards();
  });

  const ss = document.getElementById('sortSelect');
  if (ss) ss.addEventListener('change', () => {
    const val = ss.value;
    if (!val) browseState.sort = { key: null, dir: 'asc' };
    else { const [k, d] = val.split('-'); browseState.sort = { key: k, dir: d }; }
    renderComboCards();
  });

  const si = document.getElementById('searchInput');
  if (si) si.addEventListener('input', () => {
    browseState.filters.search = si.value.trim().toLowerCase();
    renderComboCards();
  });
}

function syncBrowseFilterUI() {
  document.querySelectorAll('.filter-chip[data-filter-type]').forEach(chip => {
    const type = chip.dataset.filterType;
    const value = chip.dataset.filterValue;
    const active = browseState.filters[type] && browseState.filters[type].has(value);
    chip.classList.toggle('active', !!active);
  });
}

function filterCombos() {
  const f = browseState.filters;
  let result = combos.filter(c => {
    if (f.scenarios.size && !f.scenarios.has(c.scenario)) return false;
    if (f.tags.size && !(c.tags || []).some(t => f.tags.has(t))) return false;
    if (f.search) {
      const hay = (c.name + ' ' + c.description + ' ' + (c.tags || []).join(' ') + ' ' + (c.tools || []).map(t => t.name + ' ' + t.role).join(' ')).toLowerCase();
      if (!hay.includes(f.search)) return false;
    }
    return true;
  });
  const { key, dir } = browseState.sort;
  if (key) {
    result.sort((a, b) => {
      if (key === 'difficulty') {
        const order = { '入门': 1, '进阶': 2, '专家': 3 };
        const aVal = order[a.difficulty] || 2, bVal = order[b.difficulty] || 2;
        return dir === 'asc' ? aVal - bVal : bVal - aVal;
      }
      if (key === 'addedAt') {
        return dir === 'asc' ? String(a.addedAt).localeCompare(String(b.addedAt)) : String(b.addedAt).localeCompare(String(a.addedAt));
      }
      const av = a[key], bv = b[key];
      const aNum = typeof av === 'number' ? av : 0;
      const bNum = typeof bv === 'number' ? bv : 0;
      return dir === 'asc' ? aNum - bNum : bNum - aNum;
    });
  }
  return result;
}

function renderToolChain(tools) {
  if (!tools || !tools.length) return '';
  const parts = [];
  tools.forEach((t, i) => {
    if (i > 0) parts.push('<span class="combo-tool-arrow">→</span>');
    parts.push('<div class="combo-tool"><span class="combo-tool-name">' + escapeHtml(t.name) + '</span><span class="combo-tool-role">' + escapeHtml(t.role) + '</span></div>');
  });
  return '<div class="combo-tools">' + parts.join('') + '</div>';
}

function renderComboCards() {
  const filtered = filterCombos();
  const countEl = document.getElementById('filterCount');
  if (countEl) countEl.textContent = filtered.length;
  const grid = document.getElementById('comboGrid');

  if (!filtered.length) {
    if (grid) grid.innerHTML = '<div style="text-align:center;padding:48px;color:var(--text-muted);grid-column:1/-1;">没有匹配的工具组合，试试重置筛选</div>';
    return;
  }

  if (grid) {
    grid.innerHTML = filtered.map(c => {
      const pros = (c.pros || []).slice(0, 2).map(p => '<li>' + escapeHtml(p) + '</li>').join('');
      const cons = (c.cons || []).slice(0, 2).map(cc => '<li>' + escapeHtml(cc) + '</li>').join('');
      const isFeatured = c.featured;
      const trendingBadge = c.trending ? '<span class="badge badge-warning" style="font-size:10px;">🔥 热门</span>' : '';
      const featuredBadge = isFeatured ? '<span class="badge badge-accent" style="font-size:10px;">⭐ 精选</span>' : '';

      return '<div class="combo-card' + (isFeatured ? ' featured' : '') + '">' +
        '<div class="combo-card-header">' +
          '<div>' +
            '<div class="combo-card-name">' + escapeHtml(c.name) + ' ' + trendingBadge + featuredBadge + '</div>' +
            '<div class="combo-card-scenario">' + scenarioLabel(c.scenario) + ' · ' + (DIFFICULTY_LABELS[c.difficulty] || c.difficulty) + '</div>' +
          '</div>' +
          '<span class="badge ' + scenarioCss(c.scenario) + '">' + (COST_LABELS[c.cost] || c.cost) + '</span>' +
        '</div>' +
        '<p class="combo-card-desc">' + escapeHtml(c.description) + '</p>' +
        renderToolChain(c.tools) +
        '<div class="combo-card-tags">' + renderTagsInline(c.tags) + '</div>' +
        '<div class="combo-card-meta">' +
          '<div><div class="combo-card-meta-value">' + renderStars(c.rating) + '</div><div class="combo-card-meta-item">评分</div></div>' +
          '<div><div class="combo-card-meta-value">' + (c.tools || []).length + '</div><div class="combo-card-meta-item">工具数</div></div>' +
          '<div><div class="combo-card-meta-value">' + escapeHtml(c.difficulty) + '</div><div class="combo-card-meta-item">难度</div></div>' +
          '<div><div class="combo-card-meta-value">' + escapeHtml(c.cost) + '</div><div class="combo-card-meta-item">费用</div></div>' +
        '</div>' +
        '<div class="combo-card-pros-cons">' +
          (pros ? '<div class="combo-card-pros"><strong>👍 优点</strong><ul>' + pros + '</ul></div>' : '<div></div>') +
          (cons ? '<div class="combo-card-cons"><strong>👎 注意</strong><ul>' + cons + '</ul></div>' : '<div></div>') +
        '</div>' +
        '<div class="combo-card-footer">' +
          '<span style="font-size:12px;color:var(--text-tertiary);">收录于 ' + escapeHtml(c.addedAt || '') + '</span>' +
          '<a href="#browse" class="btn btn-primary btn-sm">查看 →</a>' +
        '</div>' +
      '</div>';
    }).join('');
  }
}