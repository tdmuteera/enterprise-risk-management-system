import { useState, useEffect } from 'react'
import { Bell, AlertCircle } from 'lucide-react'
import { useUnreadAlertCount, useAlerts } from '@/hooks/useAlerts'
import { useToast } from '@/context/ToastContext'
import { formatRelative } from '@/utils/dateFormat'
import { Badge } from '@/components/ui/Badge'

export const AlertsBell = () => {
  const { data: unreadCount } = useUnreadAlertCount()
  const { data: allAlerts } = useAlerts()
  const [isOpen, setIsOpen] = useState(false)
  const [hoveredAlert, setHoveredAlert] = useState<string | null>(null)
  const { addToast } = useToast()

  // Get last 5 alerts
  const recentAlerts = allAlerts?.slice(0, 5) ?? []

  const handleAlertHover = (alertId: string) => {
    setHoveredAlert(alertId)
    // Mark as read after 2 seconds of hover
    setTimeout(() => {
      if (hoveredAlert === alertId) {
        addToast('Alert marked as read', 'success')
        // In production, call markAlertAsRead.mutate(alertId)
      }
    }, 2000)
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'text-risk-critical'
      case 'high':
        return 'text-risk-high'
      case 'medium':
        return 'text-risk-medium'
      default:
        return 'text-gray-500'
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

  return (
    <div className="relative">
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="relative rounded-xl border border-slate-200/70 bg-surface-muted/80 p-2.5 text-slate-600 shadow-sm transition hover:border-slate-300 hover:bg-white hover:text-brand-dark"
      >
        <Bell size={20} />
        {unreadCount && unreadCount > 0 && (
          <span className="absolute top-1 right-1 w-5 h-5 bg-risk-critical text-white text-xs rounded-full flex items-center justify-center font-semibold">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {/* Dropdown */}
      {isOpen && (
        <>
          {/* Overlay */}
          <div
            className="fixed inset-0 z-40"
            onClick={() => setIsOpen(false)}
          />

          {/* Dropdown menu */}
          <div className="absolute right-0 z-50 mt-2 w-80 overflow-hidden rounded-2xl border border-slate-200/80 bg-white shadow-nav">
            {/* Header */}
            <div className="border-b border-slate-100 bg-surface-muted/50 px-4 py-3">
              <h3 className="font-display text-base font-semibold text-slate-900">Alerts</h3>
              <p className="text-xs text-gray-500 mt-1">
                {unreadCount ?? 0} unread • Last 5 shown
              </p>
            </div>

            {/* Alerts list */}
            <div className="max-h-96 overflow-y-auto">
              {recentAlerts.length > 0 ? (
                recentAlerts.map((alert) => (
                  <div
                    key={alert.id}
                    className={`px-4 py-3 border-b border-gray-100 last:border-b-0 hover:bg-gray-50 transition-colors cursor-pointer ${
                      !alert.read ? 'bg-blue-50' : ''
                    }`}
                    onMouseEnter={() => handleAlertHover(alert.id)}
                  >
                    <div className="flex gap-3">
                      <span className="text-lg">{getSeverityIcon(alert.severity)}</span>
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-900">{alert.title}</p>
                        <p className="text-xs text-gray-600 mt-1 line-clamp-2">
                          {alert.message}
                        </p>
                        <div className="flex items-center gap-2 mt-2">
                          <Badge variant={alert.severity as any}>
                            {alert.severity}
                          </Badge>
                          <span className="text-xs text-gray-500">
                            {formatRelative(alert.createdAt)}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="px-4 py-8 text-center text-gray-500 text-sm">
                  No recent alerts
                </div>
              )}
            </div>

            {/* Footer */}
            <div className="px-4 py-3 border-t border-gray-200 bg-gray-50">
              <a
                href="/alerts"
                className="text-sm font-medium text-brand-mid hover:text-brand-dark transition-colors"
              >
                View All Alerts →
              </a>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
