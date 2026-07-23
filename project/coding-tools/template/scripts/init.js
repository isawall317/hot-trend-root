document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('navBrand').textContent = site.name || 'AI Coding 工具对比';
  renderRecommend();
  renderBrowse();
  renderCommunity();
  renderFooter();
  switchTab(location.hash || '#recommend');
});