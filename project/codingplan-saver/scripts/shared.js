/* ==========================================================================
   饭庐者说 · 共享工具与渲染逻辑
   ========================================================================== */

const CPS = {
  config: null,
  plans: [],
  articles: [],
  priceChanges: null,
  state: {
    filters: {
      vendors: new Set(),
      types: new Set(),
      models: new Set(),
      tags: new Set(),
      monthlyPriceMax: null,
      search: ''
    },
    sort: { key: null, dir: 'asc' }
  }
};

/* ---------- Utils ---------- */
function $(sel, root = document) { return root.querySelector(sel); }
function $$(sel, root = document) { return Array.from(root.querySelectorAll(sel)); }

function escapeHtml(text) {
  if (text === null || text === undefined) return '';
  const div = document.createElement('div');
  div.textContent = String(text);
  return div.innerHTML;
}

function formatPrice(value, currency = '¥') {
  if (value === null || value === undefined || value === '-' || value === '') return '—';
  if (typeof value === 'string') return value;
  const prefix = currency === '$' ? '$' : '¥';
  return prefix + value;
}

function formatNumber(value) {
  if (value === null || value === undefined || value === '-') return '—';
  if (typeof value === 'string') return value;
  if (value >= 1000) return value.toLocaleString();
  return value;
}

function renderStars(rating) {
  const full = '★'.repeat(rating);
  const empty = '☆'.repeat(5 - rating);
  return `<span class="stars">${full}</span><span class="stars stars-dim">${empty}</span>`;
}

function renderTagsInline(tags) {
  if (!tags || !tags.length) return '';
  return tags.map(t => `<span class="tag">${escapeHtml(t)}</span>`).join(' ');
}

function renderMarkdownLite(text) {
  if (!text) return '';
  let html = escapeHtml(text);
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
  return html;
}

/* ---------- Data Loading ---------- */
async function loadJSON(path) {
  try {
    const res = await fetch(path, { cache: 'no-store' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error(`Failed to load ${path}:`, err);
    return null;
  }
}

async function loadConfig() {
  if (!CPS.config) CPS.config = await loadJSON('config.json');
  return CPS.config;
}

async function loadPlans() {
  if (!CPS.plans.length) CPS.plans = await loadJSON('plans.json') || [];
  return CPS.plans;
}

async function loadArticles() {
  if (!CPS.articles.length) CPS.articles = await loadJSON('articles.json') || [];
  return CPS.articles;
}

async function loadPriceChanges() {
  if (!CPS.priceChanges) CPS.priceChanges = await loadJSON('price-changes.json');
  return CPS.priceChanges;
}

/* ---------- Navigation ---------- */
function renderNav(activeKey = '') {
  var config = CPS.config;
  if (!config) return '';
  var links = config.nav.map(function(item) {
    return '<a href="' + item.url + '" class="nav-link' + (item.key === activeKey ? ' active' : '') + '">' + escapeHtml(item.label) + '</a>';
  }).join('');

  // Determine if we're on the home page
  var path = window.location.pathname;
  var isHome = path.endsWith('index.html') || path === '/' || path.endsWith('/') || (path.indexOf('codingplan-saver') !== -1 && (path.endsWith('index.html') || path.endsWith('/')));

  // Tab links: always link to separate pages
  var tabs = '<a href="index.html" class="nav-link nav-tab' + (isHome ? ' active' : '') + '">推荐 & 动态</a>' +
             '<a href="compare.html" class="nav-link nav-tab' + (activeKey === 'compare' ? ' active' : '') + '">套餐对比</a>';

  return '<nav class="nav">' +
    '<div class="nav-inner">' +
      '<a href="index.html" class="nav-brand">' +
        '<span class="nav-brand-name">' + escapeHtml(config.site.name) + '</span>' +
      '</a>' +
      '<div class="nav-links" id="navLinks">' +
        tabs +
        links +
        '<a href="join.html" class="nav-cta">加入社群</a>' +
      '</div>' +
      '<button class="nav-mobile-toggle" id="navToggle" aria-label="菜单">☰</button>' +
    '</div>' +
  '</nav>';
}

function mountNav(activeKey) {
  var mount = $('#navMount');
  if (mount) {
    mount.innerHTML = renderNav(activeKey);
    var toggle = $('#navToggle');
    var links = $('#navLinks');
    if (toggle && links) {
      toggle.addEventListener('click', function() { links.classList.toggle('open'); });
    }
  }
}

/* ---------- Footer ---------- */
function renderFooter() {
  const config = CPS.config;
  if (!config) return '';
  const links = (config.footer.links || []).map(l =>
    `<a href="${l.url}">${escapeHtml(l.label)}</a>`
  ).join('');
  return `
    <footer class="footer">
      <div class="container">
        <div class="footer-disclosure">${escapeHtml(config.disclosure || '')}</div>
        <div class="footer-inner">
          <div class="footer-brand">${escapeHtml(config.footer.about || '')}</div>
          <div class="footer-links">${links}</div>
        </div>
      </div>
    </footer>
  `;
}

function mountFooter() {
  const mount = $('#footerMount');
  if (mount) mount.innerHTML = renderFooter();
}

/* ---------- Hero (reusable on home) ---------- */
function renderHomeHero() {
  const config = CPS.config;
  if (!config) return '';
  const h = config.header;
  const stats = (h.stats || []).map(s => `
    <div class="hero-stat">
      <span class="hero-stat-value">${escapeHtml(s.value)}<span style="font-size:14px;color:var(--text-tertiary);font-weight:500;margin-left:4px;">${escapeHtml(s.unit || '')}</span></span>
      <span class="hero-stat-label">${escapeHtml(s.label)}</span>
    </div>
  `).join('');
  return `
    <section class="hero">
      <div class="container">
        <span class="hero-eyebrow">${escapeHtml(h.updateDate || '')}</span>
        <h1 class="hero-title">
          买 <span class="hero-title-accent">AI Coding Plan</span><br>
          之前先看这里
        </h1>
        <p class="hero-subtitle">${escapeHtml(config.site.tagline)}</p>
        <p class="hero-subtitle" style="margin-top:-16px;font-size:14px;">${escapeHtml(h.highlights || '')}</p>
        <div class="hero-actions">
          <a href="#quickEntry" class="btn btn-primary btn-lg">开始选型 ↓</a>
          <a href="wizard.html" class="btn btn-secondary btn-lg">选型助手</a>
          <a href="blog.html" class="btn btn-ghost btn-lg">看测评</a>
        </div>
        <div class="hero-stats">${stats}</div>
      </div>
    </section>
  `;
}

/* ---------- Quick Entries ---------- */
function renderQuickEntries() {
  const config = CPS.config;
  if (!config || !config.quickEntries) return '';
  const cards = config.quickEntries.map(q => `
    <button class="quick-card" data-entry-id="${q.id}">
      <span class="quick-card-icon">${q.icon}</span>
      <span class="quick-card-title">${escapeHtml(q.title)}</span>
      <span class="quick-card-desc">${escapeHtml(q.desc)}</span>
    </button>
  `).join('');
  return `
    <section class="section-sm" id="quickEntry">
      <div class="container">
        <div class="section-header" style="margin-bottom:var(--space-6);">
          <span class="section-eyebrow">QUICK START</span>
          <h2 class="section-title">不知道从哪开始？挑一个场景</h2>
        </div>
        <div class="quick-grid">${cards}</div>
      </div>
    </section>
  `;
}

function bindQuickEntries() {
  $$('.quick-card').forEach(card => {
    card.addEventListener('click', () => {
      const id = card.dataset.entryId;
      const entry = (CPS.config.quickEntries || []).find(q => q.id === id);
      if (!entry) return;
      // Reset filters then apply
      CPS.state.filters.vendors.clear();
      CPS.state.filters.types.clear();
      CPS.state.filters.models.clear();
      CPS.state.filters.tags.clear();
      CPS.state.filters.monthlyPriceMax = null;
      const f = entry.filter || {};
      if (f.monthlyPriceMax) CPS.state.filters.monthlyPriceMax = f.monthlyPriceMax;
      if (f.model) CPS.state.filters.models.add(f.model);
      if (f.tag) CPS.state.filters.tags.add(f.tag);
      // Re-render filter UI + table
      syncFilterUI();
      // 清理搜索框和排序残留，避免与快捷入口筛选叠加
      CPS.state.sort = { key: null, dir: 'asc' };
      const sortSel = $('#sortSelect');
      const searchIn = $('#searchInput');
      if (sortSel) sortSel.value = '';
      if (searchIn) searchIn.value = '';
      renderTable();
      // Scroll to table
      const tableEl = $('#tableSection');
      if (tableEl) tableEl.scrollIntoView({ behavior: 'smooth' });
    });
  });
}

/* ---------- Recommendation Cards ---------- */
function renderRecommendations() {
  var config = CPS.config;
  if (!config || !config.recommendationGroups) return '';
  var groups = config.recommendationGroups.map(function(group) {
    var items = (group.items || []).map(function(item) {
      var plan = CPS.plans.find(function(p) { return p.vendor === item.vendor && p.plan === item.plan; });
      var priceStr = plan
        ? '<strong>' + formatPrice(plan.monthlyPrice, plan.currency || '¥') + '</strong>/月'
        : '';
      var reasons = (item.reasons || []).map(function(r) {
        return '<li>' + renderMarkdownLite(r) + '</li>';
      }).join('');
      var action = item.action || (plan ? plan.action : '#');
      return '<article class="reco-card">' +
        '<div class="reco-card-header">' +
          '<div>' +
            '<div class="reco-card-vendor">' + escapeHtml(item.vendor) + '</div>' +
            '<div class="reco-card-plan">' + escapeHtml(item.plan) + ' ' + (plan ? escapeHtml(plan.type) : '') + '</div>' +
          '</div>' +
          renderStars(item.rating) +
        '</div>' +
        (item.verdict ? '<span class="reco-card-verdict">' + escapeHtml(item.verdict) + '</span>' : '') +
        '<ul class="reco-card-reasons">' + reasons + '</ul>' +
        '<div class="reco-card-footer">' +
          '<span class="reco-card-price">' + priceStr + '</span>' +
          '<a href="' + action + '" class="reco-card-link" target="_blank" rel="noopener">查看详情</a>' +
        '</div>' +
      '</article>';
    }).join('');
    return '<div class="reco-group">' +
      '<div class="reco-group-header">' +
        '<h3 class="reco-group-title">' + escapeHtml(group.title) + '</h3>' +
        (group.subtitle ? '<p class="reco-group-subtitle">' + escapeHtml(group.subtitle) + '</p>' : '') +
      '</div>' +
      '<div class="reco-grid">' + items + '</div>' +
    '</div>';
  }).join('');
  return '<section class="section-sm">' +
    '<div class="container">' +
      '<div class="section-header">' +
        '<span class="section-eyebrow">BLOGGER PICKS</span>' +
        '<h2 class="section-title">博主真实推荐</h2>' +
        '<p class="section-subtitle">基于真实使用体验的推荐，每张卡片都带我的评价。</p>' +
      '</div>' +
      groups +
    '</div>' +
  '</section>';
}

/* ---------- Filter UI ---------- */
function renderFilterBar() {
  const plans = CPS.plans;
  if (!plans.length) return '';

  // Unique values
  const vendors = [...new Set(plans.map(p => p.vendor))].sort();
  const types = [...new Set(plans.map(p => p.type))].sort();
  const allModels = new Set();
  const allTags = new Set();
  plans.forEach(p => {
    (p.models || []).forEach(m => allModels.add(m));
    (p.tags || []).forEach(t => allTags.add(t));
  });
  const models = [...allModels].sort();
  const tags = [...allTags].sort();

  const vendorChips = vendors.map(v =>
    `<button class="filter-chip" data-filter-type="vendors" data-filter-value="${escapeHtml(v)}">${escapeHtml(v)}</button>`
  ).join('');
  const typeChips = types.map(t =>
    `<button class="filter-chip" data-filter-type="types" data-filter-value="${escapeHtml(t)}">${escapeHtml(t)}</button>`
  ).join('');
  const tagChips = tags.map(t =>
    `<button class="filter-chip" data-filter-type="tags" data-filter-value="${escapeHtml(t)}">${escapeHtml(t)}</button>`
  ).join('');

  return '<div class="filter-bar">' +
      '<select class="filter-select" id="sortSelect">' +
        '<option value="">默认排序</option>' +
        '<option value="monthlyPrice-asc">月费 低-高</option>' +
        '<option value="monthlyPrice-desc">月费 高-低</option>' +
        '<option value="rating-desc">评分 高-低</option>' +
        '<option value="measuredMonthlyToken-desc">月Token 多-少</option>' +
        '<option value="tokensPerYuan-desc">性价比 高-低</option>' +
      '</select>' +
      '<input type="text" class="filter-select" id="searchInput" placeholder="搜索平台/套餐..." style="min-width:180px;">' +
      '<button class="filter-chip" id="resetBtn">重置</button>' +
      '<span class="filter-stats">显示 <strong id="filterCount">0</strong> / ' + plans.length + ' 个套餐</span>' +
    '</div>' +
    '<div class="filter-bar">' +
      '<span style="font-size:11px;font-weight:700;color:var(--text-muted);">类型:</span>' +
      typeChips +
    '</div>' +
    '<div class="filter-bar">' +
      '<span style="font-size:11px;font-weight:700;color:var(--text-muted);">标签:</span>' +
      tagChips +
    '</div>';
}

function syncFilterUI() {
  $$('.filter-chip[data-filter-type]').forEach(chip => {
    const type = chip.dataset.filterType;
    const value = chip.dataset.filterValue;
    const active = CPS.state.filters[type] && CPS.state.filters[type].has(value);
    chip.classList.toggle('active', !!active);
  });
}

function bindFilterBar() {
  // Chip toggle
  $$('.filter-chip[data-filter-type]').forEach(chip => {
    chip.addEventListener('click', () => {
      const type = chip.dataset.filterType;
      const value = chip.dataset.filterValue;
      const set = CPS.state.filters[type];
      if (set.has(value)) set.delete(value);
      else set.add(value);
      syncFilterUI();
      renderTable();
    });
  });

  // Reset
  const reset = $('#resetBtn');
  if (reset) {
    reset.addEventListener('click', () => {
      CPS.state.filters.vendors.clear();
      CPS.state.filters.types.clear();
      CPS.state.filters.models.clear();
      CPS.state.filters.tags.clear();
      CPS.state.filters.monthlyPriceMax = null;
      CPS.state.filters.search = '';
      CPS.state.sort = { key: null, dir: 'asc' };
      const sortSel = $('#sortSelect');
      const searchIn = $('#searchInput');
      if (sortSel) sortSel.value = '';
      if (searchIn) searchIn.value = '';
      syncFilterUI();
      renderTable();
    });
  }

  // Sort
  const sortSel = $('#sortSelect');
  if (sortSel) {
    sortSel.addEventListener('change', () => {
      const val = sortSel.value;
      if (!val) {
        CPS.state.sort = { key: null, dir: 'asc' };
      } else {
        const [key, dir] = val.split('-');
        CPS.state.sort = { key, dir };
      }
      renderTable();
    });
  }

  // Search
  const searchIn = $('#searchInput');
  if (searchIn) {
    searchIn.addEventListener('input', () => {
      CPS.state.filters.search = searchIn.value.trim().toLowerCase();
      renderTable();
    });
  }
}

/* ---------- Table Rendering ---------- */
function filterPlans() {
  const f = CPS.state.filters;
  let result = CPS.plans.filter(p => {
    if (f.vendors.size && !f.vendors.has(p.vendor)) return false;
    if (f.types.size && !f.types.has(p.type)) return false;
    if (f.tags.size && !(p.tags || []).some(t => f.tags.has(t))) return false;
    if (f.models.size && !(p.models || []).some(m => f.models.has(m))) return false;
    if (f.monthlyPriceMax && typeof p.monthlyPrice === 'number' && p.monthlyPrice > f.monthlyPriceMax) return false;
    if (f.search) {
      const hay = `${p.vendor} ${p.plan} ${(p.models || []).join(' ')} ${(p.tags || []).join(' ')}`.toLowerCase();
      if (!hay.includes(f.search)) return false;
    }
    return true;
  });

  // Sort
  const { key, dir } = CPS.state.sort;
  if (key) {
    result.sort((a, b) => {
      // Special computed sort keys
      if (key === 'tokensPerYuan') {
        const aVal = (typeof a.monthlyPrice === 'number' && typeof a.measuredMonthlyToken === 'number' && a.monthlyPrice > 0)
          ? a.measuredMonthlyToken / a.monthlyPrice : -1;
        const bVal = (typeof b.monthlyPrice === 'number' && typeof b.measuredMonthlyToken === 'number' && b.monthlyPrice > 0)
          ? b.measuredMonthlyToken / b.monthlyPrice : -1;
        return dir === 'asc' ? aVal - bVal : bVal - aVal;
      }
      const av = a[key];
      const bv = b[key];
      const aNum = typeof av === 'number' ? av : (av === '无限制' ? Infinity : -1);
      const bNum = typeof bv === 'number' ? bv : (bv === '无限制' ? Infinity : -1);
      return dir === 'asc' ? aNum - bNum : bNum - aNum;
    });
  }
  return result;
}

function renderTable() {
  const tbody = $('#plansTableBody');
  const cardsView = $('#plansCardsView');
  const filtered = filterPlans();
  const countEl = $('#filterCount');
  if (countEl) countEl.textContent = filtered.length;

  if (!filtered.length) {
    const empty = `<div style="text-align:center;padding:48px;color:var(--text-muted);">没有匹配的套餐，试试重置筛选</div>`;
    if (tbody) tbody.innerHTML = `<tr><td colspan="99">${empty}</td></tr>`;
    if (cardsView) cardsView.innerHTML = empty;
    return;
  }

  // Desktop table
  if (tbody) {
    tbody.innerHTML = filtered.map(p => {
      const price = formatPrice(p.monthlyPrice, p.currency || '¥');
      const firstPrice = p.firstMonthPrice ? formatPrice(p.firstMonthPrice, p.currency || '¥') : '—';
      const measured = p.measuredMonthlyToken ? `${p.measuredMonthlyToken}M` : '—';
      const tokensPerYuan = (typeof p.monthlyPrice === 'number' && typeof p.measuredMonthlyToken === 'number' && p.monthlyPrice > 0)
        ? (p.measuredMonthlyToken / p.monthlyPrice).toFixed(2)
        : '—';
      const pricePerM = (typeof p.monthlyPrice === 'number' && typeof p.measuredMonthlyToken === 'number' && p.measuredMonthlyToken > 0)
        ? `¥${(p.monthlyPrice / p.measuredMonthlyToken).toFixed(2)}`
        : '—';
      const models = (p.models || []).slice(0, 4).join(', ') + ((p.models || []).length > 4 ? '...' : '');
      const tagsHtml = renderTagsInline(p.tags);
      return `
        <tr>
          <td class="col-vendor">${escapeHtml(p.vendor)}</td>
          <td>${escapeHtml(p.plan)}</td>
          <td><span class="badge">${escapeHtml(p.type)}</span></td>
          <td>${renderStars(p.rating)}</td>
          <td class="col-price">${price}</td>
          <td class="col-price col-extra col-hidden" style="color:var(--color-warning);">${firstPrice}</td>
          <td class="col-extra col-hidden">${formatNumber(p.monthlyRequests)}</td>
          <td class="col-price">${measured}</td>
          <td class="col-price" style="color:var(--accent-primary);">${tokensPerYuan}</td>
          <td class="col-extra col-hidden" style="font-size:12px;color:var(--text-tertiary);">${pricePerM}</td>
          <td><span style="font-size:12px;">${escapeHtml(models)}</span></td>
          <td>${tagsHtml}</td>
          <td class="col-action"><a href="${p.action || '#'}" target="_blank" rel="noopener">查看</a></td>
        </tr>
      `;
    }).join('');
  }

  // Mobile cards
  if (cardsView) {
    cardsView.innerHTML = filtered.map(p => {
      const price = formatPrice(p.monthlyPrice, p.currency || '¥');
      const measured = p.measuredMonthlyToken ? `${p.measuredMonthlyToken}M` : '—';
      const tokensPerYuan = (typeof p.monthlyPrice === 'number' && typeof p.measuredMonthlyToken === 'number' && p.monthlyPrice > 0)
        ? (p.measuredMonthlyToken / p.monthlyPrice).toFixed(2) : '—';
      const models = (p.models || []).join(', ');
      return `
        <div class="plan-card-item">
          <div class="plan-card-header">
            <div>
              <div class="plan-card-vendor">${escapeHtml(p.vendor)}</div>
              <div class="plan-card-plan">${escapeHtml(p.plan)} · ${escapeHtml(p.type)}</div>
            </div>
            <div class="plan-card-price">${price}</div>
          </div>
          ${renderStars(p.rating)}
          <div class="plan-card-row">
            <div><span class="plan-card-label">月Token</span><br><span class="plan-card-value">${measured}</span></div>
            <div><span class="plan-card-label">每元Token</span><br><span class="plan-card-value">${tokensPerYuan} M</span></div>
            <div><span class="plan-card-label">模型</span><br><span class="plan-card-value">${escapeHtml(models)}</span></div>
            <div><span class="plan-card-label">标签</span><br>${renderTagsInline(p.tags)}</div>
          </div>
          <div style="margin-top:var(--space-3);text-align:right;">
            <a href="${p.action || '#'}" target="_blank" rel="noopener" class="btn btn-primary btn-sm">查看</a>
          </div>
        </div>
      `;
    }).join('');
  }
}

function renderTableSection() {
  return `
    <section class="section" id="tableSection">
      <div class="container">
        <div class="section-header" style="display:flex;justify-content:space-between;align-items:flex-end;flex-wrap:wrap;gap:16px;">
          <div>
            <span class="section-eyebrow">FULL COMPARISON</span>
            <h2 class="section-title">完整套餐对比表</h2>
            <p class="section-subtitle">所有数据基于官方公开信息整理。点击标签筛选，悬停查看详情。</p>
          </div>
          <button class="table-toggle-btn" id="toggleColumnsBtn" onclick="toggleExtraColumns()">展开全部列</button>
        </div>
        <div id="filterBarMount"></div>
        <div class="table-wrap">
          <table class="data-table">
            <thead>
              <tr>
                <th>平台</th>
                <th>套餐</th>
                <th>类型</th>
                <th>评分</th>
                <th>月费</th>
                <th class="col-extra">首月</th>
                <th class="col-extra">月请求</th>
                <th>实测月Token</th>
                <th>每元Token</th>
                <th class="col-extra">1M Token价</th>
                <th>支持模型</th>
                <th>标签</th>
                <th>详情</th>
              </tr>
            </thead>
            <tbody id="plansTableBody"></tbody>
          </table>
        </div>
        <div class="plan-cards-view" id="plansCardsView"></div>
      </div>
    </section>
  `;
}

window._columnsExpanded = false;
function toggleExtraColumns() {
  window._columnsExpanded = !window._columnsExpanded;
  const btn = document.getElementById('toggleColumnsBtn');
  const cols = document.querySelectorAll('td.col-extra');
  cols.forEach(c => c.classList.toggle('col-hidden', !window._columnsExpanded));
  if (btn) {
    btn.textContent = window._columnsExpanded ? '收起额外列' : '展开全部列';
    btn.classList.toggle('active', window._columnsExpanded);
  }
}

/* ---------- Community Section ---------- */
function renderCommunitySection() {
  const config = CPS.config;
  if (!config || !config.community) return '';
  const c = config.community;
  return `
    <section class="section-sm">
      <div class="container">
        <div class="section-header text-center">
          <span class="section-eyebrow">JOIN COMMUNITY</span>
          <h2 class="section-title">不止于看表，来和我聊聊</h2>
          <p class="section-subtitle" style="margin:0 auto;">每周价格变动、抢购提醒、实测报告，第一时间发在社群里。</p>
        </div>
        <div class="community-grid">
          <div class="community-card community-card-free">
            <div class="community-card-header">
              <h3 class="community-card-title">${escapeHtml(c.free.title)}</h3>
              <span class="badge badge-accent">FREE</span>
            </div>
            <div class="community-card-subtitle">${escapeHtml(c.free.subtitle)}</div>
            <p class="community-card-desc">${escapeHtml(c.free.description)}</p>
            <ul class="community-highlights">
              ${(c.free.highlights || []).map(h => `<li>${escapeHtml(h)}</li>`).join('')}
            </ul>
            <a href="join.html" class="btn btn-secondary btn-lg">' + escapeHtml(c.free.ctaText) + '</a>
          </div>
          <div class="community-card community-card-paid">
            <div class="community-card-header">
              <h3 class="community-card-title">${escapeHtml(c.paid.title)}</h3>
              <span class="badge badge-premium">PRO</span>
            </div>
            <div class="community-card-subtitle">${escapeHtml(c.paid.subtitle)}</div>
            <p class="community-card-desc">${escapeHtml(c.paid.description)}</p>
            <ul class="community-highlights">
              ${(c.paid.highlights || []).map(h => `<li>${escapeHtml(h)}</li>`).join('')}
            </ul>
            <a href="${c.paid.url || 'join.html'}" class="btn btn-primary btn-lg">' + escapeHtml(c.paid.ctaText) + '</a>
          </div>
        </div>
      </div>
    </section>
  `;
}

/* ---------- Price Changes Inline ---------- */
function renderPriceChangesInline() {
  var data = CPS.priceChanges;
  if (!data || !data.changes || !data.changes.length) return '';
  var recent = data.changes.slice(0, 5);
  var items = recent.map(function(c) {
    var impactBadge = c.impact === 'positive'
      ? '<span class="badge badge-positive">利好</span>'
      : c.impact === 'negative'
      ? '<span class="badge badge-negative">利空</span>'
      : '<span class="badge">中性</span>';
    return '<div class="price-change-item">' +
      '<div>' + impactBadge + '</div>' +
      '<div>' +
        '<div class="price-change-vendor">' + escapeHtml(c.vendor) + ' ' + escapeHtml(c.type) + '</div>' +
        '<div class="price-change-detail">' + escapeHtml(c.detail) + '</div>' +
      '</div>' +
      '<span class="price-change-date">' + escapeHtml(c.date) + '</span>' +
    '</div>';
  }).join('');
  return '<section class="section-sm">' +
    '<div class="container">' +
      '<div class="card" style="padding:var(--space-5);">' +
        '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:var(--space-4);">' +
          '<div>' +
            '<span class="section-eyebrow">PRICE ALERT</span>' +
            '<h3 style="font-size:18px;font-weight:700;">近期价格变动</h3>' +
          '</div>' +
          '<span style="font-size:12px;color:var(--text-tertiary);">' + escapeHtml(data.weekRange || '') + '</span>' +
        '</div>' +
        items +
      '</div>' +
    '</div>' +
  '</section>';
}

/* ---------- Article Card ---------- */
function renderArticleCard(article) {
  var href = article.url || ('article.html?id=' + encodeURIComponent(article.id));
  var isExternal = !!article.url;
  return '<a href="' + href + '" class="card card-hover" style="display:block;text-decoration:none;"' + (isExternal ? ' target="_blank" rel="noopener"' : '') + '>' +
    '<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:var(--space-3);">' +
      '<span style="font-size:28px;font-weight:800;color:var(--accent);">' + escapeHtml(article.cover || '') + '</span>' +
      '<span class="badge badge-accent">' + escapeHtml(article.category) + '</span>' +
    '</div>' +
    '<h3 style="font-size:16px;font-weight:700;line-height:1.35;margin-bottom:var(--space-2);color:var(--text-primary);">' + escapeHtml(article.title) + '</h3>' +
    '<p style="font-size:13px;color:var(--text-tertiary);line-height:1.5;margin-bottom:var(--space-3);">' + escapeHtml(article.excerpt) + '</p>' +
    '<div style="display:flex;justify-content:space-between;align-items:center;font-size:12px;color:var(--text-muted);">' +
      '<span>' + escapeHtml(article.date) + ' ' + escapeHtml(article.readTime) + (article.author ? ' ' + escapeHtml(article.author) : '') + '</span>' +
      '<span class="text-accent" style="font-weight:600;">' + (isExternal ? '阅读' : '阅读') + '</span>' +
    '</div>' +
  '</a>';
}

/* ---------- Page Bootstrap Helper ---------- */
async function bootstrapPage(activeKey) {
  await loadConfig();
  mountNav(activeKey);
  mountFooter();
}

/* ---------- Export to window ---------- */
window.CPS = CPS;
window.$ = $;
window.$$ = $$;
window.escapeHtml = escapeHtml;
window.formatPrice = formatPrice;
window.formatNumber = formatNumber;
window.renderStars = renderStars;
window.renderTagsInline = renderTagsInline;
window.renderMarkdownLite = renderMarkdownLite;
window.loadConfig = loadConfig;
window.loadPlans = loadPlans;
window.loadArticles = loadArticles;
window.loadPriceChanges = loadPriceChanges;
window.bootstrapPage = bootstrapPage;
window.renderHomeHero = renderHomeHero;
window.renderQuickEntries = renderQuickEntries;
window.bindQuickEntries = bindQuickEntries;
window.renderRecommendations = renderRecommendations;
window.renderFilterBar = renderFilterBar;
window.bindFilterBar = bindFilterBar;
window.syncFilterUI = syncFilterUI;
window.renderTable = renderTable;
window.renderTableSection = renderTableSection;
window.toggleExtraColumns = toggleExtraColumns;
window.renderCommunitySection = renderCommunitySection;
window.renderPriceChangesInline = renderPriceChangesInline;
window.renderArticleCard = renderArticleCard;
