// ============================================================
// Tab 2: 浏览（筛选栏 + Skill 卡片网格 + 搜索）
// ============================================================
const browseState = {
  filters: { categories: new Set(), tags: new Set(), search: '' },
  sort: { key: null, dir: 'asc' }
};

function renderBrowse() {
  const body = document.getElementById('browse-body');
  body.innerHTML = renderBrowseSection();
  bindBrowseFilters();
  renderSkillCards();
}

function renderBrowseSection() {
  return '<section class="section-sm">' +
    '<div class="container">' +
      '<div class="section-header" style="display:flex;justify-content:space-between;align-items:flex-end;flex-wrap:wrap;gap:var(--space-3);">' +
        '<div>' +
          '<span class="section-eyebrow">BROWSE ALL</span>' +
          '<h2 class="section-title">全部 Skills</h2>' +
          '<p class="section-subtitle">点击分类筛选，搜索框输入关键词。找到适合你的 Skill。</p>' +
        '</div>' +
      '</div>' +
      '<div id="browseFilterBar"></div>' +
      '<div class="skill-grid" id="skillGrid"></div>' +
    '</div></section>';
}

function renderBrowseFilterBar() {
  const categories = [...new Set(skills.map(s => s.category))].sort();
  const allTags = new Set();
  skills.forEach(s => (s.tags || []).forEach(t => allTags.add(t)));
  const tags = [...allTags].sort();

  const catChips = categories.map(c => '<button class="filter-chip" data-filter-type="categories" data-filter-value="' + escapeHtml(c) + '">' + categoryLabel(c) + '</button>').join('');
  const tagChips = tags.map(t => '<button class="filter-chip" data-filter-type="tags" data-filter-value="' + escapeHtml(t) + '">' + escapeHtml(t) + '</button>').join('');

  return '<div class="filter-bar">' +
    '<select class="filter-select" id="sortSelect">' +
      '<option value="">默认排序</option>' +
      '<option value="rating-desc">评分 高-低</option>' +
      '<option value="installs-desc">安装量 多-少</option>' +
      '<option value="addedAt-desc">最新收录</option>' +
    '</select>' +
    '<input type="text" class="filter-select" id="searchInput" placeholder="搜索 Skill 名称 / 描述..." style="min-width:200px;">' +
    '<button class="filter-chip" id="resetBtn">重置</button>' +
    '<span class="filter-stats">显示 <strong id="filterCount">0</strong> / ' + skills.length + ' 个 Skills</span>' +
  '</div>' +
  (catChips ? '<div class="filter-bar"><span style="font-size:11px;font-weight:700;color:var(--text-muted);">分类:</span>' + catChips + '</div>' : '') +
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
    if (hashFilter.category) browseState.filters.categories.add(hashFilter.category);
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
      renderSkillCards();
    });
  });

  const reset = document.getElementById('resetBtn');
  if (reset) reset.addEventListener('click', () => {
    browseState.filters.categories.clear();
    browseState.filters.tags.clear();
    browseState.filters.search = '';
    browseState.sort = { key: null, dir: 'asc' };
    const ss = document.getElementById('sortSelect'); if (ss) ss.value = '';
    const si = document.getElementById('searchInput'); if (si) si.value = '';
    syncBrowseFilterUI();
    renderSkillCards();
  });

  const ss = document.getElementById('sortSelect');
  if (ss) ss.addEventListener('change', () => {
    const val = ss.value;
    if (!val) browseState.sort = { key: null, dir: 'asc' };
    else { const [k, d] = val.split('-'); browseState.sort = { key: k, dir: d }; }
    renderSkillCards();
  });

  const si = document.getElementById('searchInput');
  if (si) si.addEventListener('input', () => {
    browseState.filters.search = si.value.trim().toLowerCase();
    renderSkillCards();
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

function filterSkills() {
  const f = browseState.filters;
  let result = skills.filter(s => {
    if (f.categories.size && !f.categories.has(s.category)) return false;
    if (f.tags.size && !(s.tags || []).some(t => f.tags.has(t))) return false;
    if (f.search) {
      const hay = (s.name + ' ' + s.description + ' ' + s.author + ' ' + (s.tags || []).join(' ') + ' ' + (s.scenarios || []).join(' ')).toLowerCase();
      if (!hay.includes(f.search)) return false;
    }
    return true;
  });
  const { key, dir } = browseState.sort;
  if (key) {
    result.sort((a, b) => {
      const av = a[key], bv = b[key];
      if (key === 'installs') {
        const aNum = parseInt(String(av).replace(/[^0-9]/g, '')) || 0;
        const bNum = parseInt(String(bv).replace(/[^0-9]/g, '')) || 0;
        return dir === 'asc' ? aNum - bNum : bNum - aNum;
      }
      if (key === 'addedAt') {
        return dir === 'asc' ? String(av).localeCompare(String(bv)) : String(bv).localeCompare(String(av));
      }
      const aNum = typeof av === 'number' ? av : 0;
      const bNum = typeof bv === 'number' ? bv : 0;
      return dir === 'asc' ? aNum - bNum : bNum - aNum;
    });
  }
  return result;
}

function renderSkillCards() {
  const filtered = filterSkills();
  const countEl = document.getElementById('filterCount');
  if (countEl) countEl.textContent = filtered.length;
  const grid = document.getElementById('skillGrid');

  if (!filtered.length) {
    if (grid) grid.innerHTML = '<div style="text-align:center;padding:48px;color:var(--text-muted);grid-column:1/-1;">没有匹配的 Skill，试试重置筛选</div>';
    return;
  }

  if (grid) {
    grid.innerHTML = filtered.map(s => {
      const pros = (s.pros || []).slice(0, 2).map(p => '<li>' + escapeHtml(p) + '</li>').join('');
      const cons = (s.cons || []).slice(0, 2).map(c => '<li>' + escapeHtml(c) + '</li>').join('');
      const isFeatured = s.featured;
      const trendingBadge = s.trending ? '<span class="badge badge-warning" style="font-size:10px;">🔥 热门</span>' : '';
      const featuredBadge = s.featured ? '<span class="badge badge-accent" style="font-size:10px;">⭐ 精选</span>' : '';

      return '<div class="skill-card' + (isFeatured ? ' featured' : '') + '">' +
        '<div class="skill-card-header">' +
          '<div>' +
            '<div class="skill-card-name">' + escapeHtml(s.name) + ' ' + trendingBadge + featuredBadge + '</div>' +
            '<div class="skill-card-author">by ' + escapeHtml(s.author) + '</div>' +
          '</div>' +
          '<span class="badge ' + categoryCss(s.category) + '">' + categoryLabel(s.category) + '</span>' +
        '</div>' +
        '<p class="skill-card-desc">' + escapeHtml(s.description) + '</p>' +
        '<div class="skill-card-tags">' + renderTagsInline(s.tags) + '</div>' +
        '<div class="skill-card-meta">' +
          '<div><div class="skill-card-meta-value">' + renderStars(s.rating) + '</div><div class="skill-card-meta-item">评分</div></div>' +
          '<div><div class="skill-card-meta-value">' + escapeHtml(s.installs) + '</div><div class="skill-card-meta-item">安装量</div></div>' +
        '</div>' +
        '<div class="skill-card-pros-cons">' +
          (pros ? '<div class="skill-card-pros"><strong>👍 优点</strong><ul>' + pros + '</ul></div>' : '<div></div>') +
          (cons ? '<div class="skill-card-cons"><strong>👎 注意</strong><ul>' + cons + '</ul></div>' : '<div></div>') +
        '</div>' +
        '<div class="skill-card-footer">' +
          '<span class="skill-card-installs">' + (s.scenarios || []).slice(0, 2).map(sc => escapeHtml(sc)).join(' · ') + '</span>' +
          '<a href="' + (s.githubUrl || '#') + '" target="_blank" rel="nofollow sponsored" class="btn btn-primary btn-sm">安装 →</a>' +
        '</div>' +
      '</div>';
    }).join('');
  }
}