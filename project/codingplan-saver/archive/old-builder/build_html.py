"""
HTML 生成器 — 将数据和模板合并为单个独立 HTML 文件

输出: dist/codingplan-saver.html
  - 所有 CSS 内联
  - 所有 JS 内联
  - 所有数据嵌入
  - 多 Tab 页面结构
"""

import json
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DIST_DIR = PROJECT_ROOT / "dist"
SAVER_DIR = PROJECT_ROOT / "project" / "codingplan-saver"

# 数据文件
CONFIG_PATH = SAVER_DIR / "config.json"
PLANS_PATH = SAVER_DIR / "plans.json"
ARTICLES_PATH = SAVER_DIR / "articles.json"
PRICE_CHANGES_PATH = SAVER_DIR / "price-changes.json"

# CSS 文件
CSS_PATH = SAVER_DIR / "styles" / "shared.css"


def load_json(path: Path) -> dict | list:
    if not path.exists():
        return {} if path.suffix == ".json" else []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_text(path: Path) -> str:
    if not path.exists():
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def build_html() -> str:
    """生成完整的单文件 HTML"""
    config = load_json(CONFIG_PATH)
    plans = load_json(PLANS_PATH)
    articles = load_json(ARTICLES_PATH)
    price_changes = load_json(PRICE_CHANGES_PATH)
    css = load_text(CSS_PATH)

    # 嵌入数据
    embedded_data = json.dumps({
        "config": config,
        "plans": plans,
        "articles": articles,
        "priceChanges": price_changes,
        "generatedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }, ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CodingPlan 省钱攻略 - AI Coding Plan 选型指南</title>
<meta name="description" content="20个平台、31个套餐全方位对比。饭庐者说帮你选最划算的 AI Coding Plan。">
<style>
{css}

/* ===== Additional Styles for Single Page ===== */
.tab-panel {{ display: none; }}
.tab-panel.active {{ display: block; }}

.top-pick-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--space-4); }}
.top-pick-card {{
  background: var(--bg-card); border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg); padding: var(--space-5); position: relative; overflow: hidden;
}}
.top-pick-card.pick-best {{
  border-color: rgba(16, 185, 129, 0.3);
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.06), var(--bg-card));
}}
.top-pick-card.pick-best::before {{
  content: 'BEST'; position: absolute; top: 12px; right: -28px;
  background: var(--accent); color: #090d14; font-size: 10px; font-weight: 800;
  padding: 2px 32px; transform: rotate(45deg); letter-spacing: 0.08em;
}}
.top-pick-label {{ font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; color: var(--text-muted); margin-bottom: var(--space-2); }}
.top-pick-vendor {{ font-size: 18px; font-weight: 700; margin-bottom: var(--space-1); }}
.top-pick-plan {{ font-size: 13px; color: var(--text-tertiary); margin-bottom: var(--space-3); }}
.top-pick-price {{ font-size: 28px; font-weight: 800; font-family: var(--font-mono); color: var(--accent); }}
.top-pick-price-unit {{ font-size: 13px; font-weight: 500; color: var(--text-tertiary); }}
.top-pick-metrics {{ display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-2); margin-top: var(--space-3); padding-top: var(--space-3); border-top: 1px solid var(--border-subtle); }}
.top-pick-metric-value {{ font-size: 14px; font-weight: 700; font-family: var(--font-mono); }}
.top-pick-metric-label {{ font-size: 10px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.04em; }}
.top-pick-reason {{ font-size: 12px; color: var(--text-secondary); line-height: 1.5; margin-top: var(--space-3); padding: var(--space-3); background: var(--bg-elevated); border-radius: var(--radius-md); }}

.scenario-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: var(--space-3); }}
.scenario-card {{
  padding: var(--space-4); background: var(--bg-card); border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg); cursor: pointer; transition: all 0.15s ease;
}}
.scenario-card:hover {{ border-color: var(--accent); background: var(--bg-card-hover); transform: translateY(-1px); }}
.scenario-card-label {{ font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; color: var(--text-muted); margin-bottom: var(--space-1); }}
.scenario-card-title {{ font-size: 14px; font-weight: 700; margin-bottom: var(--space-1); }}
.scenario-card-desc {{ font-size: 12px; color: var(--text-tertiary); }}

.reco-list {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(340px, 1fr)); gap: var(--space-4); }}
.reco-item {{
  background: var(--bg-card); border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg); padding: var(--space-5); transition: all 0.15s ease;
}}
.reco-item:hover {{ border-color: var(--border-strong); transform: translateY(-1px); box-shadow: var(--shadow-md); }}
.reco-item-header {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: var(--space-2); }}
.reco-item-vendor {{ font-size: 17px; font-weight: 700; }}
.reco-item-plan {{ font-size: 12px; color: var(--text-tertiary); }}
.reco-item-verdict {{ display: inline-block; font-size: 12px; font-weight: 600; color: var(--accent); background: var(--accent-soft); padding: 2px var(--space-3); border-radius: var(--radius-full); margin-bottom: var(--space-3); }}
.reco-item-reasons {{ display: flex; flex-direction: column; gap: var(--space-2); margin-bottom: var(--space-4); }}
.reco-item-reasons li {{ position: relative; padding-left: var(--space-4); font-size: 13px; line-height: 1.5; color: var(--text-secondary); }}
.reco-item-reasons li::before {{ content: ''; position: absolute; left: 0; top: 7px; width: 5px; height: 5px; border-radius: 50%; background: var(--accent); }}
.reco-item-footer {{ display: flex; justify-content: space-between; align-items: center; padding-top: var(--space-3); border-top: 1px solid var(--border-subtle); }}

.blog-layout {{ max-width: 900px; margin: 0 auto; }}
.search-bar {{ display: flex; gap: var(--space-3); margin-bottom: var(--space-4); }}
.search-input {{
  flex: 1; padding: var(--space-2) var(--space-4); background: var(--bg-card);
  border: 1px solid var(--border-default); border-radius: var(--radius-md);
  color: var(--text-primary); font-size: 14px; outline: none; transition: border-color 0.15s;
}}
.search-input:focus {{ border-color: var(--accent); }}
.search-input::placeholder {{ color: var(--text-muted); }}

.filter-section {{ margin-bottom: var(--space-3); }}
.filter-label {{ font-size: 11px; font-weight: 700; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: var(--space-2); }}
.filter-row {{ display: flex; flex-wrap: wrap; gap: var(--space-2); }}

.toolbar {{ display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: var(--space-3); margin-bottom: var(--space-4); padding-bottom: var(--space-3); border-bottom: 1px solid var(--border-subtle); }}
.sort-btn {{ font-size: 12px; padding: var(--space-1) var(--space-3); border-radius: var(--radius-sm); color: var(--text-tertiary); cursor: pointer; transition: all 0.12s; }}
.sort-btn:hover {{ color: var(--text-primary); }}
.sort-btn.active {{ color: var(--accent); font-weight: 700; }}

.article-item {{
  display: grid; grid-template-columns: 1fr; gap: var(--space-2);
  padding: var(--space-4); border-bottom: 1px solid var(--border-subtle); transition: background 0.12s;
}}
.article-item:hover {{ background: var(--bg-card); }}
.article-item-top {{ display: flex; justify-content: space-between; align-items: flex-start; gap: var(--space-3); }}
.article-item-title {{ font-size: 15px; font-weight: 600; line-height: 1.4; color: var(--text-primary); flex: 1; }}
.article-item-title a {{ color: inherit; text-decoration: none; transition: color 0.12s; }}
.article-item-title a:hover {{ color: var(--accent); }}
.article-item-badge {{ flex-shrink: 0; }}
.article-item-meta {{ display: flex; flex-wrap: wrap; gap: var(--space-3); font-size: 12px; color: var(--text-muted); align-items: center; }}
.article-item-excerpt {{ font-size: 13px; color: var(--text-tertiary); line-height: 1.5; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }}
.article-item.featured {{ border-left: 2px solid var(--accent); padding-left: calc(var(--space-4) - 2px); }}

.pagination {{ display: flex; justify-content: center; align-items: center; gap: var(--space-2); margin-top: var(--space-6); }}
.page-btn {{
  padding: var(--space-1) var(--space-3); border-radius: var(--radius-sm); font-size: 13px; font-weight: 500;
  cursor: pointer; background: var(--bg-card); border: 1px solid var(--border-default); color: var(--text-secondary);
  transition: all 0.12s; min-width: 36px; text-align: center;
}}
.page-btn:hover {{ border-color: var(--border-strong); color: var(--text-primary); }}
.page-btn.active {{ background: var(--accent); color: #090d14; border-color: var(--accent); }}
.page-btn:disabled {{ opacity: 0.3; cursor: default; }}
.page-info {{ font-size: 12px; color: var(--text-muted); padding: 0 var(--space-2); }}

.chart-card {{ background: var(--bg-card); border: 1px solid var(--border-subtle); border-radius: var(--radius-lg); padding: var(--space-5); }}
.chart-container {{ width: 100%; height: 500px; }}

.wizard-wrap {{ max-width: 680px; margin: 0 auto; padding: var(--space-8) 0; }}
.wizard-progress {{ display: flex; gap: var(--space-2); margin-bottom: var(--space-6); }}
.wizard-step-dot {{ flex: 1; height: 3px; background: var(--bg-card); border-radius: var(--radius-full); transition: background 0.3s; }}
.wizard-step-dot.active {{ background: var(--accent); }}
.wizard-step-dot.done {{ background: var(--accent); opacity: 0.5; }}
.wizard-q {{ animation: wFade 0.3s ease; }}
@keyframes wFade {{ from {{ opacity: 0; transform: translateY(6px); }} to {{ opacity: 1; transform: translateY(0); }} }}
.wizard-q-label {{ font-size: 11px; font-weight: 700; color: var(--accent); letter-spacing: 0.06em; text-transform: uppercase; margin-bottom: var(--space-2); }}
.wizard-q-title {{ font-size: 24px; font-weight: 700; letter-spacing: -0.02em; margin-bottom: var(--space-1); }}
.wizard-q-hint {{ font-size: 13px; color: var(--text-tertiary); margin-bottom: var(--space-5); }}
.wizard-opts {{ display: grid; gap: var(--space-3); margin-bottom: var(--space-6); }}
.wizard-opt {{
  display: flex; align-items: center; gap: var(--space-4); padding: var(--space-4);
  background: var(--bg-card); border: 1px solid var(--border-subtle); border-radius: var(--radius-lg);
  cursor: pointer; transition: all 0.15s; text-align: left; width: 100%;
}}
.wizard-opt:hover {{ background: var(--bg-card-hover); border-color: var(--accent); transform: translateX(3px); }}
.wizard-opt.selected {{ background: var(--accent-soft); border-color: var(--accent); }}
.wizard-opt-label {{ font-size: 11px; font-weight: 700; color: var(--text-muted); width: 36px; flex-shrink: 0; }}
.wizard-opt-body {{ flex: 1; }}
.wizard-opt-title {{ font-size: 14px; font-weight: 600; color: var(--text-primary); margin-bottom: 2px; }}
.wizard-opt-desc {{ font-size: 12px; color: var(--text-tertiary); }}
.wizard-nav {{ display: flex; justify-content: space-between; gap: var(--space-3); }}
.result-card {{
  background: var(--bg-card); border: 1px solid var(--border-subtle); border-radius: var(--radius-lg);
  padding: var(--space-5); margin-bottom: var(--space-4); position: relative; overflow: hidden;
}}
.result-card.best {{ border-color: var(--accent); background: linear-gradient(135deg, rgba(16,185,129,0.08), var(--bg-card)); }}
.result-rank {{
  position: absolute; top: 0; right: 0; padding: var(--space-1) var(--space-3);
  font-size: 10px; font-weight: 700; background: var(--accent); color: #090d14;
  border-bottom-left-radius: var(--radius-md);
}}

@media (max-width: 768px) {{
  .top-pick-grid {{ grid-template-columns: 1fr; }}
  .scenario-grid {{ grid-template-columns: repeat(2, 1fr); }}
  .reco-list {{ grid-template-columns: 1fr; }}
  .chart-container {{ height: 360px; }}
  .wizard-wrap {{ padding: var(--space-4); }}
}}
@media (max-width: 640px) {{
  .article-item-top {{ flex-direction: column; }}
  .article-item-meta {{ gap: var(--space-2); }}
}}
</style>
<script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js"></script>
</head>
<body>
<div id="navMount"></div>
<div id="pageBody"><div style="padding:80px 0;text-align:center;color:var(--text-tertiary);"><div style="font-size:28px;margin-bottom:8px;">CP</div><div style="font-size:14px;">加载中...</div></div></div>
<div id="footerMount"></div>

<script>
// ===== EMBEDDED DATA =====
var EMBEDDED = {embedded_data};

// ===== SHARED UTILS =====
var CPS = {{ config: EMBEDDED.config, plans: EMBEDDED.plans, articles: EMBEDDED.articles, priceChanges: EMBEDDED.priceChanges, state: {{ filters: {{ vendors: new Set(), types: new Set(), models: new Set(), tags: new Set(), monthlyPriceMax: null, search: '' }}, sort: {{ key: null, dir: 'asc' }} }} }};

function $(sel, root) {{ return (root || document).querySelector(sel); }}
function $$(sel, root) {{ return Array.from((root || document).querySelectorAll(sel)); }}
function escapeHtml(text) {{
  if (text === null || text === undefined) return '';
  var div = document.createElement('div');
  div.textContent = String(text);
  return div.innerHTML;
}}
function formatPrice(value, currency) {{
  if (value === null || value === undefined || value === '-' || value === '') return '—';
  if (typeof value === 'string') return value;
  var prefix = (currency === '$') ? '$' : '¥';
  return prefix + value;
}}
function formatNumber(value) {{
  if (value === null || value === undefined || value === '-') return '—';
  if (typeof value === 'string') return value;
  return value >= 1000 ? value.toLocaleString() : value;
}}
function renderStars(rating) {{
  var full = '★'.repeat(rating);
  var empty = '☆'.repeat(5 - rating);
  return '<span class="stars">' + full + '</span><span class="stars stars-dim">' + empty + '</span>';
}}
function renderTagsInline(tags) {{
  if (!tags || !tags.length) return '';
  return tags.map(function(t) {{ return '<span class="tag">' + escapeHtml(t) + '</span>'; }}).join(' ');
}}
function renderMarkdownLite(text) {{
  if (!text) return '';
  var html = escapeHtml(text);
  html = html.replace(/\\*\\*(.+?)\\*\\*/g, '<strong>$1</strong>');
  return html;
}}

// ===== NAVIGATION =====
function renderNav(activeTab) {{
  var config = CPS.config;
  var links = (config.nav || []).map(function(item) {{
    return '<a href="#" class="nav-link" data-tab="' + item.key + '">' + escapeHtml(item.label) + '</a>';
  }}).join('');
  return '<nav class="nav"><div class="nav-inner">' +
    '<a href="#" class="nav-brand" data-tab="discover"><span class="nav-brand-name">' + escapeHtml(config.site.name) + '</span></a>' +
    '<div class="nav-links" id="navLinks">' +
      '<a href="#" class="nav-link nav-tab active" data-tab="discover">推荐 & 动态</a>' +
      '<a href="#" class="nav-link nav-tab" data-tab="compare">套餐对比</a>' +
      '<a href="#" class="nav-link nav-tab" data-tab="blog">测评文章</a>' +
      '<a href="#" class="nav-link nav-tab" data-tab="wizard">选型助手</a>' +
      links +
      '<a href="#" class="nav-cta" data-tab="join">加入社群</a>' +
    '</div>' +
    '<button class="nav-mobile-toggle" id="navToggle" aria-label="菜单">☰</button>' +
  '</div></nav>';
}}

function mountNav() {{
  var mount = document.getElementById('navMount');
  if (mount) {{
    mount.innerHTML = renderNav();
    var toggle = document.getElementById('navToggle');
    var links = document.getElementById('navLinks');
    if (toggle && links) toggle.addEventListener('click', function() {{ links.classList.toggle('open'); }});
    bindNav();
  }}
}}

function bindNav() {{
  document.querySelectorAll('.nav-link[data-tab], .nav-brand[data-tab], .nav-cta[data-tab]').forEach(function(el) {{
    el.addEventListener('click', function(e) {{
      e.preventDefault();
      switchTab(this.dataset.tab);
    }});
  }});
}}

function switchTab(tab) {{
  document.querySelectorAll('.nav-link[data-tab], .nav-brand[data-tab]').forEach(function(el) {{
    el.classList.toggle('active', el.dataset.tab === tab);
  }});
  document.querySelectorAll('.tab-panel').forEach(function(p) {{
    p.classList.toggle('active', p.id === 'panel-' + tab);
  }});
  if (tab === 'compare' && typeof echarts !== 'undefined') setTimeout(renderChart, 200);
  if (tab === 'blog') renderBlog();
  window.scrollTo({{ top: 0, behavior: 'smooth' }});
}}

// ===== FOOTER =====
function renderFooter() {{
  var config = CPS.config;
  var links = (config.footer.links || []).map(function(l) {{
    return '<a href="#" data-tab="' + l.key + '">' + escapeHtml(l.label) + '</a>';
  }}).join('');
  return '<footer class="footer"><div class="container">' +
    '<div class="footer-disclosure">' + escapeHtml(config.disclosure || '') + '</div>' +
    '<div class="footer-inner"><div class="footer-brand">' + escapeHtml(config.footer.about || '') + '</div><div class="footer-links">' + links + '</div></div>' +
  '</div></footer>';
}}

function mountFooter() {{
  var mount = document.getElementById('footerMount');
  if (mount) mount.innerHTML = renderFooter();
}}

// ===== TABLE LOGIC =====
function filterPlans() {{
  var f = CPS.state.filters;
  return CPS.plans.filter(function(p) {{
    if (f.vendors.size && !f.vendors.has(p.vendor)) return false;
    if (f.types.size && !f.types.has(p.type)) return false;
    if (f.tags.size && !(p.tags || []).some(function(t) {{ return f.tags.has(t); }})) return false;
    if (f.models.size && !(p.models || []).some(function(m) {{ return f.models.has(m); }})) return false;
    if (f.monthlyPriceMax && typeof p.monthlyPrice === 'number' && p.monthlyPrice > f.monthlyPriceMax) return false;
    if (f.search) {{
      var hay = (p.vendor + ' ' + p.plan + ' ' + (p.models || []).join(' ') + ' ' + (p.tags || []).join(' ')).toLowerCase();
      if (hay.indexOf(f.search) === -1) return false;
    }}
    return true;
  }});
}}

function renderTable() {{
  var tbody = document.getElementById('plansTableBody');
  var cardsView = document.getElementById('plansCardsView');
  var filtered = filterPlans();
  var countEl = document.getElementById('filterCount');
  if (countEl) countEl.textContent = filtered.length;

  if (!filtered.length) {{
    var empty = '<div style="text-align:center;padding:48px;color:var(--text-muted);">没有匹配的套餐</div>';
    if (tbody) tbody.innerHTML = '<tr><td colspan="99">' + empty + '</td></tr>';
    if (cardsView) cardsView.innerHTML = empty;
    return;
  }}

  if (tbody) {{
    tbody.innerHTML = filtered.map(function(p) {{
      var price = formatPrice(p.monthlyPrice, p.currency || '¥');
      var measured = p.measuredMonthlyToken ? p.measuredMonthlyToken + 'M' : '—';
      var tpu = (typeof p.monthlyPrice === 'number' && typeof p.measuredMonthlyToken === 'number' && p.monthlyPrice > 0) ? (p.measuredMonthlyToken / p.monthlyPrice).toFixed(2) : '—';
      var models = (p.models || []).slice(0, 4).join(', ') + ((p.models || []).length > 4 ? '...' : '');
      return '<tr><td class="col-vendor">' + escapeHtml(p.vendor) + '</td>' +
        '<td>' + escapeHtml(p.plan) + '</td>' +
        '<td><span class="badge">' + escapeHtml(p.type) + '</span></td>' +
        '<td>' + renderStars(p.rating) + '</td>' +
        '<td class="col-price">' + price + '</td>' +
        '<td class="col-price">' + measured + '</td>' +
        '<td class="col-price" style="color:var(--accent);">' + tpu + '</td>' +
        '<td><span style="font-size:12px;">' + escapeHtml(models) + '</span></td>' +
        '<td>' + renderTagsInline(p.tags) + '</td>' +
        '<td class="col-action"><a href="' + (p.action || '#') + '" target="_blank" rel="noopener">查看</a></td></tr>';
    }}).join('');
  }}

  if (cardsView) {{
    cardsView.innerHTML = filtered.map(function(p) {{
      var price = formatPrice(p.monthlyPrice, p.currency || '¥');
      var measured = p.measuredMonthlyToken ? p.measuredMonthlyToken + 'M' : '—';
      var tpu = (typeof p.monthlyPrice === 'number' && typeof p.measuredMonthlyToken === 'number' && p.monthlyPrice > 0) ? (p.measuredMonthlyToken / p.monthlyPrice).toFixed(2) : '—';
      return '<div class="plan-card-item"><div class="plan-card-header"><div><div class="plan-card-vendor">' + escapeHtml(p.vendor) + '</div><div class="plan-card-plan">' + escapeHtml(p.plan) + '</div></div><div class="plan-card-price">' + price + '</div></div>' +
        renderStars(p.rating) +
        '<div class="plan-card-row"><div><span class="plan-card-label">月Token</span><br><span class="plan-card-value">' + measured + '</span></div><div><span class="plan-card-label">每元Token</span><br><span class="plan-card-value">' + tpu + '</span></div></div>' +
        '<div style="margin-top:var(--space-3);text-align:right;"><a href="' + (p.action || '#') + '" target="_blank" rel="noopener" class="btn btn-primary btn-sm">查看</a></div></div>';
    }}).join('');
  }}
}}

// ===== ECHARTS =====
function renderChart() {{
  var plans = CPS.plans.filter(function(p) {{ return typeof p.monthlyPrice === 'number' && typeof p.measuredMonthlyToken === 'number'; }});
  if (!plans.length) return;
  var dom = document.getElementById('priceVsTokenChart');
  if (!dom || dom.offsetParent === null) return;
  if (window._chartInstance) window._chartInstance.dispose();
  var chart = echarts.init(dom);
  window._chartInstance = chart;

  var seen = {{}}, items = [];
  plans.forEach(function(p) {{ var k = p.vendor + '|' + p.plan; if (!seen[k]) {{ seen[k] = true; items.push(p); }} }});
  var vColors = {{ '智谱AI':'#F5F527','字节·方舟':'#FF3B3B','MiniMax':'#f97316','Kimi':'#10C2B0','阿里·百炼':'#22c55e','讯飞·星火':'#ec4899','DeepSeek 官方':'#71717B','小米·MiMo':'#2563eb','优云智算':'#3b82f6','共继算力':'#a855f7','OpenCode':'#84cc16','百度·千帆':'#06b6d4','腾讯云':'#eab308','华为云':'#ef4444','京东云':'#d946ef','Claude':'#ec4899','Codex (ChatGPT)':'#A15CF6','GitHub':'#71717B','Ollama':'#f43f5e','智谱国际版':'#10b981' }};
  var pal = ['#22c55e','#eab308','#f43f5e','#a855f7','#ef4444'], pi = 0;
  var colorMap = {{}}, vendors = [], vSet = {{}};
  items.forEach(function(i) {{ if(!vSet[i.vendor]){{ vSet[i.vendor]=true;vendors.push(i.vendor);}} }});
  vendors.forEach(function(v) {{ colorMap[v] = vColors[v] || pal[pi++ % pal.length]; }});
  var vData = {{}};
  vendors.forEach(function(v) {{ vData[v] = items.filter(function(i){{return i.vendor===v;}}).sort(function(a,b){{return a.monthlyPrice-b.monthlyPrice;}}); }});
  var allP = items.map(function(i){{return i.monthlyPrice;}}), allT = items.map(function(i){{return i.measuredMonthlyToken;}});
  var minP = Math.min.apply(null,allP), maxP = Math.max.apply(null,allP), minT = Math.min.apply(null,allT), maxT = Math.max.apply(null,allT);
  var sP = allP.slice().sort(function(a,b){{return a-b;}}), sT = allT.slice().sort(function(a,b){{return a-b;}});
  var medP = sP[Math.floor(sP.length/2)], medT = sT[Math.floor(sT.length/2)];
  var tpuVals = items.map(function(i){{return i.measuredMonthlyToken/i.monthlyPrice;}}).sort(function(a,b){{return a-b;}});
  var medTPU = tpuVals[Math.floor(tpuVals.length/2)];

  var series = vendors.map(function(v) {{
    var data = vData[v].map(function(i) {{ return {{value:[i.monthlyPrice,i.measuredMonthlyToken],plan:i.plan,vendor:i.vendor,type:i.type,price:i.monthlyPrice,token:i.measuredMonthlyToken,tokensPerYuan:(i.measuredMonthlyToken/i.monthlyPrice).toFixed(2)}}; }});
    return {{name:v,type:'line',color:colorMap[v],symbol:'circle',symbolSize:14,showSymbol:true,lineStyle:{{width:data.length>1?1.5:0,opacity:data.length>1?0.3:0}},label:{{show:true,position:'right',distance:6,color:'#94a3b8',fontSize:10,fontWeight:600,formatter:function(p){{return p.data.plan||'';}}}},labelLayout:{{hideOverlap:true}},itemStyle:{{color:colorMap[v],borderColor:'rgba(255,255,255,0.95)',borderWidth:1.5,shadowBlur:12,shadowColor:'rgba(0,0,0,0.12)'}},data:data,emphasis:{{scale:1.15}}}};
  }});

  var helper = {{type:'scatter',silent:true,animation:false,data:[],symbolSize:0,tooltip:{{show:false}},itemStyle:{{opacity:0}},
    markArea:{{silent:true,label:{{show:false}},data:[
      [{{itemStyle:{{color:'rgba(16,185,129,0.12)'}},xAxis:minP*0.7,yAxis:minP*0.7*medTPU}},{{xAxis:medP,yAxis:maxT*1.2}}],
      [{{itemStyle:{{color:'rgba(16,185,129,0.06)'}},xAxis:medP,yAxis:medP*medTPU}},{{xAxis:maxP*1.3,yAxis:maxT*1.2}}],
      [{{itemStyle:{{color:'rgba(148,163,184,0.04)'}},xAxis:minP*0.7,yAxis:minT*0.4}},{{xAxis:medP,yAxis:medP*medTPU}}],
      [{{itemStyle:{{color:'rgba(239,68,68,0.08)'}},xAxis:medP,yAxis:minT*0.4}},{{xAxis:maxP*1.3,yAxis:medP*medTPU}}]
    ]}},
    markLine:{{silent:true,symbol:'none',label:{{show:false}},data:[
      {{xAxis:medP,lineStyle:{{color:'rgba(148,163,184,0.25)',type:'dashed'}}}},
      {{yAxis:medT,lineStyle:{{color:'rgba(148,163,184,0.25)',type:'dashed'}}}}
    ]}}
  }};

  chart.setOption({{
    animationDuration:400, color:vendors.map(function(v){{return colorMap[v];}}),
    grid:{{left:90,right:40,top:60,bottom:60}},
    tooltip:{{trigger:'item',backgroundColor:'rgba(15,23,42,0.96)',borderColor:'rgba(148,163,184,0.2)',textStyle:{{color:'#f1f5f9',fontSize:13}},
      formatter:function(p){{var d=p.data;return'<div style="min-width:180px"><div style="font-size:14px;font-weight:800;margin-bottom:4px;">'+d.vendor+' '+d.plan+'</div><div style="font-size:12px;line-height:1.7;color:#cbd5e1;"><div>类型: '+d.type+'</div><div>月费: <b>'+d.price+'</b> | 月Token: <b>'+d.token+'M</b></div><div>每元Token: <b>'+d.tokensPerYuan+' M</b></div></div></div>';}}}},
    legend:{{top:0,left:0,itemWidth:10,itemHeight:10,icon:'circle',textStyle:{{color:'#94a3b8',fontSize:11,fontWeight:600}}}},
    graphic:[{{type:'text',left:100,top:40,silent:true,style:{{text:'高性价比',fill:'#10b981',fontSize:12,fontWeight:700}}}},{{type:'text',right:40,bottom:24,silent:true,style:{{text:'低性价比',fill:'#ef4444',fontSize:11,fontWeight:700}}}}],
    xAxis:{{type:'log',logBase:2,min:minP*0.75,max:maxP*1.12,name:'月费',nameTextStyle:{{color:'#94a3b8',fontSize:11,fontWeight:700}},axisLabel:{{color:'#94a3b8',fontSize:11,fontWeight:700,formatter:function(v){{return'¥'+(Number.isInteger(v)?v:v.toFixed(0));}}}},splitLine:{{show:true,lineStyle:{{color:'rgba(148,163,184,0.1)',type:'dashed'}}}}}},
    yAxis:{{type:'log',logBase:10,min:minT*0.65,max:maxT*1.18,name:'月Token上限',nameTextStyle:{{color:'#94a3b8',fontSize:11,fontWeight:700}},axisLabel:{{color:'#94a3b8',formatter:function(v){{return v>=1000?(v/1000).toFixed(1)+'B':v+'M';}}}},splitLine:{{lineStyle:{{color:'rgba(148,163,184,0.1)',type:'dashed'}}}}}},
    series:[helper].concat(series)
  }});
  window.addEventListener('resize',function(){{chart.resize();}});
}}

// ===== WIZARD =====
var WIZARD_Q = [
  {{ key:'budget', label:'问题 1/4', title:'你每月想花多少钱？', hint:'按真实预算选。',
    options:[
      {{ label:'50', value:{{max:50}}, title:'50 元以内', desc:'学生党 / 体验党' }},
      {{ label:'200', value:{{max:200}}, title:'50-200 元', desc:'日常开发者主流预算' }},
      {{ label:'500', value:{{max:500}}, title:'200-500 元', desc:'重度用户 / 多平台持有' }},
      {{ label:'MAX', value:{{max:null}}, title:'500 以上', desc:'团队 / 极客 / Agent 重度' }}
    ]}},
  {{ key:'model', label:'问题 2/4', title:'你最在意哪个模型？',
    options:[
      {{ label:'GLM', value:'GLM-5.2', title:'GLM-5.2', desc:'智谱 T0 模型' }},
      {{ label:'DS', value:'DeepSeek-V4', title:'DeepSeek V4', desc:'原生性价比之王' }},
      {{ label:'K3', value:'Kimi', title:'Kimi K3', desc:'长上下文 + 推理强' }},
      {{ label:'ALL', value:null, title:'都要', desc:'让模型最全的平台胜出' }}
    ]}},
  {{ key:'rush', label:'问题 3/4', title:'你能接受抢购吗？',
    options:[
      {{ label:'YES', value:true, title:'能抢', desc:'想要最高性价比，愿意蹲点' }},
      {{ label:'NO', value:false, title:'不抢', desc:'随时下单，不想折腾' }},
      {{ label:'ANY', value:null, title:'都行', desc:'看性价比决定' }}
    ]}},
  {{ key:'scene', label:'问题 4/4', title:'你的主要使用场景？',
    options:[
      {{ label:'DEV', value:'coding', title:'日常写代码', desc:'高频使用 / Cursor / Claude Code' }},
      {{ label:'CHAT', value:'general', title:'日常助手', desc:'问答 / 文档处理' }},
      {{ label:'IMG', value:'multimodal', title:'多模态需求', desc:'图像识别 / 视觉理解' }},
      {{ label:'BOT', value:'agentic', title:'Agent / 自动化', desc:'Agent 任务 / 长任务' }}
    ]}}
];
var wizardAnswers = {{}}, wizardStep = 0;

function renderWizard() {{
  var q = WIZARD_Q[wizardStep];
  var container = document.getElementById('wizardContainer');
  var progress = document.getElementById('wizProgress');
  if (progress) progress.innerHTML = WIZARD_Q.map(function(_,i){{ return '<div class="wizard-step-dot'+(i===wizardStep?' active':(i<wizardStep?' done':''))+'"></div>'; }}).join('');

  container.innerHTML = '<div class="wizard-q"><div class="wizard-q-label">'+escapeHtml(q.label)+'</div><h2 class="wizard-q-title">'+escapeHtml(q.title)+'</h2><p class="wizard-q-hint">'+escapeHtml(q.hint)+'</p>' +
    '<div class="wizard-opts">'+q.options.map(function(opt){{ return '<button class="wizard-opt"><span class="wizard-opt-label">'+escapeHtml(opt.label)+'</span><div class="wizard-opt-body"><div class="wizard-opt-title">'+escapeHtml(opt.title)+'</div><div class="wizard-opt-desc">'+escapeHtml(opt.desc)+'</div></div></button>'; }}).join('')+'</div>' +
    '<div class="wizard-nav"><button class="btn btn-ghost" id="wizPrev"'+(wizardStep===0?' style="visibility:hidden;"':'')+'>上一题</button><span style="font-size:13px;color:var(--text-tertiary);align-self:center;">第 '+(wizardStep+1)+'/'+WIZARD_Q.length+' 题</span></div></div>';

  container.querySelectorAll('.wizard-opt').forEach(function(btn,i){{ btn.addEventListener('click',function(){{ wizardAnswers[q.key]=q.options[i].value; if(wizardStep<WIZARD_Q.length-1){{ wizardStep++;renderWizard();}}else{{ showWizardResult();}} }}); }});
  var prev = document.getElementById('wizPrev'); if(prev) prev.addEventListener('click',function(){{ if(wizardStep>0){{ wizardStep--;renderWizard();}} }});
}}

function showWizardResult() {{
  var scored = CPS.plans.map(function(p) {{
    var score = p.rating*10, reasons=[];
    var budget=wizardAnswers.budget, price=typeof p.monthlyPrice==='number'?p.monthlyPrice:0;
    if(budget&&budget.max!==null){{ if(price<=budget.max){{ score+=20;reasons.push('¥'+price+'/月 在预算内');}}else{{ score-=30;}} }}
    var model=wizardAnswers.model;
    if(model){{ if((p.models||[]).some(function(m){{return m.indexOf(model)!==-1;}})){{ score+=30;reasons.push('支持你想要的模型');}}else{{ score-=15;}} }}
    else{{ if((p.models||[]).length>=5){{ score+=15;reasons.push('全家桶');}} }}
    var rush=wizardAnswers.rush, needRush=(p.tags||[]).indexOf('需抢购')!==-1;
    if(rush===false&&needRush) score-=25; else if(rush===false&&!needRush){{ score+=15;reasons.push('无需抢购'); }}
    var scene=wizardAnswers.scene;
    if(scene==='coding'&&p.type==='Coding Plan'){{ score+=10;reasons.push('适合高频写代码'); }}
    else if(scene==='agentic'&&p.measuredMonthlyToken&&p.measuredMonthlyToken>=1000){{ score+=15;reasons.push('Token充足'); }}
    return {{plan:p,score:score,reasons:reasons.slice(0,3)}};
  }}).filter(function(i){{return i.score>0;}}).sort(function(a,b){{return b.score-a.score;}}).slice(0,3);

  var resultEl = document.getElementById('wizardResult');
  if(!scored.length){{ resultEl.innerHTML='<div class="card" style="text-align:center;padding:48px;"><h2>没有完美匹配</h2><p style="color:var(--text-tertiary);margin:16px 0;">放宽条件重试</p><button class="btn btn-primary" onclick="resetWizard()">重新选择</button></div>';return; }}
  var labels=['最佳推荐','备选方案','第三选择'];
  resultEl.innerHTML = '<div style="text-align:center;margin-bottom:24px;"><span class="section-eyebrow">RESULT</span><h2 style="font-size:24px;margin-top:12px;">Top 3 推荐</h2></div>' +
    scored.map(function(item,i){{ var p=item.plan;
      return '<div class="result-card'+(i===0?' best':'')+'"><div class="result-rank">'+labels[i]+'</div>' +
        '<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px;"><div><h3 style="font-size:18px;font-weight:700;">'+escapeHtml(p.vendor)+' <span style="font-size:14px;color:var(--text-tertiary);">'+escapeHtml(p.plan)+'</span></h3><div style="font-size:13px;color:var(--text-tertiary);">'+escapeHtml(p.type)+' '+formatPrice(p.monthlyPrice,p.currency||'¥')+'/月</div></div>'+renderStars(p.rating)+'</div>' +
        (p.bloggerVerdict?'<p style="font-size:13px;color:var(--accent);margin-bottom:12px;">"'+escapeHtml(p.bloggerVerdict)+'"</p>':'') +
        '<ul class="reco-card-reasons" style="margin-bottom:16px;">'+item.reasons.map(function(r){{return'<li>'+escapeHtml(r)+'</li>';}}).join('')+'</ul>' +
        '<a href="'+(p.action||'#')+'" class="btn btn-primary" target="_blank" rel="noopener">查看详情</a></div>';
    }}).join('') +
    '<div style="display:flex;gap:12px;justify-content:center;margin-top:24px;"><button class="btn btn-secondary" onclick="resetWizard()">重新选择</button></div>';
}}

function resetWizard() {{ wizardStep=0; wizardAnswers={{}}; document.getElementById('wizardContainer').style.display='block'; document.getElementById('wizProgress').style.display='flex'; document.getElementById('wizardResult').innerHTML=''; renderWizard(); }}

// ===== BLOG =====
var blogState = {{ category:'', source:'', topic:'', search:'', sort:'newest', page:1, pageSize:10 }};
var BLOG_TOPICS = [{{ key:'Kimi',label:'Kimi/K3' }},{{ key:'DeepSeek',label:'DeepSeek' }},{{ key:'Claude',label:'Claude Code' }},{{ key:'Coding Plan',label:'Coding Plan' }},{{ key:'Vibe Coding',label:'Vibe Coding' }},{{ key:'Anthropic',label:'Anthropic' }},{{ key:'定价',label:'价格变动' }}];

function renderBlog() {{
  var sources = ['',...new Set(CPS.articles.map(function(a){{return a.author;}}))].sort();
  var cats = ['',...new Set(CPS.articles.map(function(a){{return a.category;}}))];
  var el = document.getElementById('panel-blog');
  if (!el || el.dataset.rendered) return;
  el.dataset.rendered = '1';
  el.innerHTML =
    '<section class="hero" style="padding-bottom:var(--space-4);"><div class="container"><div class="blog-layout"><span class="section-eyebrow">LATEST</span><h1 class="hero-title" style="font-size:clamp(24px,3vw,32px);">热点文章</h1><p class="hero-subtitle">AI Coding Plan 相关最新文章，点击标题跳转原文。</p></div></div></section>' +
    '<section class="section-sm" style="padding-top:0;"><div class="container"><div class="blog-layout">' +
      '<div class="search-bar"><input type="text" class="search-input" id="blogSearch" placeholder="搜索文章标题或关键词..."></div>' +
      '<div class="filter-section"><div class="filter-label">分类</div><div class="filter-row" id="blogCatFilters">'+cats.map(function(c){{return'<button class="filter-chip'+(c===''?' active':'')+'" data-type="category" data-value="'+c+'">'+(c||'全部')+'</button>';}}).join('')+'</div></div>' +
      '<div class="filter-section"><div class="filter-label">来源</div><div class="filter-row" id="blogSrcFilters">'+sources.map(function(s){{return'<button class="filter-chip'+(s===''?' active':'')+'" data-type="source" data-value="'+s+'">'+(s||'全部')+'</button>';}}).join('')+'</div></div>' +
      '<div class="filter-section"><div class="filter-label">话题</div><div class="filter-row" id="blogTopicFilters"><button class="filter-chip active" data-type="topic" data-value="">全部</button>'+BLOG_TOPICS.map(function(t){{return'<button class="filter-chip" data-type="topic" data-value="'+t.key+'">'+t.label+'</button>';}}).join('')+'</div></div>' +
      '<div class="toolbar"><span class="article-count" id="blogCount"></span><div><button class="sort-btn active" data-sort="newest">最新</button><button class="sort-btn" data-sort="featured">推荐</button></div></div>' +
      '<div id="blogList"></div><div class="pagination" id="blogPagination"></div>' +
    '</div></div></section>';
  bindBlogEvents();
  refreshBlogList();
}}

function bindBlogEvents() {{
  document.getElementById('blogSearch').addEventListener('input',function(){{ blogState.search=this.value.trim().toLowerCase(); blogState.page=1; refreshBlogList(); }});
  document.querySelectorAll('#blogCatFilters .filter-chip, #blogSrcFilters .filter-chip, #blogTopicFilters .filter-chip').forEach(function(chip){{ chip.addEventListener('click',function(){{ var type=this.dataset.type,val=this.dataset.value; this.parentElement.querySelectorAll('.filter-chip').forEach(function(c){{c.classList.remove('active');}}); this.classList.add('active'); blogState[type]=val; blogState.page=1; refreshBlogList(); }}); }});
  document.querySelectorAll('.sort-btn').forEach(function(b){{ b.addEventListener('click',function(){{ document.querySelectorAll('.sort-btn').forEach(function(x){{x.classList.remove('active');}}); this.classList.add('active'); blogState.sort=this.dataset.sort; blogState.page=1; refreshBlogList(); }}); }});
}}

function refreshBlogList() {{
  var filtered = CPS.articles.filter(function(a){{ if(blogState.category&&a.category!==blogState.category)return false; if(blogState.source&&a.author!==blogState.source)return false; if(blogState.topic&&a.title.indexOf(blogState.topic)===-1)return false; if(blogState.search){{ var h=(a.title+' '+a.excerpt+' '+a.author).toLowerCase(); if(h.indexOf(blogState.search)===-1)return false; }} return true; }});
  if(blogState.sort==='featured') filtered.sort(function(a,b){{return(b.featured?1:0)-(a.featured?1:0);}});
  var total=Math.ceil(filtered.length/blogState.pageSize); if(blogState.page>total) blogState.page=Math.max(1,total);
  var paged=filtered.slice((blogState.page-1)*blogState.pageSize,blogState.page*blogState.pageSize);
  document.getElementById('blogCount').textContent='共 '+filtered.length+' 篇';
  var list=document.getElementById('blogList');
  if(!paged.length){{ list.innerHTML='<div class="no-results">没有匹配的文章</div>'; document.getElementById('blogPagination').innerHTML=''; return; }}
  list.innerHTML=paged.map(function(a){{ var href=a.url||'#'; return'<div class="article-item'+(a.featured?' featured':'')+'"><div class="article-item-top"><div class="article-item-title"><a href="'+href+'" target="_blank" rel="noopener">'+escapeHtml(a.title)+'</a></div><div class="article-item-badge"><span class="badge badge-accent">'+escapeHtml(a.category)+'</span></div></div>'+(a.excerpt?'<div class="article-item-excerpt">'+escapeHtml(a.excerpt)+'</div>':'')+'<div class="article-item-meta"><span>'+(a.author?escapeHtml(a.author):'')+'</span><span>'+escapeHtml(a.date)+'</span><span>'+escapeHtml(a.readTime)+'</span>'+(a.featured?'<span class="badge badge-warning">推荐</span>':'')+'</div></div>'; }}).join('');
  var pg=document.getElementById('blogPagination'); if(total<=1){{pg.innerHTML='';return;}}
  pg.innerHTML='<button class="page-btn"'+(blogState.page===1?' disabled':'')+' data-pg="'+(blogState.page-1)+'">上一页</button><span class="page-info">'+blogState.page+'/'+total+'</span><button class="page-btn"'+(blogState.page===total?' disabled':'')+' data-pg="'+(blogState.page+1)+'">下一页</button>';
  pg.querySelectorAll('.page-btn:not([disabled])').forEach(function(b){{ b.addEventListener('click',function(){{ blogState.page=parseInt(this.dataset.pg); refreshBlogList(); }}); }});
}}

// ===== RENDER ALL =====
function init() {{
  mountNav();
  mountFooter();

  var body = document.getElementById('pageBody');
  var config = CPS.config;
  var h = config.header;
  var plans = CPS.plans;

  // Compute top picks
  var scored = plans.filter(function(p){{return typeof p.monthlyPrice==='number'&&typeof p.measuredMonthlyToken==='number';}})
    .map(function(p){{return{{plan:p,tpu:p.measuredMonthlyToken/p.monthlyPrice,score:p.rating*10+(p.measuredMonthlyToken/p.monthlyPrice)}};}})
    .sort(function(a,b){{return b.score-a.score;}}).slice(0,3);
  var topLabels=['综合最佳','高性价比','入门首选'];
  var topReasons=['综合评分最高，模型能力和性价比都很出色。','每元能拿到更多 Token，花同样的钱可用更多。','月费最低，适合预算有限或想先试试水的用户。'];

  body.innerHTML =
    // ===== DISCOVER TAB =====
    '<div class="tab-panel active" id="panel-discover">' +
      '<section class="hero" style="padding-bottom:var(--space-6);"><div class="container"><div class="hero-inner"><div>' +
        '<span class="section-eyebrow">'+escapeHtml(h.updateDate)+'</span>' +
        '<h1 class="hero-title">AI Coding Plan<br><span class="hero-title-accent">买哪个最划算？</span></h1>' +
        '<p class="hero-subtitle">'+escapeHtml(config.site.tagline)+'</p>' +
        '<p style="font-size:13px;color:var(--text-tertiary);margin-bottom:var(--space-5);">'+escapeHtml(h.highlights)+'</p>' +
        '<div class="hero-actions"><button class="btn btn-primary btn-lg" onclick="switchTab(\'compare\')">查看完整对比表</button><button class="btn btn-secondary btn-lg" onclick="switchTab(\'wizard\')">选型助手</button></div>' +
      '</div><div class="hero-stats">'+(h.stats||[]).map(function(s){{return'<div><div class="hero-stat-value">'+escapeHtml(s.value)+'<span style="font-size:13px;color:var(--text-tertiary);margin-left:2px;">'+escapeHtml(s.unit)+'</span></div><div class="hero-stat-label">'+escapeHtml(s.label)+'</div></div>';}}).join('')+'</div></div></div></section>' +

      '<section class="section-sm"><div class="container"><div class="section-header" style="margin-bottom:var(--space-4);"><span class="section-eyebrow">TOP PICKS</span><h2 class="section-title">不知道买哪个？看这三个就够了</h2></div>' +
        '<div class="top-pick-grid">'+scored.map(function(item,i){{ var p=item.plan; return'<div class="top-pick-card'+(i===0?' pick-best':'')+'"><div class="top-pick-label">'+topLabels[i]+'</div><div class="top-pick-vendor">'+escapeHtml(p.vendor)+'</div><div class="top-pick-plan">'+escapeHtml(p.plan)+' '+escapeHtml(p.type)+'</div><div class="top-pick-price">'+formatPrice(p.monthlyPrice,p.currency||'¥')+'<span class="top-pick-price-unit">/月</span></div><div class="top-pick-metrics"><div><div class="top-pick-metric-value">'+p.measuredMonthlyToken+'M</div><div class="top-pick-metric-label">月Token</div></div><div><div class="top-pick-metric-value">'+item.tpu.toFixed(1)+'</div><div class="top-pick-metric-label">每元Token</div></div></div><div class="top-pick-reason">'+topReasons[i]+'</div></div>'; }}).join('')+'</div>' +
      '</div></section>' +

      '<section class="section-sm"><div class="container"><div class="section-header" style="margin-bottom:var(--space-4);"><span class="section-eyebrow">SCENARIOS</span><h2 class="section-title">按你的场景来选</h2></div>' +
        '<div class="scenario-grid">'+(config.quickEntries||[]).map(function(q){{ return'<div class="scenario-card" onclick="applyScenario(\''+q.id+'\')"><div class="scenario-card-label">'+escapeHtml(q.icon)+'</div><div class="scenario-card-title">'+escapeHtml(q.title)+'</div><div class="scenario-card-desc">'+escapeHtml(q.desc)+'</div></div>'; }}).join('')+'</div>' +
      '</div></section>' +

      // Recommendations
      '<section class="section-sm"><div class="container"><div class="section-header" style="margin-bottom:var(--space-4);"><span class="section-eyebrow">RECOMMENDED</span><h2 class="section-title">饭庐者说推荐</h2></div>' +
        (config.recommendationGroups||[]).map(function(group){{ return'<div style="margin-bottom:var(--space-6);"><h3 style="font-size:16px;font-weight:700;margin-bottom:var(--space-3);">'+escapeHtml(group.title)+'</h3><div class="reco-list">'+(group.items||[]).map(function(item){{ var plan=plans.find(function(p){{return p.vendor===item.vendor&&p.plan===item.plan;}}); var ps=plan?'<strong>'+formatPrice(plan.monthlyPrice,plan.currency||'¥')+'</strong>/月':''; return'<div class="reco-item"><div class="reco-item-header"><div><div class="reco-item-vendor">'+escapeHtml(item.vendor)+'</div><div class="reco-item-plan">'+escapeHtml(item.plan)+' '+(plan?escapeHtml(plan.type):'')+'</div></div>'+renderStars(item.rating)+'</div>'+(item.verdict?'<span class="reco-item-verdict">'+escapeHtml(item.verdict)+'</span>':'')+'<ul class="reco-item-reasons">'+(item.reasons||[]).map(function(r){{return'<li>'+renderMarkdownLite(r)+'</li>';}}).join('')+'</ul><div class="reco-item-footer"><span style="font-family:var(--font-mono);font-size:13px;color:var(--text-tertiary);">'+ps+'</span><a href="'+(item.action||(plan?plan.action:'#'))+'" class="btn btn-sm btn-primary" target="_blank" rel="noopener">查看</a></div></div>'; }}).join('')+'</div></div>'; }}).join('') +
      '</div></section>' +

      // Price Changes
      (CPS.priceChanges&&CPS.priceChanges.changes? '<section class="section-sm"><div class="container"><div class="section-header" style="margin-bottom:var(--space-4);"><span class="section-eyebrow">PRICE ALERT</span><h2 class="section-title">价格变动记录</h2></div><div class="card">'+CPS.priceChanges.changes.slice(0,5).map(function(c){{ var b=c.impact==='positive'?'<span class="badge badge-positive">利好</span>':c.impact==='negative'?'<span class="badge badge-negative">利空</span>':'<span class="badge">中性</span>'; return'<div class="price-change-item"><div>'+b+'</div><div><div class="price-change-vendor">'+escapeHtml(c.vendor)+' '+escapeHtml(c.type)+'</div><div class="price-change-detail">'+escapeHtml(c.detail)+'</div></div><span class="price-change-date">'+escapeHtml(c.date)+'</span></div>'; }}).join('')+'</div></div></section>': '') +

      // Community
      (config.community? '<section class="section-sm"><div class="container"><div class="section-header text-center"><span class="section-eyebrow">COMMUNITY</span><h2 class="section-title">不止看数据，来群里聊</h2></div><div class="community-grid">'+['free','paid'].map(function(k){{ var c=config.community[k]; return'<div class="community-card community-card-'+k+'"><div class="community-card-header"><h3 class="community-card-title">'+escapeHtml(c.title)+'</h3><span class="badge'+(k==='paid'?' badge-premium':' badge-accent')+'">'+(k==='paid'?'PRO':'FREE')+'</span></div><div class="community-card-subtitle">'+escapeHtml(c.subtitle)+'</div><p class="community-card-desc">'+escapeHtml(c.description)+'</p><ul class="community-highlights">'+(c.highlights||[]).map(function(h){{return'<li>'+escapeHtml(h)+'</li>';}}).join('')+'</ul><a href="'+c.url+'" class="btn '+(k==='paid'?'btn-primary':'btn-secondary')+' btn-lg">'+escapeHtml(c.ctaText)+'</a></div>'; }}).join('')+'</div></div></section>': '') +
    '</div>' +

    // ===== COMPARE TAB =====
    '<div class="tab-panel" id="panel-compare">' +
      '<section class="section-sm"><div class="container"><div class="section-header" style="margin-bottom:var(--space-4);"><span class="section-eyebrow">CHART</span><h2 class="section-title">价格 vs Token 上限</h2><p class="section-subtitle">绿色区域为高性价比区。</p></div><div class="chart-card"><div class="chart-container" id="priceVsTokenChart"></div></div></div></section>' +
      '<section class="section" id="tableSection"><div class="container"><div class="section-header" style="display:flex;justify-content:space-between;align-items:flex-end;flex-wrap:wrap;gap:16px;"><div><span class="section-eyebrow">FULL COMPARISON</span><h2 class="section-title">完整套餐对比表</h2></div><button class="table-toggle-btn" id="toggleColsBtn" onclick="toggleExtraCols()">展开全部列</button></div>' +
        '<div class="filter-bar"><select class="filter-select" id="sortSelect"><option value="">默认排序</option><option value="monthlyPrice-asc">月费 低-高</option><option value="monthlyPrice-desc">月费 高-低</option><option value="rating-desc">评分 高-低</option><option value="measuredMonthlyToken-desc">月Token 多-少</option><option value="tokensPerYuan-desc">性价比 高-低</option></select><input type="text" class="filter-select" id="searchInput" placeholder="搜索平台/套餐..." style="min-width:180px;"><button class="filter-chip" id="resetBtn">重置</button><span class="filter-stats">显示 <strong id="filterCount">0</strong> / '+plans.length+' 个套餐</span></div>' +
        '<div class="table-wrap"><table class="data-table"><thead><tr><th>平台</th><th>套餐</th><th>类型</th><th>评分</th><th>月费</th><th>月Token</th><th>每元Token</th><th>模型</th><th>标签</th><th>详情</th></tr></thead><tbody id="plansTableBody"></tbody></table></div>' +
        '<div class="plan-cards-view" id="plansCardsView"></div>' +
      '</div></section>' +
    '</div>' +

    // ===== BLOG TAB (lazy) =====
    '<div class="tab-panel" id="panel-blog"></div>' +

    // ===== WIZARD TAB =====
    '<div class="tab-panel" id="panel-wizard">' +
      '<div class="wizard-wrap"><div style="text-align:center;margin-bottom:var(--space-6);"><span class="section-eyebrow">WIZARD</span><h1 class="hero-title" style="font-size:28px;margin:0 auto 8px;">30 秒找到你的<br><span class="hero-title-accent">最佳 Coding Plan</span></h1><p style="font-size:14px;color:var(--text-tertiary);">回答 4 个问题，基于真实数据给你 Top 3 推荐。</p></div>' +
        '<div class="wizard-progress" id="wizProgress"></div>' +
        '<div id="wizardContainer"></div>' +
        '<div id="wizardResult"></div>' +
      '</div>' +
    '</div>' +

    // ===== JOIN TAB =====
    '<div class="tab-panel" id="panel-join">' +
      '<section class="hero" style="padding-bottom:var(--space-4);"><div class="container"><div class="blog-layout"><span class="section-eyebrow">COMMUNITY</span><h1 class="hero-title" style="font-size:clamp(24px,3vw,32px);">加入社群</h1><p class="hero-subtitle">价格变动、抢购提醒、实测反馈，第一时间发在社群里。</p></div></div></section>' +
      '<section class="section-sm"><div class="container"><div class="community-grid">'+['free','paid'].map(function(k){{ var c=config.community[k]; return'<div class="community-card community-card-'+k+'"><div class="community-card-header"><h3 class="community-card-title">'+escapeHtml(c.title)+'</h3><span class="badge'+(k==='paid'?' badge-premium':' badge-accent')+'">'+(k==='paid'?'PRO':'FREE')+'</span></div><div class="community-card-subtitle">'+escapeHtml(c.subtitle)+'</div><p class="community-card-desc">'+escapeHtml(c.description)+'</p><ul class="community-highlights">'+(c.highlights||[]).map(function(h){{return'<li>'+escapeHtml(h)+'</li>';}}).join('')+'</ul><a href="'+c.url+'" class="btn '+(k==='paid'?'btn-primary':'btn-secondary')+' btn-lg">'+escapeHtml(c.ctaText)+'</a></div>'; }}).join('')+'</div></div></section>' +
    '</div>';

  // Init table
  renderTable();
  bindTableFilters();
  bindScenarios();
  renderWizard();
}}

function applyScenario(id) {{
  var entry = (CPS.config.quickEntries||[]).find(function(q){{return q.id===id;}});
  if(!entry) return;
  CPS.state.filters.vendors.clear(); CPS.state.filters.types.clear(); CPS.state.filters.models.clear(); CPS.state.filters.tags.clear(); CPS.state.filters.monthlyPriceMax=null;
  var f=entry.filter||{{}};
  if(f.monthlyPriceMax) CPS.state.filters.monthlyPriceMax=f.monthlyPriceMax;
  if(f.model) CPS.state.filters.models.add(f.model);
  if(f.tag) CPS.state.filters.tags.add(f.tag);
  renderTable();
  switchTab('compare');
}}

function bindTableFilters() {{
  var sortSel=document.getElementById('sortSelect'), searchIn=document.getElementById('searchInput'), resetBtn=document.getElementById('resetBtn');
  if(sortSel) sortSel.addEventListener('change',function(){{ var v=sortSel.value; if(!v){{ CPS.state.sort={{key:null,dir:'asc'}}; }}else{{ var p=v.split('-'); CPS.state.sort={{key:p[0],dir:p[1]}}; }} renderTable(); }});
  if(searchIn) searchIn.addEventListener('input',function(){{ CPS.state.filters.search=searchIn.value.trim().toLowerCase(); renderTable(); }});
  if(resetBtn) resetBtn.addEventListener('click',function(){{ CPS.state.filters.vendors.clear(); CPS.state.filters.types.clear(); CPS.state.filters.models.clear(); CPS.state.filters.tags.clear(); CPS.state.filters.monthlyPriceMax=null; CPS.state.filters.search=''; CPS.state.sort={{key:null,dir:'asc'}}; if(sortSel) sortSel.value=''; if(searchIn) searchIn.value=''; renderTable(); }});
}}

function bindScenarios() {{
  document.querySelectorAll('.scenario-card').forEach(function(card){{ card.addEventListener('click',function(){{ applyScenario(card.dataset.entryId); }}); }});
}}

var _colsExpanded = false;
function toggleExtraCols() {{
  _colsExpanded = !_colsExpanded;
  document.querySelectorAll('td.col-extra').forEach(function(c){{ c.classList.toggle('col-hidden',!_colsExpanded); }});
  var btn = document.getElementById('toggleColsBtn');
  if(btn){{ btn.textContent = _colsExpanded ? '收起额外列' : '展开全部列'; btn.classList.toggle('active',_colsExpanded); }}
}}

document.addEventListener('DOMContentLoaded', init);
</script>
</body>
</html>"""

    return html


def main():
    """生成单文件 HTML 并保存到 dist/"""
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    output_path = DIST_DIR / "codingplan-saver.html"
    html = build_html()
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"HTML 已生成: {output_path}")
    print(f"文件大小: {len(html.encode('utf-8')) / 1024:.1f} KB")


if __name__ == "__main__":
    main()