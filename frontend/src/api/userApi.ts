import { axiosClient } from './axiosClient'

export interface AdminUserRow {
  id: string
  email: string
  full_name: string
  role: string
  department_id: string | null
  is_active: boolean
  last_login: string | null
  created_at: string
  updated_at: string
}

export const userApi = {
  listUsers: async (): Promise<AdminUserRow[]> => {
    const { data } = await axiosClient.get<AdminUserRow[]>('/users')
    return (data || []).map((u) => ({
      ...u,
      id: String(u.id),
      department_id: u.department_id ? String(u.department_id) : null,
    }))
  },
}
