import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Area,
  AreaChart,
} from 'recharts'
import { useExecutiveMetrics, useInstitutionIRITrend, useForensicAlerts } from '@/hooks/useDashboard'
import { Card, CardHeader, CardBody } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { SkeletonCard, SkeletonChart, SkeletonTable } from '@/components/ui/Skeleton'
import { AlertCircle, TrendingUp } from 'lucide-react'
import { useMemo, useState } from 'react'

export const ExecutiveDashboard = () => {
  const [activeSeverityFilter, setActiveSeverityFilter] = useState<'all' | 'critical' | 'high' | 'medium' | 'low'>('all')
  const { data: metrics, isLoading: metricsLoading } = useExecutiveMetrics()
  const { data: iriTrend, isLoading: trendLoading } = useInstitutionIRITrend(30)
  const { data: alerts, isLoading: alertsLoading } = useForensicAlerts()

  const scoreCardData = [
    {
      title: 'Critical',
      icon: '🔴',
      count: metrics?.criticalRisks || 0,
      bgColor: 'bg-risk-critical',
      textColor: 'text-white',
    },
    {
      title: 'High',
      icon: '🟠',
      count: metrics?.highRisks || 0,
      bgColor: 'bg-risk-high',
      textColor: 'text-white',
    },
    {
      title: 'Medium',
      icon: '🟡',
      count: metrics?.mediumRisks || 0,
      bgColor: 'bg-risk-medium',
      textColor: 'text-white',
    },
    {
      title: 'Low',
      icon: '🟢',
      count: metrics?.lowRisks || 0,
      bgColor: 'bg-risk-low',
      textColor: 'text-white',
    },
  ]

  const filteredBoardRisks = useMemo(() => {
    const items = metrics?.topBoardRisks || []
    if (activeSeverityFilter === 'all') return items
    return items.filter((risk) => {
      if (activeSeverityFilter === 'critical') return risk.score > 15
      if (activeSeverityFilter === 'high') return risk.score > 10 && risk.score <= 15
      if (activeSeverityFilter === 'medium') return risk.score > 6 && risk.score <= 10
      return risk.score <= 6
    })
  }, [metrics?.topBoardRisks, activeSeverityFilter])

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold text-gray-900">Executive Dashboard</h1>
        <p className="text-gray-600">Institution-wide risk posture • Boardroom presentation mode • Auto-refreshes every 60s</p>
      </div>

      {/* Row 1: Institutional Risk Scorecard (4 Large Blocks) */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {scoreCardData.map((card) => (
          <div
            key={card.title}
            onClick={() => setActiveSeverityFilter(card.title.toLowerCase() as 'critical' | 'high' | 'medium' | 'low')}
            className={`${card.bgColor} ${card.textColor} rounded-lg p-8 shadow-lg cursor-pointer hover:shadow-xl transition-shadow transform hover:scale-105 ${activeSeverityFilter === card.title.toLowerCase() ? 'ring-4 ring-brand-accent' : ''}`}
          >
            <div className="text-4xl mb-2">{card.icon}</div>
            <p className="text-sm opacity-90 mb-2">{card.title} Risk</p>
            <p className="text-5xl font-bold">{card.count}</p>
            <p className="text-xs opacity-75 mt-4">Click to filter</p>
          </div>
        ))}
      </div>
      <div className="flex items-center gap-2">
        <button
          onClick={() => setActiveSeverityFilter('all')}
          className={`px-3 py-1 rounded text-sm ${activeSeverityFilter === 'all' ? 'bg-brand-mid text-white' : 'bg-gray-100 text-gray-700'}`}
        >
          Show All
        </button>
        {activeSeverityFilter !== 'all' && <span className="text-sm text-gray-600">Active filter: {activeSeverityFilter}</span>}
      </div>

      {/* Row 2: IRI Trend Line (Last 30 Days) */}
      <Card>
        <CardHeader>
          <h2 className="font-semibold text-gray-900">Institution IRI Trend (30 Days)</h2>
          <p className="text-xs text-gray-500">Institutional Risk Index over time</p>
        </CardHeader>
        <CardBody>
          {trendLoading ? (
            <SkeletonChart />
          ) : (
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart
                data={iriTrend || []}
                margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
              >
                <defs>
                  <linearGradient id="colorIri" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#2E75B6" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#2E75B6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="date" stroke="#6b7280" style={{ fontSize: 12 }} />
                <YAxis stroke="#6b7280" style={{ fontSize: 12 }} />
                <Tooltip />
                <Area
                  type="monotone"
                  dataKey="count"
                  stroke="#2E75B6"
                  fillOpacity={1}
                  fill="url(#colorIri)"
                  strokeWidth={3}
                  dot={false}
                />
              </AreaChart>
            </ResponsiveContainer>
          )}
        </CardBody>
      </Card>

      {/* Row 3: Board-Attention Risk Table (Top 10) */}
      <Card>
        <CardHeader>
          <h2 className="font-semibold text-gray-900">Top 10 Institution-Wide Risks</h2>
          <p className="text-xs text-gray-500">Highest IRI and longest-open risks</p>
        </CardHeader>
        <CardBody>
          {metricsLoading ? (
            <SkeletonTable rows={10} />
          ) : filteredBoardRisks.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-2 text-left font-medium">#</th>
                    <th className="px-4 py-2 text-left font-medium">Department</th>
                    <th className="px-4 py-2 text-left font-medium">Risk Title</th>
                    <th className="px-4 py-2 text-left font-medium">Score</th>
                    <th className="px-4 py-2 text-left font-medium">IRI</th>
                    <th className="px-4 py-2 text-left font-medium">Mitigation</th>
                    <th className="px-4 py-2 text-left font-medium">Days Open</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredBoardRisks.map((risk, idx) => (
                    <tr key={risk.id} className="border-b hover:bg-gray-50 transition-colors">
                      <td className="px-4 py-2 font-medium">
                        <div className="flex items-center gap-2">
                          {risk.hasAlert && (
                            <div className="w-2 h-2 bg-risk-critical rounded-full animate-pulse" />
                          )}
                          {idx + 1}
                        </div>
                      </td>
                      <td className="px-4 py-2">{risk.departmentName}</td>
                      <td className="px-4 py-2 font-medium text-gray-900">{risk.title}</td>
                      <td className="px-4 py-2">
                        <Badge variant={risk.score > 15 ? 'critical' : risk.score > 10 ? 'high' : 'medium'}>
                          {risk.score}
                        </Badge>
                      </td>
                      <td className="px-4 py-2">
                        <div className="flex items-center gap-2">
                          <span className="font-semibold">{risk.iri}</span>
                          {risk.iri > 50 && <TrendingUp size={16} className="text-risk-critical" />}
                        </div>
                      </td>
                      <td className="px-4 py-2">
                        <span className="text-xs px-2 py-1 rounded-full bg-blue-100 text-blue-800">
                          {risk.mitigationStatus}
                        </span>
                      </td>
                      <td className="px-4 py-2">{risk.daysOpen}d</td>
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

      {/* Row 4: Active Forensic Alerts */}
      <Card>
        <CardHeader>
          <h2 className="font-semibold text-gray-900">Active Forensic Alerts</h2>
          <p className="text-xs text-gray-500">For awareness and monitoring</p>
        </CardHeader>
        <CardBody>
          {alertsLoading ? (
            <SkeletonTable rows={3} />
          ) : alerts && alerts.length > 0 ? (
            <div className="space-y-3">
              {alerts.map((alert: any, idx) => (
                <div
                  key={idx}
                  className={`p-4 rounded-lg border-l-4 ${
                    alert.severity === 'critical'
                      ? 'bg-red-50 border-l-risk-critical'
                      : alert.severity === 'high'
                        ? 'bg-orange-50 border-l-risk-high'
                        : 'bg-yellow-50 border-l-risk-medium'
                  }`}
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <AlertCircle
                          size={16}
                          className={
                            alert.severity === 'critical'
                              ? 'text-risk-critical'
                              : alert.severity === 'high'
                                ? 'text-risk-high'
                                : 'text-risk-medium'
                          }
                        />
                        <h3 className="font-medium text-gray-900">{alert.title}</h3>
                        <Badge
                          variant={
                            alert.severity === 'critical'
                              ? 'critical'
                              : alert.severity === 'high'
                                ? 'high'
                                : 'warning'
                          }
                        >
                          {alert.severity}
                        </Badge>
                      </div>
                      <p className="text-sm text-gray-600 mt-2">{alert.description}</p>
                      <p className="text-xs text-gray-500 mt-2">
                        Risk: {alert.riskTitle} • Department: {alert.departmentName}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <p className="text-gray-500">No active forensic alerts</p>
            </div>
          )}
        </CardBody>
      </Card>

      {/* Last updated indicator */}
      <div className="text-center text-xs text-gray-500">
        ↻ Auto-refreshing every 60 seconds • Last update: {new Date().toLocaleTimeString()}
      </div>
    </div>
  )
}
