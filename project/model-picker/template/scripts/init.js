document.addEventListener('DOMContentLoaded',()=>{
  document.getElementById('navBrand').textContent=site.name||'AI 模型选型助手';
  renderRecommend();renderBrowse();renderCommunity();renderFooter();
  switchTab(location.hash||'#recommend');
});