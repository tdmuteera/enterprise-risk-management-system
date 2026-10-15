import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { ChevronDown, ChevronLeft, ChevronRight, Download } from 'lucide-react'
import { auditApi, AuditLogEntry } from '@/api/auditApi'
import { Button } from '@/components/ui/Button'
import { Card, CardHeader, CardBody } from '@/components/ui/Card'
import { Spinner } from '@/components/ui/Spinner'
import { formatDateTime } from '@/utils/dateFormat'

export const AuditTrail = () => {
  const [expandedRow, setExpandedRow] = useState<string | null>(null)
  const [filterUser, setFilterUser] = useState('')
  const [filterAction, setFilterAction] = useState('')
  const [dateFrom, setDateFrom] = useState('')
  const [dateTo, setDateTo] = useState('')
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)

  const queryParams = {
    user_filter: filterUser || undefined,
    action_filter: filterAction || undefined,
    start_date: dateFrom || undefined,
    end_date: dateTo || undefined,
    page,
    page_size: pageSize,
  }

  const { data, isLoading, error } = useQuery({
    queryKey: ['audit-logs', queryParams],
    queryFn: () => auditApi.getAuditLogs(queryParams),
  })

  const logs = data?.items ?? []
  const total = data?.total ?? 0
  const totalPages = Math.max(1, Math.ceil(total / pageSize))

  const changedFieldsFromEntry = (entry: AuditLogEntry): string[] => {
    const keys = new Set<string>()
    for (const k of Object.keys(entry.previous_values || {})) keys.add(k)
    for (const k of Object.keys(entry.new_values || {})) keys.add(k)
    return Array.from(keys)
  }

  const handleExport = () => {
    const csv = [
      ['Timestamp', 'User', 'Action', 'Risk', 'Changed Fields', 'IP Address'],
      ...logs.map((log) => [
        formatDateTime(log.changed_at),
        log.user?.email ?? 'Unknown',
        log.action,
        log.risk_title ?? log.risk_id,
        changedFieldsFromEntry(log).join('; '),
        log.ip_address ?? '',
      ]),
    ]
      .map((row) => row.map((cell) => `"${cell}"`).join(','))
      .join('\n')

    const blob = new Blob([csv], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `audit-trail-${new Date().toISOString().split('T')[0]}.csv`
    a.click()
    window.URL.revokeObjectURL(url)
  }

  const handleFilterApply = () => {
    setPage(1)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Audit Trail</h1>
          <p className="text-gray-600 mt-1">System-wide change history and event log</p>
        </div>
        <Button variant="secondary" onClick={handleExport} className="flex items-center gap-2">
          <Download size={16} />
          Export to Excel
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <h2 className="font-semibold text-gray-900">Filters</h2>
        </CardHeader>
        <CardBody>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-900 mb-2">User</label>
              <input
                type="text"
                placeholder="Filter by email..."
                value={filterUser}
                onChange={(e) => setFilterUser(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleFilterApply()}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-mid focus:border-transparent outline-none text-sm"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-900 mb-2">Action</label>
              <select
                value={filterAction}
                onChange={(e) => { setFilterAction(e.target.value); setPage(1) }}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-mid focus:border-transparent outline-none text-sm"
              >
                <option value="">All Actions</option>
                <option value="CREATE">Created</option>
                <option value="UPDATE">Updated</option>
                <option value="DELETE">Deleted</option>
                <option value="APPROVE">Approved</option>
                <option value="REJECT">Rejected</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-900 mb-2">From Date</label>
              <input
                type="date"
                value={dateFrom}
                onChange={(e) => { setDateFrom(e.target.value); setPage(1) }}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-mid focus:border-transparent outline-none text-sm"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-900 mb-2">To Date</label>
              <input
                type="date"
                value={dateTo}
                onChange={(e) => { setDateTo(e.target.value); setPage(1) }}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-mid focus:border-transparent outline-none text-sm"
              />
            </div>
          </div>
        </CardBody>
      </Card>

      {/* Audit Log Table */}
      <Card>
        <CardHeader>
          <h2 className="font-semibold text-gray-900">
            Change History ({total} records)
          </h2>
          <p className="text-xs text-gray-500 mt-1">Click rows to see detailed changes</p>
        </CardHeader>
        <CardBody>
          {isLoading ? (
            <div className="flex justify-center py-12">
              <Spinner />
            </div>
          ) : error ? (
            <p className="text-red-600 text-center py-8">Failed to load audit logs</p>
          ) : logs.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No audit log entries found</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-4 py-3 text-left font-medium w-8"></th>
                    <th className="px-4 py-3 text-left font-medium">Timestamp</th>
                    <th className="px-4 py-3 text-left font-medium">User</th>
                    <th className="px-4 py-3 text-left font-medium">Action</th>
                    <th className="px-4 py-3 text-left font-medium">Risk Affected</th>
                    <th className="px-4 py-3 text-left font-medium">Changed Fields</th>
                    <th className="px-4 py-3 text-left font-medium">IP Address</th>
                  </tr>
                </thead>
                <tbody>
                  {logs.map((log) => {
                    const fields = changedFieldsFromEntry(log)
                    const hasDetails =
                      Object.keys(log.previous_values || {}).length > 0 ||
                      Object.keys(log.new_values || {}).length > 0
                    return (
                      <tr
                        key={log.id}
                        className="border-b border-gray-200 hover:bg-gray-50 cursor-pointer transition-colors group"
                        onClick={() => hasDetails && setExpandedRow(expandedRow === log.id ? null : log.id)}
                      >
                        <td className="px-4 py-3">
                          {hasDetails && (
                            <ChevronDown
                              size={16}
                              className={`transition-transform ${expandedRow === log.id ? 'rotate-180' : ''}`}
                            />
                          )}
                        </td>
                        <td className="px-4 py-3 text-xs text-gray-600">
                          {formatDateTime(log.changed_at)}
                        </td>
                        <td className="px-4 py-3 font-medium text-gray-900">
                          {log.user?.full_name || log.user?.email || 'System'}
                        </td>
                        <td className="px-4 py-3">
                          <span className="px-2 py-1 bg-blue-100 text-blue-900 text-xs rounded-full">
                            {log.action}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-gray-900">
                          {log.risk_title || log.risk_id}
                        </td>
                        <td className="px-4 py-3 text-xs text-gray-600">
                          {fields.join(', ') || '—'}
                        </td>
                        <td className="px-4 py-3 text-xs text-gray-600 font-mono">
                          {log.ip_address ?? '—'}
                        </td>
                      </tr>
                    )
                  })}

                  {logs.map((log) =>
                    expandedRow === log.id &&
                    (Object.keys(log.previous_values || {}).length > 0 ||
                      Object.keys(log.new_values || {}).length > 0) ? (
                      <tr key={`${log.id}-detail`} className="bg-gray-50 border-b border-gray-200">
                        <td colSpan={7} className="px-4 py-4">
                          <div className="space-y-4">
                            <h4 className="font-semibold text-gray-900">Change Details</h4>
                            <div className="grid grid-cols-2 gap-4">
                              <div className="bg-red-50 p-4 rounded-lg">
                                <h5 className="font-medium text-gray-900 mb-2">Previous</h5>
                                <div className="space-y-2 font-mono text-sm">
                                  {Object.entries(log.previous_values || {}).map(([key, value]) => (
                                    <div key={key} className="text-red-900">
                                      <span className="text-gray-600">{key}:</span> {JSON.stringify(value)}
                                    </div>
                                  ))}
                                  {Object.keys(log.previous_values || {}).length === 0 && (
                                    <p className="text-gray-500 italic">No previous values</p>
                                  )}
                                </div>
                              </div>

                              <div className="bg-green-50 p-4 rounded-lg">
                                <h5 className="font-medium text-gray-900 mb-2">New</h5>
                                <div className="space-y-2 font-mono text-sm">
                                  {Object.entries(log.new_values || {}).map(([key, value]) => (
                                    <div key={key} className="text-green-900">
                                      <span className="text-gray-600">{key}:</span> {JSON.stringify(value)}
                                    </div>
                                  ))}
                                  {Object.keys(log.new_values || {}).length === 0 && (
                                    <p className="text-gray-500 italic">No new values</p>
                                  )}
                                </div>
                              </div>
                            </div>
                          </div>
                        </td>
                      </tr>
                    ) : null
                  )}
                </tbody>
              </table>
            </div>
          )}

          {/* Pagination */}
          <div className="mt-6 flex items-center justify-between border-t border-gray-200 pt-4">
            <div className="flex items-center gap-3">
              <p className="text-sm text-gray-600">
                Showing {Math.min((page - 1) * pageSize + 1, total)}–{Math.min(page * pageSize, total)} of {total} records
              </p>
              <select
                value={pageSize}
                onChange={(e) => { setPageSize(Number(e.target.value)); setPage(1) }}
                className="px-2 py-1 border border-gray-300 rounded text-sm"
              >
                <option value={10}>10 / page</option>
                <option value={20}>20 / page</option>
                <option value={50}>50 / page</option>
              </select>
            </div>
            <div className="flex gap-2">
              <Button
                size="sm"
                variant="secondary"
                disabled={page <= 1}
                onClick={() => setPage((p) => Math.max(1, p - 1))}
              >
                <ChevronLeft size={14} />
                Previous
              </Button>
              <span className="flex items-center text-sm text-gray-600 px-2">
                {page} / {totalPages}
              </span>
              <Button
                size="sm"
                variant="secondary"
                disabled={page >= totalPages}
                onClick={() => setPage((p) => p + 1)}
              >
                Next
                <ChevronRight size={14} />
              </Button>
            </div>
          </div>
        </CardBody>
      </Card>
    </div>
  )
}
