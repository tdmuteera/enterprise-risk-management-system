import { axiosClient } from './axiosClient'
import { Mitigation, MitigationCreateRequest } from '@/types'

interface MitigationRow {
  id: string
  risk_id: string
  description: string
  assigned_to_id: string
  due_date: string
  completion_date?: string | null
  status: string
  effectiveness_score?: number | null
  created_at: string
  updated_at: string
}

function mapMitigation(m: MitigationRow, riskTitle = ''): Mitigation {
  return {
    id: String(m.id),
    riskId: String(m.risk_id),
    title: m.description.slice(0, 80),
    description: m.description,
    owner: String(m.assigned_to_id),
    dueDate: String(m.due_date),
    status: mapMitigationStatus(m.status),
    effectiveness: m.effectiveness_score != null ? m.effectiveness_score * 20 : 0,
    createdAt: String(m.created_at),
  }
}

function mapMitigationStatus(s: string): Mitigation['status'] {
  const u = s.toLowerCase()
  if (u === 'completed') return 'completed'
  if (u === 'in-progress' || u === 'in_progress') return 'in_progress'
  return 'not_started'
}

export const mitigationApi = {
  /** List mitigations for one risk (required). */
  getMitigationsForRisk: async (riskId: string): Promise<Mitigation[]> => {
    const response = await axiosClient.get<MitigationRow[]>(`/risks/${riskId}/mitigations`)
    return (response.data || []).map((m) => mapMitigation(m))
  },

  getMitigationById: async (_id: string): Promise<Mitigation> => {
    throw new Error('Load mitigations via getMitigationsForRisk(riskId).')
  },

  createMitigation: async (data: MitigationCreateRequest): Promise<Mitigation> => {
    const description = [data.title, data.description].filter(Boolean).join(' — ') || data.description
    const response = await axiosClient.post<MitigationRow>(`/risks/${data.riskId}/mitigations`, {
      description,
      due_date: data.dueDate,
      assigned_to_id: data.owner,
    })
    return mapMitigation(response.data)
  },

  updateMitigation: async (id: string, data: Partial<Mitigation>): Promise<Mitigation> => {
    const payload: Record<string, unknown> = {}
    if (data.description != null) payload.description = data.description
    if (data.dueDate != null) payload.due_date = data.dueDate
    if (data.status != null) {
      const st = data.status
      payload.status =
        st === 'completed' ? 'Completed' : st === 'in_progress' ? 'In-Progress' : 'Pending'
    }
    if (data.owner != null) payload.assigned_to_id = data.owner
    const response = await axiosClient.patch<MitigationRow>(`/mitigations/${id}`, payload)
    return mapMitigation(response.data)
  },

  deleteMitigation: async (_id: string): Promise<void> => {
    throw new Error('Deleting mitigations is not exposed by the API.')
  },

  getRiskMitigations: async (riskId: string): Promise<Mitigation[]> => {
    return mitigationApi.getMitigationsForRisk(riskId)
  },

  getOverdueMitigations: async (): Promise<Mitigation[]> => {
    const response = await axiosClient.get<MitigationRow[]>('/mitigations/overdue')
    return (response.data || []).map((m) => mapMitigation(m))
  },
}
