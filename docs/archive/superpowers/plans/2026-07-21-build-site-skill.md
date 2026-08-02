# build-site Skill 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把 `project/codingplan-saver/` 重新实现为一个 skill 驱动的系统：输入是自然语言变动信号，输出是单文件 HTML。

**Architecture:** 三层（信号采集并行 / 归一化确认串行 / HTML 生成）+ 4 个 JSON 数据源（site/vendors/plans/changes）+ 项目级 skill 文档（`.claude/skills/build-site.md`）+ collector 重构（price_monitor 精简 + sources/ 新模块）。

**Tech Stack:** 纯静态 HTML（hash 路由 + ECharts CDN）+ Python collector（httpx + beautifulsoup4 + lxml）+ JSON 数据文件。

**Spec:** `docs/superpowers/specs/2026-07-21-build-site-skill-design.md`

---

## 总览

按 spec §13 分 3 个 milestone：

- **M1 骨架打通**（Task 1–9）：归档旧代码 + 新数据目录 + 迁移数据 + HTML 模板 + build 子命令
- **M2 数据更新闭环**（Task 10–16）：price_monitor 重构 + sources 框架 + 2 家示范 parser + update/scan 子命令
- **M3 厂商覆盖扩展**（Task 17–21）：Top 5 厂商 parser + pricing-urls.md 重构 + token_estimator 适配

每个 Task 独立可验证、独立 commit。

---

# Milestone 1 — 骨架打通（让 build 能跑）

**目标**：`/build-site build` 能从新数据目录读 JSON，输出可双击打开的单文件 HTML，4 个 Tab 都能渲染。

---

### Task 1: 归档旧多页面代码

**Files:**
- Create: `project/codingplan-saver/archive/README.md`
- Move: `project/codingplan-saver/{index,compare,blog,article,wizard,join,coding-agents}.html` → `archive/old-multi-page/`
- Move: `project/codingplan-saver/scripts/` → `archive/old-scripts/`
- Move: `project/codingplan-saver/styles/` → `archive/old-styles/`
- Move: `project/codingplan-saver/src/`, `vite.config.ts`, `tsconfig.app.json`, `package.json`, `package-lock.json` → `archive/old-src/`
- Move: `project/codingplan-saver/{config,plans,articles,price-changes,coding-agents}.json` → `archive/`
- Delete: `project/codingplan-saver/node_modules/`（不入 git，重装即可）

- [ ] **Step 1: 创建归档目录结构**

```bash
cd project/codingplan-saver
mkdir -p archive/old-multi-page archive/old-scripts archive/old-styles archive/old-src
```

- [ ] **Step 2: 用 git mv 归档 HTML 和资源**

```bash
cd project/codingplan-saver
git mv index.html compare.html blog.html article.html wizard.html join.html coding-agents.html archive/old-multi-page/
git mv scripts archive/old-scripts
git mv styles archive/old-styles
git mv src archive/old-src/src
git mv vite.config.ts tsconfig.app.json package.json package-lock.json archive/old-src/
```

- [ ] **Step 3: 归档旧 JSON（待迁移，先挪走）**

```bash
cd project/codingplan-saver
git mv config.json archive/old-config.json
git mv plans.json archive/old-plans.json
git mv articles.json archive/old-articles.json
git mv price-changes.json archive/old-price-changes.json
git mv coding-agents.json archive/old-coding-agents.json
```

- [ ] **Step 4: 删除 node_modules（gitignore 未跟踪）**

```bash
rm -rf project/codingplan-saver/node_modules
```

- [ ] **Step 5: 归档 build_html.py**

```bash
mkdir -p project/codingplan-saver/archive/old-builder
git mv tools/builder/build_html.py project/codingplan-saver/archive/old-builder/
```

- [ ] **Step 6: 写归档说明**

Create `project/codingplan-saver/archive/README.md`:

```markdown
# V1 归档（多页面架构）

这是 codingplan-saver 的 V1 实现，已被 V2（单文件 + skill 驱动）替代。

## 保留内容

- `old-multi-page/` — 6 个独立 HTML 页面（index/compare/blog/article/wizard/join）
- `old-scripts/shared.js` — 渲染逻辑（全局 CPS 对象）
- `old-styles/shared.css` — 设计 token 和样式系统（V2 沿用）
- `old-src/` — Vite + React 脚手架（未真正启用）
- `old-builder/build_html.py` — 旧 Python 单文件生成器
- `old-*.json` — 迁移前的原始数据（供参考）

## 为什么不删

保留供参考和回滚。V2 的 CSS 设计 token 直接继承自 `old-styles/shared.css`。
```

- [ ] **Step 7: 更新 .gitignore（dist/ 进 git）**

修改 `.gitignore`，移除 `dist/` 这一行（其他保留）。结果：

```
.DS_Store
*.log
node_modules/
.next/
build/
__pycache__/
*.pyc
*.egg-info/
.env
.env.local
.venv/
config.yaml

# Hot Trend — 采集数据（不跟踪，数据量大且频繁变化）
data/raw/
data/archive/

# 构建产物（dist/ 现在跟踪，因为是最终交付物）
```

- [ ] **Step 8: 验证归档完整性**

```bash
ls project/codingplan-saver/
# 应该看到: archive/  （只有这个）

ls project/codingplan-saver/archive/
# 应该看到: README.md old-builder/ old-config.json old-multi-page/ old-scripts/ old-src/ old-styles/ old-plans.json old-articles.json old-price-changes.json old-coding-agents.json
```

- [ ] **Step 9: Commit**

```bash
git add -A
git commit -m "refactor(codingplan-saver): 归档 V1 多页面架构到 archive/

- 6 个 HTML 页面 + scripts/ + styles/ + src/ + 旧 JSON 全部归档
- 删除 node_modules（未跟踪）
- 归档 build_html.py 到 archive/old-builder/
- .gitignore 移除 dist/（交付物将进 git）
- 保留 archive/old-styles/shared.css 供 V2 继承设计 token"
```

---

### Task 2: 创建新数据目录骨架

**Files:**
- Create: `project/codingplan-saver/data/site.json`
- Create: `project/codingplan-saver/data/vendors.json`
- Create: `project/codingplan-saver/data/plans.json`
- Create: `project/codingplan-saver/data/changes.json`
- Create: `project/codingplan-saver/data/history/.gitkeep`

- [ ] **Step 1: 创建目录**

```bash
mkdir -p project/codingplan-saver/data/history
touch project/codingplan-saver/data/history/.gitkeep
```

- [ ] **Step 2: 创建空的 site.json（占位，Task 4 填充）**

Create `project/codingplan-saver/data/site.json`:

```json
{}
```

- [ ] **Step 3: 同样创建 vendors.json / plans.json / changes.json 为空占位**

各文件内容均为：plans.json 和 vendors.json 是 `[]`，changes.json 是 `[]`，site.json 是 `{}`。

- [ ] **Step 4: Commit**

```bash
git add project/codingplan-saver/data/
git commit -m "feat(data): 创建 codingplan-saver/data/ 新数据目录骨架"
```

---

### Task 3: 写数据 schema 文档

**Files:**
- Create: `project/codingplan-saver/data/SCHEMA.md`

这一份文档是 AI 更新数据时的"宪法"，必须先于实际数据存在。

- [ ] **Step 1: 写 schema 文档**

Create `project/codingplan-saver/data/SCHEMA.md`，内容直接摘自 spec §3.3–§3.6 的完整字段定义（site.json / vendors.json / plans.json / changes.json 四份），加上枚举值说明和示例。

文档结构：

```markdown
# CodingPlan Saver 数据 Schema

> 本文件是数据更新的"宪法"。AI 更新任何 JSON 前必须对照此文档。

## 文件职责

| 文件 | 职责 | 更新方式 |
|------|------|---------|
| site.json | 站点配置（博主信息、推荐、社群） | 手动 |
| vendors.json | 厂商元信息（URL、提取策略） | 半自动（人 review URL） |
| plans.json | 套餐主数据 | 半自动（核心更新对象） |
| changes.json | 变动时间线（价格/模型/文章统一） | 半自动 |
| history/ | plans.json 历史快照 | 自动 |

## site.json
（粘贴 spec §3.3 的完整 schema + 字段说明）

## vendors.json
（粘贴 spec §3.4 的完整 schema + extractStrategy 枚举说明）

## plans.json
（粘贴 spec §3.5 的完整 schema + status/type/tier 枚举说明）

## changes.json
（粘贴 spec §3.6 的完整 schema + kind 枚举表）

## 迁移规则
（粘贴 spec §12.3）
```

- [ ] **Step 2: Commit**

```bash
git add project/codingplan-saver/data/SCHEMA.md
git commit -m "docs(data): 数据 schema 宪法文档"
```

---

### Task 4: 迁移 site.json（从旧 config.json）

**Files:**
- Modify: `project/codingplan-saver/data/site.json`
- Reference: `project/codingplan-saver/archive/old-config.json`

- [ ] **Step 1: 读取旧 config.json**

```bash
cat project/codingplan-saver/archive/old-config.json
```

- [ ] **Step 2: 按新 schema 重写 site.json**

根据 spec §3.3，去掉 `nav`、`site.url`，保留其他字段。具体改写规则：
- `site.*` 保留（除 `url`）
- `blogger.*` 全保留
- `header.*` 全保留
- `quickEntries[]` 全保留
- `recommendationGroups[]` 全保留
- `community.*` 全保留
- `disclosure` 保留
- `footer.*` 保留
- 删除 `nav`（HTML 内部 Tab，不需要导航配置）

把 `archive/old-config.json` 的内容手动转换后写入 `data/site.json`。

- [ ] **Step 3: 验证 JSON 合法**

```bash
python3 -c "import json; json.load(open('project/codingplan-saver/data/site.json')); print('OK')"
```

- [ ] **Step 4: Commit**

```bash
git add project/codingplan-saver/data/site.json
git commit -m "feat(data): 迁移 site.json（从旧 config.json 精简）"
```

---

### Task 5: 迁移 vendors.json（新建）

**Files:**
- Modify: `project/codingplan-saver/data/vendors.json`
- Reference: `tools/collector/collector/price_monitor.py` 的 PLATFORMS 表，`reference/pricing-urls.md`

- [ ] **Step 1: 从 price_monitor.py 提取厂商清单**

读取 PLATFORMS（19 家）+ plans.json 出现的额外厂商（TaoToken），按 spec §3.4 schema 构建。

- [ ] **Step 2: 写 vendors.json**

每个厂商一条，字段：`id` / `name` / `logo`（取 name 首字）/ `color`（散点图配色，复用 compare.html 的 vColors 映射）/ `urls.{pricing,docs,api,home}` / `extractStrategy`（默认 manual，待 Task 17+ 实测调整）/ `lastVerified: null` / `notes`。

19 家厂商的 `id` 清单：
```
zhipu, zhipu-intl, bytedance, deepseek, kimi, minimax, bailian, tencent,
claude, codex, github, baidu, xunfei, huawei, jd, mimo, youyun, opencode,
gongji, ollama, taotoken
```

（共 21 个 id，TaoToken 和智谱国际版单列）

URL 从 `reference/pricing-urls.md` 和 price_monitor.py 的 PLATFORMS 抄过来，`docs` 和 `api` 暂时留空字符串，Task 17+ 实测时补。

- [ ] **Step 3: 验证 JSON**

```bash
python3 -c "import json; d=json.load(open('project/codingplan-saver/data/vendors.json')); print(f'{len(d)} vendors'); print([v['id'] for v in d])"
```

预期输出：`21 vendors` + id 列表。

- [ ] **Step 4: Commit**

```bash
git add project/codingplan-saver/data/vendors.json
git commit -m "feat(data): 创建 vendors.json（21 家厂商元信息）"
```

---

### Task 6: 迁移 plans.json（从旧 plans.json 转换 schema）

**Files:**
- Modify: `project/codingplan-saver/data/plans.json`
- Reference: `project/codingplan-saver/archive/old-plans.json`

- [ ] **Step 1: 写迁移脚本（一次性用，不入库）**

Create `project/codingplan-saver/data/_migrate_plans.py`（临时脚本）：

```python
"""一次性迁移脚本：old-plans.json → 新 schema plans.json"""
import json
from pathlib import Path

SRC = Path(__file__).parent.parent / "archive" / "old-plans.json"
DST = Path(__file__).parent / "plans.json"

VENDOR_ID_MAP = {
    "智谱AI": "zhipu", "智谱国际版": "zhipu-intl", "字节·方舟": "bytedance",
    "DeepSeek 官方": "deepseek", "Kimi": "kimi", "MiniMax": "minimax",
    "阿里·百炼": "bailian", "腾讯云": "tencent", "Claude": "claude",
    "Codex (ChatGPT)": "codex", "GitHub": "github", "百度·千帆": "baidu",
    "讯飞·星火": "xunfei", "华为云": "huawei", "京东云": "jd",
    "小米·MiMo": "mimo", "优云智算": "youyun", "OpenCode": "opencode",
    "共继算力": "gongji", "Ollama": "ollama", "TaoToken": "taotoken",
}

def derive_tier(plan_name: str) -> str:
    p = plan_name.lower()
    if any(x in p for x in ["lite", "mini", "starter", "入门"]): return "lite"
    if any(x in p for x in ["max", "ultra", "premium", "旗舰"]): return "max"
    return "pro"

def migrate(old: dict) -> dict:
    vendor = old["vendor"]
    vendor_id = VENDOR_ID_MAP.get(vendor, "unknown")
    plan_lower = old["plan"].lower().replace(" ", "-")
    return {
        "id": f"{vendor_id}-{plan_lower}",
        "vendor": vendor,
        "vendorId": vendor_id,
        "plan": old["plan"],
        "type": old.get("type", "Coding Plan"),
        "tier": derive_tier(old["plan"]),
        "monthlyPrice": old.get("monthlyPrice"),
        "currency": old.get("currency", "¥"),
        "firstMonthPrice": old.get("firstMonthPrice"),
        "rating": old.get("rating", 4),
        "models": old.get("models", []),
        "monthlyRequests": old.get("monthlyRequests"),
        "tokenLimit": old.get("tokenLimit"),
        "measuredMonthlyToken": old.get("measuredMonthlyToken"),
        "tags": old.get("tags", []),
        "bloggerVerdict": old.get("bloggerVerdict", ""),
        "action": old.get("action", ""),
        "status": "active",  # 默认 active，暂停的需手工改
        "source": "manual",
        "updatedAt": "2026-07-20",
    }

def main():
    with open(SRC, encoding="utf-8") as f:
        old_list = json.load(f)
    new_list = [migrate(p) for p in old_list]
    with open(DST, "w", encoding="utf-8") as f:
        json.dump(new_list, f, ensure_ascii=False, indent=2)
    print(f"Migrated {len(new_list)} plans")

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: 运行迁移**

```bash
cd project/codingplan-saver/data
python3 _migrate_plans.py
```

预期输出：`Migrated 31 plans`（或旧文件实际条数）。

- [ ] **Step 3: 手工修正特殊状态**

人工检查 plans.json，把已知暂停的套餐 `status` 改为 `paused`（参考旧 `price-changes.json` 里 Kimi 暂停订阅的条目，把 Kimi 的所有 plan 改 `paused`）。

- [ ] **Step 4: 删除临时脚本**

```bash
rm project/codingplan-saver/data/_migrate_plans.py
```

- [ ] **Step 5: 验证 JSON**

```bash
python3 -c "import json; d=json.load(open('project/codingplan-saver/data/plans.json')); print(f'{len(d)} plans'); print(d[0])"
```

- [ ] **Step 6: Commit**

```bash
git add project/codingplan-saver/data/plans.json
git commit -m "feat(data): 迁移 plans.json 到新 schema（31 套餐）

- 新增 vendorId / tier / source 字段
- 删除 quarterly/yearly/fiveHours/weekly 等未用字段
- status 枚举化（paused 状态手工修正）
- 临时迁移脚本已删除"
```

---

### Task 7: 迁移 changes.json（合并旧 price-changes + articles）

**Files:**
- Modify: `project/codingplan-saver/data/changes.json`
- Reference: `archive/old-price-changes.json`, `archive/old-articles.json`

- [ ] **Step 1: 写迁移脚本**

Create `project/codingplan-saver/data/_migrate_changes.py`:

```python
"""一次性迁移：price-changes + articles → 统一 changes.json"""
import json
from pathlib import Path

ARCHIVE = Path(__file__).parent.parent / "archive"
DST = Path(__file__).parent / "changes.json"

KIND_MAP = {
    "计费调整": "price_change", "新增模型": "new_model", "新增平台": "new_plan",
    "暂停订阅": "subscription_pause", "订阅调整": "price_change",
    "新模型即将发布": "new_model",
}

def slugify(s: str) -> str:
    import re
    s = re.sub(r'[^\w\u4e00-\u9fff]', '-', s.lower())
    return re.sub(r'-+', '-', s).strip('-')[:30]

def migrate_price_change(c: dict) -> dict:
    kind = KIND_MAP.get(c.get("type", ""), "price_change")
    return {
        "id": f"{c['date']}-{slugify(c['vendor'])}-{kind}",
        "date": c["date"],
        "kind": kind,
        "vendor": c["vendor"],
        "title": f"{c['vendor']} {c['type']}",
        "detail": c["detail"],
        "impact": c["impact"],
        "level": c.get("impactLevel", "medium"),
        "source": "manual",
        "sourceUrl": None,
        "relatedPlans": [],
        "featured": c.get("impactLevel") == "high",
        "excerpt": None, "author": None, "readTime": None, "cover": None,
    }

def migrate_article(a: dict) -> dict:
    return {
        "id": a["id"],  # 保留原 hash id
        "date": a["date"],
        "kind": "article",
        "vendor": "通用",
        "title": a["title"],
        "detail": a.get("excerpt", a["title"]),
        "impact": "neutral",
        "level": "medium",
        "source": "signal-dailyhot",
        "sourceUrl": a.get("url"),
        "relatedPlans": [],
        "featured": a.get("featured", False),
        "excerpt": a.get("excerpt"),
        "author": a.get("author"),
        "readTime": a.get("readTime"),
        "cover": a.get("cover"),
    }

def main():
    changes = []
    # price-changes
    pc_path = ARCHIVE / "old-price-changes.json"
    if pc_path.exists():
        with open(pc_path, encoding="utf-8") as f:
            pc = json.load(f)
        changes.extend(migrate_price_change(c) for c in pc["changes"])
    # articles
    a_path = ARCHIVE / "old-articles.json"
    if a_path.exists():
        with open(a_path, encoding="utf-8") as f:
            arts = json.load(f)
        changes.extend(migrate_article(a) for a in arts)
    # 按 date 倒序
    changes.sort(key=lambda x: x["date"], reverse=True)
    with open(DST, "w", encoding="utf-8") as f:
        json.dump(changes, f, ensure_ascii=False, indent=2)
    print(f"Migrated {len(changes)} changes")

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: 运行迁移**

```bash
cd project/codingplan-saver/data
python3 _migrate_changes.py
```

预期：`Migrated 40 changes`（10 price-changes + 30 articles）。

- [ ] **Step 3: 删除临时脚本**

```bash
rm project/codingplan-saver/data/_migrate_changes.py
```

- [ ] **Step 4: 验证**

```bash
python3 -c "import json; d=json.load(open('project/codingplan-saver/data/changes.json')); print(f'{len(d)} changes'); kinds={}; [kinds.setdefault(c['kind'],0) or kinds.__setitem__(c['kind'], kinds[c['kind']]+1) for c in d]; print(kinds)"
```

- [ ] **Step 5: Commit**

```bash
git add project/codingplan-saver/data/changes.json
git commit -m "feat(data): 迁移 changes.json（合并 price-changes + articles）

- price-changes 生成新 id: {date}-{vendor-slug}-{kind}
- articles 保留原 hash id（避免破坏外链）
- 按 date 倒序，共 40 条"
```

---

### Task 8: 写 HTML 模板（template/index.html）

**Files:**
- Create: `project/codingplan-saver/template/index.html`

这是"标准件"参考实现，build 模式生成 dist/ 时直接基于它替换占位符。

- [ ] **Step 1: 写 HTML 模板骨架**

Create `project/codingplan-saver/template/index.html`。这个文件要包含：
- `<head>` 内联 CSS（从 `archive/old-styles/shared.css` 继承设计 token，加 4-Tab 新样式）
- `<body>` 结构：Nav + 4 个 Tab panel + Footer
- 数据嵌入：`<script id="cp-data" type="application/json">{{DATA}}</script>`（占位符）
- JS：Tab 切换（hash 路由）+ 数据加载 + 各 Tab 渲染函数

完整内容较长（~600 行），结构大纲：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>CodingPlan 省钱攻略</title>
  <style>
    /* === Design Tokens（从 archive/old-styles/shared.css :root 复制）=== */
    :root { --bg-base: #090d14; --accent: #10b981; ... }
    /* === Reset + Base === */
    *,*::before,*::after{box-sizing:border-box}
    body{font-family:var(--font-sans);background:var(--bg-base);color:var(--text-primary)}
    .container{max-width:var(--container-max);margin:0 auto;padding:0 var(--space-5)}
    /* === Nav === */
    .nav{...} .nav-tab{...} .nav-tab.active{...}
    /* === Tab Panels === */
    .tab-panel{display:none} .tab-panel.active{display:block}
    /* === Hero / Top picks / Scenario / Reco / Filter / Table / Chart / Timeline / Community === */
    /* （全部沿用旧 shared.css 的类名和样式，按需调整） */
  </style>
</head>
<body>
  <nav class="nav">
    <div class="container nav-inner">
      <a href="#recommend" class="nav-brand">{{site.name}}</a>
      <div class="nav-tabs">
        <a href="#recommend" class="nav-tab active">推荐</a>
        <a href="#compare" class="nav-tab">对比</a>
        <a href="#updates" class="nav-tab">动态</a>
        <a href="#community" class="nav-tab">社群</a>
      </div>
      <a href="#community" class="nav-cta">加入社群</a>
    </div>
  </nav>

  <main>
    <section id="tab-recommend" class="tab-panel active"><div class="container" id="recommend-body"></div></section>
    <section id="tab-compare" class="tab-panel"><div class="container" id="compare-body"></div></section>
    <section id="tab-updates" class="tab-panel"><div class="container" id="updates-body"></div></section>
    <section id="tab-community" class="tab-panel"><div class="container" id="community-body"></div></section>
  </main>

  <footer class="footer"><div class="container" id="footer-body"></div></footer>

  <script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js"></script>
  <script id="cp-data" type="application/json">{{DATA}}</script>
  <script>
    // === Data load ===
    const DATA = JSON.parse(document.getElementById('cp-data').textContent);
    const {site, vendors, plans, changes} = DATA;

    // === Utils (escapeHtml, formatPrice, renderStars, ...) ===
    // 从 archive/old-scripts/shared.js 移植

    // === Tab routing ===
    function switchTab(hash) { ... }
    window.addEventListener('hashchange', () => switchTab(location.hash));

    // === Render: Recommend ===
    function renderRecommend() { ... }

    // === Render: Compare (table + filter + chart) ===
    function renderCompare() { ... }

    // === Render: Updates (timeline) ===
    function renderUpdates() { ... }

    // === Render: Community ===
    function renderCommunity() { ... }

    // === Init ===
    document.addEventListener('DOMContentLoaded', () => {
      renderRecommend(); renderCompare(); renderUpdates(); renderCommunity();
      switchTab(location.hash || '#recommend');
    });
  </script>
</body>
</html>
```

**实现要点**（写模板时必须落地）：
- 工具函数从 `archive/old-scripts/shared.js` 移植：`escapeHtml` `formatPrice` `formatNumber` `renderStars` `renderTagsInline` `renderMarkdownLite`
- 推荐页 Top 3 算法从 `archive/old-multi-page/index.html` 的 `renderTopPicks()` 移植
- 对比页表格 + 筛选 + 散点图从 `archive/old-multi-page/compare.html` 移植
- 动态页是**全新**的（合并时间线），参考 `archive/old-scripts/shared.js` 的 `renderPriceChangesInline` + `blog.html` 的列表样式
- 社群页从 `index.html` 的 `renderCommunitySection` 移植
- 散点图的 vendor 颜色从 `vendors.json` 的 `color` 字段读取（不再硬编码）

- [ ] **Step 2: 手工填充测试数据验证模板**

把 `{{DATA}}` 替换为实际 JSON（从 `data/*.json` 读出来组合），在浏览器打开验证 4 个 Tab 都能渲染。

```bash
python3 <<'EOF'
import json
from pathlib import Path
data_dir = Path("project/codingplan-saver/data")
data = {
    "site": json.load(open(data_dir/"site.json")),
    "vendors": json.load(open(data_dir/"vendors.json")),
    "plans": json.load(open(data_dir/"plans.json")),
    "changes": json.load(open(data_dir/"changes.json")),
}
tpl = open("project/codingplan-saver/template/index.html").read()
html = tpl.replace("{{DATA}}", json.dumps(data, ensure_ascii=False))
open("/tmp/cp-test.html","w").write(html)
print("Wrote /tmp/cp-test.html, size:", len(html))
EOF
open /tmp/cp-test.html
```

- [ ] **Step 3: 修复模板里发现的问题**

在浏览器里逐 Tab 检查，发现问题回到 Step 1 修复模板。常见问题：CSS 变量未定义、JS 函数引用错误、占位符替换时 JSON 转义问题。

- [ ] **Step 4: Commit**

```bash
git add project/codingplan-saver/template/index.html
git commit -m "feat(template): HTML 模板标准件（4 Tab + hash 路由）

- Nav + 4 个 Tab panel + Footer 结构
- 数据嵌入: <script id=\"cp-data\" type=\"application/json\">{{DATA}}</script>
- Tab 切换: hash 路由 (#recommend/#compare/#updates/#community)
- ECharts CDN 散点图，vendor 配色从 vendors.json 读
- 设计 token 继承自 V1 shared.css"
```

---

### Task 9: 写 build 子命令的构建脚本

**Files:**
- Create: `tools/builder/build.py`（替代旧的 build_html.py，轻量版）

- [ ] **Step 1: 写构建脚本**

Create `tools/builder/build.py`:

```python
"""
HTML 构建器 — 读 JSON + 套模板 → 输出单文件 HTML

用法: python3 tools/builder/build.py
输出: dist/codingplan-saver.html
"""
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = ROOT / "project" / "codingplan-saver" / "data"
TEMPLATE = ROOT / "project" / "codingplan-saver" / "template" / "index.html"
DIST = ROOT / "dist" / "codingplan-saver.html"

def load_json(name):
    p = DATA_DIR / name
    if not p.exists():
        return {} if name == "site.json" else []
    return json.loads(p.read_text(encoding="utf-8"))

def main():
    if not TEMPLATE.exists():
        raise SystemExit(f"❌ 模板不存在: {TEMPLATE}")

    data = {
        "site": load_json("site.json"),
        "vendors": load_json("vendors.json"),
        "plans": load_json("plans.json"),
        "changes": load_json("changes.json"),
        "generatedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    tpl = TEMPLATE.read_text(encoding="utf-8")
    # 替换占位符（注意 </script> 在 JSON 里会破坏 HTML 解析，需转义）
    data_json = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    html = tpl.replace("{{DATA}}", data_json)

    DIST.parent.mkdir(parents=True, exist_ok=True)
    DIST.write_text(html, encoding="utf-8")
    size_kb = len(html.encode("utf-8")) / 1024
    print(f"✅ 生成: {DIST}")
    print(f"   大小: {size_kb:.1f} KB")
    print(f"   打开: open {DIST}")

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: 运行构建**

```bash
python3 tools/builder/build.py
```

预期：`✅ 生成: .../dist/codingplan-saver.html` + 文件大小。

- [ ] **Step 3: 浏览器打开验证**

```bash
open dist/codingplan-saver.html
```

4 个 Tab 都能正常切换、数据正常渲染。

- [ ] **Step 4: Commit**

```bash
git add tools/builder/build.py dist/codingplan-saver.html
git commit -m "feat(builder): build 脚本 + 首个 dist/codingplan-saver.html

- tools/builder/build.py: 读 data/*.json + 套模板 → dist/
- JSON 嵌入时转义 </ 避免破坏 HTML 解析
- dist/ 进入 git（最终交付物）"
```

---

### Task 10: 写 SKILL.md（仅 build 模式部分）

**Files:**
- Create: `.claude/skills/build-site.md`（替换旧同名文件）

M1 阶段只写 build 模式 + schema 引用，update/scan 模式在 M2 补。

- [ ] **Step 1: 写 SKILL.md 的 build 模式部分**

Create `.claude/skills/build-site.md`，结构：

```markdown
# /build-site — CodingPlan 省钱攻略 数据更新 + HTML 生成

## 触发
- `/build-site` 或 `/build-site build` — 读数据生成 HTML
- `/build-site update [自然语言]` — 更新数据（见 M2 后补全）
- `/build-site scan` — 扫描信号（见 M2 后补全）

## build 模式工作流

### 何时用
- 数据已更新，想重新生成 HTML
- 模板有改动，想验证新输出

### 步骤
1. 读 `project/codingplan-saver/data/` 下 4 个 JSON
2. 运行 `python3 tools/builder/build.py`
3. 输出到 `dist/codingplan-saver.html`
4. 报告文件大小，提示 `open` 命令

### 数据校验
构建前 AI 应对照 `project/codingplan-saver/data/SCHEMA.md` 快速检查：
- plans.json 每条有 id/vendor/vendorId/plan/monthlyPrice
- changes.json 每条有 id/date/kind/vendor/title
- 缺失字段 → 用默认值（如 status 默认 active），不阻塞构建

## 数据 Schema 宪法
见 `project/codingplan-saver/data/SCHEMA.md`

## HTML 模板
见 `project/codingplan-saver/template/index.html`

## 文件结构
（粘贴 spec §8 的结构树）

## update 模式（M2 实现后补全）
TODO

## scan 模式（M2 实现后补全）
TODO
```

- [ ] **Step 2: 删除旧 build-site.md 的 M1 无关内容**

旧文件 `.claude/skills/build-site.md` 已在 Task 1 归档了吗？没有——它在 `.claude/skills/`，不在 `project/codingplan-saver/`。需要单独处理：

```bash
# 备份旧版到 archive
mkdir -p project/codingplan-saver/archive/old-skill
cp .claude/skills/build-site.md project/codingplan-saver/archive/old-skill/build-site-v1.md
# 然后用 Step 1 的新内容覆盖 .claude/skills/build-site.md
```

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/build-site.md project/codingplan-saver/archive/old-skill/
git commit -m "docs(skill): 写 build-site SKILL.md（M1: 仅 build 模式）

update/scan 模式待 M2 实现。旧版备份到 archive/old-skill/。"
```

---

# Milestone 1 完成检查点

- [ ] `python3 tools/builder/build.py` 能成功输出 `dist/codingplan-saver.html`
- [ ] 浏览器打开 dist/ HTML，4 个 Tab 都能切换和渲染
- [ ] 散点图正常显示（需要联网加载 ECharts CDN）
- [ ] `git log` 显示 Task 1–10 的清晰提交
- [ ] `project/codingplan-saver/` 只剩 `archive/` `data/` `template/` 三个目录

✅ 验证通过后，进入 M2。

---

# Milestone 2 — 数据更新闭环

**目标**：`/build-site update "..."` 能合并自动信号 + 用户输入，输出 diff，确认后写入 JSON。

---

### Task 11: 更新 collector 依赖

**Files:**
- Modify: `tools/collector/pyproject.toml`

- [ ] **Step 1: 加 beautifulsoup4 + lxml 依赖**

修改 `tools/collector/pyproject.toml`:

```toml
dependencies = [
    "httpx>=0.27",
    "feedparser>=6.0",
    "beautifulsoup4>=4.12",
    "lxml>=5.0",
]
```

- [ ] **Step 2: 安装**

```bash
cd tools/collector
source .venv/bin/activate
pip install -e .
```

- [ ] **Step 3: 验证**

```bash
python3 -c "from bs4 import BeautifulSoup; print('OK')"
```

- [ ] **Step 4: Commit**

```bash
git add tools/collector/pyproject.toml
git commit -m "feat(collector): 加 beautifulsoup4 + lxml 依赖"
```

---

### Task 12: 重构 price_monitor.py

**Files:**
- Modify: `tools/collector/collector/price_monitor.py`

去掉 `_scrape_direct()`（SPA 正则产垃圾），保留 `_fetch_dailyhot_news()`（实测可用），改输出到 `data/signals/`。

- [ ] **Step 1: 精简 price_monitor.py**

重写 `price_monitor.py`，只保留信号扫描功能：

```python
"""
价格信号扫描器 — 从 DailyHotApi 科技源检测 AI Coding Plan 价格变动信号

输出: data/signals/{date}.json
  [{title, url, source, keywords, platforms, detected_at}, ...]

注: 不再尝试直接爬取 SPA 定价页（实测产垃圾数据）。
    定价页结构化提取由 sources/ 模块负责（按厂商单独实现）。
"""
import asyncio
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import httpx

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
SIGNALS_DIR = PROJECT_ROOT / "data" / "signals"
VENDORS_PATH = PROJECT_ROOT / "project" / "codingplan-saver" / "data" / "vendors.json"
DAILYHOT_BASE = os.getenv("DAILYHOT_BASE", "http://localhost:6688")

TECH_SOURCES = ["36kr", "ithome", "sspai", "juejin", "v2ex"]

PRICE_KEYWORDS = [
    "涨价", "降价", "调价", "价格", "定价", "计费",
    "新套餐", "新增模型", "下架", "售罄", "暂停",
    "Coding Plan", "Token Plan", "月费", "额度",
    "免费", "公测", "限时", "活动", "折扣",
    "倍率", "并发", "请求", "订阅",
]

def load_vendors() -> list[dict]:
    if not VENDORS_PATH.exists():
        return []
    return json.loads(VENDORS_PATH.read_text(encoding="utf-8"))

async def scan_dailyhot(client: httpx.AsyncClient) -> list[dict]:
    vendors = load_vendors()
    signals = []
    for source in TECH_SOURCES:
        try:
            resp = await client.get(f"{DAILYHOT_BASE}/{source}", timeout=15)
            if resp.status_code != 200:
                continue
            items = resp.json().get("data", [])
            for item in items:
                title = str(item.get("title", ""))
                matched_kw = [kw for kw in PRICE_KEYWORDS if kw in title]
                if not matched_kw:
                    continue
                matched_vendors = [
                    v["name"] for v in vendors
                    if v["name"] in title or v["id"] in title.lower()
                ] or ["通用"]
                signals.append({
                    "title": title,
                    "url": item.get("url", ""),
                    "source": f"dailyhot:{source}",
                    "keywords": matched_kw,
                    "vendors": matched_vendors,
                    "detected_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                })
        except Exception as e:
            print(f"  ⚠️ DailyHotApi/{source} 失败: {e}")
    return signals

async def run() -> str:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    date_str = ts[:10]
    print(f"🔍 信号扫描 — {ts}")
    async with httpx.AsyncClient(timeout=30) as client:
        signals = await scan_dailyhot(client)
    print(f"  发现 {len(signals)} 条信号")

    SIGNALS_DIR.mkdir(parents=True, exist_ok=True)
    out = SIGNALS_DIR / f"{date_str}.json"
    out.write_text(json.dumps({
        "timestamp": ts, "count": len(signals), "signals": signals,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ {out}")
    return str(out)

def main():
    asyncio.run(run())

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: 测试（需要 DailyHotApi 运行，否则降级）**

```bash
cd tools/collector && source .venv/bin/activate
python3 -m collector.price_monitor
```

如果 DailyHotApi 没跑：应该看到 `⚠️ DailyHotApi/36kr 失败: ...` 但脚本正常退出，输出空 signals 文件。

- [ ] **Step 3: Commit**

```bash
git add tools/collector/collector/price_monitor.py
git commit -m "refactor(price_monitor): 去掉 _scrape_direct，只保留信号扫描

- 删除对 SPA 定价页的正则匹配（实测产垃圾）
- 改输出到 data/signals/{date}.json
- vendor 匹配改读 vendors.json（不再硬编码 PLATFORMS）"
```

---

### Task 13: 写 sources 框架（base.py + __init__.py）

**Files:**
- Create: `tools/collector/collector/sources/__init__.py`
- Create: `tools/collector/collector/sources/base.py`
- Create: `tools/collector/collector/sources/runner.py`

- [ ] **Step 1: 写 base.py**

Create `tools/collector/collector/sources/base.py`:

```python
"""厂商定价页提取器基类"""
from dataclasses import dataclass, field

@dataclass
class ExtractResult:
    vendor_id: str
    vendor_name: str
    plans: list[dict] = field(default_factory=list)  # 提取到的套餐字段
    extracted_fields: list[str] = field(default_factory=list)  # 实际拿到的字段名
    missing_fields: list[str] = field(default_factory=list)
    source_url: str = ""
    fetched_at: str = ""
    error: str | None = None

class BaseParser:
    """每个厂商的 parser 继承此类"""
    vendor_id: str = ""
    vendor_name: str = ""

    def __init__(self, vendor_config: dict):
        self.config = vendor_config
        self.vendor_id = vendor_config["id"]
        self.vendor_name = vendor_config["name"]

    async def extract(self, client) -> ExtractResult:
        """子类实现：用 client httpx.get 拉页面/JSON，返回 ExtractResult"""
        raise NotImplementedError
```

- [ ] **Step 2: 写 __init__.py（注册表）**

Create `tools/collector/collector/sources/__init__.py`:

```python
"""sources 模块：按厂商提取定价数据

注册表 VENDOR_PARSERS: vendor_id → Parser 类
未注册的 vendor_id 跳过（走 manual 策略）"""
from .base import BaseParser, ExtractResult

# 延迟导入避免循环
_VENDOR_PARSERS: dict[str, type[BaseParser]] = {}

def register(vendor_id: str):
    """装饰器：注册 parser 类"""
    def deco(cls):
        _VENDOR_PARSERS[vendor_id] = cls
        return cls
    return deco

def get_parser(vendor_id: str) -> type[BaseParser] | None:
    return _VENDOR_PARSERS.get(vendor_id)

def load_all():
    """触发所有 parser 模块导入（填充注册表）"""
    from . import deepseek  # noqa: F401,E402  (M2 示范)
    # Task 17+ 会追加: from . import zhipu, bytedance, kimi, minimax
```

- [ ] **Step 3: 写 runner.py（调度器）**

Create `tools/collector/collector/sources/runner.py`:

```python
"""sources 调度器：读 vendors.json，并行跑所有 parser"""
import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path

import httpx

from . import get_parser, load_all
from .base import ExtractResult, BaseParser

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
VENDORS_PATH = PROJECT_ROOT / "project" / "codingplan-saver" / "data" / "vendors.json"
SIGNALS_DIR = PROJECT_ROOT / "data" / "signals"

async def run_all() -> list[ExtractResult]:
    """并行跑所有注册的 parser，返回结果列表"""
    load_all()
    vendors = json.loads(VENDORS_PATH.read_text(encoding="utf-8"))
    results: list[ExtractResult] = []

    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        tasks = []
        for v in vendors:
            if v.get("extractStrategy") == "manual":
                continue  # 跳过无源的
            parser_cls = get_parser(v["id"])
            if not parser_cls:
                continue  # 还没实现 parser 的
            tasks.append(_safe_extract(parser_cls(v), client))
        results = await asyncio.gather(*tasks)
    return [r for r in results if r]

async def _safe_extract(parser: BaseParser, client) -> ExtractResult | None:
    try:
        result = await parser.extract(client)
        result.fetched_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        print(f"  ✅ {parser.vendor_name}: {len(result.plans)} plans, fields={result.extracted_fields}")
        return result
    except Exception as e:
        print(f"  ❌ {parser.vendor_name}: {e}")
        return ExtractResult(
            vendor_id=parser.vendor_id, vendor_name=parser.vendor_name,
            error=str(e)[:200], fetched_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        )

def save_results(results: list[ExtractResult], date_str: str):
    """保存到 data/signals/extract-{date}.json"""
    SIGNALS_DIR.mkdir(parents=True, exist_ok=True)
    out = SIGNALS_DIR / f"extract-{date_str}.json"
    data = [
        {
            "vendorId": r.vendor_id, "vendor": r.vendor_name,
            "plans": r.plans, "extractedFields": r.extracted_fields,
            "missingFields": r.missing_fields, "sourceUrl": r.source_url,
            "fetchedAt": r.fetched_at, "error": r.error,
        }
        for r in results
    ]
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ {out}")
    return str(out)

async def main():
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    print(f"🌐 sources 提取 — {date_str}")
    results = await run_all()
    save_results(results, date_str)

if __name__ == "__main__":
    asyncio.run(main())
```

- [ ] **Step 4: Commit**

```bash
git add tools/collector/collector/sources/
git commit -m "feat(sources): 提取器框架（base + 注册表 + runner）

- BaseParser: 子类实现 extract() 返回 ExtractResult
- 注册表: @register(vendor_id) 装饰器
- runner: 读 vendors.json 并行跑所有 parser，输出 data/signals/extract-{date}.json"
```

---

### Task 14: 写第一家 parser（DeepSeek 示范）

**Files:**
- Create: `tools/collector/collector/sources/deepseek.py`
- Modify: `project/codingplan-saver/data/vendors.json`（补 deepseek 的 docs URL）

DeepSeek 的 `api-docs.deepseek.com/quick_start/pricing` 是文档站，最可能 httpx 拿到。

- [ ] **Step 1: 手工访问 DeepSeek 文档页确认结构**

```bash
curl -s -L https://api-docs.deepseek.com/quick_start/pricing | head -100
```

观察：是静态 HTML 还是 SPA？价格信息在什么标签里？

- [ ] **Step 2: 根据 Step 1 观察，写 parser**

Create `tools/collector/collector/sources/deepseek.py`（具体选择器根据 Step 1 实际结构调整）:

```python
"""DeepSeek 定价页提取器

目标: https://api-docs.deepseek.com/quick_start/pricing
策略: 文档站静态 HTML，httpx + BeautifulSoup 解析
"""
from bs4 import BeautifulSoup
from . import register
from .base import BaseParser, ExtractResult

DEEPSEEK_FIELDS = ["monthlyPrice", "models"]  # 期望提取的字段

@register("deepseek")
class DeepSeekParser(BaseParser):
    async def extract(self, client) -> ExtractResult:
        url = self.config.get("urls", {}).get("docs") or "https://api-docs.deepseek.com/quick_start/pricing"
        resp = await client.get(url, timeout=20)
        if resp.status_code != 200:
            return ExtractResult(
                vendor_id=self.vendor_id, vendor_name=self.vendor_name,
                source_url=url, error=f"HTTP {resp.status_code}",
            )
        soup = BeautifulSoup(resp.text, "lxml")
        plans = []
        extracted = []

        # === 根据实际页面结构写选择器 ===
        # 以下为占位，必须根据 Step 1 的 curl 结果替换
        # 示例（假设页面有 <table class="pricing">）:
        # for row in soup.select("table.pricing tr"):
        #     cells = row.find_all("td")
        #     if len(cells) >= 2:
        #         plans.append({"plan": cells[0].text.strip(), "monthlyPrice": _parse_price(cells[1].text)})
        #         extracted.append("monthlyPrice")

        missing = [f for f in DEEPSEEK_FIELDS if f not in extracted]
        return ExtractResult(
            vendor_id=self.vendor_id, vendor_name=self.vendor_name,
            plans=plans, extracted_fields=extracted, missing_fields=missing,
            source_url=url,
        )

def _parse_price(text: str) -> float | None:
    import re
    m = re.search(r"(\d+(?:\.\d+)?)", text.replace(",", ""))
    return float(m.group(1)) if m else None
```

**重要**：Step 2 的选择器代码是占位，必须根据 Step 1 实际 curl 结果改写。

- [ ] **Step 3: 更新 vendors.json 的 deepseek 条目**

把 `vendors.json` 里 deepseek 的 `extractStrategy` 改为 `"docs"`，`urls.docs` 填入实际 URL，`lastVerified` 填今天。

- [ ] **Step 4: 测试**

```bash
cd tools/collector && source .venv/bin/activate
python3 -c "
import asyncio
from collector.sources.runner import run_all, save_results
from datetime import datetime
results = asyncio.run(run_all())
for r in results:
    print(f'{r.vendor_name}: plans={len(r.plans)} fields={r.extracted_fields} err={r.error}')
save_results(results, datetime.now().strftime('%Y-%m-%d'))
"
```

- [ ] **Step 5: Commit**

```bash
git add tools/collector/collector/sources/deepseek.py project/codingplan-saver/data/vendors.json
git commit -m "feat(sources): DeepSeek parser（首家示范）"
```

---

### Task 15: 写 update 子命令的逻辑（AI 工作流，非代码）

这一步不是写脚本，而是**在 SKILL.md 里固化 update 模式的具体步骤**，让 AI 知道怎么执行。

**Files:**
- Modify: `.claude/skills/build-site.md`

- [ ] **Step 1: 在 SKILL.md 补全 update 模式**

替换 SKILL.md 里的 `## update 模式（M2 实现后补全） TODO`：

```markdown
## update 模式工作流

### 触发
`/build-site update [自然语言]`

### 步骤

**Step 1: 并行采集信号（dispatch 3 个 sub-agent）**

用 Agent 工具同时发起 3 个并行任务：
- Agent-Scan: 跑 `cd tools/collector && source .venv/bin/activate && python3 -m collector.price_monitor`，读 `data/signals/{date}.json`
- Agent-RSS: httpx 拉以下 RSSHub 路由（http://localhost:1200）：
  - /deepseek/news
  - /qwen/blog
  - /qbitai/category/AI
  - /aibase/news
  提取标题含关键词的条目
- Agent-Httpx: 跑 `python3 -m collector.sources.runner`，读 `data/signals/extract-{date}.json`

**Step 2: 合并信号**

主 agent 把三路结果合并：
- 自动信号（Step 1） ∪ 解析用户的自然语言输入
- 去重（同一 vendor + 同一 kind 视为同一条）
- 分类：哪些需要改 plans.json，哪些只需加 changes.json

**Step 3: 按 schema 草拟变更**

对照 `data/SCHEMA.md`，生成两个 unified diff：
- `changes.json` 新增条目（kind/date/vendor/title/detail/impact/level）
- `plans.json` 字段修改（如 monthlyPrice/status/models）

**Step 4: 输出 diff，请用户确认**

格式：
```
变更预览：
[changes.json] +3 条
  + 2026-07-21-kimi-resume | subscription_pause | Kimi 恢复订阅 | positive
  + ...

[plans.json] 修改 2 条
  ~ kimi-moderato: status paused → active
  ~ ...

确认应用？(y/n/改某条)
```

**Step 5: 应用变更（用户 y 之后）**

1. 快照当前 plans.json → `data/history/plans-{date}.json`
2. 写入 changes.json 和 plans.json
3. 跑 `python3 -m collector.token_estimator` 补 measuredMonthlyToken
4. 更新 plans.json 所有变动条目的 updatedAt
5. 提示用户「说 /build-site build 生成 HTML」

### 自然语言 → kind 映射

| 用户说 | kind | 改 plans.json? |
|--------|------|---------------|
| "X 涨价/降价到 ¥Y" | price_change | 是（monthlyPrice） |
| "X 新增支持 M 模型" | new_model | 是（models） |
| "X 暂停订阅" | subscription_pause | 是（status=paused） |
| "X 新套餐上线" | new_plan | 是（新增条目） |
| "X 限时活动" | promotion | 否 |
| "看到一篇文章 [URL]" | article | 否 |
| "X 故障/下架" | outage | 是（status=deprecated） |

### 错误处理
- collector 跑失败 → 降级为纯人工（只用用户的自然语言输入）
- diff 输出后用户说"改 X 条" → 单独修改那条，重新输出 diff
- 用户说 n → 不动任何文件
```

- [ ] **Step 2: 补全 scan 模式**

替换 `## scan 模式（M2 实现后补全） TODO`：

```markdown
## scan 模式工作流

### 触发
`/build-site scan`

### 步骤
1. 并行跑 Layer 1 三路信号采集（同 update 的 Step 1）
2. 合并去重
3. 输出 markdown 报告到终端（不写任何 JSON 文件）：
   ```
   本周信号 (共 N 条):
   [价格] Kimi 涨价到 ¥99 — 来源: dailyhot:36kr [link]
   [模型] 字节方舟新增 Kimi-K3 — 来源: rsshub:deepseek/news [link]
   ...
   ```
4. 提示用户「值得跟进的，说 /build-site update ...」
```

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/build-site.md
git commit -m "docs(skill): 补全 update + scan 模式工作流"
```

---

### Task 16: M2 集成验证

**Files:** 无修改，纯验证

- [ ] **Step 1: 测试 scan 模式**

对 AI 说 `/build-site scan`，应该触发：
- 并行 dispatch 3 个 agent
- 输出信号报告（可能为空，如果 collector 没数据源）
- 不改动任何文件

- [ ] **Step 2: 测试 update 模式**

对 AI 说 `/build-site update DeepSeek 降价了，输入价格从 1 元降到 0.5 元`，应该触发：
- 草拟 changes.json + plans.json diff
- 输出预览等确认
- 用户 y → 写入 + 跑 token_estimator
- 不自动 build

- [ ] **Step 3: 测试 build 模式（回归）**

```bash
python3 tools/builder/build.py
open dist/codingplan-saver.html
```

验证 update 写入的数据能在 HTML 里看到。

- [ ] **Step 4: Commit（如有 M2 修复）**

```bash
git add -A
git commit -m "test(M2): update/scan/build 集成验证通过"
```

---

# Milestone 2 完成检查点

- [ ] `/build-site scan` 能并行跑 3 路信号（即使部分失败也能降级）
- [ ] `/build-site update "..."` 能输出 diff、等确认、写入 JSON、跑 token_estimator
- [ ] DeepSeek parser 能跑（至少不报错，提取字段数 ≥ 0）
- [ ] build 模式回归正常

✅ 验证通过后，进入 M3。

---

# Milestone 3 — 厂商覆盖扩展（Top 5）

**目标**：DeepSeek + 智谱 + 字节方舟 + Kimi + MiniMax 五家都有可用的 parser，`pricing-urls.md` 重构完成。

---

### Task 17: 重构 pricing-urls.md

**Files:**
- Modify: `reference/pricing-urls.md`

- [ ] **Step 1: 按 spec §6.2 重写文档结构**

每家厂商一个 section，包含：人看定价页 URL / 文档页（提取目标）/ API JSON / httpx 实测结果。

参考 spec §6.2 的模板，对 21 家厂商逐一生成 section（docs/api 先留空，实测后补）。

- [ ] **Step 2: Commit**

```bash
git add reference/pricing-urls.md
git commit -m "docs(reference): pricing-urls.md 重构为按厂商组织 + 实测反馈列"
```

---

### Task 18: 智谱 parser

**Files:**
- Create: `tools/collector/collector/sources/zhipu.py`
- Modify: `vendors.json` 和 `pricing-urls.md`

- [ ] **Step 1: 探测智谱的静态文档/API URL**

智谱的 `open.bigmodel.cn/pricing` 是 SPA，但可能有：
- API 端点（如 `open.bigmodel.cn/api/pricing`）
- 静态文档页（如 `open.bigmodel.cn/docs/...`）
- 开发者文档站的定价表

用 curl 探测，找到能 httpx 拿到的 URL。

- [ ] **Step 2: 根据 Step 1 结果写 parser**

参考 Task 14 的 DeepSeek parser 结构。如果找不到静态源，parser 退化为：
```python
@register("zhipu")
class ZhipuParser(BaseParser):
    async def extract(self, client) -> ExtractResult:
        return ExtractResult(
            vendor_id=self.vendor_id, vendor_name=self.vendor_name,
            error="未找到静态源，走 manual 策略",
            source_url=self.config.get("urls", {}).get("pricing", ""),
        )
```
并在 vendors.json 把 extractStrategy 改为 `"manual"`。

- [ ] **Step 3: 更新 vendors.json + pricing-urls.md**

记录实测结果到两个文件。

- [ ] **Step 4: 测试 + Commit**

```bash
cd tools/collector && source .venv/bin/activate
python3 -c "
import asyncio
from collector.sources.runner import run_all
for r in asyncio.run(run_all()):
    print(f'{r.vendor_name}: {len(r.plans)} plans, err={r.error}')
"
git add tools/collector/collector/sources/zhipu.py project/codingplan-saver/data/vendors.json reference/pricing-urls.md
git commit -m "feat(sources): 智谱 parser（或降级为 manual）"
```

---

### Task 19: 字节方舟 parser

**Files:**
- Create: `tools/collector/collector/sources/bytedance.py`
- Modify: 同 Task 18

按 Task 18 的流程做字节方舟（volcengine.com/docs/82379/1099320 这个文档页是优先探测目标）。

- [ ] **Step 1–4 同 Task 18，Commit message: `feat(sources): 字节方舟 parser`**

---

### Task 20: Kimi + MiniMax parser

**Files:**
- Create: `tools/collector/collector/sources/kimi.py`
- Create: `tools/collector/collector/sources/minimax.py`
- Modify: 同 Task 18

两家一起做（流程一样），各一个 commit。

- [ ] **Kimi Commit: `feat(sources): Kimi parser`**
- [ ] **MiniMax Commit: `feat(sources): MiniMax parser`**

---

### Task 21: 完善 token_estimator 适配新 schema

**Files:**
- Modify: `tools/collector/collector/token_estimator.py`

token_estimator 当前的 `PLANS_PATH` 指向旧路径 `project/codingplan-saver/plans.json`，需要改到新路径 `data/plans.json`。同时验证它能正确读新 schema。

- [ ] **Step 1: 更新路径常量**

修改 `token_estimator.py:25`:

```python
PLANS_PATH = PROJECT_ROOT / "project" / "codingplan-saver" / "data" / "plans.json"
```

- [ ] **Step 2: 验证新 schema 字段兼容性**

读 token_estimator 的 `estimate_coding_plan` 等函数，确认它们读的字段（`monthlyRequests` / `tokenLimit` / `measuredMonthlyToken`）在新 schema 里名字一致——根据 spec §3.5，这些字段名没变，应该兼容。

- [ ] **Step 3: 跑一遍**

```bash
cd tools/collector && source .venv/bin/activate
python3 -m collector.token_estimator
```

应该输出 "加载 N 个套餐 + 已更新 plans.json"。

- [ ] **Step 4: Commit**

```bash
git add tools/collector/collector/token_estimator.py project/codingplan-saver/data/plans.json
git commit -m "fix(token_estimator): 适配新 plans.json 路径（data/plans.json）"
```

---

# Milestone 3 完成检查点

- [ ] Top 5 厂商（DeepSeek/智谱/字节方舟/Kimi/MiniMax）各有 parser，至少不报错
- [ ] 找不到静态源的厂商在 vendors.json 标 `manual` 并在 pricing-urls.md 记录原因
- [ ] `pricing-urls.md` 按 §6.2 结构组织，每家有实测反馈列
- [ ] `python3 -m collector.token_estimator` 跑通新路径
- [ ] `python3 tools/builder/build.py` 最终回归正常

---

## Self-Review

**1. Spec coverage 检查**：
- §3 Schema → Task 3（SCHEMA.md）+ Task 4–7（数据迁移）
- §4 页面展示需求 → Task 8（HTML 模板实现）
- §5 HTML 结构 → Task 8 + Task 9
- §6 URL 维护 → Task 17 + Task 18–20
- §7 工作流 → Task 10（build）+ Task 15（update/scan）
- §8 文件结构 → Task 1（归档）+ Task 2（新目录）
- §9 collector 改造 → Task 11–14 + Task 18–21
- §10 SKILL.md → Task 10 + Task 15
- §11 决策记录 → 已固化为实现选择
- §12.2 已确认决策 → 全部体现在计划中

**2. Placeholder 检查**：
- Task 8 的 HTML 模板代码用了结构大纲而非完整代码——这是有意的（完整 ~600 行不适合塞进 plan），但 Step 1 明确了"必须落地的实现要点"，Step 2 有验证机制。
- Task 14 Step 2 的 DeepSeek parser 选择器标为"占位，必须根据 Step 1 curl 结果替换"——这是对的（实际选择器依赖实时页面结构），且 Step 1 的 curl 是必要前置。

**3. 类型一致性检查**：
- `ExtractResult` 在 Task 13 定义，Task 14/18/19/20 复用，字段名一致
- `register` 装饰器在 Task 13 定义，Task 14/18/19/20 使用，一致
- `vendors.json` 的 `extractStrategy` 枚举值在 Task 5（`manual`）和 Task 13 runner（`if manual: skip`）一致
- `changes.json` 的 `kind` 枚举在 Task 3 SCHEMA.md 定义，Task 15 自然语言映射表使用一致
