// 单页模式，无 Tab 切换。保留 hashchange 监听以兼容旧书签。
function switchTab() {
  // 不再有 Tab，但散点图可能需要 resize
  if (window._chart) window._chart.resize();
}
window.addEventListener('hashchange', () => switchTab(location.hash));
