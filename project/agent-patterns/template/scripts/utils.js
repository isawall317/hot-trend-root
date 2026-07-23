function escapeHtml(t){if(t===null||t===undefined)return'';const d=document.createElement('div');d.textContent=String(t);return d.innerHTML}
function renderStars(r){const f='★'.repeat(r),e='☆'.repeat(5-r);return'<span class="stars">'+f+'</span><span class="stars stars-dim">'+e+'</span>'}
function renderTagsInline(t){if(!t||!t.length)return'';return t.map(t=>'<span class="tag">'+escapeHtml(t)+'</span>').join(' ')}
const LEVEL_LABELS={basic:'基础',advanced:'进阶',multi:'多Agent',production:'生产级'};
const LEVEL_CSS={basic:'badge-positive',advanced:'badge-accent',multi:'badge-warning',production:'badge-premium'};
