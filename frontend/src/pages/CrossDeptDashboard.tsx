import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'
import { useCrossDepartmentAnalytics, useRiskChains } from '@/hooks/useDashboard'
import { KPICard } from '@/components/dashboard/KPICard'
import { Card, CardHeader, CardBody } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { SkeletonCard, SkeletonChart, SkeletonTable } from '@/components/ui/Skeleton'
import { AlertTriangle, CheckCircle2 } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

const getRiskBand = (iriScore: number): string => {
  if (iriScore >= 80) return 'critical'
  if (iriScore >= 60) return 'high'
  if (iriScore >= 40) return 'medium'
  return 'low'
}

export const CrossDeptDashboard = () => {
  const navigate = useNavigate()
  const { data: analytics, isLoading: analyticsLoading } = useCrossDepartmentAnalytics()
  const { data: chains, isLoading: chainsLoading } = useRiskChains()

  const iriData = analytics?.departmentScores.map((dept) => ({
    name: dept.name,
    iri: Number(dept.iriScore || 0),
    risks: dept.riskCount,
  })) || []

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Cross-Department Dashboard</h1>
        <p className="text-gray-600">Institution-wide risk overview • Auto-refreshes every 60s</p>
      </div>

      {/* Row 1: KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          label="Institution IRI Score"
          value={analytics?.institutionIRIScore || 0}
          change={0}
          variant="high"
          isLoading={analyticsLoading}
        />
        <KPICard
          label="Active Risk Chains"
          value={analytics?.activeRiskChains || 0}
          change={0}
          variant="critical"
          isLoading={analyticsLoading}
        />
        <KPICard
          label="Linked Risk Pairs"
          value={analytics?.linkedRiskPairs || 0}
          change={0}
          variant="medium"
          isLoading={analyticsLoading}
        />
        <KPICard
          label="Forensic Alerts"
          value={analytics?.forensicAlerts || 0}
          change={0}
          variant="critical"
          isLoading={analyticsLoading}
        />
      </div>

      {/* Row 2: IRI Bar Chart (Full Width) */}
      <Card>
        <CardHeader>
          <h2 className="font-semibold text-gray-900">Department IRI Scores</h2>
          <p className="text-xs text-gray-500">Click to drill down</p>
        </CardHeader>
        <CardBody>
          {analyticsLoading ? (
            <SkeletonChart />
          ) : (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart
                data={iriData}
                layout="vertical"
                margin={{ top: 5, right: 30, left: 200, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis type="number" stroke="#6b7280" />
                <YAxis dataKey="name" type="category" stroke="#6b7280" width={180} style={{ fontSize: 12 }} />
                <Tooltip />
                <Bar
                  dataKey="iri"
                  fill="#2E75B6"
                  onClick={() => navigate('/departments')}
                  radius={[0, 8, 8, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          )}
        </CardBody>
      </Card>

      {/* Row 3: Risk Chain Graph */}
      <Card>
        <CardHeader>
          <h2 className="font-semibold text-gray-900">Risk Chain Analysis</h2>
          <p className="text-xs text-gray-500">Node color = severity band • Edge thickness = relationship strength</p>
        </CardHeader>
        <CardBody className="h-96 flex items-center justify-center bg-gray-50 rounded">
          {chainsLoading ? (
            <SkeletonChart />
          ) : (
            <div className="text-center text-gray-500">
              <p>Risk Chain Graph visualization</p>
              <p className="text-xs mt-2">(Ready for react-force-graph integration)</p>
              <p className="text-xs mt-4 text-gray-400">
                Showing {chains?.length || 0} risk relationships
              </p>
            </div>
          )}
        </CardBody>
      </Card>

      {/* Row 4: Emerging Institutional Risk Alerts */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <h2 className="font-semibold text-gray-900">Emerging Institutional Risk Chains</h2>
              <p className="text-xs text-gray-500">Critical risk clusters detected</p>
            </div>
          </div>
        </CardHeader>
        <CardBody>
          {chainsLoading ? (
            <SkeletonTable rows={3} />
          ) : chains && chains.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {chains.map((chain: any, idx) => (
                <div key={idx} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1">
                      <h3 className="font-medium text-gray-900 flex items-center gap-2">
                        <AlertTriangle size={16} className="text-risk-critical" />
                        {chain.title}
                      </h3>
                      <p className="text-sm text-gray-600 mt-2">{chain.description}</p>
                      <div className="mt-3 flex flex-wrap gap-2">
                        {chain.departments?.map((dept: string) => (
                          <Badge key={dept} variant="default">
                            {dept}
                          </Badge>
                        ))}
                      </div>
                      <div className="mt-3 flex justify-between text-xs">
                        <span className="text-gray-600">Combined IRI: {chain.combinedIRI}</span>
                        <span className="text-gray-600">Age: {chain.age} days</span>
                      </div>
                    </div>
                  </div>
                  <div className="mt-4 flex gap-2">
                    <Button size="sm" variant="primary" onClick={() => navigate('/forensic')}>
                      View Details
                    </Button>
                    <Button size="sm" variant="danger" onClick={() => navigate('/alerts')}>
                      Escalate
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <CheckCircle2 size={32} className="mx-auto text-green-600 mb-4" />
              <p className="text-gray-600">No emerging risk chains detected</p>
            </div>
          )}
        </CardBody>
      </Card>
    </div>
  )
}
