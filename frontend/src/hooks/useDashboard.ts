import { useQuery } from '@tanstack/react-query'
import { dashboardApi } from '@/api/dashboardApi'

const REFETCH_INTERVAL = 60000 // 60 seconds

export const useDepartmentAnalytics = (departmentId: string) => {
  return useQuery({
    queryKey: ['dashboard', 'department', departmentId, 'analytics'],
    queryFn: () => dashboardApi.getDepartmentAnalytics(departmentId),
    enabled: !!departmentId,
    refetchInterval: REFETCH_INTERVAL,
  })
}

export const useDepartmentTopRisks = (departmentId: string, limit: number = 5) => {
  return useQuery({
    queryKey: ['dashboard', 'department', departmentId, 'top-risks', limit],
    queryFn: () => dashboardApi.getDepartmentTopRisks(departmentId, limit),
    enabled: !!departmentId,
    refetchInterval: REFETCH_INTERVAL,
  })
}

export const useDepartmentHeatmap = (departmentId: string) => {
  return useQuery({
    queryKey: ['dashboard', 'department', departmentId, 'heatmap'],
    queryFn: () => dashboardApi.getDepartmentHeatmap(departmentId),
    enabled: !!departmentId,
    refetchInterval: REFETCH_INTERVAL,
  })
}

export const useDepartmentMitigations = (departmentId: string) => {
  return useQuery({
    queryKey: ['dashboard', 'department', departmentId, 'mitigations'],
    queryFn: () => dashboardApi.getDepartmentMitigations(departmentId),
    enabled: !!departmentId,
    refetchInterval: REFETCH_INTERVAL,
  })
}

export const useCrossDepartmentAnalytics = () => {
  return useQuery({
    queryKey: ['dashboard', 'cross-department', 'analytics'],
    queryFn: () => dashboardApi.getCrossDepartmentAnalytics(),
    refetchInterval: REFETCH_INTERVAL,
  })
}

export const useRiskChains = () => {
  return useQuery({
    queryKey: ['dashboard', 'risk-chains'],
    queryFn: () => dashboardApi.getRiskChains(),
    refetchInterval: REFETCH_INTERVAL,
  })
}

export const useExecutiveMetrics = () => {
  return useQuery({
    queryKey: ['dashboard', 'executive', 'metrics'],
    queryFn: () => dashboardApi.getExecutiveMetrics(),
    refetchInterval: REFETCH_INTERVAL,
  })
}

export const useInstitutionIRITrend = (days: number = 30) => {
  return useQuery({
    queryKey: ['dashboard', 'iri-trend', days],
    queryFn: () => dashboardApi.getInstitutionIRITrend(days),
    refetchInterval: REFETCH_INTERVAL,
  })
}

export const useForensicAlerts = () => {
  return useQuery({
    queryKey: ['dashboard', 'forensic-alerts'],
    queryFn: () => dashboardApi.getForensicAlerts(),
    refetchInterval: REFETCH_INTERVAL,
  })
}
