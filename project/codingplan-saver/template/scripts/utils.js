// Utils（移植自 V1 shared.js）
function escapeHtml(text) {
  if (text === null || text === undefined) return '';
  const div = document.createElement('div');
  div.textContent = String(text);
  return div.innerHTML;
}
function formatPrice(value, currency) {
  if (value === null || value === undefined || value === '-' || value === '') return '—';
  if (typeof value === 'string') return value;
  const prefix = currency === '$' ? '$' : '¥';
  return prefix + value;
}
function formatNumber(value) {
  if (value === null || value === undefined || value === '-') return '—';
  if (typeof value === 'string') return value;
  if (value >= 1000) return value.toLocaleString();
  return value;
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
function vendorColor(name) {
  const v = vendors.find(x => x.name === name);
  return v && v.color ? v.color : '#71717B';
}