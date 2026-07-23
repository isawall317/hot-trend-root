// ============================================================
// Init — 页面加载时初始化所有 Tab
// ============================================================
document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('navBrand').textContent = site.name || 'Claude Code Skills 精选';
  renderRecommend();
  renderBrowse();
  renderCommunity();
  renderFooter();
  switchTab(location.hash || '#recommend');
});