document.addEventListener('DOMContentLoaded',()=>{
  document.getElementById('navBrand').textContent=site.name||'AI Coding 经验库';
  renderRecommend();renderBrowse();renderCommunity();renderFooter();
  switchTab(location.hash||'#recommend');
});
