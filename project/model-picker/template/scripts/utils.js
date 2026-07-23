// Utils
function escapeHtml(t){if(t===null||t===undefined)return'';const d=document.createElement('div');d.textContent=String(t);return d.innerHTML}
function renderStars(r){const f='★'.repeat(r),e='☆'.repeat(5-r);return'<span class="stars">'+f+'</span><span class="stars stars-dim">'+e+'</span>'}
function renderTagsInline(t){if(!t||!t.length)return'';return t.map(t=>'<span class="tag">'+escapeHtml(t)+'</span>').join(' ')}
function formatPrice(v,c){if(v===null||v===undefined)return'—';const p=c==='$'?'$':'¥';return v===0?'免费':p+v}

const TASK_LABELS={coding:'编程',writing:'写作',vision:'多模态',chat:'对话',analysis:'分析'};
const TIER_LABELS={premium:'旗舰',mid:'中档',budget:'入门'};
const TIER_CSS={premium:'badge-premium',mid:'badge-accent',budget:'badge-positive'};