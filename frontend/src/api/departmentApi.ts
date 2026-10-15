import { axiosClient } from './axiosClient'
import { Department } from '@/types'

interface DepartmentApiRow {
  id: string
  name: string
  code: string
  description?: string | null
  head_of_dept?: string | null
  is_active: boolean
  created_at: string
  updated_at: string
  open_risks_count?: number
  iri?: number | null
}

function mapDepartment(d: DepartmentApiRow): Department {
  return {
    id: String(d.id),
    name: String(d.name),
    code: String(d.code),
    head: d.head_of_dept ?? '',
    riskScore: typeof d.iri === 'number' ? d.iri : 0,
    riskLevel: 'low',
    createdAt: String(d.created_at),
  }
}

export const departmentApi = {
  getDepartments: async (): Promise<Department[]> => {
    const response = await axiosClient.get<DepartmentApiRow[]>('/departments')
    return (response.data || []).map(mapDepartment)
  },

  getDepartmentById: async (id: string): Promise<Department> => {
    const response = await axiosClient.get<DepartmentApiRow>(`/departments/${id}`)
    return mapDepartment(response.data)
  },

  createDepartment: async (data: Omit<Department, 'id' | 'createdAt'> & { description?: string }): Promise<Department> => {
    const response = await axiosClient.post<DepartmentApiRow>('/departments', {
      name: data.name,
      code: data.code,
      description: data.description ?? null,
      head_of_dept: data.head || null,
    })
    return mapDepartment(response.data)
  },

  updateDepartment: async (
    id: string,
    data: Partial<Department> & { description?: string; is_active?: boolean }
  ): Promise<Department> => {
    const response = await axiosClient.put<DepartmentApiRow>(`/departments/${id}`, {
      name: data.name,
      code: data.code,
      description: data.description,
      head_of_dept: data.head,
      is_active: data.is_active,
    })
    return mapDepartment(response.data)
  },

  deleteDepartment: async (_id: string): Promise<void> => {
    throw new Error('Deleting departments is not supported by the API.')
  },
}
