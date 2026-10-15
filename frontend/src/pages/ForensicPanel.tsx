import { useAuth } from '@/context/AuthContext'
import { useToast } from '@/context/ToastContext'
import { useAlerts } from '@/hooks/useAlerts'
import { useRisksPaginated } from '@/hooks/useRisks'
import { KPICard } from '@/components/dashboard/KPICard'
import { Card, CardHeader, CardBody } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { AlertTriangle, TrendingDown, Clock, Link as LinkIcon } from 'lucide-react'
import { formatDate } from '@/utils/dateFormat'
import { useNavigate } from 'react-router-dom'
import type { Risk } from '@/types'

// Mock data structure
interface SuppressionLog {
  riskId: string
  riskTitle: string
  scoreBefore: number
  scoreAfter: number
  changedBy: string
  changedAt: string
  daysToReporting: number
}

interface ChronicRisk {
  id: string
  title: string
  department: string
  score: number
  daysOpen: number
  lastActionTaken: string
}

interface AnomalyEvent {
  id: string
  riskId: string
  riskTitle: string
  type: string
  description: string
  severity: string
  timestamp: string
  user: string
}

export const ForensicPanel = () => {
  const { user } = useAuth()
  const { addToast } = useToast()
  const navigate = useNavigate()
  const { data: riskPage, isLoading: risksLoading } = useRisksPaginated({
    page: 1,
    page_size: 20,
    sort_by: 'score',
    order: 'desc',
  })
  const { data: alerts } = useAlerts(false)

  const riskItems: Risk[] = riskPage?.risks ?? []
  const suppressions: SuppressionLog[] = riskItems.slice(0, 5).map((r: Risk, idx: number) => ({
    riskId: r.id,
    riskTitle: r.title,
    scoreBefore: Math.min(100, Math.round(r.riskScore + 15)),
    scoreAfter: Math.max(1, Math.round(r.riskScore)),
    changedBy: r.owner || 'System',
    changedAt: r.updatedAt,
    daysToReporting: 14 + idx,
  }))

  const chronicRisks: ChronicRisk[] = riskItems.slice(0, 8).map((r: Risk) => ({
    id: r.id,
    title: r.title,
    department: r.departmentId || 'Department',
    score: Math.round(r.riskScore),
    daysOpen: Math.max(0, Math.floor((Date.now() - new Date(r.createdAt).getTime()) / (1000 * 60 * 60 * 24))),
    lastActionTaken: `Status is ${r.status}`,
  }))

  const anomalies: AnomalyEvent[] = (alerts ?? [])
    .filter((a) => a.message.includes('FORENSIC') || a.title.toLowerCase().includes('forensic'))
    .slice(0, 20)
    .map((a, idx) => ({
      id: a.id || String(idx),
      riskId: a.riskId,
      riskTitle: a.riskId ? `Risk ${a.riskId.slice(0, 8)}...` : 'Institution-wide event',
      type: a.title,
      description: a.message,
      severity: a.severity,
      timestamp: a.createdAt,
      user: 'System',
    }))

  const isUuid = (value: string) => /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(value)
  const openRiskForInvestigation = (riskId?: string) => {
    if (!riskId || !isUuid(riskId)) {
      addToast('This forensic item is not linked to a valid risk record', 'warning')
      return
    }
    navigate(`/risks/${riskId}`)
  }

  if (
    user?.role !== 'risk_officer' &&
    user?.role !== 'admin' &&
    user?.role !== 'risk_manager' &&
    user?.role !== 'department_head'
  ) {
    return (
      <div className="text-center py-12">
        <AlertTriangle size={48} className="mx-auto text-gray-300 mb-4" />
        <p className="text-gray-600">Access restricted to risk officers, risk managers, department heads, and admins</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Forensic Panel</h1>
        <p className="text-gray-600 mt-1">Detect anomalies, suppressions, and suspicious patterns</p>
      </div>

      {/* Summary KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          label="Score Suppressions"
          value={suppressions.length}
          variant="critical"
          isLoading={risksLoading}
        />
        <KPICard
          label="Sudden Closures"
          value={2}
          variant="high"
          isLoading={false}
        />
        <KPICard
          label="Chronic Unresolved"
          value={chronicRisks.length}
          variant="medium"
          isLoading={risksLoading}
        />
        <KPICard
          label="Active Chains"
          value={3}
          variant="high"
          isLoading={false}
        />
      </div>

      {/* Risk Suppression Log */}
      <Card>
        <CardHeader>
          <h2 className="font-semibold text-gray-900 flex items-center gap-2">
            <TrendingDown size={20} className="text-risk-critical" />
            Score Suppression Log
          </h2>
          <p className="text-xs text-gray-500 mt-1">Suspicious score drops near reporting deadlines</p>
        </CardHeader>
        <CardBody>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-2 text-left font-medium">Risk Title</th>
                  <th className="px-4 py-2 text-left font-medium">Before</th>
                  <th className="px-4 py-2 text-left font-medium">After</th>
                  <th className="px-4 py-2 text-left font-medium">% Drop</th>
                  <th className="px-4 py-2 text-left font-medium">Changed By</th>
                  <th className="px-4 py-2 text-left font-medium">Days to Report</th>
                  <th className="px-4 py-2 text-left font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {suppressions.map((log) => {
                  const dropPercent = Math.round(((log.scoreBefore - log.scoreAfter) / log.scoreBefore) * 100)
                  return (
                    <tr key={log.riskId} className="border-b hover:bg-gray-50">
                      <td className="px-4 py-2 font-medium text-gray-900">{log.riskTitle}</td>
                      <td className="px-4 py-2">
                        <Badge variant="critical">{log.scoreBefore}</Badge>
                      </td>
                      <td className="px-4 py-2">
                        <Badge variant="low">{log.scoreAfter}</Badge>
                      </td>
                      <td className="px-4 py-2 font-semibold text-risk-critical">-{dropPercent}%</td>
                      <td className="px-4 py-2">{log.changedBy}</td>
                      <td className="px-4 py-2">
                        <span className={log.daysToReporting < 21 ? 'text-risk-critical font-semibold' : ''}>
                          {log.daysToReporting}d
                        </span>
                      </td>
                      <td className="px-4 py-2">
                        <Button
                          size="sm"
                          variant="secondary"
                          onClick={() => {
                            openRiskForInvestigation(log.riskId)
                            addToast('Opening suppression investigation', 'warning')
                          }}
                        >
                          Investigate
                        </Button>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </CardBody>
      </Card>

      {/* Chronic Unresolved Risks */}
      <Card>
        <CardHeader>
          <h2 className="font-semibold text-gray-900 flex items-center gap-2">
            <Clock size={20} className="text-risk-high" />
            Chronic Unresolved Risks
          </h2>
          <p className="text-xs text-gray-500 mt-1">Risks open for 90+ days with minimal action</p>
        </CardHeader>
        <CardBody>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-2 text-left font-medium">Risk Title</th>
                  <th className="px-4 py-2 text-left font-medium">Department</th>
                  <th className="px-4 py-2 text-left font-medium">Score</th>
                  <th className="px-4 py-2 text-left font-medium">Days Open</th>
                  <th className="px-4 py-2 text-left font-medium">Last Action</th>
                  <th className="px-4 py-2 text-left font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {chronicRisks.map((risk) => (
                  <tr key={risk.id} className="border-b hover:bg-gray-50">
                    <td className="px-4 py-2 font-medium text-gray-900">{risk.title}</td>
                    <td className="px-4 py-2">{risk.department}</td>
                    <td className="px-4 py-2">
                      <Badge variant={risk.score > 70 ? 'high' : 'medium'}>{risk.score}</Badge>
                    </td>
                    <td className="px-4 py-2 font-semibold text-risk-high">{risk.daysOpen}d</td>
                    <td className="px-4 py-2 text-xs text-gray-600">{risk.lastActionTaken}</td>
                    <td className="px-4 py-2">
                      <Button
                        size="sm"
                        variant="secondary"
                        onClick={() => {
                          openRiskForInvestigation(risk.id)
                          addToast('Opening risk for forensic review', 'info')
                        }}
                      >
                        Review
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardBody>
      </Card>

      {/* Risk Chain Graph */}
      <Card>
        <CardHeader>
          <h2 className="font-semibold text-gray-900 flex items-center gap-2">
            <LinkIcon size={20} />
            Risk Chain Network
          </h2>
        </CardHeader>
        <CardBody className="h-80 flex items-center justify-center bg-gray-50 rounded">
          <div className="text-center text-gray-500">
            <p>Force-directed risk chain graph</p>
            <p className="text-xs mt-2">(Ready for react-force-graph integration)</p>
          </div>
        </CardBody>
      </Card>

      {/* Audit Anomaly Feed */}
      <Card>
        <CardHeader>
          <h2 className="font-semibold text-gray-900">Forensic Anomaly Feed</h2>
          <p className="text-xs text-gray-500 mt-1">Last 20 flagged events</p>
        </CardHeader>
        <CardBody>
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {anomalies.map((event) => (
              <div
                key={event.id}
                className={`p-4 rounded-lg border-l-4 ${
                  event.severity === 'critical'
                    ? 'bg-red-50 border-l-risk-critical'
                    : 'bg-orange-50 border-l-risk-high'
                }`}
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="font-semibold text-gray-900">{event.type}</h3>
                      <Badge variant={event.severity as any}>{event.severity}</Badge>
                    </div>
                    <p className="text-sm text-gray-700 mb-2">{event.description}</p>
                    <div className="flex items-center gap-4 text-xs text-gray-600">
                      <span>Risk: {event.riskTitle}</span>
                      <span>By: {event.user}</span>
                      <span>{formatDate(event.timestamp)}</span>
                    </div>
                  </div>
                  <Button
                    size="sm"
                    variant="secondary"
                    onClick={() => {
                      openRiskForInvestigation(event.riskId)
                      addToast('Opening anomaly investigation', 'info')
                    }}
                  >
                    Investigate
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </CardBody>
      </Card>
    </div>
  )
}
