import { useState } from 'react'
import { Link } from 'react-router-dom'
import { ChevronLeft, ChevronRight, ArrowUpDown, Filter, X } from 'lucide-react'
import { useRisksPaginated, RiskFilters } from '@/hooks/useRisks'
import { useDepartments } from '@/hooks/useDepartments'
import { Card, CardBody } from '@/components/ui/Card'
import { Spinner } from '@/components/ui/Spinner'
import { Button } from '@/components/ui/Button'
import { StatusBadge } from '@/components/ui/Badge'
import { RiskCard } from '@/components/risk'

const CATEGORIES = ['Financial', 'HR', 'Academic', 'IT', 'Compliance', 'Operational', 'Reputational']
const STATUS_OPTIONS = [
  { value: 'Open', label: 'Open' },
  { value: 'Draft', label: 'Draft' },
  { value: 'Pending Approval', label: 'Pending Approval' },
  { value: 'Approved', label: 'Approved' },
  { value: 'Rejected', label: 'Rejected' },
  { value: 'In-Progress', label: 'In-Progress' },
  { value: 'Mitigated', label: 'Mitigated' },
  { value: 'Closed', label: 'Closed' },
  { value: 'Escalated', label: 'Escalated' },
]
const SORT_OPTIONS = [
  { value: 'created_at', label: 'Created Date' },
  { value: 'updated_at', label: 'Updated Date' },
  { value: 'normalised_score', label: 'Risk Score' },
  { value: 'title', label: 'Title' },
]
const PAGE_SIZES = [12, 24, 48]

export const RiskListPage = () => {
  const [category, setCategory] = useState('')
  const [status, setStatus] = useState('')
  const [departmentId, setDepartmentId] = useState('')
  const [sortBy, setSortBy] = useState('created_at')
  const [order, setOrder] = useState<'asc' | 'desc'>('desc')
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(12)
  const [showFilters, setShowFilters] = useState(false)

  const { data: departments } = useDepartments()

  const filters: RiskFilters = {
    ...(category && { category }),
    ...(status && { status }),
    ...(departmentId && { department_id: departmentId }),
    sort_by: sortBy,
    order,
    page,
    page_size: pageSize,
  }

  const { data, isLoading, error } = useRisksPaginated(filters)

  const risks = data?.risks ?? []
  const total = data?.total ?? 0
  const totalPages = Math.max(1, Math.ceil(total / pageSize))

  const activeFilterCount = [category, status, departmentId].filter(Boolean).length

  const clearFilters = () => {
    setCategory('')
    setStatus('')
    setDepartmentId('')
    setPage(1)
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Risks</h1>
          <p className="text-gray-600">Manage risks you are allowed to see</p>
        </div>
        <div className="flex items-center gap-3">
          <Button
            variant="secondary"
            size="sm"
            onClick={() => setShowFilters(!showFilters)}
            className="flex items-center gap-2"
          >
            <Filter size={16} />
            Filters
            {activeFilterCount > 0 && (
              <span className="ml-1 bg-brand-mid text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                {activeFilterCount}
              </span>
            )}
          </Button>
          <Link
            to="/risks/new"
            className="inline-flex items-center justify-center gap-2 rounded-lg bg-brand-mid px-4 py-2 text-base font-medium text-white transition-colors hover:bg-brand-dark"
          >
            + New Risk
          </Link>
        </div>
      </div>

      {/* Filters Panel */}
      {showFilters && (
        <Card>
          <CardBody>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-900 mb-1">Category</label>
                <select
                  value={category}
                  onChange={(e) => { setCategory(e.target.value); setPage(1) }}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-mid focus:border-transparent outline-none text-sm"
                >
                  <option value="">All Categories</option>
                  {CATEGORIES.map((c) => (
                    <option key={c} value={c}>{c}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-900 mb-1">Status</label>
                <select
                  value={status}
                  onChange={(e) => { setStatus(e.target.value); setPage(1) }}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-mid focus:border-transparent outline-none text-sm"
                >
                  <option value="">All Statuses</option>
                  {STATUS_OPTIONS.map((s) => (
                    <option key={s.value} value={s.value}>{s.label}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-900 mb-1">Department</label>
                <select
                  value={departmentId}
                  onChange={(e) => { setDepartmentId(e.target.value); setPage(1) }}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-mid focus:border-transparent outline-none text-sm"
                >
                  <option value="">All Departments</option>
                  {departments?.map((d) => (
                    <option key={d.id} value={d.id}>{d.name}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-900 mb-1">Sort By</label>
                <div className="flex gap-2">
                  <select
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value)}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-mid focus:border-transparent outline-none text-sm"
                  >
                    {SORT_OPTIONS.map((s) => (
                      <option key={s.value} value={s.value}>{s.label}</option>
                    ))}
                  </select>
                  <button
                    onClick={() => setOrder(order === 'asc' ? 'desc' : 'asc')}
                    className="px-2 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
                    title={order === 'asc' ? 'Ascending' : 'Descending'}
                  >
                    <ArrowUpDown size={16} className={order === 'asc' ? 'rotate-180' : ''} />
                  </button>
                </div>
              </div>

              <div className="flex items-end">
                {activeFilterCount > 0 && (
                  <Button variant="ghost" size="sm" onClick={clearFilters} className="flex items-center gap-1">
                    <X size={14} />
                    Clear Filters
                  </Button>
                )}
              </div>
            </div>
          </CardBody>
        </Card>
      )}

      {/* Content */}
      {isLoading ? (
        <div className="flex justify-center py-12"><Spinner /></div>
      ) : error ? (
        <div className="text-risk-critical text-center py-8">Failed to load risks</div>
      ) : risks.length > 0 ? (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {risks.map((risk) => (
              <Link
                key={risk.id}
                to={`/risks/${risk.id}`}
                className="block rounded-lg outline-none focus:ring-2 focus:ring-brand-mid focus:ring-offset-2"
              >
                <RiskCard risk={risk} />
              </Link>
            ))}
          </div>

          {/* Pagination */}
          <div className="flex items-center justify-between border-t border-gray-200 pt-4">
            <div className="flex items-center gap-3">
              <p className="text-sm text-gray-600">
                Showing {Math.min((page - 1) * pageSize + 1, total)}–{Math.min(page * pageSize, total)} of {total} risks
              </p>
              <select
                value={pageSize}
                onChange={(e) => { setPageSize(Number(e.target.value)); setPage(1) }}
                className="px-2 py-1 border border-gray-300 rounded text-sm"
              >
                {PAGE_SIZES.map((s) => (
                  <option key={s} value={s}>{s} / page</option>
                ))}
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
        </>
      ) : (
        <Card>
          <CardBody>
            <p className="text-center text-gray-500">No risks found</p>
          </CardBody>
        </Card>
      )}
    </div>
  )
}
