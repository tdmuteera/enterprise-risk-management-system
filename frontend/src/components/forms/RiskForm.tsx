import { useEffect, useState } from 'react'
import { isAxiosError } from 'axios'
import { useNavigate, useParams } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { riskFormSchema, RiskFormData, calculateRiskScore } from '@/forms/riskSchema'
import { useDepartments } from '@/hooks/useDepartments'
import { useRiskById, useCreateRisk, useUpdateRisk } from '@/hooks/useRisks'
import { useAuth } from '@/context/AuthContext'
import { Button } from '@/components/ui/Button'
import { Card, CardHeader, CardBody } from '@/components/ui/Card'
import { Alert } from '@/components/ui/Alert'
import { Slider, ScorePreview } from '@/components/ui/Slider'
import { Spinner } from '@/components/ui/Spinner'
const CATEGORIES = ['Financial', 'HR', 'Academic', 'IT', 'Compliance', 'Operational', 'Reputational']
const STATUSES = ['Draft', 'Open', 'In-Progress', 'Mitigated', 'Closed', 'Escalated', 'Pending Approval', 'Approved', 'Rejected']

export const RiskForm = () => {
  const navigate = useNavigate()
  const { id } = useParams<{ id: string }>()
  const { user } = useAuth()
  const { data: departments } = useDepartments()
  const { data: riskData, isLoading: riskLoading } = useRiskById(id || '')
  const createRisk = useCreateRisk()
  const updateRisk = useUpdateRisk()

  const [submitError, setSubmitError] = useState<string | null>(null)

  // Load initial data if editing
  const isEditing = !!id
  const initialData = riskData
  const isDeptScopedUser = ['dept_user', 'data_clerk', 'risk_clerk'].includes(user?.role || '')

  const deptCategoryByCode: Record<string, RiskFormData['category']> = {
    FIN: 'Financial',
    HR: 'HR',
    ACAD: 'Academic',
    IT: 'IT',
    SA: 'Operational',
    ENG: 'Operational',
    AHS: 'Operational',
  }

  const currentDept = departments?.find((d) => d.id === (user?.departmentId || user?.department_id))
  const defaultDeptCategory =
    (currentDept?.code && deptCategoryByCode[currentDept.code]) ||
    (currentDept?.name?.toLowerCase().includes('finance')
      ? 'Financial'
      : currentDept?.name?.toLowerCase().includes('human')
        ? 'HR'
        : currentDept?.name?.toLowerCase().includes('academic')
          ? 'Academic'
          : currentDept?.name?.toLowerCase().includes('information technology') || currentDept?.name?.toLowerCase().includes('it')
            ? 'IT'
            : 'Operational')

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    reset,
    formState: { errors, isSubmitting },
    trigger,
  } = useForm<RiskFormData>({
    resolver: zodResolver(riskFormSchema),
    defaultValues: {
      title: '',
      description: '',
      category: defaultDeptCategory,
      departmentId: user?.departmentId || user?.department_id || '',
      ownerId: user?.id || '',
      status: isDeptScopedUser ? 'Pending Approval' : 'Open',
      likelihood: 3,
      impact: 3,
      velocity: 3,
      detectability: 3,
    },
  })

  const watchedValues = watch()

  // Auto-populate department if user has one
  useEffect(() => {
    const deptId = user?.departmentId || user?.department_id
    if (deptId && !initialData) {
      setValue('departmentId', deptId)
      if (isDeptScopedUser) {
        setValue('category', defaultDeptCategory)
      }
    }
  }, [user?.departmentId, user?.department_id, initialData, setValue, isDeptScopedUser, defaultDeptCategory])

  useEffect(() => {
    if (user?.id && !initialData) {
      setValue('ownerId', user.id)
    }
  }, [user?.id, initialData, setValue])

  useEffect(() => {
    if (!initialData) return
    reset({
      title: initialData.title,
      description: initialData.description,
      category: initialData.category as RiskFormData['category'],
      departmentId: initialData.departmentId,
      ownerId: initialData.owner,
      status: (STATUSES.includes((initialData.apiStatus || '') as (typeof STATUSES)[number])
        ? initialData.apiStatus
        : 'Open') as RiskFormData['status'],
      likelihood: initialData.probability,
      impact: initialData.impact,
      velocity: initialData.velocity ?? 3,
      detectability: initialData.detectability ?? 3,
    })
  }, [initialData, reset])

  const onSubmit = async (data: RiskFormData) => {
    try {
      setSubmitError(null)
      if (initialData) {
        await updateRisk.mutateAsync({ id: initialData.id, data })
        navigate(`/risks/${initialData.id}`)
      } else {
        const result = await createRisk.mutateAsync(data)
        navigate(`/risks/${result.id}`)
      }
    } catch (error: unknown) {
      let msg = 'Failed to save risk'
      if (isAxiosError(error)) {
        const d = error.response?.data as { detail?: unknown }
        if (typeof d?.detail === 'string') msg = d.detail
        else if (Array.isArray(d?.detail)) {
          msg = d.detail.map((x: { field?: string; message?: string }) => `${x.field}: ${x.message}`).join('; ')
        }
      }
      setSubmitError(msg)
    }
  }

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">{initialData ? 'Edit Risk' : 'Create New Risk'}</h1>
        <p className="text-gray-600">
          {initialData ? 'Update risk details and scoring' : 'Fill in all fields to create a new risk assessment'}
        </p>
      </div>

      {submitError && (
        <Alert
          variant="error"
          title="Error"
          message={submitError}
          onClose={() => setSubmitError(null)}
          className="mb-6"
        />
      )}

      {isEditing && riskLoading ? (
        <Spinner />
      ) : (
      <form onSubmit={handleSubmit(onSubmit)} className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main form fields */}
        <div className="lg:col-span-2 space-y-6">
          {/* Title & Description */}
          <Card>
            <CardHeader>
              <h2 className="font-semibold text-gray-900">Risk Details</h2>
            </CardHeader>
            <CardBody className="space-y-4">
              <div>
                <label htmlFor="title" className="block text-sm font-medium text-gray-900 mb-1">
                  Title *
                </label>
                <input
                  id="title"
                  type="text"
                  placeholder="e.g., Key Person Risk - CFO"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-mid focus:border-transparent outline-none"
                  {...register('title')}
                  onBlur={() => trigger('title')}
                />
                {errors.title && <p className="text-sm text-risk-critical mt-1">{errors.title.message}</p>}
              </div>

              <div>
                <label htmlFor="description" className="block text-sm font-medium text-gray-900 mb-1">
                  Description *
                </label>
                <textarea
                  id="description"
                  placeholder="Describe the risk in detail..."
                  rows={4}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-mid focus:border-transparent outline-none"
                  {...register('description')}
                  onBlur={() => trigger('description')}
                />
                {errors.description && <p className="text-sm text-risk-critical mt-1">{errors.description.message}</p>}
              </div>
            </CardBody>
          </Card>

          {/* Category, Department, Owner, Status */}
          <Card>
            <CardHeader>
              <h2 className="font-semibold text-gray-900">Classification</h2>
            </CardHeader>
            <CardBody className="grid grid-cols-2 gap-4">
              <div>
                <label htmlFor="category" className="block text-sm font-medium text-gray-900 mb-1">
                  Category *
                </label>
                <select
                  id="category"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-mid focus:border-transparent outline-none"
                  disabled={isDeptScopedUser}
                  {...register('category')}
                >
                  {CATEGORIES.map((cat) => (
                    <option key={cat} value={cat}>
                      {cat}
                    </option>
                  ))}
                </select>
                {errors.category && <p className="text-sm text-risk-critical mt-1">{errors.category.message}</p>}
              </div>

              <div>
                <label htmlFor="departmentId" className="block text-sm font-medium text-gray-900 mb-1">
                  Department *
                </label>
                <select
                  id="departmentId"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-mid focus:border-transparent outline-none"
                  disabled={isDeptScopedUser}
                  {...register('departmentId')}
                >
                  <option value="">Select a department</option>
                  {departments?.map((dept) => (
                    <option key={dept.id} value={dept.id}>
                      {dept.name}
                    </option>
                  ))}
                </select>
                {errors.departmentId && <p className="text-sm text-risk-critical mt-1">{errors.departmentId.message}</p>}
              </div>

              <div>
                <label htmlFor="ownerId" className="block text-sm font-medium text-gray-900 mb-1">
                  Risk owner (user id) *
                </label>
                <select
                  id="ownerId"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-mid focus:border-transparent outline-none"
                  {...register('ownerId')}
                >
                  <option value="">Select owner</option>
                  {user && (
                    <option value={user.id}>
                      {user.name} ({user.email})
                    </option>
                  )}
                  {initialData?.owner && initialData.owner !== user?.id && (
                    <option value={initialData.owner}>Current owner (edit)</option>
                  )}
                </select>
                {errors.ownerId && <p className="text-sm text-risk-critical mt-1">{errors.ownerId.message}</p>}
              </div>

              {isDeptScopedUser && !isEditing ? (
                <input type="hidden" {...register('status')} />
              ) : (
                <div>
                  <label htmlFor="status" className="block text-sm font-medium text-gray-900 mb-1">
                    Status *
                  </label>
                  <select
                    id="status"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-mid focus:border-transparent outline-none"
                    disabled={isDeptScopedUser}
                    {...register('status')}
                  >
                    {STATUSES.map((status) => (
                      <option key={status} value={status}>
                        {status}
                      </option>
                    ))}
                  </select>
                  {errors.status && <p className="text-sm text-risk-critical mt-1">{errors.status.message}</p>}
                </div>
              )}
            </CardBody>
          </Card>

          {/* Scoring Sliders */}
          <Card>
            <CardHeader>
              <h2 className="font-semibold text-gray-900">Risk Scoring</h2>
              <p className="text-xs text-gray-500">Move sliders to see live score update</p>
            </CardHeader>
            <CardBody className="space-y-6">
              <Slider
                label="Likelihood (L)"
                value={watchedValues.likelihood}
                onChange={(v) => setValue('likelihood', v)}
                tooltip="How probable is this risk occurring? (1=Rare, 5=Almost Certain)"
                error={errors.likelihood?.message}
              />
              <Slider
                label="Impact (I)"
                value={watchedValues.impact}
                onChange={(v) => setValue('impact', v)}
                tooltip="How severe would the consequences be? (1=Negligible, 5=Catastrophic)"
                error={errors.impact?.message}
              />
              <Slider
                label="Velocity (V)"
                value={watchedValues.velocity}
                onChange={(v) => setValue('velocity', v)}
                tooltip="How quickly could this risk materialise? (1=Slow, 5=Immediate)"
                error={errors.velocity?.message}
              />
              <Slider
                label="Detectability (D)"
                value={watchedValues.detectability}
                onChange={(v) => setValue('detectability', v)}
                tooltip="How hard is this risk to detect? (1=Easily Detected, 5=Very Hidden)"
                error={errors.detectability?.message}
              />
            </CardBody>
          </Card>

          {/* Submit Buttons */}
          <div className="flex gap-3">
            <Button
              type="submit"
              variant="primary"
              isLoading={isSubmitting}
              className="flex-1"
            >
              {initialData ? 'Update Risk' : 'Create Risk'}
            </Button>
            <Button
              type="button"
              variant="secondary"
              onClick={() => navigate('/risks')}
            >
              Cancel
            </Button>
          </div>
        </div>

        {/* Score Preview Sidebar */}
        <div className="lg:col-span-1">
          <ScorePreview
            likelihood={watchedValues.likelihood}
            impact={watchedValues.impact}
            velocity={watchedValues.velocity}
            detectability={watchedValues.detectability}
          />
        </div>
      </form>
      )}
    </div>
  )
}
