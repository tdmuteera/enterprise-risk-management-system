import { axiosClient } from './axiosClient'
import { LoginRequest, RegisterRequest, AuthResponse, User } from '@/types'

function mapAuthUser(
  apiUser: {
    id: string
    name: string
    role: string
    dept?: string | null
    department_id?: string | null
  },
  email: string
): User {
  return {
    id: apiUser.id,
    email,
    name: apiUser.name,
    role: apiUser.role as User['role'],
    departmentId: apiUser.department_id ?? undefined,
  }
}

export const authApi = {
  login: async (data: LoginRequest): Promise<AuthResponse> => {
    const response = await axiosClient.post<{
      access_token: string
      refresh_token?: string
      token_type: string
      user: {
        id: string
        name: string
        role: string
        dept?: string | null
        department_id?: string | null
      }
    }>('/auth/login', data)

    const d = response.data
    return {
      token: d.access_token,
      user: mapAuthUser(d.user, data.email),
    }
  },

  register: async (data: RegisterRequest): Promise<AuthResponse> => {
    const response = await axiosClient.post<{
      access_token: string
      refresh_token?: string
      token_type: string
      user: {
        id: string
        name: string
        role: string
        dept?: string | null
        department_id?: string | null
      }
    }>('/auth/register', data)

    const d = response.data
    return {
      token: d.access_token,
      user: mapAuthUser(d.user, data.email),
    }
  },

  logout: async (): Promise<void> => {
    await axiosClient.post('/auth/logout')
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await axiosClient.get<{
      id: string
      email: string
      name: string
      role: string
      department_id?: string | null
    }>('/auth/me')
    const d = response.data
    return {
      id: d.id,
      email: d.email,
      name: d.name,
      role: d.role as User['role'],
      departmentId: d.department_id ?? undefined,
    }
  },

  refreshToken: async (refreshToken: string): Promise<AuthResponse> => {
    const response = await axiosClient.post<{ access_token: string; token_type: string }>('/auth/refresh', {
      refresh_token: refreshToken,
    })
    const me = await authApi.getCurrentUser()
    return { token: response.data.access_token, user: me }
  },

  updateMe: async (payload: { full_name?: string; password?: string }): Promise<User> => {
    const { data } = await axiosClient.put<{
      id: string
      email: string
      name: string
      role: string
      department_id?: string | null
    }>('/auth/me', payload)
    return {
      id: data.id,
      email: data.email,
      name: data.name,
      role: data.role as User['role'],
      departmentId: data.department_id ?? undefined,
    }
  },
}
