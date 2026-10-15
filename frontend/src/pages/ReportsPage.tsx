import { useState } from 'react'
import { FileText, Lock, Download, Calendar } from 'lucide-react'
import { useAuth } from '@/context/AuthContext'
import { useDepartments } from '@/hooks/useDepartments'
import { useToast } from '@/context/ToastContext'
import {
  reportApi,
  getFilenameFromResponse,
  downloadBlob,
  formatDateForFilename,
} from '@/api/reportApi'
import { Button } from '@/components/ui/Button'
import { Card, CardHeader, CardBody } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'

interface RecentReport {
  id: string
  type: string
  date: string
  format: string
  timestamp: number
}

export const ReportsPage = () => {
  const { user } = useAuth()
  const { data: departments } = useDepartments()
  const { addToast } = useToast()

  // Form state for Department Report
  const [deptReportState, setDeptReportState] = useState({
    departmentId: user?.departmentId || '',
    startDate: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000)
      .toISOString()
      .split('T')[0],
    endDate: new Date().toISOString().split('T')[0],
    format: 'pdf' as 'pdf' | 'excel',
    loading: false,
  })

  // Form state for Forensic Report
  const [forensicState, setForensicState] = useState({
    startDate: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000)
      .toISOString()
      .split('T')[0],
    endDate: new Date().toISOString().split('T')[0],
    loading: false,
  })

  // Exec Summary loading
  const [execLoading, setExecLoading] = useState(false)

  // Institutional loading
  const [instLoading, setInstLoading] = useState(false)

  // Recent reports from localStorage
  const [recentReports, setRecentReports] = useState<RecentReport[]>(() => {
    const stored = localStorage.getItem('recentReports')
    return stored ? JSON.parse(stored) : []
  })

  // Save report to history
  const addToHistory = (type: string, format: string) => {
    const newReport: RecentReport = {
      id: Date.now().toString(),
      type,
      format,
      date: new Date().toLocaleDateString(),
      timestamp: Date.now(),
    }
    const updated = [newReport, ...recentReports].slice(0, 5)
    setRecentReports(updated)
    localStorage.setItem('recentReports', JSON.stringify(updated))
  }

  const toApiDate = (value?: string): string | undefined => {
    if (!value) return undefined
    const raw = value.trim()
    if (!raw) return undefined
    if (/^\d{4}-\d{2}-\d{2}$/.test(raw)) return raw
    const m = raw.match(/^(\d{1,2})\/(\d{1,2})\/(\d{4})$/)
    if (m) {
      const [, dd, mm, yyyy] = m
      return `${yyyy}-${mm.padStart(2, '0')}-${dd.padStart(2, '0')}`
    }
    return raw
  }

  // Department Report
  const handleGenerateDeptReport = async () => {
    if (!deptReportState.departmentId) {
      addToast('Please select a department', 'warning')
      return
    }

    setDeptReportState((prev) => ({ ...prev, loading: true }))
    try {
      const { blob, headers } = await reportApi.generateDepartmentReport(
        deptReportState.departmentId,
        deptReportState.format,
        toApiDate(deptReportState.startDate),
        toApiDate(deptReportState.endDate)
      )

      const defaultExt = deptReportState.format === 'excel' ? 'xlsx' : 'pdf'
      const fallback = `dept_risk_report_${formatDateForFilename()}.${defaultExt}`
      const filename = getFilenameFromResponse({ headers }, fallback)
      downloadBlob(blob, filename)
      addToHistory('Department Risk Report', deptReportState.format)
      addToast('Report downloaded successfully', 'success')
    } catch (error) {
      addToast('Report generation failed — please try again', 'error')
    } finally {
      setDeptReportState((prev) => ({ ...prev, loading: false }))
    }
  }

  // Institutional Report
  const handleGenerateInstitutional = async () => {
    setInstLoading(true)
    try {
      const blob = await reportApi.generateInstitutionalReport()
      const filename = `institutional_report_${formatDateForFilename()}.pdf`
      downloadBlob(blob, filename)
      addToHistory('Institutional Report', 'pdf')
      addToast('Report downloaded successfully', 'success')
    } catch (error) {
      addToast('Report generation failed — please try again', 'error')
    } finally {
      setInstLoading(false)
    }
  }

  // Executive Summary
  const handleGenerateExecutive = async () => {
    setExecLoading(true)
    try {
      const blob = await reportApi.generateExecutiveSummary()
      const filename = `executive_summary_${formatDateForFilename()}.pdf`
      downloadBlob(blob, filename)
      addToHistory('Executive Summary', 'pdf')
      addToast('Report downloaded successfully', 'success')
    } catch (error) {
      addToast('Report generation failed — please try again', 'error')
    } finally {
      setExecLoading(false)
    }
  }

  // Forensic Audit Report
  const handleGenerateForensic = async () => {
    setForensicState((prev) => ({ ...prev, loading: true }))
    try {
      const blob = await reportApi.generateForensicAudit(
        toApiDate(forensicState.startDate),
        toApiDate(forensicState.endDate)
      )
      const filename = `forensic_audit_${formatDateForFilename()}.xlsx`
      downloadBlob(blob, filename)
      addToHistory('Forensic Audit Report', 'excel')
      addToast('Report downloaded successfully', 'success')
    } catch (error) {
      addToast('Report generation failed — please try again', 'error')
    } finally {
      setForensicState((prev) => ({ ...prev, loading: false }))
    }
  }

  const canAccessDeptReport =
    user?.role === 'dept_user' ||
    user?.role === 'data_clerk' ||
    user?.role === 'risk_clerk' ||
    user?.role === 'department_head' ||
    user?.role === 'risk_officer' ||
    user?.role === 'risk_manager' ||
    user?.role === 'admin'

  const canAccessInstitutional =
    user?.role === 'risk_officer' ||
    user?.role === 'risk_manager' ||
    user?.role === 'executive' ||
    user?.role === 'admin'

  const canAccessExecutive =
    user?.role === 'executive' ||
    user?.role === 'risk_officer' ||
    user?.role === 'risk_manager' ||
    user?.role === 'admin'

  const canAccessForensic =
    user?.role === 'risk_officer' ||
    user?.role === 'risk_manager' ||
    user?.role === 'department_head' ||
    user?.role === 'admin'

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Reports</h1>
        <p className="text-gray-600 mt-1">Generate and download risk reports</p>
      </div>

      {/* Report Cards Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 1. Department Risk Report */}
        <Card className={!canAccessDeptReport ? 'opacity-60' : ''}>
          <CardHeader className="flex items-start justify-between">
            <div className="flex items-center gap-2">
              <FileText size={20} className="text-brand-mid" />
              <h2 className="font-semibold text-gray-900">Department Risk Report</h2>
            </div>
            {!canAccessDeptReport && <Lock size={20} className="text-gray-400" />}
          </CardHeader>
          <CardBody className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-900 mb-2">
                Department
              </label>
              <select
                value={deptReportState.departmentId}
                onChange={(e) =>
                  setDeptReportState((prev) => ({
                    ...prev,
                    departmentId: e.target.value,
                  }))
                }
                disabled={!canAccessDeptReport}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-brand-mid focus:border-transparent outline-none disabled:bg-gray-100"
              >
                <option value="">Select a department</option>
                {departments?.map((dept) => (
                  <option key={dept.id} value={dept.id}>
                    {dept.name}
                  </option>
                ))}
              </select>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-sm font-medium text-gray-900 mb-2">
                  Start Date
                </label>
                <input
                  type="date"
                  value={deptReportState.startDate}
                  onChange={(e) =>
                    setDeptReportState((prev) => ({
                      ...prev,
                      startDate: e.target.value,
                    }))
                  }
                  disabled={!canAccessDeptReport}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-brand-mid focus:border-transparent outline-none disabled:bg-gray-100"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-900 mb-2">
                  End Date
                </label>
                <input
                  type="date"
                  value={deptReportState.endDate}
                  onChange={(e) =>
                    setDeptReportState((prev) => ({
                      ...prev,
                      endDate: e.target.value,
                    }))
                  }
                  disabled={!canAccessDeptReport}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-brand-mid focus:border-transparent outline-none disabled:bg-gray-100"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-900 mb-2">
                Format
              </label>
              <div className="flex gap-2">
                {(['pdf', 'excel'] as const).map((fmt) => (
                  <button
                    key={fmt}
                    onClick={() =>
                      setDeptReportState((prev) => ({ ...prev, format: fmt }))
                    }
                    disabled={!canAccessDeptReport}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                      deptReportState.format === fmt
                        ? 'bg-brand-mid text-white'
                        : 'bg-gray-200 text-gray-900 hover:bg-gray-300'
                    } disabled:opacity-50`}
                  >
                    {fmt.toUpperCase()}
                  </button>
                ))}
              </div>
            </div>

            <Button
              onClick={handleGenerateDeptReport}
              isLoading={deptReportState.loading}
              disabled={!canAccessDeptReport}
              className="w-full"
            >
              {deptReportState.loading ? 'Generating...' : 'Generate Report'}
            </Button>

            {!canAccessDeptReport && (
              <p className="text-xs text-gray-600 text-center">
                Only dept_user, risk_officer, or admin can access
              </p>
            )}
          </CardBody>
        </Card>

        {/* 2. Institutional Report */}
        <Card className={!canAccessInstitutional ? 'opacity-60' : ''}>
          <CardHeader className="flex items-start justify-between">
            <div className="flex items-center gap-2">
              <FileText size={20} className="text-brand-mid" />
              <h2 className="font-semibold text-gray-900">Institutional Report</h2>
            </div>
            {!canAccessInstitutional && <Lock size={20} className="text-gray-400" />}
          </CardHeader>
          <CardBody className="space-y-4">
            <p className="text-sm text-gray-600">
              Institution-wide risk posture, aggregate metrics, and cross-department analysis.
            </p>
            <div className="p-3 bg-blue-50 rounded-lg text-sm text-blue-900">
              <p className="font-medium">Format: PDF</p>
              <p className="text-xs mt-1">Full institutional overview with executive summary</p>
            </div>
            <Button
              onClick={handleGenerateInstitutional}
              isLoading={instLoading}
              disabled={!canAccessInstitutional}
              className="w-full"
            >
              {instLoading ? 'Generating...' : 'Generate Institutional Report'}
            </Button>
            {!canAccessInstitutional && (
              <p className="text-xs text-gray-600 text-center">
                Only risk_officer or admin can access
              </p>
            )}
          </CardBody>
        </Card>

        {/* 3. Executive Summary */}
        <Card className={!canAccessExecutive ? 'opacity-60' : ''}>
          <CardHeader className="flex items-start justify-between">
            <div className="flex items-center gap-2">
              <FileText size={20} className="text-brand-mid" />
              <h2 className="font-semibold text-gray-900">Executive Summary</h2>
            </div>
            {!canAccessExecutive && <Lock size={20} className="text-gray-400" />}
          </CardHeader>
          <CardBody className="space-y-4">
            <p className="text-sm text-gray-600">
              Real-time snapshot of critical risks, key metrics, and board-level insights.
            </p>
            <div className="p-3 bg-green-50 rounded-lg text-sm text-green-900">
              <p className="font-medium">Format: PDF (Current Data)</p>
              <p className="text-xs mt-1">Automatically includes latest data</p>
            </div>
            <Button
              onClick={handleGenerateExecutive}
              isLoading={execLoading}
              disabled={!canAccessExecutive}
              className="w-full flex items-center justify-center gap-2"
            >
              <Download size={16} />
              {execLoading ? 'Generating...' : 'Download Executive Summary (PDF)'}
            </Button>
            {!canAccessExecutive && (
              <p className="text-xs text-gray-600 text-center">
                Only executive, risk_officer, or admin can access
              </p>
            )}
          </CardBody>
        </Card>

        {/* 4. Forensic Audit Report */}
        <Card className={!canAccessForensic ? 'opacity-60' : ''}>
          <CardHeader className="flex items-start justify-between">
            <div className="flex items-center gap-2">
              <FileText size={20} className="text-risk-critical" />
              <h2 className="font-semibold text-gray-900">Forensic Audit Report</h2>
            </div>
            {!canAccessForensic && <Lock size={20} className="text-gray-400" />}
          </CardHeader>
          <CardBody className="space-y-4">
            <div className="p-3 bg-red-50 rounded-lg">
              <Badge variant="critical">Admin & Risk Officer Only</Badge>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-sm font-medium text-gray-900 mb-2">
                  Start Date
                </label>
                <input
                  type="date"
                  value={forensicState.startDate}
                  onChange={(e) =>
                    setForensicState((prev) => ({
                      ...prev,
                      startDate: e.target.value,
                    }))
                  }
                  disabled={!canAccessForensic}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-brand-mid focus:border-transparent outline-none disabled:bg-gray-100"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-900 mb-2">
                  End Date
                </label>
                <input
                  type="date"
                  value={forensicState.endDate}
                  onChange={(e) =>
                    setForensicState((prev) => ({
                      ...prev,
                      endDate: e.target.value,
                    }))
                  }
                  disabled={!canAccessForensic}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-brand-mid focus:border-transparent outline-none disabled:bg-gray-100"
                />
              </div>
            </div>

            <div className="p-3 bg-gray-50 rounded-lg text-sm text-gray-600">
              <p className="font-medium text-gray-900">Format: Excel</p>
              <p className="text-xs mt-1">Detailed forensic anomalies, suppressions, and audit trail</p>
            </div>

            <Button
              onClick={handleGenerateForensic}
              isLoading={forensicState.loading}
              disabled={!canAccessForensic}
              variant={canAccessForensic ? 'primary' : 'secondary'}
              className="w-full flex items-center justify-center gap-2"
            >
              <Download size={16} />
              {forensicState.loading ? 'Generating...' : 'Download Forensic Audit (Excel)'}
            </Button>

            {!canAccessForensic && (
              <p className="text-xs text-gray-600 text-center">
                Only risk_officer or admin can access
              </p>
            )}
          </CardBody>
        </Card>
      </div>

      {/* Recent Reports Panel */}
      {recentReports.length > 0 && (
        <Card>
          <CardHeader>
            <h2 className="font-semibold text-gray-900">Recent Downloads</h2>
            <p className="text-xs text-gray-500 mt-1">Last 5 reports</p>
          </CardHeader>
          <CardBody>
            <div className="space-y-2">
              {recentReports.map((report) => (
                <div
                  key={report.id}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <FileText size={18} className="text-brand-mid" />
                    <div>
                      <p className="text-sm font-medium text-gray-900">{report.type}</p>
                      <p className="text-xs text-gray-600">
                        {report.date} • {report.format.toUpperCase()}
                      </p>
                    </div>
                  </div>
                  <Button
                    size="sm"
                    variant="ghost"
                    className="flex items-center gap-1"
                    title="Re-download this report"
                  >
                    <Download size={16} />
                    Re-download
                  </Button>
                </div>
              ))}
            </div>
          </CardBody>
        </Card>
      )}
    </div>
  )
}
