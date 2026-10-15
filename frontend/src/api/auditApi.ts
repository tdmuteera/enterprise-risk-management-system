import { axiosClient } from './axiosClient'

export interface AuditLogEntry {
  id: string
  risk_id: string
  action: string
  changed_at: string
  ip_address?: string
  user_agent?: string
  previous_values: Record<string, unknown>
  new_values: Record<string, unknown>
  user?: {
    id: string
    email: string
    full_name: string
    role?: string
    department_id?: string
  }
  risk_title?: string
}

export interface AuditLogResponse {
  items: AuditLogEntry[]
  total: number
  page: number
  page_size: number
}

interface RawAuditLogEntry {
  id: string
  risk_id?: string
  entity_id?: string
  action: string
  changed_at: string
  ip_address?: string
  user_agent?: string
  previous_values: Record<string, unknown>
  new_values: Record<string, unknown>
  changed_by_id?: string
  changed_by_name?: string
  changed_by_email?: string
  risk_title?: string
}

function mapAuditEntry(raw: RawAuditLogEntry): AuditLogEntry {
  return {
    id: raw.id,
    risk_id: raw.risk_id || raw.entity_id || '',
    action: raw.action,
    changed_at: raw.changed_at,
    ip_address: raw.ip_address,
    user_agent: raw.user_agent,
    previous_values: raw.previous_values || {},
    new_values: raw.new_values || {},
    user: raw.changed_by_id
      ? {
          id: raw.changed_by_id,
          email: raw.changed_by_email || '',
          full_name: raw.changed_by_name || '',
        }
      : undefined,
    risk_title: raw.risk_title,
  }
}

export const auditApi = {
  getAuditLogs: async (params?: {
    user_filter?: string
    action_filter?: string
    start_date?: string
    end_date?: string
    page?: number
    page_size?: number
  }): Promise<AuditLogResponse> => {
    const { data } = await axiosClient.get<{ items: RawAuditLogEntry[]; total: number; page: number; page_size: number }>('/audit-logs', { params })
    return {
      items: (data.items || []).map(mapAuditEntry),
      total: data.total,
      page: data.page,
      page_size: data.page_size,
    }
  },
}
