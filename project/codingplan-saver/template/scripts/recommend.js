// ============================================================
// Tab 1: 推荐（Hero + Top3 + 场景卡片 + 博主推荐 + 最近变动）
// ============================================================
function renderRecommend() {
  const body = document.getElementById('recommend-body');
  body.innerHTML = renderHero() + renderTopPicks() + renderQuickEntries() + renderRecommendations();
  bindQuickEntries();
  bindRecentChangesModal();
}

// 弹窗：最近变动
function bindRecentChangesModal() {
  // Hero "查看完整对比表" 平滑滚动到对比表
  const compareLink = document.querySelector('.hero-actions a[href="#compare"]');
  if (compareLink) {
    compareLink.addEventListener('click', e => {
      e.preventDefault();
      const target = document.getElementById('tab-compare');
      if (target) target.scrollIntoView({ behavior: 'smooth' });
    });
  }
  // "最近变动"弹窗触发
  const trigger = document.getElementById('rcTrigger');
  if (!trigger) return;
  trigger.addEventListener('click', () => {
    // 避免重复注入
    let modal = document.getElementById('rcModal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'rcModal';
      modal.className = 'rc-modal-overlay';
      modal.innerHTML = '<div class="rc-modal">' +
        '<div class="rc-modal-header">' +
          '<h3>最近变动 · 为什么这样推荐</h3>' +
          '<button class="rc-modal-close" id="rcModalClose">✕</button>' +
        '</div>' +
        '<p class="rc-modal-sub">最近 14 天影响套餐选择的关键变动。点击查看原文。</p>' +
        '<div class="rc-modal-body">' + renderRecentChangesList() + '</div>' +
      '</div>';
      document.body.appendChild(modal);
      // 点击遮罩关闭
      modal.addEventListener('click', e => {
        if (e.target === modal || e.target.id === 'rcModalClose') {
          modal.classList.remove('rc-modal-open');
          document.body.style.overflow = '';
        }
      });
    }
    modal.classList.add('rc-modal-open');
    document.body.style.overflow = 'hidden';
  });
}

// 抽取时间线渲染（弹窗内用，不含外层 section）
function renderRecentChangesList() {
  const now = new Date();
  const cutoff = new Date(now.getTime() - 14 * 24 * 60 * 60 * 1000);
  const recent = changes
    .filter(c => new Date(c.date) >= cutoff)
    .sort((a, b) => b.date.localeCompare(a.date));
  if (!recent.length) return '<p style="color:var(--text-helper);padding:var(--sp-5);">暂无近期变动</p>';

  const items = recent.map(c => {
    const impactBadge = c.impact === 'positive' ? '<span class="badge badge-positive">利好</span>'
      : c.impact === 'negative' ? '<span class="badge badge-negative">利空</span>'
      : '<span class="badge">中性</span>';
    const kindLabel = '<span class="tag">' + (KIND_LABEL[c.kind] || c.kind) + '</span>';
    const vendorPrefix = c.vendor && c.vendor !== '通用' ? '<span class="rc-vendor">' + escapeHtml(c.vendor) + '</span> · ' : '';
    const titleHtml = c.sourceUrl
      ? '<a href="' + escapeHtml(c.sourceUrl) + '" target="_blank" rel="noopener">' + escapeHtml(c.title) + '</a>'
      : escapeHtml(c.title);
    return '<div class="rc-item' + (c.featured ? ' rc-featured' : '') + '">' +
      '<span class="rc-date">' + escapeHtml(c.date.slice(5)) + '</span>' +
      impactBadge +
      '<span class="rc-title">' + vendorPrefix + titleHtml + '</span>' +
      kindLabel +
    '</div>';
  }).join('');
  return '<div class="rc-list">' + items + '</div>';
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
      '<button id="rcTrigger" class="btn btn-secondary btn-lg">最近变动</button>' +
    '</div>' +
    '<div class="hero-stats">' + stats + '</div>' +
  '</div></div></section>';
}

function renderTopPicks() {
  // 优先读博主钦定推荐（site.recommendationGroups），读不到才 fallback 到算法
  const groups = site.recommendationGroups || [];
  const curated = groups[0] && groups[0].items && groups[0].items.length >= 3 ? groups[0].items.slice(0, 3) : null;

  let picksData;
  if (curated) {
    picksData = curated.map(item => {
      const p = plans.find(pl => pl.vendor === item.vendor && pl.plan === item.plan);
      return { item, plan: p };
    }).filter(d => d.plan); // 失配的丢掉
  }
  // fallback：算法排名
  if (!picksData || picksData.length < 3) {
    const scored = plans
      .filter(p => p.status === 'active' && typeof p.monthlyPrice === 'number' && typeof p.measuredMonthlyToken === 'number')
      .map(p => ({ plan: p, tpu: p.measuredMonthlyToken / p.monthlyPrice, score: p.rating * 10 + (p.measuredMonthlyToken / p.monthlyPrice) }))
      .sort((a, b) => b.score - a.score)
      .slice(0, 3);
    picksData = scored.map((s, i) => ({
      item: { verdict: ['综合最佳', '高性价比', '入门首选'][i], reasons: ['综合评分最高，模型能力和性价比都很出色。', '每元能拿到更多 Token，花同样的钱可用更多。', '月费最低，适合预算有限或想先试试水的用户。'][i], rating: s.plan.rating, action: s.plan.action },
      plan: s.plan, tpu: s.tpu
    }));
  }

  if (!picksData.length) return '';
  const labels = ['综合最佳', '高性价比', '入门首选'];

  const picks = picksData.map((d, i) => {
    const p = d.plan;
    const item = d.item;
    const isBest = i === 0;
    const tpu = (typeof p.monthlyPrice === 'number' && typeof p.measuredMonthlyToken === 'number' && p.monthlyPrice > 0)
      ? (p.measuredMonthlyToken / p.monthlyPrice).toFixed(1) : '—';
    const tokenStr = typeof p.measuredMonthlyToken === 'number' ? p.measuredMonthlyToken + 'M' : '—';
    const verdict = item.verdict || labels[i];
    const reasons = (item.reasons || []).map(r => '<li>' + renderMarkdownLite(r) + '</li>').join('');
    const action = item.action || p.action || '#';
    return '<div class="top-pick-card' + (isBest ? ' pick-best' : '') + '">' +
      '<div class="top-pick-label">' + escapeHtml(labels[i]) + '</div>' +
      '<div class="top-pick-vendor">' + escapeHtml(p.vendor) + '</div>' +
      '<div class="top-pick-plan">' + escapeHtml(p.plan) + ' ' + escapeHtml(p.type) + '</div>' +
      '<div class="top-pick-price">' + formatPrice(p.monthlyPrice, p.currency || '¥') + '<span class="top-pick-price-unit">/月</span></div>' +
      '<div class="top-pick-metrics">' +
        '<div><div class="top-pick-metric-value">' + tokenStr + '</div><div class="top-pick-metric-label">月Token</div></div>' +
        '<div><div class="top-pick-metric-value">' + tpu + '</div><div class="top-pick-metric-label">每元Token</div></div>' +
      '</div>' +
      (verdict ? '<div class="top-pick-reason" style="font-weight:700;color:var(--accent);">' + escapeHtml(verdict) + '</div>' : '') +
      (reasons ? '<ul class="reco-item-reasons" style="margin:var(--space-2) 0 var(--space-4);">' + reasons + '</ul>' : '') +
      '<div class="top-pick-action">' +
        '<a href="' + action + '" target="_blank" rel="nofollow sponsored" class="btn btn-primary btn-sm">优惠购买 →</a>' +
      '</div>' +
    '</div>';
  }).join('');

  const subtitle = groups[0] && groups[0].subtitle ? groups[0].subtitle : '基于评分、性价比和真实体验的综合推荐。';
  return '<section class="section-sm"><div class="container">' +
    '<div class="section-header" style="margin-bottom:var(--space-4);">' +
      '<span class="section-eyebrow">TOP PICKS</span>' +
      '<h2 class="section-title">不知道买哪个？看这三个就够了</h2>' +
      '<p class="section-subtitle">' + escapeHtml(subtitle) + '</p>' +
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
      // 平滑滚动到对比表（单页模式 router 只 resize 图表，不会自动滚）
      const target = document.getElementById('tab-compare');
      if (target) target.scrollIntoView({ behavior: 'smooth' });
    });
  });
}

function renderRecommendations() {
  const groups = site.recommendationGroups || [];
  // 跳过已被 Top3 卡片用掉的 top-picks 分组，避免重复展示
  const extra = groups.filter(g => g.id !== 'top-picks');
  if (!extra.length) return '';
  const html = extra.map((group, gi) => {
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
    const header = extra.length > 1
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
  const cutoff = new Date(now.getTime() - 14 * 24 * 60 * 60 * 1000);
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
    const titleHtml = c.sourceUrl
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
        '<p class="section-subtitle">最近 14 天影响套餐选择的关键变动。悬停查看详情。</p>' +
      '</div>' +
      '<div class="rc-list">' + items + '</div>' +
    '</div>' +
  '</section>';
}