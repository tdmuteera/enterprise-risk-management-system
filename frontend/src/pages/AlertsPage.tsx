import { useState } from 'react'
import { AlertCircle, Trash2, Eye, PlayCircle } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { useAlerts, useDeleteAlert, useMarkAllAlertsRead, useTriggerForensicScan } from '@/hooks/useAlerts'
import { useToast } from '@/context/ToastContext'
import { formatRelative } from '@/utils/dateFormat'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { Card, CardHeader, CardBody } from '@/components/ui/Card'
import { SkeletonCard } from '@/components/ui/Skeleton'
import { useAuth } from '@/context/AuthContext'

type AlertFilter = 'all' | 'forensic' | 'high-risk' | 'overdue' | 'emerging'

const FILTER_TABS = [
  { id: 'all', label: 'All' },
  { id: 'forensic', label: 'Forensic' },
  { id: 'high-risk', label: 'High Risk' },
  { id: 'overdue', label: 'Overdue' },
  { id: 'emerging', label: 'Emerging Chain' },
]

export const AlertsPage = () => {
  const navigate = useNavigate()
  const { user } = useAuth()
  const { data: alerts, isLoading, refetch } = useAlerts(false)
  const markAllRead = useMarkAllAlertsRead()
  const dismissAlert = useDeleteAlert()
  const forensicScan = useTriggerForensicScan()
  const { addToast } = useToast()
  const [activeFilter, setActiveFilter] = useState<AlertFilter>('all')

  const filterAlerts = () => {
    if (!alerts) return []

    switch (activeFilter) {
      case 'forensic':
        return alerts.filter((a) => a.severity === 'critical' || a.severity === 'high')
      case 'high-risk':
        return alerts.filter((a) => a.severity === 'high' || a.severity === 'critical')
      case 'overdue':
        return alerts.filter(
          (a) => a.title.includes('Overdue') || a.message.toLowerCase().includes('overdue')
        )
      case 'emerging':
        return alerts.filter(
          (a) => a.title.includes('Chain') || a.message.toLowerCase().includes('chain')
        )
      default:
        return alerts
    }
  }

  const filteredAlerts = filterAlerts()

  const handleRunForensicScan = async () => {
    if (
      user?.role !== 'risk_officer' &&
      user?.role !== 'admin' &&
      user?.role !== 'risk_manager'
    )
      return

    addToast('Running forensic scan...', 'info')

    try {
      const created = await forensicScan.mutateAsync()
      addToast(`Forensic scan completed — ${created} new alert(s)`, 'success')
      refetch()
    } catch {
      addToast('Forensic scan failed', 'error')
    }
  }

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
        return '🔴'
      case 'high':
        return '🟠'
      case 'medium':
        return '🟡'
      default:
        return '🔵'
    }
  }

  const isFrensicAlert = (alert: { title: string; message: string }) =>
    alert.title.includes('Forensic') ||
    alert.title.includes('RiskSuppression') ||
    alert.message.includes('FORENSIC')

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Alerts</h1>
          <p className="text-gray-600 mt-1">System alerts and forensic anomalies</p>
        </div>
        {user?.role === 'risk_officer' || user?.role === 'admin' || user?.role === 'risk_manager' ? (
          <Button
            variant="primary"
            onClick={handleRunForensicScan}
            isLoading={forensicScan.isPending}
            className="flex items-center gap-2"
          >
            <PlayCircle size={16} />
            Run Forensic Scan
          </Button>
        ) : null}
      </div>

      {/* Filter Tabs */}
      <div className="border-b border-gray-200">
        <div className="flex gap-8">
          {FILTER_TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveFilter(tab.id as AlertFilter)}
              className={`px-4 py-4 font-medium border-b-2 transition-colors ${
                activeFilter === tab.id
                  ? 'border-brand-mid text-brand-mid'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Alerts Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <SkeletonCard key={i} />
          ))}
        </div>
      ) : filteredAlerts && filteredAlerts.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredAlerts.map((alert) => (
            <Card
              key={alert.id}
              className={
                isFrensicAlert(alert)
                  ? 'border-2 border-risk-critical shadow-lg'
                  : ''
              }
            >
              <CardBody className="space-y-3">
                {/* Header */}
                <div className="flex items-start gap-3">
                  <span className="text-2xl">{getSeverityIcon(alert.severity)}</span>
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900">{alert.title}</h3>
                    <p className="text-xs text-gray-500 mt-1">
                      {formatRelative(alert.createdAt)}
                    </p>
                  </div>
                </div>

                {/* Message */}
                <p className="text-sm text-gray-700">{alert.message}</p>

                {/* Severity & Type */}
                <div className="flex gap-2">
                  <Badge variant={alert.severity as any}>
                    {alert.severity}
                  </Badge>
                  {isFrensicAlert(alert) && (
                    <Badge variant="critical">Forensic</Badge>
                  )}
                </div>

                {/* Actions */}
                <div className="flex gap-2 pt-2 border-t border-gray-100">
                  <Button
                    size="sm"
                    variant="ghost"
                    className="flex-1 flex items-center justify-center gap-1"
                    onClick={() => {
                      if (!alert.riskId) {
                        addToast('This alert is not linked to a risk', 'warning')
                        return
                      }
                      navigate(`/risks/${alert.riskId}`)
                    }}
                  >
                    <Eye size={16} />
                    View Risk
                  </Button>
                  <Button
                    size="sm"
                    variant="ghost"
                    className="flex-1 flex items-center justify-center gap-1 text-gray-600 hover:text-risk-critical"
                    isLoading={dismissAlert.isPending}
                    onClick={async () => {
                      try {
                        await dismissAlert.mutateAsync(alert.id)
                        addToast('Alert dismissed', 'success')
                        refetch()
                      } catch {
                        addToast('Failed to dismiss alert', 'error')
                      }
                    }}
                  >
                    <Trash2 size={16} />
                    Dismiss
                  </Button>
                </div>
              </CardBody>
            </Card>
          ))}
        </div>
      ) : (
        <Card>
          <CardBody className="py-12 text-center">
            <AlertCircle size={48} className="mx-auto text-gray-300 mb-4" />
            <p className="text-gray-600">No alerts for this filter</p>
          </CardBody>
        </Card>
      )}
    </div>
  )
}
