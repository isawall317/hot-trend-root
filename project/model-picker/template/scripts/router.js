// Tab 路由
function switchTab(hash){
  const tab=(hash||'#recommend').replace(/^#/,'').split('?')[0];
  const validTabs=['recommend','browse','community'];
  const target=validTabs.includes(tab)?tab:'recommend';
  document.querySelectorAll('.tab-panel').forEach(p=>p.classList.remove('active'));
  document.getElementById('tab-'+target).classList.add('active');
  document.querySelectorAll('.nav-tab').forEach(t=>t.classList.toggle('active',t.dataset.tab===target));
  window.scrollTo({top:0,behavior:'smooth'});
}
window.addEventListener('hashchange',()=>switchTab(location.hash));