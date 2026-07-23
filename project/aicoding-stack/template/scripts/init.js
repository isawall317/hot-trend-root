document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('navBrand').textContent = site.name || 'AI Coding 工具组合';
  renderRecommend();
  renderBrowse();
  renderCommunity();
  renderFooter();
  switchTab(location.hash || '#recommend');
});