// ============================================================
// Tab 3: 社群 + Footer
// ============================================================
function renderCommunity() {
  const body = document.getElementById('community-body');
  const c = site.community;
  if (!c) { body.innerHTML = ''; return; }
  body.innerHTML = '<section class="section-sm"><div class="container">' +
    '<div class="section-header text-center">' +
      '<span class="section-eyebrow">COMMUNITY</span>' +
      '<h2 class="section-title">不止看数据，来群里聊</h2>' +
      '<p class="section-subtitle" style="margin:0 auto;">Skill 创作者申请精选位，让你的作品被 10 万+ 开发者看到。标注「赞助」保持透明。</p>' +
    '</div>' +
    '<div class="community-grid">' +
      renderCommunityCard(c.free, 'free', 'FREE', 'badge-accent', 'join.html') +
      renderCommunityCard(c.paid, 'paid', 'PRO', 'badge-premium', c.paid && c.paid.url ? c.paid.url : '#') +
    '</div>' +
  '</div></section>';
}

function renderCommunityCard(card, type, badgeText, badgeClass, actionUrl) {
  if (!card) return '';
  const highlights = (card.highlights || []).map(h => '<li>' + escapeHtml(h) + '</li>').join('');
  return '<div class="community-card community-card-' + type + '">' +
    '<div class="community-card-header"><h3 class="community-card-title">' + escapeHtml(card.title) + '</h3><span class="badge ' + badgeClass + '">' + badgeText + '</span></div>' +
    '<div class="community-card-subtitle">' + escapeHtml(card.subtitle) + '</div>' +
    '<p class="community-card-desc">' + escapeHtml(card.description) + '</p>' +
    '<ul class="community-highlights">' + highlights + '</ul>' +
    '<a href="' + escapeHtml(actionUrl) + '" class="btn ' + (type === 'paid' ? 'btn-primary' : 'btn-secondary') + ' btn-lg">' + escapeHtml(card.ctaText) + '</a>' +
  '</div>';
}

function renderFooter() {
  const fb = document.getElementById('footer-body');
  if (!fb) return;
  const links = (site.footer && site.footer.links || []).map(l => '<a href="' + escapeHtml(l.url) + '">' + escapeHtml(l.label) + '</a>').join('');
  fb.innerHTML =
    '<div class="footer-disclosure">' + escapeHtml(site.disclosure || '') + '</div>' +
    '<div class="footer-inner">' +
      '<div class="footer-brand">' + escapeHtml((site.footer && site.footer.about) || '') + '</div>' +
      '<div class="footer-links">' + links + '</div>' +
    '</div>';
}