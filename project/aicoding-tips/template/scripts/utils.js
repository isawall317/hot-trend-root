function escapeHtml(t){if(t===null||t===undefined)return'';const d=document.createElement('div');d.textContent=String(t);return d.innerHTML}
function renderStars(r){const f='★'.repeat(r),e='☆'.repeat(5-r);return'<span class="stars">'+f+'</span><span class="stars stars-dim">'+e+'</span>'}
function renderTagsInline(t){if(!t||!t.length)return'';return t.map(t=>'<span class="tag">'+escapeHtml(t)+'</span>').join(' ')}
const CAT_LABELS={prompts:'Prompt技巧',workflow:'工作流',tools:'工具配置',debug:'排错Debug'};