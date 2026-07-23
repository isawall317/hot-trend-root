function renderRecommend(){
  document.getElementById('recommend-body').innerHTML=renderHero()+renderTopTips()+renderQuickEntries()+renderRecommendations()+renderRecentChanges();
  bindQuickEntries();
}
function renderHero(){
  const h=site.header||{};
  const stats=(h.stats||[]).map(s=>'<div><div class="hero-stat-value">'+escapeHtml(s.value)+'<span style="font-size:13px;color:var(--text-tertiary);font-weight:500;margin-left:2px;">'+escapeHtml(s.unit||'')+'</span></div><div class="hero-stat-label">'+escapeHtml(s.label)+'</div></div>').join('');
  return'<section class="hero"><div class="container"><div class="hero-inner"><div>'+
    '<span class="section-eyebrow">'+escapeHtml(h.updateDate||'')+'</span>'+
    '<h1 class="hero-title">AI 编程经验<br><span class="hero-title-accent">不再随聊天记录消失</span></h1>'+
    '<p class="hero-subtitle">'+escapeHtml(site.tagline||'')+'</p>'+
    '<p style="font-size:13px;color:var(--text-tertiary);margin-bottom:var(--space-5);margin-top:-12px;">'+escapeHtml(h.highlights||'')+'</p>'+
    '<div class="hero-actions"><a href="#browse" class="btn btn-primary btn-lg">浏览全部经验</a><a href="#community" class="btn btn-secondary btn-lg">加入社群</a></div>'+
    '<div class="hero-stats">'+stats+'</div></div></div></section>';
}
function renderTopTips(){
  const top3=tips.filter(t=>t.featured).sort((a,b)=>b.rating-a.rating).slice(0,3);
  if(!top3.length)return'';
  const labels=['综合最佳','最实用','必读首选'];
  const reasons=['综合评分最高，这条经验能从根本上改变你的AI编程方式。','社区反馈最实用，最多人表示「早点看到就好了」。','每个AI编程用户都应该知道的基础知识，花5分钟读完受益终身。'];
  return'<section class="section-sm"><div class="container"><div class="section-header" style="margin-bottom:var(--space-4);"><span class="section-eyebrow">TOP TIPS</span><h2 class="section-title">不知道从哪开始？先看这三条</h2><p class="section-subtitle">基于评分和实用性的综合推荐。点击场景卡片筛选或浏览全部经验。</p></div><div class="top-pick-grid">'+top3.map((t,i)=>{const isBest=i===0;return'<div class="top-pick-card'+(isBest?' pick-best':'')+'"><div class="top-pick-label">'+labels[i]+'</div><div class="top-pick-vendor">'+escapeHtml(t.title)+'</div><div class="top-pick-plan">'+(CAT_LABELS[t.category]||t.category)+' · '+escapeHtml(t.author)+'</div><div style="margin-top:var(--space-3);">'+renderStars(t.rating)+'</div><div class="top-pick-metrics"><div><div class="top-pick-metric-value">'+(t.steps||[]).length+'</div><div class="top-pick-metric-label">步骤</div></div><div><div class="top-pick-metric-value">'+(t.relatedTools||[]).length+'</div><div class="top-pick-metric-label">相关工具</div></div></div><div class="top-pick-reason">'+reasons[i]+'</div><div class="top-pick-action"><a href="#browse" class="btn btn-primary btn-sm">查看详情 →</a></div></div>'}).join('')+'</div></div></section>';
}
function renderQuickEntries(){
  const entries=site.quickEntries||[];if(!entries.length)return'';
  return'<section class="section-sm"><div class="container"><div class="section-header" style="margin-bottom:var(--space-4);"><span class="section-eyebrow">SCENARIOS</span><h2 class="section-title">按你的场景来找</h2></div><div class="quick-grid">'+entries.map(q=>'<button class="quick-card" data-entry-id="'+escapeHtml(q.id)+'"><span class="quick-card-icon">'+escapeHtml(q.icon)+'</span><span class="quick-card-title">'+escapeHtml(q.title)+'</span><span class="quick-card-desc">'+escapeHtml(q.desc)+'</span></button>').join('')+'</div></div></section>';
}
function bindQuickEntries(){
  document.querySelectorAll('.quick-card').forEach(card=>{card.addEventListener('click',()=>{
    const id=card.dataset.entryId;const entry=(site.quickEntries||[]).find(q=>q.id===id);
    if(!entry||!entry.filter)return;
    const query=Object.entries(entry.filter).map(([k,v])=>k+'='+encodeURIComponent(v)).join('&');
    location.hash='#browse'+(query?'?'+query:'');
  })});
}
function renderRecommendations(){
  const groups=site.recommendationGroups||[];if(!groups.length)return'';
  const html=groups.map((group,gi)=>{const items=(group.items||[]).map(item=>{const t=tips.find(t=>t.id===item.tipId);if(!t)return'';return'<div class="reco-item"><div class="reco-item-header"><div><div class="reco-item-vendor">'+escapeHtml(t.title)+'</div><div class="reco-item-plan">'+(CAT_LABELS[t.category]||t.category)+' · '+escapeHtml(t.author)+'</div></div>'+renderStars(item.rating)+'</div>'+(item.verdict?'<span class="reco-item-verdict">'+escapeHtml(item.verdict)+'</span>':'')+'<p style="font-size:13px;color:var(--text-secondary);line-height:1.5;margin-bottom:var(--space-3);">'+escapeHtml(t.description)+'</p><div style="background:var(--bg-elevated);border-radius:var(--radius-md);padding:var(--space-3);margin-bottom:var(--space-3);"><strong style="color:var(--accent);font-size:11px;">💡 一句话总结</strong><p style="font-size:13px;color:var(--text-primary);margin-top:2px;">'+escapeHtml(t.takeaway)+'</p></div><div class="reco-item-footer"><span style="font-size:12px;color:var(--text-tertiary);">'+(t.steps||[]).length+' 个步骤</span><a href="#browse" class="btn btn-primary">查看详情 →</a></div></div>'}).join('');const header=groups.length>1?'<div style="margin-bottom:var(--space-4);"><h3 style="font-size:16px;font-weight:700;">'+escapeHtml(group.title)+'</h3>'+(group.subtitle?'<p style="font-size:13px;color:var(--text-tertiary);">'+escapeHtml(group.subtitle)+'</p>':'')+'</div>':'';return'<div style="'+(gi>0?'margin-top:var(--space-8);':'')+'">'+header+'<div class="reco-list">'+items+'</div></div>'}).join('');return'<section class="section-sm"><div class="container"><div class="section-header" style="margin-bottom:var(--space-4);"><span class="section-eyebrow">ALL RECOMMENDATIONS</span><h2 class="section-title">饭庐者说的完整推荐</h2></div>'+html+'</div></section>';
}
const KIND_LABEL={new_tip:'新经验',article:'文章',tip_update:'更新'};
function renderRecentChanges(){const now=new Date();const cutoff=new Date(now.getTime()-30*24*60*60*1000);const recent=(changes||[]).filter(c=>new Date(c.date)>=cutoff).sort((a,b)=>b.date.localeCompare(a.date));if(!recent.length)return'';const items=recent.map(c=>{const impactBadge=c.impact==='positive'?'<span class="badge badge-positive">利好</span>':c.impact==='negative'?'<span class="badge badge-negative">利空</span>':'<span class="badge">中性</span>';const kindLabel='<span class="tag">'+(KIND_LABEL[c.kind]||c.kind)+'</span>';const titleHtml=c.kind==='article'&&c.sourceUrl?'<a href="'+escapeHtml(c.sourceUrl)+'" target="_blank" rel="noopener">'+escapeHtml(c.title)+'</a>':escapeHtml(c.title);const detailAttr=c.detail&&c.detail!==c.title?' data-detail="'+escapeHtml(c.detail).replace(/"/g,'&quot;')+'"':'';return'<div class="rc-item'+(c.featured?' rc-featured':'')+'"'+detailAttr+'><span class="rc-date">'+escapeHtml(c.date.slice(5))+'</span>'+impactBadge+'<span class="rc-title">'+titleHtml+'</span>'+kindLabel+'</div>'}).join('');return'<section class="section-sm"><div class="container"><div class="section-header" style="margin-bottom:var(--space-4);"><span class="section-eyebrow">RECENT CHANGES</span><h2 class="section-title">最近动态</h2><p class="section-subtitle">最近30天的新经验和社区动态。悬停查看详情。</p></div><div class="rc-list">'+items+'</div></div></section>';}
