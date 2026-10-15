import { axiosClient } from './axiosClient'
import type { RiskFormData } from '@/forms/riskSchema'
import { Risk, DashboardStats, RiskTrendData, RiskSeverity, RiskStatus } from '@/types'

interface RiskListPayload {
  items: Record<string, unknown>[]
  total: number
  page: number
  page_size: number
  top_5: Record<string, unknown>[]
}

export interface RiskListResponse {
  risks: Risk[]
  total: number
  page: number
  pageSize: number
}

export interface RiskDetailResponse {
  risk: Risk
  linkedRisks: Risk[]
  auditTrail: Array<{
    id: string
    action: string
    changedAt: string
    user?: { id: string; email: string; full_name: string }
    previousValues: Record<string, unknown>
    newValues: Record<string, unknown>
  }>
  recommendations: string[]
}

function mapRisk(r: Record<string, unknown>): Risk {
  const band = (r.colour_band as { label?: string } | undefined)?.label?.toLowerCase() || 'medium'
  const severity =
    band === 'critical' || band === 'high' || band === 'medium' || band === 'low' ? band : ('medium' as RiskSeverity)

  const rawStatus = String(r.status ?? 'Open')
  const st = rawStatus.toLowerCase().replace(/\s+/g, '_')
  const statusMap: Record<string, RiskStatus> = {
    open: 'open',
    draft: 'draft',
    'pending approval': 'pending_approval',
    pending_approval: 'pending_approval',
    approved: 'approved',
    rejected: 'rejected',
    'in-progress': 'monitoring',
    in_progress: 'monitoring',
    mitigated: 'mitigated',
    closed: 'closed',
    escalated: 'monitoring',
  }

  return {
    id: String(r.id),
    title: String(r.title ?? ''),
    description: String(r.description ?? ''),
    category: String(r.category ?? ''),
    departmentId: String(r.department_id ?? ''),
    severity,
    probability: Number(r.likelihood ?? 3),
    impact: Number(r.impact ?? 3),
    velocity: Number(r.velocity ?? 3),
    detectability: Number(r.detectability ?? 3),
    riskScore: Number(r.normalised_score ?? r.risk_score ?? 0),
    status: statusMap[st] ?? 'open',
    apiStatus: rawStatus,
    riskType: (r.risk_type as Risk['riskType']) ?? undefined,
    parentRiskId: r.parent_risk_id ? String(r.parent_risk_id) : undefined,
    reviewerId: r.reviewer_id ? String(r.reviewer_id) : undefined,
    reviewJustification: r.review_justification ? String(r.review_justification) : undefined,
    reviewedAt: r.reviewed_at ? String(r.reviewed_at) : undefined,
    owner: String(r.owner_id ?? ''),
    createdAt: String(r.created_at ?? ''),
    updatedAt: String(r.updated_at ?? ''),
  }
}

function mapLinkedRisk(l: Record<string, unknown>): Risk {
  const band = (l.colour_band as { label?: string } | undefined)?.label?.toLowerCase() || 'medium'
  const severity =
    band === 'critical' || band === 'high' || band === 'medium' || band === 'low' ? band : ('medium' as RiskSeverity)
  return {
    id: String(l.linked_risk_id ?? l.id ?? ''),
    title: String(l.title ?? ''),
    description: '',
    category: '',
    departmentId: String(l.department_id ?? ''),
    severity,
    probability: 3,
    impact: 3,
    riskScore: Number(l.normalised_score ?? 0),
    status: 'open',
    owner: '',
    createdAt: '',
    updatedAt: '',
  }
}

export function buildRiskCreateBody(data: RiskFormData): Record<string, unknown> {
  return {
    title: data.title,
    description: data.description,
    category: data.category,
    department_id: data.departmentId,
    owner_id: data.ownerId,
    likelihood: data.likelihood,
    impact: data.impact,
    velocity: data.velocity,
    detectability: data.detectability,
  }
}

export function buildRiskUpdateBody(data: RiskFormData): Record<string, unknown> {
  return {
    title: data.title,
    description: data.description,
    category: data.category,
    department_id: data.departmentId,
    owner_id: data.ownerId,
    status: data.status,
    likelihood: data.likelihood,
    impact: data.impact,
    velocity: data.velocity,
    detectability: data.detectability,
  }
}

export const riskApi = {
  getRisks: async (filters?: Record<string, unknown>): Promise<Risk[]> => {
    const response = await axiosClient.get<RiskListPayload | Risk[]>('/risks', { params: filters })
    const data = response.data
    if (Array.isArray(data)) return data as Risk[]
    return (data.items ?? []).map((r) => mapRisk(r))
  },

  getRisksPaginated: async (filters?: Record<string, unknown>): Promise<RiskListResponse> => {
    const response = await axiosClient.get<RiskListPayload | Risk[]>('/risks', { params: filters })
    const data = response.data
    if (Array.isArray(data)) return { risks: data as Risk[], total: data.length, page: 1, pageSize: data.length }
    return {
      risks: (data.items ?? []).map((r) => mapRisk(r)),
      total: data.total ?? 0,
      page: data.page ?? 1,
      pageSize: data.page_size ?? 20,
    }
  },

  getRiskById: async (id: string): Promise<Risk> => {
    const response = await axiosClient.get<Record<string, unknown>>(`/risks/${id}`)
    return mapRisk(response.data)
  },

  getRiskDetail: async (id: string): Promise<RiskDetailResponse> => {
    const response = await axiosClient.get<Record<string, unknown>>(`/risks/${id}`)
    const d = response.data
    const risk = mapRisk(d)
    const linked = (d.linked_risks as Record<string, unknown>[]) || []
    const rawAudit = (d.audit_trail as Record<string, unknown>[]) || []
    const recommendations = (d.recommendations as string[]) || []
    return {
      risk,
      linkedRisks: linked.map((l) => mapLinkedRisk(l)),
      auditTrail: rawAudit.map((a) => ({
        id: String(a.id ?? ''),
        action: String(a.action ?? ''),
        changedAt: String(a.changed_at ?? ''),
        user: a.user as { id: string; email: string; full_name: string } | undefined,
        previousValues: (a.previous_values as Record<string, unknown>) || {},
        newValues: (a.new_values as Record<string, unknown>) || {},
      })),
      recommendations,
    }
  },

  createRisk: async (data: RiskFormData): Promise<Risk> => {
    const response = await axiosClient.post<Record<string, unknown>>('/risks', buildRiskCreateBody(data))
    return mapRisk(response.data)
  },

  updateRisk: async (id: string, data: RiskFormData): Promise<Risk> => {
    const response = await axiosClient.patch<Record<string, unknown>>(`/risks/${id}`, buildRiskUpdateBody(data))
    return mapRisk(response.data)
  },

  deleteRisk: async (id: string): Promise<void> => {
    await axiosClient.delete(`/risks/${id}`)
  },

  getRisksByDepartment: async (departmentId: string): Promise<Risk[]> => {
    const response = await axiosClient.get<RiskListPayload>(`/departments/${departmentId}/risks`)
    return (response.data.items ?? []).map((r) => mapRisk(r))
  },

  getRiskDependencies: async (riskId: string): Promise<Risk[]> => {
    const response = await axiosClient.get<Record<string, unknown>>(`/risks/${riskId}`)
    const linked = (response.data.linked_risks as Record<string, unknown>[]) || []
    return linked.map((l) => mapLinkedRisk(l))
  },

  getDashboardStats: async (): Promise<DashboardStats> => {
    const { data } = await axiosClient.get<{
      departments: unknown[]
      distribution: Record<string, number>
    }>('/analytics/institutional-summary')
    const dist = data.distribution || {}
    const total = Object.values(dist).reduce((a, b) => a + b, 0)
    return {
      totalRisks: total,
      criticalCount: dist.Critical ?? 0,
      highCount: dist.High ?? 0,
      mediumCount: dist.Medium ?? 0,
      lowCount: dist.Low ?? 0,
      averageRiskScore: 0,
      openMitigations: 0,
    }
  },

  getRiskTrends: async (days: number = 30, departmentId?: string): Promise<RiskTrendData[]> => {
    const params: Record<string, unknown> = { days }
    if (departmentId) params.dept_id = departmentId
    const { data } = await axiosClient.get<Array<{ day: string; avg_score: number; risk_count: number }>>(
      '/analytics/trend',
      { params }
    )
    return (data || []).map((p) => ({
      date: String(p.day),
      count: p.risk_count,
      severity: p.avg_score >= 65 ? 'critical' : p.avg_score >= 40 ? 'high' : p.avg_score >= 20 ? 'medium' : 'low',
    }))
  },

  approveRisk: async (id: string, justification: string): Promise<Risk> => {
    const response = await axiosClient.post<Record<string, unknown>>(`/risks/${id}/approve`, { justification })
    return mapRisk(response.data)
  },

  rejectRisk: async (id: string, justification: string): Promise<Risk> => {
    const response = await axiosClient.post<Record<string, unknown>>(`/risks/${id}/reject`, { justification })
    return mapRisk(response.data)
  },

  getPendingRisks: async (): Promise<Risk[]> => {
    const response = await axiosClient.get<RiskListPayload | Risk[]>('/risks', {
      params: { status: 'Pending Approval' },
    })
    const data = response.data
    if (Array.isArray(data)) return data as Risk[]
    return (data.items ?? []).map((r) => mapRisk(r))
  },
}
