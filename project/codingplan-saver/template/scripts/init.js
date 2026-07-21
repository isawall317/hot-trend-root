// ============================================================
// Init — 页面加载时初始化所有 Tab
// ============================================================
document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('navBrand').textContent = site.name || 'CodingPlan 省钱攻略';
  renderRecommend();
  renderCompare();
  renderCommunity();
  renderFooter();
  switchTab(location.hash || '#recommend');
});