import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { riskApi } from '@/api/riskApi'
import type { RiskFormData } from '@/forms/riskSchema'
import type { RiskListResponse, RiskDetailResponse } from '@/api/riskApi'

const invalidateRiskRelated = (queryClient: ReturnType<typeof useQueryClient>) => {
  queryClient.invalidateQueries({ queryKey: ['risks'] })
  queryClient.invalidateQueries({ queryKey: ['dashboard'] })
}

export const useRisks = (filters?: Record<string, unknown>) => {
  return useQuery({
    queryKey: ['risks', filters],
    queryFn: () => riskApi.getRisks(filters),
  })
}

export interface RiskFilters {
  category?: string
  status?: string
  department_id?: string
  sort_by?: string
  order?: 'asc' | 'desc'
  page?: number
  page_size?: number
}

export const useRisksPaginated = (filters?: RiskFilters) => {
  return useQuery<RiskListResponse>({
    queryKey: ['risks', 'paginated', filters],
    queryFn: () => riskApi.getRisksPaginated(filters as Record<string, unknown>),
  })
}

export const useRiskById = (id: string) => {
  return useQuery({
    queryKey: ['risks', id],
    queryFn: () => riskApi.getRiskById(id),
    enabled: !!id,
  })
}

export const useRiskDetail = (id: string) => {
  return useQuery<RiskDetailResponse>({
    queryKey: ['risks', id, 'detail'],
    queryFn: () => riskApi.getRiskDetail(id),
    enabled: !!id,
  })
}

export const useCreateRisk = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationKey: ['risks', 'create'],
    mutationFn: (data: RiskFormData) => riskApi.createRisk(data),
    onSuccess: () => invalidateRiskRelated(queryClient),
  })
}

export const useUpdateRisk = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationKey: ['risks', 'update'],
    mutationFn: ({ id, data }: { id: string; data: RiskFormData }) => riskApi.updateRisk(id, data),
    onSuccess: () => invalidateRiskRelated(queryClient),
  })
}

export const useDeleteRisk = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationKey: ['risks', 'delete'],
    mutationFn: (id: string) => riskApi.deleteRisk(id),
    onSuccess: () => invalidateRiskRelated(queryClient),
  })
}

export const useRisksByDepartment = (departmentId: string) => {
  return useQuery({
    queryKey: ['risks', 'department', departmentId],
    queryFn: () => riskApi.getRisksByDepartment(departmentId),
    enabled: !!departmentId,
  })
}

export const useDashboardStats = () => {
  return useQuery({
    queryKey: ['dashboard', 'stats'],
    queryFn: () => riskApi.getDashboardStats(),
    refetchInterval: 60000,
  })
}

export const useRiskTrends = (days: number = 30, departmentId?: string) => {
  return useQuery({
    queryKey: ['risks', 'trends', days, departmentId],
    queryFn: () => riskApi.getRiskTrends(days, departmentId),
  })
}

export const useApproveRisk = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationKey: ['risks', 'approve'],
    mutationFn: ({ id, justification }: { id: string; justification: string }) =>
      riskApi.approveRisk(id, justification),
    onSuccess: () => invalidateRiskRelated(queryClient),
  })
}

export const useRejectRisk = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationKey: ['risks', 'reject'],
    mutationFn: ({ id, justification }: { id: string; justification: string }) =>
      riskApi.rejectRisk(id, justification),
    onSuccess: () => invalidateRiskRelated(queryClient),
  })
}

export const usePendingRisks = () => {
  return useQuery({
    queryKey: ['risks', 'pending'],
    queryFn: () => riskApi.getPendingRisks(),
  })
}
