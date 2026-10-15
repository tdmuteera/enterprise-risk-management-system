import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { departmentApi } from '@/api/departmentApi'
import { Department } from '@/types'

export const useDepartments = () => {
  return useQuery({
    queryKey: ['departments'],
    queryFn: () => departmentApi.getDepartments(),
  })
}

export const useDepartmentById = (id: string) => {
  return useQuery({
    queryKey: ['departments', id],
    queryFn: () => departmentApi.getDepartmentById(id),
    enabled: !!id,
  })
}

export const useCreateDepartment = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: Omit<Department, 'id' | 'createdAt'>) =>
      departmentApi.createDepartment(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['departments'] })
    },
  })
}

export const useUpdateDepartment = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Department> }) =>
      departmentApi.updateDepartment(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['departments'] })
    },
  })
}

export const useDeleteDepartment = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => departmentApi.deleteDepartment(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['departments'] })
    },
  })
}
