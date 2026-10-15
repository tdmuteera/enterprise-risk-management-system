import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Button } from '@/components/ui/Button'
import { Alert } from '@/components/ui/Alert'
import { useAuth } from '@/context/AuthContext'
import { authApi } from '@/api/authApi'

const loginSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
})

type LoginFormData = z.infer<typeof loginSchema>

export const Login = () => {
  const navigate = useNavigate()
  const { login } = useAuth()
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  })

  const onSubmit = async (data: LoginFormData) => {
    try {
      setIsLoading(true)
      setError(null)
      const response = await authApi.login(data)
      login(response.token, response.user)
      navigate('/dashboard')
    } catch (err) {
      setError('Invalid email or password')
      console.error(err)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center px-4 py-12">
      <div className="w-full max-w-md">
        <div className="rounded-2xl border border-slate-200/70 bg-white/90 p-8 shadow-shell backdrop-blur-sm">
          <div className="mb-8 text-center">
            <h1 className="font-display text-3xl font-bold tracking-tight text-brand-dark sm:text-4xl">ERM</h1>
            <p className="mt-2 text-sm font-medium uppercase tracking-[0.18em] text-brand-mid">Enterprise risk</p>
            <p className="mt-3 text-slate-600">Sign in to continue</p>
          </div>

          {/* Error Alert */}
          {error && (
            <Alert
              variant="error"
              message={error}
              onClose={() => setError(null)}
              className="mb-6"
            />
          )}

          {/* Form */}
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                Email Address
              </label>
              <input
                id="email"
                type="email"
                placeholder="you@example.com"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-mid focus:border-transparent outline-none"
                {...register('email')}
              />
              {errors.email && (
                <p className="text-risk-critical text-sm mt-1">{errors.email.message}</p>
              )}
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                Password
              </label>
              <input
                id="password"
                type="password"
                placeholder="••••••••"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-mid focus:border-transparent outline-none"
                {...register('password')}
              />
              {errors.password && (
                <p className="text-risk-critical text-sm mt-1">{errors.password.message}</p>
              )}
            </div>

            <Button
              type="submit"
              isLoading={isLoading}
              className="w-full"
            >
              Sign In
            </Button>
          </form>

          <p className="text-center text-sm text-gray-600 mt-6 space-y-2">
            <span className="block">
              Seed demo login: <span className="font-mono text-xs">admin@erm.edu</span> /{' '}
              <span className="font-mono text-xs">AdminPass123!</span>
            </span>
            <span className="block text-xs text-gray-600 mt-2">
              Risk manager: <span className="font-mono">risk.manager@erm.edu</span> /{' '}
              <span className="font-mono">RiskMgr123!</span>
              {' · '}
              Finance head: <span className="font-mono">head.fin@erm.edu</span> /{' '}
              <span className="font-mono">HeadFin123!</span>
            </span>
            <span className="block text-xs text-gray-500">
              If these fail, delete the desktop app data folder once so a fresh database is copied, or run{' '}
              <span className="font-mono">python db_seed.py</span> in the backend folder.
            </span>
            <Link to="/register" className="block text-brand-mid font-medium hover:underline">
              Create an account for your department
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
