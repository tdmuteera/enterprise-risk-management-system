import { axiosClient } from './axiosClient'
import { HeatmapCell, RiskTrendData, RiskSeverity } from '@/types'
import { alertApi } from './alertApi'
import { riskApi } from './riskApi'

export interface DepartmentAnalytics {
  totalRisks: number
  criticalCount: number
  highCount: number
  mediumCount: number
  lowCount: number
  criticalChange: number
  highChange: number
  overdueCount: number
  overdueChange: number
  averageRiskScore: number
  riskDistribution: Array<{ severity: string; count: number }>
}

export interface RiskWithMitigation {
  id: string
  title: string
  category: string
  riskScore: number
  severity: string
  owner: string
  status: string
  mitigationStatus?: string
}

export interface MitigationWithRisk {
  id: string
  riskId: string
  riskTitle: string
  description: string
  owner: string
  dueDate: string
  status: string
  daysOverdue?: number
}

export interface CrossDepartmentAnalytics {
  institutionIRIScore: number
  activeRiskChains: number
  linkedRiskPairs: number
  forensicAlerts: number
  departmentScores: Array<{
    departmentId: string
    name: string
    iriScore: number
    riskCount: number
  }>
}

export interface ExecutiveMetrics {
  criticalRisks: number
  highRisks: number
  mediumRisks: number
  lowRisks: number
  topBoardRisks: Array<{
    id: string
    departmentName: string
    title: string
    score: number
    iri: number
    mitigationStatus: string
    daysOpen: number
    hasAlert: boolean
  }>
}

interface DeptSummary {
  total_risks: number
  critical: number
  high: number
  medium: number
  low: number
  top5_risks: Array<Record<string, unknown>>
  iri?: number | null
  trend: Array<{ day: string; created: number; updated: number; closed: number }>
}

interface GraphPayload {
  nodes: Array<{ id: string; title: string; department_id: string; normalised_score: number }>
  edges: Array<{ source: string; target: string; weight: number; link_type: string }>
}

function componentStats(nodes: GraphPayload['nodes'], edges: GraphPayload['edges']) {
  const ids = nodes.map((n) => n.id)
  const adj = new Map<string, Set<string>>()
  for (const id of ids) adj.set(id, new Set())
  for (const e of edges) {
    adj.get(e.source)?.add(e.target)
    adj.get(e.target)?.add(e.source)
  }
  const seen = new Set<string>()
  const sizes: number[] = []
  for (const id of ids) {
    if (seen.has(id)) continue
    let sz = 0
    const stack = [id]
    while (stack.length) {
      const n = stack.pop()!
      if (seen.has(n)) continue
      seen.add(n)
      sz++
      for (const x of adj.get(n) || []) {
        if (!seen.has(x)) stack.push(x)
      }
    }
    sizes.push(sz)
  }
  const multi = sizes.filter((s) => s >= 2).length
  return { componentCountMulti: multi, edgeCount: edges.length }
}

export const dashboardApi = {
  getDepartmentAnalytics: async (departmentId: string): Promise<DepartmentAnalytics> => {
    const { data } = await axiosClient.get<DeptSummary>(`/departments/${departmentId}/summary`)
    return {
      totalRisks: data.total_risks,
      criticalCount: data.critical,
      highCount: data.high,
      mediumCount: data.medium,
      lowCount: data.low,
      criticalChange: 0,
      highChange: 0,
      overdueCount: 0,
      overdueChange: 0,
      averageRiskScore: 0,
      riskDistribution: [
        { severity: 'critical', count: data.critical },
        { severity: 'high', count: data.high },
        { severity: 'medium', count: data.medium },
        { severity: 'low', count: data.low },
      ],
    }
  },

  getDepartmentTopRisks: async (departmentId: string, limit: number = 5): Promise<RiskWithMitigation[]> => {
    const { data } = await axiosClient.get<DeptSummary>(`/departments/${departmentId}/summary`)
    const rows = (data.top5_risks ?? []).slice(0, limit)
    return rows.map((r) => {
      const band = (r.colour_band as { label?: string } | undefined)?.label ?? 'Medium'
      return {
        id: String(r.id),
        title: String(r.title ?? ''),
        category: String(r.category ?? ''),
        riskScore: Number(r.normalised_score ?? 0),
        severity: String(band).toLowerCase(),
        owner: String(r.owner_id ?? ''),
        status: String(r.status ?? ''),
      }
    })
  },

  getDepartmentHeatmap: async (departmentId: string): Promise<HeatmapCell[][]> => {
    const { data } = await axiosClient.get<{ dept_id: string | null; cells: Array<{ likelihood: number; impact: number; count: number }> }>(
      '/analytics/heatmap',
      { params: { dept_id: departmentId } }
    )
    const cells: HeatmapCell[] = (data.cells ?? []).map((c) => ({
      probability: c.likelihood,
      impact: c.impact,
      count: c.count,
      risks: [],
    }))
    return [cells]
  },

  getDepartmentMitigations: async (departmentId: string): Promise<MitigationWithRisk[]> => {
    const risks = await riskApi.getRisksByDepartment(departmentId)
    const limited = risks.slice(0, 25)
    const nested = await Promise.all(
      limited.map(async (r) => {
        try {
          const { data } = await axiosClient.get<
            Array<{
              id: string
              description: string
              assigned_to_id: string
              due_date: string
              status: string
            }>
          >(`/risks/${r.id}/mitigations`)
          return (data || []).map((m) => ({
            id: String(m.id),
            riskId: r.id,
            riskTitle: r.title,
            description: m.description,
            owner: String(m.assigned_to_id),
            dueDate: String(m.due_date),
            status: String(m.status),
          }))
        } catch {
          return []
        }
      })
    )
    return nested.flat()
  },

  getCrossDepartmentAnalytics: async (): Promise<CrossDepartmentAnalytics> => {
    const { data: summary } = await axiosClient.get<{
      departments: Array<{ department_id: string; department_name: string; iri: number; total_risks: number }>
      distribution: Record<string, number>
    }>('/analytics/institutional-summary')

    const { data: graph } = await axiosClient.get<GraphPayload>('/analytics/risk-chain-graph')
    const { componentCountMulti, edgeCount } = componentStats(graph.nodes ?? [], graph.edges ?? [])

    const alerts = await alertApi.getAlerts(false)
    const forensicAlerts = alerts.filter(
      (a) => a.title.includes('Forensic') || a.message.includes('FORENSIC') || a.title.includes('RiskSuppression')
    ).length

    const deps = summary.departments ?? []
    const institutionIRIScore = deps.length ? Math.max(...deps.map((d) => d.iri || 0)) : 0

    return {
      institutionIRIScore,
      activeRiskChains: componentCountMulti,
      linkedRiskPairs: edgeCount,
      forensicAlerts,
      departmentScores: deps.map((d) => ({
        departmentId: String(d.department_id),
        name: d.department_name,
        iriScore: d.iri,
        riskCount: d.total_risks,
      })),
    }
  },

  getRiskChains: async (): Promise<
    Array<{ title: string; description: string; departments: string[]; combinedIRI: number; age: number }>
  > => {
    const { data: graph } = await axiosClient.get<GraphPayload>('/analytics/risk-chain-graph')
    const nodes = graph.nodes ?? []
    const edges = graph.edges ?? []
    const adj = new Map<string, Set<string>>()
    for (const n of nodes) adj.set(n.id, new Set())
    for (const e of edges) {
      adj.get(e.source)?.add(e.target)
      adj.get(e.target)?.add(e.source)
    }
    const seen = new Set<string>()
    const clusters: string[][] = []
    for (const n of nodes) {
      if (seen.has(n.id)) continue
      const cluster: string[] = []
      const stack = [n.id]
      while (stack.length) {
        const id = stack.pop()!
        if (seen.has(id)) continue
        seen.add(id)
        cluster.push(id)
        for (const x of adj.get(id) || []) {
          if (!seen.has(x)) stack.push(x)
        }
      }
      if (cluster.length >= 2) clusters.push(cluster)
    }
    return clusters.map((ids, idx) => {
      const titles = ids
        .map((id) => nodes.find((n) => n.id === id)?.title)
        .filter(Boolean) as string[]
      const scores = ids.map((id) => nodes.find((n) => n.id === id)?.normalised_score ?? 0)
      const combinedIRI = scores.length ? scores.reduce((a, b) => a + b, 0) / scores.length : 0
      return {
        title: `Institutional chain ${idx + 1}`,
        description: titles.slice(0, 3).join(' · ') || 'Linked risk cluster',
        departments: [...new Set(ids.map((id) => nodes.find((n) => n.id === id)?.department_id).filter(Boolean) as string[])],
        combinedIRI,
        age: 0,
      }
    })
  },

  getExecutiveMetrics: async (): Promise<ExecutiveMetrics> => {
    const { data: summary } = await axiosClient.get<{ distribution: Record<string, number> }>('/analytics/institutional-summary')
    const dist = summary.distribution || {}
    const risks = await riskApi.getRisks({ page: 1, page_size: 5, sort_by: 'score', order: 'desc' })
    return {
      criticalRisks: dist.Critical ?? 0,
      highRisks: dist.High ?? 0,
      mediumRisks: dist.Medium ?? 0,
      lowRisks: dist.Low ?? 0,
      topBoardRisks: risks.slice(0, 5).map((r) => ({
        id: r.id,
        departmentName: '',
        title: r.title,
        score: r.riskScore,
        iri: r.riskScore,
        mitigationStatus: 'unknown',
        daysOpen: 0,
        hasAlert: false,
      })),
    }
  },

  getInstitutionIRITrend: async (days: number = 30): Promise<RiskTrendData[]> => {
    const { data } = await axiosClient.get<Array<{ day: string; avg_score: number; risk_count: number }>>('/analytics/trend', {
      params: { days },
    })
    return (data || []).map((p) => ({
      date: String(p.day),
      count: Math.round(p.avg_score),
      severity: (p.avg_score >= 65 ? 'critical' : p.avg_score >= 40 ? 'high' : p.avg_score >= 20 ? 'medium' : 'low') as RiskSeverity,
    }))
  },

  getForensicAlerts: async (): Promise<
    Array<{ title: string; description: string; severity: string; riskTitle: string; departmentName: string }>
  > => {
    const items = await alertApi.getAlerts(false)
    return items
      .filter((a) => a.message.includes('FORENSIC') || a.title.includes('Forensic') || a.title.includes('RiskSuppression'))
      .map((a) => ({
        title: a.title,
        description: a.message,
        severity: a.severity,
        riskTitle: a.riskId ? `Risk ${a.riskId.slice(0, 8)}…` : '—',
        departmentName: '—',
      }))
  },
}
