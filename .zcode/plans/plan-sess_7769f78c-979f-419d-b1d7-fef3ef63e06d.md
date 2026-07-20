# P2 实施方案：RSSHub 中文源 + discover 一条龙

## 战略调整（基于深度调研）

**RSSHub 是订阅器不是热榜聚合器**，但 5/6 平台都有真热榜路由。小红书在 2026 年全平台都没有真热榜（官方下架），按用户决定 P2 跳过。

P2 覆盖的中文平台：

| 平台 | RSSHub 路由 | 备注 |
|------|-----------|------|
| 知乎 | `/zhihu/daily`（推荐，无 cookie）+ `/zhihu/hot`（要 cookie） | 真热榜 |
| 微博 | `/weibo/search/hot/` | 真热搜 |
| B站 | `/bilibili/popular/all` | 热门 |
| 头条 | `/toutiao/hot` | 热文 |
| 公众号 | `/wechat/wechat2rss/:id` 等（按账号订阅） | 无热榜，订阅模式 |

## 实施步骤（共 7 步）

### 步骤 1：写 `sources/rsshub.py`（核心，~150 行）

复用 `v2ex.py` 的内存缓存模式 + `github_search.py` 的重试模式。

**JSON 响应是 JSON Feed 1.1 格式**（不是 `{items:[...]}`）：
```python
feed = {
  "version": "https://jsonfeed.org/version/1.1",
  "title": "知乎日报",
  "items": [
    {"url": "...", "title": "...", "content_html": "...", "date_published": "2026-07-20T..."}
  ]
}
```

模块签名：
```python
def fetch(limit=20, *, route="/zhihu/daily", base_url="") -> list[TrendItem]:
    """base_url 优先参数 > 环境变量 RSSHUB_BASE_URL > 默认 http://localhost:1200"""
```

预设常用路由别名（让 CLI 用 `--source zhihu` 比 `--route /zhihu/daily` 友好）：
```python
ROUTES = {
    "zhihu":      "/zhihu/daily",
    "zhihu-hot":  "/zhihu/hot",
    "weibo":      "/weibo/search/hot",
    "bilibili":   "/bilibili/popular/all",
    "toutiao":    "/toutiao/hot",
    "wechat":     "/wechat/ce/news",  # 默认订阅一个科技号聚合
}
```

### 步骤 2：扩 `models.py` 的 `TrendItem.source` Literal

```python
source: Literal["github", "hn", "v2ex", "rsshub"]  # 加 "rsshub"
```

注意 `OpportunityCard.source` 已经是 `str`，不用改。

### 步骤 3：扩 `config.py` 加 `SourcesConfig` dataclass

```python
@dataclass
class SourcesConfig:
    rsshub_base_url: str = "http://localhost:1200"

@dataclass
class Config:
    llm: LLMConfig = ...
    scoring: ScoringConfig = ...
    sources: SourcesConfig = field(default_factory=SourcesConfig)  # 新增
    opportunities_dir: Path = ...
```

`load_config()` 增加：
```python
sources_data = data.get("sources", {})
sources = SourcesConfig(
    rsshub_base_url=sources_data.get("rsshub_base_url", "http://localhost:1200"),
)
```

### 步骤 4：CLI 注册新源 + 加 `discover` 命令

修改 `cli.py`：

**4a. scan 命令扩展**：把 rsshub 别名映射进去
```python
SourceName = Literal["github", "github-trending", "hn", "v2ex",
                     "zhihu", "zhihu-hot", "weibo", "bilibili", "toutiao", "wechat"]

# _fetch_source 增加 rsshub 分支
if source in {"zhihu", "zhihu-hot", "weibo", "bilibili", "toutiao", "wechat"}:
    from .sources import rsshub
    cfg = load_config()
    return rsshub.fetch(limit=limit, route=rsshub.ROUTES[source],
                        base_url=cfg.sources.rsshub_base_url)
```

**4b. 新增 `discover` 命令**（交互式选择 → 批量分析）：
```python
@main.command()
@click.option("-s", "--source", ...)
@click.option("-l", "--limit", default=15, ...)
def discover(source, limit):
    """🚀 scan + analyze 一条龙：扫热榜 → 交互选条目 → 批量分析出卡。"""
    # 1. scan 出表格（复用 _fetch_source + _render_trend_table）
    # 2. rich.prompt 询问：选哪几条（逗号分隔 / a=全部 / q=退出）
    # 3. 逐条 analyze_trend → save_card，每条独立 try/except
    # 4. 末尾汇总：N 条分析 / M 条保存 / K 条值得孵化
```

关键设计：
- 每条 `analyze_trend` 包在 `try/except`，一条失败不影响其他
- 显示进度 `[1/3] 分析中...` + 完成后显示评分和判定
- 用 `console.status()` 做 spinner

### 步骤 5：写 docker-compose 和 .env.example

**新建 `tools/hot-trend/docker-compose.rsshub.yml`**：
```yaml
services:
  rsshub:
    image: diygod/rsshub:chromium-bundled  # P2 不用小红书，但留着为 P3
    container_name: rsshub
    restart: unless-stopped
    ports:
      - '127.0.0.1:1200:1200'  # 只本机访问，VPS 上配 Caddy
    environment:
      NODE_ENV: production
      CACHE_TYPE: redis
      REDIS_URL: 'redis://redis:6379/'
      CACHE_EXPIRE: '300'
      NO_LOGFILES: 'true'
    healthcheck:
      test: ['CMD', 'curl', '-f', 'http://localhost:1200/healthz']
      interval: 30s
      timeout: 10s
      retries: 3
    depends_on:
      redis:
        condition: service_healthy
  redis:
    image: redis:alpine
    restart: unless-stopped
    volumes:
      - redis-data:/data
    healthcheck:
      test: ['CMD', 'redis-cli', 'ping']
      interval: 30s
      retries: 5
volumes:
  redis-data:
```

**扩 `.env.example`** 加一行：
```
# RSSHub 实例地址（自建 Docker 后改成 VPS 域名）
RSSHUB_BASE_URL=http://localhost:1200
```

### 步骤 6：写 `tools/hot-trend/deploy/VPS.md` 部署文档

独立文档，5 个章节：
1. **本地快速验证**（Mac，`open -a Docker` + `docker compose -f docker-compose.rsshub.yml up -d`）
2. **VPS 部署完整流程**（买 VPS → 装 Docker → 拷 compose → 装 Caddy 反代 + TLS）
3. **平台特殊配置**（知乎可选 cookie、小红书需要 chromium-bundled + cookie 但 P2 不做）
4. **常用路由速查表**（5 个平台的 RSSHub 路由 + 是否需要 cookie）
5. **常见故障**（IP 被封、cookie 过期、healthz 失败）

含一个完整 Caddyfile 模板。

### 步骤 7：更新配置示例和 README

- `config.example.yaml` 加 `sources:` 段
- `tools/hot-trend/README.md` 加 P2 章节（新源列表 + discover 用法 + 链接到 deploy/VPS.md）
- 根 `README.md` 不动

## 验证标准（P2 完成的定义）

1. `docker compose -f docker-compose.rsshub.yml up -d` 启 RSSHub，`curl localhost:1200/healthz` 返回 ok
2. `hot-trend scan --source zhihu --limit 5` 输出知乎日报 5 条
3. `hot-trend scan --source weibo --limit 5` 输出微博热搜 5 条
4. `hot-trend scan --source bilibili --limit 5` 输出 B 站热门 5 条
5. `hot-trend discover --source zhihu --limit 10` 跑通交互流程：表格 → 选 1-2 条 → 生成机会卡
6. config.yaml 的 `sources.rsshub_base_url` 改了能生效（指向 http://localhost:1200 或 VPS）
7. `deploy/VPS.md` 文档完整，含 Caddy 配置

## 不在 P2 范围内

- ❌ 小红书（用户决定跳过，留 P3 + 自建 chromium-bundled + cookie 流程）
- ❌ MCP server 暴露（P3）
- ❌ `week` 周报（P3）
- ❌ 公众号订阅模式（虽然有路由，但需要用户自己维护账号 ID 列表，留 P3 做 watchlist 机制）
- ❌ 测试用例（P3）

## 工作量估算

| 步骤 | 预估 |
|------|------|
| 1-4（代码）| 1.5 小时 |
| 5-7（部署 + 文档）| 1 小时 |
| 端到端验证 | 30 分钟 |
| **总计** | **~3 小时** |

前提：你本地能跑起 Docker（要先 `open -a Docker`）。如果 Docker 跑不起来，验证步骤 1-4 跳过，文档先写好等你部署到 VPS 再验。