import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { isAxiosError } from 'axios'
import { Button } from '@/components/ui/Button'
import { Alert } from '@/components/ui/Alert'
import { useAuth } from '@/context/AuthContext'
import { authApi } from '@/api/authApi'
import { useDepartments } from '@/hooks/useDepartments'

const registerSchema = z
  .object({
    email: z.string().email('Invalid email address'),
    password: z.string().min(8, 'Password must be at least 8 characters'),
    confirmPassword: z.string(),
    full_name: z.string().min(2, 'Name is required').max(255),
    role: z.enum(['risk_officer', 'dept_user']),
    sub_role: z.enum(['data_clerk', 'risk_clerk']).optional(),
    department_id: z.string().optional(),
  })
  .refine((data) => {
    if (data.role === 'risk_officer') return true
    return !!data.department_id
  }, {
    message: 'Select a department',
    path: ['department_id'],
  })
  .refine((data) => {
    if (data.role === 'risk_officer') return true
    return !!data.sub_role
  }, {
    message: 'Select a department role',
    path: ['sub_role'],
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: 'Passwords do not match',
    path: ['confirmPassword'],
  })

type RegisterFormData = z.infer<typeof registerSchema>

export const Register = () => {
  const navigate = useNavigate()
  const { login } = useAuth()
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const { data: departments, isLoading: deptsLoading, isError: deptsError } = useDepartments()

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
    defaultValues: { role: 'dept_user', sub_role: 'data_clerk', department_id: '' },
  })

  const selectedRole = watch('role')

  const onSubmit = async (data: RegisterFormData) => {
    try {
      setIsLoading(true)
      setError(null)
      const response = await authApi.register({
        email: data.email.trim().toLowerCase(),
        password: data.password,
        full_name: data.full_name.trim(),
        role: data.role === 'risk_officer' ? 'risk_officer' : data.sub_role,
        department_id: data.role === 'risk_officer' ? undefined : data.department_id,
      })
      login(response.token, response.user)
      navigate('/dashboard')
    } catch (err) {
      if (isAxiosError(err)) {
        const status = err.response?.status
        const detail = err.response?.data?.detail
        const msg = typeof detail === 'string' ? detail : 'Registration failed'
        if (status === 409) {
          setError(msg)
        } else if (status === 403) {
          setError(msg)
        } else if (status === 422) {
          setError(msg)
        } else {
          setError('Could not create account. Try again or use a different email.')
        }
      } else {
        setError('Something went wrong.')
      }
      console.error(err)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center px-4 py-10">
      <div className="w-full max-w-md">
        <div className="rounded-2xl border border-slate-200/70 bg-white/90 p-8 shadow-shell backdrop-blur-sm">
          <div className="mb-8 text-center">
            <h1 className="font-display text-3xl font-bold tracking-tight text-brand-dark sm:text-4xl">ERM</h1>
            <p className="mt-2 text-sm font-medium uppercase tracking-[0.18em] text-brand-mid">Enterprise risk</p>
            <p className="mt-3 text-slate-600">Create a department account</p>
          </div>

          {error && (
            <Alert variant="error" message={error} onClose={() => setError(null)} className="mb-6" />
          )}

          {deptsError && (
            <Alert
              variant="error"
              message="Could not load departments. Check that the API is running."
              className="mb-6"
            />
          )}

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div>
              <label htmlFor="full_name" className="block text-sm font-medium text-gray-700 mb-2">
                Full name
              </label>
              <input
                id="full_name"
                type="text"
                autoComplete="name"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-mid focus:border-transparent outline-none"
                {...register('full_name')}
              />
              {errors.full_name && (
                <p className="text-risk-critical text-sm mt-1">{errors.full_name.message}</p>
              )}
            </div>

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                Email
              </label>
              <input
                id="email"
                type="email"
                autoComplete="email"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-mid focus:border-transparent outline-none"
                {...register('email')}
              />
              {errors.email && <p className="text-risk-critical text-sm mt-1">{errors.email.message}</p>}
            </div>

            <div>
              <label htmlFor="role" className="block text-sm font-medium text-gray-700 mb-2">
                Role
              </label>
              <select
                id="role"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-mid focus:border-transparent outline-none bg-white"
                {...register('role')}
              >
                <option value="dept_user">Department User</option>
                <option value="risk_officer">Risk Officer</option>
              </select>
              {errors.role && <p className="text-risk-critical text-sm mt-1">{errors.role.message}</p>}
            </div>

            {selectedRole === 'dept_user' && (
              <div>
                <label htmlFor="sub_role" className="block text-sm font-medium text-gray-700 mb-2">
                  Department User Type
                </label>
                <select
                  id="sub_role"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-mid focus:border-transparent outline-none bg-white"
                  {...register('sub_role')}
                >
                  <option value="data_clerk">Data Clerk</option>
                  <option value="risk_clerk">Risk Clerk</option>
                </select>
                {errors.sub_role && (
                  <p className="text-risk-critical text-sm mt-1">{errors.sub_role.message}</p>
                )}
              </div>
            )}

            <div>
              <label htmlFor="department_id" className="block text-sm font-medium text-gray-700 mb-2">
                Department
              </label>
              <select
                id="department_id"
                disabled={selectedRole === 'risk_officer' || deptsLoading || !!deptsError}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-mid focus:border-transparent outline-none bg-white"
                {...register('department_id')}
              >
                <option value="">
                  {selectedRole === 'risk_officer'
                    ? 'Not required for Risk Officer'
                    : deptsLoading
                      ? 'Loading…'
                      : 'Select department'}
                </option>
                {departments?.map((d) => (
                  <option key={d.id} value={d.id}>
                    {d.name} ({d.code})
                  </option>
                ))}
              </select>
              {errors.department_id && (
                <p className="text-risk-critical text-sm mt-1">{errors.department_id.message}</p>
              )}
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                Password
              </label>
              <input
                id="password"
                type="password"
                autoComplete="new-password"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-mid focus:border-transparent outline-none"
                {...register('password')}
              />
              {errors.password && (
                <p className="text-risk-critical text-sm mt-1">{errors.password.message}</p>
              )}
            </div>

            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-2">
                Confirm password
              </label>
              <input
                id="confirmPassword"
                type="password"
                autoComplete="new-password"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-mid focus:border-transparent outline-none"
                {...register('confirmPassword')}
              />
              {errors.confirmPassword && (
                <p className="text-risk-critical text-sm mt-1">{errors.confirmPassword.message}</p>
              )}
            </div>

            <Button type="submit" isLoading={isLoading} className="w-full" disabled={deptsLoading || !!deptsError}>
              Create account
            </Button>
          </form>

          <p className="text-center text-sm text-gray-600 mt-6">
            Already have an account?{' '}
            <Link to="/login" className="text-brand-mid font-medium hover:underline">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
