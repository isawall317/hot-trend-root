// ============================================================
// Tab 1: 推荐（Hero + Top3 + 场景卡片 + 博主推荐 + 最近变动）
// ============================================================
function renderRecommend() {
  const body = document.getElementById('recommend-body');
  body.innerHTML = renderHero() + renderTopPicks() + renderQuickEntries() + renderRecommendations() + renderRecentChanges();
  bindQuickEntries();
}

function renderHero() {
  const h = site.header || {};
  const stats = (h.stats || []).map(s =>
    '<div><div class="hero-stat-value">' + escapeHtml(s.value) +
    '<span style="font-size:13px;color:var(--text-tertiary);font-weight:500;margin-left:2px;">' + escapeHtml(s.unit || '') + '</span></div>' +
    '<div class="hero-stat-label">' + escapeHtml(s.label) + '</div></div>'
  ).join('');
  return '<section class="hero"><div class="container"><div class="hero-inner"><div>' +
    '<span class="section-eyebrow">' + escapeHtml(h.updateDate || '') + '</span>' +
    '<h1 class="hero-title">AI Coding Plan<br><span class="hero-title-accent">买哪个最划算？</span></h1>' +
    '<p class="hero-subtitle">' + escapeHtml(site.tagline || '') + '</p>' +
    '<p style="font-size:13px;color:var(--text-tertiary);margin-bottom:var(--space-5);margin-top:-12px;">' + escapeHtml(h.highlights || '') + '</p>' +
    '<div class="hero-actions">' +
      '<a href="#compare" class="btn btn-primary btn-lg">查看完整对比表</a>' +
      '<a href="#community" class="btn btn-secondary btn-lg">加入社群</a>' +
    '</div>' +
    '<div class="hero-stats">' + stats + '</div>' +
  '</div></div></section>';
}

function renderTopPicks() {
  const scored = plans
    .filter(p => p.status === 'active' && typeof p.monthlyPrice === 'number' && typeof p.measuredMonthlyToken === 'number')
    .map(p => ({ plan: p, tpu: p.measuredMonthlyToken / p.monthlyPrice, score: p.rating * 10 + (p.measuredMonthlyToken / p.monthlyPrice) }))
    .sort((a, b) => b.score - a.score);
  const top3 = scored.slice(0, 3);
  if (!top3.length) return '';

  const labels = ['综合最佳', '高性价比', '入门首选'];
  const reasons = [
    '综合评分最高，模型能力和性价比都很出色。',
    '每元能拿到更多 Token，花同样的钱可用更多。',
    '月费最低，适合预算有限或想先试试水的用户。'
  ];
  const picks = top3.map((item, i) => {
    const p = item.plan;
    const isBest = i === 0;
    return '<div class="top-pick-card' + (isBest ? ' pick-best' : '') + '">' +
      '<div class="top-pick-label">' + labels[i] + '</div>' +
      '<div class="top-pick-vendor">' + escapeHtml(p.vendor) + '</div>' +
      '<div class="top-pick-plan">' + escapeHtml(p.plan) + ' ' + escapeHtml(p.type) + '</div>' +
      '<div class="top-pick-price">' + formatPrice(p.monthlyPrice, p.currency || '¥') + '<span class="top-pick-price-unit">/月</span></div>' +
      '<div class="top-pick-metrics">' +
        '<div><div class="top-pick-metric-value">' + p.measuredMonthlyToken + 'M</div><div class="top-pick-metric-label">月Token</div></div>' +
        '<div><div class="top-pick-metric-value">' + item.tpu.toFixed(1) + '</div><div class="top-pick-metric-label">每元Token</div></div>' +
      '</div>' +
      '<div class="top-pick-reason">' + reasons[i] + '</div>' +
      '<div class="top-pick-action">' +
        '<a href="' + (p.action || '#') + '" target="_blank" rel="nofollow sponsored" class="btn btn-primary btn-sm">优惠购买 →</a>' +
      '</div>' +
    '</div>';
  }).join('');
  return '<section class="section-sm"><div class="container">' +
    '<div class="section-header" style="margin-bottom:var(--space-4);">' +
      '<span class="section-eyebrow">TOP PICKS</span>' +
      '<h2 class="section-title">不知道买哪个？看这三个就够了</h2>' +
      '<p class="section-subtitle">基于评分、性价比和真实体验的综合推荐。点击场景卡片筛选或查看完整对比表。</p>' +
    '</div>' +
    '<div class="top-pick-grid">' + picks + '</div>' +
  '</div></section>';
}

function renderQuickEntries() {
  const entries = site.quickEntries || [];
  if (!entries.length) return '';
  const cards = entries.map(q =>
    '<button class="quick-card" data-entry-id="' + escapeHtml(q.id) + '">' +
      '<span class="quick-card-icon">' + escapeHtml(q.icon) + '</span>' +
      '<span class="quick-card-title">' + escapeHtml(q.title) + '</span>' +
      '<span class="quick-card-desc">' + escapeHtml(q.desc) + '</span>' +
    '</button>'
  ).join('');
  return '<section class="section-sm"><div class="container">' +
    '<div class="section-header" style="margin-bottom:var(--space-4);">' +
      '<span class="section-eyebrow">SCENARIOS</span>' +
      '<h2 class="section-title">按你的场景来选</h2>' +
    '</div>' +
    '<div class="quick-grid">' + cards + '</div>' +
  '</div></section>';
}

function bindQuickEntries() {
  document.querySelectorAll('.quick-card').forEach(card => {
    card.addEventListener('click', () => {
      const id = card.dataset.entryId;
      const entry = (site.quickEntries || []).find(q => q.id === id);
      if (!entry || !entry.filter) return;
      const query = Object.entries(entry.filter).map(([k, v]) => k + '=' + encodeURIComponent(v)).join('&');
      location.hash = '#compare' + (query ? '?' + query : '');
    });
  });
}

function renderRecommendations() {
  const groups = site.recommendationGroups || [];
  if (!groups.length) return '';
  const html = groups.map((group, gi) => {
    const items = (group.items || []).map(item => {
      const plan = plans.find(p => p.vendor === item.vendor && p.plan === item.plan);
      const priceStr = plan ? '<strong>' + formatPrice(plan.monthlyPrice, plan.currency || '¥') + '</strong>/月' : '';
      const reasons = (item.reasons || []).map(r => '<li>' + renderMarkdownLite(r) + '</li>').join('');
      const action = item.action || (plan ? plan.action : '#');
      return '<div class="reco-item">' +
        '<div class="reco-item-header"><div><div class="reco-item-vendor">' + escapeHtml(item.vendor) + '</div><div class="reco-item-plan">' + escapeHtml(item.plan) + ' ' + (plan ? escapeHtml(plan.type) : '') + '</div></div>' + renderStars(item.rating) + '</div>' +
        (item.verdict ? '<span class="reco-item-verdict">' + escapeHtml(item.verdict) + '</span>' : '') +
        '<ul class="reco-item-reasons">' + reasons + '</ul>' +
        '<div class="reco-item-footer">' +
          '<span style="font-family:var(--font-mono);font-size:13px;color:var(--text-tertiary);">' + priceStr + '</span>' +
          '<a href="' + action + '" target="_blank" rel="nofollow sponsored" class="btn btn-primary">优惠购买 →</a>' +
        '</div></div>';
    }).join('');
    const header = groups.length > 1
      ? '<div style="margin-bottom:var(--space-4);"><h3 style="font-size:16px;font-weight:700;">' + escapeHtml(group.title) + '</h3>' + (group.subtitle ? '<p style="font-size:13px;color:var(--text-tertiary);">' + escapeHtml(group.subtitle) + '</p>' : '') + '</div>'
      : '';
    return '<div style="' + (gi > 0 ? 'margin-top:var(--space-8);' : '') + '">' + header + '<div class="reco-list">' + items + '</div></div>';
  }).join('');
  return '<section class="section-sm"><div class="container">' +
    '<div class="section-header" style="margin-bottom:var(--space-4);">' +
      '<span class="section-eyebrow">ALL RECOMMENDATIONS</span>' +
      '<h2 class="section-title">饭庐者说的完整推荐</h2>' +
    '</div>' + html + '</div></section>';
}

// 最近变动（紧凑单行时间线）
const KIND_LABEL = {
  price_change: '价格', promotion: '活动', new_model: '新模型', new_plan: '新套餐',
  subscription_pause: '暂停', outage: '故障', article: '文章'
};

function renderRecentChanges() {
  const now = new Date();
  const cutoff = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
  const recent = changes
    .filter(c => new Date(c.date) >= cutoff)
    .sort((a, b) => b.date.localeCompare(a.date));
  if (!recent.length) return '';

  const items = recent.map(c => {
    const impactBadge = c.impact === 'positive' ? '<span class="badge badge-positive">利好</span>'
      : c.impact === 'negative' ? '<span class="badge badge-negative">利空</span>'
      : '<span class="badge">中性</span>';
    const kindLabel = '<span class="tag">' + (KIND_LABEL[c.kind] || c.kind) + '</span>';
    const vendorPrefix = c.vendor && c.vendor !== '通用' ? '<span class="rc-vendor">' + escapeHtml(c.vendor) + '</span> · ' : '';
    const isArticle = c.kind === 'article';
    const titleHtml = isArticle && c.sourceUrl
      ? '<a href="' + escapeHtml(c.sourceUrl) + '" target="_blank" rel="noopener">' + escapeHtml(c.title) + '</a>'
      : escapeHtml(c.title);
    const detailAttr = c.detail && c.detail !== c.title ? ' data-detail="' + escapeHtml(c.detail).replace(/"/g, '&quot;') + '"' : '';
    return '<div class="rc-item' + (c.featured ? ' rc-featured' : '') + '"' + detailAttr + '>' +
      '<span class="rc-date">' + escapeHtml(c.date.slice(5)) + '</span>' +
      impactBadge +
      '<span class="rc-title">' + vendorPrefix + titleHtml + '</span>' +
      kindLabel +
    '</div>';
  }).join('');

  return '<section class="section-sm">' +
    '<div class="container">' +
      '<div class="section-header" style="margin-bottom:var(--space-4);">' +
        '<span class="section-eyebrow">RECENT CHANGES</span>' +
        '<h2 class="section-title">最近变动 · 为什么这样推荐</h2>' +
        '<p class="section-subtitle">最近 30 天影响套餐选择的关键变动。悬停查看详情。</p>' +
      '</div>' +
      '<div class="rc-list">' + items + '</div>' +
    '</div>' +
  '</section>';
}