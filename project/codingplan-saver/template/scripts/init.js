// ============================================================
// Init — 单页模式，只渲染对比表
// ============================================================
document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('navBrand').textContent = site.name || 'CodingPlan 省钱攻略';
  const taglineEl = document.getElementById('navTagline');
  if (taglineEl) taglineEl.textContent = site.tagline || '';
  renderCompare();
  renderFooter();
  // 单页模式，对比表是首屏，直接渲染散点图
  setTimeout(() => {
    if (typeof echarts !== 'undefined') renderChart();
  }, 100);
});
