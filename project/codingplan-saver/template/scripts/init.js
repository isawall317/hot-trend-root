// ============================================================
// Init — 单页模式，只渲染对比表
// ============================================================
document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('navBrand').textContent = site.name || 'CodingPlan 省钱攻略';
  const taglineEl = document.getElementById('navTagline');
  if (taglineEl) taglineEl.textContent = site.tagline || '';
  renderRecommend();
  renderCompare();
  renderFooter();
  // 对比表散点图在第二屏，延迟渲染
  setTimeout(() => {
    if (typeof echarts !== 'undefined') renderChart();
  }, 100);
});
