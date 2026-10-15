import { useMemo } from 'react'
import { Users as UsersIcon } from 'lucide-react'
import { useAdminUsers } from '@/hooks/useUsers'
import { useDepartments } from '@/hooks/useDepartments'
import { Card, CardBody } from '@/components/ui/Card'
import { Spinner } from '@/components/ui/Spinner'
import { Badge } from '@/components/ui/Badge'
import { formatDateTime } from '@/utils/dateFormat'

export const UsersPage = () => {
  const { data: users, isLoading, error } = useAdminUsers()
  const { data: departments } = useDepartments()

  const deptNameById = useMemo(() => {
    const m = new Map<string, string>()
    departments?.forEach((d) => m.set(d.id, d.name))
    return m
  }, [departments])

  if (isLoading) return <Spinner />
  if (error) {
    return <p className="text-risk-critical">Could not load users. You may need admin access.</p>
  }

  return (
    <div className="space-y-6">
      <div className="flex items-start gap-3">
        <div className="rounded-lg bg-brand-mid/10 p-2 text-brand-dark">
          <UsersIcon className="h-6 w-6" />
        </div>
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Users</h1>
          <p className="text-gray-600 mt-1">Accounts registered in the platform (admin only)</p>
        </div>
      </div>

      <Card>
        <CardBody className="overflow-x-auto p-0">
          {!users?.length ? (
            <p className="p-6 text-center text-gray-500">No users returned from the API.</p>
          ) : (
            <table className="min-w-full text-left text-sm">
              <thead className="border-b border-gray-200 bg-gray-50 text-xs font-semibold uppercase text-gray-600">
                <tr>
                  <th className="px-4 py-3">Name</th>
                  <th className="px-4 py-3">Email</th>
                  <th className="px-4 py-3">Role</th>
                  <th className="px-4 py-3">Department</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Created</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {users.map((u) => (
                  <tr key={u.id} className="hover:bg-gray-50/80">
                    <td className="px-4 py-3 font-medium text-gray-900">{u.full_name}</td>
                    <td className="px-4 py-3 text-gray-700">{u.email}</td>
                    <td className="px-4 py-3">
                      <span className="rounded bg-gray-100 px-2 py-0.5 font-mono text-xs text-gray-800">
                        {u.role}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-gray-700">
                      {u.department_id ? deptNameById.get(u.department_id) ?? u.department_id : '—'}
                    </td>
                    <td className="px-4 py-3">
                      {u.is_active ? (
                        <Badge variant="low">Active</Badge>
                      ) : (
                        <Badge variant="critical">Inactive</Badge>
                      )}
                    </td>
                    <td className="px-4 py-3 text-gray-600 whitespace-nowrap">
                      {u.created_at ? formatDateTime(u.created_at) : '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </CardBody>
      </Card>
    </div>
  )
}
