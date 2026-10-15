import { axiosClient } from './axiosClient'

export interface ReportRequest {
  departmentId?: string
  startDate?: string
  endDate?: string
  format?: 'pdf' | 'excel'
}

export const reportApi = {
  generateDepartmentReport: async (
    departmentId: string,
    format: 'pdf' | 'excel',
    startDate?: string,
    endDate?: string
  ): Promise<{ blob: Blob; headers: Record<string, string> }> => {
    const params: Record<string, string> = { format }
    if (startDate) params.start_date = startDate
    if (endDate) params.end_date = endDate
    const response = await axiosClient.get(`/reports/department/${departmentId}`, {
      params,
      responseType: 'blob',
    })
    return { blob: response.data, headers: response.headers as Record<string, string> }
  },

  generateInstitutionalReport: async (format: 'pdf' = 'pdf'): Promise<Blob> => {
    const response = await axiosClient.get('/reports/institutional', {
      params: { format },
      responseType: 'blob',
    })
    return response.data
  },

  generateExecutiveSummary: async (): Promise<Blob> => {
    const response = await axiosClient.get('/reports/executive', {
      responseType: 'blob',
    })
    return response.data
  },

  generateForensicAudit: async (startDate?: string, endDate?: string): Promise<Blob> => {
    const params: Record<string, string> = {}
    if (startDate) params.start_date = startDate
    if (endDate) params.end_date = endDate
    const response = await axiosClient.get('/reports/forensic-audit', {
      params,
      responseType: 'blob',
    })
    return response.data
  },
}

export const getFilenameFromResponse = (response: { headers?: Record<string, string> }, fallback: string): string => {
  const contentDisposition = response.headers?.['content-disposition']
  if (contentDisposition) {
    const match = contentDisposition.match(/filename="?([^"]+)"?/)
    if (match) return match[1]
  }
  return fallback
}

export const downloadBlob = (blob: Blob, filename: string) => {
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

export const formatDateForFilename = (date: Date = new Date()): string => {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}${month}${day}`
}
