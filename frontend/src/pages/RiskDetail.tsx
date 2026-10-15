import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { formatDate, getDaysSince } from '@/utils/dateFormat'
import { getRiskColor, getRiskTextClass } from '@/utils/riskColor'
import { useRiskDetail, useApproveRisk, useRejectRisk, useDeleteRisk } from '@/hooks/useRisks'
import { mitigationApi } from '@/api/mitigationApi'
import { useAuth } from '@/context/AuthContext'
import { useToast } from '@/context/ToastContext'
import { Card, CardHeader, CardBody } from '@/components/ui/Card'
import { Badge, StatusBadge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Slider } from '@/components/ui/Slider'
import { Spinner } from '@/components/ui/Spinner'
import { Edit, Link as LinkIcon, Trash2, Plus, CheckCircle, XCircle } from 'lucide-react'

export const RiskDetail = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { user } = useAuth()
  const { addToast } = useToast()
  const { data: detail, isLoading, error } = useRiskDetail(id || '')

  const { data: mitigations, isLoading: mitigationsLoading } = useQuery({
    queryKey: ['mitigations', id],
    queryFn: () => mitigationApi.getMitigationsForRisk(id!),
    enabled: !!id,
  })

  const approveRisk = useApproveRisk()
  const rejectRisk = useRejectRisk()
  const deleteRisk = useDeleteRisk()

  const [activeTab, setActiveTab] = useState<'overview' | 'audit'>('overview')
  const [showApprovalModal, setShowApprovalModal] = useState<'approve' | 'reject' | null>(null)
  const [justification, setJustification] = useState('')

  if (!id) return <div className="text-red-600">Risk ID missing</div>
  if (isLoading) return <Spinner />
  if (error || !detail) return <div className="text-red-600">Failed to load risk</div>

  const { risk, linkedRisks, auditTrail, recommendations } = detail
  const daysOpen = getDaysSince(risk.createdAt)

  const canApprove =
    risk.status === 'pending_approval' &&
    (user?.role === 'risk_officer' || user?.role === 'admin')

  const handleApprovalSubmit = async () => {
    if (!justification.trim()) return
    try {
      if (showApprovalModal === 'approve') {
        await approveRisk.mutateAsync({ id: risk.id, justification })
      } else {
        await rejectRisk.mutateAsync({ id: risk.id, justification })
      }
      setShowApprovalModal(null)
      setJustification('')
    } catch {
      // error handled by axios interceptor toast
    }
  }

  const handleDeleteRisk = async () => {
    if (!window.confirm('Are you sure you want to delete this risk?')) return
    try {
      await deleteRisk.mutateAsync(risk.id)
      addToast('Risk deleted successfully', 'success')
      navigate('/risks')
    } catch {
      addToast('Failed to delete risk', 'error')
    }
  }

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">{risk.title}</h1>
          <div className="flex items-center gap-3 mt-3 flex-wrap">
            <Badge variant={risk.severity}>{risk.severity}</Badge>
            <StatusBadge status={risk.status} />
            <span className="text-sm text-gray-600">Category: {risk.category}</span>
            <span className="text-sm text-gray-600">Department: {risk.departmentId}</span>
            <span className="text-sm text-gray-600">{daysOpen}d open</span>
          </div>
        </div>
        <div className="flex gap-2 flex-wrap">
          {canApprove && (
            <>
              <Button
                variant="primary"
                size="sm"
                onClick={() => setShowApprovalModal('approve')}
                className="bg-green-600 hover:bg-green-700"
              >
                <CheckCircle size={16} />
                Approve
              </Button>
              <Button
                variant="primary"
                size="sm"
                onClick={() => setShowApprovalModal('reject')}
                className="bg-red-600 hover:bg-red-700"
              >
                <XCircle size={16} />
                Reject
              </Button>
            </>
          )}
          <Button variant="secondary" size="sm" onClick={() => navigate(`/risks/${risk.id}/edit`)}>
            <Edit size={16} />
            Edit
          </Button>
          <Button variant="secondary" size="sm" isLoading={deleteRisk.isPending} onClick={handleDeleteRisk}>
            <Trash2 size={16} />
            Delete
          </Button>
        </div>
      </div>

      {/* Approval Modal */}
      {showApprovalModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm">
          <div className="bg-white rounded-xl shadow-xl p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              {showApprovalModal === 'approve' ? 'Approve Risk' : 'Reject Risk'}
            </h3>
            <p className="text-sm text-gray-600 mb-4">
              Provide a justification for {showApprovalModal === 'approve' ? 'approving' : 'rejecting'} this risk.
            </p>
            <textarea
              rows={4}
              placeholder="Enter justification..."
              value={justification}
              onChange={(e) => setJustification(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-mid focus:border-transparent outline-none text-sm mb-4"
            />
            <div className="flex gap-3 justify-end">
              <Button
                variant="secondary"
                size="sm"
                onClick={() => { setShowApprovalModal(null); setJustification('') }}
              >
                Cancel
              </Button>
              <Button
                variant="primary"
                size="sm"
                disabled={!justification.trim() || approveRisk.isPending || rejectRisk.isPending}
                isLoading={approveRisk.isPending || rejectRisk.isPending}
                onClick={handleApprovalSubmit}
                className={showApprovalModal === 'approve' ? 'bg-green-600 hover:bg-green-700' : 'bg-red-600 hover:bg-red-700'}
              >
                {showApprovalModal === 'approve' ? 'Approve' : 'Reject'}
              </Button>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Score Card */}
          <Card>
            <CardHeader>
              <h2 className="font-semibold text-gray-900">Risk Score</h2>
            </CardHeader>
            <CardBody className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-2">Overall Risk Score</p>
                <p className={`text-5xl font-bold ${getRiskTextClass(risk.severity)}`}>
                  {risk.riskScore}
                </p>
              </div>
              <div
                className="w-24 h-24 rounded-full flex items-center justify-center text-white font-bold text-2xl"
                style={{ backgroundColor: getRiskColor(risk.severity) }}
              >
                {risk.riskScore}
              </div>
            </CardBody>
          </Card>

          {/* Score Breakdown */}
          <Card>
            <CardHeader>
              <h2 className="font-semibold text-gray-900">Score Breakdown</h2>
              <p className="text-xs text-gray-500">L: Likelihood, I: Impact, V: Velocity, D: Detectability</p>
            </CardHeader>
            <CardBody className="space-y-6">
              <Slider label="Likelihood (L)" value={risk.probability} onChange={() => {}} tooltip="" readOnly />
              <Slider label="Impact (I)" value={risk.impact} onChange={() => {}} tooltip="" readOnly />
              <Slider label="Velocity (V)" value={risk.velocity ?? 3} onChange={() => {}} tooltip="" readOnly />
              <Slider label="Detectability (D)" value={risk.detectability ?? 3} onChange={() => {}} tooltip="" readOnly />
            </CardBody>
          </Card>

          {/* Description */}
          <Card>
            <CardHeader>
              <h2 className="font-semibold text-gray-900">Description</h2>
            </CardHeader>
            <CardBody>
              <p className="text-gray-700 leading-relaxed">{risk.description}</p>
            </CardBody>
          </Card>

          {/* Review Info (if reviewed) */}
          {risk.reviewJustification && (
            <Card>
              <CardHeader>
                <h2 className="font-semibold text-gray-900">Review Decision</h2>
              </CardHeader>
              <CardBody className="space-y-2">
                <div className="flex items-center gap-2">
                  <StatusBadge status={risk.status} />
                  {risk.reviewedAt && (
                    <span className="text-xs text-gray-500">on {formatDate(risk.reviewedAt)}</span>
                  )}
                </div>
                <p className="text-sm text-gray-700">{risk.reviewJustification}</p>
              </CardBody>
            </Card>
          )}

          {/* Tabs */}
          <div className="border-b border-gray-200">
            <div className="flex gap-8">
              <button
                onClick={() => setActiveTab('overview')}
                className={`px-4 py-4 font-medium border-b-2 transition-colors ${
                  activeTab === 'overview'
                    ? 'border-brand-mid text-brand-mid'
                    : 'border-transparent text-gray-600 hover:text-gray-900'
                }`}
              >
                Actions & Recommendations
              </button>
              <button
                onClick={() => setActiveTab('audit')}
                className={`px-4 py-4 font-medium border-b-2 transition-colors ${
                  activeTab === 'audit'
                    ? 'border-brand-mid text-brand-mid'
                    : 'border-transparent text-gray-600 hover:text-gray-900'
                }`}
              >
                Audit Trail
              </button>
            </div>
          </div>

          {activeTab === 'overview' && (
            <div className="space-y-6">
              {/* Smart Recommendations */}
              <Card>
                <CardHeader>
                  <h2 className="font-semibold text-gray-900">Smart Recommendations</h2>
                </CardHeader>
                <CardBody>
                  {recommendations.length > 0 ? (
                    <ul className="space-y-3">
                      {recommendations.map((rec, idx) => (
                        <li key={idx} className="flex gap-3 text-gray-700">
                          <span className="text-brand-mid font-bold mt-1">•</span>
                          <span>{rec}</span>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-gray-500 text-center py-4">No recommendations available</p>
                  )}
                </CardBody>
              </Card>

              {/* Mitigation Actions */}
              <Card>
                <CardHeader className="flex items-center justify-between">
                  <h2 className="font-semibold text-gray-900">Mitigation Actions</h2>
                  <Button size="sm" variant="primary">
                    <Plus size={16} /> Add Mitigation
                  </Button>
                </CardHeader>
                <CardBody>
                  {mitigationsLoading ? (
                    <div className="flex justify-center py-6"><Spinner /></div>
                  ) : mitigations && mitigations.length > 0 ? (
                    <div className="space-y-4">
                      {mitigations.map((m) => (
                        <div key={m.id} className="border border-gray-200 rounded-lg p-4">
                          <div className="flex items-start justify-between gap-4 mb-2">
                            <div>
                              <h3 className="font-medium text-gray-900">{m.title}</h3>
                              <p className="text-sm text-gray-600 mt-1">{m.description}</p>
                            </div>
                            <Badge variant={m.status === 'completed' ? 'success' : m.status === 'in_progress' ? 'warning' : 'default'}>
                              {m.status === 'completed' ? 'Completed' : m.status === 'in_progress' ? 'In-Progress' : 'Not Started'}
                            </Badge>
                          </div>
                          <div className="flex justify-between text-xs text-gray-600 mt-3">
                            <span>Owner: {m.owner}</span>
                            <span>Due: {formatDate(m.dueDate)}</span>
                            <span>Effectiveness: {m.effectiveness}%</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-gray-500 text-center py-8">No mitigations yet</p>
                  )}
                </CardBody>
              </Card>
            </div>
          )}

          {activeTab === 'audit' && (
            <Card>
              <CardHeader>
                <h2 className="font-semibold text-gray-900">Change History</h2>
              </CardHeader>
              <CardBody>
                {auditTrail.length > 0 ? (
                  <div className="space-y-8 relative">
                    <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-gray-200" />
                    {auditTrail.map((entry, idx) => (
                      <div key={entry.id || idx} className="relative pl-16">
                        <div className="absolute left-0 w-12 h-12 bg-white border-4 border-brand-mid rounded-full flex items-center justify-center -translate-x-6">
                          <div className="w-2 h-2 bg-brand-mid rounded-full" />
                        </div>
                        <div>
                          <div className="flex items-center gap-2 mb-1">
                            <span className="font-medium text-gray-900">
                              {entry.user?.full_name || entry.user?.email || 'System'}
                            </span>
                            <span className="text-xs text-gray-500">{entry.action}</span>
                          </div>
                          {Object.keys(entry.previousValues).length > 0 && (
                            <div className="text-sm text-gray-600 mb-1 space-y-1">
                              {Object.keys(entry.newValues).map((key) => (
                                <p key={key}>
                                  <span className="font-medium">{key}:</span>{' '}
                                  <span className="font-mono bg-red-50 px-1">
                                    {JSON.stringify(entry.previousValues[key])}
                                  </span>{' '}
                                  →{' '}
                                  <span className="font-mono bg-green-50 px-1">
                                    {JSON.stringify(entry.newValues[key])}
                                  </span>
                                </p>
                              ))}
                            </div>
                          )}
                          <p className="text-xs text-gray-500">{formatDate(entry.changedAt)}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500 text-center py-8">No change history available</p>
                )}
              </CardBody>
            </Card>
          )}
        </div>

        {/* Sidebar */}
        <div className="lg:col-span-1 space-y-6">
          {/* Status Card */}
          <Card>
            <CardHeader>
              <h2 className="font-semibold text-gray-900">Status</h2>
            </CardHeader>
            <CardBody className="space-y-4">
              <div>
                <p className="text-xs text-gray-600 mb-1">Current Status</p>
                <StatusBadge status={risk.status} />
              </div>
              {risk.riskType && (
                <div>
                  <p className="text-xs text-gray-600 mb-1">Risk Type</p>
                  <p className="text-sm font-medium text-gray-900">{risk.riskType}</p>
                </div>
              )}
              <div>
                <p className="text-xs text-gray-600 mb-1">Owner</p>
                <p className="text-sm font-medium text-gray-900">{risk.owner}</p>
              </div>
              <div>
                <p className="text-xs text-gray-600 mb-1">Created</p>
                <p className="text-sm text-gray-900">{formatDate(risk.createdAt)}</p>
              </div>
              <div>
                <p className="text-xs text-gray-600 mb-1">Last Updated</p>
                <p className="text-sm text-gray-900">{formatDate(risk.updatedAt)}</p>
              </div>
            </CardBody>
          </Card>

          {/* Linked Risks */}
          <Card>
            <CardHeader>
              <h2 className="font-semibold text-gray-900 flex items-center gap-2">
                <LinkIcon size={16} />
                Linked Risks
              </h2>
            </CardHeader>
            <CardBody>
              {linkedRisks.length > 0 ? (
                <div className="space-y-2">
                  {linkedRisks.map((linked) => (
                    <div
                      key={linked.id}
                      onClick={() => navigate(`/risks/${linked.id}`)}
                      className="p-2 border border-gray-200 rounded hover:bg-gray-50 cursor-pointer"
                    >
                      <p className="text-sm font-medium text-brand-mid hover:underline">{linked.title}</p>
                      <div className="flex items-center gap-2 mt-1">
                        <Badge variant={linked.severity}>{linked.severity}</Badge>
                        <span className="text-xs text-gray-600">Score: {linked.riskScore}</span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 text-center py-4">No linked risks</p>
              )}
              <Button variant="ghost" size="sm" className="w-full mt-3">
                Link Another Risk
              </Button>
            </CardBody>
          </Card>

          {/* Context Info */}
          <Card>
            <CardHeader>
              <h2 className="font-semibold text-gray-900">Quick Info</h2>
            </CardHeader>
            <CardBody className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Probability:</span>
                <span className="font-medium">{risk.probability}/5</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Impact:</span>
                <span className="font-medium">{risk.impact}/5</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Days Open:</span>
                <span className="font-medium">{daysOpen}</span>
              </div>
            </CardBody>
          </Card>
        </div>
      </div>
    </div>
  )
}
