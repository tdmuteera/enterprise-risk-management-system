import { axiosClient } from './axiosClient'
import { Alert, RiskSeverity } from '@/types'

interface AlertItemRaw {
  id: string
  alert_type: string
  risk_id?: string | null
  message: string
  severity: string
  is_read: boolean
  is_dismissed: boolean
  created_for_role: string
  created_at: string
}

function mapSeverity(sev: string): RiskSeverity {
  const s = sev.toLowerCase()
  if (s === 'critical') return 'critical'
  if (s === 'warning') return 'high'
  return 'medium'
}

function mapAlert(a: AlertItemRaw): Alert {
  return {
    id: String(a.id),
    riskId: a.risk_id ? String(a.risk_id) : '',
    title: a.alert_type,
    message: a.message,
    severity: mapSeverity(a.severity),
    read: a.is_read,
    createdAt: a.created_at,
  }
}

export const alertApi = {
  getAlerts: async (unreadOnly: boolean = false): Promise<Alert[]> => {
    const response = await axiosClient.get<{ items: AlertItemRaw[]; total: number }>('/alerts', {
      params: { unreadOnly },
    })
    const items = response.data.items ?? []
    return items.map(mapAlert)
  },

  markAlertAsRead: async (id: string): Promise<Alert> => {
    const response = await axiosClient.patch<AlertItemRaw>(`/alerts/${id}/read`)
    return mapAlert(response.data)
  },

  markAllAsRead: async (): Promise<void> => {
    await axiosClient.patch('/alerts/read-all')
  },

  deleteAlert: async (id: string): Promise<void> => {
    await axiosClient.delete(`/alerts/${id}`)
  },

  getUnreadCount: async (): Promise<number> => {
    const response = await axiosClient.get<{ unread: number }>('/alerts/unread-count')
    return response.data.unread
  },

  triggerForensicScan: async (): Promise<number> => {
    const response = await axiosClient.post<{ created: number }>('/alerts/forensic-scan')
    return response.data.created
  },
}
