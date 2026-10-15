import { Building2 } from 'lucide-react'
import { useDepartments } from '@/hooks/useDepartments'
import { Card, CardBody } from '@/components/ui/Card'
import { Spinner } from '@/components/ui/Spinner'
import { Badge } from '@/components/ui/Badge'
import { formatDate } from '@/utils/dateFormat'

export const DepartmentsPage = () => {
  const { data: departments, isLoading, error } = useDepartments()

  if (isLoading) return <Spinner />
  if (error) {
    return <p className="text-risk-critical">Could not load departments. Is the API running?</p>
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Departments</h1>
        <p className="text-gray-600 mt-1">Active organisational units in the institution</p>
      </div>

      {!departments?.length ? (
        <Card>
          <CardBody>
            <p className="text-center text-gray-500">No departments found. Seed the database or create departments as an admin.</p>
          </CardBody>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {departments.map((d) => (
            <Card key={d.id}>
              <CardBody>
                <div className="flex items-start gap-3">
                  <div className="rounded-lg bg-brand-mid/10 p-2 text-brand-dark">
                    <Building2 className="h-5 w-5" />
                  </div>
                  <div className="min-w-0 flex-1 space-y-2">
                    <div className="flex flex-wrap items-center gap-2">
                      <h2 className="text-lg font-semibold text-gray-900">{d.name}</h2>
                      <Badge variant="low">{d.code}</Badge>
                    </div>
                    {d.head ? (
                      <p className="text-sm text-gray-600">
                        Head: <span className="font-medium text-gray-800">{d.head}</span>
                      </p>
                    ) : null}
                    <div className="flex flex-wrap gap-4 text-xs text-gray-500">
                      {typeof d.riskScore === 'number' && d.riskScore > 0 ? (
                        <span>IRI-style score: {d.riskScore.toFixed(1)}</span>
                      ) : null}
                      <span>Added {formatDate(d.createdAt)}</span>
                    </div>
                  </div>
                </div>
              </CardBody>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
