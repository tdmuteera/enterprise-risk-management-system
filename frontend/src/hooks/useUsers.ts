import { useQuery } from '@tanstack/react-query'
import { userApi } from '@/api/userApi'

export const useAdminUsers = () => {
  return useQuery({
    queryKey: ['users', 'admin-list'],
    queryFn: () => userApi.listUsers(),
  })
}
