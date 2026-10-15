import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useAuth } from '@/context/AuthContext'
import { useToast } from '@/context/ToastContext'
import { authApi } from '@/api/authApi'
import { Button } from '@/components/ui/Button'
import { Card, CardBody } from '@/components/ui/Card'
const settingsSchema = z
  .object({
    full_name: z.string().min(2, 'Name must be at least 2 characters').max(255),
    password: z.string().optional(),
    confirmPassword: z.string().optional(),
  })
  .refine((d) => !d.password || d.password.length >= 8, {
    message: 'New password must be at least 8 characters',
    path: ['password'],
  })
  .refine((d) => !d.password || d.password === d.confirmPassword, {
    message: 'Passwords do not match',
    path: ['confirmPassword'],
  })

type SettingsForm = z.infer<typeof settingsSchema>

export const SettingsPage = () => {
  const { user, setUser } = useAuth()
  const { addToast } = useToast()

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<SettingsForm>({
    resolver: zodResolver(settingsSchema),
    defaultValues: { full_name: '', password: '', confirmPassword: '' },
  })

  useEffect(() => {
    if (user?.name) {
      reset({ full_name: user.name, password: '', confirmPassword: '' })
    }
  }, [user?.name, reset])

  const onSubmit = async (data: SettingsForm) => {
    try {
      const payload: { full_name?: string; password?: string } = {
        full_name: data.full_name.trim(),
      }
      if (data.password && data.password.length > 0) {
        payload.password = data.password
      }
      const updated = await authApi.updateMe(payload)
      setUser(updated)
      reset({ full_name: updated.name, password: '', confirmPassword: '' })
      addToast('Settings saved', 'success')
    } catch {
      addToast('Could not save settings', 'error')
    }
  }

  return (
    <div className="mx-auto max-w-lg space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
        <p className="mt-1 text-gray-600">Update your profile and password</p>
      </div>

      <Card>
        <CardBody className="space-y-4">
          <div className="rounded-lg bg-gray-50 px-4 py-3 text-sm text-gray-600">
            <p>
              <span className="font-medium text-gray-800">Email</span> ({user?.email}) cannot be changed here.
            </p>
            <p className="mt-1 capitalize">Role: {user?.role?.replace(/_/g, ' ')}</p>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div>
              <label htmlFor="full_name" className="mb-2 block text-sm font-medium text-gray-700">
                Display name
              </label>
              <input
                id="full_name"
                autoComplete="name"
                className="w-full rounded-lg border border-gray-300 px-4 py-2 outline-none focus:border-transparent focus:ring-2 focus:ring-brand-mid"
                {...register('full_name')}
              />
              {errors.full_name && (
                <p className="mt-1 text-sm text-risk-critical">{errors.full_name.message}</p>
              )}
            </div>

            <div className="border-t border-gray-100 pt-4">
              <p className="mb-3 text-sm font-medium text-gray-800">Change password</p>
              <p className="mb-3 text-xs text-gray-500">Leave blank to keep your current password.</p>
              <div className="space-y-3">
                <div>
                  <label htmlFor="password" className="mb-2 block text-sm font-medium text-gray-700">
                    New password
                  </label>
                  <input
                    id="password"
                    type="password"
                    autoComplete="new-password"
                    className="w-full rounded-lg border border-gray-300 px-4 py-2 outline-none focus:border-transparent focus:ring-2 focus:ring-brand-mid"
                    {...register('password')}
                  />
                  {errors.password && (
                    <p className="mt-1 text-sm text-risk-critical">{errors.password.message}</p>
                  )}
                </div>
                <div>
                  <label htmlFor="confirmPassword" className="mb-2 block text-sm font-medium text-gray-700">
                    Confirm new password
                  </label>
                  <input
                    id="confirmPassword"
                    type="password"
                    autoComplete="new-password"
                    className="w-full rounded-lg border border-gray-300 px-4 py-2 outline-none focus:border-transparent focus:ring-2 focus:ring-brand-mid"
                    {...register('confirmPassword')}
                  />
                  {errors.confirmPassword && (
                    <p className="mt-1 text-sm text-risk-critical">{errors.confirmPassword.message}</p>
                  )}
                </div>
              </div>
            </div>

            <Button type="submit" isLoading={isSubmitting} className="w-full sm:w-auto">
              Save changes
            </Button>
          </form>
        </CardBody>
      </Card>
    </div>
  )
}
