import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from 'axios'
import { showAppToast } from '@/lib/toastBridge'

/** API origin (no trailing /api). Token is read from localStorage; AuthContext keeps it in sync on login/logout. */
const useRelativeApi = import.meta.env.VITE_USE_RELATIVE_API === 'true'
const rawBase = useRelativeApi
  ? ''
  : import.meta.env.VITE_API_BASE_URL ||
    import.meta.env.VITE_API_URL?.replace(/\/api\/?$/, '') ||
    'http://localhost:8000'

const API_ROOT = `${String(rawBase).replace(/\/$/, '')}/api/v1`

function getStoredToken(): string | null {
  return localStorage.getItem('authToken')
}

export const axiosClient: AxiosInstance = axios.create({
  baseURL: API_ROOT,
  headers: {
    'Content-Type': 'application/json',
  },
})

function formatValidationErrors(detail: unknown): string {
  if (!Array.isArray(detail)) {
    return typeof detail === 'string' ? detail : 'Validation failed'
  }
  const parts = detail.map((item: unknown) => {
    if (item && typeof item === 'object' && 'field' in item && 'message' in item) {
      const f = (item as { field: string; message: string }).field
      const m = (item as { field: string; message: string }).message
      return `${f}: ${m}`
    }
    if (item && typeof item === 'object' && 'loc' in item && 'msg' in item) {
      const loc = (item as { loc: unknown[] }).loc
      const msg = (item as { msg: string }).msg
      const field = Array.isArray(loc) ? loc.filter((x) => !['body', 'query', 'path'].includes(String(x))).join('.') : 'field'
      return `${field || 'request'}: ${msg}`
    }
    return JSON.stringify(item)
  })
  return parts.join('; ')
}

axiosClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = getStoredToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

axiosClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<{ detail?: unknown }>) => {
    const status = error.response?.status
    const data = error.response?.data

    if (status === 401) {
      const url = String(error.config?.url ?? '')
      const isCredentialAttempt = url.includes('/auth/login') || url.includes('/auth/register')
      if (!isCredentialAttempt) {
        localStorage.removeItem('authToken')
        localStorage.removeItem('user')
        window.dispatchEvent(new CustomEvent('erm:session-expired'))
        showAppToast('Session expired', 'warning', 6000)
        if (!window.location.pathname.startsWith('/login')) {
          window.location.assign('/login')
        }
      }
      return Promise.reject(error)
    }

    if (status === 403) {
      showAppToast('Access denied', 'error')
      return Promise.reject(error)
    }

    if (status === 422) {
      const msg = formatValidationErrors(data?.detail)
      showAppToast(msg || 'Validation failed', 'error', 8000)
      return Promise.reject(error)
    }

    if (status === 500) {
      showAppToast('Server error — our team has been notified', 'error')
      return Promise.reject(error)
    }

    if (error.message === 'Network Error' || error.code === 'ERR_NETWORK') {
      showAppToast('Cannot connect to server — check your connection', 'error')
      return Promise.reject(error)
    }

    return Promise.reject(error)
  }
)

export default axiosClient
