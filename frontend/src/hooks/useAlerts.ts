import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { alertApi } from '@/api/alertApi'
import { Alert } from '@/types'

export const useAlerts = (unreadOnly: boolean = false) => {
  return useQuery({
    queryKey: ['alerts', unreadOnly],
    queryFn: () => alertApi.getAlerts(unreadOnly),
    refetchInterval: 30000, // Refresh every 30 seconds
  })
}

export const useUnreadAlertCount = () => {
  return useQuery({
    queryKey: ['alerts', 'unread-count'],
    queryFn: () => alertApi.getUnreadCount(),
    refetchInterval: 30000,
  })
}

export const useMarkAlertAsRead = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => alertApi.markAlertAsRead(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] })
    },
  })
}

export const useMarkAllAlertsRead = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: () => alertApi.markAllAsRead(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] })
    },
  })
}

export const useDeleteAlert = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => alertApi.deleteAlert(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] })
    },
  })
}

export const useTriggerForensicScan = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationKey: ['forensic-scan'],
    mutationFn: () => alertApi.triggerForensicScan(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard'] })
    },
  })
}
