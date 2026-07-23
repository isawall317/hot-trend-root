// Utils
function escapeHtml(text) {
  if (text === null || text === undefined) return '';
  const div = document.createElement('div');
  div.textContent = String(text);
  return div.innerHTML;
}
function renderStars(rating) {
  const full = '★'.repeat(rating);
  const empty = '☆'.repeat(5 - rating);
  return '<span class="stars">' + full + '</span><span class="stars stars-dim">' + empty + '</span>';
}
function renderTagsInline(tags) {
  if (!tags || !tags.length) return '';
  return tags.map(t => '<span class="tag">' + escapeHtml(t) + '</span>').join(' ');
}
function renderMarkdownLite(text) {
  if (!text) return '';
  let html = escapeHtml(text);
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
  return html;
}

const SCENARIO_LABELS = {
  frontend: '前端开发', backend: '后端开发', fullstack: '全栈开发',
  solo: '独立开发', team: '团队协作', prototype: '快速原型',
  docs: '文档写作', devops: 'DevOps', ui: 'UI设计',
  oss: '开源维护', learning: '学习入门', mobile: '移动端',
  research: '学术研究', quality: '质量保障'
};
const TYPE_CSS = {
  frontend: 'sc-frontend', backend: 'sc-backend', fullstack: 'sc-fullstack',
  solo: 'sc-solo', team: 'sc-team'
};
const DIFFICULTY_LABELS = { '入门': '🟢 入门', '进阶': '🟡 进阶', '专家': '🔴 专家' };
const COST_LABELS = { '免费': '免费', '低成本': '低成本', '中等': '中等', '高': '高费用' };

function scenarioLabel(s) { return SCENARIO_LABELS[s] || s; }
function scenarioCss(s) { return SCENARIO_CSS[s] || ''; }