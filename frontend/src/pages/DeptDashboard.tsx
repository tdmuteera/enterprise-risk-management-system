import { useParams } from 'react-router-dom'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
} from 'recharts'
import { riskColorMap } from '@/utils/riskColor'
import { formatDate, getDayUntil } from '@/utils/dateFormat'
import { useDepartmentAnalytics, useDepartmentTopRisks, useDepartmentMitigations, useDepartmentHeatmap } from '@/hooks/useDashboard'
import { useRiskTrends } from '@/hooks/useRisks'
import { KPICard } from '@/components/dashboard/KPICard'
import { Card, CardHeader, CardBody } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { SkeletonCard, SkeletonTable, SkeletonChart } from '@/components/ui/Skeleton'
import { AlertCircle, Edit, Eye } from 'lucide-react'

export const DeptDashboard = () => {
  const { deptId } = useParams<{ deptId: string }>()
  const { data: analytics, isLoading: analyticsLoading } = useDepartmentAnalytics(deptId || '')
  const { data: topRisks, isLoading: risksLoading } = useDepartmentTopRisks(deptId || '', 5)
  const { data: mitigations, isLoading: mitigationsLoading } = useDepartmentMitigations(deptId || '')
  const { data: trendData, isLoading: trendLoading } = useRiskTrends(30, deptId || undefined)
  const { data: heatmapData, isLoading: heatmapLoading } = useDepartmentHeatmap(deptId || '')

  if (!deptId) return <div className="text-red-600">Department ID missing</div>

  // Risk distribution for pie chart
  const riskDistribution = [
    { name: 'Critical', value: analytics?.criticalCount || 0, fill: riskColorMap.critical },
    { name: 'High', value: analytics?.highCount || 0, fill: riskColorMap.high },
    { name: 'Medium', value: analytics?.mediumCount || 0, fill: riskColorMap.medium },
    { name: 'Low', value: analytics?.lowCount || 0, fill: riskColorMap.low },
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Department Dashboard</h1>
        <p className="text-gray-600">Real-time risk overview • Auto-refreshes every 60s</p>
      </div>

      {/* Row 1: KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          label="Total Risks"
          value={analytics?.totalRisks || 0}
          change={0}
          variant="default"
          isLoading={analyticsLoading}
        />
        <KPICard
          label="Critical Risks 🔴"
          value={analytics?.criticalCount || 0}
          change={analytics?.criticalChange}
          variant="critical"
          isLoading={analyticsLoading}
        />
        <KPICard
          label="High Risks 🟠"
          value={analytics?.highCount || 0}
          change={analytics?.highChange}
          variant="high"
          isLoading={analyticsLoading}
        />
        <KPICard
          label="Overdue Mitigations ⚠️"
          value={analytics?.overdueCount || 0}
          change={analytics?.overdueChange}
          variant="medium"
          isLoading={analyticsLoading}
        />
      </div>

      {/* Row 2: Top Risks Table + Risk Distribution Donut */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Top 5 Risks Table */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <h2 className="font-semibold text-gray-900">Top 5 Risks</h2>
            </CardHeader>
            <CardBody>
              {risksLoading ? (
                <SkeletonTable rows={5} />
              ) : topRisks && topRisks.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-4 py-2 text-left font-medium">#</th>
                        <th className="px-4 py-2 text-left font-medium">Title</th>
                        <th className="px-4 py-2 text-left font-medium">Category</th>
                        <th className="px-4 py-2 text-left font-medium">Score</th>
                        <th className="px-4 py-2 text-left font-medium">Owner</th>
                        <th className="px-4 py-2 text-left font-medium">Status</th>
                        <th className="px-4 py-2 text-left font-medium">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {topRisks.map((risk, idx) => (
                        <tr key={risk.id} className="border-b hover:bg-gray-50">
                          <td className="px-4 py-2">{idx + 1}</td>
                          <td className="px-4 py-2 font-medium text-gray-900">{risk.title}</td>
                          <td className="px-4 py-2">{risk.category}</td>
                          <td className="px-4 py-2">
                            <Badge variant={risk.severity as any}>{risk.riskScore}</Badge>
                          </td>
                          <td className="px-4 py-2">{risk.owner}</td>
                          <td className="px-4 py-2">
                            <span className="text-xs px-2 py-1 rounded-full bg-blue-100 text-blue-800">
                              {risk.status}
                            </span>
                          </td>
                          <td className="px-4 py-2 flex gap-2">
                            <button className="p-1 hover:bg-gray-200 rounded">
                              <Eye size={16} className="text-gray-600" />
                            </button>
                            <button className="p-1 hover:bg-gray-200 rounded">
                              <Edit size={16} className="text-gray-600" />
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p className="text-gray-500 text-center py-8">No risks found</p>
              )}
            </CardBody>
          </Card>
        </div>

        {/* Risk Distribution Donut Chart */}
        <Card>
          <CardHeader>
            <h2 className="font-semibold text-gray-900">Risk Distribution</h2>
          </CardHeader>
          <CardBody className="flex items-center justify-center">
            {heatmapLoading ? (
              <SkeletonChart />
            ) : (
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie
                    data={riskDistribution.filter((d) => d.value > 0)}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={90}
                    paddingAngle={2}
                    dataKey="value"
                  >
                    {riskDistribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.fill} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            )}
            <div className="absolute text-center">
              <p className="text-2xl font-bold">{analytics?.totalRisks || 0}</p>
              <p className="text-xs text-gray-600">Total Risks</p>
            </div>
          </CardBody>
        </Card>
      </div>

      {/* Row 3: Risk Heatmap + 30-Day Trend */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Risk Heatmap */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <h2 className="font-semibold text-gray-900">Risk Heatmap</h2>
              <p className="text-xs text-gray-500">Likelihood vs Impact</p>
            </CardHeader>
            <CardBody>
              {heatmapLoading ? (
                <SkeletonChart />
              ) : heatmapData ? (
                <div className="overflow-x-auto">
                  <div className="grid gap-0.5 p-4" style={{ gridTemplateColumns: 'repeat(5, 1fr)' }}>
                    {heatmapData.flat().map((cell, idx) => {
                      const intensity = cell.count > 0 ? Math.min(cell.count / 10, 1) : 0
                      const bgColor =
                        intensity === 0
                          ? 'bg-white'
                          : `bg-gradient-to-br from-orange-100 to-red-${Math.floor(intensity * 9)}00`
                      return (
                        <div
                          key={idx}
                          className={`p-3 rounded border border-gray-200 ${bgColor} text-center cursor-pointer hover:shadow-md transition-shadow`}
                          title={cell.risks?.map((r: any) => r.title).join(', ')}
                        >
                          <span className="text-sm font-semibold text-gray-900">{cell.count}</span>
                        </div>
                      )
                    })}
                  </div>
                </div>
              ) : (
                <p className="text-gray-500">No heatmap data</p>
              )}
            </CardBody>
          </Card>
        </div>

        {/* 30-Day Trend Line Chart */}
        <Card>
          <CardHeader>
            <h2 className="font-semibold text-gray-900">30-Day Trend</h2>
            <p className="text-xs text-gray-500">Avg Risk Score</p>
          </CardHeader>
          <CardBody>
            {trendLoading ? (
              <SkeletonChart />
            ) : (
              <ResponsiveContainer width="100%" height={250}>
                <LineChart data={trendData || []}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis dataKey="date" stroke="#6b7280" style={{ fontSize: 12 }} />
                  <YAxis stroke="#6b7280" style={{ fontSize: 12 }} />
                  <Tooltip />
                  <Line
                    type="monotone"
                    dataKey="count"
                    stroke="#2E75B6"
                    fill="#2E75B6"
                    fillOpacity={0.2}
                    strokeWidth={2}
                    dot={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            )}
          </CardBody>
        </Card>
      </div>

      {/* Row 4: Mitigation Tracker */}
      <Card>
        <CardHeader>
          <h2 className="font-semibold text-gray-900">Mitigation Tracker</h2>
        </CardHeader>
        <CardBody>
          {mitigationsLoading ? (
            <SkeletonTable rows={5} />
          ) : mitigations && mitigations.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-2 text-left font-medium">Risk</th>
                    <th className="px-4 py-2 text-left font-medium">Mitigation</th>
                    <th className="px-4 py-2 text-left font-medium">Assigned To</th>
                    <th className="px-4 py-2 text-left font-medium">Due Date</th>
                    <th className="px-4 py-2 text-left font-medium">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {mitigations.map((m) => {
                    const isOverdue = getDayUntil(m.dueDate) < 0
                    return (
                      <tr
                        key={m.id}
                        className={`border-b hover:bg-gray-50 ${isOverdue ? 'border-l-4 border-l-risk-critical' : ''}`}
                      >
                        <td className="px-4 py-2 font-medium">{m.riskTitle}</td>
                        <td className="px-4 py-2">{m.description}</td>
                        <td className="px-4 py-2">{m.owner}</td>
                        <td className="px-4 py-2">
                          <div className="flex items-center gap-2">
                            {formatDate(m.dueDate)}
                            {isOverdue && <AlertCircle size={16} className="text-risk-critical" />}
                          </div>
                        </td>
                        <td className="px-4 py-2">
                          <Badge variant={isOverdue ? 'critical' : 'success'}>{m.status}</Badge>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-gray-500 text-center py-8">No mitigations</p>
          )}
        </CardBody>
      </Card>
    </div>
  )
}
