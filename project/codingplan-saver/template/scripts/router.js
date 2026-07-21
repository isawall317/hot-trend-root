// Tab 路由
function switchTab(hash) {
  const tab = (hash || '#recommend').replace(/^#/, '').split('?')[0];
  const validTabs = ['recommend', 'compare', 'community'];
  const target = validTabs.includes(tab) ? tab : 'recommend';

  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  document.getElementById('tab-' + target).classList.add('active');
  document.querySelectorAll('.nav-tab').forEach(t => t.classList.toggle('active', t.dataset.tab === target));
  window.scrollTo({ top: 0, behavior: 'smooth' });

  // 对比 tab：首次进入渲染散点图，后续进入 resize
  if (target === 'compare') {
    setTimeout(() => {
      if (window._chart) {
        window._chart.resize();
      } else if (typeof echarts !== 'undefined') {
        renderChart();
      }
    }, 100);
  }
}
window.addEventListener('hashchange', () => switchTab(location.hash));