function renderRecommend(){
  document.getElementById('recommend-body').innerHTML=renderHero()+renderTopModels()+renderQuickEntries()+renderRecommendations()+renderRecentChanges();
  bindQuickEntries();
}
function renderHero(){
  const h=site.header||{};
  const stats=(h.stats||[]).map(s=>'<div><div class="hero-stat-value">'+escapeHtml(s.value)+'<span style="font-size:13px;color:var(--text-tertiary);font-weight:500;margin-left:2px;">'+escapeHtml(s.unit||'')+'</span></div><div class="hero-stat-label">'+escapeHtml(s.label)+'</div></div>').join('');
  return'<section class="hero"><div class="container"><div class="hero-inner"><div>'+
    '<span class="section-eyebrow">'+escapeHtml(h.updateDate||'')+'</span>'+
    '<h1 class="hero-title">AI 模型这么多<br><span class="hero-title-accent">选哪个最适合？</span></h1>'+
    '<p class="hero-subtitle">'+escapeHtml(site.tagline||'')+'</p>'+
    '<p style="font-size:13px;color:var(--text-tertiary);margin-bottom:var(--space-5);margin-top:-12px;">'+escapeHtml(h.highlights||'')+'</p>'+
    '<div class="hero-actions"><a href="#browse" class="btn btn-primary btn-lg">对比所有模型</a><a href="#community" class="btn btn-secondary btn-lg">加入社群</a></div>'+
    '<div class="hero-stats">'+stats+'</div></div></div></section>';
}
function renderTopModels(){
  const top3=models.filter(m=>m.featured).sort((a,b)=>b.rating-a.rating).slice(0,3);
  if(!top3.length)return'';
  const labels=['综合最佳','本周最热','性价比之王'];
  const reasons=['综合评分最高，编程和深度分析能力业界领先，适合严肃开发者。','最近一周最受关注的模型，全球榜单登顶，社区讨论度最高。','综合能力和价格的黄金平衡点，API价格极低但能力超强。'];
  const picks=top3.map((m,i)=>{
    const isBest=i===0;
    return'<div class="top-pick-card'+(isBest?' pick-best':'')+'">'+
      '<div class="top-pick-label">'+labels[i]+'</div>'+
      '<div class="top-pick-vendor">'+escapeHtml(m.name)+'</div>'+
      '<div class="top-pick-plan">'+escapeHtml(m.provider)+' · '+(TIER_LABELS[m.tier]||m.tier)+' · '+escapeHtml(m.category)+'</div>'+
      '<div style="margin-top:var(--space-3);">'+renderStars(m.rating)+'</div>'+
      '<div class="top-pick-metrics">'+
        '<div><div class="top-pick-metric-value">'+formatPrice(m.priceInput,m.currency||'¥')+'</div><div class="top-pick-metric-label">输入/1M tokens</div></div>'+
        '<div><div class="top-pick-metric-value">'+(m.contextWindow/1000).toFixed(0)+'K</div><div class="top-pick-metric-label">上下文窗口</div></div>'+
      '</div>'+
      '<div class="top-pick-reason">'+reasons[i]+'</div>'+
      '<div class="top-pick-action"><a href="#browse" class="btn btn-primary btn-sm">查看详情 →</a></div></div>';
  }).join('');
  return'<section class="section-sm"><div class="container">'+
    '<div class="section-header" style="margin-bottom:var(--space-4);">'+
      '<span class="section-eyebrow">TOP PICKS</span><h2 class="section-title">不知道选哪个？先看这三个</h2>'+
      '<p class="section-subtitle">基于评分、性价比和真实体验的综合推荐。点击场景卡片筛选或对比全部模型。</p></div>'+
    '<div class="top-pick-grid">'+picks+'</div></div></section>';
}
function renderQuickEntries(){
  const entries=site.quickEntries||[];if(!entries.length)return'';
  const cards=entries.map(q=>'<button class="quick-card" data-entry-id="'+escapeHtml(q.id)+'">'+
    '<span class="quick-card-icon">'+escapeHtml(q.icon)+'</span>'+
    '<span class="quick-card-title">'+escapeHtml(q.title)+'</span>'+
    '<span class="quick-card-desc">'+escapeHtml(q.desc)+'</span></button>').join('');
  return'<section class="section-sm"><div class="container">'+
    '<div class="section-header" style="margin-bottom:var(--space-4);"><span class="section-eyebrow">SCENARIOS</span><h2 class="section-title">按你的场景来找</h2></div>'+
    '<div class="quick-grid">'+cards+'</div></div></section>';
}
function bindQuickEntries(){
  document.querySelectorAll('.quick-card').forEach(card=>{card.addEventListener('click',()=>{
    const id=card.dataset.entryId;
    const entry=(site.quickEntries||[]).find(q=>q.id===id);
    if(!entry||!entry.filter)return;
    const query=Object.entries(entry.filter).map(([k,v])=>k+'='+encodeURIComponent(v)).join('&');
    location.hash='#browse'+(query?'?'+query:'');
  })});
}
function renderRecommendations(){
  const groups=site.recommendationGroups||[];if(!groups.length)return'';
  const html=groups.map((group,gi)=>{
    const items=(group.items||[]).map(item=>{
      const m=models.find(m=>m.id===item.modelId);if(!m)return'';
      return'<div class="reco-item">'+
        '<div class="reco-item-header"><div><div class="reco-item-vendor">'+escapeHtml(m.name)+'</div><div class="reco-item-plan">'+escapeHtml(m.provider)+' · '+(TIER_LABELS[m.tier]||m.tier)+'</div></div>'+renderStars(item.rating)+'</div>'+
        (item.verdict?'<span class="reco-item-verdict">'+escapeHtml(item.verdict)+'</span>':'')+
        '<p style="font-size:13px;color:var(--text-secondary);line-height:1.5;margin-bottom:var(--space-3);">'+escapeHtml(m.description)+'</p>'+
        '<ul class="reco-item-reasons" style="margin-bottom:var(--space-3);">'+(m.strengths||[]).slice(0,2).map(s=>'<li>'+escapeHtml(s)+'</li>').join('')+'</ul>'+
        '<div class="reco-item-footer">'+
          '<span style="font-size:12px;color:var(--text-tertiary);">输入 '+formatPrice(m.priceInput,m.currency||'¥')+'/1M</span>'+
          '<a href="#browse" class="btn btn-primary">查看详情 →</a></div></div>';
    }).join('');
    const header=groups.length>1?'<div style="margin-bottom:var(--space-4);"><h3 style="font-size:16px;font-weight:700;">'+escapeHtml(group.title)+'</h3>'+(group.subtitle?'<p style="font-size:13px;color:var(--text-tertiary);">'+escapeHtml(group.subtitle)+'</p>':'')+'</div>':'';
    return'<div style="'+(gi>0?'margin-top:var(--space-8);':'')+'">'+header+'<div class="reco-list">'+items+'</div></div>';
  }).join('');
  return'<section class="section-sm"><div class="container"><div class="section-header" style="margin-bottom:var(--space-4);"><span class="section-eyebrow">ALL RECOMMENDATIONS</span><h2 class="section-title">饭庐者说的完整推荐</h2></div>'+html+'</div></section>';
}
const KIND_LABEL={new_model:'新模型',price_change:'价格变动',article:'文章'};
function renderRecentChanges(){
  const now=new Date();const cutoff=new Date(now.getTime()-30*24*60*60*1000);
  const recent=(changes||[]).filter(c=>new Date(c.date)>=cutoff).sort((a,b)=>b.date.localeCompare(a.date));
  if(!recent.length)return'';
  const items=recent.map(c=>{
    const impactBadge=c.impact==='positive'?'<span class="badge badge-positive">利好</span>':c.impact==='negative'?'<span class="badge badge-negative">利空</span>':'<span class="badge">中性</span>';
    const kindLabel='<span class="tag">'+(KIND_LABEL[c.kind]||c.kind)+'</span>';
    const vendorPrefix=c.vendor&&c.vendor!=='通用'?'<span class="rc-vendor">'+escapeHtml(c.vendor)+'</span> · ':'';
    const isArticle=c.kind==='article';
    const titleHtml=isArticle&&c.sourceUrl?'<a href="'+escapeHtml(c.sourceUrl)+'" target="_blank" rel="noopener">'+escapeHtml(c.title)+'</a>':escapeHtml(c.title);
    const detailAttr=c.detail&&c.detail!==c.title?' data-detail="'+escapeHtml(c.detail).replace(/"/g,'&quot;')+'"':'';
    return'<div class="rc-item'+(c.featured?' rc-featured':'')+'"'+detailAttr+'>'+
      '<span class="rc-date">'+escapeHtml(c.date.slice(5))+'</span>'+impactBadge+
      '<span class="rc-title">'+vendorPrefix+titleHtml+'</span>'+kindLabel+'</div>';
  }).join('');
  return'<section class="section-sm"><div class="container"><div class="section-header" style="margin-bottom:var(--space-4);"><span class="section-eyebrow">RECENT CHANGES</span><h2 class="section-title">最近动态 · 模型生态变化</h2><p class="section-subtitle">最近30天模型发布和价格变动。悬停查看详情。</p></div><div class="rc-list">'+items+'</div></div></section>';
}