import { Spinner } from '@/components/ui/Spinner'
import { Card, CardBody } from '@/components/ui/Card'
import { useDashboardStats } from '@/hooks/useRisks'

export const DashboardPage = () => {
  const { data: stats, isLoading } = useDashboardStats()

  if (isLoading) return <Spinner />

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600">Executive overview of enterprise risks</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <Card>
          <CardBody>
            <div className="text-center">
              <p className="text-sm text-gray-600">Total Risks</p>
              <p className="text-4xl font-bold text-gray-900">{stats?.totalRisks || 0}</p>
            </div>
          </CardBody>
        </Card>

        <Card>
          <CardBody>
            <div className="text-center">
              <p className="text-sm text-gray-600">Average Risk Score</p>
              <p className="text-4xl font-bold text-brand-mid">{stats?.averageRiskScore?.toFixed(1) || '0'}</p>
            </div>
          </CardBody>
        </Card>

        <Card>
          <CardBody>
            <div className="text-center">
              <p className="text-sm text-gray-600">Critical Risks</p>
              <p className="text-4xl font-bold text-risk-critical">{stats?.criticalCount || 0}</p>
            </div>
          </CardBody>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardBody>
            <p className="text-gray-500">Charts & analytics - to be implemented</p>
          </CardBody>
        </Card>
        <Card>
          <CardBody>
            <p className="text-gray-500">Recent activities - to be implemented</p>
          </CardBody>
        </Card>
      </div>
    </div>
  )
}
