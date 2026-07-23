document.addEventListener('DOMContentLoaded',()=>{
  document.getElementById('navBrand').textContent=site.name||'AI Agent 模式库';
  renderRecommend();renderBrowse();renderCommunity();renderFooter();
  switchTab(location.hash||'#recommend');
});
