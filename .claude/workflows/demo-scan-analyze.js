export const meta = {
  name: 'demo-scan-analyze',
  description: 'Demo workflow: scan hot trends → analyze top signals → summary report',
  phases: [
    { title: 'Scan', detail: '读取热点数据并聚类筛选' },
    { title: 'Analyze', detail: '对 top 信号做深度分析' },
    { title: 'Report', detail: '汇总输出报告' },
  ],
}

// ── Phase 1: Scan ──────────────────────────────────
phase('Scan')

const scanResult = await agent(
  `你是热点分析专家。请读取 data/raw/2026-07-20/ 目录下的所有 JSON 文件，
   分析其中的热点话题，按以下维度聚类：
   1. 技术趋势（AI、开发工具、框架等）
   2. 商业机会（可变现的方向）
   3. 社区热点（高讨论度话题）

   对每个聚类输出：
   - 聚类名称
   - 包含的话题数
   - 代表性话题（3-5个）
   - 热度评分（1-5）
   - 商业化潜力评分（1-5）`,
  {
    label: '热点扫描',
    phase: 'Scan',
    schema: {
      type: 'object',
      properties: {
        clusters: {
          type: 'array',
          items: {
            type: 'object',
            properties: {
              name: { type: 'string' },
              topicCount: { type: 'integer' },
              representativeTopics: { type: 'array', items: { type: 'string' } },
              heatScore: { type: 'integer', minimum: 1, maximum: 5 },
              commercialScore: { type: 'integer', minimum: 1, maximum: 5 },
            },
            required: ['name', 'topicCount', 'representativeTopics', 'heatScore', 'commercialScore'],
          },
        },
      },
      required: ['clusters'],
    },
  },
)

log(`扫描完成，发现 ${scanResult.clusters.length} 个热点聚类`)

// ── Phase 2: Analyze ───────────────────────────────
phase('Analyze')

// 取 commercialScore 最高的 2 个聚类做深度分析
const topClusters = scanResult.clusters
  .sort((a, b) => b.commercialScore - a.commercialScore)
  .slice(0, 2)

const analyses = await parallel(
  topClusters.map((cluster) => () =>
    agent(
      `针对以下热点聚类做深度利基分析：

      聚类名称：${cluster.name}
      热度评分：${cluster.heatScore}/5
      商业化潜力：${cluster.commercialScore}/5
      代表性话题：${cluster.representativeTopics.join(', ')}

      请按以下维度分析：
      1. 需求真实性 — 有真实用户在找解决方案吗？
      2. 增长潜力 — 赛道在增长吗？
      3. 付费意愿 — 用户愿意付费吗？
      4. 竞争空间 — 有差异化空间吗？
      5. 执行可行性 — AI 能帮我做多少？
      6. 规模化潜力 — 能做成睡后收入吗？

      最终给出 Go/No-Go 建议。`,
      {
        label: `分析: ${cluster.name}`,
        phase: 'Analyze',
        schema: {
          type: 'object',
          properties: {
            clusterName: { type: 'string' },
            scores: {
              type: 'object',
              properties: {
                demandReality: { type: 'integer', minimum: 1, maximum: 5 },
                growthPotential: { type: 'integer', minimum: 1, maximum: 5 },
                willingnessToPay: { type: 'integer', minimum: 1, maximum: 5 },
                competitionSpace: { type: 'integer', minimum: 1, maximum: 5 },
                feasibility: { type: 'integer', minimum: 1, maximum: 5 },
                scalability: { type: 'integer', minimum: 1, maximum: 5 },
              },
              required: ['demandReality', 'growthPotential', 'willingnessToPay', 'competitionSpace', 'feasibility', 'scalability'],
            },
            goNoGo: { type: 'string', enum: ['Go', 'No-Go', 'Conditional'] },
            reason: { type: 'string' },
            suggestedMvp: { type: 'string' },
          },
          required: ['clusterName', 'scores', 'goNoGo', 'reason', 'suggestedMvp'],
        },
      },
    ),
  ),
)

// ── Phase 3: Report ────────────────────────────────
phase('Report')

const report = analyses.filter(Boolean).map((a) => ({
  name: a.clusterName,
  totalScore: Object.values(a.scores).reduce((s, v) => s + v, 0),
  goNoGo: a.goNoGo,
  reason: a.reason,
  mvp: a.suggestedMvp,
}))

log(`\n📊 Demo 分析报告`)
report.forEach((r) => {
  log(`\n【${r.name}】`)
  log(`  总分: ${r.totalScore}/30 | 建议: ${r.goNoGo}`)
  log(`  理由: ${r.reason}`)
  log(`  MVP 建议: ${r.mvp}`)
})

return { clusters: scanResult.clusters, analyses: report }