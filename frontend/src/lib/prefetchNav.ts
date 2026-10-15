import { alertApi } from '@/api/alertApi'
import { dashboardApi } from '@/api/dashboardApi'
import { riskApi } from '@/api/riskApi'
import { queryClient } from '@/lib/queryClient'

/** Warm React Query cache when the user hovers sidebar links (snappier transitions). */
export function prefetchSidebarRoute(href: string, opts?: { departmentId?: string | null }) {
  const deptId = opts?.departmentId

  if (href === '/dashboard') {
    void queryClient.prefetchQuery({
      queryKey: ['dashboard', 'stats'],
      queryFn: () => riskApi.getDashboardStats(),
    })
    void queryClient.prefetchQuery({
      queryKey: ['dashboard', 'executive', 'metrics'],
      queryFn: () => dashboardApi.getExecutiveMetrics(),
    })
    void queryClient.prefetchQuery({
      queryKey: ['dashboard', 'iri-trend', 30],
      queryFn: () => dashboardApi.getInstitutionIRITrend(30),
    })
    if (deptId) {
      void queryClient.prefetchQuery({
        queryKey: ['dashboard', 'department', deptId, 'analytics'],
        queryFn: () => dashboardApi.getDepartmentAnalytics(deptId),
      })
    }
  }

  if (href === '/risks') {
    void queryClient.prefetchQuery({
      queryKey: ['risks', undefined],
      queryFn: () => riskApi.getRisks(),
    })
  }

  if (href === '/alerts') {
    void queryClient.prefetchQuery({
      queryKey: ['alerts', false],
      queryFn: () => alertApi.getAlerts(false),
    })
  }

  if (href === '/departments') {
    void queryClient.prefetchQuery({
      queryKey: ['dashboard', 'cross-department', 'analytics'],
      queryFn: () => dashboardApi.getCrossDepartmentAnalytics(),
    })
  }

  if (href === '/reports') {
    void queryClient.prefetchQuery({
      queryKey: ['dashboard', 'cross-department', 'analytics'],
      queryFn: () => dashboardApi.getCrossDepartmentAnalytics(),
    })
    void queryClient.prefetchQuery({
      queryKey: ['dashboard', 'executive', 'metrics'],
      queryFn: () => dashboardApi.getExecutiveMetrics(),
    })
  }
}
