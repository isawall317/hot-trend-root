const browseState={filters:{categories:new Set,tiers:new Set,search:''},sort:{key:null,dir:'asc'}};

function renderBrowse(){
  document.getElementById('browse-body').innerHTML=renderBrowseSection();
  bindBrowseFilters();renderModelCards();
}
function renderBrowseSection(){
  return'<section class="section-sm"><div class="container">'+
    '<div class="section-header" style="display:flex;justify-content:space-between;align-items:flex-end;flex-wrap:wrap;gap:var(--space-3);">'+
      '<div><span class="section-eyebrow">COMPARE ALL</span><h2 class="section-title">全部模型对比</h2><p class="section-subtitle">点击分类筛选，搜索模型名或厂商。找到最适合你的模型。</p></div></div>'+
    '<div id="browseFilterBar"></div><div class="model-grid" id="modelGrid"></div></div></section>';
}
function renderBrowseFilterBar(){
  const categories=[...new Set(models.map(m=>m.category))].sort();
  const tiers=[...new Set(models.map(m=>m.tier))].sort();
  const catChips=categories.map(c=>'<button class="filter-chip" data-filter-type="categories" data-filter-value="'+escapeHtml(c)+'">'+(c==='commercial'?'商业模型':c==='open-source'?'开源模型':c)+'</button>').join('');
  const tierChips=tiers.map(t=>'<button class="filter-chip" data-filter-type="tiers" data-filter-value="'+escapeHtml(t)+'">'+(TIER_LABELS[t]||t)+'</button>').join('');
  return'<div class="filter-bar">'+
    '<select class="filter-select" id="sortSelect">'+
      '<option value="">默认排序</option><option value="rating-desc">评分 高-低</option>'+
      '<option value="priceInput-asc">价格 低-高</option><option value="contextWindow-desc">上下文 大-小</option></select>'+
    '<input type="text" class="filter-select" id="searchInput" placeholder="搜索模型名/厂商..." style="min-width:200px;">'+
    '<button class="filter-chip" id="resetBtn">重置</button>'+
    '<span class="filter-stats">显示 <strong id="filterCount">0</strong> / '+models.length+' 个模型</span></div>'+
    (catChips?'<div class="filter-bar"><span style="font-size:11px;font-weight:700;color:var(--text-muted);">类型:</span>'+catChips+'</div>':'')+
    (tierChips?'<div class="filter-bar"><span style="font-size:11px;font-weight:700;color:var(--text-muted);">档次:</span>'+tierChips+'</div>':'');
}
function parseHashFilter(){
  const hash=location.hash;const qIdx=hash.indexOf('?');if(qIdx<0)return null;
  const params=new URLSearchParams(hash.slice(qIdx+1));const f={};
  for(const[k,v]of params)f[k]=v;return f;
}
function bindBrowseFilters(){
  const fm=document.getElementById('browseFilterBar');if(!fm)return;fm.innerHTML=renderBrowseFilterBar();
  const hashFilter=parseHashFilter();
  if(hashFilter){
    if(hashFilter.task){const taskMap={coding:'编程',writing:'写作',vision:'多模态'};browseState.filters.search=taskMap[hashFilter.task]||hashFilter.task;const si=document.getElementById('searchInput');if(si)si.value=browseState.filters.search}
    if(hashFilter.tier)browseState.filters.tiers.add(hashFilter.tier);
  }
  syncFilterUI();
  fm.querySelectorAll('.filter-chip[data-filter-type]').forEach(chip=>{chip.addEventListener('click',()=>{
    const type=chip.dataset.filterType,value=chip.dataset.filterValue,set=browseState.filters[type];
    if(set.has(value))set.delete(value);else set.add(value);syncFilterUI();renderModelCards();
  })});
  document.getElementById('resetBtn')?.addEventListener('click',()=>{
    browseState.filters.categories.clear();browseState.filters.tiers.clear();browseState.filters.search='';browseState.sort={key:null,dir:'asc'};
    document.getElementById('sortSelect').value='';document.getElementById('searchInput').value='';syncFilterUI();renderModelCards();
  });
  document.getElementById('sortSelect')?.addEventListener('change',()=>{
    const val=document.getElementById('sortSelect').value;
    if(!val)browseState.sort={key:null,dir:'asc'};else{const[k,d]=val.split('-');browseState.sort={key:k,dir:d}}renderModelCards();
  });
  document.getElementById('searchInput')?.addEventListener('input',()=>{browseState.filters.search=document.getElementById('searchInput').value.trim().toLowerCase();renderModelCards();});
}
function syncFilterUI(){
  document.querySelectorAll('.filter-chip[data-filter-type]').forEach(chip=>{
    const type=chip.dataset.filterType,value=chip.dataset.filterValue,active=browseState.filters[type]&&browseState.filters[type].has(value);
    chip.classList.toggle('active',!!active);
  });
}
function filterModels(){
  const f=browseState.filters;let result=models.filter(m=>{
    if(f.categories.size&&!f.categories.has(m.category))return false;
    if(f.tiers.size&&!f.tiers.has(m.tier))return false;
    if(f.search){const hay=(m.name+' '+m.provider+' '+m.description+' '+(m.bestFor||[]).join(' ')+(m.strengths||[]).join(' ')).toLowerCase();if(!hay.includes(f.search))return false}
    return true;
  });
  const{key,dir}=browseState.sort;
  if(key)result.sort((a,b)=>{const av=a[key],bv=b[key];const aNum=typeof av==='number'?av:0;const bNum=typeof bv==='number'?bv:0;return dir==='asc'?aNum-bNum:bNum-aNum});
  return result;
}
function renderModelCards(){
  const filtered=filterModels();
  const countEl=document.getElementById('filterCount');if(countEl)countEl.textContent=filtered.length;
  const grid=document.getElementById('modelGrid');
  if(!filtered.length){if(grid)grid.innerHTML='<div style="text-align:center;padding:48px;color:var(--text-muted);grid-column:1/-1;">没有匹配的模型，试试重置筛选</div>';return}
  if(grid)grid.innerHTML=filtered.map(m=>{
    const strengths=(m.strengths||[]).slice(0,2).map(s=>'<li>'+escapeHtml(s)+'</li>').join('');
    const weaknesses=(m.weaknesses||[]).slice(0,2).map(w=>'<li>'+escapeHtml(w)+'</li>').join('');
    const isFeatured=m.featured;const trendingBadge=m.trending?'<span class="badge badge-warning" style="font-size:10px;">🔥 热门</span>':'';
    const featuredBadge=isFeatured?'<span class="badge badge-accent" style="font-size:10px;">⭐ 精选</span>':'';
    return'<div class="model-card'+(isFeatured?' featured':'')+'">'+
      '<div class="model-card-header"><div><div class="model-card-name">'+escapeHtml(m.name)+' '+trendingBadge+featuredBadge+'</div><div class="model-card-scenario">'+escapeHtml(m.provider)+' · '+(TIER_LABELS[m.tier]||m.tier)+'</div></div><span class="badge '+TIER_CSS[m.tier]+'">'+(TIER_LABELS[m.tier]||m.tier)+'</span></div>'+
      '<p class="model-card-desc">'+escapeHtml(m.description)+'</p>'+
      '<div class="model-card-tags">'+(m.bestFor||[]).slice(0,4).map(t=>'<span class="tag">'+escapeHtml(t)+'</span>').join(' ')+'</div>'+
      '<div class="model-card-meta">'+
        '<div><div class="model-card-meta-value">'+renderStars(m.rating)+'</div><div class="model-card-meta-item">评分</div></div>'+
        '<div><div class="model-card-meta-value">'+formatPrice(m.priceInput,m.currency||'¥')+'</div><div class="model-card-meta-item">输入/1M</div></div>'+
        '<div><div class="model-card-meta-value">'+formatPrice(m.priceOutput,m.currency||'¥')+'</div><div class="model-card-meta-item">输出/1M</div></div>'+
        '<div><div class="model-card-meta-value">'+(m.contextWindow/1000).toFixed(0)+'K</div><div class="model-card-meta-item">上下文</div></div>'+
      '</div>'+
      '<div class="model-card-pros-cons">'+
        (strengths?'<div class="model-card-pros"><strong>👍 优势</strong><ul>'+strengths+'</ul></div>':'<div></div>')+
        (weaknesses?'<div class="model-card-cons"><strong>👎 注意</strong><ul>'+weaknesses+'</ul></div>':'<div></div>')+
      '</div>'+
      '<div class="model-card-footer"><span style="font-size:12px;color:var(--text-tertiary);">'+(m.languages||[]).slice(0,2).map(l=>escapeHtml(l)).join(' · ')+'</span><a href="'+(m.apiUrl||'#')+'" target="_blank" rel="nofollow sponsored" class="btn btn-primary btn-sm">定价页 →</a></div></div>';
  }).join('');
}